from __future__ import annotations

import json
from pathlib import Path

from desktop_app.workflows.verifier import (
    VISUAL_SIGNATURE_PLACEMENT,
    build_artifact_receipt,
    verify_output,
    write_artifact_receipt,
)


def test_artifact_receipt_verifies_changed_output_and_is_content_addressed(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    output = tmp_path / "signed-output.pdf"
    receipt_path = tmp_path / "receipts" / "artifact.json"
    source.write_bytes(b"source-pdf")
    output.write_bytes(b"source-pdf-with-visual-signature-placement")

    receipt = build_artifact_receipt(
        str(source),
        str(output),
        generated_at="2026-08-12T00:00:00+00:00",
        operator_subject="operator@example.test",
        execution_id="execution-1",
    )
    write_artifact_receipt(receipt, str(receipt_path))

    assert verify_output(str(source), str(output)).ok is True
    assert receipt.verification_status == "verified"
    assert receipt.artifact_id == f"sha256:{receipt.output_sha256}"
    assert receipt.signature_semantics == VISUAL_SIGNATURE_PLACEMENT
    assert json.loads(receipt_path.read_text())["execution_id"] == "execution-1"


def test_artifact_receipt_rejects_missing_and_unchanged_outputs(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    source.write_bytes(b"same-bytes")

    missing = build_artifact_receipt(str(source), str(tmp_path / "missing.pdf"))
    unchanged_path = tmp_path / "unchanged.pdf"
    unchanged_path.write_bytes(source.read_bytes())
    unchanged = build_artifact_receipt(str(source), str(unchanged_path))

    assert missing.verification_status == "rejected"
    assert missing.verification_reason == "output_missing"
    assert unchanged.verification_status == "rejected"
    assert unchanged.verification_reason == "unchanged_digest"


def test_artifact_receipt_rejects_in_place_output(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    source.write_bytes(b"source")

    receipt = build_artifact_receipt(str(source), str(source))

    assert receipt.verification_status == "rejected"
    assert receipt.verification_reason == "in_place_not_allowed"
