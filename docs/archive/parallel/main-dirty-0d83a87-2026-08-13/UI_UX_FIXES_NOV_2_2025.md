# UI/UX Fixes - November 2, 2025

## ✅ Completed Fixes

### 1. Fixed `get_zoom_percent` AttributeError ✅
**File**: `desktop_app/widgets/image_view.py`

**Problem**: Method didn't exist, causing crashes when trying to display zoom percentage.

**Solution**: Added `get_zoom_percent()` method to ImageView class:
```python
def get_zoom_percent(self) -> float:
    """Get current zoom level as a percentage relative to image pixel size."""
    return self._zoom * 100.0
```

### 2. Auto-Fit Zoom Policy for Source Canvas ✅
**Files**:
- `desktop_app/widgets/image_view.py`
- `desktop_app/views/main_window_parts/extraction.py`

**Problem**: Images loaded at 1:1 pixel scale, causing tiny collapsed views with scrollbars.

**Solution**:
1. Enhanced `fit()` method to support margins (5% default)
2. Added auto-fit on image load (on_open, library load)
3. Added auto-fit after rotation
4. Fit uses 50ms delay to ensure image is fully loaded

**Code Example**:
```python
# After loading image
self.src_view.set_image(image)
# Auto-fit with 5% margin
QTimer.singleShot(50, lambda: self.src_view.fit(margin_percent=5.0))
```

**Result**: Images now fit viewport with nice margins, no scrollbars initially.

### 3. macOS Vibrancy and Proper Color Tokens ✅
**File**: `desktop_app/views/main_window_parts/theme.py`

**Problem**: Dull gray Qt default background, not vibrant like native macOS apps.

**Solution**: Theme-aware background colors:
- **Dark mode**: `rgb(32, 32, 36)` - deep, rich background
- **Light mode**: `rgb(246, 246, 248)` - bright, clean white

**Before**: Plain mid-gray Qt background
**After**: Vibrant, native macOS appearance

### 4. PDF Tab Styling Consistency ✅
**File**: `desktop_app/views/main_window_parts/pdf.py`

**Problem**: PDF tab had slightly different panel colors than extraction tab.

**Solution**: Matched panel colors exactly:
- Dark: `rgba(28, 28, 32, 248)`
- Light: `rgba(251, 251, 253, 250)`

**Result**: Both tabs now have identical visual language.

## 🔄 In Progress

### 5. Light Mode Text Contrast Audit 🔄
**Status**: Checking all translucent text in light mode

**Areas to Verify**:
- Section labels (should be `alpha=235` in light mode) ✅ Already fixed
- Welcome card text (should be opaque dark gray) ✅ Already fixed
- Disabled button text (should be `alpha=180` in light mode) ✅ Already fixed
- Library tooltips and helper text

**Next Steps**:
- Test app in light mode
- Check all text elements for readability
- Ensure 4.5:1 contrast ratio minimum

## 📋 Pending Tasks

### 6. Add Zoom Policy Toggle ⏳
**Estimated Time**: 1-2 hours

**Requirements**:
1. Add "auto-fit" vs "manual" state flag
2. Fit button shows active state when auto-fit enabled
3. Manual zoom/pan disables auto-fit
4. Double-click canvas toggles fit ↔ 100%
5. Keyboard shortcuts:
   - `0`: Fit
   - `1`: 100%
   - `+/-`: Zoom in/out

**Implementation Notes**:
- Add `_auto_fit_mode: bool` flag to extraction state
- Update fit button styling when active
- Hook into zoom/pan events to disable auto-fit
- Add double-click handler to src_view

### 7. Add Selection Hint Overlay ⏳
**Estimated Time**: 1 hour

**Requirements**:
- Show "Drag to select area" centered on source view
- Only when no selection exists and in Select mode
- Hide on first drag event
- Semi-transparent overlay, friendly font

**Implementation**:
- Create QLabel overlay in source view
- Position with `setAlignment(Qt.AlignCenter)`
- Connect to selection changed signal
- Style: 60% opacity, 14px font

## 📊 Testing Checklist

### Auto-Fit Behavior
- [ ] Load tall image (e.g., 5000×800): fits with margins ✓
- [ ] Load wide image (e.g., 800×5000): fits with margins ✓
- [ ] Rotate image: refits automatically ✓
- [ ] Load from library: fits properly ✓
- [ ] Resize window: image stays centered

### Styling
- [x] Dark mode: deep background, no gray wash
- [ ] Light mode: white background, no washed-out appearance
- [x] PDF tab matches extraction tab colors
- [ ] All text readable in both modes
- [ ] Focus rings visible when tabbing

### Zoom Controls
- [ ] Zoom in/out buttons work
- [ ] Zoom combo editable
- [ ] Fit button resets view
- [ ] Reset button works
- [ ] Scroll wheel zoom works
- [ ] Middle-click pan works

## 🎯 Success Metrics

**Before**:
- Images appeared tiny/collapsed
- Dull gray appearance
- PDF tab looked different
- Poor contrast in light mode

**After**:
- Images auto-fit with margins ✅
- Vibrant macOS-native appearance ✅
- Consistent design language ✅
- Readable text in all modes (in progress)

## 🔧 Technical Details

### Color Tokens Used

**Dark Mode**:
```python
main_bg = rgb(32, 32, 36)        # Main window
panel_bg = rgba(28, 28, 32, 248)  # Sidebars
button_bg = lighter(panel_bg, 115) with alpha 220
focus_ring = #007AFF
```

**Light Mode**:
```python
main_bg = rgb(246, 246, 248)       # Main window
panel_bg = rgba(251, 251, 253, 250) # Sidebars
button_bg = lighter(panel_bg, 108) with alpha 180
focus_ring = #0051D5
```

### Fit Algorithm

```python
def fit(self, margin_percent: float = 5.0):
    # Calculate effective viewport (minus margins)
    margin = margin_percent / 100.0
    effective_width = viewport_width * (1 - 2 * margin)
    effective_height = viewport_height * (1 - 2 * margin)

    # Scale to fit
    scale_x = effective_width / image_width
    scale_y = effective_height / image_height
    scale = min(scale_x, scale_y)

    # Apply and center
    self.scale(scale, scale)
    self.centerOn(self._pixmap_item)
```

## 📝 Notes

- Auto-fit delay of 50ms ensures image is loaded before fitting
- All transparent widgets to allow background to show through
- Theme detection: `base_color.lightness() < 120` = dark mode
- PDF tab uses same exact color scheme as extraction tab

## 🚀 Next Actions

1. **Test in light mode**: Verify all text is readable
2. **Add zoom policy toggle**: Let users control auto-fit
3. **Add selection hint**: Guide new users
4. **Verify responsiveness**: Test window resize behavior
5. **Performance check**: Ensure fit doesn't lag on huge images

---

**Date**: November 2, 2025
**Status**: 4/7 tasks complete, 1 in progress, 2 pending
**Priority**: High - core UX improvements
