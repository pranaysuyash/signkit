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

Integrated local regression after the four promotion commits: `170 passed in
9.14s` with the canonical `.venv`, isolated SQLite database, and offscreen Qt.
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
| RECON-05 | open | workspace tooling | Run `/Users/pranay/Projects/agent-start --project Data_Science/computer_vision/proj6/signature-extractor-app` under a bounded timeout, repair or explicitly report retrieval health, and attach regenerated context hashes. |
| RECON-06 | open | release and ops | Apply the Alembic head to the target database, run authenticated hosted extraction and local inspection smoke, prove replay, deletion, rollback, and operator recovery receipts. |
| RECON-07 | open | release owner | Run the hosted public-surface probe after deployment propagation and retain root, redirect, JavaScript content-type, and claim results. |
| RECON-08 | open | commercial and release | Configure a provider-neutral adapter boundary, controlled purchase, receipt activation, refund/revocation, offline-grace expiry, support recovery, and customer-safe claims. |
| RECON-09 | open | packaging | Produce real platform artifacts and complete signing, launch smoke, rollback, and machine-readable ledger evidence for every release artifact. |
| RECON-10 | open | QA and product | Run browser accessibility, narrow viewport, device, full-suite, remote CI, and external-corpus checks at their required evidence and sensitivity tiers. |

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

## Next coherent unit

Reconcile the remaining canonical docs and code families against the path-level
matrix, then run the hosted and workspace-tooling gates that can be executed
without credentials or deployment mutation. Do not push remote `main` until
the local acceptance report lists every remaining item and its closure path.
