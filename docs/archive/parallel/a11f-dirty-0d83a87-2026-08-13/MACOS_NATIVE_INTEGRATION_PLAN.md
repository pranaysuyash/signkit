# macOS Native Integration Plan

Status note (2026-07-24): This document remains a **parity roadmap** for PySide macOS quality and packager polish.
For product split decision tied to premium perception, use:

- [gtm_mac_runtime_split_record.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/gtm_mac_runtime_split_record.md)

The recommendation at this stage is to complete controlled workflow trust features first, then evaluate native split only on evidence from W16.

## Current Status (November 2, 2025)

### ✅ Completed
1. Removed hardcoded min/max heights from preview and result views
2. Implemented smart layout that minimizes source and maximizes result after selection
3. Fixed panel width responsiveness (min 320px, max 380px)
4. Improved text contrast (white text on dark background)

### ❌ Still Using Non-Native Approaches
1. **Custom stylesheets** instead of native macOS palette
2. **Hardcoded colors** (rgba values) instead of system colors
3. **Generic icons** instead of SF Symbols
4. **Not packaged as .app bundle** - missing native menubar integration

---

## Priority 1: Remove Custom Stylesheet, Use Native Palette

### Current Problem
File: `desktop_app/views/main_window_parts/extraction.py:156-213`

The entire sidebar uses a custom stylesheet with hardcoded colors:
```python
left_panel.setStyleSheet(
    "QWidget#extractionControlsPanel {"
    f"  background-color: {_rgba(panel_color)};"
    f"  border-right: 1px solid {subtle_line_str};"
    f"  color: {text_color.name()};"
    ...
)
```

### Solution
Replace with palette-driven approach:
```python
# Instead of custom stylesheet, use system palette
palette = self.palette()
panel_palette = QPalette(palette)

# Let macOS define the colors based on light/dark mode
panel_palette.setColor(QPalette.ColorRole.Window, palette.window().color())
panel_palette.setColor(QPalette.ColorRole.WindowText, palette.windowText().color())

left_panel.setPalette(panel_palette)
left_panel.setAutoFillBackground(True)

# Remove the entire setStyleSheet() block
```

### Benefits
- Automatic light/dark mode support
- Native appearance changes respected
- Reduced code complexity
- Better accessibility (system honors user preferences)

---

## Priority 2: Replace Fixed Heights with Visibility Toggles

### Current Problem
Still manipulating widget sizes instead of visibility:
- Preview/result containers shown/hidden but layout stretches manually adjusted

### Solution
Use QWidget visibility and size policies:
```python
# When showing result
self.preview_container.setVisible(True)
self.res_view.setVisible(True)

# Layout automatically adjusts via size policies, no manual stretch manipulation needed
```

Remove the `_adjust_pane_layout()` method and rely purely on:
- Size policies (Expanding, Preferred, Minimum)
- Visibility toggles
- Let Qt's layout engine handle the rest

---

## Priority 3: SF Symbols for Icons

### Current Problem
Using generic/emoji icons or custom PNG files

### Solution
Use SF Symbols (macOS system icons):

```python
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

# SF Symbols available via system fonts on macOS
def get_sf_symbol(symbol_name: str, size: int = 16) -> QIcon:
    """Get SF Symbol as QIcon."""
    # Use NSImage from PyObjC or Qt's native symbol support
    # Example symbols:
    # - "folder" for open
    # - "square.and.arrow.up" for export
    # - "arrow.clockwise" for rotate
    # - "plus" / "minus" for zoom
    pass
```

### Icons to Replace
- Open: folder.badge.plus
- Export: square.and.arrow.up
- Save: square.and.arrow.down
- Zoom In: plus.magnifyingglass
- Zoom Out: minus.magnifyingglass
- Rotate: arrow.clockwise / arrow.counterclockwise
- Delete: trash
- Help: questionmark.circle

### Implementation
File: `desktop_app/resources/icons.py`

Replace `get_icon()` function to use SF Symbols on macOS, fall back to Unicode/emoji on other platforms.

---

## Priority 4: Package as .app Bundle

### Current Problem
App runs as Python script, doesn't integrate with macOS properly:
- No native menubar name
- No Dock icon
- No "Open With" integration
- No file associations

### Solution A: py2app
```bash
pip install py2app

# Create setup.py
python setup.py py2app

# Result: dist/Signature Extractor.app
```

### Solution B: PyInstaller
```bash
pip install pyinstaller

pyinstaller --name="Signature Extractor" \
            --windowed \
            --icon=resources/icon.icns \
            --osx-bundle-identifier=com.signaturetools.extractor \
            desktop_app/main.py
```

### Benefits
- Native menubar shows "Signature Extractor"
- Proper application icon in Dock
- Can register file type associations (.png, .pdf)
- Follows macOS application conventions
- Can be distributed via DMG

---

## Priority 5: Native macOS Controls

### Replace Custom Buttons
Instead of styled QPushButton, consider:
- NSButton via PyObjC for truly native buttons
- Qt's native macOS style (already using `app.setStyle("macOS")`)

### Remove Custom Stylesheet for Buttons
Currently:
```python
QPushButton {
    padding: 7px 14px;
    border-radius: 8px;
    background-color: ...;
}
```

Should be:
```python
# No stylesheet - let macOS style handle it
button = QPushButton("Click")
# That's it - native appearance automatically
```

---

## Implementation Order

### Phase 1: Native Styling (1-2 days)
1. Remove custom stylesheet from sidebar
2. Use QPalette for colors
3. Remove hardcoded rgba() values
4. Test light/dark mode switching

### Phase 2: SF Symbols (1 day)
1. Research PySide6 SF Symbol support or PyObjC integration
2. Update `icons.py` with SF Symbol support
3. Replace all toolbar/button icons
4. Test icon scaling and appearance

### Phase 3: Layout Polish (1 day)
1. Remove manual stretch manipulation
2. Rely on visibility + size policies
3. Test responsive behavior at different sizes
4. Ensure smooth transitions when showing/hiding panes

### Phase 4: App Bundle (1 day)
1. Create .app bundle with py2app or PyInstaller
2. Add Info.plist with proper metadata
3. Create application icon (icon.icns)
4. Test native menubar integration
5. Package as DMG for distribution

---

## Testing Checklist

- [ ] Light mode → Dark mode transition works smoothly
- [ ] All text remains readable in both modes
- [ ] No custom colors override system preferences
- [ ] Icons scale properly at different display resolutions
- [ ] Layout adjusts correctly when showing/hiding panes
- [ ] App appears in menubar as "Signature Extractor"
- [ ] Keyboard shortcuts work system-wide
- [ ] Window management (minimize, full-screen) works natively
- [ ] High contrast mode supported (accessibility)
- [ ] VoiceOver can navigate all controls (accessibility)

---

## References

- [Apple Human Interface Guidelines - macOS](https://developer.apple.com/design/human-interface-guidelines/macos)
- [SF Symbols Browser](https://developer.apple.com/sf-symbols/)
- [Qt for macOS](https://doc.qt.io/qt-6/macos.html)
- [PySide6 macOS Extras](https://doc.qt.io/qtforpython-6/overviews/macos.html)
- [py2app Documentation](https://py2app.readthedocs.io/)
