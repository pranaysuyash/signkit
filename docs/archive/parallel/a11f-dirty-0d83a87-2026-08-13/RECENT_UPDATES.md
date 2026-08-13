# Recent Updates

**Last Updated:** June 23, 2026

## 📊 Update: Landing Page Refresh and Mobile Gallery Fix (June 23, 2026)

**Status:** ✅ Implemented and locally smoke-tested

Refreshed the SignKit landing page control variant to make the hero more polished and conversion-focused:

- Tightened the headline, added a trust strip, and improved the paper-style visual system.
- Fixed the in-page anchors so the footer `Screenshots` and `FAQ` links now resolve correctly.
- Swapped the weakest gallery image for a clearer workflow shot and added responsive `srcset` handling so mobile gets the smaller optimized screenshots.
- Applied the same control-variant refresh to `root.html` so `/` and `/root` stay visually aligned while keeping root-specific analytics intact.

**See:** [index.html](../index.html), [root.html](../root.html)

## 📊 Update: Capture Signature Crash Hardening (June 18, 2026)

**Status:** ✅ Implemented and tested

Hardened the webcam preview path so `Capture Signature` no longer depends on every frame being a perfect 3-channel BGR image:

- Normalized camera frames before rendering them into the preview widget.
- Wrapped the live preview timer slot in exception handling so unexpected camera data stays inside the dialog instead of crashing the app.
- Added regression tests for grayscale frames and unsupported frame shapes.

**See:** [desktop_app/views/main_window_parts/extraction.py](../desktop_app/views/main_window_parts/extraction.py), [desktop_app/tests/test_capture_dialog.py](../desktop_app/tests/test_capture_dialog.py), [docs/signature_capture_crash_issue_review_2026-06-18.md](./signature_capture_crash_issue_review_2026-06-18.md)

## 📊 Update: API Boundary Hardening From Feedback Review (June 17, 2026)

**Status:** ✅ Implemented and tested

Applied the long-term parts of the ChatGPT review to the desktop API boundary:

- Added typed response objects for login, upload, and processing contracts.
- Added typed API errors for validation, contract, auth, backend availability, and processing failures.
- Tightened `ApiClient` input validation for base URLs, uploads, crop rectangles, thresholds, and color values.
- Moved session mutation for login back into the caller layer instead of the transport method and gave `SessionState` explicit setters.
- Removed the last direct extraction-session writes from the UI workflow and switched the extraction flow to `SessionState` intent methods.
- Separated manual offline mode from observed backend reachability so transient health failures do not latch the client forever.
- Switched backend URL changes to the validated `ApiClient.update_base_url(...)` boundary instead of mutating the public field directly.
- Added client tests for invalid URLs, contract failures, selection validation, health recovery, and offline behavior.

**See:** [desktop_app/api/client.py](../desktop_app/api/client.py), [desktop_app/api/errors.py](../desktop_app/api/errors.py), [desktop_app/views/login_dialog.py](../desktop_app/views/login_dialog.py), [desktop_app/tests/test_api_client.py](../desktop_app/tests/test_api_client.py)

## 📊 Latest: Capture Input + Positioning Pass (June 17, 2026)

**Status:** ✅ Implemented

Added a camera capture path for environments where users cannot upload files:

- Added `Capture Signature` button and `Ctrl+Shift+C` shortcut in the extraction UI.
- Introduced a webcam capture dialog with live preview and frame capture.
- Captured image is fed through the existing `_load_image_from_path` path so extraction, auto-detection, preview, and export behavior stay identical to file uploads.
- Updated copy in `index.html`, `purchase.html`, and `web/live/index.html` to reflect launch pricing: `$29 launch` then `$39 lifetime`.
- Kept this on long-term architecture by reusing one extraction pipeline (no duplicate flow or separate contract).

**See:** [desktop_app/views/main_window_parts/extraction.py](../desktop_app/views/main_window_parts/extraction.py), [index.html](../index.html), [purchase.html](../purchase.html), [web/live/index.html](../web/live/index.html), [docs/PRICING.md](../docs/PRICING.md)

## 📊 Latest: ChatGPT UX Review Analysis (November 2, 2025)

**Status:** ✅ Analysis complete, ready for implementation

Received comprehensive UI/UX review from ChatGPT. Analysis complete with implementation plan.

**See:** [CHATGPT_UX_REVIEW_ANALYSIS_NOV_2_2025.md](./CHATGPT_UX_REVIEW_ANALYSIS_NOV_2_2025.md) and [IMPLEMENTATION_PLAN_CHATGPT_REVIEW_NOV_2_2025.md](./IMPLEMENTATION_PLAN_CHATGPT_REVIEW_NOV_2_2025.md)

**Top Priorities:**
1. ⚡ Async health check - Prevents UI freezes (2-3h)
2. ✅ Persistent health indicator - Infrastructure exists, needs wiring (1-2h)
3. 📦 Docs path fallback - Critical for distribution (1h)
4. 🦮 Accessibility labels - Screen reader support (30min)
5. ✅ Fix hardcoded URL - 5 minutes

---

## Previous Updates

### Problems Solved

### 1. Selection vs Pan Conflict ✅

**Issue**: When zoomed in, left-click tried to both select and pan, causing erratic behavior.

**Solution**:

- Added "Mode: Select" / "Mode: Pan" toggle button
- Selection mode (default): Left-click draws selection rectangle
- Pan mode: Left-click drags the view
- Middle-click always pans regardless of mode

**How to Use**: Click "Mode: Select" button to switch between modes, or use middle-mouse-button to pan anytime.

---

### 2. Image Orientation Fixed ✅

**Issue**: Photos taken on phone appeared rotated in the app (vertical image showed as horizontal).

**Solution**:

- Added EXIF metadata reading on image load
- Auto-rotates images based on camera orientation tag (0x0112)
- Handles all standard orientations (0°, 90°, 180°, 270°)
- Falls back to basic loading if EXIF parsing fails

**Result**: Source view now matches the image orientation you see in your photo viewer.

---

### 3. Preview/Result Panes Hidden Until Selection ✅

**Issue**: Preview and result areas took up screen space before any selection was made.

**Solution**:

- Crop preview and result panes start hidden
- Source view gets full window initially
- Panes appear automatically when you make a selection
- Hide again when selection is cleared

**Result**: More room to see and select from the source image.

---

### 4. Result Visibility Improved ✅

**Issue**: Transparent PNG output was hard to see against dark gray background.

**Solution**:

- Result view now has white background
- Crop preview also has white background with subtle border
- Transparency is now clearly visible (white shows through transparent areas)

**Result**: Much easier to see your extracted signature.

---

## What to Test

1. **Upload a vertical photo** (from phone):
   - Should appear correctly oriented in source view
2. **Zoom in (Ctrl+wheel or + button)**:
   - Click "Mode: Pan" button
   - Left-click-drag to pan around
   - Click "Mode: Select" button
   - Left-click-drag to make selection
3. **Make a selection**:
   - Preview and result panes should appear
   - Crop preview shows your selection on white background
   - Adjust threshold/color → result updates automatically
4. **Clear selection**:
   - Panes hide again
   - Full window for source view

---

## What's Next (Priority Order)

1. **Icons & Visual Polish** (1-2 hours)

   - Add emoji or QIcon to buttons (+, −, ↶, ↷)
   - Set app window icon
   - Optional: subtle color theme (blue accent for buttons)

2. **Rotate Buttons** (2-3 hours)

   - Add "Rotate ↶" and "Rotate ↷" buttons
   - Client rotates image in-memory
   - Re-uploads as new session
   - Updates source view

3. **Export Metadata** (1 hour)

   - "Export Metadata" button
   - Saves JSON with selection bbox, color, threshold, timestamp
   - Saves alongside PNG with same base filename

4. **REST API Docs** (1 hour)

   - Create `docs/API.md`
   - Document endpoints for browser extension developers
   - Include curl examples

5. **Auto-Detection Research** (4-6 hours)
   - Prototype contour-based signature detection
   - Test on 10-20 sample documents
   - Document accuracy and edge cases

---

## Run It

```bash
# Backend (if not running)
source .venv/bin/activate
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001

# Desktop app (new terminal)
source .venv/bin/activate
python -m desktop_app.main
```

For archived, one-off notes that were previously in the repository root, see `docs/ROOT_DOCS_INDEX.md`.

---

## Full Roadmap

See `docs/ROADMAP.md` for:

- Phase 2-8 features (processing options, integrations, deployment)
- Auto-recognition (OCR, signature detection)
- Deployment strategy (PyInstaller, Docker, Fly.io)
- Marketing plan (landing page, SEO, launch strategy)
- Success metrics and risk mitigation

---

**Questions? Issues?**  
Check the image attached showing your vertical document—confirm it loads correctly oriented now, and test the mode toggle when zoomed in.
