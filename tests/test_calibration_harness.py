"""Tests for the calibration harness.

These run with NO labeled data and NO sklearn/opencv by exercising the
deterministic synthetic self-test path, plus pure unit checks on the metrics.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from calibration import metrics  # noqa: E402
from calibration.adapters import SyntheticAdapter  # noqa: E402
from calibration.dataset import DatasetSpecError, load_manifest  # noqa: E402
from calibration.harness import CalibrationOptions, run_calibration  # noqa: E402
from calibration.self_test_data import build_self_test_dataset  # noqa: E402


def test_self_test_end_to_end():
    spec = build_self_test_dataset(n_samples=60, seed=7)
    report = run_calibration(spec, SyntheticAdapter(), CalibrationOptions(calibrator="isotonic"))

    assert report["detector"] == "synthetic"
    assert "uncalibrated" in report and "calibrated" in report
    assert "thresholds" in report

    u, c = report["uncalibrated"], report["calibrated"]
    # AUC must be a valid probability.
    assert 0.0 <= u["roc_auc"] <= 1.0, u["roc_auc"]
    assert 0.0 <= u["pr_auc"] <= 1.0, u["pr_auc"]
    # A well-fit calibrator must not *worsen* ECE.
    assert c["ece"] <= u["ece"] + 1e-9, (c["ece"], u["ece"])
    # recall_at_k is in [0, 1] or nan (never negative).
    assert c["recall_at_1"] is None or 0.0 <= c["recall_at_1"] <= 1.0
    assert c["recall_at_3"] is None or 0.0 <= c["recall_at_3"] <= 1.0
    # We expect an actual improvement on the overconfident synthetic data.
    assert report.get("ece_improvement", 0.0) >= 0.0


def test_platt_and_isotonic_both_run():
    spec = build_self_test_dataset(n_samples=80, seed=11)
    for method in ("isotonic", "platt"):
        report = run_calibration(
            spec, SyntheticAdapter(), CalibrationOptions(calibrator=method)
        )
        assert report["calibrator"] == method
        assert report["calibrated"]["ece"] <= report["uncalibrated"]["ece"] + 1e-9


def test_metrics_unit():
    # IoU: identical boxes -> 1.0; disjoint -> 0.0.
    assert metrics.iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    assert metrics.iou((0, 0, 10, 10), (100, 100, 10, 10)) == 0.0
    # Partially overlapping: (0,0,10,10) vs (5,0,10,10) => inter 50, union 150 => 1/3.
    assert abs(metrics.iou((0, 0, 10, 10), (5, 0, 10, 10)) - 1 / 3) < 1e-9

    conf = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    lab = np.array([0, 0, 1, 1, 1])
    assert metrics.ece(conf, lab) >= 0.0
    # Perfectly calibrated scores => ECE ~ 0.
    perf_conf = np.array([0.0, 0.0, 1.0, 1.0, 1.0])
    perf_lab = np.array([0, 0, 1, 1, 1])
    assert metrics.ece(perf_conf, perf_lab) < 1e-9

    # ROC AUC of a perfect ranker is 1.0.
    assert metrics.roc_auc(np.array([0.1, 0.2, 0.8, 0.9]), np.array([0, 0, 1, 1])) == 1.0
    # Constant scores are undefined -> convention returns 0.5 (must not crash).
    assert metrics.roc_auc(np.array([0.5, 0.5, 0.5, 0.5]), np.array([0, 0, 1, 1])) == 0.5
    # A reversed ranker yields AUC 0.0.
    assert metrics.roc_auc(np.array([0.9, 0.8, 0.2, 0.1]), np.array([0, 0, 1, 1])) == 0.0

    # recall_at_k: one GT covered by the top candidate -> 1.0.
    per_sample = [([((0.0, 0.0, 20.0, 20.0), 0.9), ((50.0, 50.0, 5.0, 5.0), 0.1)],
                   [(0.0, 0.0, 20.0, 20.0)])]
    assert metrics.recall_at_k(per_sample, 1, 0.5) == 1.0
    assert metrics.recall_at_k(per_sample, 1, 0.99) == 1.0  # IoU 1.0 still passes 0.99

    p, r = metrics.precision_recall_at_threshold(np.array([0.9, 0.2]), np.array([1, 0]), 0.5)
    assert (p, r) == (1.0, 1.0)


def test_candidate_labels_are_one_to_one_and_page_aware():
    candidates = [(0.0, 0.0, 10.0, 10.0), (0.0, 0.0, 10.0, 10.0)]
    gts = [(0.0, 0.0, 10.0, 10.0)]

    assert metrics.candidate_labels(candidates, gts, 0.5) == [1, 0]
    assert metrics.candidate_labels(
        candidates,
        gts,
        0.5,
        candidate_page_indexes=[1, 0],
        gt_page_indexes=[0],
    ) == [0, 1]


def test_schema_validation():
    good = {
        "name": "demo",
        "detector": "pdf",
        "samples": [
            {
                "sample_id": "d1",
                "asset_path": "datasets/x.pdf",
                "split": "train",
                "ground_truth": [{"page_index": 0, "bbox": [120.0, 200.0, 240.0, 44.0]}],
            }
        ],
    }
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "manifest.json"
        p.write_text(json.dumps(good), encoding="utf-8")
        spec = load_manifest(p)
        assert spec.detector == "pdf"
        assert len(spec.samples) == 1
        assert spec.samples[0].ground_truth[0].bbox == (120.0, 200.0, 240.0, 44.0)

    # Missing detector -> error.
    bad = {"name": "x", "samples": [{"sample_id": "s"}]}
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "bad.json"
        p.write_text(json.dumps(bad), encoding="utf-8")
        try:
            load_manifest(p)
            assert False, "expected DatasetSpecError"
        except DatasetSpecError:
            pass

    missing_page = {
        "name": "pdf-without-page",
        "detector": "pdf",
        "samples": [{"sample_id": "s", "ground_truth": [{"bbox": [1, 2, 3, 4]}]}],
    }
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "missing-page.json"
        p.write_text(json.dumps(missing_page), encoding="utf-8")
        try:
            load_manifest(p)
            assert False, "expected DatasetSpecError"
        except DatasetSpecError as exc:
            assert "page_index is required" in str(exc)


def test_report_warns_when_metrics_are_not_held_out():
    spec = build_self_test_dataset(n_samples=12, seed=3)
    for sample in spec.samples:
        sample.split = "all"

    report = run_calibration(spec, SyntheticAdapter(), CalibrationOptions())

    assert any("not held-out evidence" in note for note in report["notes"])

    # Malformed bbox -> error.
    bad2 = {
        "name": "x",
        "detector": "pdf",
        "samples": [{"sample_id": "s", "ground_truth": [{"bbox": [1, 2, 3]}]}],
    }
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "bad2.json"
        p.write_text(json.dumps(bad2), encoding="utf-8")
        try:
            load_manifest(p)
            assert False, "expected DatasetSpecError"
        except DatasetSpecError:
            pass
