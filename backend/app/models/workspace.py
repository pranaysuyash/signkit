"""Persistence models for the topology-aware workflow control plane.

These records deliberately store workflow metadata and event lineage, not source
PDFs, signatures, or signing assertions. The document/evidence layer remains a
separate, future capability with its own assurance requirements.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from backend.app.database import Base
from backend.app.db_types import GUID


class WorkspaceExecution(Base):
    """An owner-controlled run of a versioned workflow template."""

    __tablename__ = "workspace_executions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    owner_user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    template_code = Column(String(80), nullable=False, index=True)
    template_version = Column(Integer, nullable=False)
    topology = Column(String(20), nullable=False, default="cloud")
    status = Column(String(48), nullable=False, index=True)
    title = Column(String(180), nullable=False)
    participant_name = Column(String(160), nullable=False)
    participant_email = Column(String(255), nullable=False)
    reviewer_name = Column(String(160), nullable=False)
    reviewer_email = Column(String(255), nullable=False)
    effective_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class WorkspaceExecutionEvent(Base):
    """Append-only workflow event receipt without document or signature payloads."""

    __tablename__ = "workspace_execution_events"
    __table_args__ = (
        UniqueConstraint("execution_id", "sequence", name="uq_workspace_event_sequence"),
        UniqueConstraint(
            "execution_id",
            "actor_user_id",
            "event_type",
            "idem_key",
            name="uq_workspace_event_idempotent_replay",
        ),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    execution_id = Column(
        GUID(),
        ForeignKey("workspace_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence = Column(Integer, nullable=False)
    actor_user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type = Column(String(80), nullable=False)
    status_from = Column(String(48), nullable=True)
    status_to = Column(String(48), nullable=False)
    idem_key = Column(String(80), nullable=True, index=True)
    request_hash = Column(String(64), nullable=True, index=True)
    result_json = Column(Text, nullable=True)
    summary = Column(String(320), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
