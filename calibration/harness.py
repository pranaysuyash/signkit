"""Calibration harness orchestration.

Given a labeled dataset and a detector adapter, this:

1. Runs the detector over every sample (split into train/test).
2. Labels each candidate positive/negative via IoU against ground truth.
3. Computes uncalibrated calibration + discrimination metrics.
4. Fits a calibrator on the train split and applies it to the test split.
5. Computes calibrated metrics and derives recommended thresholds from the
   product accuracy bar (target recall / precision).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from . import calibrators, metrics
from .adapters import SyntheticAdapter
from .types import Candidate, DatasetSpec, DetectorAdapter, Sample


@dataclass
class CalibrationOptions:
    iou_match_threshold: float = 0.5
    n_bins: int = 15
    calibrator: str = "isotonic"  # "isotonic" | "platt"
    target_recall: Optional[float] = None
    target_precision: Optional[float] = None
    auto_place_min_iou: float = 0.85
    show_threshold_default: float = 0.5
    auto_place_threshold_default: float = 0.9
    min_train_samples: int = 8


def _collect(
    samples: List[Sample],
    adapter: DetectorAdapter,
    iou_thr: float,
):
    confs: List[float] = []
    labels: List[int] = []
    per_sample: List[tuple] = []
    for s in samples:
        cands: List[Candidate] = adapter.detect(s)
        gts = [g.bbox for g in s.ground_truth]
        lab = metrics.candidate_labels(
            [c.bbox for c in cands],
            gts,
            iou_thr,
            candidate_page_indexes=[c.page_index for c in cands],
            gt_page_indexes=[g.page_index for g in s.ground_truth],
        )
        for c, l in zip(cands, lab):
            confs.append(c.confidence)
            labels.append(l)
        per_sample.append(([(c.bbox, c.confidence) for c in cands], gts))
    return np.array(confs, dtype=float), np.array(labels, dtype=int), per_sample


def _metrics_block(conf: np.ndarray, labels: np.ndarray, per_sample, opts):
    if len(conf) == 0:
        return {
            "n_candidates": 0,
            "n_positive": 0,
            "n_negative": 0,
            "ece": float("nan"),
            "roc_auc": float("nan"),
            "pr_auc": float("nan"),
            "recall_at_1": float("nan"),
            "recall_at_3": float("nan"),
        }
    return {
        "n_candidates": int(len(conf)),
        "n_positive": int(labels.sum()),
        "n_negative": int((1 - labels).sum()),
        "ece": metrics.ece(conf, labels, opts.n_bins),
        "reliability": metrics.reliability(conf, labels, opts.n_bins),
        "roc_auc": metrics.roc_auc(conf, labels),
        "pr_auc": metrics.pr_auc(conf, labels),
        "recall_at_1": metrics.recall_at_k(per_sample, 1, opts.iou_match_threshold),
        "recall_at_3": metrics.recall_at_k(per_sample, 3, opts.iou_match_threshold),
        "confidence_hist": np.histogram(conf, bins=10, range=(0.0, 1.0))[0].tolist(),
    }


def _derive_thresholds(cal_conf: np.ndarray, labels: np.ndarray, opts) -> dict:
    out = {
        "show_candidate": opts.show_threshold_default,
        "auto_place": opts.auto_place_threshold_default,
        "note": "defaults (raw thresholds mapped through calibrator)",
    }
    if len(cal_conf) == 0:
        return out
    # Candidate thresholds: the unique calibrated scores plus 0/1.
    thr_grid = np.unique(np.concatenate([[0.0, 1.0], np.clip(cal_conf, 0.0, 1.0)]))
    if opts.target_precision is not None:
        chosen = None
        for t in thr_grid:
            p, _ = metrics.precision_recall_at_threshold(cal_conf, labels, t)
            if p >= opts.target_precision:
                chosen = float(t)
                break
        if chosen is not None:
            out["show_candidate"] = chosen
            out["note"] = f"show threshold set to meet target precision {opts.target_precision}"
    if opts.target_recall is not None:
        chosen = None
        for t in reversed(thr_grid.tolist()):
            _, r = metrics.precision_recall_at_threshold(cal_conf, labels, t)
            if r >= opts.target_recall:
                chosen = float(t)
                break
        if chosen is not None:
            out["auto_place"] = chosen
            out["note"] = f"auto-place threshold set to meet target recall {opts.target_recall}"
    return out


def run_calibration(
    spec: DatasetSpec,
    adapter: DetectorAdapter,
    options: Optional[CalibrationOptions] = None,
) -> dict:
    opts = options or CalibrationOptions()

    notes: List[str] = []

    has_explicit_split = any(s.split in {"train", "val", "test"} for s in spec.samples)
    has_explicit_test = any(s.split == "test" for s in spec.samples)
    if has_explicit_split:
        train_samples = [s for s in spec.samples if s.split == "train"]
        test_samples = [s for s in spec.samples if s.split == "test"]
    else:
        train_samples = list(spec.samples)
        test_samples = list(spec.samples)

    # If there is no dedicated test split, evaluate on the training data but
    # make the leakage boundary explicit in every report.
    if not has_explicit_test:
        notes.append("no dedicated test split; reported metrics are not held-out evidence")
    if not test_samples:
        test_samples = train_samples
    if not train_samples:
        notes.append("no train split; calibrator fitting is unavailable")

    train_conf, train_lab, _ = _collect(train_samples, adapter, opts.iou_match_threshold)
    test_conf, test_lab, test_per = _collect(test_samples, adapter, opts.iou_match_threshold)

    uncalibrated = _metrics_block(test_conf, test_lab, test_per, opts)

    calibrator = None
    if len(train_conf) >= opts.min_train_samples:
        try:
            calibrator = calibrators.fit_calibrator(train_conf, train_lab, opts.calibrator)
            cal_conf = calibrators.apply_calibrator(calibrator, test_conf)
        except Exception as exc:  # pragma: no cover - defensive
            notes.append(f"calibrator fit failed ({exc}); reporting raw metrics only")
            cal_conf = test_conf
    else:
        notes.append(
            f"fewer than {opts.min_train_samples} training samples; "
            "reporting raw metrics only, no calibrator fit"
        )
        cal_conf = test_conf

    calibrated = _metrics_block(cal_conf, test_lab, test_per, opts)
    thresholds = _derive_thresholds(cal_conf, test_lab, opts)

    report = {
        "detector": spec.detector,
        "dataset": spec.name,
        "n_samples": len(spec.samples),
        "iou_match_threshold": opts.iou_match_threshold,
        "calibrator": opts.calibrator if calibrator is not None else None,
        "uncalibrated": uncalibrated,
        "calibrated": calibrated,
        "thresholds": thresholds,
        "notes": notes,
    }
    if calibrator is not None:
        improvement = uncalibrated["ece"] - calibrated["ece"]
        report["ece_improvement"] = float(improvement)
    return report


def run_self_test(options: Optional[CalibrationOptions] = None) -> dict:
    """Build the synthetic dataset and run the full pipeline end-to-end."""
    from .self_test_data import build_self_test_dataset

    spec = build_self_test_dataset()
    return run_calibration(spec, SyntheticAdapter(), options or CalibrationOptions())
