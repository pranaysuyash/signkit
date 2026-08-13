# SignKit worktree preservation index

Date: 2026-08-13
Purpose: preserve every parallel authoring stream before reconciliation into
`main`.

## Preservation decision

The primary `main` implementation remains the canonical destination. No dirty
work was discarded, reset, force-merged, or pushed during this preservation
pass. Every intentional source, test, fixture, research, release, and
documentation path was captured in an immutable archive commit before any
promotion decision.

Documents are preserved in full. A document may later be classified as
canonical, superseded, historical, or archive-only, but that classification
must not delete the original. Any later relocation belongs under
`docs/archive/` with a dated reason and a link to the current source of truth.

## Immutable refs

| Stream | Worktree or ref | Base or captured commit | Archive ref | Disposition |
| --- | --- | --- | --- | --- |
| Common baseline | local `main` before preservation | `0d83a87` | `archive/main-baseline-0d83a87-2026-08-13` | Keep as reconciliation base |
| Primary dirty checkout | `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app` | `0d83a87` plus 258 intentional paths | `archive/main-dirty-0d83a87-2026-08-13` at `ee12dba` | Primary candidate stream, review before promotion |
| a11f dirty checkout | `/Users/pranay/.codex/worktrees/a11f/signature-extractor-app` | `0d83a87` plus 281 intentional paths | `archive/a11f-dirty-0d83a87-2026-08-13` at `b8d024c` | Parallel candidate stream, compare per file and hunk |
| eb41 clean checkout | `/Users/pranay/.codex/worktrees/eb41/signature-extractor-app` | `17f644b` | `archive/eb41-17f644b-2026-08-13` | Clean incoming candidate, already identical to `origin/main` |
| Incoming remote | `origin/main` | `17f644b` | `archive/remote-main-17f644b-2026-08-13` | Remote candidate, not yet promoted to local `main` |

The separate remote branch `origin/landing-page` remains at `dc90d3e` and was
not rewritten or deleted. It remains an independent review input.

## What was captured

The archive commits contain the intentional dirty source and documentation
streams, including:

- backend routes, services, models, migrations, hosted extraction contracts,
  and runtime profile work;
- desktop PDF runtime, signing, credential, entitlement, workflow, and UI
  work;
- tests, synthetic fixtures, corpus metadata, mutation checks, and release
  probes;
- public web surfaces, deployment scripts, claim registries, and checkout
  contracts;
- product-owner backlog, QA results, release ledger specifications, ADRs,
  research, visual reviews, expansion notes, and operator documentation;
- the deleted `512px-Mohammad_Rafiquzzaman_signature.jpg` as a recorded
  deletion in the archive commit, with the original bytes still recoverable
  from the `0d83a87` parent.

## Explicit exclusions and classification

The following generated paths were intentionally not added to the archive
commits:

- primary checkout: `.wrangler/`
- a11f checkout: `.codex-test-tmp/`
- a11f checkout: `.wrangler/`

These paths remain on disk and were not deleted. They are test or deployment
runtime outputs, not canonical product source. Before any cleanup, inspect
their contents and record whether a specific output is release evidence that
belongs under an intentional evidence path. Rebuildable output may then be
ignored or regenerated, but only after that disposition is recorded.

No `.env`, private key, credential, token, or secret-like untracked file was
found in the preservation inventory. Synthetic signature fixtures are tracked
as test assets because their metadata and tests reference them. They still
require privacy, licensing, and corpus validation before release claims.

## Reconciliation rules

1. Treat `main` as the canonical destination, not as permission to discard
   parallel work.
2. Compare `ee12dba`, `b8d024c`, and `17f644b` against the common baseline at
   `0d83a87` by coherent product group and then by full file and hunk.
3. Promote a path only after checking callers, routes, schemas, migrations,
   fixtures, tests, docs, claims, observability, and operator recovery.
4. Do not use whole-tree `ours` or `theirs` resolution, blind `git add -A`,
   reset, forced checkout, destructive cleanup, or force push.
5. Preserve duplicate or superseded documents until a dated archive decision
   identifies the canonical replacement and closure evidence.
6. Report tests with sensitivity and evidence tiers. Local focused tests do
   not close hosted migration, live deployment, rollback, or operator receipt
   gates.

## Initial disposition map

| Area | Initial disposition | Closure evidence required |
| --- | --- | --- |
| `backend/app/routers/extraction.py`, migrations, ownership services | Preserve and reconcile as P0 | target database migration, authenticated hosted smoke, retry/idempotency, deletion and audit recovery |
| `desktop_app/pdf/`, signing, credentials, entitlements | Preserve and harden | local runtime, trust/error paths, entitlement provider evidence, user-visible failure and recovery |
| `index.html`, `web/`, claim registry, deployment scripts | Preserve and reconcile as P0 | deployed root and asset probes, redirect/content-type proof, qualified local and hosted claims |
| `tools/release_artifact_ledger.py`, release docs, CI gates | Preserve and promote candidate | real artifact checksum, signing/notarization evidence, smoke output, rollback artifact and operator receipt |
| `docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md` and QA docs | Preserve as canonical task input | status synchronization against current code, tests, runtime, and deployment evidence |
| `backend/app/runtime.py`, SignVerod, autoresearch, document-registration studio | Preserve as main-only candidate | architecture review, scope decision, data provenance, benchmark sensitivity, and product-owner promotion decision |
| `.codex-test-tmp/`, `.wrangler/` | Preserve locally for classification, exclude from source archive | evidence extraction or documented rebuildability before cleanup |

## Current gate state

This index proves preservation only. It does not prove that the candidate
implementation is production-ready. The following remain open until directly
verified after reconciliation:

- target database migration and rollback/recovery;
- live authenticated hosted extraction smoke and operator receipt evidence;
- deployed public-surface parity, redirect, and content-type checks;
- entitlement provider fulfilment, revocation, refund, and offline-grace
  behavior;
- deterministic `agent-start` regeneration and fresh context artifacts;
- full test, mutation, runtime, accessibility, and browser evidence at the
  appropriate sensitivity tiers.

Next step: build the file-level disposition matrix from these immutable refs,
then promote reviewed groups into local `main` in separate, hook-verified
commits. No remote alignment occurs until that review is complete.
