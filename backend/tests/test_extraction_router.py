from __future__ import annotations

from io import BytesIO
import os

from PIL import Image

from backend.app.services.upload_lifecycle import cleanup_expired_uploads


def _png_payload() -> bytes:
    image = Image.new("RGB", (16, 16), color="#f8f9fa")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_upload_image_contract_does_not_return_public_upload_path(
    tmp_path,
    monkeypatch,
    extraction_client,
):
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setattr("backend.app.routers.extraction.os_uploads_dir", uploads_dir)
    monkeypatch.setattr("backend.app.routers.extraction.REGION_METADATA_DIR", uploads_dir / "regions")

    client, _, _ = extraction_client
    response = client.post(
        "/extraction/upload",
        files={"file": ("signature.png", _png_payload(), "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["file_path"] is None
    assert "/uploads/images/" not in str(payload.get("file_path"))
    uploaded_files = list(uploads_dir.iterdir())
    assert len(uploaded_files) == 1
    assert uploaded_files[0].suffix == ".png"
    assert uploaded_files[0].stat().st_mode & 0o077 == 0


def test_expired_private_upload_artifacts_are_removed_but_unknown_files_are_preserved(
    tmp_path,
):
    uploads_dir = tmp_path / "uploads"
    metadata_dir = uploads_dir / "regions"
    metadata_dir.mkdir(parents=True)
    stale_image = uploads_dir / "session.png"
    stale_region = metadata_dir / "session.json"
    preserved_file = uploads_dir / "operator-note.txt"
    for path in (stale_image, stale_region, preserved_file):
        path.write_text("fixture", encoding="utf-8")
        os.utime(path, (100.0, 100.0))

    removed = cleanup_expired_uploads(
        uploads_dir,
        metadata_dir,
        now=200.0,
        retention_seconds=60,
    )

    assert removed == 2
    assert not stale_image.exists()
    assert not stale_region.exists()
    assert preserved_file.exists()


def test_invalid_image_payload_is_rejected_without_creating_an_artifact(
    tmp_path,
    monkeypatch,
    extraction_client,
):
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setattr("backend.app.routers.extraction.os_uploads_dir", uploads_dir)

    client, _, _ = extraction_client
    response = client.post(
        "/extraction/upload",
        files={"file": ("signature.png", b"not-an-image", "image/png")},
    )

    assert response.status_code == 400
    assert list(uploads_dir.iterdir()) == []


def test_upload_rejects_oversized_payload_and_dimensions(
    tmp_path,
    monkeypatch,
    extraction_client,
):
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setattr("backend.app.routers.extraction.os_uploads_dir", uploads_dir)
    monkeypatch.setattr("backend.app.security.UploadSecurity.MAX_FILE_SIZE", 32)

    client, _, _ = extraction_client
    oversized_payload_response = client.post(
        "/extraction/upload",
        files={"file": ("signature.png", _png_payload(), "image/png")},
    )

    assert oversized_payload_response.status_code == 400
    assert list(uploads_dir.iterdir()) == []

    monkeypatch.setattr("backend.app.security.UploadSecurity.MAX_FILE_SIZE", 50 * 1024 * 1024)
    monkeypatch.setattr("backend.app.security.UploadSecurity.MAX_IMAGE_WIDTH", 8)
    oversized_dimensions_response = client.post(
        "/extraction/upload",
        files={"file": ("signature.png", _png_payload(), "image/png")},
    )

    assert oversized_dimensions_response.status_code == 400
    assert list(uploads_dir.iterdir()) == []


def test_select_region_rejects_invalid_session_id_without_writing_metadata(
    tmp_path,
    monkeypatch,
    extraction_client,
):
    uploads_dir = tmp_path / "uploads"
    metadata_dir = uploads_dir / "regions"
    metadata_dir.mkdir(parents=True)
    monkeypatch.setattr("backend.app.routers.extraction.os_uploads_dir", uploads_dir)
    monkeypatch.setattr("backend.app.routers.extraction.REGION_METADATA_DIR", metadata_dir)

    client, _, _ = extraction_client
    response = client.post(
        "/extraction/select_region/",
        json={
            "session_id": "not-a-uuid",
            "x1": 1,
            "y1": 1,
            "x2": 15,
            "y2": 15,
            "color": "#111111",
            "threshold": 128,
        },
    )

    assert response.status_code == 404
    assert list(metadata_dir.iterdir()) == []


def test_select_region_contract_does_not_return_public_upload_path(
    tmp_path,
    monkeypatch,
    extraction_client,
):
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setattr("backend.app.routers.extraction.os_uploads_dir", uploads_dir)
    monkeypatch.setattr("backend.app.routers.extraction.REGION_METADATA_DIR", uploads_dir / "regions")

    client, _, _ = extraction_client
    upload_response = client.post(
        "/extraction/upload",
        files={"file": ("signature.png", _png_payload(), "image/png")},
    )
    upload_payload = upload_response.json()
    assert upload_response.status_code == 200

    select_response = client.post(
        "/extraction/select_region/",
        json={
            "session_id": upload_payload["id"],
            "x1": 1,
            "y1": 1,
            "x2": 15,
            "y2": 15,
            "color": "#111111",
            "threshold": 128,
        },
    )

    assert select_response.status_code == 200
    payload = select_response.json()
    assert payload["file_path"] is None
    assert "/uploads/images/" not in str(payload.get("file_path"))
