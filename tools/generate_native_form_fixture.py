"""Generate a reusable native AcroForm benchmark PDF for parser exploration."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import random
import json
import sys

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


OUTPUT = Path(__file__).resolve().parents[1] / "desktop_app" / "tests" / "fixtures" / "native_form_benchmark.pdf"
SCRIPT_VERSION = "1.0.0"
DEFAULT_SEED = 20260812


def build_fixture(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cnv = canvas.Canvas(str(path), pagesize=letter)

    cnv.setTitle("Native Form Benchmark")
    cnv.setFont("Helvetica-Bold", 16)
    cnv.drawString(72, 748, "Native Form Benchmark")
    cnv.setFont("Helvetica", 11)
    cnv.drawString(72, 724, "This fixture exercises real AcroForm widgets for parser exploration.")

    cnv.setFont("Helvetica-Bold", 12)
    cnv.drawString(72, 680, "Full Name")
    cnv.setFont("Helvetica", 11)
    cnv.acroForm.textfield(
        name="full_name",
        tooltip="Full Name",
        x=180,
        y=668,
        width=240,
        height=20,
        borderStyle="inset",
        forceBorder=True,
    )

    cnv.setFont("Helvetica-Bold", 12)
    cnv.drawString(72, 638, "Agree Terms")
    cnv.acroForm.checkbox(
        name="agree_terms",
        tooltip="Agree Terms",
        x=180,
        y=634,
        buttonStyle="check",
        checked=False,
    )

    cnv.setFont("Helvetica-Bold", 12)
    cnv.drawString(72, 598, "Country")
    cnv.acroForm.choice(
        name="country",
        tooltip="Country",
        value="US",
        options=["US", "CA", "UK"],
        x=180,
        y=588,
        width=120,
        height=20,
    )

    cnv.setFont("Helvetica-Bold", 12)
    cnv.drawString(72, 552, "Plan")
    cnv.acroForm.radio(
        name="plan",
        value="basic",
        selected=True,
        x=180,
        y=548,
        tooltip="Plan",
    )
    cnv.drawString(205, 550, "Basic")
    cnv.acroForm.radio(
        name="plan",
        value="pro",
        selected=False,
        x=280,
        y=548,
        tooltip="Plan",
    )
    cnv.drawString(305, 550, "Pro")

    cnv.showPage()
    cnv.save()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a native-form fixture used by parser/integration tests."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT,
        help="Fixture output path.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Determinism seed for any future randomized generation paths.",
    )
    return parser.parse_args()


def emit_reproducibility_metadata(seed: int, output: Path) -> None:
    metadata = {
        "script": "generate_native_form_fixture.py",
        "version": SCRIPT_VERSION,
        "seed": seed,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "output": str(output),
        "command": " ".join([str(arg) for arg in sys.argv]),
    }
    print(json.dumps(metadata, indent=2))


def main() -> None:
    args = parse_args()
    output = args.output
    random.seed(args.seed)

    emit_reproducibility_metadata(seed=args.seed, output=output)
    build_fixture(output)
    print(output)


if __name__ == "__main__":
    main()
