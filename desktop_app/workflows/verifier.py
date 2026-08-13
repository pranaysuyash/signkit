"""Output verification utilities for controlled workflow jobs.

These helpers provide a thin verification layer for outputs produced by the
workflow engine before the output becomes final for presentation.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ARTIFACT_RECEIPT_SCHEMA = "signkit.artifact_receipt.v1"
VISUAL_SIGNATURE_PLACEMENT = "visual_signature_placement_not_cryptographic_signature"


@dataclass(frozen=True)
class VerifyResult:
    """Simple verification status for a signed artifact."""

    ok: bool
    reason: str | None = None


@dataclass(frozen=True)
class ArtifactReceipt:
    """Content-addressed receipt for a locally produced signature-placement artifact.

    This contract records integrity and provenance metadata. It deliberately
    does not claim cryptographic signing, signer authentication, or legal
    non-repudiation.
    """

    schema: str
    artifact_type: str
    signature_semantics: str
    verification_status: str
    verification_reason: str | None
    artifact_id: str | None
    input_name: str
    input_sha256: str | None
    output_name: str
    output_sha256: str | None
    output_size_bytes: int
    generated_at: str
    operator_subject: str | None = None
    execution_id: str | None = None
    cryptographic_signature: bool = False
    certificate_fingerprint: str | None = None
    trust_scope: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def file_hash(path: str) -> str:
    """Compute SHA-256 of a filesystem file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _verification_reason(input_path: str, output_path: str) -> str | None:
    input_file = Path(input_path)
    output_file = Path(output_path)
    if not input_file.is_file():
        return "input_missing"
    if input_file.resolve() == output_file.resolve():
        return "in_place_not_allowed"
    if not output_file.is_file():
        return "output_missing"
    if output_file.stat().st_size <= 0:
        return "output_empty"
    if file_hash(str(input_file)) == file_hash(str(output_file)):
        return "unchanged_digest"
    return None


def verify_output(input_path: str, output_path: str) -> VerifyResult:
    """Verify output exists, is non-empty, and differs from input."""
    reason = _verification_reason(input_path, output_path)
    return VerifyResult(reason is None, reason)


def build_artifact_receipt(
    input_path: str,
    output_path: str,
    *,
    generated_at: str | None = None,
    operator_subject: str | None = None,
    execution_id: str | None = None,
    artifact_type: str = "local_signature_placement_pdf",
    signature_semantics: str = VISUAL_SIGNATURE_PLACEMENT,
    cryptographic_signature: bool = False,
    certificate_fingerprint: str | None = None,
    trust_scope: str | None = None,
) -> ArtifactReceipt:
    """Build a stable integrity receipt for a local output artifact."""

    input_file = Path(input_path)
    output_file = Path(output_path)
    reason = _verification_reason(input_path, output_path)
    input_digest = file_hash(str(input_file)) if input_file.is_file() else None
    output_digest = file_hash(str(output_file)) if output_file.is_file() else None
    verified = reason is None and output_digest is not None
    timestamp = generated_at or datetime.now(timezone.utc).isoformat()

    return ArtifactReceipt(
        schema=ARTIFACT_RECEIPT_SCHEMA,
        artifact_type=artifact_type,
        signature_semantics=signature_semantics,
        verification_status="verified" if verified else "rejected",
        verification_reason=None if verified else reason,
        artifact_id=f"sha256:{output_digest}" if verified else None,
        input_name=input_file.name,
        input_sha256=input_digest,
        output_name=output_file.name,
        output_sha256=output_digest,
        output_size_bytes=output_file.stat().st_size if output_file.is_file() else 0,
        generated_at=timestamp,
        operator_subject=operator_subject,
        execution_id=execution_id,
        cryptographic_signature=cryptographic_signature,
        certificate_fingerprint=certificate_fingerprint,
        trust_scope=trust_scope,
    )


def write_artifact_receipt(receipt: ArtifactReceipt, receipt_path: str) -> None:
    """Atomically persist a receipt without exposing partial JSON."""

    destination = Path(receipt_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(receipt.to_dict(), indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        dir=destination.parent,
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, destination)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
