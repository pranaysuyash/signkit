# Signature Extractor Desktop App: UI/UX & Styling Debug Report

## Date: 1 November 2025

---

## 1. Context

The Signature Extractor desktop app (PySide6/Qt6) was experiencing crashes and visual styling issues after recent changes to improve macOS native appearance.

---

## 2. Issues Identified & Fixed

### ✅ QAction Import Error (FIXED)

- **Problem:** `ImportError: cannot import name 'QAction' from 'PySide6.QtWidgets'`
- **Root Cause:** In PySide6, `QAction` moved to `QtGui`.
- **Solution:** Import from `PySide6.QtGui`.
- **Files:** `desktop_app/views/main_window.py`

### ✅ QPalette.Window AttributeError (FIXED)

- **Problem:** `AttributeError: 'PySide6.QtGui.QPalette' object has no attribute 'Window'`
- **Root Cause:** Use `QPalette.ColorRole.Window`.
- **Files:** `desktop_app/widgets/glass_panel.py`

### ✅ QToolBar Type Errors (FIXED)

- **Problem:** Mypy error - QToolBar expects QWidget parent, not mixin.
- **Solution:** Use `cast(QWidget, self)`.
- **Files:** `desktop_app/views/main_window_parts/toolbar.py`

### ✅ QColor.HexArgb Access Error (FIXED)

- **Problem:** `QColor.HexArgb` not found.
- **Solution:** Use `QColor.NameFormat.HexArgb`.
- **Files:** `desktop_app/views/main_window_parts/extraction.py`

### ✅ Invalid RGBA Stylesheet Values (FIXED)

- **Problem:** Qt stylesheets don't accept fractional alpha (0.0-1.0).
- **Solution:** Use integer alpha (0-255).
- **Files:** `desktop_app/views/main_window_parts/extraction.py`, `status.py`

### ✅ Wrong Parameter Name (FIXED)

- **Problem:** `_remember_color()` got unexpected keyword argument.
- **Solution:** Use `_suppress_preview`.
- **Files:** `desktop_app/views/main_window_parts/extraction.py`

---

## 3. Current Status: Remaining Issues

### ⚠️ Stylesheet Parse Warnings (ACTIVE)

- **Problem:** App runs but shows `Could not parse stylesheet of object QWidget` (4 times).
- **Current Investigation:**
  - App launches and is functional
  - 4 parse warnings occur during initialization
  - Likely related to complex stylesheets or empty `setStyleSheet("")`
- **Next Steps:**
  1. Add Qt message handler to capture failing stylesheet
  2. Simplify multi-selector stylesheets
  3. Verify QColor format specifiers
  4. Test removing empty stylesheet

---

## 4. Visual/UX Concerns from User

- **User Feedback:**

  > "the dullness now doesn't look good, the combined grey space for the preview and results is a let down, the UI is not polished, glassmorphism and mac native looks are gone, doesn't look modern"

- **Assessment:**

  - GlassPanel widget is still in use
  - Glassmorphism styling is present (semi-transparent backgrounds with blur)
  - macOS-specific styling code is still active
  - Status bar has translucent background

- **Possible Causes:**
  1. Integer RGBA values may need tuning for better appearance
  2. Glass panel blur/transparency may need adjustment
  3. Native macOS vibrancy may need PyObjC for true native feel

---

## 5. What Was Tried

- Fixed all import errors related to Qt6 module changes
- Corrected all enum access patterns for PySide6
- Converted all fractional RGBA values to integer (0-255)
- Fixed type casting issues in mixins
- Verified app launches and runs

---

## 6. What Still Needs Investigation

- Identify exact source of 4 stylesheet parse warnings
- Tune visual appearance for better glassmorphism effect
- Consider adding macOS vibrancy via PyObjC if needed

---

## 7. Next Steps (Options)

- Add debug logging to identify failing stylesheets
- Adjust visual styling for better appearance
- Investigate PyObjC integration for native macOS vibrancy
