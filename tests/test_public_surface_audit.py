"""Executable release-gate coverage for the public-surface auditor."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_public_surface_audit_has_no_blocking_errors() -> None:
    result = subprocess.run(
        [sys.executable, "tools/audit_public_surface.py", "--strict"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
