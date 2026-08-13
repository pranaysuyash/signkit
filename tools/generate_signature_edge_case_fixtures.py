#!/usr/bin/env python3
"""Generate deterministic, privacy-safe signature extraction edge fixtures."""

from __future__ import annotations

import json
import hashlib
import random
from pathlib import Path

from PIL import Image, ImageDraw


SEED = 20260812
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "desktop_app/tests/fixtures/signature_edge_cases"
METADATA_PATH = OUTPUT_DIR / "metadata.json"


def _draw_mark(
    *,
    background: int,
    ink: int,
    offset: tuple[int, int] = (0, 0),
    stroke_width: int = 5,
) -> Image.Image:
    image = Image.new("L", (512, 512), color=background)
    draw = ImageDraw.Draw(image)
    ox, oy = offset
    paths = [
        [(105, 300), (130, 230), (155, 170), (180, 300), (205, 235), (230, 175), (250, 305)],
        [(250, 275), (270, 245), (300, 245), (320, 275), (300, 305), (270, 305), (250, 275)],
        [(330, 185), (330, 295), (340, 310), (370, 310), (395, 290), (405, 260)],
        [(95, 345), (150, 350), (220, 352), (290, 350), (365, 347), (425, 345)],
    ]
    for path in paths:
        draw.line([(x + ox, y + oy) for x, y in path], fill=ink, width=stroke_width, joint="curve")
    return image


def _draw_noisy(rng: random.Random) -> Image.Image:
    image = _draw_mark(background=248, ink=18, offset=(45, -12), stroke_width=5)
    pixels = image.load()
    for _ in range(1800):
        x = rng.randrange(image.width)
        y = rng.randrange(image.height)
        if pixels[x, y] > 80:
            pixels[x, y] = rng.randrange(235, 249)
    return image


def _draw_occluded() -> Image.Image:
    image = _draw_mark(background=255, ink=18)
    ImageDraw.Draw(image).rectangle((245, 205, 325, 335), fill=255)
    return image


def _draw_multi_signature() -> Image.Image:
    image = Image.new("L", (512, 512), color=255)
    draw = ImageDraw.Draw(image)
    for offset in (0, 205):
        paths = [
            [(45, 300), (70, 230), (95, 170), (120, 300), (145, 235), (170, 175), (190, 305)],
            [(190, 275), (210, 245), (235, 245), (250, 275), (235, 305), (210, 305), (190, 275)],
            [(260, 185), (260, 295), (270, 310), (295, 310), (315, 285), (325, 255)],
            [(35, 345), (90, 350), (145, 352), (175, 350)],
        ]
        for path in paths:
            draw.line([(x + offset, y) for x, y in path], fill=18, width=5, joint="curve")
    return image


def _save_png(image: Image.Image, name: str) -> str:
    path = OUTPUT_DIR / name
    image.save(path, format="PNG", optimize=False)
    return str(path.relative_to(ROOT))


def generate() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    cases = [
        {
            "name": "blank_canvas",
            "file": _save_png(Image.new("L", (512, 512), color=255), "blank_canvas.png"),
            "expected_detection": "none",
            "ground_truth": [],
            "tags": ["blank", "background_only"],
        },
        {
            "name": "low_contrast",
            "file": _save_png(_draw_mark(background=230, ink=168), "low_contrast.png"),
            "expected_detection": "present",
            "ground_truth": [[90, 160, 430, 360]],
            "min_width": 120,
            "min_height": 40,
            "tags": ["contrast:low", "background:gray"],
        },
        {
            "name": "rotated_tilted",
            "file": _save_png(
                _draw_mark(background=255, ink=18).rotate(
                    12, resample=Image.Resampling.BICUBIC, expand=False, fillcolor=255
                ),
                "rotated_tilted.png",
            ),
            "expected_detection": "present",
            "ground_truth": [[70, 130, 445, 385]],
            "min_width": 120,
            "min_height": 40,
            "tags": ["rotation:tilted", "background:white"],
        },
        {
            "name": "offset_noisy",
            "file": _save_png(_draw_noisy(rng), "offset_noisy.png"),
            "expected_detection": "present",
            "ground_truth": [[135, 145, 475, 350]],
            "min_width": 120,
            "min_height": 40,
            "tags": ["signature_position:offset", "scan_noise:high"],
        },
        {
            "name": "partial_occlusion",
            "file": _save_png(_draw_occluded(), "partial_occlusion.png"),
            "expected_detection": "present",
            "ground_truth": [[90, 160, 425, 355]],
            "min_width": 100,
            "min_height": 35,
            "tags": ["occlusion:partial", "signature_position:center"],
        },
        {
            "name": "multi_signature",
            "file": _save_png(_draw_multi_signature(), "multi_signature.png"),
            "expected_detection": "present",
            "ground_truth": [[30, 160, 360, 355], [235, 160, 510, 355]],
            "min_width": 120,
            "min_height": 40,
            "tags": ["signature_count:multiple", "signature_position:split"],
        },
    ]
    metadata = {
        "schema_version": "1.0.0",
        "seed": SEED,
        "generator": "tools/generate_signature_edge_case_fixtures.py",
        "privacy": "synthetic only; no production-derived strokes",
        "annotation_schema": "ground_truth boxes are [x1, y1, x2, y2] in source-image pixels",
        "cases": cases,
    }
    for case in cases:
        case["split"] = "regression"
        case["image_size"] = [512, 512]
        case["sha256"] = hashlib.sha256((ROOT / case["file"]).read_bytes()).hexdigest()
    METADATA_PATH.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


if __name__ == "__main__":
    result = generate()
    print(f"Generated {len(result['cases'])} signature edge fixtures with seed={SEED}")
