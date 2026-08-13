# # # backend/alembic/env.py
# # import os
# # import sys
# # from logging.config import fileConfig

# # from sqlalchemy import engine_from_config
# # from sqlalchemy import pool
# # from alembic import context

# # # Add backend/app to sys.path
# # sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# # from app.models import User, Image  # Import only User and Image
# # from app.database import Base  # Import Base from your database setup

# # # this is the Alembic Config object, which provides
# # # access to the values within the .ini file in use.
# # config = context.config

# # # Interpret the config file for Python logging.
# # fileConfig(config.config_file_name)

# # # add your model's MetaData object here
# # # for 'autogenerate' support
# # target_metadata = Base.metadata

# # def run_migrations_offline():
# #     """Run migrations in 'offline' mode."""
# #     url = config.get_main_option("sqlalchemy.url")
# #     context.configure(
# #         url=url,
# #         target_metadata=target_metadata,
# #         literal_binds=True,
# #         dialect_opts={"paramstyle": "named"},
# #     )

# #     with context.begin_transaction():
# #         context.run_migrations()

# # def run_migrations_online():
# #     """Run migrations in 'online' mode."""
# #     connectable = engine_from_config(
# #         config.get_section(config.config_ini_section),
# #         prefix="sqlalchemy.",
# #         poolclass=pool.NullPool,
# #     )

# #     with connectable.connect() as connection:
# #         context.configure(
# #             connection=connection, target_metadata=target_metadata
# #         )

# #         with context.begin_transaction():
# #             context.run_migrations()

# # if context.is_offline_mode():
# #     run_migrations_offline()
# # else:
# #     run_migrations_online()


# from logging.config import fileConfig
# from sqlalchemy import engine_from_config
# from sqlalchemy import pool
# from alembic import context
# from app.models import Base  # Import all models
# from app.config import settings

# # this is the Alembic Config object, which provides
# # access to the values within the .ini file in use.
# config = context.config

# # Setup the database URL
# config.set_main_option("sqlalchemy.url", f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")

# # Interpret the config file for Python logging.
# # This line sets up loggers basically.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# # add your model's MetaData object here
# # for 'autogenerate' support
# target_metadata = Base.metadata

# def run_migrations_offline() -> None:
#     """Run migrations in 'offline' mode."""
#     url = config.get_main_option("sqlalchemy.url")
#     context.configure(
#         url=url,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )

#     with context.begin_transaction():
#         context.run_migrations()

# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode."""
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, 
#             target_metadata=target_metadata,
#             compare_type=True,
#             compare_server_default=True,
#         )

#         with context.begin_transaction():
#             context.run_migrations()

# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import Base and models
from backend.app.database import Base
from backend.app.models.user import User  # noqa
from backend.app.models.image import Image  # noqa
from backend.app.models.workspace import WorkspaceExecution, WorkspaceExecutionEvent  # noqa
from backend.app.models.extraction_audit import ExtractionAuditEvent  # noqa
from backend.app.config import settings

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url
config.set_main_option(
    "sqlalchemy.url",
    os.getenv("DATABASE_URL", settings.DATABASE_URL)
)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for autogenerate support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
