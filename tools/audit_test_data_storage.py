#!/usr/bin/env python3
"""Report disk pressure and candidate cleanup targets without deleting anything."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


def directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for root, _, files in os.walk(path):
        for filename in files:
            try:
                total += (Path(root) / filename).stat().st_size
            except OSError:
                continue
    return total


def format_size(value: int) -> str:
    size = float(value)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if size < 1024 or unit == "GiB":
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{value}B"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    usage = shutil.disk_usage(repo_root)
    print(f"filesystem total={format_size(usage.total)} used={format_size(usage.used)} free={format_size(usage.free)}")
    candidates = (
        ("canonical project runtime", repo_root / ".venv", "protected; do not delete"),
        ("alternate project runtime", repo_root / "venv", "review before deletion; may be stale duplicate"),
        ("type-check cache", repo_root / ".mypy_cache", "generated; deletion requires approval"),
        ("pytest cache", repo_root / ".pytest_cache", "generated; deletion requires approval"),
        ("private external corpus", repo_root.parent / ".private" / "ultralytics_signature_v0.0.0", "protected raw data; do not delete"),
    )
    for label, path, disposition in candidates:
        print(f"{label}: path={path} size={format_size(directory_size(path))} disposition={disposition}")
    print("No files were deleted or modified by this audit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
