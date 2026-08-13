"""Protected API for the browser-native workflow control plane."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.workspace import WorkspaceExecution
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
            "events": events,
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


@router.post(
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
    try:
        return inspect_local_document(
            db,
            execution,
            current_user,
            filename=file.filename or "",
            document_bytes=file.file.read(MAX_DOCUMENT_BYTES + 1),
            page_index=page_index,
            idem_key=idempotency_key.strip() if idempotency_key else None,
        )
    except DocumentInspectionConflict as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except DocumentInspectionTopologyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except DocumentInspectionError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
