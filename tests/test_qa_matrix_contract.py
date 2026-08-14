"""Keep the durable QA matrix structurally complete and boundary-aware."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).parents[1]
QA_MATRIX = ROOT / "docs" / "QA_RESULTS.md"


def test_qa_matrix_has_reproducible_results_negative_paths_and_known_limits() -> None:
    matrix = QA_MATRIX.read_text(encoding="utf-8")

    assert "# SignKit release QA results" in matrix
    assert "| ID | Result | Evidence | Notes |" in matrix
    for row_id in ("QA-05", "QA-13", "QA-14", "QA-15", "QA-55"):
        assert f"| {row_id} |" in matrix
    assert "| QA-13 | FAIL, release-blocking |" in matrix
    assert "| QA-14 | OPEN |" in matrix
    assert "| QA-15 | OPEN |" in matrix
    assert "unsupported-media contract" in matrix
    assert "## Not closed by this run" in matrix
    assert "optional PyMuPDF" in matrix
    assert "reference retired routes" in matrix
    assert "This is local evidence only" in matrix
