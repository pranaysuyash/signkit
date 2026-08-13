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
| RECON-05 | open | workspace tooling | Bounded rerun exits `0` but emits a missing `/Users/pranay/Projects/workspace_memory/.venv/bin/python` diagnostic and writes `_Search failed for this collection/query._` into every retrieval section. Repair or explicitly report retrieval health, fix false-success behavior, and attach regenerated context hashes. |
| RECON-06 | open | release and ops | Apply the Alembic head to the target database, run authenticated hosted extraction and local inspection smoke, prove replay, deletion, rollback, and operator recovery receipts. |
| RECON-07 | open | release owner | Run the hosted public-surface probe after deployment propagation and retain root, redirect, JavaScript content-type, and claim results. |
| RECON-08 | open | commercial and release | Configure a provider-neutral adapter boundary, controlled purchase, receipt activation, refund/revocation, offline-grace expiry, support recovery, and customer-safe claims. |
| RECON-09 | open | packaging | Produce real platform artifacts and complete signing, launch smoke, rollback, and machine-readable ledger evidence for every release artifact. |
| RECON-10 | open | QA and product | Run browser accessibility, narrow viewport, device, full-suite, remote CI, and external-corpus checks at their required evidence and sensitivity tiers. |
| RECON-11 | done | parallel-work integrity | The original primary `main` dirty diff is fully accounted for: 258 changed paths, 256 present at current paths, one baseline-recoverable deletion, and one archived superseded ADR. |
| RECON-12 | done | parallel-work integrity | The a11f worktree diff is fully accounted for: 281 tracked changed paths, 280 non-deleted paths present in current `main`, and runtime-only untracked directories preserved on disk. |

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
