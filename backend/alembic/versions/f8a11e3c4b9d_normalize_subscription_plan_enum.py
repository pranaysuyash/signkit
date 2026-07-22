"""normalize_subscription_plan_enum

Revision ID: f8a11e3c4b9d
Revises: b712aa6d45af
Create Date: 2026-06-29 17:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = "f8a11e3c4b9d"
down_revision: Union[str, None] = "b712aa6d45af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_type_name(bind: object, table: str, column: str) -> str | None:
    query = """
        SELECT udt_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = :table
          AND column_name = :column
    """
    result = bind.execute(
        text(query),
        {"table": table, "column": column},
    ).scalar()
    return result


def _enum_type_exists(bind: object, type_name: str) -> bool:
    return (
        bind.execute(
            text(
                """
                SELECT 1
                FROM pg_type
                WHERE typname = :type_name
                """
            ),
            {"type_name": type_name},
        ).scalar()
        is not None
    )


def _column_exists(bind: object, table: str, column: str) -> bool:
    inspector = sa.inspect(bind)
    return column in {col["name"] for col in inspector.get_columns(table)}


def _enum_in_use(bind: object, type_name: str, table: str, column: str) -> bool:
    result = bind.execute(
        text(
            """
            SELECT COUNT(*)
            FROM pg_attribute a
            JOIN pg_class c ON c.oid = a.attrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_type t ON t.oid = a.atttypid
            WHERE t.typname = :type_name
              AND n.nspname = 'public'
              AND c.relkind = 'r'
              AND NOT (c.relname = :table AND a.attname = :column)
        """
        ),
        {"type_name": type_name, "table": table, "column": column},
    ).scalar()
    if result is None:
        return False
    # If there are columns of this type on other tables and this is not the target
    # column, we keep the enum type in place.
    return int(result) > 0


def _create_enum_type(bind: object, enum_name: str) -> None:
    if not _enum_type_exists(bind, enum_name):
        op.execute(
            text(
                f"""
                CREATE TYPE {enum_name} AS ENUM ('Free', 'Pro', 'Enterprise')
                """
            )
        )


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    table = "users"
    column = "subscription_plan"
    legacy_enum = "subscriptionplan"
    canonical_enum = "subscription_plan"
    if not _column_exists(bind, table, column):
        return

    current_type = _column_type_name(bind, table, column)
    if current_type == canonical_enum:
        # Keep DB aligned with model definition going forward.
        _create_enum_type(bind, canonical_enum)
        if _enum_type_exists(bind, legacy_enum) and not _enum_in_use(
            bind, legacy_enum, table, column
        ):
            op.execute(text(f'DROP TYPE IF EXISTS "{legacy_enum}" CASCADE'))
        return

    if current_type == legacy_enum:
        _create_enum_type(bind, canonical_enum)
        op.execute(text(f'ALTER TABLE "{table}" ALTER COLUMN "{column}" DROP DEFAULT'))
        op.execute(
            text(
                f"""
                ALTER TABLE "{table}"
                ALTER COLUMN "{column}"
                TYPE {canonical_enum}
                USING "{column}"::text::{canonical_enum}
                """
            )
        )
        op.execute(
            text(
                f"""
                ALTER TABLE "{table}"
                ALTER COLUMN "{column}"
                SET DEFAULT 'Free'::{canonical_enum}
                """
            )
        )
        if not _enum_in_use(bind, legacy_enum, table, column):
            op.execute(text(f'DROP TYPE IF EXISTS "{legacy_enum}" CASCADE'))
        return

    # Fallback for any unexpected pre-existing schema state.
    _create_enum_type(bind, canonical_enum)
    op.execute(
        text(
            f"""
            ALTER TABLE "{table}"
            ALTER COLUMN "{column}"
            TYPE {canonical_enum}
            USING "{column}"::text::{canonical_enum}
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    table = "users"
    column = "subscription_plan"
    legacy_enum = "subscriptionplan"
    canonical_enum = "subscription_plan"
    if not _column_exists(bind, table, column):
        return

    current_type = _column_type_name(bind, table, column)
    if current_type != canonical_enum:
        return

    _create_enum_type(bind, legacy_enum)
    op.execute(text(f'ALTER TABLE "{table}" ALTER COLUMN "{column}" DROP DEFAULT'))
    op.execute(
        text(
            f"""
            ALTER TABLE "{table}"
            ALTER COLUMN "{column}"
            TYPE {legacy_enum}
            USING "{column}"::text::{legacy_enum}
            """
        )
    )
    op.execute(
        text(
            f"""
            ALTER TABLE "{table}"
            ALTER COLUMN "{column}"
            SET DEFAULT 'Free'::{legacy_enum}
            """
        )
    )
