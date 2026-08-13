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
| L0-06 | explicit | architecture | Reconcile stale docs as canonical vs historical (`FINAL_STATUS_AND_TODO`, legacy landing notes) | done | P1 | Current docs link to the dated truth map and canonical tracker; historical status reports, retained landing variants, and parallel snapshots are explicitly classified and cannot override current evidence | `docs/DOCUMENTATION_TRUTH_MAP_2026-08-13.md`, `docs/DOCUMENTATION_STATUS.md`, `docs/README.md` | PO |
| L0-07 | explicit | config | Standardize port policy between docs, backend config, and dev scripts | in-progress | P1 | `scripts/run-backend-dev.sh` uses configurable `BACKEND_PORT` (default 8001), and tracked app docs now align around 8001 in active paths | `scripts/run-backend-dev.sh`, `docs/TODO_FULL.md`, `docs/TODO.md`, `Docs/APP_OPEN_ITEMS.md` | PO + eng |
| L0-08 | implicit | architecture | Restore canonical motto propagation so `agent-start` can regenerate context without a symlink guard failure, and promote doctrine additions to the Downloads source | done | P0 | `/Users/pranay/Downloads/motto_v5.md` contains the doctrine additions; `/Users/pranay/Projects/motto_v5.md` is a symlink to that source; project context regeneration exits successfully and records the canonical source | `/Users/pranay/Downloads/motto_v5.md`, `/Users/pranay/Projects/motto_v5.md`, `/Users/pranay/Projects/agent-start`, `docs/context/agent-start/*` | PO + eng |
| L1-01 | explicit | licensing | Implement consistent evaluation mode behavior across export/copy/save path and status copy in UI copywriting | done | P1 | Export/copy/library now use one gate helper, action controls are disabled in trial, and lock messaging is unified | `desktop_app/views/main_window_parts/extraction.py` | eng |
| L1-02 | explicit | docs | Publish legal/commercial footer entries in Help/About (refund/privacy/terms/notice access) and remove missing claims | done | P1 | Every Help/About surface includes legal policy links and refund path references | `docs/HELP.md`, `docs/SHORTCUTS.md`, `desktop_app/views/main_window.py`, `desktop_app/views/main_window_parts/status.py` | PO |
| L1-03 | explicit | docs | Unify config references to port 8001 and generate `.env.example` with exact required variables | in-progress | P2 | Config loads from `.env.example` defaults and all tracked docs use same values | `.env.example`, `desktop_app/config.py`, `backend/app/config.py` | eng |
| L1-04 | explicit | support | Add Help-driven issue reporting flow with local diagnostics snapshot + prefilled email template | done | P1 | Help menu action opens diagnostics folder and opens pre-filled email payload with version, environment, and session context | `desktop_app/views/main_window.py`, `docs/HELP.md`, `Docs/APP_OPEN_ITEMS.md` | PO |
| L1-05 | explicit | docs | Add in-app update-check action wired to `updates.json` compare flow | done | P1 | Help menu opens update check and status message with `UPDATES_URL` comparison logic and user prompt to download update | `desktop_app/views/main_window.py`, `Docs/APP_OPEN_ITEMS.md`, `Docs/TODO.md` | eng |
| L2-01 | explicit | wayfinder | Close `reconcile-historical-docs-and-public-claims.md` as executable remediation, not a passive ticket | done | P0 | Ticket is resolved with a dated truth map, canonical source precedence, and explicit remaining claim/deployment tasks | `docs/wayfinder/tickets/reconcile-historical-docs-and-public-claims.md`, `docs/DOCUMENTATION_TRUTH_MAP_2026-08-13.md` | PO |
| L2-02 | explicit | wayfinder | Resolve `define-template-system-and-governance.md` with owner/versioned addendum | blocked | P2 | Decision memo includes versioning, ownership, publish controls, rollback path | `docs/wayfinder/tickets/define-template-system-and-governance.md` | PO |
| L2-03 | explicit | wayfinder | Resolve `choose-commercial-packaging-and-activation-model.md` | blocked | P0 | Chosen topology+pricing+activation model and operational impact documented with legal/commercial sign-off | `docs/wayfinder/tickets/choose-commercial-packaging-and-activation-model.md` | PO |
| L2-04 | implicit | quality | Add contract-level tests for extraction route abuse and partial-failure recovery | done | P1 | Tier 3 coverage includes unauthenticated/cross-owner/cross-workspace denial, duplicate replay/conflict, concurrent convergence, export, deletion replay, audit-after-delete, malformed/oversized inputs, and private artifact responses | `backend/tests/test_extraction_router.py`, `backend/tests/test_extraction_hosted.py`, `desktop_app/tests/test_api_client.py` | eng |
| L0-09 | implicit | release/backend | Apply the extraction ownership migration and prove hosted rollout/recovery against the real deployment topology | in-progress | P0 | Local production-like smoke now passes with `e42b7f8c91aa`; target database application, live authenticated smoke, rollback/recovery, and operator receipt evidence remain required | `tools/run_extraction_hosted_smoke.py`, `backend/alembic/versions/e42b7f8c91aa_add_extraction_asset_ownership_receipts.py`, `scripts/test-deployment.sh`, `docs/decisions/ADR-0142-authenticated-extraction-asset-contract.md` | eng + ops |
| L0-10 | implicit | developer experience | Make the backend test runtime preflight detect missing API dependencies instead of reporting only desktop test-data readiness | done | P1 | `tools/validate_test_data_environment.py --backend` passes in the repaired canonical project environment and detects stale launchers/missing modules before backend evidence is collected | `tools/validate_test_data_environment.py`, `tools/README.md`, `docs/test_data_environment.md` | eng |
| L1-06 | implicit | workspace | Close the local document-inspection contract: preserve requested topology, reject cloud inspection, avoid document retention, and make retries replay-safe | done | P1 | Authenticated local inspection returns isolated/non-retained receipt data; same key replays; changed bytes conflict; cloud topology returns 409; full workspace/backend regression passes | `backend/app/schemas/workspace.py`, `backend/app/services/document_inspection.py`, `backend/app/routers/workspace.py`, `backend/tests/test_workspace_router.py`, `docs/decisions/ADR-0143-local-document-inspection-contract.md` | eng |
| L0-11 | implicit | developer experience | Diagnose the non-returning `agent-start --project ... --skip-index --quiet` refresh path and restore deterministic context regeneration | done | P1 | Ordinary `--skip-index --quiet` completes and refreshes truthful fast-mode context; full retrieval and explicitly forced retrieval fail closed when the shared runtime is absent; cause and evidence are documented without bypassing canonical motto guards | `/Users/pranay/Projects/agent-start`, `docs/context/agent-start/*`, `docs/issue_review_agent_start_context_2026-08-13.md`, `/Users/pranay/Projects/motto_v5.md` | eng |
| L0-12 | implicit | packaging | Close the local packaged desktop runtime contract for the promoted product direction | done-local | P0 | ARM64 bundle starts the in-process backend with generated user-writable local settings, serves the canonical `/workspace-app/`, contains no developer `.env`, passes bounded local smoke and ad hoc signature verification; cross-platform, notarization, rollback, hosted, and provider evidence remain separate | `desktop_app/backend_manager.py`, `build-tools/SignatureExtractor_*.spec`, `docs/decisions/ADR-0148-local-packaged-runtime-boundary.md`, `docs/review/local_packaging_runtime_proof_2026-08-13.md`, `tests/test_build_profile.py` | desktop + release |
| L2-08 | implicit | backend | Add regression check so extraction responses never return public `uploads/images` URLs | done | P1 | Upload/select responses keep `file_path` null/internal and contract tests guard against accidental reintroduction | `backend/app/routers/extraction.py`, `backend/tests/test_extraction_router.py`, `desktop_app/tests/test_api_client.py` | eng |
| L2-09 | implicit | QA/tooling | Make the canonical local test command collect every first-party backend and desktop suite, while keeping optional PDF capability boundaries explicit | done-local | P1 | Root `pytest` collects all three first-party test roots, the CI matrix uses the same collection, missing optional PyMuPDF skips explicitly, and the expanded suite passes with bounded skips | `pytest.ini`, `.github/workflows/test-data.yml`, `desktop_app/tests/test_pdf_form_fields.py`, `docs/decisions/ADR-0149-first-party-test-discovery-and-optional-pdf-boundary.md` | eng + QA |
| L2-10 | implicit | security/config | Remove hardcoded database credentials, fail closed for incomplete production database configuration, and add a narrow settings reload seam | done-local | P1 | No real-looking credential defaults remain; explicit production configuration fails closed without a complete URL or credentials; isolated local SQLite remains supported; targeted tests pass | `backend/app/config.py`, `backend/tests/test_config_and_path_security.py`, `docs/decisions/ADR-0150-config-and-local-pii-boundary.md` | eng + security |
| L2-11 | implicit | security/privacy | Enforce owner-only POSIX permissions on local user-data, upload, and selection-sidecar paths | done-local | User-data/upload/sidecar directories are `0700` and selection metadata files are `0600` on POSIX; non-POSIX behavior is explicitly bounded | `backend/app/paths.py`, `backend/app/routers/extraction.py`, `backend/app/services/extraction.py`, `backend/tests/test_config_and_path_security.py`, `docs/decisions/ADR-0150-config-and-local-pii-boundary.md` | eng + security |
| L2-05 | implicit | QA | Create QA matrix with reproducible commands/results and attach to runbook | in-progress | P1 | Matrix includes negative-path cases and known-limit table | `docs/QA_*` (new) | PO + QA |
| L2-06 | explicit | web claims | Add `docs/launch_claims/registry.md` and claim smoke check for every public copy statement that implies hosted/cloud behavior | in-progress | P2 | Every hosted claim has a gate test and a source commit hash | `web/live`, `tests/test_landing_surface_contract.py` | PO |
| L2-07 | explicit | UX | Add explicit delete/escape/shortcut discoverability and close alignment with docs | done | P1 | `Docs/SHORTCUTS.md` and actual bindings match | `desktop_app/views/main_window_parts/extraction.py` | eng |
| L0-13 | implicit | release/claims | Reject HTML fallbacks and retired high-risk claims on the deployed root and checkout assets | in-progress | P0 | Local strict audit now reports `13` claim families and `0` errors, while retained legacy claim warnings remain explicit; deployed probe requires canonical root markers, JavaScript checkout assets, required redirects, and no retired absolute claims after deployment propagation | `tools/audit_public_surface.py`, `tools/test_deployed_surface.py`, `tests/test_deployed_surface_probe.py`, `docs/review/claim_surface_inventory_2026-08-13.md`, `QA-27` | eng + Web Platform |
| L0-14 | implicit | release | Create a per-artifact release ledger with checksum, signing, smoke, and rollback evidence | in-progress | P0 | Each platform artifact has source SHA/tag, checksum, platform, signing/notarization state, smoke result, evidence references, release URL, and a recoverable rollback artifact; the strict release job blocks incomplete evidence | `tools/release_artifact_ledger.py`, `tests/test_release_artifact_ledger.py`, `docs/release/RELEASE_ARTIFACT_LEDGER_SPEC.md`, `.github/workflows/build-all-platforms.yml` | eng + release owner |
| L1-07 | implicit | claims | Extend claim governance from the canonical root to all reachable, retained, legal, support, email, and release surfaces | in-progress | P1 | The local audit classifies the retained surface and reports `30` historical documentation references plus explicit legacy-page warnings; every reachable surface must still be qualified, redirected, archived, or removed from delivery, with a clean deployed scan or explicit owner/date | `tools/audit_public_surface.py`, `docs/launch_claims/registry.md`, `docs/review/claim_surface_inventory_2026-08-13.md`, `QA-27` | PO + Legal |
| L1-08 | implicit | operator workflow | Establish one operator-facing state and recovery contract across desktop extraction, PDF placement, Vault, export, and workspace surfaces | in-progress | P1 | The local proof observes extraction, Vault, forced failure, retry, passport, and verified visual placement; workflow and local-companion primary copy are now bounded and recoverable; malformed-input, timeout, partial-export, deletion-cleanup, local-companion process recovery, and accessibility observations remain open | `docs/PRODUCT_GLOSSARY.md`, `docs/STATE_CONTENT_MATRIX.md`, `docs/review/local_operator_state_proof_2026-08-13.md`, `desktop_app/workflows/operator_content.py`, `desktop_app/views/main_window_parts/workflow_console.py`, `desktop_app/views/main_window.py`, `desktop_app/views/onboarding_dialog.py`, `tests/test_operator_content.py`, `tests/test_topology_experience_contract.py`, `QA-28`, `QA-29`, `QA-30` | Product + eng |

## Implicit but must be explicit now

- `backend/app/main.py` previously exposed `/uploads/images` publicly through `StaticFiles`; this contract risk is mitigated by removing the mount and returning private `file_path` values from extraction responses. The hosted extraction contract now enforces authenticated owner/workspace scope, export/deletion/audit receipts, and database-backed idempotent replay. Production migration and rollout evidence remain open under `L0-09`.
- `on_copy` and `on_save_to_library` are now hard-gated. Public legal/policy linkage and trial messaging have been updated in this cycle (menu, about, status bar).
- Several docs remain at “pending” while code moved ahead. This is a high-risk claims gap, even when technical code is done.

- Packaging is now locally proven for macOS ARM64, but no release claim may
  generalize that result to other platforms, notarization, clean installation,
  rollback, hosted deployment, or provider activation.

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
- `L0-11`: Closed for deterministic context generation and false-success prevention. Ordinary fast mode returns `0` with explicit retrieval-skipped sections; full and explicitly forced retrieval return `1` when the shared interpreter or usable `memsearch` runtime is absent. The shared environment rebuild and real retrieval proof remain separately tracked under `RECON-06`.
- `L0-03`: Application closure this pass: authenticated owner/workspace scope, private asset lifecycle, export/deletion/audit receipts, and durable database-backed idempotency are implemented and covered by hosted integration tests. Deployment migration and live-host evidence remain under `L0-09`.
- `L0-04`: Elevated to in-progress; production smoke evidence still reports route inconsistency in previous report.
- `L2-04`: Closed with Tier 3 evidence: `.venv/bin/pytest -q backend/tests/test_extraction_router.py backend/tests/test_extraction_hosted.py` passed `10 passed`; desktop API assertions cover generated idempotency headers. The focused suite was first red on three response classification defects, then passed after fixing those defects (S2).

- `L2-08`: Closed by adding backend regression coverage in `backend/tests/test_extraction_router.py` and client contract assertions in `desktop_app/tests/test_api_client.py`.
- `L2-09`: Closed locally. Root collection now includes `tests`, `backend/tests`, and `desktop_app/tests`; the latest expanded command collects `492` tests and passes `488 passed, 4 skipped`, including the documentation truth-map and operator-state checks. Prior `491 collected / 487 passed` and `487 collected / 484 passed` results remain historical evidence. The optional PyMuPDF boundary is explicit, and the destructor shutdown regression has S2 evidence. Hosted, remote-runner, provider, device, and assistive-technology gates remain separate.

## Addendum (2026-08-13): first-party test collection and context doctrine

The random document audit at
`docs/audits/random_document_audit_AUTO_DETECTION_ML_2026-08-13.md` identified
that root `pytest` silently omitted 291 backend and desktop tests. That finding
was independently reproduced in the live checkout. ADR-0149 makes the three
first-party roots canonical, removes the hand-picked CI collection boundary,
and records the optional PyMuPDF and Qt event-loop limits.

The same startup pass found a generator conflict: the shared
`/Users/pranay/Projects/agent-start` had begun deleting this repository's
tracked `motto_v5.md` in favor of workspace Doctrine 6.0. The generator now
retains a project-local `motto_v5.md` override and records that choice in the
generated context. The workspace Doctrine 6.0 symlink remains available for
projects without a local motto. The original generated Doctrine 6.0 copy was
preserved outside this repository at
`/Users/pranay/Projects/OPERATING_DOCTRINE.md.generated-copy-20260813` before
the symlink was restored.

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
| RECON-06 | implicit | agent-start | open | P1 | The shared `/Users/pranay/Projects/agent-start` wrapper now fails closed for full retrieval when the workspace Python interpreter or usable `memsearch` CLI is absent; `--skip-index --quiet` remains explicitly truthful. The interpreter is still absent and `memsearch` remains a 17-byte `exit 0` stub. | Rebuild the shared workspace-memory environment through the documented setup path, run a real sync/index/search refresh, confirm retrieval results or truthful unavailable status, and attach generated context hashes. |
| RECON-07 | implicit | hosted migration and recovery | open | P0 | Local contract and temporary SQLite smoke exist; no target database or live authenticated recovery receipt is claimed. | Apply target migrations, run authenticated upload/process/export/delete/replay, prove rollback and operator recovery. |
| RECON-08 | explicit | public claims and deployment | open | P0 | Local root, redirect, asset content-type, and retired-claim probes pass Tier 3; the hosted probe remains a release gate. | Run `scripts/test-deployment.sh https://signkit.work` and `tools/test_deployed_surface.py --base-url https://signkit.work --json` after deployment propagation. |
| RECON-09 | explicit | provider and packaging | open | P0 | Provider-neutral receipt and release ledger contracts fail closed without real provider or artifact evidence. | Controlled purchase/revocation, support recovery, signed artifacts, launch smoke, rollback artifact, and ready ledger evidence. |
| RECON-10 | implicit | full validation | open | P1 | Focused suites and mutation gates pass; browser accessibility, device, remote CI, full-suite, and external-corpus evidence remain scoped. | Run each QA row at its required evidence tier and record S2/S3 where release blocking. |

The live reconciliation record is maintained in
`docs/RECONCILIATION_STATUS_2026-08-13.md`. The no-push statement in this
historical addendum was true when it was written; later remote parity is
recorded in the live reconciliation record.

Historical integrated local regression checkpoint: the then-current `main`
checkout passed `170 passed in 9.14s` with the canonical `.venv`, isolated SQLite database,
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
  commits and their evidence. At the time of this historical addendum no remote
  push was performed; current parity is recorded in the live reconciliation
  record.

## Addendum (2026-08-13): agent-start guard correction

The earlier bounded-refresh result above is preserved as historical evidence.
The shared wrapper now fails closed for full retrieval and for an explicitly
forced retrieval attempt under `--skip-index --quiet`: both return exit `1`
when the workspace interpreter or usable `memsearch` CLI is absent. Ordinary
`--skip-index --quiet` remains a truthful exit-`0` fast mode. The shared runtime
is still not rebuilt; `RECON-06` remains open for the documented setup path,
real indexing/search verification, and final context hashes.

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

## Addendum (2026-08-13): worktree file inventory

The a11f worktree is fully accounted for in
`docs/archive/A11F_WORKTREE_281_PATH_ACCOUNTING_2026-08-13.md`. Its preserved
snapshot contains 281 tracked changed paths, of which 234 are byte-identical
in current `main` and 46 have explicit reconciled content. No non-deleted
tracked a11f path is missing from current `main`.

The a11f worktree still contains only the untracked runtime directories
`.codex-test-tmp/` and `.wrangler/`; they remain on disk and are intentionally
excluded from source history. The eb41 worktree is clean and identical to
incoming `17f644b`. `RECON-12` is closed for accounting; hosted, provider,
packaging, and QA gates remain open.

## Addendum (2026-08-13): local product direction promotion

The user clarified that the immediate objective is the long-term, first-
principles local product, not hosted deployment parity. The backlog therefore
adds and tracks the local promotion separately from deployment gates:

| ID | Type | Workstream | Status | Priority | Current evidence | Closure criteria |
| --- | --- | --- | --- | --- | --- | --- |
| RECON-13 | implicit | local product / design | done | P0 | `index.html`, `web/canonical_landing/`, ADR-0146, and 29 focused tests now bind the selected document-registration-studio direction to the canonical root. | Keep the root, local workspace handoff, and claim registry on one canonical path; revisit only through ADR-0146 triggers. |
| RECON-14 | implicit | local product / QA | done | P0 | `node tools/run_local_product_browser_proof.mjs` passed in real Chrome with `reducedMotion: "reduce"` at 1440x900, 390x844, and 320x844; keyboard Source→Mark, pointer Mark→Clean, checkout fallback, workspace handoff, no overflow, and no browser errors passed. | Preserve the reusable proof command and rerun it after local surface changes. Hosted and user-research evidence remain separate gates. |
| RECON-15 | implicit | documentation / truth boundary | done | P1 | ADR-0146 and the visual-direction addendum record the promotion, ownership boundaries, and remaining hosted gates. | Keep dated addenda synchronized when local capability or product direction changes. |
| RECON-16 | implicit | local operator workflow / developer experience | done | P1 | `tools/run_local_product_stack.py --once` started the existing FastAPI companion and canonical `serve.py`, waited for `/health` and `/`, used isolated SQLite and filesystem data defaults even with ambient values set, and cleanly stopped both processes; the long-running stack then passed the full local browser proof. | Preserve the one-command launcher and rerun its startup, browser, isolated-data, and cleanup checks after changes to either local surface. |
| RECON-17 | implicit | local product / operator execution | done-local | P0 | `tools/run_local_source_to_ready_proof.py` runs the real desktop extraction, encrypted vault round-trip, controlled placement/export, forced signing failure, canonical retry, metadata-only passports, and verified artifact receipt in a disposable directory. `tools/run_local_workspace_bridge_browser_proof.mjs` now joins that local execution owner to the browser passport projection and proves the operator-visible recovery path. | Preserve both reusable proofs and rerun them after local execution, passport, browser, or boundary changes. Hosted, packaged, and external-research evidence remain separate gates. |
| RECON-18 | implicit | local product / cross-surface architecture | done-local | P0 | The existing `/workspace` route family now exposes authenticated `/workspace/local-jobs`, `/workspace/local-jobs/{job_id}`, and `/workspace/local-jobs/{job_id}/retry` projections. The desktop JSON store remains the source of truth; `ExecutionPassport` is metadata-only; authorization binds the exact `ExecutionGrant.approver_subject` to the authenticated user; hosted profile returns 404. Focused route tests pass, 2 bridge mutants are killed, and the real Chrome bridge proof passes with 401/404, private-path exclusion, retry, recovery, and zero browser errors. | Preserve one canonical local bridge. Reopen if the desktop store, authorization model, workspace route family, passport boundary, or local/hosted topology changes. Do not interpret this local closure as hosted deployment or legal-signing evidence. |
| RECON-19 | implicit | local product / retry integrity | done-local | P0 | The existing retry route now serializes local store mutations, accepts or derives a bounded idempotency key, persists a replay receipt, and exposes the opaque key through the existing passport. The focused workflow/store/passport/bridge suite passes `32` tests at S1; the full `12/12` mutation manifest passes at S3; same-key replay and concurrent keyed requests converge on one engine execution; fresh source-to-ready and real-Chrome bridge proofs pass at Tier 4. | Preserve the route/store/engine ownership boundary. Reopen if the local store changes, retry becomes multi-process across machines, or receipt retention requires compaction. Hosted/provider retry remains separate. |
| RECON-20 | implicit | local packaged runtime | done-local | P0 | The macOS ARM64 PyInstaller artifact starts the in-process backend with generated local SQLite/JWT settings, serves and renders the bundled canonical `/workspace-app/`, passes the real-browser landing/workspace handoff and authenticated local bridge recovery flow, contains no `.env`, passes ad hoc code-sign verification, and leaves no port-8001 listener after bounded shutdown. | Preserve the spec/runtime contract and rerun `QA-20` after packaging changes. Intel/Windows/Linux, notarization, clean-install, rollback, hosted, and provider evidence remain separate. |
| RECON-21 | implicit | local product / entitlement integrity | done-local | P0 | `desktop_app/license/` now requires an Ed25519-signed canonical receipt for paid access, derives plan/add-on grants from the receipt, rejects unsigned/key-shaped grants, isolates the historical test key behind explicit test mode, includes the activation modules in every PyInstaller spec, and replays one activation idempotently while rejecting a different second entitlement. Focused entitlement tests pass. | Preserve the receipt-owned grant and replay boundary. Reopen when a provider adapter, product ID, account/device policy, refund/revocation delivery, or support recovery path is selected; those remain `L0-02`, `L2-03`, `QA-15`, and `RECON-09` gates. |
| RECON-22 | implicit | local product / auto-detection safety | done-local | P1 | The existing ranked `auto_detect_signatures` API is now surfaced through `SignatureCandidateDialog`; the local code contract exposes a clipped candidate preview and requires confirmation before selection is applied. Focused candidate-picker and detection tests pass. | Preserve explicit human confirmation and the non-probabilistic score label. A real-GUI observation, recall@k/IoU evaluation, and ML/cloud detection remain separate gates requiring a labeled, permissioned corpus and an agreed accuracy bar. |
| RECON-23 | implicit | local product / desktop observation | done-local | P1 | `docs/review/candidate_picker_native_gui_proof_2026-08-13.md` records the native macOS run of `tools/run_candidate_picker_gui_proof.py`: rendered preview, keyboard focus, explicit cancel, confirmation of candidate 2, bounded missing-image messaging, and screenshot digest. | Preserve the reusable proof and rerun it after candidate-dialog or desktop-runtime changes. This does not close assistive-technology, cross-platform, packaged, hosted, or full-workflow gates. |
| RECON-24 | implicit | research / auto-detection evaluation | in-progress | P1 | `docs/research/auto_detection_synthetic_baseline_2026-08-13.md` records a reproducible Tier 2 synthetic baseline. The six-case edge regression has instance recall `0.833` and mean IoU `0.840`; three-case subject-disjoint synthetic validation and test slices each have instance recall `1.000` and mean IoU `0.784`. This is not human, production-like, or permissioned-corpus evidence. | Register a permissioned labeled corpus, or explicitly decide to remain synthetic-only, with provenance/split/retention rules; run a sufficiently sized held-out baseline with failure classes; agree the product accuracy bar; and decide whether any threshold/default can be promoted. Do not collect user documents without explicit consent and deletion rules. |

## Addendum (2026-08-13): synthetic auto-detection baseline

The first local evaluation slice is recorded in
`docs/research/auto_detection_synthetic_baseline_2026-08-13.md`. It advances
RECON-24 from open to in-progress by measuring the checked-in synthetic
fixtures and exposing the known multi-signature miss. It does not close the
permissioned-corpus, product-threshold, or human/production evidence gates.

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

## Addendum (2026-08-13): local entitlement integrity

The local-first entitlement slice is now implemented and tracked as `RECON-21`.
`EntitlementReceipt` signs canonical provider/product/plan/add-on/activation
fields with Ed25519. The local verifier reads only an explicit public-key
keyring, `LicenseInfo` derives paid grants from the signed receipt, and the
activation path replays the same activation without mutation while rejecting a
different second entitlement. Legacy key-only records remain readable but
cannot unlock paid features. The historical test email requires explicit
`SIGNKIT_LICENSE_TEST_MODE=1`.

This closes only the local code and test slice at Tier 2. It does not close the
provider/product configuration, checkout fulfilment, controlled purchase,
refund/dispute/chargeback delivery, device or account policy, support recovery,
or hosted release gates. `L0-02` and `L2-03` therefore remain in progress or
blocked as recorded above; `QA-15` and `RECON-09` remain open.
