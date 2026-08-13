from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from io import BytesIO
import uuid
import zipfile
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base, get_db
from backend.app.models.image import Image as ImageModel
from backend.app.models.user import User
from backend.app.models.workspace import WorkspaceExecution
from backend.app.routers.extraction import router as extraction_router
from backend.app.utils.auth import create_access_token


def _png_payload(color: str = "#f8f9fa") -> bytes:
    image = Image.new("RGB", (16, 16), color=color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@contextmanager
def _hosted_client(tmp_path):
    database_path = tmp_path / "extraction-hosted.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    seed_session = session_factory()
    owner = User(id=uuid.uuid4(), email="owner@example.com", hashed_password="x" * 80)
    other_owner = User(id=uuid.uuid4(), email="other@example.com", hashed_password="x" * 80)
    seed_session.add_all([owner, other_owner])
    seed_session.commit()
    seed_session.refresh(owner)
    seed_session.refresh(other_owner)

    app = FastAPI()
    app.include_router(extraction_router, prefix="/extraction")

    def override_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db

    def headers(user: User, idem_key: str | None = None) -> dict[str, str]:
        result = {"Authorization": f"Bearer {create_access_token({'sub': str(user.id)})}"}
        if idem_key:
            result["Idempotency-Key"] = idem_key
        return result

    try:
        with TestClient(app) as client:
            yield client, session_factory, owner, other_owner, headers
    finally:
        seed_session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _upload(client, headers, user, payload=None, idem_key=None, workspace_execution_id=None):
    data = {}
    if workspace_execution_id:
        data["workspace_execution_id"] = str(workspace_execution_id)
    return client.post(
        "/extraction/upload",
        files={"file": ("signature.png", payload or _png_payload(), "image/png")},
        data=data,
        headers=headers(user, idem_key),
    )


def test_extraction_requires_authentication_and_enforces_owner_and_workspace_scope(tmp_path):
    with _hosted_client(tmp_path) as (client, session_factory, owner, other_owner, headers):
        unauthenticated = client.post(
            "/extraction/upload",
            files={"file": ("signature.png", _png_payload(), "image/png")},
        )
        assert unauthenticated.status_code == 401

        other_session = session_factory()
        foreign_execution = WorkspaceExecution(
            id=uuid.uuid4(),
            owner_user_id=other_owner.id,
            template_code="hr-onboarding-core",
            template_version=1,
            topology="cloud",
            status="pending_review",
            title="Foreign execution",
            participant_name="Other Participant",
            participant_email="participant@example.com",
            reviewer_name="Other Reviewer",
            reviewer_email="reviewer@example.com",
        )
        other_session.add(foreign_execution)
        other_session.commit()
        foreign_execution_id = foreign_execution.id
        other_session.close()

        foreign_workspace_upload = _upload(
            client,
            headers,
            owner,
            workspace_execution_id=foreign_execution_id,
        )
        assert foreign_workspace_upload.status_code == 404

        owner_upload = _upload(client, headers, owner, idem_key="owner-upload-001")
        assert owner_upload.status_code == 200
        asset_id = owner_upload.json()["id"]

        assert client.get("/extraction/assets", headers=headers(other_owner)).json()["assets"] == []
        foreign_select = client.post(
            "/extraction/select_region/",
            json={
                "session_id": asset_id,
                "x1": 1,
                "y1": 1,
                "x2": 15,
                "y2": 15,
                "color": "#111111",
                "threshold": 128,
            },
            headers=headers(other_owner),
        )
        assert foreign_select.status_code == 404

        foreign_delete = client.delete(
            f"/extraction/assets/{asset_id}",
            headers=headers(other_owner, "foreign-delete-001"),
        )
        assert foreign_delete.status_code == 404


def test_upload_selection_and_processing_replay_and_conflict_are_durable(tmp_path):
    with _hosted_client(tmp_path) as (client, _, owner, _, headers):
        payload = _png_payload()
        first = _upload(client, headers, owner, payload, "upload-replay-001")
        replay = _upload(client, headers, owner, payload, "upload-replay-001")
        conflict = _upload(client, headers, owner, _png_payload("#111111"), "upload-replay-001")

        assert first.status_code == 200
        assert replay.status_code == 200
        assert replay.json()["id"] == first.json()["id"]
        assert replay.json()["replayed"] is True
        assert conflict.status_code == 409
        asset_id = first.json()["id"]

        selection_payload = {
            "session_id": asset_id,
            "x1": 1,
            "y1": 1,
            "x2": 15,
            "y2": 15,
            "color": "#111111",
            "threshold": 128,
        }
        selection = client.post(
            "/extraction/select_region/",
            json=selection_payload,
            headers=headers(owner, "selection-replay-001"),
        )
        selection_replay = client.post(
            "/extraction/select_region/",
            json=selection_payload,
            headers=headers(owner, "selection-replay-001"),
        )
        assert selection.status_code == 200
        assert selection_replay.status_code == 200
        assert selection_replay.json()["replayed"] is True
        assert selection_replay.json()["receipt_id"] == selection.json()["receipt_id"]

        process_data = {
            "session_id": asset_id,
            "x1": "1",
            "y1": "1",
            "x2": "15",
            "y2": "15",
            "color": "#111111",
            "threshold": "128",
        }
        processed = client.post(
            "/extraction/process_image/",
            data=process_data,
            headers=headers(owner, "process-replay-001"),
        )
        processed_replay = client.post(
            "/extraction/process_image/",
            data=process_data,
            headers=headers(owner, "process-replay-001"),
        )
        assert processed.status_code == 200
        assert processed_replay.status_code == 200
        assert processed.headers["X-Extraction-Receipt"] == processed_replay.headers["X-Extraction-Receipt"]
        assert processed_replay.headers["X-Extraction-Replayed"] == "true"
        assert processed.content == processed_replay.content

        audit = client.get(f"/extraction/assets/{asset_id}/audit", headers=headers(owner))
        assert audit.status_code == 200
        assert {event["event_type"] for event in audit.json()} >= {"upload", "select_region", "process_image"}


def test_concurrent_upload_retry_converges_on_one_owner_asset(tmp_path):
    with _hosted_client(tmp_path) as (client, _, owner, _, headers):
        def submit():
            return _upload(client, headers, owner, _png_payload(), "concurrent-upload-001")

        with ThreadPoolExecutor(max_workers=2) as executor:
            responses = list(executor.map(lambda _: submit(), range(2)))

        assert {response.status_code for response in responses} == {200}
        assert len({response.json()["id"] for response in responses}) == 1


def test_export_delete_and_audit_receipts_survive_file_deletion(tmp_path):
    with _hosted_client(tmp_path) as (client, session_factory, owner, _, headers):
        upload = _upload(client, headers, owner, idem_key="export-delete-upload-001")
        asset_id = upload.json()["id"]
        selection = client.post(
            "/extraction/select_region/",
            json={
                "session_id": asset_id,
                "x1": 1,
                "y1": 1,
                "x2": 15,
                "y2": 15,
                "color": "#111111",
                "threshold": 128,
            },
            headers=headers(owner, "export-delete-selection-001"),
        )
        assert selection.status_code == 200

        export = client.post(
            f"/extraction/assets/{asset_id}/export",
            headers=headers(owner, "export-001"),
        )
        assert export.status_code == 200
        with zipfile.ZipFile(BytesIO(export.content)) as archive:
            assert "manifest.json" in archive.namelist()
            assert any(name.endswith(".png") for name in archive.namelist())

        db = session_factory()
        asset_path = db.query(ImageModel).filter_by(id=asset_id).one().file_path
        db.close()

        deleted = client.delete(
            f"/extraction/assets/{asset_id}",
            headers=headers(owner, "delete-001"),
        )
        deleted_replay = client.delete(
            f"/extraction/assets/{asset_id}",
            headers=headers(owner, "delete-001"),
        )
        assert deleted.status_code == 200
        assert deleted.json()["cleanup_status"] == "complete"
        assert deleted_replay.status_code == 200
        assert deleted_replay.json()["replayed"] is True
        assert not Path(asset_path).exists()

        audit = client.get(f"/extraction/assets/{asset_id}/audit", headers=headers(owner))
        assert audit.status_code == 200
        assert audit.json()[-1]["event_type"] == "delete"

        without_key = client.delete(f"/extraction/assets/{asset_id}", headers=headers(owner))
        assert without_key.status_code == 404
