"""Protected API for the browser-native workflow control plane."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.workspace import WorkspaceExecution
from backend.app.runtime import is_local_companion
from backend.app.schemas.workspace import (
    DocumentInspectionResponse,
    LocalWorkflowJobResponse,
    WorkspaceExecutionCreate,
    WorkspaceExecutionResponse,
    WorkspaceExecutionTransition,
    WorkflowTemplateResponse,
)
from backend.app.services.document_inspection import (
    MAX_DOCUMENT_BYTES,
    DocumentInspectionConflict,
    DocumentInspectionError,
    DocumentInspectionTopologyError,
    inspect_local_document,
    record_inspection_failure,
)
from backend.app.services.passport import project_workspace_execution
from backend.app.services.workspace import (
    WorkspaceCatalogError,
    WorkspaceTransitionError,
    create_execution,
    execution_events,
    get_template,
    list_templates,
    transition_execution,
)
from backend.app.utils.dependencies import get_current_user


router = APIRouter(tags=["Workspace"])
local_document_router = APIRouter(tags=["Local companion"])


def _event_payload(event) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": event.id,
        "sequence": event.sequence,
        "event_type": event.event_type,
        "status_from": event.status_from,
        "status_to": event.status_to,
        "idem_key": event.idem_key,
        "summary": event.summary,
        "created_at": event.created_at,
    }
    if event.result_json and event.event_type in {
        "document_inspection",
        "document_inspection_failed",
    }:
        try:
            result = json.loads(event.result_json)
        except json.JSONDecodeError:
            result = None
        if isinstance(result, dict):
            payload["result"] = result
    return payload


def _as_response(db: Session, execution: WorkspaceExecution) -> WorkspaceExecutionResponse:
    events = execution_events(db, execution.id)
    return WorkspaceExecutionResponse.model_validate(
        {
            "id": execution.id,
            "template_code": execution.template_code,
            "template_version": execution.template_version,
            "topology": execution.topology,
            "status": execution.status,
            "title": execution.title,
            "participant_name": execution.participant_name,
            "participant_email": execution.participant_email,
            "reviewer_name": execution.reviewer_name,
            "reviewer_email": execution.reviewer_email,
            "effective_date": execution.effective_date,
            "notes": execution.notes,
            "created_at": execution.created_at,
            "updated_at": execution.updated_at,
            "events": [_event_payload(event) for event in events],
            "passport": project_workspace_execution(execution, events).to_payload(),
        }
    )


def _get_owned_execution(
    db: Session,
    execution_id: str,
    current_user: User,
) -> WorkspaceExecution:
    execution = (
        db.query(WorkspaceExecution)
        .filter(
            WorkspaceExecution.id == execution_id,
            WorkspaceExecution.owner_user_id == current_user.id,
        )
        .first()
    )
    if execution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow execution not found.")
    return execution


def _local_subjects(current_user: User) -> tuple[str, ...]:
    """Return exact desktop subjects owned by the authenticated account.

    UUID is the canonical bridge identity. Email remains an exact compatibility
    identity because existing desktop grants were created with operator email
    subjects; it is unique in the authenticated user table and is never treated
    as a wildcard or substring match.
    """
    subjects = [str(current_user.id)]
    email = str(current_user.email or "").strip()
    if email and email not in subjects:
        subjects.append(email)
    return tuple(subjects)


def _authorize_local_job(job, current_user: User):
    from desktop_app.workflows import authorization

    for subject in _local_subjects(current_user):
        decision = authorization.require_authorization(
            job,
            subject=subject,
            requested_action="inspect_job",
        )
        if decision.allowed:
            return subject
    return None


def _get_authorized_local_job(job_id: str, current_user: User):
    """Read one local job through the desktop store's existing grant boundary."""
    if not is_local_companion():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local workflow bridge is unavailable on the hosted runtime profile.",
        )

    from desktop_app.workflows import store

    job = store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Local workflow job not found.")

    subject = _authorize_local_job(job, current_user)
    if subject is None:
        # Do not disclose whether an unowned job exists or why its grant failed.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Local workflow job not found.")
    return job, store, subject


def _local_job_response(job, store) -> LocalWorkflowJobResponse:
    from desktop_app.workflows.passport import project_local_job

    passport = project_local_job(job, store.list_events(job.job_id))
    return LocalWorkflowJobResponse.model_validate(
        {
            "job_id": job.job_id,
            "title": f"Local desktop execution {job.job_id[:8]}",
            "status": job.state.value,
            "topology": "local",
            "template_code": job.recipe_id,
            "template_version": job.recipe_version,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "passport": passport.to_payload(),
        }
    )


@router.get("/local-jobs", response_model=list[LocalWorkflowJobResponse])
def get_local_jobs(current_user: User = Depends(get_current_user)):
    """Project only the authenticated user's local desktop jobs."""
    if not is_local_companion():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local workflow bridge is unavailable on the hosted runtime profile.",
        )

    from desktop_app.workflows import store

    result = []
    for job in store.list_jobs():
        if _authorize_local_job(job, current_user) is not None:
            result.append(_local_job_response(job, store))
    return result


@router.get("/local-jobs/{job_id}", response_model=LocalWorkflowJobResponse)
def get_local_job(job_id: str, current_user: User = Depends(get_current_user)):
    job, store, _ = _get_authorized_local_job(job_id, current_user)
    return _local_job_response(job, store)


@router.post("/local-jobs/{job_id}/retry", response_model=LocalWorkflowJobResponse)
def retry_local_job(
    job_id: str,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
):
    from desktop_app.workflows import models
    from desktop_app.workflows.engine import WorkflowEngine
    from desktop_app.workflows import store as workflow_store

    initial_job, _, _ = _get_authorized_local_job(job_id, current_user)
    provided_key = idempotency_key.strip() if idempotency_key else ""
    retry_key = provided_key or f"local-retry:{initial_job.job_id}:attempt:{initial_job.attempts}"
    if len(retry_key) < 6 or len(retry_key) > 80:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key must be between 6 and 80 characters.",
        )

    with workflow_store.workflow_store_lock():
        job, store, subject = _get_authorized_local_job(job_id, current_user)

        replay = store.get_retry_receipt(job.job_id, retry_key)
        if replay is not None:
            replay_job = models.WorkflowJob.from_payload(replay["job"])
            return _local_job_response(replay_job, store)

        if job.state not in {
            models.WorkflowState.FAILED,
            models.WorkflowState.RETRY,
            models.WorkflowState.NEEDS_REVIEW,
        }:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Local workflow job is not retryable in its current state.",
            )

        engine = WorkflowEngine(
            actor=f"workspace-local:{current_user.id}",
            audit_actor="workspace-local-bridge",
        )
        engine.start()
        try:
            updated = engine.retry_job(
                job.job_id,
                actor=f"workspace-local:{current_user.id}",
                action_subject=subject,
                idempotency_key=retry_key,
            )
        except ValueError as exc:
            if str(exc).startswith("job_not_found:"):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Local workflow job not found.") from exc
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Local workflow retry could not be started.",
            ) from exc
        finally:
            engine.stop()

        store.save_retry_receipt(updated, retry_key)
        return _local_job_response(updated, store)


@router.get("/templates", response_model=list[WorkflowTemplateResponse])
def get_templates(_: User = Depends(get_current_user)):
    """Expose the code-owned catalog through one authenticated endpoint."""
    return list_templates()


@router.get("/templates/{template_code}", response_model=WorkflowTemplateResponse)
def get_workspace_template(template_code: str, _: User = Depends(get_current_user)):
    try:
        return get_template(template_code).to_response()
    except WorkspaceCatalogError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/executions", response_model=list[WorkspaceExecutionResponse])
def get_executions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    executions = (
        db.query(WorkspaceExecution)
        .filter(WorkspaceExecution.owner_user_id == current_user.id)
        .order_by(WorkspaceExecution.updated_at.desc(), WorkspaceExecution.created_at.desc())
        .all()
    )
    return [_as_response(db, execution) for execution in executions]


@router.post(
    "/executions",
    response_model=WorkspaceExecutionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workspace_execution(
    payload: WorkspaceExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.topology.value == "local" and not is_local_companion():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Local topology is unavailable on the hosted runtime profile.",
        )
    try:
        execution = create_execution(db, current_user, payload)
        return _as_response(db, execution)
    except WorkspaceCatalogError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc


@router.get("/executions/{execution_id}", response_model=WorkspaceExecutionResponse)
def get_workspace_execution(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _as_response(db, _get_owned_execution(db, execution_id, current_user))


@router.post("/executions/{execution_id}/transitions", response_model=WorkspaceExecutionResponse)
def transition_workspace_execution(
    execution_id: str,
    payload: WorkspaceExecutionTransition,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    execution = _get_owned_execution(db, execution_id, current_user)
    try:
        updated_execution = transition_execution(
            db,
            execution,
            current_user,
            payload.action,
            idem_key=payload.idem_key,
        )
        return _as_response(db, updated_execution)
    except WorkspaceTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@local_document_router.post(
    "/executions/{execution_id}/document-inspections",
    response_model=DocumentInspectionResponse,
)
def inspect_execution_document(
    execution_id: str,
    file: UploadFile = File(...),
    page_index: int = Form(0),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    execution = _get_owned_execution(db, execution_id, current_user)
    if execution.topology != "local":
        record_inspection_failure(
            db,
            execution,
            current_user,
            idem_key=idempotency_key.strip() if idempotency_key else None,
            page_index=page_index,
            document_bytes=b"",
            failure_code="topology_not_local",
            retryable=False,
            operator_action="Use a local-companion execution for document inspection.",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document inspection is available only for local topology executions.",
        )
    try:
        document_bytes = file.file.read(MAX_DOCUMENT_BYTES + 1)
        return inspect_local_document(
            db,
            execution,
            current_user,
            filename=file.filename or "",
            document_bytes=document_bytes,
            page_index=page_index,
            idem_key=idempotency_key.strip() if idempotency_key else None,
        )
    except DocumentInspectionConflict as exc:
        db.rollback()
        record_inspection_failure(
            db,
            execution,
            current_user,
            idem_key=idempotency_key.strip() if idempotency_key else None,
            page_index=page_index,
            document_bytes=document_bytes,
            failure_code="idempotency_conflict",
            retryable=False,
            operator_action="Use a new idempotency key for different document bytes.",
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except DocumentInspectionTopologyError as exc:
        db.rollback()
        record_inspection_failure(
            db,
            execution,
            current_user,
            idem_key=idempotency_key.strip() if idempotency_key else None,
            page_index=page_index,
            document_bytes=document_bytes,
            failure_code="topology_not_local",
            retryable=False,
            operator_action="Use a local-companion execution for document inspection.",
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except DocumentInspectionError as exc:
        db.rollback()
        message = str(exc).lower()
        if "worker" in message:
            failure_code = "worker_failure"
            retryable = True
            operator_action = "Retry inspection; escalate if the worker fails again."
        elif "idempotency" in message:
            failure_code = "idempotency_invalid"
            retryable = False
            operator_action = "Provide a valid idempotency key and retry."
        else:
            failure_code = "invalid_document"
            retryable = False
            operator_action = "Correct the PDF or page selection before retrying."
        record_inspection_failure(
            db,
            execution,
            current_user,
            idem_key=idempotency_key.strip() if idempotency_key else None,
            page_index=page_index,
            document_bytes=document_bytes,
            failure_code=failure_code,
            retryable=retryable,
            operator_action=operator_action,
        )
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
