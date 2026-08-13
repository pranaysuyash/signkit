# Critical Bugs Analysis & Fix Plan

## User-Reported Issues

### 1. Clear Selection Doesn't Work on Library Items ❌

**Report:** "clear selection didn't work on the saved signature when opened as source"

**Root Cause Investigation:**

- The `clear_selection()` method exists and looks correct
- Button is connected: `self.clear_sel_btn.clicked.connect(self.on_clear_selection)`
- When image is loaded via `load_image_bytes`, it calls `set_image()` which resets `_last_rect = QRect()`
- **Hypothesis:** Selection rect is being drawn but not properly stored in `_last_rect`

**Fix:**

- Add debug logging to track selection state
- Ensure `_last_rect` is properly updated in `mouseReleaseEvent`
- Make Clear Selection button always enabled when source image exists

### 2. Rotation Still Broken ❌

**Report:** "rotation is still broken"

**Root Cause Investigation:**

- I modified `on_rotate` to use `_current_image_data` instead of `_last_local_path`
- But rotation creates a NEW backend session with new coordinates
- **Issue:** After rotation, old selection coordinates are invalid but not cleared
- **Issue 2:** The app might not have been properly restarted after my code change

**Fix:**

- Ensure rotation CLEARS previous selection (call `on_clear_selection()` after rotate)
- Clear preview and result panes properly
- Add explicit selection reset

### 3. Black Output from Library Signatures ❌

**Report:** "saved signature when used as source to crop, the o/p is just black (changing threshold worked but check)"

**Root Cause Investigation:**

- User opens saved signature → makes selection → processes → result is black
- Threshold changes work → backend is receiving the request
- **Hypothesis 1:** Selection coordinates might be inverted or wrong
- **Hypothesis 2:** Image might not be properly uploaded to backend
- **Hypothesis 3:** Backend session_id mismatch

**Fix:**

- Add logging for selection coordinates before sending to backend
- Verify session_id is correct after library open
- Check if backend is receiving correct image data
- Validate selection rect before processing (x1 < x2, y1 < y2)

### 4. Upscale/Recolor Features Requested ✨

**Report:** "is there a possibility to upscale, recolour, etc.?"

**Response:** YES! These are great ideas:

- **Upscale:** Use PIL to resize with LANCZOS filter (2x, 4x options)
- **Recolor:** Change signature color (user picks new color, replace black with new color)
- **Additional ideas:** Brightness, Contrast, Invert colors

**Implementation:** Add to Export dialog or as post-process options

### 5. Click-to-Focus Pane System 🎯

**Report:** "let the user click the relevant pane from the right panel like they click preview then the toolbar commands like zoom etc apply on that else whatever else is selected?"

**This is BRILLIANT UX!**

**Current Problem:**

- All controls in sidebar apply to... what exactly?
- Zoom buttons → zoom Source? Or Result?
- Rotate → only affects Source
- Export → only works on Result
- Confusing!

**Proposed Solution: Active Pane System**

```
[Sidebar Controls]              [Right Panel]

VIEW (applies to active pane):  ┌─────────────────────┐
- Zoom In/Out                   │ ● SOURCE (ACTIVE)   │ ← Blue border
- Fit/100%                      │   [Image]           │
- Pan/Select mode               └─────────────────────┘

IMAGE (Source only):            ┌─────────────────────┐
- Rotate CCW/CW                 │ ○ Preview           │ ← Gray, inactive
                                │   [Crop]            │
SELECTION (Source only):        └─────────────────────┘
- Color picker
- Threshold                     ┌─────────────────────┐
- Clear Selection               │ ○ Result            │ ← Gray, inactive
                                │   [Processed]       │
EXPORT (Result only):           └─────────────────────┘
- Export/Copy/Save
```

**Implementation:**

1. Add `_active_pane` state: "source", "preview", or "result"
2. Make each pane clickable (detect mouse click on QGraphicsView)
3. Show visual indicator (border color) for active pane
4. Enable/disable controls based on active pane:
   - Zoom/Fit → always available for active pane
   - Rotate → only when Source active
   - Export → only when Result active
5. Add pane indicator in status bar: "Active: Source" / "Active: Result"

**Benefits:**

- User explicitly selects which pane they're working on
- Controls are contextual but still centralized
- Clear visual feedback
- Natural workflow

## Fix Priority

1. **IMMEDIATE:** Fix rotation clear selection issue (blocks workflow)
2. **IMMEDIATE:** Debug black output issue (core functionality broken)
3. **HIGH:** Implement click-to-focus pane system (major UX improvement)
4. **MEDIUM:** Add upscale/recolor features (nice-to-have enhancements)
5. **LOW:** Clear selection button state management (minor polish)

## Implementation Plan

### Step 1: Fix Rotation + Clear Selection

```python
def on_rotate(self, degrees: int):
    # ... existing rotation code ...
    # After successful rotation:
    self.on_clear_selection()  # Clear old selection
    self.status_bar.showMessage("Rotated - make new selection", 3000)
```

### Step 2: Debug Black Output

```python
def on_preview(self):
    x1, y1, x2, y2 = self.src_view.selected_rect_image_coords()
    print(f"[DEBUG] Selection coords: ({x1}, {y1}) → ({x2}, {y2})")
    print(f"[DEBUG] Session ID: {self.session.session_id}")
    # Validate coordinates
    if x1 >= x2 or y1 >= y2:
        print(f"[ERROR] Invalid selection coordinates!")
        return
    # ... continue with processing ...
```

### Step 3: Click-to-Focus System

```python
class MainWindow(QMainWindow):
    def __init__(self, ...):
        self._active_pane = "source"  # "source", "preview", "result"

        # Make panes clickable
        self.src_view.mousePressEvent = lambda e: self._on_pane_clicked("source", e)
        self.res_view.mousePressEvent = lambda e: self._on_pane_clicked("result", e)

    def _on_pane_clicked(self, pane: str, event):
        self._active_pane = pane
        self._update_pane_borders()
        self.status_bar.showMessage(f"Active: {pane.capitalize()}", 2000)
        # Call original mousePressEvent
        super(type(event.widget()), event.widget()).mousePressEvent(event)

    def _update_pane_borders(self):
        # Blue border for active, gray for inactive
        self.src_view.setStyleSheet("border: 2px solid #007AFF;" if self._active_pane == "source" else "")
        self.res_view.setStyleSheet("border: 2px solid #007AFF;" if self._active_pane == "result" else "")

    def on_zoom_in(self):
        if self._active_pane == "source":
            self.src_view.zoom_in()
        elif self._active_pane == "result":
            self.res_view.zoom_in()
```

### Step 4: Upscale/Recolor Features

Add to Export dialog:

- [ ] Upscale 2x / 4x checkbox
- [ ] Recolor option with color picker
- [ ] Brightness/Contrast sliders

## Testing Checklist

- [ ] Open library signature → rotate → verify old selection cleared
- [ ] Open library signature → select → process → verify output not black
- [ ] Click Source pane → zoom controls affect Source
- [ ] Click Result pane → zoom controls affect Result
- [ ] Rotate button disabled when Result pane active
- [ ] Export button disabled when Source pane active
- [ ] Visual border shows active pane clearly
