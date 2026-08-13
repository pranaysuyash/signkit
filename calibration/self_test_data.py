"""Deterministic synthetic dataset for the harness self-test.

This exists so the full calibration pipeline (detect -> label -> metrics ->
calibrate -> thresholds) is exercised in CI and locally with zero labeled data
and zero heavyweight dependencies. The generated data is intentionally
*overconfident* (high raw confidence frequently maps to a negative label), so a
fitted calibrator should lower ECE. It is NOT a substitute for a real labeled
dataset -- see docs/calibration_dataset_spec.md.
"""

from __future__ import annotations

import numpy as np

from .types import Candidate, DatasetSpec, GroundTruth, Sample


def build_self_test_dataset(n_samples: int = 60, seed: int = 12345) -> DatasetSpec:
    """Build a reproducible synthetic dataset with train/test splits.

    Each candidate has a latent ``z``; label = 1 if z > 0. The raw confidence is
    ``0.5 + 0.5*tanh(2.5*z)`` -- a *sharper* (more confident) transform than the
    true logistic, so the score still ranks positives above negatives (AUC > 0.5)
    but is overconfident in absolute terms (ECE > 0). That is exactly the
    miscalibration shape the harness is built to repair.
    """
    rng = np.random.default_rng(seed)
    samples: list[Sample] = []
    for i in range(n_samples):
        sid = f"synthetic-{i:04d}"
        k = int(rng.integers(1, 4))  # 1-3 candidates per sample
        cands: list[Candidate] = []
        gts: list[GroundTruth] = []
        for j in range(k):
            z = rng.normal(0.0, 1.0)
            label = 1 if z > 0 else 0
            conf = float(np.clip(0.5 + 0.5 * np.tanh(2.5 * z), 0.01, 0.99))
            x = 10.0 + j * 5.0
            y = 10.0
            w = 20.0
            h = 20.0
            cands.append(
                Candidate(
                    sample_id=sid,
                    confidence=conf,
                    bbox=(x, y, w, h),
                    source="synthetic",
                )
            )
            if label == 1:
                gts.append(GroundTruth(sample_id=sid, bbox=(x, y, w, h)))
        split = "train" if i < int(n_samples * 0.7) else "test"
        samples.append(
            Sample(
                sample_id=sid,
                asset_path=None,
                ground_truth=gts,
                split=split,
                synthetic_candidates=cands,
            )
        )
    return DatasetSpec(
        name="self-test",
        detector="synthetic",
        samples=samples,
        iou_match_threshold=0.5,
    )
