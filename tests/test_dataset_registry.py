import json
from pathlib import Path

from tools.validate_dataset_registry import validate_registry


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/test_data_dataset_registry_2026-08-13.json"


def test_dataset_registry_is_valid_and_has_no_approved_external_data():
    assert validate_registry(REGISTRY) == []


def test_dataset_registry_rejects_downloaded_do_not_download_candidate(tmp_path):
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    candidate = next(item for item in payload["datasets"] if item["id"] == "ifkash-signatures")
    candidate["download_status"] = "private_external_only"
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert any("do_not_download entries must not be downloaded" in error for error in validate_registry(path))
