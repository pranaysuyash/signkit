"""Generate a labeled calibration dataset for both signature detectors.

This is the "acquire the data" step. The samples are **real files on disk**
(rendered PNGs / PDFs), not toy synthetic scores, so the harness runs the actual
detectors (`extractor.py`, `field_detection.py`) end-to-end and calibrates on
their real outputs.

Internal use only — see docs/calibration_dataset_spec.md. Generated PNG/PDF
assets are git-ignored; manifests, reports, and provenance notes are committed
so calibration is reproducible without making generated binaries a source of
truth.

Design notes (why it looks the way it does):
  * The image detector keys off blue ink (`blue-red > 60`); its confidence is a
    within-image relative ranking (`dominance / max_in_image`). To get a realistic
    spread of *false* positives we draw some negatives with a blue (non-signature)
    logo — the detector cannot tell a blue logo from a blue signature. Clean
    negatives (no blue) fall back to the grayscale path at a fixed 0.4.
  * The PDF detector reads page /Annots Widgets. reportlab 4.4.4 has no
    addSignature helper, so we inject a /Sig (positive) or /Tx (negative) widget
    with pikepdf after rendering. Hard negatives additionally get a drawn
    signature-like mark that the rendered OpenCV heuristic fires on.

Usage:
    python scripts/build_calibration_dataset.py --image-n 120 --pdf-n 120 --out datasets
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

import numpy as np
import pikepdf
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas

# ---------------------------------------------------------------------------
# Image dataset (feeds desktop_app/processing/extractor.py)
# ---------------------------------------------------------------------------

IMG_W, IMG_H = 820, 1040
BLUE_INK = (28, 28, 205)  # (B,G,R)-ish; PIL is (R,G,B) -> blue is high B.


def _gray_text_lines(d: ImageDraw.ImageDraw, rng: random.Random) -> None:
    for i in range(rng.randint(4, 9)):
        y = 70 + i * 64
        d.rectangle([60, y, 60 + rng.randint(200, 520), y + 16], fill=(185, 185, 185))


def _blue_squiggle(d: ImageDraw.ImageDraw, rng: random.Random):
    """Return a blue-ink signature stroke and its bbox (x, y, w, h) top-left origin."""
    x0 = 80 + rng.randint(0, 180)
    y0 = 720 + rng.randint(0, 110)
    n = rng.randint(34, 52)
    pts = [
        (x0 + i * 7, y0 + int(34 * math.sin(i / 2.3) + rng.randint(-12, 12)))
        for i in range(n)
    ]
    width = rng.randint(3, 7)
    d.line(pts, fill=BLUE_INK, width=width)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pad = 14
    return (
        float(min(xs) - pad),
        float(min(ys) - pad),
        float((max(xs) - min(xs)) + 2 * pad),
        float((max(ys) - min(ys)) + 2 * pad),
    )


def _blue_logo(d: ImageDraw.ImageDraw, rng: random.Random):
    """Draw a blue (non-signature) logo/box — a realistic hard negative."""
    bx = 80 + rng.randint(0, 260)
    by = 730 + rng.randint(0, 90)
    bw = rng.randint(90, 240)
    bh = rng.randint(40, 110)
    shade = rng.randint(120, 230)
    d.rectangle([bx, by, bx + bw, by + bh], outline=(shade, shade // 2, 255), width=4)
    d.ellipse([bx + 10, by + 10, bx + bw - 10, by + bh - 10], fill=(shade, shade // 2, 255))


def _make_image(is_positive: bool, rng: random.Random):
    img = Image.new("RGB", (IMG_W, IMG_H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    _gray_text_lines(d, rng)
    bbox = None
    if is_positive:
        bbox = _blue_squiggle(d, rng)
    else:
        # 50% hard negatives: a blue logo the blue-ink path will mis-fire on.
        if rng.random() < 0.5:
            _blue_logo(d, rng)
        else:
            # Clean negative: a gray (non-blue) logo box -> no blue-ink fire.
            d.rectangle([90, 760, 300, 850], outline=(120, 120, 120), width=3)
    return np.asarray(img), bbox


# ---------------------------------------------------------------------------
# PDF dataset (feeds desktop_app/pdf/field_detection.py)
# ---------------------------------------------------------------------------

PDF_W, PDF_H = 612.0, 792.0  # US Letter in points (bottom-left origin)
GENERATOR_VERSION = "1"
DEFAULT_SEED = 20260814


def _manifest_metadata(detector: str, sample_count: int, seed: int) -> dict:
    return {
        "schema_version": 1,
        "generation": {
            "generator": "scripts/build_calibration_dataset.py",
            "generator_version": GENERATOR_VERSION,
            "detector": detector,
            "sample_count": sample_count,
            "seed": seed,
            "asset_policy": "generated-assets-ignored-manifest-report-notes-tracked",
            "ground_truth": "programmatic synthetic labels; internal-use only",
        },
    }


def _draw_signature_mark(c, rng: random.Random) -> None:
    """Draw a long horizontal line or a box that the rendered heuristic detects."""
    if rng.random() < 0.5:
        y = 150.0 + rng.uniform(0, 60)
        x = 60.0
        w = 300.0 + rng.uniform(0, 120)
        c.line(x, y, x + w, y)
    else:
        x = 60.0 + rng.uniform(0, 80)
        y = 150.0 + rng.uniform(0, 40)
        w = 240.0 + rng.uniform(0, 60)
        h = 44.0 + rng.uniform(0, 14)
        c.rect(x, y, w, h, stroke=1, fill=0)


def _inject_widget(pdf: pikepdf.Pdf, page: pikepdf.Page, rect, ft: str, name: str) -> None:
    """Add a Widget annotation (and register it in /AcroForm) to a page.

    rect is (x0, y0, w, h) in PDF points, bottom-left origin.
    ft is '/Sig' or '/Tx'. The detector keys off /Subtype /Widget + /FT (+ /T label).
    """
    x0, y0, w, h = rect
    annot = pdf.make_indirect(
        pikepdf.Dictionary(
            Type=pikepdf.Name("/Annot"),
            Subtype=pikepdf.Name("/Widget"),
            Rect=[x0, y0, x0 + w, y0 + h],
            F=4,  # Print
            T=pikepdf.String(name),
            FT=pikepdf.Name(ft),
        )
    )
    if "/Annots" not in page:
        page.Annots = pdf.make_indirect(pikepdf.Array([]))
    page.Annots.append(annot)

    if "/AcroForm" not in pdf.Root:
        pdf.Root.AcroForm = pdf.make_indirect(pikepdf.Dictionary())
    af = pdf.Root.AcroForm
    if "/Fields" not in af:
        af.Fields = pdf.make_indirect(pikepdf.Array([]))
    af.Fields.append(annot)


def _make_pdf(is_positive: bool, rng: random.Random, out_path: Path):
    gt_rect = None  # (x0, y0, w, h) bottom-left origin, points
    c = canvas.Canvas(str(out_path), pagesize=(PDF_W, PDF_H))
    # Some faux printed lines so the rendered heuristic has context.
    for i in range(rng.randint(3, 6)):
        y = 600.0 + i * 28
        c.line(60, y, 60 + rng.uniform(200, 420), y)
    c.save()

    with pikepdf.open(out_path, allow_overwriting_input=True) as pdf:
        page = pdf.pages[0]
        if is_positive:
            w = 200.0 + rng.uniform(0, 80)
            h = 44.0 + rng.uniform(0, 16)
            x0 = 60.0 + rng.uniform(0, 120)
            y0 = 120.0 + rng.uniform(0, 60)
            _inject_widget(pdf, page, (x0, y0, w, h), "/Sig", "Signature")
            gt_rect = (x0, y0, w, h)
            # Also draw a mark so the rendered heuristic corroborates.
            _draw_signature_mark(c, rng)
        else:
            # Negative: a text widget (detector emits a 'text' candidate -> label 0).
            tw = 180.0 + rng.uniform(0, 60)
            th = 36.0 + rng.uniform(0, 12)
            tx = 80.0 + rng.uniform(0, 120)
            ty = 150.0 + rng.uniform(0, 40)
            _inject_widget(pdf, page, (tx, ty, tw, th), "/Tx", "TextField")
            # 50% hard negatives: a drawn signature-like mark the heuristic mis-fires on.
            if rng.random() < 0.5:
                _draw_signature_mark(c, rng)
        pdf.save()
    return gt_rect


# ---------------------------------------------------------------------------
# Manifest assembly
# ---------------------------------------------------------------------------


def _split_for(index: int, total: int):
    # 70 / 15 / 15 train / val / test.
    if index < int(total * 0.7):
        return "train"
    if index < int(total * 0.85):
        return "val"
    return "test"


def generate_image_dataset(out_dir: Path, n: int, seed: int) -> Path:
    img_dir = out_dir / "image_signatures" / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    samples = []
    for i in range(n):
        is_pos = i % 2 == 0
        arr, bbox = _make_image(is_pos, rng)
        fname = f"img-{i:04d}.png"
        Image.fromarray(arr).save(img_dir / fname)
        gts = [{"label": "signature", "bbox": [bbox[0], bbox[1], bbox[2], bbox[3]]}] if (is_pos and bbox) else []
        samples.append(
            {
                "sample_id": f"img-{i:04d}",
                "asset_path": f"images/{fname}",
                "split": _split_for(i, n),
                "ground_truth": gts,
            }
        )
    manifest = {
        "name": "image-signatures-generated-v1",
        "detector": "image",
        "iou_match_threshold": 0.5,
        "samples": samples,
    }
    manifest.update(_manifest_metadata("image", n, seed))
    (out_dir / "image_signatures" / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return out_dir / "image_signatures" / "manifest.json"


def generate_pdf_dataset(out_dir: Path, n: int, seed: int) -> Path:
    pdf_dir = out_dir / "pdf_fields" / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed + 1)
    samples = []
    for i in range(n):
        is_pos = i % 2 == 0
        fname = f"doc-{i:04d}.pdf"
        gt_rect = _make_pdf(is_pos, rng, pdf_dir / fname)
        gts = []
        if gt_rect is not None:
            x0, y0, w, h = gt_rect
            gts.append({"label": "signature", "page_index": 0, "bbox": [x0, y0, w, h]})
        samples.append(
            {
                "sample_id": f"doc-{i:04d}",
                "asset_path": f"pdfs/{fname}",
                "split": _split_for(i, n),
                "ground_truth": gts,
            }
        )
    manifest = {
        "name": "pdf-fields-generated-v1",
        "detector": "pdf",
        "iou_match_threshold": 0.5,
        "samples": samples,
    }
    manifest.update(_manifest_metadata("pdf", n, seed))
    (out_dir / "pdf_fields" / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return out_dir / "pdf_fields" / "manifest.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="datasets")
    ap.add_argument("--image-n", type=int, default=120)
    ap.add_argument("--pdf-n", type=int, default=120)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    img_man = generate_image_dataset(out, args.image_n, args.seed)
    pdf_man = generate_pdf_dataset(out, args.pdf_n, args.seed)
    print(f"wrote image manifest: {img_man} ({args.image_n} samples)")
    print(f"wrote pdf   manifest: {pdf_man} ({args.pdf_n} samples)")


if __name__ == "__main__":
    main()
