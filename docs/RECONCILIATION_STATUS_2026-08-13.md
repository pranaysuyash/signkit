# Main reconciliation status

Date: 2026-08-13
Canonical checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Remote push: verified after the latest canonical `main` handoff; local `HEAD`
and `origin/main` were equal at the handoff commit.

This is the live status record for bringing the preserved parallel work into
local `main`. It complements the immutable preservation index and the Product
Owner backlog. It does not treat an archive document or a passing static test
as production proof.

## Completed promotion groups

| Group | Commit | Scope | Evidence | Remaining boundary |
| --- | --- | --- | --- | --- |
| Runtime and operator recovery | `b631e35` | Explicit `local_companion` versus `hosted` profile, private health proof, typed document-inspection receipts, hosted route exclusion, desktop remote-upload guard | 36 focused tests, S1; full motto commit gate | Hosted migration, live authenticated smoke, rollback, and operator receipt evidence remain open |
| Release and entitlement evidence | `6d0e54e` | Shared environment contract, deployment/public-surface gates, release artifact ledger, provider-neutral entitlement receipt, synthetic fixtures, QA matrix, claim inventory, release ADRs | 64 focused tests, S1; entitlement mutation failed then passed, S2; 5/5 mutation manifest, S3; local deployment smoke, Tier 3 | Provider adapter and purchase/revocation evidence, signed artifacts, cross-platform launch, hosted deployment, target migration and remote CI remain open |
| Research and operator workflow | `5798235` | Extractor confidence threshold, web receipt hydration and failure visibility, isolated document-registration concept, browser proof, SignverOD inspection/evaluation, autoresearch protocol | 39 focused tests, S1; 7/7 mutation manifest, S3; Python compilation | Browser proof requires the external Playwright runtime and keep-running backend; external corpus and product promotion remain gated |

The current canonical first-party local regression is `488 passed, 4 skipped`
from `492` collected with the canonical `.venv`, isolated SQLite database, and
offscreen Qt. Earlier smaller counts below are preserved as historical
promotion evidence.
This is S1 evidence for the current checkout. It does not close hosted,
provider, signing, rollback, browser-device, remote CI, or agent-start gates.

## Documentation preservation

- The primary and a11f documentation trees are preserved in full under
  `docs/archive/parallel/`.
- `docs/archive/WORKTREE_PRESERVATION_INDEX_2026-08-13.md` records refs,
  exclusions, and reconciliation rules.
- The current canonical release, QA, entitlement, claim, and topology docs
  remain at their normal paths. Archive snapshots are historical evidence and
  must not silently override current product truth.
- Product and research strategy documents promoted as current inputs are
  `docs/SIGNKIT_PRODUCT_ML_DISCUSSION_2026-08-13.md`,
  `docs/SIGNKIT_S_TIER_PRODUCT_EXPANSION_MAP.md`, and
  `docs/review/product_visual_direction_strategy_2026-08-13.md`.

## Open tracked tasks

| ID | Status | Owner | Closure criteria |
| --- | --- | --- | --- |
| RECON-01 | done | release engineering | All preserved refs are recorded and both dirty documentation trees are recoverable inside `docs/archive/parallel/`. |
| RECON-02 | done | backend and desktop | Runtime profile, local inspection receipts, health proof, and remote-upload policy are in one canonical path with focused tests. |
| RECON-03 | done | release engineering | Release ledger, deployment probes, claim checks, QA matrix, and entitlement receipt contract are in local `main`. |
| RECON-04 | done | research and product | Research tooling, web operator receipt recovery, isolated concept surface, and evidence-bound experiment protocol are in local `main`. |
| RECON-05 | done | documentation continuity | The dated truth map, canonical source precedence, stale-status classification, and backlog/task-reference repair are now in `docs/DOCUMENTATION_TRUTH_MAP_2026-08-13.md`; remaining claim/deployment work is tracked separately. |
| RECON-06 | open | workspace tooling and agent-start | Fast-mode source selection and project-motto retention are repaired and proven twice, but the shared workspace Python interpreter and usable `memsearch` CLI remain absent. Rebuild the shared environment through the documented setup path, run a real sync/index/search refresh, confirm retrieval results or truthful unavailable status, and attach generated context hashes. |
| RECON-07 | open | hosted migration and recovery | Apply the Alembic head to the target database, run authenticated hosted extraction and local inspection smoke, prove replay, deletion, rollback, and operator recovery receipts. |
| RECON-08 | open | public claims and deployment | Run the hosted public-surface probe after deployment propagation and retain root, redirect, JavaScript content-type, and claim results. |
| RECON-09 | open | commercial and release | Configure a provider-neutral adapter boundary, controlled purchase, receipt activation, refund/revocation, offline-grace expiry, support recovery, and customer-safe claims. |
| RECON-10 | open | packaging and QA | Produce real platform artifacts and complete signing, launch smoke, rollback, machine-readable ledger, browser accessibility, narrow viewport, device, remote CI, and external-corpus evidence at their required tiers. |
| RECON-11 | done | parallel-work integrity | The original primary `main` dirty diff is fully accounted for: 258 changed paths, 256 present at current paths, one baseline-recoverable deletion, and one archived superseded ADR. |
| RECON-12 | done | parallel-work integrity | The a11f worktree diff is fully accounted for: 281 tracked changed paths, 280 non-deleted paths present in current `main`, and runtime-only untracked directories preserved on disk. |
| RECON-17 | done-local | local product and operator workflow | The disposable local proof proves desktop source/import, extraction and cleanup, encrypted vault, controlled placement/export, forced failure, canonical retry, metadata-only recovery passports, and verified artifact receipt. The real browser bridge proof now exposes that local passport and recovery state through `/workspace-app/` without document bytes. |
| RECON-18 | done-local | local cross-surface architecture | The canonical `/workspace/local-jobs` bridge reads the desktop store through the existing `ExecutionPassport`, binds access to the authenticated user's exact canonical UUID or unique email subject, delegates retry to `WorkflowEngine`, rejects hosted profile access, and hides paths/messages. Route tests, 11/11 mutation sensitivity, and a fresh local Chrome runtime proof pass. |
| RECON-19 | done-local | local retry integrity | The canonical local retry route now uses an optional or deterministic `Idempotency-Key`, a re-entrant process/OS store lock, durable retry receipts, and passport key projection. Same-key replay and concurrent keyed requests invoke the engine once. The focused workflow/store/passport/bridge suite passes `32` tests at S1, the complete mutation manifest kills `12/12` at S3, and fresh source-to-ready plus real-Chrome bridge proofs pass at Tier 4. |
| RECON-20 | done-local | packaged desktop runtime | The macOS ARM64 PyInstaller artifact starts the in-process backend with generated local SQLite/JWT settings, serves and renders the bundled canonical `/workspace-app/`, passes the real-browser landing/workspace handoff and authenticated local bridge recovery flow, contains no `.env`, passes ad hoc code-sign verification, and leaves no port-8001 listener after bounded shutdown. The focused contract suite passes `10` tests at S1 and the complete mutation manifest passes `13/13` at S3. Evidence is in `docs/review/local_packaging_runtime_proof_2026-08-13.md`. |
| RECON-26 | done-local | workspace tooling and doctrine safety | The shared wrapper now selects and retains the project-local `motto_v5.md`, safely restores the Projects-root alias, and keeps workspace Doctrine 6.0 separate. Two bounded refreshes returned `0` with unchanged motto SHA and truthful generated provenance; the static guard and QA-42 record the proof. | Keep the source-selection/retention guard and rerun two bounded refreshes after shared-wrapper changes. Real workspace-memory indexing/search remains open under RECON-06. |
| RECON-27 | done-local | local operator recovery | The workflow engine and console now recover old transient jobs explicitly into `NEEDS_REVIEW` with a durable interruption event, no automatic retry, bounded copy, and invalid-timestamp fail-safe. Focused engine, operator-content, and Qt smoke tests pass `36` checks. | Keep the explicit recovery action and age threshold. Reopen for packaged/cross-platform interruption, filesystem recovery, assistive-technology, hosted, or provider evidence. |
| RECON-28 | open | auto-detection confidence governance | The preserved calibration slice is integrated locally with detector adapters, manifest/PDF page validation, one-to-one matching, pure-numpy metrics/calibrators, split-boundary warnings, a CLI, dataset-schema documentation, and `7` focused checks plus a synthetic self-test. | Prove held-out permissioned evaluation, document calibration and threshold falsifiers, complete privacy/consent governance, decide the product accuracy bar, and decide whether to promote any calibrated threshold into the detector contract. Do not claim production or real-data calibration from the synthetic self-test. |
| RECON-29 | done-local | local operator deletion recovery | Library deletion now records the sidecar basename in a metadata-only receipt and exposes an explicit `Repair Cleanup` action for incomplete receipts. Recovery is bounded to regular files inside the library, updates receipts atomically, preserves unresolved directories and unsafe/malformed targets, and reports remaining work. QA-44 passed `37` focused checks with `3` pre-existing event-loop skips. | Keep explicit operator invocation and the local path boundary. Reopen for real permission/device behavior, restart recovery, packaged/cross-platform, assistive-technology, hosted, or provider evidence. |

## Explicit non-claims

- Local deployment smoke is not hosted deployment proof.
- A provider-neutral receipt contract is not evidence of a configured provider,
  purchase, refund webhook, or production activation.
- Synthetic fixtures and SignverOD research are not customer or production
  benchmark evidence.
- The isolated document-registration studio is a truth-bound concept surface,
  not a production signing route.
- `agent-start` context artifacts are not considered healthy until the live
  bounded refresh and retrieval behavior are rechecked.
- The 2026-08-13 live hosted probe still serves the older landing and checkout
  surface. It is not evidence that the reconciled local `main` has been
  deployed.

## Addendum (2026-08-13): live gate results

The workspace tooling refresh was rerun with a 90-second bound. It returned
shell exit code `0` while reporting the missing workspace-memory interpreter and
failed retrieval sections. The exact evidence and interpretation are recorded
in `docs/issue_review_agent_start_context_2026-08-13.md`; RECON-06 remains open.

The hosted checks were also rerun read-only against `https://signkit.work`:

- `tools/test_deployed_surface.py --base-url https://signkit.work --json` failed
  because `/` lacked the current canonical public-surface marker, legacy paths
  such as `/buy`, `/gum`, `/new`, `/purchase`, `/root`, and `/test-variants`
  returned `200` or `308` instead of the required `301`, and retired
  `/web/live/js/checkout.js` and `/web/live/js/checkout-config.js` returned
  HTML instead of JavaScript.
- `scripts/test-deployment.sh https://signkit.work` passed the root `200` check
  but failed the `/index.html` redirect check because the host returned `308`
  instead of `301`.

These are Tier 3 command-execution results against the deployed surface, but
they do not prove a code defect in the unreleased local checkout. RECON-08
remains open until the reconciled public surface is deployed and the same
probes pass.

## Addendum (2026-08-13): agent-start false-success guard

The shared `/Users/pranay/Projects/agent-start` entry point was hardened after
the live refresh audit found that full retrieval could return shell exit `0`
with an absent workspace interpreter and a no-op `memsearch` stub. Full refresh
now returns exit `1` before claiming retrieval health; explicit
`AGENT_START_SKIP_INDEX_RETRIEVE=1` also returns `1` when used with
`--skip-index --quiet`, while ordinary `--skip-index --quiet` still returns `0`
and marks retrieval as skipped. This is S2 command-execution evidence.

The shared runtime is not rebuilt in this product pass because the documented
setup recreates `/Users/pranay/Projects/workspace_memory/.venv`. RECON-06
remains open for that workspace-tooling owner action, real indexing/search
verification, and final context hashes. The current truthful fast-mode hashes
are recorded in `docs/issue_review_agent_start_context_2026-08-13.md`.

## Next coherent unit

Run the local claim-surface and operator-state checks for `L0-13`, `L1-07`, and
`L1-08`, then keep hosted, provider, and workspace-tooling gates explicitly
separate until their required external evidence exists.

## Addendum (2026-08-13): exact implementation path accounting

The three implementation commits are a direct descendant of the incoming
baseline `17f644b`:

```text
17f644b -> b631e35 -> 6d0e54e -> 5798235
```

Their per-commit file-change counts are `13 + 57 + 24 = 94` entries. That
number is not 94 unique paths because two paths were changed in more than one
commit:

- `desktop_app/app_bootstrap.py`, changed by `b631e35` and `6d0e54e`
- `tools/mutation_check.py`, changed by `6d0e54e` and `5798235`

The authoritative path-level comparison is:

```text
git diff 17f644b..5798235
92 files changed, 3312 insertions(+), 67 deletions(-)
```

All 92 unique paths in that diff exist in the current `main` tree. Therefore,
the accurate statement is: 94 per-commit file-change entries, 92 unique
implementation and evidence paths, all present after the incoming `17f644b`
baseline. The later documentation preservation commit `27ababa` contains the
1,314-file full documentation snapshot, followed by evidence-only commits
`29bc4a0` and `ab530e9`.

The separate original-primary inventory is recorded in
`docs/archive/PRIMARY_MAIN_258_PATH_ACCOUNTING_2026-08-13.md`. It proves that
the 258-path primary dirty diff was not reduced to the focused 92-path series:
198 primary contents were already present in incoming `17f644b`, 218 current
paths remain byte-identical to the primary snapshot, and the remaining paths
have explicit incoming, reconciled, deletion, or archival dispositions.

The separate a11f worktree inventory is recorded in
`docs/archive/A11F_WORKTREE_281_PATH_ACCOUNTING_2026-08-13.md`. Its 281-path
tracked diff has no missing non-deleted path in current `main`; its only
untracked directories are `.codex-test-tmp/` and `.wrangler/`, which remain
excluded runtime artifacts. The eb41 worktree is a clean incoming reference at
`17f644b`.

## Addendum (2026-08-13): local product direction promotion

The immediate product objective is now explicitly local and first-principles,
with deployment parity deferred. `RECON-13` is closed by promoting the selected
document-registration-studio direction into `/index.html`, adding the owned
`web/canonical_landing/` interaction surface, and linking local operators to
the existing backend-mounted `/workspace-app/` surface. No duplicate browser
workspace, API route, or signing pipeline was introduced.

Local evidence is recorded in
`docs/review/local_product_surface_runtime_proof_2026-08-13.md`: 180 full-suite
tests passed S1, 11/11 sensitivity mutants were killed S3, and Browser
Daemon runtime checks covered 1440px, 390px, and 320px root behavior plus the
390px workspace surface at Tier 4. The reusable local browser proof now closes
`RECON-14` / `QA-16` with actual reduced-motion emulation at all three required
viewports. `RECON-16` is also closed: `tools/run_local_product_stack.py` now
starts the existing backend and `serve.py` together, health-gates both,
defaults to isolated SQLite and filesystem data roots, and cleans up both child
processes without changing the canonical backend or workspace route. Hosted
deployment and provider gates are intentionally unchanged. The desktop
source-to-ready proof and local desktop-passport-to-browser bridge are now
closed at the local evidence tier under `RECON-17` and `RECON-18`; hosted
deployment, packaging, provider, and external-research gates remain separate.

## Addendum (2026-08-13): local packaged runtime

The local packaging gate advanced without changing the hosted or provider
boundary. `desktop_app/backend_manager.py` now applies the explicit local
database/JWT/runtime/health contract before the in-process backend import.
All desktop PyInstaller specs omit the developer `backend/.env` and include
the canonical `web/cloud_workspace/` assets.

The ARM64 standard bundle was rebuilt with the canonical `venv` and exercised
in a real offscreen frozen process. It reached `/health` with HTTP 200, served
`/workspace-app/` with HTTP 200, created only isolated local state, passed
`codesign --verify --deep --strict`, and stopped under a 15-second bound with
no remaining port-8001 listener. This is Tier 4 local artifact evidence and
S2-style regression evidence because the prior artifact failed at missing
`JWT_SECRET` before the environment fix.

`RECON-20` and `QA-20` are closed locally. `RECON-09`, `L0-05`, and the broad
release gate remain open for Intel/Windows/Linux artifacts, distribution
signing/notarization, clean installation, rollback, and a release ledger tied
to a real release source and recoverable prior artifact.

## Addendum (2026-08-13): canonical first-party test collection

The current local checkout now uses one default test collection across
`tests/`, `backend/tests/`, and `desktop_app/tests/`. The previous root command
collected only 181 tests while the omitted suites contained 291 tests. The
first explicit omitted-suite run exposed three missing-optional-PyMuPDF
failures and repeated destructor logging errors at interpreter shutdown.

ADR-0149 records the decision and alternatives. The canonical root run now
collects 487 tests and passes `484 passed, 4 skipped` at S1 after the signed
entitlement slice. The PyMuPDF
native-form capability remains an explicit optional skip, and three Qt cases
remain event-loop-dependent. A deliberate reversion of the destructor fix
failed its regression test and the restored fix passed, providing S2 evidence.

## Addendum (2026-08-13): instruction-surface preservation

The shared agent-start generator now preserves a project-local `motto_v5.md`
when present instead of deleting it in favor of the workspace-wide Doctrine
6.0. Fresh fast-mode regeneration succeeded and recorded the local doctrine
path, version, SHA-256, and explicit workspace separation in the context pack.

## Addendum (2026-08-13): PDF field-detection contract

The preserved local PDF detector slice was reviewed and integrated as `RECON-25`
and `QA-37`. It consolidates the image-pixel to PDF-point transform and
candidate dedupe policy, adds a generated labeled AcroForm regression with a
confidence floor and IoU threshold, and adds a documentation drift gate for the
image and PDF detector modules. Fifteen focused checks passed. This closes only
the local code/regression/documentation contract; human or production PDF
accuracy, confidence calibration, unattended placement, packaged/cross-platform,
hosted, and assistive-technology evidence remain separate.
