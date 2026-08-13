import json
from pathlib import Path

from desktop_app.library import storage


def test_library_deletion_removes_sidecar_and_records_complete_receipt(tmp_path, monkeypatch) -> None:
    library_dir = tmp_path / "signatures"
    library_dir.mkdir()
    monkeypatch.setattr(storage, "LIB_DIR", str(library_dir))

    image = library_dir / "signature.png"
    sidecar = library_dir / "signature.json"
    image.write_bytes(b"signature-bytes")
    sidecar.write_text('{"source": "test"}\n', encoding="utf-8")

    result = storage.delete_item_with_result(str(image))

    assert result.status == "deleted"
    assert result.primary_deleted is True
    assert result.cleanup_complete is True
    assert not image.exists()
    assert not sidecar.exists()

    receipts = list((library_dir / storage.DELETION_RECEIPT_DIRNAME).glob("*.json"))
    assert len(receipts) == 1
    payload = json.loads(receipts[0].read_text(encoding="utf-8"))
    assert payload["schema"] == "signkit.library_deletion_receipt.v1"
    assert payload["cleanup_status"] == "complete"
    assert payload["item_name"] == "signature.png"


def test_library_deletion_surfaces_sidecar_cleanup_failure(tmp_path, monkeypatch) -> None:
    library_dir = tmp_path / "signatures"
    library_dir.mkdir()
    monkeypatch.setattr(storage, "LIB_DIR", str(library_dir))

    image = library_dir / "signature.png"
    sidecar = library_dir / "signature.json"
    image.write_bytes(b"signature-bytes")
    sidecar.mkdir()

    result = storage.delete_item_with_result(str(image))

    assert result.status == "cleanup_incomplete"
    assert result.primary_deleted is True
    assert result.cleanup_complete is False
    assert not image.exists()
    assert sidecar.is_dir()


def test_library_deletion_rejects_path_outside_library(tmp_path, monkeypatch) -> None:
    library_dir = tmp_path / "signatures"
    library_dir.mkdir()
    monkeypatch.setattr(storage, "LIB_DIR", str(library_dir))
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"do not delete")

    result = storage.delete_item_with_result(str(outside))

    assert result.status == "not_deleted"
    assert result.primary_deleted is False
    assert outside.exists()


def test_library_cleanup_recovery_is_explicit_and_updates_receipt(tmp_path, monkeypatch) -> None:
    library_dir = tmp_path / "signatures"
    library_dir.mkdir()
    monkeypatch.setattr(storage, "LIB_DIR", str(library_dir))

    image = library_dir / "signature.png"
    sidecar = library_dir / "signature.json"
    image.write_bytes(b"signature-bytes")
    sidecar.write_text('{"source": "test"}\n', encoding="utf-8")

    original_remove = storage.os.remove
    failed_once = {"value": True}

    def fail_sidecar_once(path: str) -> None:
        if path == str(sidecar) and failed_once["value"]:
            failed_once["value"] = False
            raise OSError("simulated sidecar permission failure")
        original_remove(path)

    monkeypatch.setattr(storage.os, "remove", fail_sidecar_once)
    result = storage.delete_item_with_result(str(image))
    assert result.status == "cleanup_incomplete"
    assert result.primary_deleted is True
    assert sidecar.exists()

    monkeypatch.setattr(storage.os, "remove", original_remove)
    assert storage.incomplete_deletion_count() == 1
    summary = storage.recover_incomplete_deletions()

    assert summary == {"scanned": 1, "recovered": 1, "remaining": 0}
    assert not sidecar.exists()
    receipts = list((library_dir / storage.DELETION_RECEIPT_DIRNAME).glob("*.json"))
    payload = json.loads(receipts[0].read_text(encoding="utf-8"))
    assert payload["cleanup_status"] == "complete"
    assert "recovered_at" in payload
    assert storage.incomplete_deletion_count() == 0


def test_library_cleanup_recovery_does_not_remove_sidecar_directories(tmp_path, monkeypatch) -> None:
    library_dir = tmp_path / "signatures"
    library_dir.mkdir()
    monkeypatch.setattr(storage, "LIB_DIR", str(library_dir))

    image = library_dir / "signature.png"
    sidecar = library_dir / "signature.json"
    image.write_bytes(b"signature-bytes")
    sidecar.mkdir()

    result = storage.delete_item_with_result(str(image))
    assert result.status == "cleanup_incomplete"
    summary = storage.recover_incomplete_deletions()

    assert summary == {"scanned": 1, "recovered": 0, "remaining": 1}
    assert sidecar.is_dir()
