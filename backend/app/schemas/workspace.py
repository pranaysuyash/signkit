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
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkspaceTransitionAction(str, Enum):
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
    participant_name: str = Field(..., min_length=2, max_length=160)
    participant_email: EmailStr
    reviewer_name: str = Field(..., min_length=2, max_length=160)
    reviewer_email: EmailStr
    effective_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class WorkspaceExecutionTransition(BaseModel):
    action: WorkspaceTransitionAction


class WorkspaceExecutionEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sequence: int
    event_type: str
    status_from: str | None
    status_to: str
    summary: str
    created_at: datetime


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
