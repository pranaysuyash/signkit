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
DEPLOYED_HIGH_RISK_CLAIMS = (
    "100% offline",
    "100 percent offline",
    "your files never leave your computer",
    "your data never touches our servers",
    "own forever",
)


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


def _media_type(content_type: object) -> str:
    return str(content_type or "").split(";", 1)[0].strip().lower()


def _content_type_matches(content_type: object, expected: str) -> bool:
    actual = _media_type(content_type)
    if expected == "application/javascript":
        return actual in {"application/javascript", "text/javascript"}
    if expected == "application/xml":
        return "xml" in actual
    return actual == expected


def validate_asset_response(
    path: str,
    result: dict[str, object],
    *,
    expected_content_type: str,
    required_marker: str,
) -> list[str]:
    """Return release-gate failures for one deployed executable asset."""

    errors: list[str] = []
    if result.get("status") != 200:
        errors.append(f"{path} expected 200, got {result.get('status')}")
    if not _content_type_matches(result.get("content_type"), expected_content_type):
        errors.append(
            f"{path} expected content-type {expected_content_type}, "
            f"got {result.get('content_type') or '<empty>'}"
        )
    if required_marker not in str(result.get("body", "")):
        errors.append(f"{path} is not the canonical instrumented runtime")
    return errors


def validate_root_response(result: dict[str, object]) -> list[str]:
    """Return release-gate failures for the canonical deployed root page."""

    errors: list[str] = []
    if result.get("status") != 200:
        errors.append(f"/ expected 200, got {result.get('status')}")
    if not _content_type_matches(result.get("content_type"), "text/html"):
        errors.append(
            f"/ expected content-type text/html, got "
            f"{result.get('content_type') or '<empty>'}"
        )
    body = str(result.get("body", ""))
    if "public_surface_boundary" not in body:
        errors.append("/ does not contain the current canonical public-surface marker")
    lowered = body.lower()
    for claim in DEPLOYED_HIGH_RISK_CLAIMS:
        if claim in lowered:
            errors.append(f"/ contains retired high-risk claim: {claim}")
    return errors


def probe(base_url: str) -> dict[str, object]:
    opener = build_opener(NoRedirectHandler)
    errors: list[str] = []
    results: dict[str, object] = {}

    root = fetch(opener, base_url, "/")
    results["/"] = root
    errors.extend(validate_root_response(root))

    for path in redirect_paths():
        result = fetch(opener, base_url, path)
        results[path] = result
        if result.get("status") != 301:
            errors.append(f"{path} expected 301, got {result.get('status')}")
        if not str(result.get("location", "")).startswith("/"):
            errors.append(f"{path} does not redirect to a root-relative location")

    checkout = fetch(opener, base_url, "/web/live/js/checkout.js")
    results["/web/live/js/checkout.js"] = checkout
    errors.extend(
        validate_asset_response(
            "/web/live/js/checkout.js",
            checkout,
            expected_content_type="application/javascript",
            required_marker="checkout_intent",
        )
    )

    checkout_config = fetch(opener, base_url, "/web/live/js/checkout-config.js")
    results["/web/live/js/checkout-config.js"] = checkout_config
    errors.extend(
        validate_asset_response(
            "/web/live/js/checkout-config.js",
            checkout_config,
            expected_content_type="application/javascript",
            required_marker="SignKitCheckoutConfig",
        )
    )

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
