# macOS Native App Recommendations

**Date:** November 2, 2025
**Based on:** Codex analysis and macOS HIG (Human Interface Guidelines)

---

## ✅ Completed in This Session

### 1. Full-Screen Layout Fixes
- ✅ Changed GlassPanel size policy from `Expanding` → `Preferred`
- ✅ Removed manual `setMaximumHeight` logic
- ✅ Added proper stretch factors: source container (stretch=3), preview panel (stretch=2)
- ✅ Panel now resizes to content naturally, keeping canvas dominant

### 2. Visual Polish
- ✅ Vibrant panel colors instead of calculated dull greys
- ✅ Improved shadow quality (blur 32px, alpha 80)
- ✅ Standardized border-radius to 8px
- ✅ Restored balanced spacing (320px panel, 18/22 margins, 12px spacing)

---

## 🎯 Next Steps for Full macOS Native Experience

### 1. Application Bundle & Menu Bar Name

**Problem:**
The menubar shows "Python" when launched via `python -m desktop_app.main` because we're running through the Python interpreter.

**Solution:**
Package as a macOS `.app` bundle with proper metadata.

#### Option A: PyInstaller (Recommended for Desktop Distribution)
```bash
pip install pyinstaller

pyinstaller --windowed \\
  --name "Signature Extractor" \\
  --icon desktop_app/resources/app_icon.icns \\
  --add-data "desktop_app/resources:desktop_app/resources" \\
  desktop_app/main.py
```

Then edit `dist/Signature Extractor.app/Contents/Info.plist`:
```xml
<key>CFBundleName</key>
<string>Signature Extractor</string>
<key>CFBundleDisplayName</key>
<string>Signature Extractor</string>
<key>CFBundleIdentifier</key>
<string>com.signaturetools.extractor</string>
```

#### Option B: Briefcase (Recommended for Cross-Platform)
```bash
pip install briefcase

# Create briefcase configuration
briefcase create macos
briefcase build macos
briefcase run macos
```

**Configuration** (`pyproject.toml`):
```toml
[tool.briefcase.app.signature-extractor.macOS]
bundle = "com.signaturetools"
```

**Result:** Menubar will show "Signature Extractor" instead of "Python"

---

### 2. SF Symbols & Native Icons

**Problem:**
Current icons use legacy PNG files in `desktop_app/resources/icons.py`. macOS apps should use SF Symbols (vector, monochrome glyphs) that adapt to light/dark mode.

**Recommendation:**
Replace PNG icons with SF Symbol-based assets or vector PDFs.

#### Implementation Options:

**Option A: Use SF Symbols directly (macOS 11+)**
```python
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

# Use system symbols
def get_icon(name: str) -> QIcon:
    # Map custom names to SF Symbol names
    symbol_map = {
        "open": "folder.badge.plus",
        "save": "square.and.arrow.down",
        "copy": "doc.on.doc",
        "delete": "trash",
        "rotate": "arrow.clockwise",
        #... more mappings
    }

    if sys.platform == "darwin" and hasattr(QIcon, "fromTheme"):
        symbol = symbol_map.get(name, name)
        icon = QIcon.fromTheme(f"com.apple.{symbol}")
        if not icon.isNull():
            return icon

    # Fallback to current PNG icons
    return _get_legacy_icon(name)
```

**Option B: Use Vector PDFs**
```python
# Convert icons to PDF format (vectors scale better)
# Place in desktop_app/resources/icons/*.pdf

def get_icon(name: str) -> QIcon:
    pdf_path = f"desktop_app/resources/icons/{name}.pdf"
    if os.path.exists(pdf_path):
        # Qt can render PDF as icon
        return QIcon(pdf_path)

    # Fallback to PNG
    return _get_legacy_icon(name)
```

**Option C: Use SF Symbols via NSImage (requires PyObjC)**
```python
try:
    from AppKit import NSImage
    from PySide6.QtGui import QPixmap
    from PySide6.QtCore import QByteArray, QBuffer, QIODevice

    def get_sf_symbol(symbol_name: str, size: int = 24) -> QIcon:
        ns_image = NSImage.imageWithSystemSymbolName_accessibilityDescription_(
            symbol_name, None
        )
        # Convert NSImage to QIcon via TIFF data
        tiff_data = ns_image.TIFFRepresentation()
        qt_data = QByteArray(bytes(tiff_data))
        pixmap = QPixmap()
        pixmap.loadFromData(qt_data, "TIFF")
        return QIcon(pixmap)
except ImportError:
    # PyObjC not available, use fallback
    pass
```

**After Icon Replacement:**
Update `desktop_app/views/main_window_parts/toolbar.py` button sizes to match HIG:
```python
# Toolbar buttons should be 28x28 or 32x32 for macOS
button.setIconSize(QSize(28, 28))
```

---

### 3. Native Sidebar Styling

**Problem:**
Custom stylesheets override system palette, making the sidebar look heavy/non-native. Section headers use manual lightening, controls use translucent backgrounds.

**Recommendation:**
Strip back custom styling and let macOS native `QPalette` + `QStyle` handle appearance.

#### Current Approach (Heavy Custom Styling):
```python
# extraction.py lines 113-216
panel_color = QColor(30, 30, 35, 242)  # Custom vibrant color
left_panel.setStyleSheet(
    f"background-color: {panel_color_str};"
    "border-right: 1px solid rgba(255, 255, 255, 26);"
    # ... 100+ lines of custom button/input styling
)
```

#### Recommended Approach (Native Styling):
```python
# Let Qt's macOS style handle most appearance
# Only customize spacing/layout, not colors/backgrounds

left_panel.setAutoFillBackground(True)  # Use system palette
# Remove custom color StyleSheet

# For section labels, use system colors:
label.setForeground(QPalette.ColorRole.WindowText)  # Auto adapts to light/dark

# For buttons, use default macOS style:
button = QPushButton("Open")
# Don't set custom background/border colors
# Only customize spacing/padding if needed:
button.setStyleSheet("padding: 6px 12px;")  # Minimal override
```

#### Benefits:
- ✅ Automatic dark mode support (system-managed)
- ✅ Native hover/pressed/disabled states
- ✅ Respects user's accent color preference
- ✅ Matches Finder/System Settings appearance
- ✅ Less code to maintain

#### Migration Strategy:
1. Create a branch: `git checkout -b native-styling-test`
2. Comment out custom color stylesheets in `extraction.py` lines 105-216
3. Test appearance in both light and dark modes
4. Keep only spacing/padding overrides that are necessary
5. Compare with Finder sidebar for reference

---

### 4. Window Chrome & Vibrancy

**Recommendation:**
Use macOS native window vibrancy for true blur effects.

#### Current (Custom GlassPanel):
```python
# glass_panel.py uses QGraphicsDropShadowEffect
# Simulates blur with semi-transparent background
```

#### Native Approach (PyObjC):
```python
from AppKit import NSVisualEffectView, NSVisualEffectBlendingModeBehindWindow
from PySide6.QtCore import Qt

def apply_vibrancy(widget: QWidget, material="sidebar"):
    """Apply native macOS vibrancy to a widget."""
    if sys.platform != "darwin":
        return

    try:
        from AppKit import NSVisualEffectView
        import objc

        ns_view = widget.winId().__int__()  # Get native view
        effect_view = NSVisualEffectView.alloc().initWithFrame_(
            ((0, 0), (widget.width(), widget.height()))
        )

        # Materials: sidebar, titlebar, menu, popover, sheet, etc.
        effect_view.setMaterial_(material)
        effect_view.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
        effect_view.setState_(1)  # Active

        # Add as subview
        # (Requires more integration work)
    except ImportError:
        # Fall back to GlassPanel
        pass
```

**Note:** This requires significant refactoring and PyObjC dependency. Consider for v2.0.

---

### 5. Toolbar Integration

**Current:** Toolbar is separate from title bar

**Recommendation:** Use unified title bar + toolbar (like Safari, Pages, Keynote)

```python
# main_window.py
self.setUnifiedTitleAndToolBarOnMac(True)

# This makes toolbar merge with title bar for native look
```

---

## 📋 Implementation Priority

### High Priority (Do Soon):
1. **Package as .app bundle** - Fixes menu bar name immediately
2. **Strip custom sidebar colors** - Test native styling approach
3. **SF Symbols migration** - Better icon quality and dark mode support

### Medium Priority (Next Release):
4. **Unified toolbar** - One-line change, big visual impact
5. **Update toolbar button sizes** - Match HIG after icon replacement

### Low Priority (Future Enhancement):
6. **Native vibrancy with PyObjC** - Requires significant refactoring
7. **Full HIG compliance audit** - Spacing, typography, interactions

---

## 🧪 Testing Checklist

After implementing recommendations:

### Bundle & Menu:
- [ ] App launches from `.app` bundle
- [ ] Menu bar shows "Signature Extractor" not "Python"
- [ ] App icon displays in Dock
- [ ] About dialog shows correct app name

### Native Styling:
- [ ] Sidebar colors match Finder in light mode
- [ ] Sidebar colors match Finder in dark mode
- [ ] Buttons have native hover states
- [ ] Disabled controls use system disabled appearance
- [ ] Accent color matches user's system preference

### Icons & Toolbar:
- [ ] Icons are crisp at 2x Retina resolution
- [ ] Icons adapt to light/dark mode
- [ ] Toolbar buttons are consistent size (28-32px)
- [ ] Unified title bar looks native

---

## 📚 Resources

### Apple Documentation:
- [macOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/macos)
- [SF Symbols for macOS](https://developer.apple.com/sf-symbols/)
- [NSVisualEffectView Documentation](https://developer.apple.com/documentation/appkit/nsvisualeffectview)

### Qt Documentation:
- [Qt macOS-specific](https://doc.qt.io/qt-6/macos.html)
- [QPalette for native colors](https://doc.qt.io/qt-6/qpalette.html)
- [QStyle for platform appearance](https://doc.qt.io/qt-6/qstyle.html)

### Packaging Tools:
- [PyInstaller](https://pyinstaller.org/)
- [Briefcase](https://briefcase.readthedocs.io/)
- [PyObjC](https://pyobjc.readthedocs.io/)

---

## 💡 Summary

**What We Fixed Today:**
- ✅ Layout responsiveness with proper stretch factors
- ✅ Visual polish with vibrant colors and better shadows
- ✅ Consistent spacing and border-radius

**What's Next for True macOS Native Feel:**
1. Package as `.app` bundle → fixes menu bar name
2. Test native styling → strip custom colors, use QPalette
3. Migrate to SF Symbols → vector icons, auto dark mode
4. Enable unified toolbar → one-line change for big impact

**Goal:** App should be indistinguishable from Apple's own apps (Finder, Preview, Pages) in terms of appearance and behavior.

---

_Documented by: Claude (Sonnet 4.5)_
_Based on: Codex recommendations + macOS HIG_
