"""Keep optional landing analytics silent when no provider is configured."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
ANALYTICS = ROOT / "web" / "live" / "js" / "analytics.js"
LANDING = ROOT / "index.html"


HARNESS = r"""
const fs = require('node:fs');
const vm = require('node:vm');

const calls = [];
const logs = [];
const listeners = {};
const hasGtag = process.env.SIGNKIT_ANALYTICS_HAS_GTAG === '1';
const document = {
  addEventListener(name, handler) {
    (listeners[name] ||= []).push(handler);
  },
  querySelectorAll() { return []; },
  documentElement: { scrollHeight: 1000 },
  hasFocus() { return false; },
};
const window = {
  addEventListener() {},
};
const navigator = {
  userAgent: 'Mozilla/5.0',
  webdriver: !hasGtag,
  plugins: [1],
};
const console = {
  debug(...args) { logs.push({ type: 'debug', args }); },
  info(...args) { logs.push({ type: 'info', args }); },
};
const context = {
  document,
  navigator,
  window,
  console,
  setTimeout() {},
};
if (hasGtag) {
  context.gtag = (...args) => calls.push(args);
}
vm.runInNewContext(
  fs.readFileSync(process.env.SIGNKIT_ANALYTICS_PATH, 'utf8'),
  context,
  { filename: process.env.SIGNKIT_ANALYTICS_PATH },
);
if (hasGtag) {
  const click = (listeners.click || [])[0];
  if (click) click();
}
process.stdout.write(JSON.stringify({ calls, logs }));
"""


def _run(*, has_gtag: bool) -> dict[str, object]:
    completed = subprocess.run(
        ["node", "-e", HARNESS],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "SIGNKIT_ANALYTICS_PATH": str(ANALYTICS),
            "SIGNKIT_ANALYTICS_HAS_GTAG": "1" if has_gtag else "0",
        },
    )
    return json.loads(completed.stdout)


def test_missing_gtag_is_silent_even_when_bot_detection_runs() -> None:
    result = _run(has_gtag=False)

    assert result["calls"] == []
    assert result["logs"] == []


def test_landing_uses_explicit_asset_version_for_provider_boundary_changes() -> None:
    page = LANDING.read_text(encoding="utf-8")

    assert 'src="web/live/js/analytics.js?v=2026-08-14-analytics-silent"' in page


def test_configured_gtag_still_receives_real_user_events() -> None:
    result = _run(has_gtag=True)

    event_names = [call[1] for call in result["calls"] if call[0] == "event"]
    assert "real_user_detected" in event_names
    assert [call[0] for call in result["calls"]].count("set") == 1
    assert not any(
        entry["type"] == "debug" and "REMOTE_EVENT" in str(entry["args"])
        for entry in result["logs"]
    )
