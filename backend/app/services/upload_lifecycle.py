"""Lifecycle controls for private extraction upload artifacts.

The extraction API is currently a local/private companion to the desktop app,
not an authenticated hosted asset service. This module keeps that boundary
explicit by bounding retention and removing stale image/selection artifacts.
"""

from __future__ import annotations

import os
import time
from pathlib import Path


DEFAULT_UPLOAD_RETENTION_SECONDS = 24 * 60 * 60
_UPLOAD_SUFFIXES = {".png", ".jpg", ".jpeg", ".part"}


def upload_retention_seconds() -> int:
    """Return a safe, operator-configurable retention window in seconds."""
    raw_value = os.getenv(
        "SIGNKIT_UPLOAD_RETENTION_SECONDS",
        str(DEFAULT_UPLOAD_RETENTION_SECONDS),
    )
    try:
        return max(60, int(raw_value))
    except (TypeError, ValueError):
        return DEFAULT_UPLOAD_RETENTION_SECONDS


def cleanup_expired_uploads(
    uploads_dir: Path,
    metadata_dir: Path,
    *,
    now: float | None = None,
    retention_seconds: int | None = None,
) -> int:
    """Delete stale private upload and region-metadata artifacts.

    Only known extraction suffixes are eligible. Unexpected files in the
    configured directories are preserved for operator review.
    """
    retention = upload_retention_seconds() if retention_seconds is None else max(60, retention_seconds)
    cutoff = (time.time() if now is None else now) - retention
    removed = 0

    for directory, suffixes in (
        (uploads_dir, _UPLOAD_SUFFIXES),
        (metadata_dir, {".json"}),
    ):
        if not directory.exists():
            continue
        for candidate in directory.iterdir():
            if not candidate.is_file() or candidate.suffix.lower() not in suffixes:
                continue
            try:
                if candidate.stat().st_mtime < cutoff:
                    candidate.unlink()
                    removed += 1
            except FileNotFoundError:
                continue
            except OSError:
                # Cleanup is best-effort and must not take the API down.
                continue

    return removed
