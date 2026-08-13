#!/usr/bin/env python3
"""Validate labeled signature corpus structure before evaluation or release."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image


ALLOWED_SPLITS = {"regression", "train", "development", "validation", "test", "held_out"}
DEFAULT_REQUIRED_TAGS = {
    "blank",
    "contrast:low",
    "rotation:tilted",
    "scan_noise:high",
    "occlusion:partial",
    "signature_count:multiple",
}


def _box_is_valid(box: Any, width: int, height: int) -> bool:
    if not isinstance(box, list) or len(box) != 4:
        return False
    x1, y1, x2, y2 = box
    return (
        all(isinstance(value, (int, float)) for value in box)
        and 0 <= x1 < x2 <= width
        and 0 <= y1 < y2 <= height
    )


def validate_corpus(
    corpus_path: Path,
    repo_root: Path,
    *,
    require_held_out: bool = False,
    require_subject_disjoint: bool = False,
    required_tags: set[str] | None = None,
) -> list[str]:
    payload = json.loads(corpus_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if payload.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if not payload.get("annotation_schema"):
        errors.append("annotation_schema is required")
    if not payload.get("privacy"):
        errors.append("privacy provenance is required")

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["cases must be a non-empty list"]

    names: set[str] = set()
    files: set[str] = set()
    splits: dict[str, set[str]] = {}
    subjects_by_split: dict[str, set[str]] = {}
    observed_tags: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        name = case.get("name")
        file_name = case.get("file")
        split = case.get("split")
        if not isinstance(name, str) or not name:
            errors.append(f"{prefix}.name is required")
        elif name in names:
            errors.append(f"duplicate case name: {name}")
        else:
            names.add(name)
        if not isinstance(file_name, str) or not file_name:
            errors.append(f"{prefix}.file is required")
            continue
        if file_name in files:
            errors.append(f"duplicate fixture file across splits: {file_name}")
        files.add(file_name)
        if split not in ALLOWED_SPLITS:
            errors.append(f"{prefix}.split must be one of {sorted(ALLOWED_SPLITS)}")
        else:
            splits.setdefault(split, set()).add(file_name)
            if require_subject_disjoint:
                subject_id = case.get("subject_id")
                if not isinstance(subject_id, str) or not subject_id:
                    errors.append(f"{prefix}.subject_id is required for subject-disjoint validation")
                else:
                    subjects_by_split.setdefault(split, set()).add(subject_id)

        image_path = repo_root / file_name
        if not image_path.is_file():
            errors.append(f"missing image: {file_name}")
            continue
        image_size = case.get("image_size")
        if not isinstance(image_size, list) or len(image_size) != 2:
            errors.append(f"{prefix}.image_size must contain width and height")
            continue
        try:
            with Image.open(image_path) as image:
                actual_size = list(image.size)
        except Exception as exc:
            errors.append(f"cannot open {file_name}: {exc}")
            continue
        if actual_size != image_size:
            errors.append(f"image_size mismatch for {file_name}: {actual_size} != {image_size}")
        if case.get("sha256") != hashlib.sha256(image_path.read_bytes()).hexdigest():
            errors.append(f"sha256 mismatch for {file_name}")
        ground_truth = case.get("ground_truth")
        if not isinstance(ground_truth, list):
            errors.append(f"{prefix}.ground_truth must be a list")
        else:
            for box_index, box in enumerate(ground_truth):
                if not _box_is_valid(box, image_size[0], image_size[1]):
                    errors.append(f"invalid box {prefix}.ground_truth[{box_index}]")
        tags = case.get("tags")
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            errors.append(f"{prefix}.tags must be a list of strings")
        else:
            observed_tags.update(tags)

    if require_held_out and not (splits.get("test") or splits.get("held_out")):
        errors.append("held-out validation requires a test or held_out split")
    if require_subject_disjoint:
        split_names = sorted(subjects_by_split)
        for index, left_split in enumerate(split_names):
            for right_split in split_names[index + 1 :]:
                overlap = subjects_by_split[left_split] & subjects_by_split[right_split]
                if overlap:
                    errors.append(
                        f"subject leakage between {left_split} and {right_split}: "
                        + ", ".join(sorted(overlap))
                    )
    missing_tags = (required_tags or set()) - observed_tags
    if missing_tags:
        errors.append("missing required coverage tags: " + ", ".join(sorted(missing_tags)))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="desktop_app/tests/fixtures/signature_edge_cases/metadata.json")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--require-held-out", action="store_true")
    parser.add_argument("--require-subject-disjoint", action="store_true")
    parser.add_argument("--require-tag", action="append", default=[])
    args = parser.parse_args(argv)
    errors = validate_corpus(
        Path(args.repo_root).resolve() / args.corpus,
        Path(args.repo_root).resolve(),
        require_held_out=args.require_held_out,
        require_subject_disjoint=args.require_subject_disjoint,
        required_tags=set(args.require_tag) or DEFAULT_REQUIRED_TAGS,
    )
    if errors:
        print("SIGNATURE_CORPUS_ERROR:")
        for error in errors:
            print(f" - {error}")
        return 2
    print("Signature corpus OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
