"""API contracts for the browser-native workflow workspace."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class WorkspaceTopology(str, Enum):
    CLOUD = "cloud"
    HYBRID = "hybrid"
    LOCAL = "local"


class WorkspaceExecutionStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    AWAITING_PARTICIPANT = "awaiting_participant"
    RECEIVED = "received"
    NEEDS_CORRECTION = "needs_correction"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    SIGNED = "signed"
    EXPORTED = "exported"
    EXCEPTION = "exception"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkspaceTransitionAction(str, Enum):
    MARK_RECEIVED = "mark_received"
    REQUEST_REVIEW = "request_review"
    REQUEST_CORRECTION = "request_correction"
    APPROVE = "approve"
    SIGN = "sign"
    EXPORT = "export"
    RECORD_EXCEPTION = "record_exception"
    RETRY_REVIEW = "retry_review"
    RECORD_REVIEW = "record_review"
    RECORD_PARTICIPANT_CONFIRMATION = "record_participant_confirmation"
    CANCEL = "cancel"


class WorkflowTemplateStep(BaseModel):
    id: str
    label: str
    role: str
    description: str


class WorkflowTemplateResponse(BaseModel):
    code: str
    version: int
    name: str
    vertical: str
    description: str
    document_count: int
    privacy_note: str
    steps: list[WorkflowTemplateStep]


class WorkspaceExecutionCreate(BaseModel):
    template_code: str = Field(..., min_length=3, max_length=80)
    topology: WorkspaceTopology = WorkspaceTopology.CLOUD
    participant_name: str = Field(..., min_length=2, max_length=160)
    participant_email: EmailStr
    reviewer_name: str = Field(..., min_length=2, max_length=160)
    reviewer_email: EmailStr
    effective_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class WorkspaceExecutionTransition(BaseModel):
    action: WorkspaceTransitionAction
    idem_key: str | None = Field(default=None, min_length=6, max_length=80)


class WorkspaceExecutionEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sequence: int
    event_type: str
    status_from: str | None
    status_to: str
    idem_key: str | None = None
    summary: str
    result: dict[str, object] | None = None
    created_at: datetime


class ExecutionPassportEvidenceResponse(BaseModel):
    sequence: int
    code: str
    state_from: str | None
    state_to: str
    actor: str
    occurred_at: str
    message: str | None = None


class ExecutionPassportResponse(BaseModel):
    """API binding for the shared dependency-light Execution Passport contract."""

    passport_version: str
    execution_id: str
    topology: WorkspaceTopology
    source_of_truth: str
    owner_role: str
    template_code: str
    template_version: int
    aggregate_status: str
    child_job_id: str | None = None
    child_job_status: str | None = None
    correlation_id: str | None = None
    idempotency_key: str | None = None
    input_fingerprint: str | None = None
    output_reference: str | None = None
    attempt: int | None = None
    max_attempts: int | None = None
    evidence: list[ExecutionPassportEvidenceResponse] = Field(default_factory=list)
    recovery_action: str
    data_boundary: str
    created_at: str | None = None
    updated_at: str | None = None


class WorkspaceExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    template_code: str
    template_version: int
    topology: WorkspaceTopology
    status: WorkspaceExecutionStatus
    title: str
    participant_name: str
    participant_email: EmailStr
    reviewer_name: str
    reviewer_email: EmailStr
    effective_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    events: list[WorkspaceExecutionEventResponse] = Field(default_factory=list)
    passport: ExecutionPassportResponse


class DocumentInspectionResponse(BaseModel):
    execution_id: UUID
    event_type: str
    runtime_mode: str
    retained: bool
    input_sha256: str
    receipt_id: UUID
    page_index: int
    pages_processed: int
    candidates: list["DocumentInspectionCandidate"] = Field(default_factory=list)
    replayed: bool = False


class DocumentInspectionCandidate(BaseModel):
    page_index: int = Field(..., ge=0, le=100_000)
    field_type: str = Field(..., min_length=1, max_length=80)
    x: float = Field(..., ge=0, le=10_000_000)
    y: float = Field(..., ge=0, le=10_000_000)
    width: float = Field(..., ge=0, le=10_000_000)
    height: float = Field(..., ge=0, le=10_000_000)
    confidence: float = Field(..., ge=0, le=1)
    source: str = Field(..., min_length=1, max_length=80)
    reason: str = Field(..., min_length=1, max_length=512)
    label: str = Field(default="", max_length=160)
