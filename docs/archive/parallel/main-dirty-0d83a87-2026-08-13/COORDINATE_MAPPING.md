# Coordinate Mapping System

## Overview

The Signature Extractor Desktop App uses a coordinate mapping system to translate user selections from the display viewport to actual image pixel coordinates. This document explains how the system works and the recent improvements made to ensure accuracy across all view states.

## Architecture

### Coordinate Spaces

The application works with three coordinate spaces:

1. **View Coordinates** (Widget space)

   - The pixel positions on the screen where the user draws their selection rectangle
   - Origin: Top-left corner of the `QGraphicsView` widget
   - Affected by: Window size, viewport size, scrollbars

2. **Scene Coordinates** (Logical space)

   - The abstract coordinate system used by `QGraphicsScene`
   - Origin: Top-left corner of the scene (set to image top-left at (0,0))
   - Affected by: View transformations (zoom, pan, rotation)
   - Units: Scene units (1:1 mapping to image pixels by design)

3. **Image Coordinates** (Pixel space)
   - The actual pixel positions in the source image
   - Origin: Top-left corner of the image (0,0)
   - Range: (0,0) to (width, height)
   - Units: Pixels

### Key Design Decision

**The scene coordinate system is intentionally aligned with image pixel coordinates.**

In `ImageView.set_image()`:

```python
pix = QPixmap.fromImage(image)
self._pixmap_item = self.scene().addPixmap(pix)
self.setSceneRect(pix.rect())  # Scene rect = image dimensions
```

The pixmap item is positioned at scene coordinate (0,0), and the scene rect is set to the image dimensions. This means:

- Scene coordinate (100, 50) = Image pixel (100, 50)
- No additional transformation needed
- Direct mapping from scene to image space

## Coordinate Mapping Implementation

### Method: `selected_rect_image_coords()`

Located in: `desktop_app/widgets/image_view.py`

#### Current Implementation (Rotation‑aware — Oct 2025)

```python
def selected_rect_image_coords(self) -> tuple[int, int, int, int]:
    if not self._pixmap_item or self._last_rect_scene_bounds.isNull():
        return (0, 0, 0, 0)

    bounds = self._last_rect_scene_bounds  # scene-space bbox from all 4 corners
    x1 = math.floor(bounds.left())
    y1 = math.floor(bounds.top())
    x2 = math.ceil(bounds.right())
    y2 = math.ceil(bounds.bottom())

    # Clamp to image bounds (scene == image space)
    img = self._pixmap_item.pixmap().rect()
    x1 = max(0, x1); y1 = max(0, y1)
    x2 = min(img.width(), x2); y2 = min(img.height(), y2)

    if x2 <= x1 or y2 <= y1:
        return (0, 0, 0, 0)
    return (x1, y1, x2, y2)
```

Selection persistence:
- On mouse release we capture the 4 selection corners in scene coordinates, build a normalized bounding box, and store it. This survives zoom, pan, fit, resize, and rotation.

Why it’s accurate:
- Scene is aligned to image pixels, so scene→image is 1:1.
- Bounding the 4 rotated corners covers off‑axis selection rectangles.
- Floor/ceil create an inclusive integer region matching the visual selection.

### Previous Implementation (Broken - Before 2025-10-28)

```python
# ❌ Old approach: Four-corner mapping
corners = [
    self._last_rect.topLeft(),
    self._last_rect.topRight(),
    self._last_rect.bottomLeft(),
    self._last_rect.bottomRight()
]
scene_corners = [self.mapToScene(corner) for corner in corners]
item_corners = [self._pixmap_item.mapFromScene(sc) for sc in scene_corners]

x_coords = [p.x() for p in item_corners]
y_coords = [p.y() for p in item_corners]

x1 = math.floor(min(x_coords))
y1 = math.floor(min(y_coords))
x2 = math.ceil(max(x_coords))
y2 = math.ceil(max(y_coords))
```

**Why it failed:**

- ❌ Unnecessary complexity for axis-aligned selections
- ❌ Additional `mapFromScene` on pixmap item introduced floating-point errors
- ❌ Multiple min/max operations accumulated rounding errors
- ❌ Caused incorrect offsets when zoomed/panned/fitted

## View Transformations

### Zoom (Scale)

**User action**: Click Zoom In/Out, Ctrl+Wheel, or use shortcuts

**Transform applied**:

```python
self.scale(factor, factor)  # Uniform scale around viewport center
self._zoom *= factor
```

**Effect on coordinates**:

- View coordinates change (selection appears larger/smaller on screen)
- Scene coordinates remain stable (mapToScene handles the transform)
- Image coordinates unchanged (scene = image space)

**Example**:

```
Image: 1000×800 pixels
Zoom: 50% (factor = 0.5)

User draws selection: View (200,100) to (400,300)
Maps to scene: (400,200) to (800,600)
Image coordinates: (400,200) to (800,600) ✓
```

### Fit to Window

**User action**: Click Fit button or Ctrl+1

**Transform applied**:

```python
self.fitInView(pixmap_item, Qt.KeepAspectRatio)
transform = self.transform()
self._zoom = transform.m11()  # Actual scale factor
```

**Effect on coordinates**:

- Calculates optimal scale to fit image in viewport
- May add letterboxing (black bars) if aspect ratios don't match
- Viewport may not start at scene (0,0)

**Example (Letterboxing)**:

```
Image: 1920×1080 (16:9)
Viewport: 600×800 (portrait)

Fit calculates:
- Scale to fit width: 600/1920 = 0.3125
- Scaled height: 1080×0.3125 = 337.5px
- Letterbox: (800-337.5)/2 = 231.25px top/bottom

Visible scene bounds: (0, -231) to (1920, 1311)
Selection at view (100,300): Scene (320, 729)
```

### 100% Zoom (Reset)

**User action**: Click 100% button or Ctrl+0

**Transform applied**:

```python
self.setTransform(QTransform())  # Identity transform
self._zoom = 1.0
```

**Effect on coordinates**:

- 1:1 pixel mapping between view and scene/image
- No scaling, no rotation
- Most accurate coordinate mapping

**Example**:

```
User draws selection: View (100,50) to (300,200)
Maps to scene: (100,50) to (300,200)
Image coordinates: (100,50) to (300,200) ✓
```

### Rotation (Not Supported During Selection)

**User action**: Rotate source pane

**Application behavior**:

```python
def on_rotate(self, degrees: int):
    if active == "source":
        # ... perform rotation ...
        self.src_view.clear_selection()  # ← Selection cleared!
        self.sel_info.setText("Selection: –")
```

**Why**:

- Rotating creates a new image with different dimensions
- Old selection coordinates would be invalid
- Forces user to make new selection after rotation

**Preview/Result rotation**:

- Display-only (visual rotation of the view)
- Does not affect underlying image data
- No coordinate mapping needed

## Real-Time Coordinate Display

### Status Bar Footer (Added 2025-10-28)

The status bar now shows live coordinate information to help debug and verify accuracy:

#### View Coordinates

```python
self.view_coords_label = QLabel("View: (x1,y1)→(x2,y2)")
```

Shows the visible viewport bounds in image pixel space:

- Updates on zoom, pan, window resize
- Clamped to actual image dimensions
- Reveals letterboxing (e.g., starts at (0,100) for 16:9 image in portrait viewport)

**Example**:

```
View: (0,150)→(1920,930)
→ Top 150px and bottom area are out of view
```

#### Selection Coordinates

```python
self.selection_coords_label = QLabel("Selection: (x1,y1)→(x2,y2) [w×h]")
```

Shows the selected area in image pixel coordinates:

- Persists across pane switches
- Includes dimensions in brackets
- Allows verification that crop matches expectation

**Example**:

```
Selection: (427,203)→(873,689) [446×486]
→ Selection starts at pixel (427,203)
→ Ends at pixel (873,689)
→ Dimensions: 446 pixels wide, 486 pixels tall
```

#### Zoom Level

```python
self.zoom_label = QLabel("Zoom: X%")
```

Shows current zoom percentage:

- 100% = 1:1 pixel mapping
- <100% = zoomed out / fitted
- > 100% = zoomed in

**Example**:

```
Zoom: 67%  → Fitted to window
Zoom: 100% → Reset to actual size
Zoom: 156% → Zoomed in 1.56x
```

### Update Logic

The `_update_coordinate_display()` method calculates and updates all coordinate labels:

```python
def _update_coordinate_display(self):
    active_view = self.src_view  # or preview_view / res_view

    # Get visible viewport bounds
    viewport_rect = active_view.viewport().rect()
    tl_scene = active_view.mapToScene(viewport_rect.topLeft())
    br_scene = active_view.mapToScene(viewport_rect.bottomRight())

    # Clamp to image bounds
    img_rect = active_view._pixmap_item.pixmap().rect()
    view_x1 = max(0, min(int(tl_scene.x()), img_rect.width()))
    # ... etc

    # Format and display
    self.view_coords_label.setText(f"View: ({view_x1},{view_y1})→({view_x2},{view_y2})")
```

**Triggered by**:

- `zoomChanged` signal (new in 2025-10-28)
- `selectionChanged` signal
- Pane click events
- Image load/clear operations

## Testing

### Automated Test Suite

Located in: `desktop_app/tests/test_coordinate_mapping.py`

#### Test Cases

1. **`test_coordinate_mapping_at_fit`**

   - Verifies accuracy when view is fitted to window
   - Expects ±5 pixel tolerance due to fit calculations
   - Validates that scene coordinates map back correctly

2. **`test_coordinate_mapping_at_100_percent`**

   - Tests 1:1 pixel mapping at 100% zoom
   - Most strict tolerances (±5px)
   - Confirms identity transform accuracy

3. **`test_coordinate_mapping_zoomed_in`**

   - Validates coordinates when zoomed in 2x
   - Ensures scaling doesn't introduce offset
   - Tests: zoom_in() called twice

4. **`test_coordinate_mapping_zoomed_out`**

   - Tests zoomed out view (0.64x = 0.8 × 0.8)
   - Verifies coordinates remain accurate when scaled down
   - Larger selection area to reduce rounding effects

5. **`test_coordinate_mapping_rotated_90` / `_180`**

   - Confirms that rotation + selection returns (0,0,0,0)
   - Tests the application's intentional behavior
   - Ensures graceful handling of invalid state

6. **`test_coordinate_clamping`**

   - Verifies selection beyond image bounds gets clamped
   - Tests negative coordinates and oversized selections
   - Ensures no crashes or invalid coordinates

7. **`test_crop_matches_coordinates`**
   - End-to-end validation
   - Confirms `crop_selection()` returns image matching coordinate span
   - Checks: cropped.width() == x2-x1, cropped.height() == y2-y1

### Manual Testing Procedure

1. **Load an image** (any size, preferably >1000px)

2. **Test Fit mode**:

   - Click Fit button
   - Check status bar: Zoom should be <100%
   - Draw selection
   - Verify: Selection coords match visual area
   - Verify: Crop preview shows exact selected area

3. **Test 100% mode**:

   - Click 100% button
   - Check status bar: Zoom should be exactly 100%
   - View coords should start at (0,0) or scroll position
   - Draw selection
   - Verify: Coordinates are exact (no offset)

4. **Test Zoom In**:

   - Click Zoom In multiple times
   - Check status bar: Zoom >100%
   - Draw selection in visible area
   - Verify: Crop matches selection despite magnification

5. **Test Zoom Out**:

   - Click Zoom Out
   - Check status bar: Zoom <100%
   - Draw selection
   - Verify: No parts of selection are cut off

6. **Test Window Resize**:

   - Make selection
   - Resize window smaller/larger
   - Check View coords update
   - Selection coords should remain stable
   - Re-process: should give same crop

7. **Test Letterboxing** (aspect ratio mismatch):
   - Load 16:9 image (1920×1080)
   - Resize window to portrait orientation
   - Click Fit
   - Check View coords: may show negative y1 or y2 > image height
   - Draw selection in visible area
   - Verify: Crop is correct despite letterboxing

## Debugging Tips

### Common Issues

#### Issue: Selection offset after zooming

**Symptom**: Crop preview doesn't match visual selection
**Check**:

- View coords in status bar
- Selection coords
- Compare with expected pixel positions
  **Likely cause**: Incorrect coordinate mapping or caching

#### Issue: Parts of selection cut off

**Symptom**: Crop is smaller than expected
**Check**:

- Console logs from `selected_rect_image_coords()`
- Are coordinates being clamped incorrectly?
- Is scene rect wrong?
  **Likely cause**: Premature clamping or wrong coordinate space

#### Issue: Letterboxing confusion

**Symptom**: Can't select top/bottom of image
**Check**:

- View coords show negative or out-of-bounds values
- Zoom level <100%
  **Explanation**: Letterboxing is normal for aspect ratio mismatch
  **Solution**: Click 100% or Zoom In to see full image

### Debug Logging

The application logs coordinate transformations to console:

```python
print(f"[ImageView] View rect: {self._last_rect}")
print(f"[ImageView] Scene coords: ({top_left_scene.x():.2f}, ...)")
print(f"[ImageView] Rotation: {self._rotation}°")
print(f"[ImageView] Image bounds: {img_rect.width()} x {img_rect.height()}")
print(f"[ImageView] Final coords: ({x1}, {y1}) -> ({x2}, {y2})")
```

To enable, selections will automatically print to console during development.

## Future Considerations

### Potential Enhancements

1. **Rotation Support During Selection**

   - Would require four-corner mapping approach
   - More complex coordinate calculations
   - Current design decision: not worth the complexity

2. **Sub-pixel Precision**

   - Return float coordinates instead of int
   - Backend would need to handle float crop coordinates
   - Benefit: Slightly more accurate for small selections at high zoom

3. **Coordinate History**

   - Store last N selections for quick recall
   - Useful for repetitive tasks
   - Would need UI for selection history

4. **Coordinate Input**
   - Allow manual coordinate entry
   - Useful for precise, repeatable crops
   - Would need validation and bounds checking

### Performance Notes

Current implementation is very efficient:

- O(1) coordinate mapping (just two mapToScene calls)
- No allocations (returns tuple of ints)
- Negligible CPU impact (<1ms per selection)

The four-corner approach was O(4) with more allocations, but still fast. The change was made for accuracy, not performance.

## References

- Qt Documentation: [QGraphicsView Coordinate Systems](https://doc.qt.io/qt-6/qgraphicsview.html#coordinate-systems)
- PySide6 API: [QGraphicsView.mapToScene](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QGraphicsView.html#PySide6.QtWidgets.PySide6.QtWidgets.QGraphicsView.mapToScene)
- Project: `desktop_app/widgets/image_view.py` - Implementation
- Project: `desktop_app/tests/test_coordinate_mapping.py` - Test suite
- Project: `CHANGELOG.md` - Change history
