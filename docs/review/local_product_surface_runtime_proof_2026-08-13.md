# Local product surface runtime proof: 2026-08-13

Scope: canonical root promotion to the document registration studio and its
handoff to the existing local metadata workspace.

This is local product evidence only. It is not hosted deployment evidence,
payment evidence, browser-native signing evidence, or user comprehension
research.

The browser proof is also a bounded accessibility contract. It checks the
semantic main landmark, focused skip-link visibility and target, labeled state
rail, canonical primary workspace CTA, keyboard focus/state behavior, reduced
motion, narrow-viewport overflow, and browser errors. It is not a
screen-reader or full assistive-technology certification.

## Runtime setup

- Landing preview: `QT_QPA_PLATFORM=offscreen .venv/bin/python serve.py` at
  `http://127.0.0.1:8080/`.
- Workspace proof backend: `.venv/bin/python tools/run_contractdesk_web_proof.py
  --port 8001 --keep-running`.
- Unified local stack: `./.venv/bin/python
  tools/run_local_product_stack.py`, which starts both local services with an
  isolated SQLite default and cleans them up together.
- Browser: Browser Daemon with the project Playwright skill.

## Observed root behavior

| View | Observation | Evidence |
| --- | --- | --- |
| 1440x900 | Page title is `SignKit | Document registration studio`; root main is present; no horizontal overflow; ArrowRight on the focused Source tab changes the visible state to `MARK EXTRACTED` and focuses Mark. | Tier 4 runtime/manual |
| 390x844 | Root remains within the viewport; the local workspace links resolve to `http://127.0.0.1:8001/workspace-app/`; checkout fallback is actionable through the configured Gumroad URL while Dodo is unavailable. | Tier 4 runtime/manual |
| 320x844 | Root remains within the viewport; main landmark and workspace handoff remain present. | Tier 4 runtime/manual |
| Console | No page errors or error-level console entries were observed. Analytics emitted expected debug records because the local preview does not load the remote analytics function. | Tier 4 runtime/manual |

## Observed workspace behavior

- `http://127.0.0.1:8001/workspace-app/` returned `200` and the title
  `SignKit Workspace`.
- The workspace boundary states that it is metadata-first, supports local
  inspection, and is not a signing claim.
- At 390x844 there was no horizontal overflow, and the auth/workspace controls
  remained present.
- The proof runner returned `pass` for health, workspace mount, fixture, and
  `app.js`/`styles.css` assets.

## Static and sensitivity checks

- `.venv/bin/pytest -q`: `180 passed` with the local data root isolated under
  `.codex-test-tmp/full-suite-data-receipt`, S1.
- Focused local product, passport, bridge, stack, browser-proof, canonical
  landing, and claim tests: `37 passed`, S1, including a fresh-process data-root override
  check and exact UUID/email subject binding.
- `node --check web/canonical_landing/app.js`: passed, S1.
- `node --check web/live/js/checkout.js`: passed, S1.
- `.venv/bin/python tools/audit_public_surface.py --strict`: passed, Tier 1
  static release-gate evidence. Warnings are retained historical-page claims,
  not root blocking errors.
- `TMPDIR=/var/tmp .venv/bin/python tools/mutation_check.py`: `11/11 mutants
  killed`, S3. In addition to the existing extraction, workspace, passport,
  runtime-profile, and inspection invariants, the manifest covers forced retry
  recovery, durable retry-attempt accounting, exact bridge owner binding, and
  complete passport projection.

## Closure evidence

The reusable `node tools/run_local_product_browser_proof.mjs` command now runs
a real headless Chrome context with `reducedMotion: "reduce"` and passed at
1440x900, 390x844, and 320x844. It verifies the media query is active, root
scroll behavior is reduced, transition duration is reduced, keyboard and
pointer state changes bind, checkout fallback is actionable, the workspace
handoff is canonical, and no page or console errors occur. `RECON-14` / `QA-16`
is therefore closed for the local surface at Tier 4.

The public hosted root remains outside this local pass. Deployment parity,
provider activation, signed packaging, and user comprehension remain separate
release gates. `RECON-16` is closed by the one-command local stack launcher
described below. `RECON-17` and `RECON-18` are now closed at the local evidence
tier by the disposable source-to-ready proof and the authenticated browser
bridge proof described below.

## Unified startup evidence

- `./.venv/bin/python tools/run_local_product_stack.py --once` passed: the
  backend became healthy at `http://127.0.0.1:8001/health`, the canonical root
  became reachable at `http://127.0.0.1:8080/`, the isolated SQLite URL was
  printed, and both child processes were terminated on completion.
- A long-running invocation was then started, the full browser proof passed
  against both surfaces, and Ctrl-C terminated both children. This is Tier 4
  local operational evidence.
- The launcher was also run with ambient `DATABASE_URL` and `SIGNKIT_DATA_DIR`
  values pointing elsewhere. It still selected the isolated database and
  logged uploads under `.codex-test-tmp/local-product-stack-data/uploads/`.
  This is Tier 4 evidence that local preview startup does not silently write
  to the normal SignKit application-support data root.

## Source-to-ready desktop execution evidence

`./.venv/bin/python tools/run_local_source_to_ready_proof.py
--output-dir .codex-test-tmp/source-to-ready-proof-review-live` passed with the
following Tier 4 local evidence:

- A disposable source image was created, loaded through `SignatureExtractor`,
  auto-detected, cleaned, and processed into an RGBA extracted mark.
- The extracted bytes made an encrypted `NotaryVault` round trip.
- The canonical `WorkflowEngine` placed the mark into the canonical PDF
  fixture through the existing signer and produced a non-empty verified output.
- A forced first signing failure produced `retry` with `ERR_SIGNING_FAILED` and
  attempt `1`; `retry_job` then completed the same durable job at attempt `1`.
- The local `ExecutionPassport` exposed `retry_local_job` for the failed state
  and `metadata_only_no_document_bytes` for both states. The final artifact
  receipt reported `verification_status: verified` and visual-placement, not
  cryptographic-signature, semantics.
- The manifest explicitly records `hosted_service_contacted: false` and
  `document_bytes_in_browser_workspace: false`. The shared passport and
  browser boundary contracts enforce the latter, and the local bridge now
  projects the desktop passport through `/workspace/local-jobs` without paths,
  event messages, or document bytes.

The retry accounting defect found during this proof was fixed in
`desktop_app/workflows/engine.py`: transitions into `retry`, `failed`, and
`cancelled` now consume a durable attempt. The focused workflow and passport
suite passed `19 tests`, and the retry-accounting mutation was killed at S3.

## Local desktop passport bridge evidence

The bridge uses the existing `/workspace` route family and does not add a
second workflow store or signing pipeline:

- `GET /workspace/local-jobs` lists only jobs whose existing
  `ExecutionGrant.approver_subject` exactly matches the authenticated user's
  canonical UUID or unique account email. No wildcard or substring matching is
  used.
- `GET /workspace/local-jobs/{job_id}` returns the canonical local
  `ExecutionPassport`; foreign and missing jobs both return `404`.
- `POST /workspace/local-jobs/{job_id}/retry` delegates to `WorkflowEngine`;
  the browser never mutates the JSON store directly.
- Hosted runtime profile returns `404` for the local bridge.
- The projection omits `input_path_ref`, private event messages, vault data,
  document bytes, and extracted images.

Route tests passed `20` focused bridge/workspace/runtime cases. The full
mutation manifest now contains `11` mutants and killed `11/11`
at S3, including owner binding and complete passport projection. A fresh
real-Chrome run of `tools/run_local_workspace_bridge_browser_proof.mjs` passed
with `unauthenticated_status: 401`, `missing_status: 404`, one exact
owner-bound job, `retry_status: failed`, visible `inspect_local_job` recovery,
the actual source-proof artifact reference
`local-receipt:sha256:3dbb4132b1e95927c2edc4409719533b0a057b1b96f24a2ece153a3ca13eb2ff`,
no private path in the API or UI, `document_bytes_in_browser_workspace: false`,
and zero browser errors. This is Tier 3 cross-surface HTTP plus Tier 4 observed
browser evidence for the local topology only.

## Three-pass review record

1. Immediate correctness: root route, five-state interaction, checkout
   fallback, local workspace handoff, responsive widths, and full regression
   suite were checked. Result: no confirmed local product regression.
2. Architecture: the root now owns orientation, `web/canonical_landing/` owns
   its interaction, `checkout.js` remains the only checkout owner, and
   `web/cloud_workspace/` plus the existing `/workspace` API remain the only
   workspace path. Result: no duplicate route or parallel pipeline introduced.
3. Rule compliance: claim markers, qualified local boundaries, evidence tiers,
   and S1/S3 sensitivity reporting were checked. Result: the actual reduced-
   motion browser context passed; no hosted or user-research completion claim
   is made.

## Addendum (2026-08-13): local retry integrity hardening

The local bridge retry contract was strengthened after the initial browser
proof identified a remaining concurrent-request risk. The route now accepts an
optional `Idempotency-Key`, derives a deterministic key when the header is
absent, serializes the canonical JSON store with a process and OS file lock,
and persists an internal retry receipt containing the returned job snapshot.
The existing passport exposes only the opaque key as metadata.

Evidence from the current main working tree:

- `backend/tests/test_local_workflow_bridge.py`: `5 passed`, S1, including
  same-key replay, store reload, and two concurrent keyed requests converging
  on one engine call;
- focused workflow, store, passport, and bridge suite: `32 passed`, S1;
- `tools/mutation_check.py` now contains 12 mutants, including the retry replay
  invariant; the full run killed `12/12`, S3;
- no route family or second workflow pipeline was introduced.

Fresh local execution and browser-bridge evidence for this addendum:

- `tools/run_local_source_to_ready_proof.py` returned `status: pass` at Tier 4,
  with artifact receipt `sha256:7872316227d38d452962120ed99d93dc5b9850d1721c7627bdbb093d4201c6c5`,
  two attempts after a forced signing failure, and no hosted service contact;
- `tools/run_local_workspace_bridge_browser_proof.mjs` returned `status: pass`
  in real headless Chrome at Tier 4, with `401` unauthenticated rejection,
  `404` missing-job rejection, visible local source and opaque receipt metadata,
  retry recovery, zero browser errors, and
  `document_bytes_in_browser_workspace: false`.

The strengthened local product browser proof also passed in real Chrome at
1440x900, 390x844, and 320x844 after adding explicit skip-link, state-label,
primary-CTA, focus-visibility, and browser-error assertions. This closes the
reusable local QA-12 contract at Tier 4, while screen-reader, device-browser,
and manual assistive-technology evidence remain separate.

This is local JSON-store evidence. It does not establish cross-machine
coordination, hosted retry semantics, provider retry semantics, or retention
and compaction policy for very high-volume local automation.
