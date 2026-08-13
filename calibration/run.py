"""CLI entrypoint for the calibration harness.

Examples
--------
# Run the full pipeline on synthetic data (no dataset needed):
python -m calibration.run --self-test

# Calibrate the PDF field detector against a labeled manifest:
python -m calibration.run --dataset datasets/pdf_fields/manifest.json \
    --detector pdf --report calibration_report.json

# Derive thresholds for a product accuracy bar:
python -m calibration.run --dataset manifest.json --detector pdf \
    --target-precision 0.95 --target-recall 0.90
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Make the package importable whether run as a module or a script.
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from calibration.adapters import ImageSignatureAdapter, PdfFieldAdapter, SyntheticAdapter
from calibration.dataset import DatasetSpecError, load_manifest
from calibration.harness import CalibrationOptions, run_calibration, run_self_test


def _print_report(report: dict) -> None:
    print("=" * 64)
    print(f"Calibration report — detector: {report['detector']}  dataset: {report['dataset']}")
    print(f"samples: {report['n_samples']}  IoU match thr: {report['iou_match_threshold']}")
    print(f"calibrator: {report['calibrator']}")
    print("-" * 64)
    u = report["uncalibrated"]
    c = report["calibrated"]
    print(f"{'metric':<22}{'uncalibrated':>16}{'calibrated':>16}")
    for key in ("ece", "roc_auc", "pr_auc", "recall_at_1", "recall_at_3"):
        uv = u.get(key)
        cv = c.get(key)
        print(
            f"{key:<22}"
            f"{_fmt(uv):>16}"
            f"{_fmt(cv):>16}"
        )
    print("-" * 64)
    print(f"recommended thresholds: {report['thresholds']}")
    if report.get("ece_improvement") is not None:
        print(f"ECE improvement after calibration: {report['ece_improvement']:.4f}")
    for note in report.get("notes", []):
        print(f"  note: {note}")
    print("=" * 64)


def _fmt(v) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, float):
        if v != v:  # nan
            return "n/a"
        return f"{v:.4f}"
    return str(v)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Signature detector confidence calibration harness")
    parser.add_argument("--self-test", action="store_true", help="Run on synthetic data (no dataset needed)")
    parser.add_argument("--dataset", help="Path to a dataset manifest JSON file")
    parser.add_argument("--detector", choices=["pdf", "image", "synthetic"], default="pdf")
    parser.add_argument("--report", help="Write the JSON report to this path")
    parser.add_argument("--calibrator", choices=["isotonic", "platt"], default="isotonic")
    parser.add_argument("--target-recall", type=float, default=None)
    parser.add_argument("--target-precision", type=float, default=None)
    parser.add_argument("--bins", type=int, default=15)
    args = parser.parse_args(argv)

    if args.self_test:
        report = run_calibration_with_opts(
            self_test=True, args=args
        )
    elif args.dataset:
        try:
            spec = load_manifest(args.dataset)
        except DatasetSpecError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        if spec.detector != args.detector:
            print(
                f"WARNING: manifest detector is '{spec.detector}' but --detector is "
                f"'{args.detector}'; using manifest's '{spec.detector}'.",
                file=sys.stderr,
            )
        adapter = _adapter_for(spec.detector)
        report = run_calibration_with_opts(spec=spec, adapter=adapter, args=args)
    else:
        parser.error("either --self-test or --dataset is required")
        return 2

    _print_report(report)
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        print(f"report written to {args.report}")
    return 0


def run_calibration_with_opts(
    self_test: bool = False,
    spec=None,
    adapter=None,
    args=None,
):
    opts = CalibrationOptions(
        calibrator=args.calibrator,
        target_recall=args.target_recall,
        target_precision=args.target_precision,
        n_bins=args.bins,
    )
    if self_test:
        return run_self_test(opts)
    return run_calibration(spec, adapter, opts)


def _adapter_for(detector: str):
    if detector == "pdf":
        return PdfFieldAdapter()
    if detector == "image":
        return ImageSignatureAdapter()
    return SyntheticAdapter()


if __name__ == "__main__":
    raise SystemExit(main())
