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
| L0-07 | explicit | config | Standardize port policy between docs, backend config, and dev scripts | done | P1 | `scripts/run-backend-dev.sh` uses configurable `BACKEND_PORT` (default 8001), the root `.env` is the shared settings surface, and tracked app docs align around 8001 in active paths | `scripts/run-backend-dev.sh`, `backend/app/config.py`, `backend/app/database.py`, `backend/alembic/env.py`, `tests/test_configuration_contract.py` | PO + eng |
| L0-08 | implicit | architecture | Restore canonical motto propagation so `agent-start` can regenerate context without a symlink guard failure, and promote doctrine additions to the Downloads source | done | P0 | `/Users/pranay/Downloads/motto_v5.md` contains the doctrine additions; `/Users/pranay/Projects/motto_v5.md` is a symlink to that source; project context regeneration exits successfully and records the canonical source | `/Users/pranay/Downloads/motto_v5.md`, `/Users/pranay/Projects/motto_v5.md`, `/Users/pranay/Projects/agent-start`, `docs/context/agent-start/*` | PO + eng |
| L1-01 | explicit | licensing | Implement consistent evaluation mode behavior across export/copy/save path and status copy in UI copywriting | done | P1 | Export/copy/library now use one gate helper, action controls are disabled in trial, and lock messaging is unified | `desktop_app/views/main_window_parts/extraction.py` | eng |
| L1-02 | explicit | docs | Publish legal/commercial footer entries in Help/About (refund/privacy/terms/notice access) and remove missing claims | done | P1 | Every Help/About surface includes legal policy links and refund path references | `docs/HELP.md`, `docs/SHORTCUTS.md`, `desktop_app/views/main_window.py`, `desktop_app/views/main_window_parts/status.py` | PO |
| L1-03 | explicit | docs | Unify config references to port 8001 and generate `.env.example` with exact required variables | done | P2 | `.env.example` documents the shared root `.env` contract, local SQLite/8001 defaults, required secret replacement, and all active tracked docs use the same values | `.env.example`, `backend/app/config.py`, `scripts/run-backend-dev.sh`, `tests/test_configuration_contract.py` | eng |
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
| L2-05 | implicit | QA | Create QA matrix with reproducible commands/results and attach to runbook | done | P1 | Matrix includes negative-path cases, reproducible commands/results, evidence tiers, hosted gates, and a known-limit table | `docs/QA_CHECKLIST.md`, `docs/QA_RESULTS.md`, `docs/LAUNCH_TOP_10_STATUS.md` | PO + QA |
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
6. [done] Add a task status legend to `.env` docs and `.env.example` to remove historical drift.
7. [done] Run a focused extraction-route safety smoke locally with the canonical `.venv` backend test profile.
8. [pending] Close wayfinder blockers with explicit dependency conditions before commercial web expansion decisions.
9. [done] Draft and implement the release artifact ledger; retain external signing, smoke, rollback, and tagged-run evidence as open closure gates.
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

- `L0-07`: Closed with a shared repository-root `.env` settings path, explicit
  `DATABASE_URL` resolution, local SQLite fallback, and launcher contract
  tests. This is local configuration evidence, not hosted database evidence.
- `L1-03`: Closed for active documentation and runtime-source alignment. The
  example secret remains intentionally invalid until an operator replaces it,
  so copying `.env.example` is a setup template, not a production credential.
- `L2-05`: Closed for the requested QA matrix artifact. Local matrix results are
  recorded as S1 unless the test-sensitivity requirement is independently
  promoted to S3; device, hosted, migration, packaging, and provider gates
  remain open and are not hidden by the local passes.

## Addendum (2026-08-13): configuration and QA closure

- New implicit task completed: make `.env.example`, backend settings, Alembic,
  database initialization, and `scripts/run-backend-dev.sh` share one root
  configuration contract. `tests/test_configuration_contract.py` passed `6
  passed`; an isolated SQLite migration reached Alembic head.
- New implicit task completed: close the all-orientation EXIF and unsupported
  media-type QA gaps. The desktop loader now uses `ImageOps.exif_transpose`
  and explicit RGB stride; `desktop_app/tests/test_main_window_logic.py`
  passed `28 passed, 3 skipped`, and `backend/tests/test_extraction_router.py`
  passed `7 passed` with the 415 contract.
- New implicit task completed: create and execute the local QA matrix. See
  `docs/QA_CHECKLIST.md` and `docs/QA_RESULTS.md`. The task artifact is done;
  hosted deployment, target migration/recovery, clean-install/device, and
  provider purchase evidence remain release gates under L0-04, L0-09, and
  L0-15.
- The configuration status legend is now present in both `.env.example` and
  `docs/README.md`, with a contract assertion in
  `tests/test_configuration_contract.py`.

## Motto_v5 continuation review (2026-08-13): configuration and QA pass

### Pass 1: immediate correctness and completeness

- The documented root `.env` contract, backend settings, database URL
  resolution, Alembic environment, and launcher now agree on local defaults.
- The QA matrix is executable and records large payloads/dimensions, all eight
  EXIF orientations, tiny selections, 415/404/422 negative paths, offline mode,
  and configuration. The EXIF check found and closed the RGB scanline stride
  defect before the final pass.
- The current local result is `33 passed` for backend/config scope and `56
  passed, 3 skipped` for desktop/API scope. Skips are event-loop-dependent
  tests outside the changed loader path and remain visible in the QA record.

### Pass 2: architecture and long-term viability

- The implementation extends the existing settings, extraction route, and
  desktop loader. It does not add a duplicate upload route, parallel config
  source, or alternate EXIF pipeline.
- QA separates local code evidence from runtime, hosted, migration, device,
  packaging, and provider evidence. The known-limit table is part of the
  canonical launch artifact rather than hidden in test output.
- Unsupported media type handling is a boundary-level 415 contract while
  extension, magic-number, size, dimension, and malformed-image checks remain
  distinct validation layers.

### Pass 3: rule compliance and supervision readiness

- No commit, stage, push, deployment, reset, cleanup, or destructive action was
  performed. Existing dirty and untracked parallel work remains preserved.
- Evidence is labeled by tier and test sensitivity. Local passes do not close
  the failing `signkit.work` probe, target migration/recovery, clean-install,
  signing, or provider purchase gates.
- Local-scope confidence is high but below `1.00` for release readiness because
  those external gates remain unverified. The next closure triggers are the
  exact QA-12 through QA-15 procedures in `docs/QA_CHECKLIST.md`.

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

## Addendum (2026-08-13): execution register and release-gate hardening

This addendum is the current execution view for the next implementation pass.
It supersedes older status wording where the live checkout or deployed probe
shows a different state. Static checks are not deployment proof.

| ID | Type | Workstream | Task | Status | Priority | Acceptance | Evidence | Owner |
|---|---|---|---|---|---|---|---|---|
| L0-12 | implicit | release | Make the route authorities and deployment smoke agree on one canonical `/` plus legacy `301` policy | in-progress | P0 | `_redirects`, `serve.py`, `scripts/test-deployment.sh`, `tools/test_deployed_surface.py`, and tests use the same route policy; local gate passes; deployed gate passes with query preservation | `docs/launch_claims/public_surface_map.md`, `tests/test_deployed_surface_probe.py`, `scripts/test-deployment.sh` | eng + Web Platform |
| L0-13 | implicit | release/claims | Reject HTML fallbacks and retired high-risk claims on deployed root and checkout assets | in-progress | P0 | Deployed probe requires HTML root, JavaScript checkout assets, canonical markers, and no retired absolute claims; a deliberate HTML fallback fails the test | `tools/test_deployed_surface.py`, `tests/test_deployed_surface_probe.py`, live probe output 2026-08-13 | eng + Web Platform |
| L0-14 | implicit | release | Create a per-artifact release ledger with checksum, signing, smoke, and rollback evidence | in-progress | Each platform artifact has source SHA/tag, checksum, platform, signing/notarization state, smoke result, evidence references, release URL, and rollback artifact; the strict release job blocks incomplete evidence | `tools/release_artifact_ledger.py`, `tests/test_release_artifact_ledger.py`, `docs/release/RELEASE_ARTIFACT_LEDGER_SPEC.md`, `.github/workflows/build-all-platforms.yml` | eng + release owner |
| L1-07 | implicit | claims | Extend claim governance from the canonical root to all reachable, retained, legal, support, email, and release surfaces | in-progress | P1 | Every reachable surface is classified and either qualified, redirected, archived, or removed from delivery; deployed scan is clean or has explicit owner/date | `tools/audit_public_surface.py`, `docs/launch_claims/registry.md`, `docs/review/claim_surface_inventory_2026-08-13.md` | PO + Legal |
| L1-08 | implicit | operator workflow | Establish one operator-facing state and recovery contract across desktop extraction, PDF placement, vault, export, and workspace surfaces | in-progress | P1 | Core source-to-export workflow, failure states, retry/idempotency, cleanup, and receipts are documented and runtime-observed; terminology distinguishes local companion from hosted service | `docs/PRODUCT_GLOSSARY.md`, `docs/STATE_CONTENT_MATRIX.md`, `desktop_app/views/`, `desktop_app/workflows/` | Product + eng |
| L1-09 | implicit | CI/release | Add backend migration, hosted smoke, public-surface, and high-risk test-sensitivity gates to CI | in-progress | P1 | CI uses the canonical environment, applies migrations, runs backend and hosted smoke, runs public probes, and reports S2/S3 evidence for launch invariants | `.github/workflows/test-data.yml`, `tools/run_extraction_hosted_smoke.py`, `tools/mutation_check.py` | eng |
| L1-10 | implicit | developer experience | Restore deterministic agent-start context regeneration and distinguish propagation from retrieval health | in-progress | P1 | Regeneration completes within a bounded timeout, generated context is populated, retrieval failures are visible and dispositioned, and no parallel context work is overwritten | `/Users/pranay/Projects/agent-start`, `docs/context/agent-start/SESSION_CONTEXT.md` | eng + workspace tooling |
| L0-15 | implicit | licensing | Convert provider research into a provider-neutral entitlement and receipt contract before replacing local-only key acceptance | in-progress | P0 | Gumroad product ID, verification state mapping, replay/idempotency, offline grace, revocation/refund behavior, support recovery, and controlled purchase evidence are documented and implemented | `docs/research/gumroad_entitlement_contract_2026-08-13.md`, `desktop_app/license/entitlements.py`, `desktop_app/license/storage.py`, `tests/test_entitlement_receipts.py` | eng + release owner |

### Execution update

- `L0-12`: implementation started. The deployment script now treats `/index.html` as a legacy redirect, matching `_redirects`, `serve.py`, and the public-surface map. Production still returns `308` or `200` for several paths, so the task remains open.
- `L0-12`: local closure advanced. `serve.py` now matches the wildcard retained-tree rules already present in `_redirects` for generated deploy, archive, backup, concept, and HTML documentation paths. `bash scripts/test-deployment.sh http://127.0.0.1:8080` passed across the full local route, content-type, and asset matrix. The task remains open only for target deployment propagation and the live probe.
- `L0-13`: implementation started. The deployed probe now checks JavaScript media types, canonical checkout markers, root content type, and retired absolute claims. The deliberate HTML-fallback regression test was red before the implementation and now passes, giving S2 evidence for the new guard. The live site still fails the probe.
- `L1-07`: research/documentation started. `docs/review/claim_surface_inventory_2026-08-13.md` classifies the canonical root, retained HTML, desktop onboarding, legal docs, and release workflows. Remediation remains open because several legacy or legal surfaces contain stronger wording than the current claim registry permits.
- `L1-07`: local browser evidence added. The canonical root rendered at `http://127.0.0.1:8080/` with the expected title, one main landmark and h1, a focusable skip link, resolved ARIA references, and no browser console errors. This is Tier 4 local runtime evidence only; deployed and legal disposition remain open.
- `L1-08`: research/documentation started. `docs/PRODUCT_GLOSSARY.md` and `docs/STATE_CONTENT_MATRIX.md` now define the shared local/hosted vocabulary, operator states, recovery expectations, and receipt obligations. Code-surface mapping and runtime proof remain open.
- `L1-09`: implementation started. The existing GitHub workflow now validates the backend environment, applies Alembic head to an isolated CI database, runs backend contract tests, runs the authenticated extraction smoke, and runs the public-surface contract checks. The task remains open until a CI run proves the workflow itself and S2/S3 high-risk sensitivity coverage is attached.
- `L1-09`: local deployment execution was added to the workflow. CI now starts the canonical `serve.py` on loopback and runs the complete `scripts/test-deployment.sh` matrix before syntax checks. The local equivalent passed in this worktree; the task remains open until GitHub executes the workflow and high-risk S2/S3 evidence is attached.
- `L1-09`: the reproducible release QA matrix is now bound into the existing
  `test-data` workflow and protected by `tests/test_ci_workflow_contract.py`.
  A serialized CI-equivalent run passed `90 passed, 3 skipped`, the hosted
  extraction smoke passed, and the separate mutation gate killed `5/5`
  mutants. The first concurrent mutation-plus-test attempt was invalid because
  the sensitivity tool edits source during execution; it was not counted.
  The task remains open only for a real GitHub workflow receipt and retained
  S2/S3 evidence from that runner.
- `L1-10`: static propagation remains aligned, but the generated context contains retrieval failures. A full `agent-start` regeneration is not run in this pass until its overwrite behavior is isolated from the dirty parallel context files.
- `L1-10`: execution evidence updated. `agent-start --skip-index --quiet` completed in 12 seconds and truthfully produced fast-mode retrieval-skipped sections. The full bounded refresh returned shell exit `0` but emitted a missing workspace-memory interpreter error and regenerated search-failed sections. See `docs/issue_review_agent_start_context_2026-08-13.md`; rebuilding the shared `.venv` remains an explicit workspace-tooling action, not silently performed here.
- `L0-15`: provider research started and is documented in `docs/research/gumroad_entitlement_contract_2026-08-13.md`. Official Gumroad documentation confirms product-ID verification and provider state fields, but no SignKit product ID, controlled purchase, or provider-to-license receipt path is configured. The task remains pending and local minimum-length key acceptance is not release evidence.
- `L0-14`: implementation started. `tools/release_artifact_ledger.py` is now the canonical dependency-light ledger producer and validator. It computes SHA-256 and byte counts from the actual files, requires explicit signing and smoke statuses plus evidence references, and blocks a strict release without a recoverable prior artifact. The release job now checks out the source, generates JSON and operator-readable Markdown, attaches both to the release, and runs the strict gate. The task remains open because repository signing/smoke evidence inputs and a rollback artifact are not configured, and no tagged workflow run has yet produced Tier 3 evidence.
- `L0-15`: implementation started. `desktop_app/license/entitlements.py` now defines the provider-neutral receipt and state contract, including fail-closed unknown/refunded/disputed/chargebacked mappings and bounded offline grace. `desktop_app/license/storage.py` persists the contract without changing the legacy no-receipt compatibility path. The focused receipt and storage suite passes `8 passed` after a red-first import failure. The task remains open until a real provider adapter, configured product ID, replay/idempotency policy, and controlled purchase or sandbox evidence exist.
- The release QA run also exposed noisy destructor logging after pytest closed its
  capture stream. `SignatureExtractor.__del__` now performs silent best-effort
  cleanup during interpreter teardown while explicit cleanup retains normal
  observability; `desktop_app/tests/test_extractor.py` covers the boundary with
  `9 passed`.
- Existing local public-surface tests remain S1 only. They do not close any production, provider, accessibility, comprehension, migration, or entitlement gate.

## Addendum (2026-08-13): artifact ledger execution register

- Red-first evidence: importing `tests/test_release_artifact_ledger.py` before
  the tool existed failed during collection with `ModuleNotFoundError`; after
  implementation, the same focused suite passed `2 passed`. This is S2 for
  the ledger readiness contract, not release proof.
- The strict GitHub release gate intentionally defaults missing signing,
  smoke, and rollback inputs to blocked states. Repository or environment
  owners must provide evidence-bearing values before a tagged release can be
  published. A successful ledger unit test cannot substitute for that
  external configuration or a real workflow run.
- Closure criteria added: run the tagged workflow with real artifacts, attach
  the JSON and Markdown ledger, record platform launch smoke and signing or
  notarization evidence, verify a recoverable prior-release artifact, and
  retain the workflow URL and release receipt in the release review record.

## Motto_v5 review passes (2026-08-13)

### Pass 1: immediate correctness and completeness

- Route policy is now internally aligned for local preview and deployment
  scripts: root `200`, legacy `/index.html` and retained paths `301`, with
  query preservation.
- The deployed probe now fails on content-type fallback, missing canonical
  markers, and retired root claims. The live probe remains red as expected.
- Local companion and onboarding copy no longer says “cloud features enabled”
  or “Works 100% offline”; the regression test was red before the fix and is
  green after it (S2).
- New task IDs cover the release, claim, operator, CI, context, and entitlement
  gaps found during implementation.

### Pass 2: architecture and long-term viability

- Existing `_redirects`, `serve.py`, deployment scripts, and public-surface
  tools were extended. No duplicate route or parallel checkout pipeline was
  introduced.
- The CI changes extend the existing test-data workflow rather than creating a
  second backend pipeline. The hosted smoke remains explicitly local
  production-like evidence, not target-host proof.
- The entitlement work stops at the provider-neutral contract and research
  boundary until a real product ID and controlled provider flow exist. This
  avoids hardening a local-only fallback into a false source of truth.

### Pass 3: rule compliance and supervision readiness

- Static evidence, S2 regression evidence, local runtime evidence, external
  provider research, and live deployment failures are separately labeled.
- Full `agent-start` retrieval is not marked complete. The missing shared
  workspace-memory interpreter is recorded in
  `docs/issue_review_agent_start_context_2026-08-13.md` with an owner and exact
  repair path.
- No deployment, provider purchase, commit, push, reset, stage, or destructive
  cleanup was performed. The dirty parallel tree remains preserved.

## Motto_v5 continuation review (2026-08-13)

### Pass 1: immediate correctness and completeness

- The local deployment gate now exercises the explicit and wildcard retained
  route classes; it passed against `serve.py` after the wildcard parity fix.
- The release ledger and entitlement tests both used red-first checks. The
  combined focused suite passed `33 passed`, but no test count is treated as
  production or provider proof.
- The live target was re-probed and remains red: it serves the older root,
  `200`/`308` variants, and HTML at the checkout JavaScript paths.

### Pass 2: architecture and long-term viability

- Wildcard route handling was added to the existing local route authority, not
  a second redirect mechanism. Entitlement state is a shared provider-neutral
  primitive, not a Gumroad-specific branch in the feature gate.
- Release metadata is produced by one tool and retained as JSON plus Markdown;
  no second release manifest or parallel provider receipt store was introduced.

### Pass 3: rule compliance and supervision readiness

- ADRs `ADR-0145` and `ADR-0146` record the route and entitlement decisions,
  alternatives, risks, evidence tiers, and closure triggers.
- Remaining external gates have explicit owners and falsifiers: Web Platform
  must propagate the canonical public surface, and release/product owners
  must configure provider and artifact evidence before closing the P0 tasks.
- Current confidence is below complete release readiness because live
  deployment parity, CI execution, provider purchase evidence, legal review,
  and full cross-platform smoke remain unverified.

## Motto_v5 continuation review 2 (2026-08-13)

### Pass 1: immediate correctness and completeness

- The canonical Python 3.13 environment now passes the backend-aware test-data
  preflight. The manifest validator reports `29 entries validated`, the
  synthetic signature corpus validator passes, and a direct hash comparison
  reports zero mismatches.
- Restored generated signature edge-case and benchmark PNGs are now explicitly
  allowlisted in `.gitignore`, so the manifest-listed assets remain visible to
  version control in a clean checkout. This closes a reproducibility gap that
  was previously hidden by the broad image ignore rule.
- The focused high-risk suite passed `55 passed`, including real PDF workflow,
  entitlement storage/state, release ledger, public surface, execution
  passport, and artifact receipt coverage.

### Pass 2: architecture and long-term viability

- The CI migration command was exercised against a fresh SQLite database and
  initially exposed that `backend/alembic.ini` must run from `backend` with
  `PYTHONPATH=..`. The workflow now uses that canonical working directory and
  import path instead of claiming migration coverage that could not execute.
- The corrected migration gate reached Alembic head and the backend contract
  suite passed `28 passed`. The existing workflow remains the single CI path;
  no parallel migration pipeline was added.

### Pass 3: rule compliance and supervision readiness

- The local server smoke matrix passed all route, redirect, content-type, and
  checkout asset checks. The local public-surface audit and local deployed
  surface probe both pass; retained historical claim warnings remain explicit
  open work under `L1-07`.
- CI is still not closed until GitHub executes the updated workflow, and the
  external public site remains red until deployment propagation is performed.
  No deployment, commit, push, staging, or destructive cleanup was performed.
- The curated S3 gate initially exposed an ambient-settings collection defect
  for backend mutants. `tools/mutation_check.py` now supplies isolated JWT and
  SQLite settings, the rerun killed all `5/5` mutants, and
  `.github/workflows/test-data.yml` now executes the gate. This is S3
sensitivity evidence for the listed invariants, not full product coverage.

## Motto_v5 continuation review 3 (2026-08-13)

### Pass 1: immediate correctness and completeness

- `L1-08` advanced from documentation-only to an operator-visible contract.
  `desktop_app/views/main_window_parts/workflow_console.py` now renders the
  selected job's metadata-only execution passport, bounded recovery action,
  attempt count, data boundary, and ordered event codes. The panel is read-only
  and excludes document paths, raw error text, and document bytes.
- The targeted Qt and passport suite passed `18 passed`. A selected retry job
  with an error event was observed through the console test path and exposed
  `retry_local_job` plus `ERR_OUTPUT_IO` without leaking the synthetic output
  path.

### Pass 2: architecture and long-term viability

- The operator panel reuses `project_local_job()` and the existing workflow
  store. No second state machine, event store, or browser-specific local
  receipt was introduced.
- The tagged release workflow now runs the dependency-free public-surface
  auditor before the release artifact ledger. `tests/test_public_surface_audit.py`
  verifies gate ordering, and the public-surface test set passes `21 passed`.
- `scripts/deploy_canonical_landing.sh` now requires and uses the canonical
  `.venv/bin/python` for audit, test, compile, and deployed-probe commands. Its
  confirmation barrier remains unchanged, and the wrapper was not invoked.

### Pass 3: rule compliance and supervision readiness

- The local claim audit remains green with explicit retained-page warnings; the
  warnings are not treated as legal approval or deployed proof.
- `L1-08` remains in progress because full source-to-export manual runtime
  recovery observation is still open. `L1-07` remains in progress because the
  live site and legal/retained claim surfaces still require disposition.
- The final current-state probe at 2026-08-13 14:02 local time still reports
  the deployed root marker mismatch, `200`/`308` legacy-route responses, and
  HTML content at both checkout JavaScript paths. This remains the falsifier
  for `L0-12` and `L0-13`; local smoke remains green.
- The release and operator changes are locally verified, but no CI run,
  deployment, provider purchase, legal approval, commit, push, staging, or
  destructive cleanup was performed.
