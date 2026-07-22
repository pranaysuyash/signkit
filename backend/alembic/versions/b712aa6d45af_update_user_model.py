"""update_user_model

Revision ID: b712aa6d45af
Revises: fe07219460da
Create Date: 2024-11-14 14:47:38.006662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.engine import Connection


# revision identifiers, used by Alembic.
revision: str = 'b712aa6d45af'
down_revision: Union[str, None] = 'fe07219460da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(bind: Connection, table: str, column: str) -> bool:
    inspector = sa.inspect(bind)
    return column in {c["name"] for c in inspector.get_columns(table)}


def _enum_type_exists(bind: Connection, type_name: str) -> bool:
    result = bind.execute(
        text(
            """
            SELECT 1
            FROM pg_type
            WHERE typname = :type_name
            """
        ),
        {"type_name": type_name},
    ).scalar()
    return result is not None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"
    table = "users"
    column = "subscription_plan"
    enum_name = "subscription_plan"

    if not _column_exists(bind, table, column):
        if is_postgres:
            if not _enum_type_exists(bind, enum_name):
                op.execute(
                    text(
                        """
                        CREATE TYPE subscription_plan AS ENUM ('Free', 'Pro', 'Enterprise')
                        """
                    )
                )

            op.add_column(
                table,
                sa.Column(
                    column,
                    sa.Enum(
                        "Free",
                        "Pro",
                        "Enterprise",
                        name=enum_name,
                        create_type=False,
                    ),
                    nullable=False,
                    server_default=sa.text("'Free'"),
                ),
            )
        else:
            op.add_column(
                table,
                sa.Column(
                    column,
                    sa.String(length=20),
                    nullable=False,
                    server_default=sa.text("'Free'"),
                ),
            )
            with op.batch_alter_table(table) as batch_op:
                batch_op.alter_column(
                    column,
                    existing_type=sa.String(length=20),
                    nullable=False,
                )
                batch_op.create_check_constraint(
                    "ck_users_subscription_plan",
                    f"{column} IN ('Free', 'Pro', 'Enterprise')",
                )
    else:
        op.execute(
            text(
                f"""
                UPDATE {table}
                SET {column} = 'Free'
                WHERE {column} IS NULL
                """
            )
        )
        if is_postgres:
            op.alter_column(
                table,
                column,
                existing_type=sa.Enum(
                    "Free",
                    "Pro",
                    "Enterprise",
                    name=enum_name,
                    create_type=False,
                ),
                nullable=False,
                server_default=sa.text("'Free'"),
            )
        else:
            with op.batch_alter_table(table) as batch_op:
                batch_op.alter_column(
                    column,
                    existing_type=sa.String(length=20),
                    nullable=False,
                )


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"
    table = "users"
    column = "subscription_plan"
    enum_name = "subscription_plan"

    if _column_exists(bind, table, column):
        if is_postgres:
            op.drop_column(table, column)
            op.execute(
                text(f"DROP TYPE IF EXISTS {enum_name} CASCADE")
            )
        else:
            with op.batch_alter_table(table) as batch_op:
                batch_op.drop_constraint("ck_users_subscription_plan", type_="check")
                batch_op.drop_column(column)
