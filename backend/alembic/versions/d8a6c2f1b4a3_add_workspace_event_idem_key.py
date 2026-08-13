"""add workspace execution event idempotency key

Revision ID: d8a6c2f1b4a3
Revises: ca3107e4a9f1
Create Date: 2026-08-12 00:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d8a6c2f1b4a3"
down_revision: Union[str, None] = "ca3107e4a9f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "workspace_execution_events",
        sa.Column("idem_key", sa.String(length=80), nullable=True),
    )
    op.create_index(
        "ix_workspace_execution_events_idem_key",
        "workspace_execution_events",
        ["idem_key"],
    )
    op.create_index(
        "uq_workspace_event_idempotent_replay",
        "workspace_execution_events",
        ["execution_id", "actor_user_id", "event_type", "idem_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_workspace_event_idempotent_replay",
        table_name="workspace_execution_events",
    )
    op.drop_index(
        "ix_workspace_execution_events_idem_key",
        table_name="workspace_execution_events",
    )
    op.drop_column("workspace_execution_events", "idem_key")
