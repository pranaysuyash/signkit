"""Regression tests for the deployed public-surface release probe."""

from __future__ import annotations

from tools.test_deployed_surface import validate_asset_response, validate_root_response


def test_javascript_probe_rejects_html_fallback() -> None:
    result = {
        "status": 200,
        "content_type": "text/html; charset=utf-8",
        "body": "<!doctype html><html><body>old landing page</body></html>",
    }

    errors = validate_asset_response(
        "/web/live/js/checkout.js",
        result,
        expected_content_type="application/javascript",
        required_marker="checkout_intent",
    )

    assert any("content-type" in error for error in errors)
    assert any("canonical instrumented runtime" in error for error in errors)


def test_canonical_root_probe_rejects_retired_absolute_claims() -> None:
    result = {
        "status": 200,
        "content_type": "text/html; charset=utf-8",
        "body": "100% offline. Your files never leave your computer.",
    }

    errors = validate_root_response(result)

    assert any("public-surface marker" in error for error in errors)
    assert any("retired high-risk claim" in error for error in errors)
