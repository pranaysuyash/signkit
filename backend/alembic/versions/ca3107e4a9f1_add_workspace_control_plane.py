"""add workspace control plane

Revision ID: ca3107e4a9f1
Revises: f8a11e3c4b9d
Create Date: 2026-07-31 00:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "ca3107e4a9f1"
down_revision: Union[str, None] = "f8a11e3c4b9d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _guid_type(bind: object):
    return postgresql.UUID(as_uuid=True) if bind.dialect.name == "postgresql" else sa.String(length=36)


def upgrade() -> None:
    bind = op.get_bind()
    guid = _guid_type(bind)
    op.create_table(
        "workspace_executions",
        sa.Column("id", guid, primary_key=True, nullable=False),
        sa.Column("owner_user_id", guid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("template_code", sa.String(length=80), nullable=False),
        sa.Column("template_version", sa.Integer(), nullable=False),
        sa.Column("topology", sa.String(length=20), nullable=False, server_default="cloud"),
        sa.Column("status", sa.String(length=48), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("participant_name", sa.String(length=160), nullable=False),
        sa.Column("participant_email", sa.String(length=255), nullable=False),
        sa.Column("reviewer_name", sa.String(length=160), nullable=False),
        sa.Column("reviewer_email", sa.String(length=255), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_workspace_executions_owner_user_id", "workspace_executions", ["owner_user_id"])
    op.create_index("ix_workspace_executions_template_code", "workspace_executions", ["template_code"])
    op.create_index("ix_workspace_executions_status", "workspace_executions", ["status"])
    op.create_table(
        "workspace_execution_events",
        sa.Column("id", guid, primary_key=True, nullable=False),
        sa.Column("execution_id", guid, sa.ForeignKey("workspace_executions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", guid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("status_from", sa.String(length=48), nullable=True),
        sa.Column("status_to", sa.String(length=48), nullable=False),
        sa.Column("summary", sa.String(length=320), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("execution_id", "sequence", name="uq_workspace_event_sequence"),
    )
    op.create_index("ix_workspace_execution_events_execution_id", "workspace_execution_events", ["execution_id"])
    op.create_index("ix_workspace_execution_events_actor_user_id", "workspace_execution_events", ["actor_user_id"])


def downgrade() -> None:
    op.drop_index("ix_workspace_execution_events_actor_user_id", table_name="workspace_execution_events")
    op.drop_index("ix_workspace_execution_events_execution_id", table_name="workspace_execution_events")
    op.drop_table("workspace_execution_events")
    op.drop_index("ix_workspace_executions_status", table_name="workspace_executions")
    op.drop_index("ix_workspace_executions_template_code", table_name="workspace_executions")
    op.drop_index("ix_workspace_executions_owner_user_id", table_name="workspace_executions")
    op.drop_table("workspace_executions")
