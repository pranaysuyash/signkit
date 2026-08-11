"""Static-public-surface contract tests for the SignKit landing page.

These tests deliberately run the checkout script in a tiny DOM harness.  They
exercise configured, absent, and malformed Dodo product IDs without a payment
account, browser credential, or external network request.
"""

from __future__ import annotations

import fnmatch
import json
import os
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REDIRECTS_PATH = REPO_ROOT / "_redirects"
CHECKOUT_CONFIG_PATH = REPO_ROOT / "web/live/js/checkout-config.js"
CHECKOUT_PATH = REPO_ROOT / "web/live/js/checkout.js"
LEGACY_VARIANTS = ("root", "buy", "purchase", "gum", "test-variants")
REVIEW_ENTRYPOINTS = (
    "/web/live/",
    "/web/live/index.html",
    "/web/new_landing_page/",
    "/web/new_landing_page/index.html",
    "/web/cloud_workspace/",
    "/web/cloud_workspace/index.html",
)


def _redirect_manifest() -> dict[str, tuple[str, str]]:
    manifest: dict[str, tuple[str, str]] = {}
    for raw_line in REDIRECTS_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        source, destination, status = line.split()
        assert source not in manifest, f"duplicate redirect source: {source}"
        manifest[source] = (destination, status)
    return manifest


def _redirect_rules() -> list[tuple[str, str, str]]:
    rules: list[tuple[str, str, str]] = []
    for raw_line in REDIRECTS_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        source, destination, status = line.split()
        rules.append((source, destination, status))
    return rules


def _redirect_for(path: str) -> tuple[str, str] | None:
    for source, destination, status in _redirect_rules():
        if source == path or ("*" in source and fnmatch.fnmatch(path, source)):
            return destination, status
    return None


def _run_node(script: str, extra_env: dict[str, str]) -> dict[str, object]:
    node = shutil.which("node")
    assert node, "Node.js is required to execute the dependency-free checkout contract harness"
    completed = subprocess.run(
        [node, "-e", script],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, **extra_env},
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def _checkout_config() -> dict[str, object]:
    return _run_node(
        """
const fs = require('node:fs');
const vm = require('node:vm');
const window = {};
vm.runInNewContext(
  fs.readFileSync(process.env.SIGNKIT_CHECKOUT_CONFIG_PATH, 'utf8'),
  { window },
  { filename: process.env.SIGNKIT_CHECKOUT_CONFIG_PATH },
);
console.log(JSON.stringify(window.SignKitCheckoutConfig));
""",
        {"SIGNKIT_CHECKOUT_CONFIG_PATH": str(CHECKOUT_CONFIG_PATH)},
    )


def _checkout_state(config: dict[str, object]) -> dict[str, object]:
    return _run_node(
        """
const fs = require('node:fs');
const vm = require('node:vm');
const config = JSON.parse(process.env.SIGNKIT_CHECKOUT_CONFIG);

function makeClassList() {
  const values = new Set();
  return {
    add(...names) { names.forEach((name) => values.add(name)); },
    remove(...names) { names.forEach((name) => values.delete(name)); },
    contains(name) { return values.has(name); },
  };
}

function makeLink(provider, placement) {
  const attributes = {};
  const handlers = {};
  return {
    dataset: { checkoutProvider: provider, checkoutPlacement: placement },
    classList: makeClassList(),
    href: '',
    title: '',
    setAttribute(name, value) {
      attributes[name] = String(value);
      if (name === 'href') this.href = String(value);
    },
    getAttribute(name) {
      return Object.prototype.hasOwnProperty.call(attributes, name) ? attributes[name] : null;
    },
    removeAttribute(name) {
      delete attributes[name];
      if (name === 'href') this.href = '';
    },
    addEventListener(name, handler) {
      (handlers[name] ||= []).push(handler);
    },
    clickForTest() {
      let prevented = false;
      for (const handler of handlers.click || []) {
        handler({ preventDefault() { prevented = true; } });
      }
      return prevented;
    },
  };
}

const dodo = makeLink('dodo', 'test-dodo');
const gumroad = makeLink('gumroad', 'test-gumroad');
const configurationNote = { focused: 0, focus() { this.focused += 1; } };
const document = {
  readyState: 'complete',
  documentElement: { dataset: {} },
  querySelectorAll(selector) {
    if (selector === '[data-checkout-provider="dodo"]') return [dodo];
    if (selector === '[data-checkout-provider="gumroad"]') return [gumroad];
    return [];
  },
  querySelector(selector) {
    return selector === '[data-checkout-configuration-note]' ? configurationNote : null;
  },
};
const window = { SignKitCheckoutConfig: config };
vm.runInNewContext(
  fs.readFileSync(process.env.SIGNKIT_CHECKOUT_PATH, 'utf8'),
  { window, document, URL, encodeURIComponent, console },
  { filename: process.env.SIGNKIT_CHECKOUT_PATH },
);
function snapshot(link) {
  return {
    href: link.href,
    ariaDisabled: link.getAttribute('aria-disabled'),
    role: link.dataset.checkoutRole || null,
    unavailable: link.classList.contains('checkout-unavailable'),
    primary: link.classList.contains('checkout-primary'),
    fallback: link.classList.contains('checkout-fallback'),
  };
}
console.log(JSON.stringify({
  dodo: snapshot(dodo),
  gumroad: snapshot(gumroad),
  documentState: document.documentElement.dataset,
  dodoClickPrevented: dodo.clickForTest(),
  configurationNoteFocuses: configurationNote.focused,
}));
""",
        {
            "SIGNKIT_CHECKOUT_PATH": str(CHECKOUT_PATH),
            "SIGNKIT_CHECKOUT_CONFIG": json.dumps(config),
        },
    )


def test_canonical_root_and_legacy_routes_have_one_public_destination() -> None:
    manifest = _redirect_manifest()

    assert (REPO_ROOT / "index.html").is_file()
    assert "/" not in manifest, "the canonical root must remain a direct 200 response"

    for variant in LEGACY_VARIANTS:
        assert (REPO_ROOT / f"{variant}.html").is_file(), (
            f"{variant}.html is retained for historical review, even though it is no longer public"
        )
        for route in (f"/{variant}", f"/{variant}/", f"/{variant}.html"):
            assert manifest.get(route) == ("/", "301"), (
                f"{route} must permanently canonicalize to the root landing page"
            )

    for route in REVIEW_ENTRYPOINTS:
        assert _redirect_for(route) == ("/", "301"), (
            f"{route} must remain a review artifact, not a second public landing"
        )


def test_every_retained_html_artifact_is_non_public() -> None:
    """Cloudflare publishes the root, so stale HTML must be redirected too."""

    excluded_dirs = {".git", ".venv", "venv", "node_modules"}
    for path in REPO_ROOT.rglob("*.html"):
        relative_parts = path.relative_to(REPO_ROOT).parts
        if any(part in excluded_dirs for part in relative_parts):
            continue
        route = "/" + path.relative_to(REPO_ROOT).as_posix()
        if route in {"/index.html", "/404.html"}:
            continue
        assert _redirect_for(route) == ("/", "301"), (
            f"retained HTML artifact {route} needs an explicit or wildcard root redirect"
        )


def test_default_checkout_config_uses_the_single_public_config_contract() -> None:
    config = _checkout_config()

    assert config["dodoProductId"] == ""
    assert config["dodoBaseUrl"] == "https://checkout.dodopayments.com/buy/"
    assert config["gumroadUrl"] == "https://pranaysuyash.gumroad.com/l/signkit-v1"


def test_empty_or_malformed_dodo_id_makes_gumroad_the_actionable_primary() -> None:
    config = _checkout_config()

    for invalid_product_id in ("", "product-signkit", "pdt_not-valid!"):
        state = _checkout_state({**config, "dodoProductId": invalid_product_id})
        dodo = state["dodo"]
        gumroad = state["gumroad"]
        document_state = state["documentState"]

        assert dodo["href"] == ""
        assert dodo["ariaDisabled"] == "true"
        assert dodo["role"] == "unavailable"
        assert dodo["unavailable"] is True
        assert state["dodoClickPrevented"] is True
        assert state["configurationNoteFocuses"] == 1

        assert gumroad["href"] == config["gumroadUrl"]
        assert gumroad["role"] == "primary"
        assert gumroad["primary"] is True
        assert document_state["dodoCheckout"] == "missing"
        assert document_state["checkoutProvider"] == "gumroad"
        assert document_state["checkoutState"] == "gumroad-primary"


def test_configured_dodo_is_actionable_and_gumroad_stays_an_explicit_fallback() -> None:
    config = _checkout_config()
    state = _checkout_state({**config, "dodoProductId": "pdt_SignKit2026"})
    dodo = state["dodo"]
    gumroad = state["gumroad"]
    document_state = state["documentState"]

    assert dodo["href"] == "https://checkout.dodopayments.com/buy/pdt_SignKit2026"
    assert dodo["ariaDisabled"] is None
    assert dodo["role"] == "primary"
    assert dodo["primary"] is True
    assert dodo["unavailable"] is False
    assert state["dodoClickPrevented"] is False

    assert gumroad["href"] == config["gumroadUrl"]
    assert gumroad["role"] == "fallback"
    assert gumroad["fallback"] is True
    assert document_state["dodoCheckout"] == "configured"
    assert document_state["checkoutProvider"] == "dodo"
    assert document_state["checkoutState"] == "dodo-primary"
