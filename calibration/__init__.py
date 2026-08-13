"""Calibration package for the signature auto-detectors.

This package provides a dependency-light (numpy only) harness to measure and
repair the *calibration* of the two uncalibrated detectors in this repo:

- PDF signature-field detection  -> desktop_app/pdf/field_detection.py
- Image signature detection      -> desktop_app/processing/extractor.py

Both emit hand-ranked "confidence" numbers that are NOT calibrated
probabilities. This harness turns a labeled dataset into:

- calibration metrics (ECE, reliability, ROC/PR AUC, recall@k, IoU),
- a fitted calibrator (Platt / isotonic, pure numpy),
- recommended auto-placement thresholds derived from a product accuracy bar.

It is intentionally runnable with NO labeled data via ``--self-test`` so the
pipeline is real and CI-green before any dataset exists.
"""

from __future__ import annotations

from .types import (
    Candidate,
    DatasetSpec,
    DetectorAdapter,
    GroundTruth,
    Sample,
)
from .harness import CalibrationOptions, run_calibration

__all__ = [
    "Candidate",
    "DatasetSpec",
    "DetectorAdapter",
    "GroundTruth",
    "Sample",
    "CalibrationOptions",
    "run_calibration",
]
