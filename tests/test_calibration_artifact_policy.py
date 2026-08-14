"""Tests for the durable calibration artifact boundary.

The manifests, reports, and notes are reviewable inputs and evidence. PNG/PDF
assets are generated outputs and must be reproducible from manifest metadata,
not treated as a second editable source of truth.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from calibration.dataset import DatasetSpecError, load_manifest

ROOT = Path(__file__).resolve().parent.parent


def _run_builder(out: Path) -> dict[str, dict]:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_calibration_dataset.py"),
            "--out",
            str(out),
            "--image-n",
            "8",
            "--pdf-n",
            "8",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {
        detector: json.loads(
            (out / directory / "manifest.json").read_text(encoding="utf-8")
        )
        for detector, directory in (
            ("image", "image_signatures"),
            ("pdf", "pdf_fields"),
        )
    }


def test_builder_records_reproducibility_metadata_and_assets(tmp_path):
    first = _run_builder(tmp_path / "first")
    second = _run_builder(tmp_path / "second")

    for detector, manifest in first.items():
        generation = manifest["generation"]
        assert generation["generator"] == "scripts/build_calibration_dataset.py"
        assert generation["generator_version"] == "1"
        assert generation["detector"] == detector
        assert generation["sample_count"] == 8
        assert generation["seed"] == 20260814
        assert generation["asset_policy"] == (
            "generated-assets-ignored-manifest-report-notes-tracked"
        )
        assert generation["ground_truth"] == (
            "programmatic synthetic labels; internal-use only"
        )
        assert manifest == second[detector]

        asset_dir = tmp_path / "first" / (
            "image_signatures/images" if detector == "image" else "pdf_fields/pdfs"
        )
        assert len(list(asset_dir.iterdir())) == 8


def test_tracked_artifact_policy_files_are_small_and_explicit():
    expected = (
        ROOT / "datasets/image_signatures/manifest.json",
        ROOT / "datasets/image_signatures/calibration_report_isotonic.json",
        ROOT / "datasets/image_signatures/calibration_report_platt.json",
        ROOT / "datasets/image_signatures/notes.md",
        ROOT / "datasets/pdf_fields/manifest.json",
        ROOT / "datasets/pdf_fields/calibration_report_isotonic.json",
        ROOT / "datasets/pdf_fields/calibration_report_platt.json",
        ROOT / "datasets/pdf_fields/notes.md",
    )
    for path in expected:
        assert path.exists(), path
        assert path.stat().st_size < 100_000, path


def test_manifest_generation_metadata_is_validated(tmp_path):
    manifest = _run_builder(tmp_path / "valid")["image"]
    path = tmp_path / "metadata.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert len(load_manifest(path).samples) == 8

    invalid = dict(manifest)
    invalid["generation"] = dict(manifest["generation"], sample_count=9)
    path.write_text(json.dumps(invalid), encoding="utf-8")
    with pytest.raises(DatasetSpecError, match="sample_count"):
        load_manifest(path)
