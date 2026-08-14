# Local product operator proof: 2026-08-14

Scope: fresh local observation of the canonical document-registration-studio
landing, the metadata-first workspace, the disposable desktop source-to-ready
workflow, and the authenticated local passport bridge.

This is local Tier 4 evidence only. It is not hosted deployment, provider,
cross-platform, assistive-technology, legal-signature, or real-user evidence.

## Runtime and ownership boundary

- Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
- Branch: `main`
- Local stack: `tools/run_local_product_stack.py`
- Landing: `http://127.0.0.1:8080/`
- Companion and workspace: `http://127.0.0.1:8001/`
- Database and filesystem: isolated under `.codex-test-tmp/local-product-stack*`
- Hosted service contact: none
- Browser workspace document bytes: none

The stack was started as one owned process group, health-gated, exercised, and
stopped with Ctrl-C. The launcher cleaned up both child processes.

## Canonical local surface observation

Command:

```text
node tools/run_local_product_browser_proof.mjs
```

The reusable real Chrome proof returned `status: pass` at all required viewports:

| Viewport | Observed contract |
| --- | --- |
| 1440x900 | `SignKit | Document registration studio`, semantic main, five Source to Ready states, keyboard Source to Mark transition, pointer Mark to Clean transition, canonical workspace handoff, no overflow, reduced motion, actionable Gumroad fallback, zero browser errors |
| 390x844 | Same local handoff and state contract with no horizontal overflow or browser errors |
| 320x844 | Same narrow-viewport contract with no horizontal overflow or browser errors |

The workspace returned HTTP `200`, title `SignKit Workspace`, both auth and app
shells, a semantic main landmark, and the explicit metadata-first boundary:
local inspection is not a signing claim, does not send documents to cloud
storage, does not verify identity, and does not create a legal signing
certificate.

The persistent Browser Daemon observation independently saw the same landing
title and body copy, then the workspace boundary at the canonical local URLs.
Only expected debug analytics messages appeared. No error-level console or
page errors were observed.

## Source-to-ready execution and recovery

Command:

```text
./.venv/bin/python tools/run_local_source_to_ready_proof.py \
  --output-dir .codex-test-tmp/local-source-to-ready-proof-20260814
```

The proof returned `status: pass` and `hosted_service_contacted: false`.
Observed facts:

- A disposable signature source was extracted, cleaned, and processed as RGBA.
- The extracted bytes completed an encrypted local Vault round-trip.
- The canonical workflow placed the mark into a PDF and verified the output.
- The forced first failure emitted `ERR_SIGNING_FAILED`, entered `retry`, and
  was recovered through the canonical retry path.
- The final workflow state was `completed` after two attempts.
- The artifact receipt was `verified` with ID
  `sha256:0d3d13811121d716bcfae3c49f0240c06b265a82e59ce6f7d4cd3b0bbde96f2d`.
- Receipt semantics were explicitly visual signature placement, not a
  cryptographic signature.
- The passport boundary remained `metadata_only_no_document_bytes`.

## Authenticated local browser bridge

Command, run against the isolated stack data root:

```text
SIGNKIT_DATA_DIR="$PWD/.codex-test-tmp/local-product-stack-data" \
SIGNKIT_PYTHON="$PWD/.venv/bin/python" \
SIGNKIT_WORKSPACE_BASE_URL="http://127.0.0.1:8001" \
node tools/run_local_workspace_bridge_browser_proof.mjs
```

The proof returned `status: pass` with:

- unauthenticated direct-job status: `401`;
- missing-job status for an authenticated user: `404`;
- exact owner-bound local job visible in the workspace;
- opaque receipt metadata visible before retry;
- retry response status: `failed`, with the bounded recovery state visible;
- no private source path in API or browser output;
- `document_bytes_in_browser_workspace: false`;
- zero browser errors.

## Evidence and remaining gates

Evidence tier is Tier 4 because the local processes and real Chrome browser
were observed end to end. Test sensitivity for this fresh run is S1. The
existing focused contract and mutation evidence remains the stronger
regression guard for the underlying code paths.

This proof advances the local evidence for `L1-08`, `RECON-17`, and `RECON-18`.
It does not close packaged or cross-platform stale-state behavior, manual
assistive-technology review, provider activation, hosted migration, hosted
deployment, legal-signature claims, or real-user comprehension research.
