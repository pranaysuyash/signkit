#!/usr/bin/env python3
"""Convert an Ultralytics YOLO signature corpus into SignKit metadata.

The source images remain in the caller-provided external directory. This tool
only writes metadata and never copies source images into the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

from PIL import Image


SOURCE_URL = "https://github.com/ultralytics/assets/releases/download/v0.0.0/signature.zip"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pixel_box(values: list[str], width: int, height: int) -> list[int]:
    if len(values) != 5:
        raise ValueError(f"YOLO annotation must contain 5 values: {' '.join(values)}")
    class_id, center_x, center_y, box_width, box_height = values
    if class_id != "0":
        raise ValueError(f"unexpected class id {class_id!r}; expected signature class 0")
    cx, cy, bw, bh = (float(value) for value in (center_x, center_y, box_width, box_height))
    if not (0 <= cx <= 1 and 0 <= cy <= 1 and 0 < bw <= 1 and 0 < bh <= 1):
        raise ValueError(f"normalized box is outside the valid range: {' '.join(values)}")
    x1 = max(0, min(width, round((cx - bw / 2) * width)))
    y1 = max(0, min(height, round((cy - bh / 2) * height)))
    x2 = max(0, min(width, round((cx + bw / 2) * width)))
    y2 = max(0, min(height, round((cy + bh / 2) * height)))
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"normalized box becomes empty in {width}x{height}: {' '.join(values)}")
    return [x1, y1, x2, y2]


def _read_boxes(label_path: Path, width: int, height: int) -> list[list[int]]:
    boxes: list[list[int]] = []
    for line_number, line in enumerate(label_path.read_text().splitlines(), start=1):
        values = line.split()
        if not values:
            continue
        try:
            boxes.append(_pixel_box(values, width, height))
        except ValueError as exc:
            raise ValueError(f"{label_path}:{line_number}: {exc}") from exc
    return boxes


def convert(dataset_root: Path, archive_sha256: str, intake_date: str, source_url: str) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for source_split, output_split in (("train", "development"), ("val", "validation")):
        image_dir = dataset_root / "images" / source_split
        label_dir = dataset_root / "labels" / source_split
        if not image_dir.is_dir() or not label_dir.is_dir():
            raise ValueError(f"missing source split directories for {source_split!r}")
        images = sorted(path for path in image_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)
        if not images:
            raise ValueError(f"no images found in {image_dir}")
        for image_path in images:
            label_path = label_dir / f"{image_path.stem}.txt"
            if not label_path.is_file():
                raise ValueError(f"missing label for {image_path}")
            with Image.open(image_path) as image:
                width, height = image.size
            boxes = _read_boxes(label_path, width, height)
            cases.append(
                {
                    "name": f"ultralytics_{source_split}_{image_path.stem}",
                    "file": str(image_path.relative_to(dataset_root)),
                    "expected_detection": "present" if boxes else "none",
                    "ground_truth": boxes,
                    "tags": ["external", "source:ultralytics", f"source_split:{source_split}", "license:agpl-3.0"],
                    "split": output_split,
                    "image_size": [width, height],
                    "sha256": _sha256(image_path),
                }
            )
    return {
        "schema_version": "1.0.0",
        "annotation_schema": "ground_truth boxes are [x1, y1, x2, y2] in source-image pixels",
        "privacy": "external source; internal evaluation only; no redistribution; raw images remain outside repository",
        "generator": "tools/import_ultralytics_signature_corpus.py",
        "source": {
            "name": "Ultralytics Signature Detection Dataset",
            "url": source_url,
            "archive_sha256": archive_sha256,
            "intake_date": intake_date,
            "license": "AGPL-3.0",
            "subject_provenance": "not established by published dataset documentation",
            "independent_test_split": False,
        },
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive-sha256", required=True)
    parser.add_argument("--intake-date", default=date.today().isoformat())
    parser.add_argument("--source-url", default=SOURCE_URL)
    args = parser.parse_args()
    metadata = convert(args.dataset_root.resolve(), args.archive_sha256, args.intake_date, args.source_url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Wrote {len(metadata['cases'])} cases to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
