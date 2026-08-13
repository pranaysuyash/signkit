#!/usr/bin/env python3
"""Generate a deterministic subject-disjoint synthetic signature benchmark."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np


SEED = 20260813
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "desktop_app/tests/fixtures/signature_benchmark_v1"
METADATA_PATH = OUTPUT_DIR / "metadata.json"
IMAGE_SIZE = (512, 512)


def _draw_page(subject_index: int, signature_count: int) -> tuple[np.ndarray, list[list[int]]]:
    rng = np.random.default_rng(SEED + subject_index)
    background = np.full((IMAGE_SIZE[1], IMAGE_SIZE[0], 3), 238, dtype=np.int16)
    background += rng.normal(0, 3, background.shape).astype(np.int16)
    image = np.clip(background, 220, 250).astype(np.uint8)
    cv2.putText(
        image,
        f"SYNTHETIC PAGE {subject_index:02d}",
        (24, 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (35, 35, 35),
        2,
        cv2.LINE_AA,
    )
    if signature_count == 0:
        return image, []

    centers = [(130, 190), (380, 320)] if signature_count == 2 else [(256, 255)]
    boxes: list[list[int]] = []
    ink = (185 + subject_index % 15, 42 + subject_index % 8, 18)
    for center_x, center_y in centers:
        cx = center_x + int(rng.integers(-8, 9))
        cy = center_y + int(rng.integers(-8, 9))
        points = np.array(
            [
                (cx - 65, cy + 10),
                (cx - 45, cy - 24),
                (cx - 25, cy + 20),
                (cx - 5, cy - 18),
                (cx + 15, cy + 20),
                (cx + 40, cy - 5),
                (cx + 68, cy - 20),
            ],
            dtype=np.int32,
        )
        cv2.polylines(image, [points], False, ink, 6, cv2.LINE_AA)
        cv2.ellipse(image, (cx + 20, cy + 5), (48, 18), -10, 0, 310, ink, 5, cv2.LINE_AA)
        cv2.line(image, (cx - 76, cy + 43), (cx + 76, cy + 40), ink, 5, cv2.LINE_AA)
        boxes.append([cx - 84, cy - 55, cx + 84, cy + 56])
    return image, boxes


def generate() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cases: list[dict] = []
    counts = (0, 1, 2, 1, 0, 2, 1, 2, 0, 1, 2, 1)
    for subject_index, signature_count in enumerate(counts):
        split = "train" if subject_index < 6 else "validation" if subject_index < 9 else "test"
        subject_id = f"synthetic-subject-{subject_index:02d}"
        name = f"{subject_id}-page-01"
        image, ground_truth = _draw_page(subject_index, signature_count)
        file_path = OUTPUT_DIR / f"{name}.png"
        if not cv2.imwrite(str(file_path), image):
            raise RuntimeError(f"could not write {file_path}")
        count_tag = "none" if signature_count == 0 else "single" if signature_count == 1 else "multiple"
        cases.append(
            {
                "name": name,
                "file": str(file_path.relative_to(ROOT)),
                "subject_id": subject_id,
                "split": split,
                "ground_truth": ground_truth,
                "tags": ["synthetic", "ink:blue", "split:subject-disjoint", f"signature_count:{count_tag}"],
                "image_size": list(IMAGE_SIZE),
            }
        )

    for case in cases:
        case["sha256"] = hashlib.sha256((ROOT / case["file"]).read_bytes()).hexdigest()
    metadata = {
        "schema_version": "1.0.0",
        "seed": SEED,
        "generator": "tools/generate_signature_benchmark.py",
        "privacy": "synthetic only; procedurally generated strokes; no production or human data",
        "annotation_schema": "ground_truth boxes are [x1, y1, x2, y2] in source-image pixels",
        "split_policy": "subject-disjoint train/validation/test; subject_id must occur in one split only",
        "cases": cases,
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


if __name__ == "__main__":
    result = generate()
    print(f"Generated {len(result['cases'])} benchmark pages with seed={SEED}")
