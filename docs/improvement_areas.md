# Improvement Opportunities

## Critical Fixes

- ~~Implement `MainWindow.on_save_to_library` so the "Save to Library" button stops raising an `AttributeError` when clicked.~~ ✅ **COMPLETED** (Oct 2025)
- ~~Add an `on_library_item_clicked` slot (or remove the signal hookup) to prevent crashes when the signature list is used.~~ ✅ **COMPLETED** (Oct 2025)
- Unify the upload directory configuration so files written by `extraction.upload_image_endpoint` are consistently stored in `UPLOADS_DIR`, private to backend runtime, and lifecycle-managed.

## Desktop App UX & Features

- Finish the signature library experience: persist saved results, show thumbnails/metadata, and allow reloading into the preview pane. _(IN PROGRESS)_
- Add rotate ↶/↷ controls that re-upload the rotated bitmap and keep selection state in sync.
- ~~Provide inline progress/status cues for long uploads or processing calls (spinner, disabled buttons, status bar text).~~ ✅ **COMPLETED** - Status bar with messages (Oct 2025)
- Restore an optional login flow (auto-open on HTTP 401) or remove the placeholder UI to keep behavior consistent.
- Offer quick actions such as copy-to-clipboard, preset threshold/color combos, and recent color swatches.
- Add accessibility refinements: keyboard shortcuts for zoom/pan/toggle, larger hit targets, and a help/onboarding pane.

## Backend & API Hardening

- Replace form parsing in `/extraction/process_image/` with a validated Pydantic model and return explicit error payloads.
- Normalize uploads: detect content type, convert to a canonical PNG (or preserve original) instead of blindly renaming everything to `.png`.
- Store upload metadata (dimensions, EXIF, processing settings) to support future reporting and reproducibility.
- Add lifecycle management for session files (expiry/cleanup) and quota checks before writing to disk.
- Remove legacy commented blocks from `backend/app/main.py`, routers, and CRUD modules to improve readability and reduce confusion.
- Align module imports (e.g., tests still reference `app.*`) and add automated formatting/linting to prevent regressions.

## Data & Persistence

- Move session/library records into the database so the desktop library can sync across devices or survive restarts.
- Track user activity (uploads, extractions) for audit/history views and potential billing tiers.

## Testing & Observability

- Add integration tests that cover upload → process → save, including EXIF rotation and threshold edge cases.
- Create smoke tests for unauthenticated vs authenticated flows to ensure optional auth paths still work.
- Introduce structured logging and request timing around the extraction endpoints (FastAPI middleware) for easier diagnostics.
- Add GUI smoke tests (e.g., pytest-qt) to exercise the main PySide6 flows in CI.

## Documentation & Developer Experience

- ~~Reconcile conflicting port defaults (README mentions 8001, desktop config defaults to 8001, desktop README cites 8000) and publish a single source of truth.~~ ✅ **COMPLETED** - Standardized on 8001 (Oct 2025)
- Document mandatory environment variables (JWT secret, database URL) and provide a ready-to-use `.env.example`.
- Publish an API reference (`docs/API.md`) with curl examples so integrators know how to talk to the backend.
- Update contributor docs with setup scripts, lint/test commands, and troubleshooting tips (DB migrations, PySide installation).

## Deployment & Packaging

- Script PyInstaller/Nuitka builds for macOS, Windows, and Linux, including notarization/signing guidance.
- Provide Docker Compose (FastAPI + DB) for local development and a production-ready container image with health checks.
- Define a release checklist (tagging, changelog, asset upload) and consider automatic updates for the desktop client.

## Product & Growth Features

- Export companion metadata JSON alongside PNG results (selection bbox, threshold, timestamp, color).
- Support batch extraction and multi-page documents with per-page session tracking.
- Layer in advanced processing toggles (Otsu/adaptive thresholding, morphology, edge smoothing) with sane defaults.
- Prototype contour- or ML-based signature auto-detection and surface suggestions in the UI.
- Add integrations roadmap items (DocuSign, Google Drive, Zapier) with clear MVP slices for each.
- Offer optional cloud sync/workspaces so teams can share signature libraries and audit histories.

## Research Backlog (External Validation Recommended)

- Signature auto-detection
  - Contour/connected-components heuristics: aspect ratio, solidity, area ranges; evaluate on mixed scans and photos.
  - ML detectors: MobileNet/YOLOv8-nano fine-tuned on signature boxes; assess latency on CPU-only.
  - Datasets: CEDAR, GPDS (for signatures) to bootstrap evaluation; verify licensing and suitability for detection vs verification.
- Advanced binarization and cleanup
  - Adaptive methods: Sauvola/Niblack (e.g., scikit-image threshold_sauvola) vs OpenCV adaptiveThreshold; quantify quality vs speed.
  - Morphology pipelines for pen-ink enhancement and background removal; compare bilateral/median denoise + morphological open/close.
- Vectorization & scaling quality
  - Potrace or autotrace for converting to SVG; benchmark fidelity on common pen strokes and noisy inputs.
  - Super-resolution for small signatures (e.g., Real-ESRGAN-lite) to improve print quality; assess model size/CPU viability.
- Packaging & distribution
  - PyInstaller vs Nuitka vs Briefcase; app size, start-up time, Apple notarization, Windows signing; choose cross-platform baseline.
  - Auto-update options: Sparkle (macOS), WinSparkle/Squirrel (Windows); check licensing and embedding with Python apps.
- Privacy, compliance, and telemetry
  - PII handling, local-only default, opt-in analytics (Plausible/PostHog); document data retention for cloud tiers.
  - HIPAA considerations for healthcare workflows; encryption of rest/transit for cloud sync.
- Browser extension architecture
  - Chrome/Firefox Native Messaging vs local HTTP to 127.0.0.1; UX and security trade-offs; store permissions minimalistically.
  - Clipboard pipeline from extension to desktop (PNG and metadata); verify cross-OS reliability.
- Performance & memory
  - Tiling very large images to reduce RAM; lazy-loading and pyramid levels for smooth zoom.
  - Investigate OpenCV CPU optimizations and optional cv2.cuda availability when present; keep pure-CPU fallback.

## Competitive/Benchmarking Checklist

- Compare against: Adobe Scan/Fill & Sign, DocuSign, Smallpdf/ILovePDF (signature tools), Krita/GIMP workflows.
- Benchmarks to capture: extraction accuracy (IoU of mask), time-to-result, file size of outputs, vectorization fidelity, UX steps count.
- Pricing landscape: freemium limits (pages per month, watermarking), team features (shared libraries), API pricing units.

## Open Questions

- Which platforms are tier-1 for packaging (macOS universal2, Windows x64, Linux AppImage)?
- Should library sync be local-only initially (SQLite + OS folder) or offered with optional cloud right away?
- What minimum offline capability is required for enterprise (no network at all vs on-prem server allowed)?
