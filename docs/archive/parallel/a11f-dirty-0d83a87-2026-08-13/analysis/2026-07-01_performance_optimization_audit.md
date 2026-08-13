# Performance Optimization Audit & Implementation

**Project:** SignKit (signature-extractor-app)
**Date:** 2026-07-01
**Status:** Implemented (see per-item disposition below)
**Owner:** Session agent (Claude); next reviewer: Pranay

## Summary

A first pass (subagent-generated) produced 12 candidate performance findings across the desktop app and backend. Per motto_v3 §0.7 (AI Output Boundary Rule), each finding was re-verified against the live code before any fix — several of the original claims turned out to be inaccurate or overstated once checked against real call sites and actual code paths. This document records what was verified, what was fixed, what was deferred (and why), and what tests now guard each change.

Evidence tiers used below follow motto_v3 §0.5: Tier 1 = static inspection, Tier 2 = targeted test passed, Tier 3 = integration/e2e verified, Tier 4 = runtime/manual behavior observed.

---

## Fixed

### 1. Library tooltip opened every image file with PIL on every list refresh
**File:** [desktop_app/library/storage.py](../../desktop_app/library/storage.py) — `LibraryItem.tooltip_text`
**Verified (Tier 1):** Confirmed both save paths (`save_png_to_library`, `save_image_to_library`) already write `image_size`/`image_mode` into the JSON metadata sidecar at save time. `tooltip_text` was nonetheless re-opening the file with `PIL.Image.open()` unconditionally — an O(n) PIL decode on every `_refresh_library_list()` call.
**Fix:** Read dimensions from `self.metadata["image_size"]` when present; fall back to a PIL open only for legacy items saved without that field.
**Tests (Tier 2):** [desktop_app/tests/test_library_storage.py](../../desktop_app/tests/test_library_storage.py) — asserts zero `PIL.Image.open` calls when metadata is cached, and correct fallback behavior when it's missing.

### 2. `list_items()` parsed every sidecar before sorting and truncating (superseded, see 2026-07-01 addendum below)
**File:** [desktop_app/library/storage.py](../../desktop_app/library/storage.py) — `list_items`
**Verified (Tier 1):** `os.listdir` + JSON sidecar parse **for every file**, then sort, then truncate to `limit` — O(total files) JSON-parse work to return O(limit) results.
**Original decision (superseded):** deferred as not worth a manifest index. Manifest indexing is still rejected (see addendum), but the O(n)-parse-to-return-O(limit) waste itself was independently fixable without one — see addendum for the actual fix landed.

### 3. `on_preview()` ran extraction + backend sync + quality analysis synchronously on the UI thread
**Files:** [desktop_app/views/main_window_parts/extraction.py](../../desktop_app/views/main_window_parts/extraction.py) (`on_preview`, new `_on_preview_worker_finished`/`_on_preview_worker_error`), [desktop_app/views/main_window_parts/extraction_utils.py](../../desktop_app/views/main_window_parts/extraction_utils.py) (new `run_signature_preview`)
**Verified (Tier 1 + Tier 4):** `process_selection`/`process_selection_kmeans` (cv2 thresholding or K-Means), `_persist_selection_to_backend` (synchronous HTTP call), and `analyze_quality` all ran inline on the Qt UI thread. This is a high-risk path per motto_v3 §0.5 ("extraction and normalization pipelines").
**Fix:** Extracted the pure, Qt-free `run_signature_preview()` function (extraction_utils.py) and dispatched it via the codebase's existing `AsyncRunner` + `QThreadPool` pattern (already used for backend health checks — reused rather than inventing a parallel mechanism, per motto_v3 §11). A monotonic `_preview_request_id` guards against a stale (superseded) result being applied if two preview requests overlap. All failure modes (extraction failure, quality-analysis failure, best-effort backend-sync failure) are captured inside the returned dict rather than raised, so there is exactly one delivery path back to the UI thread.
**Risk-based verification performed (motto_v3 §0.6, high-risk path):**
  - Idempotency / stale-result handling: `_preview_request_id` guard, tested directly.
  - Partial failure: quality-analysis failure still returns the successfully extracted PNG (tested).
  - Backend-sync failure: caught inside the worker, never fails the local preview (tested).
  - Real thread-pool round trip observed end-to-end (Tier 4).
**Tests:** [desktop_app/tests/test_preview_worker.py](../../desktop_app/tests/test_preview_worker.py) (7 tests: pure-function success/failure paths, stale-result guard, real `QThreadPool` round trip).

### 4. Dead duplicate `class SignatureExtractor` silently broke forensic watermarking
**File:** [desktop_app/processing/extractor.py](../../desktop_app/processing/extractor.py)
**Discovered while verifying item 3** (same file/class touched for the threading fix — in blast radius per motto_v3 §6.1). The module defined `class SignatureExtractor` twice; Python silently used the second definition, so the live class never set `self.watermarker` / `self.original_path`. `process_selection_kmeans`'s watermark step referenced both, always raised `AttributeError`, and the exception was swallowed by a broad `except Exception` logged as "Watermarking failed" — meaning **forensic-mode signature exports were never actually watermarked**, silently, since this code was introduced.
**Fix:** Removed the dead class. Added `self.watermarker = WatermarkEngine()` to the live class's `__init__`. Replaced `self.original_path` (never set anywhere) with `session.file_path` (already tracked per-session, and correct for concurrent sessions — the old attribute would have been wrong for concurrent forensic exports even if it had existed).
**Tests (Tier 2):** [desktop_app/tests/test_extractor.py](../../desktop_app/tests/test_extractor.py) — decodes the LSB-embedded watermark payload from the K-Means output and asserts it round-trips correctly, plus general session/processing/quality tests (this module had zero prior test coverage).

### 5. PDF signature-field detection: no user feedback during the blocking call
**File:** [desktop_app/pdf/viewer.py](../../desktop_app/pdf/viewer.py) — `find_signature_fields`
**Verified (Tier 1):** `detect_page()` renders the current page via pypdfium2 at `scale=2.0` and runs OpenCV contour heuristics — genuine synchronous CPU/IO work triggered directly from a button click.
**Original decision (superseded, see 2026-07-01 addendum below):** partial fix only (wait cursor + disabled button) — full async was deferred pending explicit user sign-off, since it would change `place_signature_on_detected_field`'s synchronous `bool` contract.
**Tests (Tier 2):** [desktop_app/tests/test_pdf_field_detection.py](../../desktop_app/tests/test_pdf_field_detection.py) — button/cursor restored on both success and detector-exception paths.

### 6. PDF page bitmap re-rendered from scratch on every zoom/page-navigation, even revisits
**File:** [desktop_app/pdf/viewer.py](../../desktop_app/pdf/viewer.py) — `_render_current_page`, `open_pdf`, `close_pdf`
**Verified (Tier 1):** `PDFRenderer.render_page` does a full pdfium bitmap render (~150 DPI × zoom) + PIL conversion + QImage/QPixmap construction, unconditionally, on every page switch and zoom change — including returning to a page/zoom combination already rendered moments earlier.
**Fix:** Added a bounded LRU cache (`_page_render_cache`, cap 12 entries) keyed by `(page_num, round(zoom_level, 4), dpi)`. Cache is cleared on `open_pdf` (new document — entries are page-content-specific) and `close_pdf`. Verified no other code path mutates the underlying `QPixmap` in place (`PDFPageView.set_page` only stores/paints it), so sharing cached instances across repeated displays is safe.
**Memory trade-off (see item 8 below):** the cap of 12 was chosen deliberately to bound worst-case memory (~25–75MB depending on zoom/page size), not left unbounded.
**Tests (Tier 2):** [desktop_app/tests/test_pdf_render_cache.py](../../desktop_app/tests/test_pdf_render_cache.py) — revisit-hits-cache, zoom-change-misses-then-hits, cache cleared on new document, cache bounded across many zoom levels.

### 7. Backend re-read the same uploaded image from disk on every threshold-tweak request
**File:** [backend/app/services/extraction.py](../../backend/app/services/extraction.py) — `render_signature_png`, new `_read_image_cached`
**Verified (Tier 1):** `cv2.imread(str(file_path))` unconditionally on every call, no caching. Note: the desktop app's interactive extraction path is now fully local (`SignatureExtractor` in-process) and does **not** currently call this backend endpoint for interactive tuning — `desktop_app/api/client.py`'s `process_image` exists but has no production caller. This endpoint remains reachable by any API consumer doing interactive threshold tuning over HTTP, so the fix is still a real, low-risk, contract-preserving improvement, not a fix for a currently-hot path in this specific desktop client.
**Fix:** Added an `(resolved_path, mtime)`-keyed bounded LRU cache (cap 32). Keying on mtime means a file replaced at the same path (e.g., a re-upload reusing a session id) automatically invalidates the stale entry — addresses the "can stale data produce incorrect user-visible behavior" check from motto_v3 §0.6. Cached arrays are marked `writeable = False` since callers must treat them as read-only when shared across concurrent requests (FastAPI runs sync `def` routes in a thread pool).
**Tests:** added to the **canonical existing** [tests/test_extraction_service.py](../../tests/test_extraction_service.py) (a duplicate file was initially created at the wrong path and removed — see "Process note" below) — cache hit, mtime-based invalidation, read-only contract, and the realistic "four threshold tweaks → one disk read" scenario.

### 8. Redundant QImage→QPixmap conversion on every selection-drag frame
**Files:** [desktop_app/widgets/image_view.py](../../desktop_app/widgets/image_view.py) (new `ImageView.set_pixmap`), [desktop_app/views/main_window_parts/extraction.py](../../desktop_app/views/main_window_parts/extraction.py) (`on_selection_changed`)
**Verified (Tier 1):** `on_selection_changed` (fires on every selection-rect update, i.e. every mouse-move during a drag) converted the cropped `QImage` to a `QPixmap` once for `_current_crop_preview_pixmap`, then called `preview_view.set_image(cropped)`, which internally performed the **same conversion again** on identical data.
**Fix:** Added `ImageView.set_pixmap(pixmap)` for callers that already hold a converted `QPixmap`; `on_selection_changed` now reuses `_current_crop_preview_pixmap` instead of re-converting.
**Tests (Tier 2):** [desktop_app/tests/test_image_view.py](../../desktop_app/tests/test_image_view.py) — asserts `set_pixmap` triggers zero additional `QPixmap.fromImage` calls; `set_image` still converts correctly for callers that only have a `QImage`.

---

## Investigated, no fix needed (original claims did not hold up)

### 9. "Overlay pixmap re-scaled every preview frame" — inaccurate
**File:** `extraction.py` — `_build_overlay_preview_pixmap`
Verified this runs once per **completed** extraction result (called from `_on_process_finished`, which now only fires once per debounced, now-async preview), not per UI frame. The overlay PNG content differs on every real call (it's a new extraction result each time), so a size-keyed cache would never hit — the original "cache the scaled overlay" suggestion doesn't apply to how this function is actually invoked. No action needed; already benefits from item 3's UI-thread offload.

### 10. "Grayscale conversion duplicated across process_selection/analyze_quality" — real but not worth the risk
`process_selection`/`process_selection_kmeans` and `analyze_quality` each independently crop and `cv2.cvtColor` the same region. This is a real, small (~1–3ms typical) duplicate computation. Sharing a precomputed grayscale buffer would require changing the internal shape of `SignatureExtractor`'s extraction API — a high-risk path per motto_v3 §0.5 — for a saving that no longer affects UI responsiveness now that the whole pipeline runs off the UI thread (item 3). Deferred per motto_v3 §0.13 (scope control): the risk of touching this contract isn't justified by the benefit.

### 11. "Stylesheet rebuild on every pane click costs 50–100ms" — false
`_update_pane_borders` sets three short (~10-line) QSS strings on up to three widgets. This is sub-millisecond in practice; the original claim's magnitude was fabricated/unverified. No action needed.

### 12. "Audit log lookup is O(n) — fix with glob" — the proposed fix wouldn't help
`get_audit_logs_for_pdf` does `os.listdir` + filename prefix match. Switching to `glob.glob` was the originally suggested fix, but `glob` also does a full `readdir` + pattern match in userspace — it is the same O(n) with no complexity improvement, just cosmetically different code. A genuine fix would need a directory-per-PDF or manifest structure, not justified for realistic local audit-log volume (dozens to low hundreds of files per user). Deferred with corrected reasoning; not implemented.

### 13. "PDF fully loaded into memory, 50–200MB per 100-page document" — not consistent with pypdfium2's architecture
Verified pypdfium2's `PdfDocument` opens the file and parses structure at open time but does not eagerly decode/render every page into memory; individual pages are rasterized on demand via `page.render()`, and this app only ever renders `self.current_page` at a time (now plus a capped 12-entry cache from item 6). No fix applied since no real problem was confirmed. The actual relevant memory consideration going forward is the new render cache's bound (item 6) — a deliberate, documented cap, not unbounded growth.

---

## Process note: duplicate test file

While adding tests for item 7 (backend image cache), a new `backend/tests/test_extraction_service.py` was initially created without first checking for an existing canonical test file. A canonical `tests/test_extraction_service.py` already existed at the repo root covering the same module. Per the project's no-duplicate-routes/no-parallel-truth-sources principle (applied here to test files), the duplicate was deleted and its test cases were merged into the existing canonical file instead. Lesson: always check the root `tests/` directory (this repo's `pytest.ini` sets `testpaths = tests`) before creating a new test file for a backend module.

---

## Test summary

All new/modified tests pass; full existing suites re-run with no regressions.

```
tests/ (root, excluding e2e):                53 passed
desktop_app/tests/ (full suite):            123 passed, 3 skipped (pre-existing, unrelated —
                                             require a running Qt event loop for QTimer.singleShot chains)
```

New test files added:
- `desktop_app/tests/test_extractor.py` (extractor.py had zero prior coverage)
- `desktop_app/tests/test_library_storage.py` (storage.py had zero prior coverage)
- `desktop_app/tests/test_preview_worker.py`
- `desktop_app/tests/test_pdf_render_cache.py`
- `desktop_app/tests/test_image_view.py`
- Extended `tests/test_extraction_service.py` (canonical, pre-existing) and `desktop_app/tests/test_pdf_field_detection.py` (canonical, pre-existing)

## Remaining open items / follow-ups (as of initial pass, superseded — see addendum)

1. ~~Item 5 (PDF field detection async conversion)~~ — done, see addendum.
2. ~~Item 2 (library manifest index)~~ — the O(n)-parse issue is fixed without a manifest; see addendum.
3. No profiling tool (e.g. `cProfile`, `py-spy`) was run in this session to get exact millisecond measurements for any of the fixed items; all "Verified" claims above are Tier 1 (static inspection) plus Tier 2 (targeted tests) and, for item 3, Tier 4 (real thread-pool round trip observed). If precise before/after timings are needed for a future decision, that would require a dedicated profiling pass — flagged here rather than asserting numbers that weren't measured. Still open.

---

## Addendum (2026-07-01, same day): closing the two deferred items + one new finding

User explicitly authorized proceeding on both deferred items. Asked specifically about item 2 (library manifest) given it contradicted this doc's own recommendation; answer was "best/long-term/first-principles/motto_v3 aligned" — decision reasoning below.

### Item 5, closed: PDF field-detection is now genuinely async

**Files:** [desktop_app/pdf/viewer.py](../../desktop_app/pdf/viewer.py) (`find_signature_fields`, `place_signature_on_detected_field`, new `_place_on_best_field_candidate`, `_on_field_detect_finished`, `_on_field_detect_error`), [desktop_app/views/main_window_parts/pdf.py](../../desktop_app/views/main_window_parts/pdf.py) (`_on_pdf_find_fields`, `_on_pdf_place_on_field`), new [desktop_app/widgets/async_utils.py](../../desktop_app/widgets/async_utils.py).

**Layering fix first:** `AsyncRunner`/`run_async` lived in `views/main_window_parts/extraction_utils.py`, but `pdf/viewer.py` needed the same dispatch primitive and `pdf/` depending on `views/main_window_parts/` would be a backwards layering dependency (views/ is built on top of pdf/, not the reverse). Moved the generic (non-extraction-tab-specific) parts to `desktop_app/widgets/async_utils.py` — a location both packages can validly depend on (`pdf/viewer.py` already imports `ModernMacButton` from `desktop_app.widgets`) — and re-exported from `extraction_utils.py` for backward compatibility. Also added a small `dispatch(runner)` helper to remove the `QRunnable.create(...)/setAutoDelete/thread_pool.start(...)` boilerplate that was duplicated at both existing call sites (health check, preview worker) plus the new one.

**Re-scoped the contract change after re-checking every real caller** (the original deferral cited "3 call sites" from a first pass that wasn't exhaustive):
- `find_signature_fields()` now dispatches `detector.detect_page()` via `AsyncRunner` + `dispatch()`, taking `silent: bool` (suppress the "Fields Detected"/"No Fields Found" dialogs) and `on_complete: Callable[[List[Dict]], None]`. Handles the case where the user navigates to a different page while detection for the previous page is still in flight — the result is stored under its own page index and does not overwrite the now-current page's candidates.
- `place_signature_on_detected_field()` keeps its **exact synchronous behavior** when `field_candidates` are already cached for the current page (the common case — most calls hit this branch) — this covers two of the three originally-cited call sites (`viewer.py`'s own `_on_page_clicked`, and the existing test `test_place_signature_on_detected_field`) with **zero behavior change**, verified by re-running those tests unmodified. Only the "not yet detected" branch is now async: returns `None` immediately and delivers the real result via `on_complete`.
- The one call site that actually depended on the old synchronous "detect-then-place" behavior — `desktop_app/views/main_window_parts/pdf.py:_on_pdf_place_on_field` — was updated to pass `on_complete` instead of checking a synchronous return value. `_on_pdf_find_fields` had the same latent bug (checked `field_candidates` immediately after calling the now-async `find_signature_fields()`) and was fixed the same way.

**Risk-based verification (motto_v3 §0.6):** stale-result handling for page navigation during in-flight detection (tested); failure path always restores button/cursor via the error-signal handler (tested, matches the existing `finally`-based restoration semantics); synchronous fast path provably unchanged (existing test passes unmodified).

**Tests:** extended [desktop_app/tests/test_pdf_field_detection.py](../../desktop_app/tests/test_pdf_field_detection.py) (async button/cursor round trip, detector-failure round trip, new detect-then-place-async test, new synchronous-guard-stays-synchronous test) and new [desktop_app/tests/test_async_utils.py](../../desktop_app/tests/test_async_utils.py) for the relocated shared helper.

**New finding surfaced while tracing every caller (not in the original 12):** `_detect_signature_fields_silent()` — a *third*, previously-unlisted synchronous detection entry point — is called from `_resolve_signature_placement_rect` and `_compute_bulk_signature_rect_for_target` in `desktop_app/views/main_window_parts/pdf.py`, used by **bulk/template signature placement in "adaptive" mode**. If a bulk-apply loop calls this once per target page, a multi-page document means N sequential synchronous single-page detections — worse than the single "Find Fields" button case, potentially several seconds for a 10–20 page document. **Not fixed in this pass.** Converting it requires either a per-page async worker chain with progress reporting, or batching all N page detections before applying any placement — a materially different, higher-risk shape of change (bulk/template signing is itself explicitly a high-risk workflow per motto_v3 §0.5) than the single-page button case just converted, and deserves its own scoped design rather than being folded into this change under time pressure. Flagged here per motto_v3 §0.13 (scope control: pause and report rather than silently rush or silently skip) — **needs an explicit decision from the user** on whether/when to take this on.

### Item 2, closed differently than either original option: bounded scan instead of a manifest

**File:** [desktop_app/library/storage.py](../../desktop_app/library/storage.py) — `list_items`

**Why a manifest index was rejected on first principles, not just "no evidence of scale":** a manifest/index would be a **second source of truth** for metadata the filesystem (directory + per-item JSON sidecars) already owns correctly. For a local, single-user store that can be touched out-of-band (a sync folder, Finder, crash recovery mid-write), the directory listing has to stay authoritative regardless — so a manifest doesn't remove the need to reconcile against disk, it just adds a second thing that can drift from it (staleness, corruption, crash-consistency), which is exactly the "duplicate/parallel source of truth" pattern this project's engineering rules warn against. The only architecture that would genuinely retire the directory-as-source-of-truth model is a real embedded database (e.g. SQLite) as the canonical store — a much larger migration, unjustified by any current evidence and itself a textbook case of premature/speculative engineering for this data volume.

**What was actually wrong, independent of scale:** `list_items(limit)` parsed every sidecar for every file in the directory, sorted, *then* truncated to `limit` — O(total files) JSON-parse work to return O(limit) results, regardless of how large the library ever gets. That's a genuine algorithmic defect, not a scale question.

**Fix:** two-pass — first pass stats every file (`os.path.getmtime`, filesystem metadata only, no content read) to establish recency order; second pass parses a JSON sidecar only for the top `limit` entries that will actually be returned. Bounded cost regardless of library size, no new failure modes, no second source of truth, no manifest to keep in sync.

**Tests (Tier 2):** new test in [desktop_app/tests/test_library_storage.py](../../desktop_app/tests/test_library_storage.py) — with 20 files on disk and `limit=5`, asserts exactly 5 JSON sidecars are opened (not 20), and that they're the 5 most-recently-modified.

### Updated test summary (after this addendum)

```
tests/ (root, excluding e2e):                53 passed
desktop_app/tests/ (full suite):            130 passed, 3 skipped (pre-existing, unrelated —
                                             require a running Qt event loop for QTimer.singleShot chains)
```

New files added in this addendum:
- `desktop_app/widgets/async_utils.py` (moved AsyncRunner/run_async here; extraction_utils.py re-exports)
- `desktop_app/tests/test_async_utils.py`

Extended in this addendum: `desktop_app/tests/test_pdf_field_detection.py`, `desktop_app/tests/test_library_storage.py`, `desktop_app/views/main_window_parts/pdf.py`, `desktop_app/pdf/viewer.py`, `desktop_app/views/main_window_parts/extraction.py` (now uses the shared `dispatch()` helper instead of duplicated thread-pool boilerplate), `desktop_app/library/storage.py`.

### Remaining open items (as of the first addendum, superseded — see second addendum)

1. ~~Bulk/template adaptive-mode field detection (`_detect_signature_fields_silent`)~~ — done, see second addendum below.
2. No profiling tool was run for exact millisecond measurements; all claims are Tier 1–4 as stated per item above. Still open.

---

## Addendum 2 (2026-07-01, same day): bulk/template field-detection batching, scoped and built

User explicitly authorized scoping and building the bulk-detection fix flagged in addendum 1.

### Scoping: two distinct synchronous loops, both traced to their real call sites

**Flow A — `_on_pdf_template_apply_to_pages`** (`desktop_app/views/main_window_parts/pdf.py`): user picks a template + target pages via `BulkSignDialog`, confirms, then a synchronous `for page_num in target_pages: self._apply_template_to_target_page(...)` runs. When `template.use_field_anchor` is set, `_apply_template_to_target_page` → `_resolve_signature_placement_rect` → `_detect_signature_fields_silent()` once per page.

**Flow B — the bulk branch of `_on_pdf_signature_placed`**: triggered when the user places a signature on a "source" page while in bulk-sign mode; a synchronous `for target_page in target_pages: ... self._compute_bulk_signature_rect_for_target(use_same_pos=...)` runs. In "adaptive" mode (`not use_same_pos`), this also calls `_detect_signature_fields_silent()` once per page.

Both loops also call `self.pdf_viewer.goto_page(target_page)` per iteration — a structural requirement, not incidental: `PDFPageView` stores overlays/candidates per-page via `all_signatures`/`all_field_candidates` dicts keyed by the *current* page, so placing a signature on page K requires navigating to page K first. This meant the fix could not simply "make detection async" per page (that would still serialize N page-navigations with N async waits); it had to decouple *detection* from *navigation+placement* entirely: batch-detect every target page's fields in one background pass, then run the (now detection-free, fast) per-page navigate+place loop synchronously afterward.

### Fix

**New:** `PDFViewer.detect_fields_for_pages(page_indices, on_complete)` (`desktop_app/pdf/viewer.py`) — dispatches one `AsyncRunner`/`dispatch()` worker that loops `detector.detect_page()` over all requested pages and returns `{page_index: [candidates]}`. Per-page exceptions are caught and logged individually (`results[page_index] = []`) so one corrupt/unreadable page cannot abort detection for the rest of the batch — this **is** the failure-isolation behavior risk-based verification requires for a batch operation (motto_v3 §0.6: partial failure must be a first-class case, not an afterthought). Results are merged into `self.all_field_candidates` in place before `on_complete` fires.

**New:** `MainWindow._run_after_bulk_field_detection(pages, needs_detection, then_fn)` (`desktop_app/views/main_window_parts/pdf.py`) — shared by both flows. Runs `then_fn()` immediately when detection isn't needed (e.g. "same position" bulk mode never detects); otherwise shows a busy cursor (`QApplication.setOverrideCursor`, appropriate here since the operation is about to navigate across the whole document, unlike the single-page button's widget-scoped cursor) and a status-bar message, dispatches the batch, and calls `then_fn()` only once it completes.

**Changed contracts (additive, backward-compatible):** `_resolve_signature_placement_rect`, `_apply_template_to_target_page`, and `_compute_bulk_signature_rect_for_target` all gained a `skip_detection: bool = False` keyword. Default preserves the exact old synchronous single-page behavior (`_on_pdf_template_apply`, the single-placement path, are completely unaffected — verified by re-running existing tests unmodified). The two bulk loops now pass `skip_detection=True` after pre-populating `all_field_candidates` via the batch pass; the existing `goto_page()` → `_render_current_page()` → `_load_page_field_candidates()` chain automatically surfaces the pre-computed candidates for whatever page the loop navigates to next, so no other code needed to change.

**Tests:** [desktop_app/tests/test_pdf_bulk_field_detection.py](../../desktop_app/tests/test_pdf_bulk_field_detection.py) (6 tests) — batches N pages into one worker call (not N), isolates a per-page detector exception without losing other pages' results, de-duplicates repeated page indices, no-PDF-open short-circuits synchronously, `_run_after_bulk_field_detection` skips the dispatch entirely when not needed, and an end-to-end regression test against a real `MainWindow` + `PDFViewer` proving `_apply_template_to_target_page` in a 4-page bulk apply calls `detect_page` exactly 4 times total (matching the old per-page total, so no wasted extra detection work) dispatched from **one** `detect_fields_for_pages` call rather than 4 separate synchronous `_detect_signature_fields_silent()` calls, and that the old synchronous method is never invoked in this path.

### New finding surfaced while verifying this fix: `all_field_candidates` coordinate-space bug (not fixed — separate bug class, flagged for a decision)

While confirming that pre-computed batch candidates survive the `goto_page()` navigation correctly, traced `_save_page_field_candidates()` (`desktop_app/pdf/viewer.py`) and found: `_load_page_field_candidates()` transforms `all_field_candidates[page]` from **PDF-point space** (what `SignatureFieldDetector` produces) into `page_view.field_candidates` in **pixel/view space** (with a Y-axis flip, since PDF points are bottom-up), for display. But `_save_page_field_candidates()` — called by `goto_page()`/`previous_page()`/`next_page()` on **every** page navigation, unconditionally, unrelated to bulk operations — copies `page_view.field_candidates` (pixel/view space) straight back into `all_field_candidates[page]` with **no inverse transform**. This overwrites the correct point-space data with pixel-space data. The next time that page is loaded, `_load_page_field_candidates()` applies the point→pixel transform *again*, on data that is already pixel-space, producing doubly-transformed (visibly wrong) field-overlay positions.

This is a real, pre-existing, user-visible correctness bug: browse to a page, detect/place fields, navigate away and back, and detected-field overlays can be mispositioned. It is **not caused by, and does not affect, the bulk-detection fix above** — the batch pass always freshly overwrites `all_field_candidates[page]` with correct point-space data for every page in its batch, which incidentally self-heals any prior corruption for those specific pages, but does nothing for the general single-page navigation path. Per motto_v3 §6.1 (blast radius: adjacent-but-unrelated pre-existing bugs should be triaged and reported, not silently fixed as scope creep or silently ignored now that they're known): **not fixed in this pass.** It's a different bug class (coordinate-space correctness, not performance) requiring its own scoped fix across every read/write of `all_field_candidates`, and deserves its own explicit decision rather than being folded into a performance change under time pressure.

**Proof/repro (static, Tier 1):** `desktop_app/pdf/viewer.py` — compare the transform in `_load_page_field_candidates` (lines ~759-762, point→pixel with Y-flip) against the raw copy in `_save_page_field_candidates` (lines ~719-720, no transform). No test currently exercises "detect fields, navigate away, navigate back, check overlay position," which is exactly why this went unnoticed.

### Updated test summary (after this addendum)

```
tests/ (root, excluding e2e):                53 passed
desktop_app/tests/ (full suite):            136 passed, 3 skipped (pre-existing, unrelated)
```

New files added in this addendum:
- `desktop_app/tests/test_pdf_bulk_field_detection.py`

### Remaining open items (as of addendum 2, superseded — see addendum 3)

1. ~~`all_field_candidates` coordinate-space bug~~ — fixed, see addendum 3.
2. No profiling tool was run for exact millisecond measurements; all claims are Tier 1–4 as stated. Still open.

---

## Addendum 3 (2026-07-01, same day): coordinate-space bug fixed by removing the dead code that caused it

User authorized fixing this. Root-caused rather than patched.

**Why removal, not an inverse-transform patch:** traced every write path to `page_view.field_candidates` and confirmed it is *never mutated in place* anywhere in the codebase — it's set wholesale via `set_field_candidates()`/`clear_field_candidates()` and only ever *read* (for click hit-testing and `selected_field_candidate_index` lookups). There was therefore never anything for `_save_page_field_candidates()` to legitimately save — the user cannot reposition, resize, or edit a detected field candidate in the view. The method was pure liability: it existed only to copy the display projection back over the authoritative point-space data, corrupting it. Adding an inverse transform would have "fixed" the symptom while preserving a pointless, risk-bearing round-trip for data that never needed round-tripping — the correct long-term fix (motto_v3 §11: prefer simplification over layering; §21: code is evidence, not a boundary) is to delete it, making `all_field_candidates` the single, exclusively-written-by-detection source of truth it was always supposed to be.

**Change:** removed `_save_page_field_candidates()` entirely, including its 4 call sites: 3 in `previous_page()`/`next_page()`/`goto_page()` (all navigation paths — the bug's actual trigger), and 1 inside `_detect_signature_fields_silent()` where it was calling save immediately before unconditionally overwriting the same data on the next line — already fully dead there regardless of the bug. `_save_page_signatures()` (a similarly-named but unrelated method for user-*placed* signatures, which genuinely are repositionable and do need saving) was left untouched — confirmed it doesn't share this bug since signature dicts are stored/read in one consistent coordinate space with no point↔pixel conversion anywhere in that path.

**Tests:** new [desktop_app/tests/test_pdf_field_detection.py](../../desktop_app/tests/test_pdf_field_detection.py)`::test_field_candidate_positions_survive_page_navigation` — detects fields on page 0 of a 2-page PDF, records the view-space overlay positions, navigates to page 1 and back to page 0, and asserts the positions are byte-identical (not double-transformed). This is the first test in the suite that exercises "detect → navigate away → navigate back → check overlay position," which is exactly why the bug went unnoticed until now.

### Updated test summary (final, after all three addenda)

```
tests/ (root, excluding e2e):                53 passed
desktop_app/tests/ (full suite):            137 passed, 3 skipped (pre-existing, unrelated)
```

### Remaining open items (final)

1. No profiling tool was run for exact millisecond measurements; all claims in this document are Tier 1–4 as stated per item. If precise before/after timings are needed for a future decision, that requires a dedicated profiling pass.
