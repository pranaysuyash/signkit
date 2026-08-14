#!/usr/bin/env python3
"""Regenerate ignored calibration fixtures and enforce tracked report baselines.

The repository tracks calibration manifests and reports, but intentionally does
not track the generated PNG/PDF fixture binaries. This command recreates those
fixtures in an isolated directory, runs the real detector adapters through the
calibration CLI, and compares all four generated reports with the tracked
baselines. A detector or generator change must therefore update the evidence
deliberately instead of silently changing a calibration result in CI.

The results are synthetic-labelled internal evidence only. This command does
not promote thresholds, claim real-document accuracy, or replace the
permissioned-data and product-accuracy gates in RECON-24 and RECON-28.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any


FIXTURE_CONFIG = (
    ("image", "image_signatures"),
    ("pdf", "pdf_fields"),
)
CALIBRATORS = ("isotonic", "platt")
EXPECTED_GENERATOR = "scripts/build_calibration_dataset.py"


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"could not read JSON fixture {path}: {exc}") from exc


def _fixture_metadata(repo_root: Path, detector: str, directory: str) -> tuple[int, int]:
    manifest_path = repo_root / "datasets" / directory / "manifest.json"
    manifest = _read_json(manifest_path)
    generation = manifest.get("generation")
    if not isinstance(generation, dict):
        raise RuntimeError(f"{manifest_path}: generation metadata is required")
    if generation.get("generator") != EXPECTED_GENERATOR:
        raise RuntimeError(
            f"{manifest_path}: expected generator {EXPECTED_GENERATOR!r}, "
            f"got {generation.get('generator')!r}"
        )
    if generation.get("detector") != detector:
        raise RuntimeError(
            f"{manifest_path}: expected detector {detector!r}, "
            f"got {generation.get('detector')!r}"
        )
    sample_count = generation.get("sample_count")
    seed = generation.get("seed")
    if not isinstance(sample_count, int) or sample_count <= 0:
        raise RuntimeError(f"{manifest_path}: generation.sample_count must be positive")
    if not isinstance(seed, int):
        raise RuntimeError(f"{manifest_path}: generation.seed must be an integer")
    return sample_count, seed


def _run(command: list[str], repo_root: Path) -> None:
    completed = subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0:
        return
    details = "\n".join(part for part in (completed.stdout, completed.stderr) if part.strip())
    raise RuntimeError(
        f"command failed with exit {completed.returncode}: {' '.join(command)}\n{details}"
    )


def assert_report_matches(expected_path: Path, actual_path: Path) -> None:
    """Fail when a generated report differs from its tracked evidence baseline."""

    expected = _read_json(expected_path)
    actual = _read_json(actual_path)
    if expected != actual:
        raise RuntimeError(
            f"calibration baseline drift: generated {actual_path} differs from "
            f"tracked {expected_path}; review the detector/generator change and "
            "update the report only with fresh evidence"
        )


class _FixedWorkDirectory:
    """Context manager used when a caller wants to retain generated outputs."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def __enter__(self) -> Path:
        return self.path

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None


def run_regression(repo_root: Path, work_dir: Path | None = None) -> list[Path]:
    """Run the clean-fixture regression and return generated report paths."""

    repo_root = repo_root.resolve()
    if work_dir is None:
        context: AbstractContextManager[str | Path] = tempfile.TemporaryDirectory(
            prefix="signkit-calibration-regression-"
        )
    else:
        work_dir.mkdir(parents=True, exist_ok=True)
        context = _FixedWorkDirectory(work_dir)

    generated_reports: list[Path] = []
    with context as raw_work_dir:
        run_root = Path(raw_work_dir)
        generated_datasets = run_root / "datasets"
        generated_reports_dir = run_root / "reports"
        generated_reports_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            detector: _fixture_metadata(repo_root, detector, directory)
            for detector, directory in FIXTURE_CONFIG
        }
        image_n, seed = metadata["image"]
        pdf_n, pdf_seed = metadata["pdf"]
        if seed != pdf_seed:
            raise RuntimeError("image and PDF fixtures must share one reproducibility seed")

        python = sys.executable
        _run(
            [
                python,
                "scripts/build_calibration_dataset.py",
                "--out",
                str(generated_datasets),
                "--image-n",
                str(image_n),
                "--pdf-n",
                str(pdf_n),
                "--seed",
                str(seed),
            ],
            repo_root,
        )

        for detector, directory in FIXTURE_CONFIG:
            tracked_dir = repo_root / "datasets" / directory
            generated_dir = generated_datasets / directory
            tracked_manifest = _read_json(tracked_dir / "manifest.json")
            generated_manifest = _read_json(generated_dir / "manifest.json")
            if tracked_manifest != generated_manifest:
                raise RuntimeError(
                    f"calibration manifest drift: generated {generated_dir / 'manifest.json'} "
                    f"differs from tracked {tracked_dir / 'manifest.json'}"
                )

            for calibrator in CALIBRATORS:
                report_name = f"calibration_report_{calibrator}.json"
                generated_report = generated_reports_dir / f"{detector}_{calibrator}.json"
                _run(
                    [
                        python,
                        "-m",
                        "calibration.run",
                        "--dataset",
                        str(generated_dir / "manifest.json"),
                        "--detector",
                        detector,
                        "--calibrator",
                        calibrator,
                        "--report",
                        str(generated_report),
                    ],
                    repo_root,
                )
                assert_report_matches(tracked_dir / report_name, generated_report)
                generated_reports.append(generated_report)

    return generated_reports


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository containing tracked calibration manifests and reports",
    )
    parser.add_argument(
        "--work-dir",
        type=Path,
        help="retain generated fixture/report outputs under this directory",
    )
    args = parser.parse_args(argv)
    try:
        reports = run_regression(args.repo_root, args.work_dir)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Calibration regression PASS: {len(reports)} tracked reports match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
