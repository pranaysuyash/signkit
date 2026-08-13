#!/usr/bin/env python3
"""Inspect SignverOD Parquet metadata without copying document images into Git."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

EXPECTED_CATEGORIES = {1: "signature", 2: "initials", 3: "redaction", 4: "date"}


def inspect(paths: list[Path]) -> dict[str, object]:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError(
            "SignverOD inspection requires the optional pyarrow dependency; "
            "install the research environment before running this tool."
        ) from exc

    total_rows = 0
    total_boxes = 0
    category_counts: Counter[str] = Counter()
    box_counts: Counter[int] = Counter()
    shards: list[dict[str, object]] = []
    for path in paths:
        parquet_file = pq.ParquetFile(path)
        rows = 0
        boxes = 0
        shard_categories: Counter[str] = Counter()
        shard_box_counts: Counter[int] = Counter()
        for batch in parquet_file.iter_batches(columns=["width", "height", "objects", "image_id"]):
            objects_column = batch.column(batch.schema.get_field_index("objects"))
            for objects in objects_column.to_pylist():
                category_values = (objects or {}).get("category", [])
                count = len(category_values)
                rows += 1
                boxes += count
                shard_box_counts[count] += 1
                for category in category_values:
                    label = EXPECTED_CATEGORIES.get(int(category), f"unknown:{category}")
                    shard_categories[label] += 1
        total_rows += rows
        total_boxes += boxes
        category_counts.update(shard_categories)
        box_counts.update(shard_box_counts)
        shards.append(
            {
                "path": str(path),
                "rows": rows,
                "boxes": boxes,
                "category_counts": dict(sorted(shard_categories.items())),
                "boxes_per_image": dict(sorted((str(key), value) for key, value in shard_box_counts.items())),
                "parquet_schema": str(parquet_file.schema_arrow),
            }
        )
    return {
        "schema_version": "1.0.0",
        "dataset": "SignverOD",
        "rows": total_rows,
        "boxes": total_boxes,
        "category_counts": dict(sorted(category_counts.items())),
        "boxes_per_image": dict(sorted((str(key), value) for key, value in box_counts.items())),
        "multi_box_images": sum(value for key, value in box_counts.items() if key >= 2),
        "shards": shards,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parquet", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = inspect(args.parquet)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
