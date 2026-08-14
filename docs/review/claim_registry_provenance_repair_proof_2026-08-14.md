# Claim registry provenance repair proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Evidence scope: canonical-root claim source-control synchronization

## Result

The full-suite run after the entitlement slice exposed that the claim registry
still pointed at the pre-analytics `index.html` commit. The registry was
updated to the actual current source commit, `0fa3cbf1830a954610164f86c7dc9bf9249c453c`,
for its snapshot and registered claim rows.

## Evidence

- The red-first full run recorded `1 failed, 540 passed, 4 skipped` because
  `tests/test_launch_claim_registry.py::test_registry_records_existing_source_commit_for_every_claim`
  detected the stale snapshot.
- After the registry repair, the canonical full suite passed `541 passed, 4
  skipped`.
- The focused registry contract remains responsible for checking that the
  snapshot matches `git log -1 --format=%H -- index.html` and that every row
  provenance value names an existing commit.

## Boundary

This repairs local source provenance only. It does not prove hosted page
parity, deployed redirects, provider activation, legal approval, or production
claim review.
