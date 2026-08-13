# Local canonical accessibility audit

Date: 2026-08-13
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Scope: canonical root landing and backend-mounted `/workspace-app/` local surface
Evidence tier: Tier 4 local real-Chrome browser proof plus Tier 2 static contracts

## Changes made

- Added a visible-on-focus skip link and one stable `main#main-content` landmark
  to the workspace shell. The same landmark now covers both the unauthenticated
  login view and the authenticated workspace view, so the skip target remains
  valid across the view transition.
- Added an explicit `for`/`id` association for the dynamically rendered local
  PDF inspection file control.
- Extended the reusable local browser proof to check the workspace landmark,
  skip-link destination, label, focusability, and visible focus treatment.

## Evidence

Focused static contracts:

```text
./.venv/bin/python -m pytest \
  tests/test_cloud_workspace_visual_contract.py \
  tests/test_canonical_landing_visual_contract.py \
  tests/test_document_registration_studio_contract.py -q
13 passed
```

Real local Chrome proof:

```text
./.venv/bin/python tools/run_local_product_stack.py
node tools/run_local_product_browser_proof.mjs
```

The proof passed at 1440x900, 390x844, and 320x844 for the landing surface,
and at 390x844 for the workspace surface. It observed the workspace `main`
landmark, `#main-content` skip target, visible focused skip link, metadata-only
boundary copy, no horizontal overflow, and zero browser errors. The landing
proof continued to pass its existing reduced-motion, keyboard state transition,
pointer state transition, checkout fallback, and workspace-handoff assertions.

## Boundary and remaining work

This closes the local semantic and browser-observable accessibility sub-gate
for the canonical surfaces. It does not claim WCAG conformance or substitute
for:

- VoiceOver or another screen-reader pass;
- manual zoom/reflow and high-contrast checks on supported devices;
- keyboard testing of authenticated transitions and the native dialog with
  real user input beyond the reusable proof's current scope;
- packaged Intel/Windows/Linux accessibility observation; or
- hosted deployment accessibility evidence.

Those remain explicit release-quality follow-ups under `L1-08` and the hosted
deployment gates.
