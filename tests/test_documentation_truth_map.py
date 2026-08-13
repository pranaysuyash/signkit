"""Regression checks for current versus historical documentation authority."""

from pathlib import Path


ROOT = Path(__file__).parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_current_docs_link_the_truth_map_and_canonical_backlog() -> None:
    truth_map = _read("docs/DOCUMENTATION_TRUTH_MAP_2026-08-13.md")
    readme = _read("docs/README.md")
    documentation_status = _read("docs/DOCUMENTATION_STATUS.md")

    assert "docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md" in truth_map
    assert "docs/QA_RESULTS.md" in truth_map
    assert "docs/launch_claims/registry.md" in truth_map
    assert "DOCUMENTATION_TRUTH_MAP_2026-08-13.md" in readme
    assert "DOCUMENTATION_TRUTH_MAP_2026-08-13.md" in documentation_status
    assert "historical" in documentation_status.lower()


def test_claim_inventory_task_ids_exist_in_the_canonical_backlog() -> None:
    backlog = _read("docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md")
    inventory = _read("docs/review/claim_surface_inventory_2026-08-13.md")

    for task_id in ("L0-13", "L0-14", "L1-07", "L1-08"):
        assert f"| {task_id} |" in backlog
        assert task_id in inventory


def test_wayfinder_resolution_points_to_open_claim_remediation() -> None:
    ticket = _read("docs/wayfinder/tickets/reconcile-historical-docs-and-public-claims.md")
    backlog = _read("docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md")

    assert "status: resolved" in ticket
    assert "DOCUMENTATION_TRUTH_MAP_2026-08-13.md" in ticket
    assert "L1-07" in ticket
    assert "| L2-01 | explicit | wayfinder |" in backlog


def test_operator_state_task_points_to_current_runtime_evidence() -> None:
    backlog = _read("docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md")
    matrix = _read("docs/STATE_CONTENT_MATRIX.md")
    qa = _read("docs/QA_RESULTS.md")

    assert "local_operator_state_proof_2026-08-13.md" in backlog
    assert "disposable source-to-ready observation" in matrix
    assert "QA-28" in qa
