"""Canonical catalog and state transitions for topology-aware workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.workspace import WorkspaceExecution, WorkspaceExecutionEvent
from backend.app.schemas.workspace import (
    WorkspaceExecutionCreate,
    WorkspaceExecutionStatus,
    WorkspaceTransitionAction,
    WorkflowTemplateResponse,
    WorkflowTemplateStep,
)


@dataclass(frozen=True)
class WorkflowTemplateDefinition:
    code: str
    version: int
    name: str
    vertical: str
    description: str
    document_count: int
    privacy_note: str
    steps: tuple[WorkflowTemplateStep, ...]

    def to_response(self) -> WorkflowTemplateResponse:
        return WorkflowTemplateResponse(
            code=self.code,
            version=self.version,
            name=self.name,
            vertical=self.vertical,
            description=self.description,
            document_count=self.document_count,
            privacy_note=self.privacy_note,
            steps=list(self.steps),
        )


WORKFLOW_CATALOG: Final[dict[str, WorkflowTemplateDefinition]] = {
    "hr-onboarding-core": WorkflowTemplateDefinition(
        code="hr-onboarding-core",
        version=1,
        name="HR Onboarding Core",
        vertical="Human resources",
        description=(
            "A controlled three-step onboarding checklist for owner-recorded review "
            "and participant confirmation."
        ),
        document_count=3,
        privacy_note=(
            "This foundation stores workflow metadata only. It does not upload, sign, "
            "or retain the underlying onboarding documents."
        ),
        steps=(
            WorkflowTemplateStep(
                id="prepare",
                label="Prepare packet",
                role="Workspace owner",
                description="Confirm the right packet and participant details before review.",
            ),
            WorkflowTemplateStep(
                id="review",
                label="Record reviewer approval",
                role="Reviewer",
                description="Record that the designated reviewer approved the prepared packet.",
            ),
            WorkflowTemplateStep(
                id="confirm",
                label="Record participant confirmation",
                role="Participant",
                description="Record completion only after the participant has confirmed externally.",
            ),
        ),
    )
}


class WorkspaceCatalogError(ValueError):
    """Raised when a caller refers to an unavailable template."""


class WorkspaceTransitionError(ValueError):
    """Raised when a requested action is invalid for the current state."""


_TRANSITIONS: Final[dict[tuple[WorkspaceExecutionStatus, WorkspaceTransitionAction], WorkspaceExecutionStatus]] = {
    (
        WorkspaceExecutionStatus.PENDING_REVIEW,
        WorkspaceTransitionAction.RECORD_REVIEW,
    ): WorkspaceExecutionStatus.AWAITING_PARTICIPANT,
    (
        WorkspaceExecutionStatus.AWAITING_PARTICIPANT,
        WorkspaceTransitionAction.RECORD_PARTICIPANT_CONFIRMATION,
    ): WorkspaceExecutionStatus.COMPLETED,
    (
        WorkspaceExecutionStatus.PENDING_REVIEW,
        WorkspaceTransitionAction.CANCEL,
    ): WorkspaceExecutionStatus.CANCELLED,
    (
        WorkspaceExecutionStatus.AWAITING_PARTICIPANT,
        WorkspaceTransitionAction.CANCEL,
    ): WorkspaceExecutionStatus.CANCELLED,
}


def list_templates() -> list[WorkflowTemplateResponse]:
    """Return the versioned, code-owned catalog in a stable display order."""
    return [definition.to_response() for definition in WORKFLOW_CATALOG.values()]


def get_template(code: str) -> WorkflowTemplateDefinition:
    try:
        return WORKFLOW_CATALOG[code]
    except KeyError as exc:
        raise WorkspaceCatalogError("Unknown or inactive workflow template.") from exc


def resolve_transition(
    status: WorkspaceExecutionStatus,
    action: WorkspaceTransitionAction,
) -> WorkspaceExecutionStatus:
    """Return the next state or fail closed for invalid/replayed transitions."""
    next_status = _TRANSITIONS.get((status, action))
    if next_status is None:
        raise WorkspaceTransitionError(
            f"Cannot apply '{action.value}' while execution is '{status.value}'."
        )
    return next_status


def _event_summary(action: WorkspaceTransitionAction | None) -> str:
    summaries = {
        None: "Workflow execution created from the versioned template catalog.",
        WorkspaceTransitionAction.RECORD_REVIEW: "Reviewer approval recorded by workspace owner.",
        WorkspaceTransitionAction.RECORD_PARTICIPANT_CONFIRMATION: (
            "Participant confirmation recorded by workspace owner."
        ),
        WorkspaceTransitionAction.CANCEL: "Workflow execution cancelled by workspace owner.",
    }
    return summaries[action]


def _record_event(
    db: Session,
    execution: WorkspaceExecution,
    actor: User,
    *,
    event_type: str,
    status_from: str | None,
    status_to: str,
    summary: str,
) -> WorkspaceExecutionEvent:
    sequence = (
        db.query(func.coalesce(func.max(WorkspaceExecutionEvent.sequence), 0))
        .filter(WorkspaceExecutionEvent.execution_id == execution.id)
        .scalar()
    )
    event = WorkspaceExecutionEvent(
        execution_id=execution.id,
        sequence=int(sequence) + 1,
        actor_user_id=actor.id,
        event_type=event_type,
        status_from=status_from,
        status_to=status_to,
        summary=summary,
    )
    db.add(event)
    return event


def create_execution(
    db: Session,
    owner: User,
    payload: WorkspaceExecutionCreate,
) -> WorkspaceExecution:
    """Create a Cloud-topology execution and its first immutable event receipt."""
    template = get_template(payload.template_code)
    execution = WorkspaceExecution(
        owner_user_id=owner.id,
        template_code=template.code,
        template_version=template.version,
        topology="cloud",
        status=WorkspaceExecutionStatus.PENDING_REVIEW.value,
        title=f"{template.name}: {payload.participant_name}",
        participant_name=payload.participant_name.strip(),
        participant_email=str(payload.participant_email).lower(),
        reviewer_name=payload.reviewer_name.strip(),
        reviewer_email=str(payload.reviewer_email).lower(),
        effective_date=payload.effective_date,
        notes=payload.notes.strip() if payload.notes else None,
    )
    db.add(execution)
    db.flush()
    _record_event(
        db,
        execution,
        owner,
        event_type="execution_created",
        status_from=None,
        status_to=WorkspaceExecutionStatus.PENDING_REVIEW.value,
        summary=_event_summary(None),
    )
    db.commit()
    db.refresh(execution)
    return execution


def transition_execution(
    db: Session,
    execution: WorkspaceExecution,
    actor: User,
    action: WorkspaceTransitionAction,
) -> WorkspaceExecution:
    """Advance one owner-controlled execution through its explicitly allowed states."""
    current_status = WorkspaceExecutionStatus(execution.status)
    next_status = resolve_transition(current_status, action)
    execution.status = next_status.value
    _record_event(
        db,
        execution,
        actor,
        event_type=action.value,
        status_from=current_status.value,
        status_to=next_status.value,
        summary=_event_summary(action),
    )
    db.commit()
    db.refresh(execution)
    return execution


def execution_events(db: Session, execution_id: object) -> list[WorkspaceExecutionEvent]:
    """Read event lineage in canonical sequence order."""
    return (
        db.query(WorkspaceExecutionEvent)
        .filter(WorkspaceExecutionEvent.execution_id == execution_id)
        .order_by(WorkspaceExecutionEvent.sequence.asc())
        .all()
    )
