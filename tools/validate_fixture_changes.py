#!/usr/bin/env python3
"""Check whether fixture changes are accompanied by manifest updates."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Set


def git_diff_names(base: str, head: str) -> list[str]:
    output = subprocess.check_output(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        text=True,
    )
    return [line.strip() for line in output.splitlines() if line.strip()]


def classify_changes(changed: list[str]) -> tuple[Set[str], Set[str]]:
    fixture_prefix = "desktop_app/tests/fixtures/"
    fixture_changes = {p for p in changed if p.startswith(fixture_prefix)}
    manifest_changes = {p for p in changed if p == "docs/test_data_manifest.md"}
    return fixture_changes, manifest_changes


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate fixture edits have corresponding manifest updates."
    )
    parser.add_argument("--base", default="HEAD~1", help="Base ref for comparison")
    parser.add_argument("--head", default="HEAD", help="Head ref for comparison")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if fixture changes are unreviewed in manifest.",
    )
    args = parser.parse_args()

    changed = git_diff_names(args.base, args.head)
    fixture_changes, manifest_changes = classify_changes(changed)

    if not fixture_changes:
        print("No fixture path changes detected.")
        return

    print("Fixture changes detected:")
    for path in sorted(fixture_changes):
        print(f" - {path}")

    if manifest_changes:
        print("Manifest updated: docs/test_data_manifest.md")
    elif args.strict:
        print(
            "ERROR: fixture changes detected without docs/test_data_manifest.md updates "
            "(run this in review context or add --strict false if intentionally handled elsewhere)."
        )
        raise SystemExit(2)
    else:
        print(
            "WARN: fixture changes detected without manifest update. "
            "Use this as a review signal before merge."
        )


if __name__ == "__main__":
    main()
