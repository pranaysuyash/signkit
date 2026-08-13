"""Package the deterministic ContractDesk fixture as a synthetic audit receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = REPO_ROOT / "web" / "cloud_workspace" / "proof-fixtures.json"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "expansion" / "artifacts" / "contractdesk_stage1_synthetic_receipt"


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _atomic_write(path: Path, content: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return _sha256(content)


def build_package(fixture_path: Path, output_dir: Path) -> dict[str, Any]:
    fixture_bytes = fixture_path.read_bytes()
    fixture = json.loads(fixture_bytes)
    executions = fixture.get("executions") or []
    if len(executions) != 1:
        raise ValueError("ContractDesk proof packaging requires exactly one execution fixture")

    execution = executions[0]
    manifest = execution.get("manifest") or {}
    events = execution.get("events") or []
    receipt_lines = b"".join(_canonical_json(event) for event in events)
    fixture_sha256 = _sha256(fixture_bytes)
    receipt_sha256 = _sha256(receipt_lines)
    package_id = f"{fixture.get('scenario_id', 'contractdesk-proof')}-{fixture_sha256[:12]}"

    audit_manifest = {
        "schema_version": "1.0",
        "package_id": package_id,
        "artifact_type": "synthetic_control_plane_audit",
        "synthetic": True,
        "signature_status": "not_signed",
        "source": {
            "fixture_path": str(fixture_path.relative_to(REPO_ROOT)),
            "fixture_sha256": fixture_sha256,
            "scenario_id": fixture.get("scenario_id"),
        },
        "workflow": manifest.get("workflow", "contractdesk-stage1"),
        "input_hash": manifest.get("input_hash"),
        "decision_rules": manifest.get("decision_rules"),
        "expected_stages": manifest.get("stages", []),
        "receipt": {
            "event_count": len(events),
            "receipt_file": "receipt.ndjson",
            "receipt_sha256": receipt_sha256,
        },
        "output": {
            "state": "synthetic export complete",
            "document_artifact": None,
            "signature_artifact": None,
        },
        "boundary": "Metadata-only proof package. It is not a signed document, certificate, or hosted API export.",
    }
    manifest_bytes = _canonical_json(audit_manifest)
    index = {
        "schema_version": "1.0",
        "package_id": package_id,
        "artifact_type": "synthetic_control_plane_audit",
        "files": {
            "manifest.json": {"sha256": _sha256(manifest_bytes)},
            "receipt.ndjson": {"sha256": receipt_sha256},
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_hash = _atomic_write(output_dir / "manifest.json", manifest_bytes)
    receipt_hash = _atomic_write(output_dir / "receipt.ndjson", receipt_lines)
    index_hash = _atomic_write(output_dir / "package_index.json", _canonical_json(index))
    return {
        "status": "pass",
        "package_id": package_id,
        "output_dir": str(output_dir),
        "manifest_sha256": manifest_hash,
        "receipt_sha256": receipt_hash,
        "package_index_sha256": index_hash,
        "event_count": len(events),
        "synthetic": True,
        "signature_status": "not_signed",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        result = build_package(args.fixture.resolve(), args.output_dir.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"contractdesk proof packaging failed: {exc}")
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

