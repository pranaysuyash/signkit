"""Executable contract for the local extraction ownership smoke tool."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]
TOOL = ROOT / "tools" / "run_extraction_hosted_smoke.py"


def test_extraction_smoke_tool_passes_health_and_lifecycle_contract() -> None:
    result = subprocess.run(
        [sys.executable, str(TOOL)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "passed"
    assert "health" in payload["checks"]
    assert "durable upload replay" in payload["checks"]
    assert "post-delete audit receipt" in payload["checks"]
