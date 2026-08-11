"""initial_migration

Revision ID: fe07219460da
Revises: 
Create Date: 2024-11-14 13:38:24.758450

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'fe07219460da'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())
    guid = postgresql.UUID(as_uuid=True) if bind.dialect.name == "postgresql" else sa.String(length=36)
    subscription_plan = sa.Enum(
        "Free",
        "Pro",
        "Enterprise",
        name="subscription_plan",
    )

    # The historical revision was generated as an empty placeholder. Keep this
    # bootstrap idempotent so databases created manually before Alembic remain
    # valid while new environments receive the canonical base schema.
    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", guid, primary_key=True, nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("hashed_password", sa.String(length=255), nullable=False),
            sa.Column(
                "subscription_plan",
                subscription_plan,
                nullable=False,
                server_default=sa.text("'Free'"),
            ),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("email"),
        )
        op.create_index("ix_users_email", "users", ["email"])

    if "images" not in existing_tables:
        op.create_table(
            "images",
            sa.Column("id", guid, primary_key=True, nullable=False),
            sa.Column("user_id", guid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("filename", sa.String(), nullable=False),
            sa.Column("file_path", sa.String(), nullable=False),
            sa.Column("content_type", sa.String(), nullable=False),
            sa.Column("original_image_id", guid, sa.ForeignKey("images.id", ondelete="CASCADE"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )

    if "pdf_audit_logs" not in existing_tables:
        op.create_table(
            "pdf_audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("pdf_path", sa.String(length=512), nullable=False),
            sa.Column("pdf_name", sa.String(length=255), nullable=False),
            sa.Column("operation", sa.String(length=50), nullable=False),
            sa.Column("user_email", sa.String(length=255), nullable=True),
            sa.Column("details", sa.Text(), nullable=True),
            sa.Column("page_number", sa.Integer(), nullable=True),
            sa.Column("signature_path", sa.String(length=512), nullable=True),
            sa.Column("x", sa.Integer(), nullable=True),
            sa.Column("y", sa.Integer(), nullable=True),
            sa.Column("width", sa.Integer(), nullable=True),
            sa.Column("height", sa.Integer(), nullable=True),
            sa.Column("output_path", sa.String(length=512), nullable=True),
            sa.Column("signature_count", sa.Integer(), nullable=True),
            sa.Column("error_type", sa.String(length=100), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.true()),
        )
        op.create_index("ix_pdf_audit_logs_pdf_path", "pdf_audit_logs", ["pdf_path"])
        op.create_index("ix_pdf_audit_logs_operation", "pdf_audit_logs", ["operation"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())
    if "pdf_audit_logs" in existing_tables:
        op.drop_index("ix_pdf_audit_logs_operation", table_name="pdf_audit_logs")
        op.drop_index("ix_pdf_audit_logs_pdf_path", table_name="pdf_audit_logs")
        op.drop_table("pdf_audit_logs")
    if "images" in existing_tables:
        op.drop_table("images")
    if "users" in existing_tables:
        op.drop_index("ix_users_email", table_name="users")
        op.drop_table("users")
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS subscription_plan")
