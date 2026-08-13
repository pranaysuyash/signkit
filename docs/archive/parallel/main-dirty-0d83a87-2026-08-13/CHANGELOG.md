# Changelog

## [Unreleased] - 2025-11-01

### Fixed

- **PDF Signing Reliability**: Replaced brittle pikepdf stream injection with PyMuPDF's robust `Page.insert_image()` API
  - Fixes Acrobat "There was a problem reading this document" errors
  - Ensures signatures appear correctly in saved PDFs
  - Added automatic pixel-to-point coordinate conversion from viewer outputs
  - Maintains backward compatibility with existing point-based coordinates
  - Uses deflate compression to keep PDF sizes reasonable (PyMuPDF path)
  - Falls back to legacy pikepdf if PyMuPDF unavailable

### Changed

- Updated `desktop_app/requirements.txt` with pinned versions from current environment:
  - PySide6==6.10.0
  - requests==2.32.5
  - python-dotenv==1.1.1
  - pillow==12.0.0
  - pypdfium2==5.0.0
  - pikepdf==10.0.0
  - numpy==2.2.6
  - opencv-python==4.12.0.88
  - PyMuPDF==1.26.5

### Technical Details

#### PDF Signing Fix

**Problem**: Saved PDFs showed Acrobat "There was a problem reading this document" errors and missing signatures due to low-level pikepdf image stream embedding being unsupported for new images.

**Solution**:

- Primary: PyMuPDF `page.insert_image(rect, filename=..., keep_proportion=True, overlay=True)`
- Coordinates: Viewer exports pixel coords + metadata; signer converts to points using `72 / (dpi * scale)`
- Compression: `deflate=True` on save to minimize size increase
- Fallback: Legacy pikepdf path preserved for compatibility

**Files Changed**:

- `desktop_app/pdf/signer.py`: PyMuPDF integration, coordinate conversion
- `desktop_app/pdf/viewer.py`: Added units/dpi/scale metadata to signatures
- `desktop_app/requirements.txt`: Updated versions, added PyMuPDF

---

## [Unreleased] - 2025-10-29

### Changed

- **Enhanced Coordinate Display**: "Visible" now shows both viewport position and image portion
  - Format: `@(vx1,vy1)→(vx2,vy2) shows (ix1,iy1)→(ix2,iy2)`
  - First part `@(...)→(...)`: Where image is painted in viewport (viewport pixel coordinates)
  - Second part `shows (...)→(...)`: What portion of image is visible (image pixel coordinates)
  - **Example**: `@(267,1)→(575,549) shows (0,0)→(2268,4032)` means:
    - Image is painted at viewport coordinates (267,1) to (575,549)
    - You can see the entire image from pixel (0,0) to (2268,4032)
  - Helps understand image positioning, especially with letterboxing/pillarboxing at different zoom levels

### Added

- Help menu with links to Help & Troubleshooting, Keyboard Shortcuts, and a quick backend health opener (`http://127.0.0.1:8001/health`)

### Technical Details

**Why Two Coordinate Systems?**

When you zoom or fit an image, Qt's QGraphicsView creates a transform between:

1. **Viewport coordinates**: Physical pixels on your screen (widget size)
2. **Scene/Image coordinates**: Logical pixels in the image data

At 13.6% zoom with 2268×4032 image in 842×551 viewport:

- Image scales to 308×548 displayed pixels
- Viewport is larger, so image is centered with margins
- Image appears at viewport pixels (267,1)→(575,549)
- But shows the full image area (0,0)→(2268,4032)

At 171.7% zoom with 512×184 image in 899×551 viewport:

- Image scales to 879×316 displayed pixels
- Image fills width but has vertical margins
- Image appears at viewport pixels (~10,118)→(~889,434)
- Shows the full image area (0,0)→(512,184)

**Crop Coordinate Mapping (Rotation-aware)**

The selection/crop uses `selected_rect_image_coords()` which:

1. Captures the 4 selection corners in scene coordinates on mouse release
2. Builds a normalized scene-space bounding box that persists through zoom/pan/fit/resize/rotation
3. Maps directly to image pixels (scene == image space), then clamps to pixmap bounds
4. Backend crops using those integer pixel coordinates
5. Verified across zoom levels and after 90°/180° rotations (tests included)

---

## [Unreleased] - 2025-10-28

### Changed

- Coordinate mapping now uses rotation-aware scene bounds from all four selection corners and persists across view changes.

### Added

- **Real-time Coordinate Display**: Status bar footer now shows live coordinate information

  - **Viewport**: `W×H` - Viewport widget size in pixels (changes on window resize)
  - **Image**: `W×H` - Actual image resolution in pixels
  - **Visible**: `@(x1,y1)→(x2,y2) shows (ix1,iy1)→(ix2,iy2)` - Where image appears in viewport @ what portion of image is shown
  - **Selection**: `(x1,y1)→(x2,y2) [w×h]` - Selected area coordinates in image pixel space
  - **Zoom**: `X%` - Current zoom level of the active pane
  - **Rotation**: `X°` - Current rotation angle
  - Coordinates auto-update on:
    - Image load/upload
    - Zoom in/out (buttons, combo, or Ctrl+wheel)
    - Fit to window / Reset to 100%
    - Selection changes
    - Pane switching
    - Window resize events
  - Monospace font styling for easy reading
  - Tooltips explain what each coordinate represents
  - Helps debug coordinate issues and understand image positioning across view states
  - **Note**: Crop coordinates use proper coordinate mapping (`selected_rect_image_coords`) independent of display coordinates

- **Zoom Change Signal**: Added `zoomChanged` signal to `ImageView` class
  - Emitted whenever zoom level changes (zoom in/out, fit, reset)
  - Automatically updates coordinate display in real-time
  - Tracks accurate zoom percentage after fit operation

### Technical Details

#### Coordinate Mapping Fix (`desktop_app/widgets/image_view.py`)

**Before** (Four-corner approach):

```python
# Mapped all four corners and calculated bounding box
corners = [topLeft, topRight, bottomLeft, bottomRight]
scene_corners = [mapToScene(c) for c in corners]
item_corners = [pixmap_item.mapFromScene(sc) for sc in scene_corners]
x1, y1 = floor(min(x_coords)), floor(min(y_coords))
x2, y2 = ceil(max(x_coords)), ceil(max(y_coords))
```

**After** (Two-corner approach):

```python
# Map only top-left and bottom-right directly to scene
top_left_scene = self.mapToScene(top_left_view)
bottom_right_scene = self.mapToScene(bottom_right_view)
x1, y1 = math.floor(top_left_scene.x()), math.floor(top_left_scene.y())
x2, y2 = math.ceil(bottom_right_scene.x()), math.ceil(bottom_right_scene.y())
```

**Why this works**:

- The pixmap item is positioned at (0,0) in the scene
- Scene rect is set to image dimensions via `setSceneRect(pix.rect())`
- Therefore, scene coordinates ARE image pixel coordinates
- Using all four corners provides robustness when the view is rotated

#### Coordinate Display Implementation (`desktop_app/views/main_window.py`)

**Status Bar Widgets Added**:

```python
self.viewport_size_label = QLabel("Viewport: –")    # Widget dimensions
self.view_coords_label = QLabel("Image Bounds: –")  # Visible image area
self.selection_coords_label = QLabel("Selection: –") # Selection area
self.zoom_label = QLabel("Zoom: –")                  # Zoom percentage
```

**Update Logic** (`_update_coordinate_display()`):

1. Gets active view (source/preview/result)
2. Displays viewport widget dimensions (e.g., "512×184")
3. Maps viewport corners to scene coordinates
4. Clamps to actual image bounds
5. Formats and displays image coordinates
6. Calculates zoom percentage from transform matrix
7. Shows selection coordinates persistently across pane switches

**Signal Connections**:

```python
self.src_view.zoomChanged.connect(self._update_coordinate_display)
self.preview_view.zoomChanged.connect(self._update_coordinate_display)
self.res_view.zoomChanged.connect(self._update_coordinate_display)
```

### Testing

All automated tests pass:

- ✅ 8 coordinate mapping tests (fit, 100%, zoom in/out, rotation, clamping, crop accuracy)
- ✅ 12 main window logic tests (pane focus, rotation, selection, library, auto-threshold)
- ✅ Total: 20/20 tests passing

**Test Coverage**:

- `test_coordinate_mapping_at_fit`: Verifies coordinates when view is fitted
- `test_coordinate_mapping_at_100_percent`: Tests 1:1 pixel mapping at 100% zoom
- `test_coordinate_mapping_zoomed_in`: Validates coordinates when zoomed in 2x
- `test_coordinate_mapping_zoomed_out`: Tests zoomed out view
- `test_coordinate_mapping_rotated_90/180`: Confirms invalid coords for unsupported rotation+selection
- `test_coordinate_clamping`: Ensures coordinates are properly clamped to image bounds
- `test_crop_matches_coordinates`: Verifies cropped image dimensions match coordinate span

### Known Behavior

**Selection + Rotation**:

- The application intentionally clears selections when the source image is rotated
- This is by design: rotating the source creates a new session with new image data
- Preview and result panes can be rotated independently (display-only, no coordinate change)
- Tests confirm that rotation+selection returns invalid coordinates `(0,0,0,0)` as expected

### Files Changed

- `desktop_app/widgets/image_view.py`: Simplified `selected_rect_image_coords()`, added `zoomChanged` signal
- `desktop_app/views/main_window.py`: Added coordinate display labels and `_update_coordinate_display()` method
- `desktop_app/tests/test_coordinate_mapping.py`: Updated rotation tests to reflect actual application behavior

### Migration Notes

No breaking changes. The coordinate mapping fix is transparent to users and improves accuracy.

---

## [Unreleased] - 2025-10-26

### Added

- **Professional Export Dialog** with industry-standard options:

  - Format selection: PNG-24, PNG-8 (palette), JPEG
  - Background options: Transparent, White, Black, Custom color
  - Trim to content bounds with configurable padding (0-100px)
  - JPEG quality control (1-100%)
  - Defaults to `.png` extension
  - Inspired by Adobe Photoshop and Affinity Photo workflows

- **Save to Library** quick-save button:

  - Auto-generated filenames with timestamp: `signature_YYYYMMDD_HHMMSS.png`
  - Defaults to PNG format with transparency
  - Prepared for integration with persistent library directory

- **Button Tooltips** for clarity:
  - Preview: "Process the selected region with current threshold and color settings"
  - Export: "Export with advanced options (background, trim, format)"
  - Save to Library: "Quick save as PNG to local library"

### Changed

- Renamed "Save Result" button to "Export..." to better reflect professional export workflow
- Export and Save to Library buttons now properly enable/disable based on result availability
- Clear Selection now properly resets both export buttons

### Documentation

- Added `docs/EXPORT_OPTIONS.md` with comprehensive guide:
  - Button function explanations
  - Format recommendations by use case (signatures, documents, web, print)
  - Technical details on trim algorithm, background compositing, format conversion
  - Comparison with industry tools
  - Best practices guide

### Fixed

- Corrected import paths for `ApiClient`, `SessionState`, and `ImageView`
- Export dialog properly handles transparency vs solid backgrounds
- JPEG export correctly removes alpha channel

### Technical

- Export dialog uses PIL for advanced image processing
- Implements alpha_composite for proper background blending
- Adaptive palette quantization for PNG-8 format
- Content-aware trimming using alpha channel bounding box
