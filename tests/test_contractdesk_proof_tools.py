from __future__ import annotations

import json
from pathlib import Path

from tools.package_contractdesk_proof import build_package


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "web" / "cloud_workspace" / "proof-fixtures.json"


def test_build_package_is_content_addressed_and_explicitly_synthetic(tmp_path: Path) -> None:
    result = build_package(FIXTURE, tmp_path / "receipt")

    assert result["status"] == "pass"
    assert result["synthetic"] is True
    assert result["signature_status"] == "not_signed"
    assert result["event_count"] >= 1

    manifest = json.loads((tmp_path / "receipt" / "manifest.json").read_text())
    index = json.loads((tmp_path / "receipt" / "package_index.json").read_text())
    assert manifest["package_id"] == index["package_id"]
    assert manifest["receipt"]["receipt_sha256"] == index["files"]["receipt.ndjson"]["sha256"]
    assert manifest["output"]["document_artifact"] is None
    assert manifest["output"]["signature_artifact"] is None

