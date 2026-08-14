#!/usr/bin/env python3
"""Prove local Alembic head downgrade and re-upgrade on disposable state."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


HEAD = "9c4b7e2d1a6f"
ROLLBACK_TARGET = "e42b7f8c91aa"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _revision(db_path: Path) -> str:
    from sqlalchemy import create_engine, text

    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.connect() as connection:
            return str(connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one())
    finally:
        engine.dispose()


def _event_columns(db_path: Path) -> set[str]:
    from sqlalchemy import create_engine, inspect

    engine = create_engine(f"sqlite:///{db_path}")
    try:
        return {column["name"] for column in inspect(engine).get_columns("workspace_execution_events")}
    finally:
        engine.dispose()


def _event_indexes(db_path: Path) -> set[str]:
    from sqlalchemy import create_engine, inspect

    engine = create_engine(f"sqlite:///{db_path}")
    try:
        return {index["name"] for index in inspect(engine).get_indexes("workspace_execution_events")}
    finally:
        engine.dispose()


def run_proof() -> dict[str, object]:
    from alembic import command
    from alembic.config import Config

    repo_root = _repo_root()
    with tempfile.TemporaryDirectory(prefix="signkit-migration-recovery-") as temp_dir:
        db_path = Path(temp_dir) / "recovery.sqlite"
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        os.environ["JWT_SECRET"] = "migration-recovery-secret-that-is-at-least-32-bytes"

        alembic_config = Config(str(repo_root / "backend" / "alembic.ini"))
        alembic_config.set_main_option(
            "script_location",
            str(repo_root / "backend" / "alembic"),
        )

        command.upgrade(alembic_config, "head")
        initial_revision = _revision(db_path)
        initial_columns = _event_columns(db_path)
        if not {"request_hash", "result_json"}.issubset(initial_columns):
            raise RuntimeError("Alembic head did not create document-inspection receipt fields")
        if "ix_workspace_execution_events_request_hash" not in _event_indexes(db_path):
            raise RuntimeError("Alembic head did not create the request-hash index")

        command.downgrade(alembic_config, ROLLBACK_TARGET)
        rolled_back_columns = _event_columns(db_path)
        if {"request_hash", "result_json"} & rolled_back_columns:
            raise RuntimeError("downgrade left document-inspection receipt fields behind")

        command.upgrade(alembic_config, "head")
        final_columns = _event_columns(db_path)
        if not {"request_hash", "result_json"}.issubset(final_columns):
            raise RuntimeError("re-upgrade did not restore document-inspection receipt fields")

        return {
            "status": "passed",
            "database": "temporary SQLite",
            "initial_head": initial_revision,
            "rollback_target": ROLLBACK_TARGET,
            "final_head": _revision(db_path),
            "checks": [
                "head creates receipt fields and request-hash index",
                "downgrade removes receipt fields",
                "re-upgrade restores receipt fields",
            ],
        }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        print(json.dumps(run_proof(), indent=2))
    except Exception as error:
        print(json.dumps({"status": "failed", "error": str(error)}, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
