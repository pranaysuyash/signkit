"""add metadata fields for local document inspection receipts

Revision ID: 9c4b7e2d1a6f
Revises: e42b7f8c91aa
Create Date: 2026-08-13 00:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c4b7e2d1a6f"
down_revision: Union[str, None] = "e42b7f8c91aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "workspace_execution_events",
        sa.Column("request_hash", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "workspace_execution_events",
        sa.Column("result_json", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_workspace_execution_events_request_hash",
        "workspace_execution_events",
        ["request_hash"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_workspace_execution_events_request_hash",
        table_name="workspace_execution_events",
    )
    op.drop_column("workspace_execution_events", "result_json")
    op.drop_column("workspace_execution_events", "request_hash")
