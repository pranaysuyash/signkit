"""API contracts for owner-scoped extraction assets and receipts."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExtractionAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    content_type: str
    workspace_execution_id: UUID | None = None
    created_at: datetime
    retention_expires_at: datetime | None = None
    deleted_at: datetime | None = None


class ExtractionAuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    asset_id: UUID | None = None
    event_type: str
    idem_key: str | None = None
    status_code: int
    response_json: str | None = None
    created_at: datetime


class ExtractionReceiptResponse(BaseModel):
    receipt_id: UUID
    asset: ExtractionAssetResponse | None = None
    event_type: str
    replayed: bool = False
    cleanup_status: str | None = None
