"""Contract and mutation-sensitivity checks for the clean-fixture CI gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.run_calibration_regression import assert_report_matches


ROOT = Path(__file__).resolve().parents[1]


def test_calibration_regression_tool_declares_both_real_fixture_adapters() -> None:
    source = (ROOT / "tools/run_calibration_regression.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/test-data.yml").read_text(encoding="utf-8")

    assert '("image", "image_signatures")' in source
    assert '("pdf", "pdf_fields")' in source
    assert 'CALIBRATORS = ("isotonic", "platt")' in source
    assert "scripts/build_calibration_dataset.py" in source
    assert "calibration baseline drift" in source
    assert "tools/run_calibration_regression.py --repo-root ." in workflow


def test_calibration_regression_rejects_changed_report(tmp_path: Path) -> None:
    expected = tmp_path / "expected.json"
    actual = tmp_path / "actual.json"
    expected.write_text(json.dumps({"ece": 0.1}), encoding="utf-8")
    actual.write_text(json.dumps({"ece": 0.2}), encoding="utf-8")

    with pytest.raises(RuntimeError, match="calibration baseline drift"):
        assert_report_matches(expected, actual)
