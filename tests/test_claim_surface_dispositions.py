"""Keep strict public-surface warnings tied to explicit dispositions."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
AUDIT = ROOT / "tools" / "audit_public_surface.py"
DISPOSITIONS = ROOT / "docs" / "launch_claims" / "retained_surface_dispositions.md"


def test_every_strict_audit_warning_path_has_a_disposition() -> None:
    result = subprocess.run(
        ["python", str(AUDIT), "--strict", "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(result.stdout)
    register = DISPOSITIONS.read_text(encoding="utf-8")

    for relative_path in report["historical_docs_with_retired_routes"]:
        assert f"| `{relative_path}` |" in register, relative_path

    for warning in report["warnings"]:
        if warning.startswith("retained page contains "):
            surface = warning.rsplit(": ", 1)[1]
            assert f"| `{surface}` |" in register, surface

    assert "local source-tree warning disposition" in register
    assert "deployed redirect behavior" in register
    assert "release artifact exclusion" in register
