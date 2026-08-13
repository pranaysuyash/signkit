# UI Changes Visual Guide

## Before & After

### Before (Issues)

```
┌─────────────────────────────────────────┐
│ [Open] [Threshold] [Color]              │
│ [+ - Fit 100%] [Clear]                  │  ← Zoom caused pan+select conflict
│                                         │
│ ┌───────────────────────────┐          │
│ │                           │          │
│ │   Source (rotated wrong)  │          │  ← Phone image appeared sideways
│ │                           │          │
│ └───────────────────────────┘          │
│                                         │
│ Crop preview (always visible)           │  ← Took up space before selection
│ ┌─────────────────┐                    │
│ │ [empty]         │                    │
│ └─────────────────┘                    │
│                                         │
│ Result (dark background)                │  ← Hard to see transparent PNG
│ ┌─────────────────┐                    │
│ │ [barely visible]│                    │
│ └─────────────────┘                    │
└─────────────────────────────────────────┘
```

### After (Fixed)

```
┌─────────────────────────────────────────┐
│ [Open] [Threshold] [Color]              │
│ [+ - Fit 100%] [Mode: Select]           │  ← Toggle mode button
│ [Clear Selection]                       │
│                                         │
│ ┌───────────────────────────────────────┐
│ │                                       │
│ │                                       │
│ │   Source (correctly oriented)         │  ← EXIF auto-rotate
│ │   [Full window initially]             │  ← More room to work
│ │                                       │
│ │                                       │
│ └───────────────────────────────────────┘
│                                         │
│ [Preview & Result panes hidden until    │  ← Appear when selection made
│  you make a selection]                  │
│                                         │
│ After selection:                        │
│ Crop preview (white bg)                 │  ← Clear visibility
│ ┌─────────────────┐                    │
│ │ [selection]     │                    │
│ └─────────────────┘                    │
│ Result (white bg)                       │  ← Transparent areas clearly visible
│ ┌─────────────────┐                    │
│ │ [processed sig] │                    │
│ └─────────────────┘                    │
└─────────────────────────────────────────┘
```

## Key Interactions

### Selection Mode (Default)

1. Left-click and drag → draws selection rectangle
2. Release → shows crop preview and result panes
3. Adjust threshold/color → result updates automatically

### Pan Mode

1. Click "Mode: Pan" button (or "Mode: Select" to toggle)
2. Left-click and drag → pans the zoomed view
3. Middle-click → always pans regardless of mode

### Zoom Workflow

```
1. Click "Open & Upload"
2. Image loads correctly oriented (EXIF handled)
3. Full window available for selection
4. Zoom in with Ctrl+wheel or + button
5. Toggle to Pan mode to reposition
6. Toggle back to Select mode
7. Make selection
8. Preview and result panes appear
9. Tweak threshold/color → live updates
10. Save result
```

## Color Scheme (Current)

- Background: Default Qt gray
- Result view: White (for transparency visibility)
- Crop preview: White with 1px gray border
- Buttons: Default Qt style (ready for icons)

## Planned Visual Improvements

1. **Button Icons** (Next)

   - +/− → ➕➖ or custom zoom icons
   - Fit → ⤢ (maximize icon)
   - 100% → 🔍 or 1:1
   - Rotate → ↶↷
   - Mode: Select → ⊕ (crosshair)
   - Mode: Pan → ✋ (hand)
   - Clear → ✖️ or 🗑️

2. **Color Theme** (Optional)

   - Accent color: #007AFF (iOS blue) or #0078D4 (Windows blue)
   - Hover states for buttons
   - Active button highlight

3. **App Icon**
   - Simple signature glyph + extraction arrow
   - macOS: 1024x1024 PNG for .icns
   - Windows: 256x256 ICO
   - Linux: 512x512 PNG

## Testing Checklist

- [ ] Upload vertical phone photo → appears upright
- [ ] Upload horizontal photo → appears normal
- [ ] Zoom in → toggle to Pan mode → drag view → works smoothly
- [ ] Toggle to Select mode → drag selection → no pan conflict
- [ ] Selection shows crop preview on white background
- [ ] Result view shows processed signature clearly (transparent areas visible)
- [ ] Clear selection → panes hide → full source view again
- [ ] Adjust threshold while selection active → result updates live
- [ ] Change color → result updates live
- [ ] Save result → PNG is correct

---

**Status**: All core UX fixes deployed. Ready for icons and rotate buttons next.
