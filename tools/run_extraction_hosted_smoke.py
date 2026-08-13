#!/usr/bin/env python3
"""Run a production-like authenticated extraction smoke against a temp database."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _png_bytes() -> bytes:
    from PIL import Image

    image = Image.new("RGB", (32, 32), "white")
    image.putpixel((8, 8), (0, 0, 0))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def _assert_status(response, expected: int, action: str) -> None:
    if response.status_code != expected:
        raise RuntimeError(
            f"{action} returned {response.status_code}, expected {expected}: {response.text}"
        )


def _register_and_login(client, email: str, password: str) -> str:
    registration = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    _assert_status(registration, 201, f"register {email}")
    login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    _assert_status(login, 200, f"login {email}")
    return login.json()["access_token"]


def run_smoke() -> dict[str, object]:
    repo_root = _repo_root()
    with tempfile.TemporaryDirectory(prefix="signkit-extraction-smoke-") as temp_dir:
        temp_root = Path(temp_dir)
        db_path = temp_root / "smoke.sqlite"
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        os.environ["JWT_SECRET"] = "smoke-test-secret-that-is-at-least-32-bytes"

        from alembic import command
        from alembic.config import Config

        alembic_config = Config(str(repo_root / "backend" / "alembic.ini"))
        alembic_config.set_main_option(
            "script_location",
            str(repo_root / "backend" / "alembic"),
        )
        command.upgrade(alembic_config, "head")

        from fastapi.testclient import TestClient

        from backend.app.main import app
        from backend.app.routers import extraction as extraction_router

        private_root = temp_root / "uploads"
        regions_root = private_root / "regions"
        private_root.mkdir()
        regions_root.mkdir()
        extraction_router.UPLOADS_DIR = private_root
        extraction_router.REGION_METADATA_DIR = regions_root
        extraction_router.os_uploads_dir = private_root

        with TestClient(app) as client:
            owner_token = _register_and_login(client, "smoke-owner@example.com", "owner-password-123")
            other_token = _register_and_login(client, "smoke-other@example.com", "other-password-123")
            owner_headers = {"Authorization": f"Bearer {owner_token}"}
            other_headers = {"Authorization": f"Bearer {other_token}"}

            upload = client.post(
                "/extraction/upload",
                files={"file": ("smoke.png", _png_bytes(), "image/png")},
                headers={**owner_headers, "Idempotency-Key": "smoke-upload-001"},
            )
            _assert_status(upload, 200, "upload")
            asset_id = upload.json()["id"]

            replay = client.post(
                "/extraction/upload",
                files={"file": ("smoke.png", _png_bytes(), "image/png")},
                headers={**owner_headers, "Idempotency-Key": "smoke-upload-001"},
            )
            _assert_status(replay, 200, "upload replay")
            if not replay.json().get("replayed"):
                raise RuntimeError("upload replay did not return replayed=true")

            selection_payload = {
                "session_id": asset_id,
                "x1": 1,
                "y1": 1,
                "x2": 20,
                "y2": 20,
                "color": "#111111",
                "threshold": 128,
            }
            foreign_select = client.post(
                "/extraction/select_region/",
                json=selection_payload,
                headers={**other_headers, "Idempotency-Key": "smoke-foreign-select-001"},
            )
            _assert_status(foreign_select, 404, "cross-owner select")

            selection = client.post(
                "/extraction/select_region/",
                json=selection_payload,
                headers={**owner_headers, "Idempotency-Key": "smoke-select-001"},
            )
            _assert_status(selection, 200, "select region")

            process_payload = {
                "session_id": asset_id,
                "x1": "1",
                "y1": "1",
                "x2": "20",
                "y2": "20",
                "color": "#111111",
                "threshold": "128",
            }
            processed = client.post(
                "/extraction/process_image/",
                data=process_payload,
                headers={**owner_headers, "Idempotency-Key": "smoke-process-001"},
            )
            _assert_status(processed, 200, "process image")

            exported = client.post(
                f"/extraction/assets/{asset_id}/export",
                headers={**owner_headers, "Idempotency-Key": "smoke-export-001"},
            )
            _assert_status(exported, 200, "export asset")
            with zipfile.ZipFile(BytesIO(exported.content)) as archive:
                if "manifest.json" not in archive.namelist():
                    raise RuntimeError("export archive is missing manifest.json")

            deleted = client.delete(
                f"/extraction/assets/{asset_id}",
                headers={**owner_headers, "Idempotency-Key": "smoke-delete-001"},
            )
            _assert_status(deleted, 200, "delete asset")
            if deleted.json().get("cleanup_status") != "complete":
                raise RuntimeError("delete did not report complete cleanup")

            audit = client.get(f"/extraction/assets/{asset_id}/audit", headers=owner_headers)
            _assert_status(audit, 200, "audit asset")
            event_types = [event["event_type"] for event in audit.json()]
            expected_events = {"upload", "select_region", "process_image", "export", "delete"}
            if not expected_events.issubset(event_types):
                raise RuntimeError(f"audit receipt set incomplete: {event_types}")

            foreign_delete = client.delete(
                f"/extraction/assets/{asset_id}",
                headers={**other_headers, "Idempotency-Key": "smoke-foreign-delete-001"},
            )
            _assert_status(foreign_delete, 404, "cross-owner delete")

        return {
            "status": "passed",
            "database": "temporary SQLite with Alembic head applied",
            "checks": [
                "register/login",
                "authenticated upload",
                "durable upload replay",
                "cross-owner select denial",
                "region selection",
                "image processing",
                "export manifest",
                "delete cleanup receipt",
                "post-delete audit receipt",
                "cross-owner delete denial",
            ],
        }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        result = run_smoke()
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
