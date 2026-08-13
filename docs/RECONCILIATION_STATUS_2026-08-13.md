# Main reconciliation status

Date: 2026-08-13
Canonical checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Remote push: not performed

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

Integrated local regression after the three implementation promotion commits:
`170 passed in 9.14s` with the canonical `.venv`, isolated SQLite database, and
offscreen Qt.
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
| RECON-05 | open | workspace tooling | The shared `/Users/pranay/Projects/agent-start` wrapper now fails closed with exit `1` when a full refresh cannot find `/Users/pranay/Projects/workspace_memory/.venv/bin/python` or a usable `memsearch` CLI; fast `--skip-index --quiet` remains explicit and non-blocking. The configured interpreter is still absent and `memsearch` is still a 17-byte `exit 0` stub. Rebuild the shared environment through the documented setup path, prove real indexing/retrieval, and attach regenerated context hashes. |
| RECON-06 | open | release and ops | Apply the Alembic head to the target database, run authenticated hosted extraction and local inspection smoke, prove replay, deletion, rollback, and operator recovery receipts. |
| RECON-07 | open | release owner | Run the hosted public-surface probe after deployment propagation and retain root, redirect, JavaScript content-type, and claim results. |
| RECON-08 | open | commercial and release | Configure a provider-neutral adapter boundary, controlled purchase, receipt activation, refund/revocation, offline-grace expiry, support recovery, and customer-safe claims. |
| RECON-09 | open | packaging | Produce real platform artifacts and complete signing, launch smoke, rollback, and machine-readable ledger evidence for every release artifact. |
| RECON-10 | open | QA and product | Run browser accessibility, narrow viewport, device, full-suite, remote CI, and external-corpus checks at their required evidence and sensitivity tiers. |
| RECON-11 | done | parallel-work integrity | The original primary `main` dirty diff is fully accounted for: 258 changed paths, 256 present at current paths, one baseline-recoverable deletion, and one archived superseded ADR. |
| RECON-12 | done | parallel-work integrity | The a11f worktree diff is fully accounted for: 281 tracked changed paths, 280 non-deleted paths present in current `main`, and runtime-only untracked directories preserved on disk. |
| RECON-17 | done-local | local product and operator workflow | The disposable local proof proves desktop source/import, extraction and cleanup, encrypted vault, controlled placement/export, forced failure, canonical retry, metadata-only recovery passports, and verified artifact receipt. The real browser bridge proof now exposes that local passport and recovery state through `/workspace-app/` without document bytes. |
| RECON-18 | done-local | local cross-surface architecture | The canonical `/workspace/local-jobs` bridge reads the desktop store through the existing `ExecutionPassport`, binds access to the authenticated user's exact canonical UUID or unique email subject, delegates retry to `WorkflowEngine`, rejects hosted profile access, and hides paths/messages. Route tests, 11/11 mutation sensitivity, and a fresh local Chrome runtime proof pass. |
| RECON-19 | done-local | local retry integrity | The canonical local retry route now uses an optional or deterministic `Idempotency-Key`, a re-entrant process/OS store lock, durable retry receipts, and passport key projection. Same-key replay and concurrent keyed requests invoke the engine once. The focused workflow/store/passport/bridge suite passes `32` tests at S1, the complete mutation manifest kills `12/12` at S3, and fresh source-to-ready plus real-Chrome bridge proofs pass at Tier 4. |
| RECON-20 | done-local | packaged desktop runtime | The macOS ARM64 PyInstaller artifact starts the in-process backend with generated local SQLite/JWT settings, serves and renders the bundled canonical `/workspace-app/`, passes the real-browser landing/workspace handoff and authenticated local bridge recovery flow, contains no `.env`, passes ad hoc code-sign verification, and leaves no port-8001 listener after bounded shutdown. The focused contract suite passes `10` tests at S1 and the complete mutation manifest passes `13/13` at S3. Evidence is in `docs/review/local_packaging_runtime_proof_2026-08-13.md`. |

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
in `docs/issue_review_agent_start_context_2026-08-13.md`; RECON-05 remains open.

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
setup recreates `/Users/pranay/Projects/workspace_memory/.venv`. RECON-05
remains open for that workspace-tooling owner action, real indexing/search
verification, and final context hashes. The current truthful fast-mode hashes
are recorded in `docs/issue_review_agent_start_context_2026-08-13.md`.

## Next coherent unit

Reconcile the remaining canonical docs and code families against the path-level
matrix, then run the hosted and workspace-tooling gates that can be executed
without credentials or deployment mutation. Do not push remote `main` until
the local acceptance report lists every remaining item and its closure path.

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
