"""Generate a small parser benchmark corpus for exploration and regression checks."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import random
import sys

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


FIXTURES = Path(__file__).resolve().parents[1] / "desktop_app" / "tests" / "fixtures"
SCRIPT_VERSION = "1.0.0"
DEFAULT_SEED = 20260812


def build_checkbox_heavy(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cnv = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    cnv.setTitle("Checkbox Heavy Benchmark")
    cnv.setFont("Helvetica-Bold", 16)
    cnv.drawString(72, height - 54, "Checkbox Heavy Benchmark")
    cnv.setFont("Helvetica", 11)
    cnv.drawString(72, height - 78, "Native widgets with repeated boolean choices.")

    for idx, label in enumerate(["Marketing", "Sales", "Legal", "Finance", "Ops"], start=1):
        y = height - (120 + idx * 42)
        cnv.setFont("Helvetica-Bold", 12)
        cnv.drawString(72, y + 4, label)
        cnv.acroForm.checkbox(name=f"{label.lower()}_enabled", tooltip=label, x=180, y=y, buttonStyle="check", checked=idx % 2 == 0)

    cnv.showPage()
    cnv.save()


def build_mixed_layout(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cnv = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    cnv.setTitle("Mixed Layout Benchmark")
    cnv.setFont("Helvetica-Bold", 16)
    cnv.drawString(72, height - 54, "Mixed Layout Benchmark")
    cnv.setFont("Helvetica", 11)
    cnv.drawString(72, height - 78, "Text-native page with signature lines and form-like regions.")

    cnv.setFont("Helvetica-Bold", 12)
    cnv.drawString(72, height - 128, "Authorized Signer")
    cnv.line(180, height - 132, 410, height - 132)
    cnv.drawString(72, height - 168, "Date")
    cnv.line(180, height - 172, 300, height - 172)
    cnv.drawString(72, height - 210, "Initials")
    cnv.rect(180, height - 224, 68, 24, stroke=1, fill=0)
    cnv.showPage()
    cnv.save()


def build_scan_like(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1600, 2200), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    draw.text((120, 120), "Scan-Like Benchmark", fill="black", font=font)
    draw.text((120, 180), "Rendered into an image, so the PDF carries no text layer.", fill="black", font=font)
    draw.line((120, 620, 980, 620), fill="black", width=5)
    draw.rectangle((120, 760, 420, 840), outline="black", width=4)
    draw.rectangle((120, 930, 520, 1040), outline="black", width=4)
    draw.text((130, 650), "Signature", fill="black", font=font)
    draw.text((130, 865), "Checkbox area", fill="black", font=font)
    draw.text((130, 1080), "Text box area", fill="black", font=font)

    image_path = path.with_suffix(".png")
    image.save(image_path)

    cnv = canvas.Canvas(str(path), pagesize=letter)
    cnv.drawImage(ImageReader(str(image_path)), 0, 0, width=letter[0], height=letter[1])
    cnv.showPage()
    cnv.save()
    image_path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate parser benchmark PDFs used by test fixtures."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=FIXTURES,
        help="Fixture output directory.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Determinism seed for any future randomized generation paths.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generation plan and reproducibility metadata without writing files.",
    )
    return parser.parse_args()


def emit_reproducibility_metadata(seed: int, output_dir: Path) -> None:
    metadata = {
        "script": "generate_parser_benchmark_corpus.py",
        "version": SCRIPT_VERSION,
        "seed": seed,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "outputs": [
            str((output_dir / "checkbox_heavy_benchmark.pdf")),
            str((output_dir / "mixed_layout_benchmark.pdf")),
            str((output_dir / "scan_like_benchmark.pdf")),
        ],
        "command": " ".join([str(arg) for arg in sys.argv]),
    }
    print(json.dumps(metadata, indent=2))


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir
    seed = args.seed
    random.seed(seed)

    files = [
        output_dir / "checkbox_heavy_benchmark.pdf",
        output_dir / "mixed_layout_benchmark.pdf",
        output_dir / "scan_like_benchmark.pdf",
    ]

    emit_reproducibility_metadata(seed=seed, output_dir=output_dir)

    if args.dry_run:
        print("Dry-run enabled. No files written.")
        return

    build_checkbox_heavy(files[0])
    build_mixed_layout(files[1])
    build_scan_like(files[2])
    print("Generated parser benchmark corpus in", output_dir)


if __name__ == "__main__":
    main()
