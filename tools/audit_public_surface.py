#!/usr/bin/env python3
"""Audit the canonical SignKit public-surface contract.

The auditor treats `_redirects` and `serve.py` as runtime authorities, the
launch registry and `index.html` as claim authorities, and retained variants as
historical sources that may produce warnings but cannot become public routes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REDIRECTS = ROOT / "_redirects"
SERVER = ROOT / "serve.py"
INDEX = ROOT / "index.html"
REGISTRY = ROOT / "docs" / "launch_claims" / "registry.md"
HIGH_RISK_TERMS = (
    "100% offline",
    "100 percent offline",
    "your data never touches our servers",
    "your files never leave your computer",
    "saves you $1,000",
    "4.8/5",
    "YOUR_PRODUCT_ID",
)


def _server_paths() -> set[str]:
    source = SERVER.read_text(encoding="utf-8")
    match = re.search(
        r"LEGACY_ROUTE_PATHS\s*=\s*frozenset\(\s*\{(.*?)\n\s*\}\s*\)",
        source,
        re.DOTALL,
    )
    if not match:
        return set()
    return set(re.findall(r'"([^"\\]+)"', match.group(1)))


def _server_wildcard_paths() -> set[str]:
    source = SERVER.read_text(encoding="utf-8")
    prefixes_match = re.search(
        r"LEGACY_ROUTE_PREFIXES\s*=\s*\((.*?)\n\s*\)",
        source,
        re.DOTALL,
    )
    patterns_match = re.search(
        r"LEGACY_ROUTE_PATTERNS\s*=\s*\((.*?)\)",
        source,
        re.DOTALL,
    )
    prefixes = set()
    if prefixes_match:
        prefixes = {f"{value}*" for value in re.findall(r'"([^"\\]+)"', prefixes_match.group(1))}
    patterns = set()
    if patterns_match:
        patterns = set(re.findall(r'"([^"\\]+\*[^"\\]*)"', patterns_match.group(1)))
    return prefixes | patterns


def _redirect_paths() -> set[str]:
    paths: set[str] = set()
    for line in REDIRECTS.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[2] == "301" and "*" not in fields[0]:
            paths.add(fields[0])
    return paths


def _redirect_wildcard_paths() -> set[str]:
    paths: set[str] = set()
    for line in REDIRECTS.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[2] == "301" and "*" in fields[0]:
            paths.add(fields[0])
    return paths


def _registry_ids() -> set[str]:
    registry = REGISTRY.read_text(encoding="utf-8")
    return set(re.findall(r"\| `([a-z_]+)` \|", registry))


def _index_ids() -> set[str]:
    page = INDEX.read_text(encoding="utf-8")
    return set(re.findall(r"<!--\s*launch-claim:\s*([a-z_]+)\s*-->", page))


def _legacy_warnings(paths: set[str]) -> list[str]:
    warnings: list[str] = []
    for path in sorted(paths):
        if not path.endswith(".html") or path == "/index.html":
            continue
        file_path = ROOT / path.lstrip("/")
        if not file_path.exists():
            warnings.append(f"redirect target source is missing: {path}")
            continue
        text = file_path.read_text(encoding="utf-8", errors="replace")
        if "launch-claim:" in text:
            warnings.append(f"retained page contains claim markers: {path}")
        if "gumroad.com/l/" in text or "gum.new/" in text:
            warnings.append(f"retained page contains direct checkout reference: {path}")
        for term in HIGH_RISK_TERMS:
            if term.lower() in text.lower():
                warnings.append(f"retained page contains high-risk claim '{term}': {path}")
    return warnings


def audit() -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    server_paths = _server_paths()
    server_wildcard_paths = _server_wildcard_paths()
    redirect_paths = _redirect_paths()
    redirect_wildcard_paths = _redirect_wildcard_paths()
    registry_ids = _registry_ids()
    index_ids = _index_ids()

    if not server_paths:
        errors.append("serve.py has no parseable LEGACY_ROUTE_PATHS contract")
    if "/" in server_paths:
        errors.append("canonical / must not be listed as a legacy route")

    missing_redirects = sorted(server_paths - redirect_paths)
    if missing_redirects:
        errors.append(f"legacy paths missing from _redirects: {missing_redirects}")

    missing_server_paths = sorted(redirect_paths - server_paths - {"/docs/*.html", "/deploy_dist/*"})
    if missing_server_paths:
        warnings.append(f"redirect-only paths not represented in local server contract: {missing_server_paths}")

    missing_wildcard_paths = sorted(server_wildcard_paths - redirect_wildcard_paths)
    if missing_wildcard_paths:
        errors.append(f"wildcard local paths missing from _redirects: {missing_wildcard_paths}")
    extra_wildcard_paths = sorted(redirect_wildcard_paths - server_wildcard_paths)
    if extra_wildcard_paths:
        errors.append(f"wildcard _redirects paths missing from local server contract: {extra_wildcard_paths}")

    if index_ids != registry_ids:
        errors.append(
            f"claim parity mismatch: index-only={sorted(index_ids - registry_ids)}, "
            f"registry-only={sorted(registry_ids - index_ids)}"
        )

    index_text = INDEX.read_text(encoding="utf-8")
    if 'rel="canonical" href="https://signkit.work"' not in index_text:
        errors.append("index.html is missing the canonical URL")
    for asset in ("web/live/js/checkout-config.js", "web/live/js/checkout.js"):
        if asset not in index_text:
            errors.append(f"index.html is missing canonical checkout asset: {asset}")
    for term in HIGH_RISK_TERMS:
        if term.lower() in index_text.lower():
            errors.append(f"canonical index contains high-risk claim: {term}")

    warnings.extend(_legacy_warnings(server_paths))
    historical_docs = []
    for directory in (ROOT / "docs" / "landing", ROOT / "docs" / "moved_root_docs"):
        if directory.exists():
            for file_path in directory.rglob("*.md"):
                if file_path.name == "CANONICAL_SURFACE_ADDENDUM_2026-08-12.md":
                    continue
                text = file_path.read_text(encoding="utf-8", errors="replace")
                if re.search(r"/root|/buy|/purchase|/gum", text):
                    historical_docs.append(str(file_path.relative_to(ROOT)))
    if historical_docs:
        warnings.append(f"historical docs reference retired routes: {len(historical_docs)} files")

    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "server_legacy_path_count": len(server_paths),
        "redirect_legacy_path_count": len(redirect_paths),
        "server_wildcard_path_count": len(server_wildcard_paths),
        "redirect_wildcard_path_count": len(redirect_wildcard_paths),
        "claim_count": len(index_ids),
        "historical_docs_with_retired_routes": historical_docs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="return non-zero when blocking errors exist")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    result = audit()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"public surface audit: {result['status'].upper()}")
        print(f"legacy paths: {result['server_legacy_path_count']} local / {result['redirect_legacy_path_count']} deployed")
        print(f"governed claims: {result['claim_count']}")
        for message in result["errors"]:
            print(f"ERROR: {message}")
        for message in result["warnings"]:
            print(f"WARNING: {message}")
    return 1 if args.strict and result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
