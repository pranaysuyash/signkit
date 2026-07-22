# Broader Improvement Survey (Frontend, Backend, CV, Features)

**Project:** SignKit (signature-extractor-app)
**Date:** 2026-07-01
**Status:** Survey + bounded fixes implemented; larger items deferred pending product decisions
**Owner:** Session agent (Claude); next reviewer: Pranay

## Summary

Follow-on to the same-day performance audit ([2026-07-01_performance_optimization_audit.md](./2026-07-01_performance_optimization_audit.md)). An Explore agent surveyed the codebase across frontend/UX, backend architecture, CV/extraction quality, and feature/product gaps, producing 16 candidate findings. Per motto_v3 §0.7, each was re-verified before acting — two turned out to be stale or incorrect on inspection (see "Corrected findings" below). Small, bounded, non-controversial fixes were implemented and tested; everything that amounts to a new feature or a security-relevant contract change is reported here for an explicit decision rather than built unprompted.

---

## Fixed

### Backend: `/health` endpoint disclosed the absolute uploads-directory filesystem path
**File:** [backend/app/main.py](../../backend/app/main.py)
**Verified (Tier 1):** `/health` returned `{"uploads_dir": str(UPLOADS_DIR), ...}` — the real server filesystem path, in a public, unauthenticated endpoint. No consumer (desktop client or tests) reads that field; it added no operational value here.
**Fix:** Removed the path; kept `uploads_dir_exists` (a useful boolean operational signal) without the path itself.

### CV: `analyze_quality()`'s failure fallback gave no reason
**File:** [desktop_app/processing/extractor.py](../../desktop_app/processing/extractor.py) — `analyze_quality`
**Verified (Tier 1):** on any exception, returned `{"rating": "Unknown", "issues": ["Analysis Failed"], ...}` with no detail. The UI surfaces `issues` directly in the health-badge tooltip, so users saw an unexplained failure with no actionable next step.
**Fix:** the fallback issue now includes the actual exception message (`f"Analysis failed: {e}"`).
**Tests (Tier 2):** new test in [desktop_app/tests/test_extractor.py](../../desktop_app/tests/test_extractor.py) — forces a `cv2.Laplacian` failure and asserts the real error text appears in `issues`.

### Duplicated hardcoded version placeholder
**Files:** [desktop_app/config.py](../../desktop_app/config.py) (new `APP_VERSION` constant), [desktop_app/views/main_window.py](../../desktop_app/views/main_window.py), [desktop_app/processing/extractor.py](../../desktop_app/processing/extractor.py) (forensic watermark metadata)
**Verified (Tier 1):** the literal `"1.0.0"` was independently hardcoded in two unrelated files with a comment admitting it was a placeholder — a pure "could silently drift apart" risk, since nothing kept them in sync.
**Fix:** centralized into one `APP_VERSION` constant in `config.py`, imported by both consumers. Still a placeholder (no packaging/release process sets a real version yet) — this doesn't invent a fake real version, it just removes the duplicate-literal drift risk. `main_window.py`'s existing `VERSION`-file override mechanism (reads `../../VERSION` if present) is preserved unchanged. Also narrowed an adjacent bare `except:` to `except OSError:` on the same touched lines (correctness hygiene, not scope creep — same lines already being edited).

### CV magic numbers: documented rationale, values left untouched
**Files:** [desktop_app/processing/extractor.py](../../desktop_app/processing/extractor.py) (`auto_detect_signature`'s contour/threshold parameters, `analyze_quality`'s blur/contrast/resolution cutoffs, K-Means ink-cluster selection), [desktop_app/pdf/field_detection.py](../../desktop_app/pdf/field_detection.py) (AcroForm field-type confidence scores, OCR hint confidence formula and 0.35 threshold)
**Verified (Tier 1):** all of these are real, unexplained constants controlling detection accuracy — confirmed by reading the code.
**Decision: document, don't retune.** Changing these values without a labeled set of real signature scans to validate against would be guessing, not fixing — exactly the kind of unjustified change motto_v3 §11 warns against ("avoid ... speculative engineering"). Added inline rationale for what's inferable from standard CV practice (why block sizes are the size they are, why the area/aspect-ratio bounds exist), and explicit "not empirically validated, revisit with labeled data" caveats where the value is genuinely arbitrary. For the K-Means ink-cluster selection specifically (`np.argmin(l_values)`, always assumes the darkest cluster is ink), added a more detailed callout since this is a real robustness gap, not just an unexplained constant: it will misidentify ink on light-pen/dark-paper documents or pages with strong shadows, and does so silently (no confidence signal, produces a plausible-looking but wrong extraction). Fixing that properly is a real algorithmic change (e.g. background-lightness-relative cluster selection, or a confidence score surfaced to the user), not a parameter tweak — flagged, not attempted, without test images covering the failure cases.

---

## Corrected findings (the survey's initial claims did not hold up)

### "Bulk/template adaptive-mode field detection is still synchronous" — stale
The survey read this as an open gap, but it's exactly what the immediately-preceding session work fixed (`PDFViewer.detect_fields_for_pages` + the `skip_detection` flag threaded through `_apply_template_to_target_page`/`_compute_bulk_signature_rect_for_target`; see addendum 2 of the performance audit). Verified directly: `grep skip_detection` shows the batching wiring is in place and the per-page synchronous path is only used as the (correct, unchanged) fallback in single-page contexts.

### "`/select_region/` persists metadata even for zero-area selections" — incorrect
Verified directly by calling `build_selection_metadata()` with a zero-area selection: it raises `ValueError("Invalid crop dimensions: area is zero")` (via `normalize_crop_bounds`) *before* `persist_selection_metadata()` is ever reached, and the router's existing `except ValueError` handler converts that into an HTTP 400. No fix needed; this was already correctly validated.

---

## Flagged, not built: needs an explicit product/architecture decision

These are either new features (not bugs) or a security-relevant contract change — building any of them without direction would be scope creep past "check for and fix improvements."

### Security: uploaded images are served with no authentication
**File:** [backend/app/main.py](../../backend/app/main.py) — `app.mount("/uploads/images", StaticFiles(...))`
**Severity: depends on deployment topology (see below), potentially significant.**
The backend has real JWT auth (`auth.router`) elsewhere, but uploaded signature/document images are served via a plain `StaticFiles` mount with no auth check at all — anyone who obtains or guesses a `/uploads/images/<session_id>.png` URL (session IDs are UUIDs, so this is security-through-obscurity, not real access control) can fetch it. `select_region`'s response includes this URL directly (`routers/extraction.py:69,111`).

Whether this is a real vulnerability or a non-issue depends on how the backend is actually deployed — the desktop app's primary flow is now fully local processing (per the performance audit), so if the backend is only ever run on `127.0.0.1` for local/optional use, exposure is minimal. If there's any hosted/multi-tenant deployment mode, this is a real gap: uploaded images can include full documents (potentially containing other sensitive personal/financial information, not just the signature), and one user's uploads would be fetchable by anyone with (or able to guess) another user's session ID.

**Recommended fix path, if confirmed needed:** replace the static mount with an authenticated download endpoint that checks the requesting user owns the session, or scope the mount behind the existing auth middleware. This changes the `file_path` response contract in `extraction.py`'s router and would need corresponding updates in `desktop_app/api/client.py` and its tests.
**Needs:** confirmation of deployment topology / whether hosted mode is a real near-term target, before deciding whether to fix now.

### Feature: bulk batch processing has no cancel and no progress bar
**File:** `desktop_app/views/main_window_parts/extraction.py` (batch queue processing)
A queued multi-file batch run shows a status label but no progress bar and no cancel button; a user partway through a 50-file batch who wants to stop is stuck waiting. Real UX gap for the batch workflow, but building cancellation correctly (interrupting an in-flight extraction cleanly, not leaving partial state) is a scoped feature, not a one-line fix.

### Feature: OCR-based document cleanup (roadmap item) never built
**File referenced:** `docs/analysis/ROADMAP_30_60_90_2026-06-17.md`
Tesseract is already a dependency and already used for field-detection *hints*, but the roadmap's planned "OCR cleanup path for image-only PDFs" (to improve field detection on scanned documents by making them searchable first) was never built. This is a genuine feature project (new pipeline stage, new UI surface), not a bug fix.

### Feature: signature consistency/anomaly detection (roadmap item) never built
**File referenced:** `docs/analysis/FEATURE_EXPANSION_ROADMAP_2026-06-17.md`
Comparing a newly captured signature against previously saved ones and flagging outliers. Completely unimplemented; a real new capability (similarity scoring, review UI), not a fix.

### Feature: digital certificate / PAdES-style signing (roadmap item) never built
**File referenced:** `docs/analysis/ROADMAP_30_60_90_2026-06-17.md`
Current signing is image-stamping, not a legally-binding digital signature with certificate/timestamp. The roadmap names `pyHanko` as a candidate library. Large feature with real legal/compliance implications if pursued — needs explicit product sign-off, not something to bolt on.

### Feature: no "auto-fill detected form fields with the extracted signature" workflow
**Files:** `desktop_app/views/main_window_parts/pdf.py`, `desktop_app/pdf/field_detection.py`
Field detection identifies likely signature fields, but there's no one-click "fill every detected field" action — users place each detected field's signature manually. A plausible, bounded feature (not a bug), listed here as a product idea rather than something built unprompted.

### UX: Undo/Redo menu actions exist but are permanently disabled
**File:** `desktop_app/views/main_window.py`
Present in the menu (matching platform convention) but wired to `setEnabled(False)` with no undo stack behind them. Since the interactive extraction workflow is largely non-destructive (preview-based, nothing auto-saves), the absence is lower-impact than it looks, but a permanently-disabled menu item with no explanation is a rough edge. Real undo/redo requires a command-stack architecture — a scoped feature project, not a quick fix.

### UX: "Cloud sync/updates disabled" message is a dead end
**File:** `desktop_app/views/main_window_parts/extraction.py`
Tells the user a feature is disabled with no path forward (no explanation of why, no ETA, no alternative). Minor but easy to improve messaging-only if desired — flagged rather than changed since the "why" behind the current cloud-feature gating is a product decision I don't have visibility into (license tier? incomplete backend integration? deliberately paused?).

---

## Test summary

```
tests/ (root, excluding e2e):                53 passed
desktop_app/tests/ (full suite):            138 passed, 3 skipped (pre-existing, unrelated)
```

New/changed test coverage in this pass: `desktop_app/tests/test_extractor.py` (new failure-path test for `analyze_quality`). All other changes in this doc are comment-only (CV rationale) or trivial response-shape edits (health endpoint) with existing coverage unaffected.

## Remaining open items

1. **Uploads-serving auth gap** — needs a deployment-topology answer before deciding whether/how to fix.
2. **Five flagged features** (batch cancel/progress, OCR cleanup, anomaly detection, digital certificates, auto-fill-detected-fields) and **one UX gap** (undo/redo) — all real, none built; each needs its own scoping conversation if prioritized.
3. CV parameter values (contour detection, quality thresholds, field-detection confidence scores) are now documented but still unvalidated against real labeled data — if extraction/detection quality issues are reported in practice, start here.
