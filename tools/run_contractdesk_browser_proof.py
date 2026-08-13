"""Exercise the live ContractDesk workspace surface through a real browser.

The backend proof server must already be running, typically with
``run_contractdesk_web_proof.py --keep-running``. This is intentionally a
small browser control-plane proof, not a claim of hosted document processing,
cryptographic signing, or legal certificate validity.
"""

from __future__ import annotations

import argparse
import json
import re
from urllib.request import urlopen

from playwright.sync_api import sync_playwright


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8872")
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()

    workspace_url = f"{args.base_url.rstrip('/')}/workspace-app/index.html"
    with urlopen(f"{args.base_url.rstrip('/')}/health", timeout=5) as response:
        if response.status != 200:
            raise RuntimeError(f"health returned HTTP {response.status}")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=not args.headed)
        page = browser.new_page()
        response = page.goto(workspace_url, wait_until="networkidle")
        if response is None or response.status != 200:
            status = response.status if response is not None else "no response"
            raise RuntimeError(f"workspace returned HTTP {status}")

        body = page.locator("body").inner_text()
        required_patterns = {
            "workspace_title": r"SignKit Workspace",
            "local_boundary": r"local[- ]companion",
            "cloud_boundary": r"metadata-only",
            "source_deletion_boundary": r"deletes source bytes|source bytes after",
        }
        missing = [
            name for name, pattern in required_patterns.items()
            if re.search(pattern, body, re.IGNORECASE) is None
        ]
        browser.close()

    if missing:
        raise RuntimeError(f"workspace proof missing markers: {', '.join(missing)}")

    print(json.dumps({
        "status": "pass",
        "workspace_url": workspace_url,
        "evidence": "browser control-plane integration",
        "markers": sorted(required_patterns),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
