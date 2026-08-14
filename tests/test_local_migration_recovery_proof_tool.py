"""Executable contract for disposable migration recovery proof."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]
TOOL = ROOT / "tools" / "run_local_migration_recovery_proof.py"


def test_local_migration_recovery_proof_round_trips_the_receipt_fields() -> None:
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
    assert payload["rollback_target"] == "e42b7f8c91aa"
    assert "downgrade removes receipt fields" in payload["checks"]
    assert "re-upgrade restores receipt fields" in payload["checks"]
