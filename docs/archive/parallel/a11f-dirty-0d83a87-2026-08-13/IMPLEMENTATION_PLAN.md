# Implementation Plan — Signature Extractor

## Overview
- Scope: Consolidated plan covering current state, gaps, quick wins, phased delivery, backend cleanup, research spikes, QA/observability, and open decisions.
- Sources: Code review across desktop_app, backend/app, and docs; aligns with docs/ROADMAP.md and docs/improvement_areas.md.

## Current State Snapshot
- Desktop UI: Selection/pan toggle, EXIF rotation, zoom/fit/reset, crop preview, debounced live preview, status bar with session ID (main_window.py).
- Export: Professional export dialog (PNG-24/PNG-8/JPEG, backgrounds, trim, quality) with docs (export_dialog.py, docs/EXPORT_OPTIONS.md).
- Icons: Centralized icon manager using Qt standard icons + emoji (desktop_app/resources/icons.py) and applied in main window.
- Backend: `/extraction/upload` and `/extraction/process_image/` operational; uploads kept under `uploads/images` for internal processing/sync.
- Pricing/Docs: Updated pricing strategy, icons research, auto-detection plan, use cases, roadmap (docs/PRICING.md, ICON_OPTIONS.md, AUTO_DETECTION_ML.md, USE_CASES.md, ROADMAP.md).

## Gaps & Risks
- Library persistence: No local library directory/indexing; list handlers are placeholders.
- Rotation: No 90° CW/CCW rotate and re-upload flow.
- Trial/licensing: Pricing/trial documented but no enforcement logic implemented.
- API consistency: Commented/duplicated blocks in backend/app/main.py and routers cause maintenance risk.
- Port/docs: Unify on port 8001 across all docs and examples.
- Uploads path cohesion: Ensure writer paths stay within user-writable storage and are not publicly exposed; document retention/deletion policy.
- Shortcuts: Missing keyboard shortcuts (Ctrl+O, Ctrl+S, Delete, Esc).
- Tests: No automated integration tests for upload→process; no GUI smoke tests.

## Quick Wins (1–2 days)
- Library MVP
  - Create default directory: ~/.signature_extractor/signatures (per OS conventions).
  - Quick-save with auto name; populate sidebar; double-click to open.
- Rotation CW/CCW
  - PIL rotate locally; re-upload as new session; reset selection; update status.
- Keyboard Shortcuts
  - Ctrl+O open, Ctrl+S export, Delete clear, Esc cancel selection.
- Docs Sync
  - Standardize port 8001; add .env.example with JWT_SECRET and DATABASE_URL (SQLite).

## Phased Delivery
- Phase 1 — Library + Rotation (Now)
  - Deliverables: Persistent library save/load; rotate CW/CCW with re-upload; clear status updates.
  - Acceptance: Items persist across restarts; rotated images get new session_id; no crashes.

- Phase 2 — Processing Options
  - Deliverables: Threshold mode dropdown (Manual/Otsu/Adaptive); morphology toggles (erode/dilate); basic edge smoothing option.
  - Acceptance: Visible quality changes; consistent performance on large images.

- Phase 3 — Export & Metadata
  - Deliverables: Export metadata JSON (bbox, settings, timestamp); clipboard copy; preset save/load (color/threshold/morphology).
  - Acceptance: JSON saved alongside image; presets persist across sessions.

- Phase 4 — Trial/License Hooks
  - Deliverables: Local counters for days and extractions (7 days, 10 extractions by default); soft-gate messaging; optional online check stub.
  - Acceptance: Remaining usage visible; transitions to view-only after limits.

- Phase 5 — Cleanup & Tests
  - Deliverables: Backend code cleanup (remove commented duplicates); integration tests for upload/process; minimal GUI smoke test.
  - Acceptance: Clean app startup; tests run green locally.

## Backend Cleanup & Hardening
- Consolidate backend/app/main.py to one canonical setup; remove commented/duplicated code blocks.
- Normalize uploads: validate content types; keep internal paths private; avoid forced .png renaming on upload (convert only when needed in process).
- Local upload lifecycle: Keep validated files private, atomically persisted, and cleaned by the 24-hour default retention task (`SIGNKIT_UPLOAD_RETENTION_SECONDS`). The hosted extraction contract now adds authenticated owner/workspace scope, export/deletion/audit receipts, and durable database-backed idempotency; target-database migration and live rollout remain release prerequisites.
- Imports: Unify tests/scripts to backend.app.* namespace.

## Research Spikes (External Validation)
- Auto-detection
  - Contour/connected-components heuristics; measure IoU/precision on 20–30 samples.
  - ML detector (MobileNet/YOLOv8-nano) viability on CPU; optional model download.
- Binarization & cleanup
  - Compare OpenCV adaptiveThreshold vs Sauvola (scikit-image) on uneven lighting.
- Vectorization
  - Potrace/autotrace quality for SVG export; fidelity on pen strokes.
- Packaging
  - PyInstaller baseline for macOS/Windows/Linux; signing/notarization notes.

## Quality & Observability
- Integration tests: authenticated upload → select → process → export/delete/audit assertions; cross-owner/workspace denial; duplicate and concurrent retry convergence; malformed/oversized input and partial-failure recovery.
- Logging: Structured request logging with durations around processing endpoints.
- GUI smoke: Minimal pytest-qt or scripted sanity checks if feasible.

## Open Decisions
- Library path and metadata: Default folder, store thumbnails/JSON index?
- Trial UX: Where to surface limits/messages; offline behavior policy.
- Defaults for advanced processing: Which options are enabled by default to keep UI simple.

## Dependencies & Config
- Default DB: SQLite for desktop (DATABASE_URL=sqlite:///backend/data/app.db). Keep Postgres optional for server use.
- API Base URL: Default http://127.0.0.1:8001; document override in .env and desktop_app/config.py.

## Success Criteria
- User can: upload, select, preview, export, rotate, and manage a local library without errors.
- Clean startup (no noisy logs), consistent port/docs, and basic tests passing.
- Clear, incremental feature adoption without regressing core flows.

### Hosted extraction contract addendum (2026-08-12)

The canonical route is `backend/app/routers/extraction.py`. Do not add a second upload or extraction route. Asset ownership is `Image.user_id`; workspace execution ownership is checked through `WorkspaceExecution.owner_user_id`. `ExtractionAuditEvent` is the durable receipt source. Apply migration `e42b7f8c91aa` before enabling hosted extraction and retain the `L0-09` live smoke gate.
