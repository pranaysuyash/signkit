"""add owner-scoped extraction assets and audit receipts

Revision ID: e42b7f8c91aa
Revises: d8a6c2f1b4a3
Create Date: 2026-08-12 00:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "e42b7f8c91aa"
down_revision: Union[str, None] = "d8a6c2f1b4a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _guid_type(bind: object):
    return postgresql.UUID(as_uuid=True) if bind.dialect.name == "postgresql" else sa.String(length=36)


def upgrade() -> None:
    bind = op.get_bind()
    guid = _guid_type(bind)

    with op.batch_alter_table("images") as batch_op:
        batch_op.add_column(sa.Column("workspace_execution_id", guid, nullable=True))
        batch_op.add_column(sa.Column("content_sha256", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("selection_json", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("retention_expires_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("deleted_by_user_id", guid, nullable=True))
        batch_op.create_foreign_key(
            "fk_images_workspace_execution_id",
            "workspace_executions",
            ["workspace_execution_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_foreign_key(
            "fk_images_deleted_by_user_id",
            "users",
            ["deleted_by_user_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.create_index("ix_images_workspace_execution_id", "images", ["workspace_execution_id"])
    op.create_index("ix_images_content_sha256", "images", ["content_sha256"])
    op.create_index("ix_images_retention_expires_at", "images", ["retention_expires_at"])
    op.create_index("ix_images_deleted_at", "images", ["deleted_at"])

    op.create_table(
        "extraction_audit_events",
        sa.Column("id", guid, primary_key=True, nullable=False),
        sa.Column("asset_id", guid, sa.ForeignKey("images.id", ondelete="SET NULL"), nullable=True),
        sa.Column("owner_user_id", guid, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(length=48), nullable=False),
        sa.Column("idem_key", sa.String(length=80), nullable=True),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False, server_default="200"),
        sa.Column("response_json", sa.Text(), nullable=True),
        sa.Column("artifact_path", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint(
            "owner_user_id",
            "event_type",
            "idem_key",
            name="uq_extraction_audit_idempotent_replay",
        ),
    )
    op.create_index("ix_extraction_audit_events_asset_id", "extraction_audit_events", ["asset_id"])
    op.create_index("ix_extraction_audit_events_owner_user_id", "extraction_audit_events", ["owner_user_id"])
    op.create_index("ix_extraction_audit_events_event_type", "extraction_audit_events", ["event_type"])
    op.create_index("ix_extraction_audit_events_idem_key", "extraction_audit_events", ["idem_key"])


def downgrade() -> None:
    op.drop_index("ix_extraction_audit_events_idem_key", table_name="extraction_audit_events")
    op.drop_index("ix_extraction_audit_events_event_type", table_name="extraction_audit_events")
    op.drop_index("ix_extraction_audit_events_owner_user_id", table_name="extraction_audit_events")
    op.drop_index("ix_extraction_audit_events_asset_id", table_name="extraction_audit_events")
    op.drop_table("extraction_audit_events")

    op.drop_index("ix_images_deleted_at", table_name="images")
    op.drop_index("ix_images_retention_expires_at", table_name="images")
    op.drop_index("ix_images_content_sha256", table_name="images")
    op.drop_index("ix_images_workspace_execution_id", table_name="images")
    with op.batch_alter_table("images") as batch_op:
        batch_op.drop_constraint("fk_images_deleted_by_user_id", type_="foreignkey")
        batch_op.drop_constraint("fk_images_workspace_execution_id", type_="foreignkey")
        batch_op.drop_column("deleted_by_user_id")
        batch_op.drop_column("deleted_at")
        batch_op.drop_column("retention_expires_at")
        batch_op.drop_column("selection_json")
        batch_op.drop_column("content_sha256")
        batch_op.drop_column("workspace_execution_id")
