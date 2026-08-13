"""Sensitivity tests for the release artifact ledger gate."""

from __future__ import annotations

import json
from pathlib import Path

from tools.release_artifact_ledger import build_ledger, validate_ledger


def test_ledger_records_sha256_and_rejects_unready_release(tmp_path: Path) -> None:
    artifact = tmp_path / "SignKit_test.zip"
    artifact.write_bytes(b"deterministic artifact")

    ledger = build_ledger(
        release_tag="v9.9.9",
        source_sha="a" * 40,
        release_url="https://example.test/releases/v9.9.9",
        rollback_artifact="not-recorded",
        generated_at="2026-08-13T00:00:00Z",
        artifact_specs=[
            f"SignKit test|Test|x86_64|{artifact}|not_verified|not_run",
        ],
    )

    assert ledger["artifacts"][0]["sha256"]
    assert ledger["artifacts"][0]["bytes"] == len(b"deterministic artifact")
    errors = validate_ledger(ledger, require_ready=True)
    assert any("signing_status" in error for error in errors)
    assert any("smoke_status" in error for error in errors)
    assert any("signing_evidence" in error for error in errors)
    assert any("smoke_evidence" in error for error in errors)
    assert any("rollback_artifact" in error for error in errors)


def test_ready_ledger_validates_after_statuses_are_recorded(tmp_path: Path) -> None:
    artifact = tmp_path / "SignKit_ready.zip"
    artifact.write_bytes(b"ready artifact")
    ledger = build_ledger(
        release_tag="v1.2.3",
        source_sha="b" * 40,
        release_url="https://example.test/releases/v1.2.3",
        rollback_artifact="v1.2.2-artifacts",
        generated_at="2026-08-13T00:00:00Z",
        artifact_specs=[
            f"SignKit ready|Test|x86_64|{artifact}|signed|passed|attestation://signkit-ready|smoke://signkit-ready",
        ],
    )

    assert validate_ledger(ledger, require_ready=True) == []
    assert ledger["artifacts"][0]["signing_evidence"] == "attestation://signkit-ready"
    assert ledger["artifacts"][0]["smoke_evidence"] == "smoke://signkit-ready"
    assert json.loads(json.dumps(ledger))["schema_version"] == "signkit.release-ledger.v1"


def test_ledger_rejects_tampered_digest() -> None:
    ledger = {
        "schema_version": "signkit.release-ledger.v1",
        "generated_at": "2026-08-13T00:00:00Z",
        "release_tag": "v1.2.3",
        "source_sha": "c" * 40,
        "release_url": "https://example.test/releases/v1.2.3",
        "rollback_artifact": "v1.2.2-artifacts",
        "artifacts": [
            {
                "name": "SignKit test",
                "platform": "Test",
                "architecture": "x86_64",
                "path": "SignKit_test.zip",
                "bytes": 1,
                "sha256": "0" * 63 + "g",
                "signing_status": "signed",
                "smoke_status": "passed",
            }
        ],
    }

    assert any("sha256" in error for error in validate_ledger(ledger, require_ready=True))
