# Product Owner Backlog Audit — 2026-08-12

Persona: Product Owner — backlog ownership and sequencing
Scope: Desktop app, backend API, web landing/control-plane surface, launch docs, and decision/debt threads.

Baseline evidence checked this pass:
- `Docs/APP_OPEN_ITEMS.md`
- `Docs/LAUNCH_TOP_10_STATUS.md`
- `Docs/TODO.md`
- `Docs/TODO_FULL.md`
- `docs/analysis/2026-08-03_super_app_feature_matrix.md`
- `desktop_app/views/main_window_parts/extraction.py`
- `desktop_app/views/main_window.py`
- `desktop_app/license/*`
- `backend/app/main.py`
- `backend/app/paths.py`
- `backend/app/routers/extraction.py`
- `backend/app/routers/workspace.py`
- `docs/wayfinder/tickets/*.md`
- `scripts/test-deployment.sh`

## PO ownership stance

- Backlog order is value-first and evidence-bound.
- A task is explicit when it appears in app docs or open tickets.
- A task is implicit when it is required to preserve product integrity but is missing from trackers.
- A task is `ready` when prerequisites are satisfied.
- A task is `in-progress` when we started execution or updated execution notes this pass.
- A task is `blocked` when an external decision or missing external dependency is required.
- Confidence on this pass: `0.91` (Tier 3 local hosted-contract evidence and Tier 2 migration evidence; production rollout and live-host proof remain open).

## Executive readout

- Strengths: local extraction/PDF core, vault, workflow UI, launch docs, and workspace control-plane are implemented and mostly coherent.
- Primary risk area: **entitlement and release evidence** (local proof > local-only gating > cloud-hosted/checkout contracts).
- Next highest-value sequence for launch readiness: harden entitlement model, close extraction boundary in API, close landing/route deployment evidence.

## Active PO register

| ID | Type | Workstream | Task | Status | Priority | Acceptance | Evidence source | Owner |
|---|---|---|---|---|---|---|---|---|
| L0-01 | explicit | launch | Maintain this live PO backlog as canonical task surface and track every explicit/implicit update | done | P0 | This file contains explicit+implicit tasks with dependency links and last-update log | this file | PO |
| L0-02 | explicit | licensing | Decide and implement the entitlement contract (hard vs soft gate model), including activation receipt/idempotency/revocation policy | in-progress | P0 | One canonical entitlement path used by app + checkout + support claims; no local-only fallback ambiguity | `desktop_app/license/*`, `desktop_app/views/main_window.py`, `desktop_app/views/main_window_parts/extraction.py` | PO + eng |
| L0-03 | explicit | backend | Resolve `/extraction` + `/uploads/images` boundary for any hosted claim (authentication, owner scope, retention, deletion, idempotency) | in-progress | P0 | Application contract is authenticated and owner/workspace scoped with private artifacts, export/deletion/audit receipts, and durable idempotency; production migration/rollout and live-host proof remain required | `backend/app/routers/extraction.py`, `backend/app/models/image.py`, `backend/app/models/extraction_audit.py`, `backend/alembic/versions/e42b7f8c91aa_add_extraction_asset_ownership_receipts.py`, `docs/decisions/ADR-0142-authenticated-extraction-asset-contract.md` | eng |
| L0-04 | explicit | release | Complete deployment smoke contract for root and `/index.html`, including redirect and content-type checks | in-progress | P0 | Clean pass of `bash scripts/test-deployment.sh https://signkit.work` with required redirects/content types | `scripts/test-deployment.sh`, `web/live/js/checkout.js` | eng |
| L0-05 | explicit | release | Publish evidence-backed artifact ledger (release SHA, package filename, checksum, signing/notarization, smoke output) | in-progress | P0 | One ledger file per release artifact with reproducible checks | CI + release scripts | PO + eng |
| L0-06 | explicit | architecture | Reconcile stale docs as canonical vs historical (`FINAL_STATUS_AND_TODO`, legacy landing notes) | in-progress | P1 | Public-facing docs now link to current canonical tracker and call out date/range of truth | `Docs/APP_OPEN_ITEMS.md`, `Docs/TODO.md`, `Docs/TODO_FULL.md` | PO |
| L0-07 | explicit | config | Standardize port policy between docs, backend config, and dev scripts | in-progress | P1 | `scripts/run-backend-dev.sh` uses configurable `BACKEND_PORT` (default 8001), and tracked app docs now align around 8001 in active paths | `scripts/run-backend-dev.sh`, `docs/TODO_FULL.md`, `docs/TODO.md`, `Docs/APP_OPEN_ITEMS.md` | PO + eng |
| L0-08 | implicit | architecture | Restore canonical motto propagation so `agent-start` can regenerate context without a symlink guard failure, and promote doctrine additions to the Downloads source | done | P0 | `/Users/pranay/Downloads/motto_v5.md` contains the doctrine additions; `/Users/pranay/Projects/motto_v5.md` is a symlink to that source; project context regeneration exits successfully and records the canonical source | `/Users/pranay/Downloads/motto_v5.md`, `/Users/pranay/Projects/motto_v5.md`, `/Users/pranay/Projects/agent-start`, `docs/context/agent-start/*` | PO + eng |
| L1-01 | explicit | licensing | Implement consistent evaluation mode behavior across export/copy/save path and status copy in UI copywriting | done | P1 | Export/copy/library now use one gate helper, action controls are disabled in trial, and lock messaging is unified | `desktop_app/views/main_window_parts/extraction.py` | eng |
| L1-02 | explicit | docs | Publish legal/commercial footer entries in Help/About (refund/privacy/terms/notice access) and remove missing claims | done | P1 | Every Help/About surface includes legal policy links and refund path references | `docs/HELP.md`, `docs/SHORTCUTS.md`, `desktop_app/views/main_window.py`, `desktop_app/views/main_window_parts/status.py` | PO |
| L1-03 | explicit | docs | Unify config references to port 8001 and generate `.env.example` with exact required variables | in-progress | P2 | Config loads from `.env.example` defaults and all tracked docs use same values | `.env.example`, `desktop_app/config.py`, `backend/app/config.py` | eng |
| L1-04 | explicit | support | Add Help-driven issue reporting flow with local diagnostics snapshot + prefilled email template | done | P1 | Help menu action opens diagnostics folder and opens pre-filled email payload with version, environment, and session context | `desktop_app/views/main_window.py`, `docs/HELP.md`, `Docs/APP_OPEN_ITEMS.md` | PO |
| L1-05 | explicit | docs | Add in-app update-check action wired to `updates.json` compare flow | done | P1 | Help menu opens update check and status message with `UPDATES_URL` comparison logic and user prompt to download update | `desktop_app/views/main_window.py`, `Docs/APP_OPEN_ITEMS.md`, `Docs/TODO.md` | eng |
| L2-01 | explicit | wayfinder | Close `reconcile-historical-docs-and-public-claims.md` as executable remediation, not a passive ticket | in-progress | P0 | Ticket updated from “open” to “resolved” or replaced by concrete migration ticket with criteria | `docs/wayfinder/tickets/reconcile-historical-docs-and-public-claims.md` | PO |
| L2-02 | explicit | wayfinder | Resolve `define-template-system-and-governance.md` with owner/versioned addendum | blocked | P2 | Decision memo includes versioning, ownership, publish controls, rollback path | `docs/wayfinder/tickets/define-template-system-and-governance.md` | PO |
| L2-03 | explicit | wayfinder | Resolve `choose-commercial-packaging-and-activation-model.md` | blocked | P0 | Chosen topology+pricing+activation model and operational impact documented with legal/commercial sign-off | `docs/wayfinder/tickets/choose-commercial-packaging-and-activation-model.md` | PO |
| L2-04 | implicit | quality | Add contract-level tests for extraction route abuse and partial-failure recovery | done | P1 | Tier 3 coverage includes unauthenticated/cross-owner/cross-workspace denial, duplicate replay/conflict, concurrent convergence, export, deletion replay, audit-after-delete, malformed/oversized inputs, and private artifact responses | `backend/tests/test_extraction_router.py`, `backend/tests/test_extraction_hosted.py`, `desktop_app/tests/test_api_client.py` | eng |
| L0-09 | implicit | release/backend | Apply the extraction ownership migration and prove hosted rollout/recovery against the real deployment topology | in-progress | P0 | Local production-like smoke now passes with `e42b7f8c91aa`; target database application, live authenticated smoke, rollback/recovery, and operator receipt evidence remain required | `tools/run_extraction_hosted_smoke.py`, `backend/alembic/versions/e42b7f8c91aa_add_extraction_asset_ownership_receipts.py`, `scripts/test-deployment.sh`, `docs/decisions/ADR-0142-authenticated-extraction-asset-contract.md` | eng + ops |
| L0-10 | implicit | developer experience | Make the backend test runtime preflight detect missing API dependencies instead of reporting only desktop test-data readiness | done | P1 | `tools/validate_test_data_environment.py --backend` passes in the repaired canonical project environment and detects stale launchers/missing modules before backend evidence is collected | `tools/validate_test_data_environment.py`, `tools/README.md`, `docs/test_data_environment.md` | eng |
| L1-06 | implicit | workspace | Close the local document-inspection contract: preserve requested topology, reject cloud inspection, avoid document retention, and make retries replay-safe | done | P1 | Authenticated local inspection returns isolated/non-retained receipt data; same key replays; changed bytes conflict; cloud topology returns 409; full workspace/backend regression passes | `backend/app/schemas/workspace.py`, `backend/app/services/document_inspection.py`, `backend/app/routers/workspace.py`, `backend/tests/test_workspace_router.py`, `docs/decisions/ADR-0143-local-document-inspection-contract.md` | eng |
| L0-11 | implicit | developer experience | Diagnose the non-returning `agent-start --project ... --skip-index --quiet` refresh path and restore deterministic context regeneration | in-progress | P1 | Command completes within an established local timeout, generated context files are refreshed, and the cause/evidence is documented without bypassing canonical motto guards | `/Users/pranay/Projects/agent-start`, `docs/context/agent-start/*`, `/Users/pranay/Projects/motto_v5.md` | eng |
| L2-08 | implicit | backend | Add regression check so extraction responses never return public `uploads/images` URLs | done | P1 | Upload/select responses keep `file_path` null/internal and contract tests guard against accidental reintroduction | `backend/app/routers/extraction.py`, `backend/tests/test_extraction_router.py`, `desktop_app/tests/test_api_client.py` | eng |
| L2-05 | implicit | QA | Create QA matrix with reproducible commands/results and attach to runbook | in-progress | P1 | Matrix includes negative-path cases and known-limit table | `docs/QA_*` (new) | PO + QA |
| L2-06 | explicit | web claims | Add `docs/launch_claims/registry.md` and claim smoke check for every public copy statement that implies hosted/cloud behavior | in-progress | P2 | Every hosted claim has a gate test and a source commit hash | `web/live`, `tests/test_landing_surface_contract.py` | PO |
| L2-07 | explicit | UX | Add explicit delete/escape/shortcut discoverability and close alignment with docs | done | P1 | `Docs/SHORTCUTS.md` and actual bindings match | `desktop_app/views/main_window_parts/extraction.py` | eng |

## Implicit but must be explicit now

- `backend/app/main.py` previously exposed `/uploads/images` publicly through `StaticFiles`; this contract risk is mitigated by removing the mount and returning private `file_path` values from extraction responses. The hosted extraction contract now enforces authenticated owner/workspace scope, export/deletion/audit receipts, and database-backed idempotent replay. Production migration and rollout evidence remain open under `L0-09`.
- `on_copy` and `on_save_to_library` are now hard-gated. Public legal/policy linkage and trial messaging have been updated in this cycle (menu, about, status bar).
- Several docs remain at “pending” while code moved ahead. This is a high-risk claims gap, even when technical code is done.

## Current pass work queue (this PO cycle)

1. [done] Add a small addendum section to `Docs/LAUNCH_TOP_10_STATUS.md` linking every status row to this backlog and evidence path.
2. [done] Add canonical PO references to `Docs/TODO.md` and `Docs/APP_OPEN_ITEMS.md` for status-sync discipline.
3. [done] Remove unauthenticated `/uploads/images` route mount and update `/extraction` response contract to avoid public URLs.
4. [done] Bound local extraction upload reads, atomically write private artifacts, and add retention cleanup with focused regression coverage.
5. [done] Close authenticated owner/workspace scope, hosted export/deletion/audit receipts, durable idempotency, and Tier 3 recovery coverage.
3. [in progress] Add a task status legend to `.env` docs and `.env.example` to remove historical drift.
4. [in progress] Run a focused extraction-route safety smoke locally once `.venv` tooling is available (`uvicorn`, `pytest` profile in backend tests).
5. [pending] Close wayfinder blockers with explicit dependency conditions before commercial web expansion decisions.
6. [pending] Draft release artifact ledger template and assign one owner.
7. [done] Added Help/About legal and refund visibility (menu, about text, status bar CTA) and docs alignment for keyboard shortcuts.
8. [done] Added issue reporting action and diagnostics snapshot generation in Help menu; updated `Docs/APP_OPEN_ITEMS.md` + `docs/HELP.md` status surfaces.

## Status transitions this pass

- `L0-01`: Done on this cycle as baseline; this file updated with expanded explicit/implicit sections.
- `L0-07`: Started; local execution script and task trackers now enforce a single port contract across active app docs and backend start path.
- `L0-06`: Started; stale-doc reconciliation tasks now explicitly visible and assigned. Status-sync discipline now mirrored in `Docs/TODO.md` and `Docs/APP_OPEN_ITEMS.md`.
- `L1-01`: Closed via shared export gate helper; export/copy/save now follow one entitlement path and status messaging.
- `L1-02`: Closed by adding legal links in Help/About, refund path entry, and trial-mode CTA updates.
- `L1-05`: Closed by aligning in-app manual update flow status and Help menu evidence with backlog/task trackers.
- `L1-04`: Closed by implementing Help → Report Issue / Send Diagnostics with local log snapshot capture and prefilled support email.
- `L0-08`: Closed this pass. The 44-line doctrine addition is present in the Downloads canonical source; the Projects-root motto is now a symlink to it; `agent-start --project Data_Science/computer_vision/proj6/signature-extractor-app --skip-index --quiet` regenerated the project context successfully.
- `L0-03`: Application closure this pass: authenticated owner/workspace scope, private asset lifecycle, export/deletion/audit receipts, and durable database-backed idempotency are implemented and covered by hosted integration tests. Deployment migration and live-host evidence remain under `L0-09`.
- `L0-04`: Elevated to in-progress; production smoke evidence still reports route inconsistency in previous report.
- `L2-04`: Closed with Tier 3 evidence: `.venv/bin/pytest -q backend/tests/test_extraction_router.py backend/tests/test_extraction_hosted.py` passed `10 passed`; desktop API assertions cover generated idempotency headers. The focused suite was first red on three response classification defects, then passed after fixing those defects (S2).

- `L2-08`: Closed by adding backend regression coverage in `backend/tests/test_extraction_router.py` and client contract assertions in `desktop_app/tests/test_api_client.py`.

## Add-task protocol (live)

When a missing integrity gap appears:
1. Add one row with `implicit` type.
2. Set owner and dependency chain to the nearest explicit blocker.
3. Add one evidence source.
4. Update this status log.

Suggested new task format:
- ID: `X-YY-<short>`
- Example: `S2-09`
- Columns to always fill: `Type`, `Workstream`, `Task`, `Status`, `Priority`, `Acceptance`, `Evidence`, `Owner`

## Confidence and next evidence checkpoints

- Confidence in this audit: `0.91`
- Hard blockers before launch: `L0-02`, `L0-03`, `L0-04`
- Next checkpoint: apply `e42b7f8c91aa` in the target deployment, run the authenticated hosted smoke, and attach the receipt/recovery output to `L0-09`

## Addendum (2026-08-12): P0 extraction closure

- The four annotated P0 gaps are closed in the canonical application path: JWT-authenticated asset access, optional workspace execution ownership checks, private export/delete/audit receipts, and durable replay keyed by owner + operation + request key.
- The new audit table is append-only for operation receipts. Asset deletion is a soft-delete state transition with physical artifact cleanup; audit remains available to the owner after deletion.
- Evidence: focused router/hosted suite `10 passed` (Tier 3), desktop client idempotency assertions (Tier 2), and isolated SQLite Alembic upgrade through `e42b7f8c91aa` (Tier 2).
- Remaining release gate: target-database migration, production configuration review, live hosted smoke, and operator recovery evidence. Do not describe hosted extraction as production-ready until `L0-09` closes.

## Addendum (2026-08-12): runtime preflight gap

- The active checkout currently has `venv/bin/python` but its environment is missing FastAPI, so the full backend suite cannot collect. The prior focused suite passed in the then-available project environment; this new failure is environment evidence, not a product regression.
- `tools/validate_test_data_environment.py --backend` now checks FastAPI, SQLAlchemy, multipart parsing, and JWT modules in addition to desktop test-data dependencies. The current environment correctly reports the missing backend module.
- Recovery command: install the pinned project dependencies into the selected `venv` or restore the canonical `.venv`, then rerun the backend preflight and `backend/tests`. Do not use system Python as evidence.
- The full backend/client run now passes `39 passed` when invoked through `venv/bin/python -m pytest`; the standalone `venv/bin/pytest` launcher is stale and intentionally remains a failed preflight until repaired.
- The broader backend run also exposed and closed a receipt-ordering defect: SQLite server timestamps were second-resolution, so receipts could be returned out of operation order. Application timestamps now preserve ordering for the audit contract.
- `tools/run_extraction_hosted_smoke.py` is now the canonical local release proof for the authenticated extraction flow. Its current run is blocked by the active `venv` missing Alembic; install the pinned backend runtime or restore the prior complete project environment before using it as release evidence.
- `L1-06` is closed with Tier 2 evidence: the workspace router contract test and full backend/client run pass `42 passed`; the implementation uses the existing workspace event table and does not create a parallel document-retention store.
- `L0-11` remains open: the context refresh was attempted on 2026-08-13, produced no output within the interactive wait window, and was interrupted. No conclusion about the root cause is asserted; reproduce with bounded diagnostics before changing agent-start.
- `L0-09`: Local closure advanced this pass. `tools/run_extraction_hosted_smoke.py` passed against a temporary SQLite database after applying every migration through `e42b7f8c91aa`; live target deployment remains open.
- `L0-10`: Closed this pass. Repaired pip with `ensurepip`, installed declared `alembic==1.16.4`, regenerated the pytest launcher for Python 3.13, and confirmed the backend preflight passes.

## Addendum (2026-08-13): local-main reconciliation checkpoint

This addendum supersedes stale completion language only where it names the
current checkout and current evidence. Historical entries above remain intact
as dated records.

### Reconciliation tasks

| ID | Type | Workstream | Status | Priority | Current evidence | Closure criteria |
| --- | --- | --- | --- | --- | --- | --- |
| RECON-01 | implicit | parallel-work integrity | done | P0 | Preservation refs and both dirty documentation trees are recorded in `docs/archive/WORKTREE_PRESERVATION_INDEX_2026-08-13.md` and `docs/archive/parallel/`. | Keep archive refs and snapshots recoverable until the user approves cleanup. |
| RECON-02 | implicit | runtime topology | done | P0 | `b631e35`; 36 focused tests passed S1; local versus hosted route and upload boundaries are explicit. | Hosted migration, live smoke, rollback, and operator receipt evidence remain separate gates. |
| RECON-03 | explicit | release evidence | done | P0 | `6d0e54e`; 64 focused tests passed S1, entitlement mutation S2, 5/5 mutation S3, local public-surface smoke Tier 3. | Complete provider, signing, cross-platform launch, remote CI, and hosted deployment proof. |
| RECON-04 | implicit | research and operator workflow | done | P1 | `5798235`; 39 focused tests passed S1 and 7/7 mutation S3. | Complete browser runtime proof and decide which research candidates, if any, are promoted. |
| RECON-05 | implicit | documentation continuity | done | P1 | Current reconciliation status is in `docs/RECONCILIATION_STATUS_2026-08-13.md`; primary and a11f full docs are archived. | Keep canonical docs synchronized as remaining gates close. |
| RECON-06 | implicit | agent-start | open | P1 | Existing issue review documents the missing workspace-memory interpreter and truthful retrieval-refresh gap. | Run bounded full refresh, repair or explicitly report retrieval health, and attach generated context hashes. |
| RECON-07 | implicit | hosted migration and recovery | open | P0 | Local contract and temporary SQLite smoke exist; no target database or live authenticated recovery receipt is claimed. | Apply target migrations, run authenticated upload/process/export/delete/replay, prove rollback and operator recovery. |
| RECON-08 | explicit | public claims and deployment | open | P0 | Local root, redirect, asset content-type, and retired-claim probes pass Tier 3; the hosted probe remains a release gate. | Run `scripts/test-deployment.sh https://signkit.work` and `tools/test_deployed_surface.py --base-url https://signkit.work --json` after deployment propagation. |
| RECON-09 | explicit | provider and packaging | open | P0 | Provider-neutral receipt and release ledger contracts fail closed without real provider or artifact evidence. | Controlled purchase/revocation, support recovery, signed artifacts, launch smoke, rollback artifact, and ready ledger evidence. |
| RECON-10 | implicit | full validation | open | P1 | Focused suites and mutation gates pass; browser accessibility, device, remote CI, full-suite, and external-corpus evidence remain scoped. | Run each QA row at its required evidence tier and record S2/S3 where release blocking. |

The live reconciliation record is maintained in
`docs/RECONCILIATION_STATUS_2026-08-13.md`. No remote push has occurred.

Integrated local regression checkpoint: the current `main` checkout passed
`170 passed in 9.14s` with the canonical `.venv`, isolated SQLite database,
and offscreen Qt. This is S1 evidence only. Hosted migration and recovery,
public deployment, provider activation, signed packaging, browser/device
coverage, remote CI, and agent-start retrieval health remain open tasks.

## Addendum (2026-08-13): live reconciliation gate results

- `RECON-06` / agent-start remains open. A bounded full refresh returned shell
  exit code `0` while reporting the missing
  `/Users/pranay/Projects/workspace_memory/.venv/bin/python` interpreter. The
  regenerated context contained `_Search failed for this collection/query._`
  in every retrieval section. See
  `docs/issue_review_agent_start_context_2026-08-13.md` for reproduction and
  closure criteria.
- `RECON-08` / hosted public surface remains open. The read-only probes against
  `https://signkit.work` found the older root surface, legacy routes returning
  `200` or `308` rather than `301`, and retired `/web/live` JavaScript paths
  returning HTML. Local `main` was not changed to mask a deployment mismatch.
- The local reconciled checkout remains the source of truth for the six local
  commits and their evidence. No remote push was performed.

## Addendum (2026-08-13): corrected path accounting

The implementation reconciliation descends directly from incoming baseline
`17f644b` through `b631e35`, `6d0e54e`, and `5798235`. The visible commit file
counts are `13`, `57`, and `24`, which sum to 94 per-commit file-change
entries. The unique path count is 92 because `desktop_app/app_bootstrap.py`
and `tools/mutation_check.py` were each changed in two of those commits.

The authoritative `git diff 17f644b..5798235` reports 92 files changed, with
all 92 paths present in current `main`. The 1,314-file documentation snapshot
is separately committed in `27ababa`; `29bc4a0` and `ab530e9` contain later
evidence updates. The earlier shorthand “94 file paths” is corrected here to
“94 per-commit entries, 92 unique paths.”

## Addendum (2026-08-13): original primary-main inventory

The original dirty primary `main` snapshot is separately accounted for in
`docs/archive/PRIMARY_MAIN_258_PATH_ACCOUNTING_2026-08-13.md`. Its diff from
`0d83a87` to `ee12dba` contains 258 changed paths. This is broader than the
focused 92-path implementation promotion series because 198 primary contents
were already present in incoming `17f644b` before those promotions.

Current disposition is explicit: 218 paths remain byte-identical to the
primary snapshot, 38 paths have reconciled content, the deleted signature image
is recoverable from the baseline, and the historical ADR is preserved under
the full primary archive snapshot. `RECON-11` is closed for accounting;
production and hosted gates remain governed by RECON-06 through RECON-10.
