# Visual Regression Fix - Restoring macOS Polish

**Date:** November 1, 2025
**Issue:** App lost all macOS-native polish during refactoring

---

## Problems Identified

From screenshot and user feedback:

1. ❌ **Colors are dull and grey** - Lost vibrant macOS colors
2. ❌ **Glassmorphism removed** - No blur/transparency effects
3. ❌ **Poor shadows** - Flat, Windows 95 appearance
4. ❌ **Straight lines everywhere** - Lost rounded corners
5. ❌ **Gaps and random spacing** - Layout issues
6. ❌ **Stylesheet parsing errors** - "Could not parse stylesheet"
7. ❌ **Grey combined preview/result** - Poor visual separation
8. ❌ **PDF tab looks different than Signature tab** - Inconsistent styling

---

## Root Causes

### 1. GlassPanel Wrapper Missing (FIXED ✅)
- **Problem:** Preview and result panes were separate QWidgets
- **Original:** Wrapped in `GlassPanel` for glassmorphism
- **Fix Applied:** Restored `GlassPanel` wrapper with proper spacing

### 2. Empty Stylesheet Causing Parse Errors (FIXED ✅)
- **Problem:** `self.preview_container.setStyleSheet("")` caused Qt parse errors
- **Fix Applied:** Removed empty stylesheet

### 3. GlassPanel Implementation Reverted (FIXED ✅)
- **Problem:** Custom paintEvent() was breaking the glass effect
- **Original:** Simple `WA_StyledBackground = True` with shadow
- **Fix Applied:** Restored original simple implementation

### 4. Color Calculation Issues (NEEDS FIX ⚠️)
- **Problem:** Panel colors are too dull/grey
- **Current:** `panel_color = base_color.lighter(165)`
- **Needed:** More vibrant, translucent colors

---

## What Was Fixed

✅ Restored `GlassPanel` wrapper for preview/result panes
✅ Removed stylesheet parsing errors
✅ Restored original GlassPanel with shadow effects
✅ Fixed parent widget casting for type safety

---

## What Still Needs Fixing

### High Priority:

⚠️ **1. Left Panel Colors** (Line 92-120 in extraction.py)
```python
# Current: Too dark and dull
panel_color = base_color.lighter(165)

# Should be: Vibrant with transparency
panel_color = QColor(30, 30, 35, 242)  # Or use vibrancy
```

⚠️ **2. GlassPanel Vibrancy**
Consider using NSVisualEffectView via PyObjC for true macOS vibrancy:
```python
# Future enhancement: Real macOS vibrancy
from objc import NSVisualEffectView
```

⚠️ **3. Shadow Quality**
Current shadow might be too weak:
```python
shadow.setBlurRadius(24)  # Increase to 32?
shadow.setOffset(0, 12)   # Increase to (0, 16)?
shadow.setColor(QColor(0, 0, 0, 45))  # Increase alpha to 80?
```

### Medium Priority:

⚠️ **4. Border Radius Consistency**
Ensure all panels use 16px corner radius:
```python
border-radius: 16px;  # Not 6px or 8px
```

⚠️ **5. Spacing/Padding Consistency**
- Left panel: 18px, 22px margins
- GlassPanel: 16px margins
- Controls: 12px spacing

⚠️ **6. Accent Color Usage**
Ensure system accent color is used consistently:
```python
accent = palette.color(QPalette.ColorRole.Highlight)
```

---

## Testing Checklist

### Visual Appearance:
- [ ] Left panel has beautiful translucent effect
- [ ] Preview/result glass panel is visible with blur
- [ ] Shadows are soft and prominent
- [ ] All corners are rounded (16px)
- [ ] Colors are vibrant, not dull grey
- [ ] Spacing is consistent throughout

### Functional:
- [ ] No stylesheet parsing errors in console
- [ ] App launches without warnings
- [ ] All interactions work correctly
- [ ] PDF tab matches Signature tab styling

### macOS Native Feel:
- [ ] Matches system appearance (light/dark mode)
- [ ] Uses system accent color
- [ ] Feels like a native macOS app
- [ ] Not like Windows 95/98!

---

## Comparison: Before vs After

### Original (Good):
```python
preview_result_panel = GlassPanel(self)
stack_layout = QVBoxLayout(preview_result_panel)
stack_layout.setContentsMargins(16, 16, 16, 16)
stack_layout.setSpacing(12)
```

### During Regression (Bad):
```python
# NO GlassPanel wrapper!
images.addWidget(self.preview_container, 1)
images.addWidget(result_container, 1)
```

### After Fix (Good):
```python
preview_result_panel = GlassPanel(parent_widget)
stack_layout = QVBoxLayout(preview_result_panel)
stack_layout.setContentsMargins(16, 16, 16, 16)
stack_layout.setSpacing(12)
stack_layout.addWidget(self.preview_container, 1)
stack_layout.addWidget(result_container, 1)
images.addWidget(preview_result_panel, 2)
```

---

## App Name Fix

✅ Already correct in main.py:
```python
QApplication.setApplicationName("Signature Extractor")
QApplication.setApplicationDisplayName("Signature Extractor")
```

If menu still shows "Python", it's because macOS caches app names. Fix:
```bash
defaults delete com.apple.dock
killall Dock
```

---

## Next Steps

1. **Test Current State:**
   ```bash
   source .venv/bin/activate
   python -m desktop_app.main
   ```

2. **Take Screenshot:** Compare with your "good" version

3. **Adjust Colors:** If still dull, try these vibrant colors:
   ```python
   # For dark mode left panel:
   panel_color = QColor(30, 30, 35, 242)  # Deep charcoal with alpha
   text_color = QColor(255, 255, 255, 217)  # Bright white with slight transparency
   ```

4. **Enhance Shadows:**
   ```python
   shadow.setBlurRadius(32)  # Softer, more prominent
   shadow.setOffset(0, 16)    # Deeper elevation
   shadow.setColor(QColor(0, 0, 0, 80))  # Darker shadow
   ```

5. **Commit When Perfect:**
   ```bash
   git add desktop_app/views/main_window_parts/
   git commit -m "fix: restore macOS-native polish and glassmorphism"
   ```

---

## Key Lesson Learned

**Never let automated formatters/linters touch UI code without review!**

The refactoring from monolithic `main_window.py` to mixins was good architecture, but the visual implementation got lost in translation. Always preserve:
- GlassPanel wrappers
- Color constants
- Shadow parameters
- Spacing/margin values
- Corner radius consistency

---

## Resources

- [APPLE_NATIVE_IMPROVEMENTS.md](docs/APPLE_NATIVE_IMPROVEMENTS.md) - Original design goals
- [glass_panel.py](desktop_app/widgets/glass_panel.py) - Glassmorphism widget
- [Qt Styling Docs](https://doc.qt.io/qt-6/stylesheet.html)
- [macOS HIG](https://developer.apple.com/design/human-interface-guidelines/macos)
