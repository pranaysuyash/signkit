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
