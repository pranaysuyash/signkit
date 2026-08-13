#!/usr/bin/env python3
"""Validate the test-data manifest and report quality gaps."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MANDATORY_COLUMNS = [
    "file",
    "type",
    "purpose",
    "generation",
    "source",
    "reproducible_seed",
    "origin",
    "pii",
    "contains_pii",
    "redacted",
    "reviewed_on",
    "sha256",
]


def parse_manifest(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    table_rows = []
    header_seen = False
    for line in lines:
        text = line.strip()
        if not text.startswith("|"):
            continue
        if text.startswith("| ---"):
            header_seen = True
            continue
        if text.startswith("| file ") or text.startswith("|file"):
            continue
        if not header_seen:
            continue
        if not text:
            break
        # stop if row no longer looks like markdown table
        if not re.match(r"^\|\s*`[^`]+`", text):
            break
        cols = [c.strip() for c in text.strip("|").split("|")]
        if len(cols) < len(MANDATORY_COLUMNS):
            continue
        row = dict(zip(MANDATORY_COLUMNS, cols[: len(MANDATORY_COLUMNS)]))
        table_rows.append(row)
    return table_rows


def validate_row(row: dict[str, str], issues: list[str], warnings: list[str], repo_root: Path):
    fixture = repo_root / row["file"].strip("`")
    if not fixture.exists():
        issues.append(f"missing_file={row['file']}")

    if row["type"] not in {"pdf", "image", "json", "other"}:
        issues.append(f"invalid_type={row['file']}:{row['type']}")

    if row["pii"] not in {"yes", "no", "unknown"}:
        issues.append(f"invalid_pii={row['file']}:{row['pii']}")

    if row["contains_pii"] not in {"yes", "no", "unknown"}:
        issues.append(f"invalid_contains_pii={row['file']}:{row['contains_pii']}")

    if row["redacted"] not in {"yes", "no", "partial", "n/a"}:
        issues.append(f"invalid_redacted={row['file']}:{row['redacted']}")

    sha256 = row["sha256"].lower()
    if sha256 not in {"", "n/a"}:
        if not re.fullmatch(r"[0-9a-f]{64}", sha256):
            issues.append(f"invalid_sha256={row['file']}:{row['sha256']}")

    if row["contains_pii"] in {"yes", "unknown"} and row["redacted"] == "no":
        warnings.append(f"pii_not_confirmed_handled={row['file']}:{row['contains_pii']}")

    if not row["source"]:
        warnings.append(f"missing_source={row['file']}")

    if row["generation"] in {"synthetic", "generated"} and row["reproducible_seed"] in {
        "",
        "N/A",
        "na",
        "n/a",
    }:
        warnings.append(f"missing_seed_for_generated={row['file']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default="docs/test_data_manifest.md",
        help="Path to markdown manifest.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root for fixture path checks.",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    repo_root = Path(args.repo_root).resolve()

    rows = parse_manifest(manifest_path)
    if not rows:
        raise SystemExit("manifest_error: no table rows parsed. Check manifest format.")

    issues: list[str] = []
    warnings: list[str] = []

    for row in rows:
        validate_row(row, issues, warnings, repo_root)

    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f" - {warning}")

    if issues:
        print("BLOCKERS:")
        for issue in issues:
            print(f" - {issue}")
        raise SystemExit(2)

    print(f"Manifest OK: {len(rows)} entries validated.")


if __name__ == "__main__":
    main()
