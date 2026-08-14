# Local operator browser observation

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Evidence scope: fresh local landing and workspace runtime observation

## Setup

The isolated local stack was started with:

```bash
./.venv/bin/python tools/run_local_product_stack.py \
  --data-dir .codex-test-tmp/browser-operator-proof
```

The reusable browser proof passed with:

```bash
SIGNKIT_LANDING_BASE_URL=http://127.0.0.1:8080 \
SIGNKIT_WORKSPACE_BASE_URL=http://127.0.0.1:8001 \
node tools/run_local_product_browser_proof.mjs
```

A persistent Chrome Browser Daemon observation additionally navigated to both
local surfaces and inspected their rendered DOM at a 1440x900 viewport.

## Observed result

The landing passed:

- title `SignKit | Document registration studio`;
- `h1` `Move the document from source to ready.`;
- the five-state rail `01 Source`, `02 Mark`, `03 Clean`, `04 Place`, `05 Ready`;
- canonical CTA handoff to `/workspace-app/`;
- semantic `main#main-content` and visible skip-link focus behavior;
- no horizontal overflow at 1440x900, 390x844, or 320x844;
- reduced-motion behavior;
- keyboard Source to Mark and pointer Mark to Clean state transitions; and
- zero browser errors.

The workspace passed HTTP `200`, title `SignKit Workspace`, the main landmark,
authentication and application shells, no overflow, and the explicit boundary:
local workflow control and metadata-only local inspection, not a signing claim.
The page states that it does not send documents to cloud storage, verify
identity, or create a legal signing certificate.

The browser console contained two existing debug telemetry messages caused by
absent `gtag`; no `error` console entries or page errors were observed. The
stack was stopped with Ctrl-C and follow-up requests confirmed ports 8080 and
8001 were closed.

## Evidence boundary

This is fresh Tier 4 local browser evidence for `L1-08`. It is not packaged or
cross-platform stale-state proof, a screen-reader or assistive-technology
audit, hosted deployment evidence, provider evidence, legal-signature proof,
or real-user comprehension research.
