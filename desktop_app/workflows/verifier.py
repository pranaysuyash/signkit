"""Output verification utilities for controlled workflow jobs.

These helpers provide a thin verification layer for outputs produced by the
workflow engine before the output becomes final for presentation.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class VerifyResult:
    """Simple verification status for a signed artifact."""

    ok: bool
    reason: str | None = None


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


def verify_output(input_path: str, output_path: str) -> VerifyResult:
    """Verify output exists, is non-empty, and differs from input."""
    if not os.path.exists(output_path):
        return VerifyResult(False, "output_missing")

    if output_path == input_path:
        return VerifyResult(False, "in_place_not_allowed")

    if os.path.getsize(output_path) <= 0:
        return VerifyResult(False, "output_empty")

    if file_hash(input_path) == file_hash(output_path):
        return VerifyResult(False, "unchanged_digest")

    return VerifyResult(True, None)
