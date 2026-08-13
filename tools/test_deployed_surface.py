#!/usr/bin/env python3
"""Probe the deployed SignKit public-surface contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


ROOT = Path(__file__).resolve().parents[1]
REDIRECTS = ROOT / "_redirects"


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file, code, msg, headers, newurl):
        return None


def redirect_paths() -> list[str]:
    paths = []
    for line in REDIRECTS.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[2] == "301" and "*" not in fields[0]:
            paths.append(fields[0])
    return sorted(set(paths))


def fetch(opener, base_url: str, path: str) -> dict[str, object]:
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        headers={"User-Agent": "Mozilla/5.0 (SignKit release surface probe)"},
        method="GET",
    )
    try:
        with opener.open(request, timeout=15) as response:
            return {
                "status": response.status,
                "location": response.headers.get("Location"),
                "content_type": response.headers.get("Content-Type"),
                "body": response.read(4000).decode("utf-8", errors="replace"),
            }
    except HTTPError as error:
        return {
            "status": error.code,
            "location": error.headers.get("Location"),
            "content_type": error.headers.get("Content-Type"),
            "body": error.read(4000).decode("utf-8", errors="replace"),
        }
    except URLError as error:
        return {"status": None, "error": str(error)}


def probe(base_url: str) -> dict[str, object]:
    opener = build_opener(NoRedirectHandler)
    errors: list[str] = []
    results: dict[str, object] = {}

    root = fetch(opener, base_url, "/")
    results["/"] = root
    if root.get("status") != 200:
        errors.append(f"/ expected 200, got {root.get('status')}")
    if "public_surface_boundary" not in str(root.get("body", "")):
        errors.append("/ does not contain the current canonical public-surface marker")

    for path in redirect_paths():
        result = fetch(opener, base_url, path)
        results[path] = result
        if result.get("status") != 301:
            errors.append(f"{path} expected 301, got {result.get('status')}")
        if not str(result.get("location", "")).startswith("/"):
            errors.append(f"{path} does not redirect to a root-relative location")

    checkout = fetch(opener, base_url, "/web/live/js/checkout.js")
    results["/web/live/js/checkout.js"] = checkout
    if checkout.get("status") != 200:
        errors.append(f"checkout asset expected 200, got {checkout.get('status')}")
    if "checkout_intent" not in str(checkout.get("body", "")):
        errors.append("deployed checkout asset is not the canonical instrumented runtime")

    return {"status": "pass" if not errors else "fail", "errors": errors, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://signkit.work")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = probe(args.base_url)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"deployed surface probe: {result['status'].upper()}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
