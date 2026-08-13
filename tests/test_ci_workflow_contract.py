"""Executable contract for the canonical CI release-safety workflow."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "test-data.yml"
PYTEST_CONFIG = ROOT / "pytest.ini"


def test_ci_workflow_runs_the_reproducible_release_qa_matrix() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "name: Run reproducible release QA matrix" in workflow
    assert "QT_QPA_PLATFORM: offscreen" in workflow
    assert "DATABASE_URL: sqlite:///./ci-qa.sqlite" in workflow
    assert "JWT_SECRET: ci-only-secret-that-is-at-least-32-bytes-long" in workflow
    assert "./.venv/bin/pytest -q" in workflow
    assert "./.venv/bin/pytest -q" in workflow


def test_pytest_default_collection_includes_all_first_party_suites() -> None:
    config = PYTEST_CONFIG.read_text(encoding="utf-8")

    assert "testpaths =\n    tests\n    backend/tests\n    desktop_app/tests" in config


def test_ci_workflow_keeps_the_high_risk_and_release_gates() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    required_gates = (
        "alembic -c alembic.ini upgrade head",
        "tools/run_extraction_hosted_smoke.py",
        "tools/mutation_check.py",
        "tests/test_launch_claim_registry.py",
        "scripts/test-deployment.sh http://127.0.0.1:8080",
    )
    for gate in required_gates:
        assert gate in workflow
