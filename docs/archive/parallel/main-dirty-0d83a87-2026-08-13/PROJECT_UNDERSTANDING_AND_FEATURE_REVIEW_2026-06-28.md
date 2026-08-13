# Project Understanding & Feature Review
## Signature Extractor App (as of 2026-06-28)

## 0) Scope and context
This review was done against the live codebase in `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app` and the repo’s instruction/context stack.

Primary sources:
- `docs/*` for stated goals and roadmap
- FastAPI backend routes in `backend/app/*.py`
- Desktop runtime entry points in `desktop_app/*`
- PDF signing modules in `desktop_app/pdf/*`

Date context used: Sunday, June 28, 2026.

## 1) What this repo is trying to be
The product is a desktop-first document workflow app that combines:
1. Signature image extraction/editing
2. PDF field placement/signing workflow
3. Session/license management
4. Local auditability and logs
5. Optional optionality for backend-managed pipelines vs local-first processing paths

This is a practical desktop tool with some enterprise-looking infrastructure for auditing, profile-based stacks, and optional runtime resiliency.

---

## 2) High-level architecture (current)

### Backend (`backend/app`)
- FastAPI app entrypoint: `backend/app/main.py`
- Routers:
  - `backend/app/routers/auth.py` under `/auth`
  - `backend/app/routers/extraction.py` under `/extraction`
- Database initialization and startup routines run in startup event.
- Static upload directory is used for persisted uploaded artifacts.

### Desktop app (`desktop_app`)
- UI and flow orchestration in `desktop_app/main.py`, `desktop_app/views/*`
- Backend process manager in `desktop_app/backend_manager.py` with health/restart logic.
- API contract wrapper in `desktop_app/api/client.py`.
- Session and license behavior in `desktop_app/state/session.py` and `desktop_app/license/*`.

### PDF subsystem (`desktop_app/pdf/*`)
- Explicit multi-engine strategy with capability flags (`stack_profile.py`) for:
  - rendering
  - signing
  - OCR/scanning support
  - optional fallback behavior
- Audit and field mapping modules for traceability.

### Data/config layer
- Several JSON/JSONL and docs-driven config assets support runtime behavior and audits.
- Session/state artifacts are generated and logged, not just transient UI states.

---

## 3) Feature state: implemented, partial, missing, and planned

### 2026-06-28 (Product Upgrade: Batch Queue Orchestration)
- Implemented: **desktop batch queue workflow** in `desktop_app/views/main_window_parts/extraction.py`.
  - Added vertical queue controls and list on extraction left rail:
    - `Add to Queue`, `Process Selected`, `Process Next`, `Process Queue/Stop Queue`, `Remove Selected`, `Clear Queue`.
  - Added per-item statuses (`pending`, `processing`, `done`, `failed`) and stable session binding (`session_id`, `error`) for queued items.
  - Added auto-advance queue mode (sequential processing) with graceful stop and continue controls.
  - Added queue refresh, progress label, control-state gating, and empty-state rendering.
  - Added clean-session interaction to stop batch auto-processing so long-running queue runs can be interrupted safely.
- User behavior impact:
  - Users can now queue multiple local image files and process them in sequence while preserving existing horizontal source/preview/result workflow.
  - Queue now provides deterministic control of batch throughput and retry visibility.
- Remaining gap:
  - Retry policy is currently single-pass with manual restart/selection for failures; no exponential backoff or skip/retry policy persists to disk yet.

## Implemented / active
- File upload flow in backend:
  - endpoint validates bytes and stores file references.
- Core extraction pipeline:
  - thresholding/coloring/cropping path and image return.
- Desktop extraction UI:
  - open/signature capture flow, zoom/pan, rotate, selection and controls.
- PDF basic workflow:
  - open PDF, navigate pages, place signature objects, save signed artifact.
- Auditing/instrumentation:
  - JSONL/audit-oriented persistence exists for PDF signing and runtime visibility.
- Runtime orchestration:
  - backend auto-start/health-check in desktop shell.
- License/session integration:
  - session state + gating logic is wired in.
- Documentation corpus:
  - project has explicit architecture, roadmap, status, and gap documents.

## Implemented but fragile / likely to regress
- Backend auth route file contains legacy/dead historical route blocks (commented code) alongside active paths.
- Region selection API path is present but mostly echo/stub behavior in one endpoint, not a real processing action.
- Upload handling is currently narrow and writes with fixed extension, which is not fully faithful to upstream file-type metadata.
- Some features in docs are described as complete at a “roadmap stage,” while runtime proof currently exists for a narrower subset.

## Could be improved (medium priority)
- Remove/repair dead route clutter and inconsistent comments in `backend/app/routers/auth.py`.
- Tighten response/error contracts across extraction endpoints and front-end client usage.
- Normalize upload handling to preserve input format metadata and reduce silent assumptions.
- Strengthen observability in processing/error paths: more explicit server-side failure states and explicit retry/fallback signals.
- Consolidate docs so “implemented vs planned” is one source-of-truth with less stale language.
- Hardening of `/select_region/` to become actionful, idempotent, and validated.
- Improve test coverage for API contract edge cases (invalid images, large file sizes, malformed payloads, timeout paths).

## Not done / incomplete as runtime behavior
- Full duplicate route elimination and canonical route cleanup are not complete.
- No evidence of complete end-to-end contract tests between desktop UI and backend auth/extraction for all branches.
- Many enterprise/automation/richer workflow items remain aspirational in planning docs.
- Some historic architecture alternatives (backend-externalization decisions) are debated but not materially resolved in implementation.
- UX polish set (uniform visual semantics, advanced progress states, robust onboarding copy) is not fully standardized.

## Should be done next (recommended execution order)
1. Route hygiene and contract cleanup
   - finalize extraction route behavior;
   - remove dead/commented route duplicates;
   - standardize payload and validation behavior.
2. API and data correctness hardening
   - make upload/storage safer and transparent;
   - align client parsing, backend responses, and error envelopes.
3. Observability and operations
   - add explicit telemetry fields for backend mode, stack selection, retries, failures.
4. Feature gap closure in order of user value
   - implement full server-side `select_region` path;
   - improve batch handling, repeatability, and deterministic output names.
5. Documentation convergence
   - update one canonical “current state” doc with strict status tags:
     `Done`, `Partial`, `Blocked`, `Not Started`, `Research`.

## Should be explored (deeper investigation)
- Architecture decision: fully local extraction path vs mixed backend-assisted path under desktop constraints.
- Signed artifact trust/forensics: stronger non-repudiation and evidence retention design.
- Adaptive extraction model evaluation:
  - compare deterministic CV thresholds with ML-assisted candidate detection.
- Batch/enterprise workflows:
  - throughput, parallel job scheduling, queue visibility, and retry semantics.

---

## 4) Product vs code truth alignment

### What docs clearly claim
- Ambitious features and near-term roadmap items include enterprise scaling, advanced automation, and deep integration tracks.

### What code clearly does now
- Solid single-user desktop execution with extraction + PDF placement/signing.
- Core workflow is usable and technically functional.
- Some backend/frontend/API edges remain implementation debt.

### Mismatch pattern
- Stale completion tags in historical docs can overstate runtime readiness for several advanced/edge items.
- Planned architecture alternatives are documented but not consistently reflected as active code decisions.

---

## 5) Risks and failure modes to track
- **Contract drift:** docs/roadmaps and implementation diverge on maturity.
- **Operational drift:** commented legacy endpoints/routes can hide duplicated behavior or false confidence.
- **Data correctness risk:** upload/type assumptions reduce fidelity for unusual inputs.
- **Observability gaps:** limited explicit failure diagnostics in some extraction endpoints.
- **Route duplication risk:** rule-level risk if legacy duplicate route files are reintroduced.

---

## 6) Suggested immediate discussion agenda
1. Confirm whether the priority is:
   - clean architecture (route/debt cleanup first), or
   - feature velocity (new extraction/PDF features first).
2. Approve one canonical status taxonomy and source-of-truth doc for feature state.
3. Decide backend architecture direction for next quarter:
   - keep current backend-assisted model,
   - or prioritize local-only paths with backend reserved for heavy tasks.
4. Pick observability depth target:
   - minimum for production reliability (high value),
   - or richer enterprise audit trail.

---

## 7) Action list you can pick now
- [ ] Create a canonical status matrix (Done/Partial/Blocked/Not Started/Planned) in one file.
- [ ] Implement and test `backend/app/routers/extraction.py::select_region` behavior.
- [ ] Remove commented legacy route blocks in auth router, preserve intent through clean deprecation if needed.
- [ ] Add integration checks for upload→select_region→process_image.
- [ ] Refresh three docs at once with synchronized definitions:
  - `docs/CURRENT_STATE_ANALYSIS.md`
  - `docs/IMPLEMENTATION_STATUS_VS_DOCS.md`
  - `docs/ROADMAP.md`
