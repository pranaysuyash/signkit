#!/usr/bin/env python3
"""Generate the deterministic, identity-free signature fixture used by tests."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def generate_asset(output: Path, *, size: int = 512) -> None:
    """Write a synthetic signature-like mark with stable geometry and encoding."""

    image = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(image)
    scale = size / 512

    def point(x: float, y: float) -> tuple[int, int]:
        return round(x * scale), round(y * scale)

    strokes = [
        [(54, 294), (72, 252), (90, 188), (111, 140), (125, 185), (135, 254), (146, 300)],
        [(98, 264), (130, 235), (158, 220), (182, 224), (198, 244), (194, 270), (178, 289), (150, 292), (126, 280)],
        [(198, 274), (220, 232), (244, 208), (266, 211), (276, 238), (270, 272), (250, 292)],
        [(278, 278), (302, 238), (329, 216), (350, 226), (355, 255), (347, 286), (325, 302)],
        [(358, 286), (382, 254), (406, 242), (429, 250), (445, 271), (455, 298)],
        [(45, 326), (112, 319), (185, 324), (266, 333), (344, 327), (420, 319), (468, 326)],
    ]
    for stroke in strokes:
        draw.line([point(x, y) for x, y in stroke], fill=(25, 25, 45), width=max(2, round(5 * scale)), joint="curve")

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="JPEG", quality=95, optimize=False, progressive=False, subsampling=0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("desktop_app/resources/signature_template_synthetic_512.jpg"),
    )
    parser.add_argument(
        "--png-output",
        type=Path,
        help="also write the same synthetic mark as a PNG fixture",
    )
    args = parser.parse_args()
    generate_asset(args.output)
    if args.png_output:
        args.png_output.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(args.output) as image:
            image.save(args.png_output, format="PNG", optimize=False)
        print(f"generated synthetic PNG fixture: {args.png_output}")
    print(f"generated synthetic signature asset: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
