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


def test_tagged_release_workflow_runs_dependency_free_claim_gate_before_ledger() -> None:
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "build-all-platforms.yml").read_text(
        encoding="utf-8"
    )
    claim_gate = "python3 tools/audit_public_surface.py --strict"
    ledger_step = "python3 tools/release_artifact_ledger.py"

    assert claim_gate in workflow
    assert ledger_step in workflow
    assert workflow.index(claim_gate) < workflow.index(ledger_step)


def test_canonical_deploy_wrapper_uses_project_interpreter_for_python_gates() -> None:
    script = (PROJECT_ROOT / "scripts" / "deploy_canonical_landing.sh").read_text(encoding="utf-8")

    assert 'PROJECT_PYTHON="$PROJECT_ROOT/.venv/bin/python"' in script
    assert '"$PROJECT_PYTHON" tools/audit_public_surface.py --strict' in script
    assert '"$PROJECT_PYTHON" tools/test_deployed_surface.py' in script
    assert "python3 -m pytest" not in script
