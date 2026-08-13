# SignKit Issue Review: Full-Suite Failures

Date: 2026-08-12
Discovered during: Test Data Engineering external corpus intake and extractor benchmark
Scope: outside the touched test-data/extractor change set

## Findings

- **P2 landing checkout contract**: One test in
  `tests/test_landing_surface_contract.py` fails because malformed Dodo product
  IDs produce `#checkout-configuration-note` instead of the contractually
  expected empty `href`. The checkout-state contract and its focused tests need
  alignment before this is considered closed.

## Evidence

The first full command `./.venv/bin/pytest -q` completed with `110 passed, 5 failed`,
including four transient or order-dependent auth mapping failures. A second
full run completed with `121 passed, 1 failed`; the auth failures did not
reproduce, while the landing contract failure did.
The focused test set for this task completed with `24 passed`, and the failures
did not involve the importer, corpus validator, extractor candidate helper, or
signature edge-case tests.

## Disposition

The landing finding was repaired in `web/live/js/checkout.js` and its contract
test was updated to assert the intended empty-href behavior. The browser
workspace now has one main landmark and an explicit current/planned topology
disclosure. The desktop extraction indentation defect was also repaired. The
full repository suite now passes `126 passed`; this review is closed.
