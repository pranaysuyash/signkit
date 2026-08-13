"""Append-only ownership, retry, deletion, and export receipts."""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from backend.app.database import Base
from backend.app.db_types import GUID


class ExtractionAuditEvent(Base):
    """A privacy-safe receipt for one extraction asset operation."""

    __tablename__ = "extraction_audit_events"
    __table_args__ = (
        UniqueConstraint(
            "owner_user_id",
            "event_type",
            "idem_key",
            name="uq_extraction_audit_idempotent_replay",
        ),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    asset_id = Column(
        GUID(),
        ForeignKey("images.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    owner_user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type = Column(String(48), nullable=False, index=True)
    idem_key = Column(String(80), nullable=True, index=True)
    request_hash = Column(String(64), nullable=False)
    status_code = Column(Integer, nullable=False, default=200)
    response_json = Column(Text, nullable=True)
    artifact_path = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
