"""Manifest loading and validation for a labeled calibration dataset.

The manifest is a JSON file describing one detector's samples and their
ground-truth boxes. See docs/calibration_dataset_spec.md for the full schema
and collection guidelines.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List

from .types import DatasetSpec, GroundTruth, Sample


class DatasetSpecError(ValueError):
    """Raised when a manifest is structurally invalid."""


def _require(d: dict, key: str, ctx: str) -> Any:
    if key not in d or d[key] is None:
        raise DatasetSpecError(f"{ctx}: missing required key '{key}'")
    return d[key]


def _as_bbox(value: Any, ctx: str) -> tuple[float, float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise DatasetSpecError(f"{ctx}: bbox must be a list of 4 numbers, got {value!r}")
    try:
        return (float(value[0]), float(value[1]), float(value[2]), float(value[3]))
    except (TypeError, ValueError) as exc:
        raise DatasetSpecError(f"{ctx}: bbox contains non-numeric values: {exc}")


def sample_from_dict(d: dict) -> Sample:
    ctx = f"sample '{d.get('sample_id', '?')}'"
    sid = _require(d, "sample_id", ctx)
    if not isinstance(sid, str):
        raise DatasetSpecError(f"{ctx}: sample_id must be a string")
    gts: List[GroundTruth] = []
    for i, g in enumerate(d.get("ground_truth", []) or []):
        gctx = f"{ctx}.ground_truth[{i}]"
        gts.append(
            GroundTruth(
                sample_id=sid,
                bbox=_as_bbox(_require(g, "bbox", gctx), gctx),
                page_index=g.get("page_index"),
                label=g.get("label", "signature"),
            )
        )
    return Sample(
        sample_id=sid,
        asset_path=d.get("asset_path"),
        ground_truth=gts,
        split=d.get("split", "all"),
    )


def load_manifest(path: str | Path) -> DatasetSpec:
    """Load and validate a dataset manifest JSON file."""
    path = Path(path)
    if not path.exists():
        raise DatasetSpecError(f"manifest not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DatasetSpecError(f"{path}: invalid JSON: {exc}")

    if not isinstance(data, dict):
        raise DatasetSpecError(f"{path}: top-level JSON must be an object")

    name = _require(data, "name", str(path))
    detector = _require(data, "detector", str(path))
    if detector not in ("pdf", "image", "synthetic"):
        raise DatasetSpecError(
            f"{path}: detector must be 'pdf', 'image', or 'synthetic', got {detector!r}"
        )
    if not isinstance(data.get("samples", []), list):
        raise DatasetSpecError(f"{path}: 'samples' must be a list")

    samples = [sample_from_dict(s) for s in data["samples"]]
    if not samples:
        raise DatasetSpecError(f"{path}: manifest has no samples")

    for sample in samples:
        if sample.split not in {"train", "val", "test", "all"}:
            raise DatasetSpecError(
                f"sample '{sample.sample_id}': split must be train, val, test, or all"
            )
        if detector == "pdf":
            for index, ground_truth in enumerate(sample.ground_truth):
                if ground_truth.page_index is None:
                    raise DatasetSpecError(
                        f"sample '{sample.sample_id}'.ground_truth[{index}]: "
                        "page_index is required for PDF ground truth"
                    )

    iou_match_threshold = float(data.get("iou_match_threshold", 0.5))
    if not 0.0 < iou_match_threshold <= 1.0:
        raise DatasetSpecError("iou_match_threshold must be greater than 0 and at most 1")

    return DatasetSpec(
        name=name,
        detector=detector,
        samples=samples,
        iou_match_threshold=iou_match_threshold,
    )


def validate_assets_exist(spec: DatasetSpec) -> list[str]:
    """Return a list of warnings for samples whose asset file is missing.

    Synthetic samples have no asset file and are skipped.
    """
    warnings: list[str] = []
    for s in spec.samples:
        if s.asset_path and not Path(s.asset_path).exists():
            warnings.append(f"{s.sample_id}: asset not found: {s.asset_path}")
    return warnings
