# Icon Resources for Signature Extractor

## Current Approach

We're using **Qt Standard Icons** which are functional but basic. Here are options to make them beautiful:

---

## Option A: Qt Icon Themes (Best for Cross-Platform)

Qt supports **icon themes** which automatically adapt to the system theme.

### Implementation

```python
# In desktop_app/resources/icons.py
from PySide6.QtGui import QIcon

# Use theme icons (follows system theme)
QIcon.fromTheme("document-open")  # Open file
QIcon.fromTheme("document-save")  # Save
QIcon.fromTheme("zoom-in")        # Zoom in
QIcon.fromTheme("zoom-out")       # Zoom out
QIcon.fromTheme("edit-delete")    # Delete
QIcon.fromTheme("view-refresh")   # Refresh
```

### Supported Themes

- **macOS**: Uses SF Symbols (modern, beautiful)
- **Windows**: Uses Fluent Design icons (modern)
- **Linux**: Uses Breeze/Adwaita themes (KDE/GNOME)

### Pros

- ✅ Native look on each platform
- ✅ Automatically adapts to light/dark mode
- ✅ Zero asset management
- ✅ Scales perfectly (vector)

### Cons

- ❌ Less control over exact appearance
- ❌ May not be available on all systems (fallback needed)

---

## Option B: Material Icons (Modern & Consistent)

Use **Google Material Design** icons for a modern, professional look.

### Implementation

1. Download Material Icons SVG/PNG pack from https://fonts.google.com/icons
2. Add to `desktop_app/resources/icons/material/`
3. Load in code:

```python
icon = QIcon(":/icons/material/open_file.svg")
```

### Resource File (.qrc)

```xml
<!DOCTYPE RCC>
<RCC version="1.0">
  <qresource>
    <file>icons/material/open_file.svg</file>
    <file>icons/material/save.svg</file>
    <file>icons/material/zoom_in.svg</file>
    <!-- etc -->
  </qresource>
</RCC>
```

Compile: `pyside6-rcc resources.qrc -o resources_rc.py`

### Pros

- ✅ Consistent across all platforms
- ✅ Beautiful, modern design
- ✅ Huge icon library (2000+ icons)
- ✅ Free and open source

### Cons

- ❌ Needs manual asset management
- ❌ Increases app size slightly
- ❌ More setup work

---

## Option C: Fluent UI Icons (Windows 11 Style)

Microsoft's **Fluent UI** icons are gorgeous and modern.

### Source

- https://github.com/microsoft/fluentui-system-icons
- MIT licensed, free to use

### Similar to Material but:

- More rounded, softer look
- Matches Windows 11 aesthetic
- Also works great on macOS/Linux

---

## Option D: SF Symbols (macOS Native)

If targeting macOS primarily, use **SF Symbols**.

### Implementation

```python
# macOS only
from PySide6.QtGui import QIcon
icon = QIcon.fromTheme("folder.fill")  # SF Symbol name
```

### Pros

- ✅ Native macOS icons (same as Finder, etc.)
- ✅ Automatically matches system theme
- ✅ Pixel-perfect on macOS

### Cons

- ❌ macOS only (need fallback for Windows/Linux)

---

## Recommendation for You

**Hybrid Approach** (best of both worlds):

1. **Primary**: Use Qt Icon Themes (`QIcon.fromTheme()`)

   - Adapts to system theme automatically
   - Native look on each platform

2. **Fallback**: Bundle Material Icons as resources

   - When theme icon not available, load from resources
   - Ensures consistent experience everywhere

3. **Keep emoji** for personality (like we have now)
   - Users love the visual flair
   - Makes UI friendly and approachable

### Example Code

```python
def get_icon(icon_type: str) -> QIcon:
    """Get icon with theme fallback to bundled resources."""

    # Try theme icon first (native)
    theme_map = {
        'open': 'document-open',
        'save': 'document-save',
        'export': 'document-save-as',
        'zoom_in': 'zoom-in',
        'zoom_out': 'zoom-out',
        'delete': 'edit-delete',
    }

    theme_name = theme_map.get(icon_type)
    if theme_name:
        icon = QIcon.fromTheme(theme_name)
        if not icon.isNull():
            return icon

    # Fallback to bundled resource
    resource_path = f":/icons/material/{icon_type}.svg"
    icon = QIcon(resource_path)
    if not icon.isNull():
        return icon

    # Final fallback: standard pixmap (what we have now)
    return IconManager.get_standard_icon(icon_type)
```

---

## Implementation Steps

1. **Phase 1** (Quick - Do Now):

   - Switch to `QIcon.fromTheme()` for common icons
   - Keeps native look, zero extra work
   - Fallback to current StandardPixmap

2. **Phase 2** (Later - Polish):

   - Download Material Icons SVG pack
   - Create .qrc resource file
   - Bundle as fallback for consistency

3. **Phase 3** (Optional - Branding):
   - Design custom app icon (512x512)
   - Use as window icon, dock icon, file associations
   - Hire designer on Fiverr ($20-50)

---

## Icon Size Guidelines

- **Toolbar**: 24x24 or 32x32
- **Buttons**: 16x16 or 24x24
- **Window/App**: 512x512 (scales down)
- **High DPI**: Use SVG or provide @2x/@3x variants

Qt handles scaling automatically if you use vector formats (SVG) or provide multiple sizes.

---

## Want me to implement Phase 1 now?

I can update the icon manager to use `QIcon.fromTheme()` which will give you native, beautiful icons instantly with ZERO extra assets needed.
