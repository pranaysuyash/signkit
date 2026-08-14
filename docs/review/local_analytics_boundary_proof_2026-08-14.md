# Local analytics boundary proof

Date: 2026-08-14

## Decision

Optional landing analytics is fail-silent when no `gtag` provider is
configured. A missing provider must not emit console messages that resemble
remote events, and it must not be presented as outbound telemetry. When a real
`gtag` function is configured, the existing user-event forwarding remains
available.

## Evidence

- Source contract: `web/live/js/analytics.js` calls `gtag` only when
  `typeof gtag === "function"`; otherwise the call returns without logging or
  forwarding.
- Delivery contract: the canonical root and retained live landing reference
  the analytics asset with an explicit contract-version query so a changed
  optional boundary is not hidden by a persistent browser cache.
- Focused regression: `./.venv/bin/python -m pytest
  tests/test_landing_analytics_contract.py -q` passed `3` tests.
- The missing-provider test runs bot detection with no `gtag` and asserts zero
  calls and zero console records.
- The configured-provider test supplies a collector as `gtag`, invokes the
  registered click handler, and asserts that `real_user_detected` and the
  expected `set` call are forwarded without a synthetic `REMOTE_EVENT` log.
- The Browser Daemon loaded the cache-versioned canonical root after the
  change and reported zero console entries; the reusable local browser proof
  also passed at desktop, touch, and narrow viewports with zero browser errors.
- The complete canonical suite passed `538 passed, 4 skipped`; the skips remain
  the documented optional PyMuPDF and Qt event-loop boundaries.
- A preceding real local Browser Daemon observation recorded the original
  debug messages from the absent-provider path. The messages were confirmed to
  originate in the current source, which is why this change exists. The
  historical observation remains preserved in
  `docs/review/local_operator_browser_observation_2026-08-14.md` and QA-61.

## Boundary

This is local JavaScript contract evidence only. It does not prove analytics
provider activation, consent compliance, hosted deployment parity, event
delivery, identity behavior, or production observability. Those remain
separate release and legal/product-owner gates.
