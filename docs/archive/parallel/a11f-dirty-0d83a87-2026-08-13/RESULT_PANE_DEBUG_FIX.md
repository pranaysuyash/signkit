# Result Pane Debug - November 2, 2025

## Issue
Result pane shows label but no processed image after selection.

## What's Working
✅ Backend running and healthy
✅ Crop preview showing correctly
✅ Selection being made

## What's NOT Working
❌ NO `/extraction/process_image/` API calls in backend logs
❌ Result pane empty

## Code Flow Analysis

### Expected Flow
1. User makes selection → `on_selection_changed()` called (line 1362)
2. Calls `schedule_preview()` (line 1394)
3. Timer fires after 200ms → calls `on_preview()` (line 1118)
4. `on_preview()` makes API call via `AsyncRunner` (line 1149)
5. Backend processes, returns PNG
6. `_on_process_finished()` loads image into result view (line 1173)

### Actual Flow (Based on Logs)
1. ✅ Selection made (visible in UI)
2. ✅ Crop preview shows (line 1381 works)
3. ✅ `schedule_preview()` called (line 1394)
4. ❌ Timer NEVER fires OR `on_preview()` returns early
5. ❌ NO API call made
6. ❌ Result stays empty

## Possible Causes

### 1. Timer Not Firing
- Parent widget issue
- Event loop blocked
- Timer destroyed prematurely

### 2. Early Return in `on_preview()`
Check lines 1120-1140 for conditions that return early:
- Line 1120: No session_id
- Line 1132: Empty selection (x1==x2 or y1==y2)
- Line 1137: Invalid coordinates (x1>=x2 or y1>=y2)

### 3. Silent Exception
- AsyncRunner failing silently
- API client not initialized

## Debug Steps

Add logging to trace execution:

```python
# In schedule_preview() - line 1417
def schedule_preview(self):
    LOG.info("[DEBUG] schedule_preview called, session_id=%s", self.session.session_id)
    if not self.session.session_id:
        LOG.warning("[DEBUG] No session_id, returning")
        return
    x1, y1, x2, y2 = self.src_view.selected_rect_image_coords()
    LOG.info("[DEBUG] Selection coords: (%d,%d)→(%d,%d)", x1, y1, x2, y2)
    if x1 == x2 or y1 == y2:
        LOG.warning("[DEBUG] Empty selection, returning")
        return
    LOG.info("[DEBUG] Starting 200ms timer")
    self._preview_timer.start(200)

# In on_preview() - line 1118
def on_preview(self):
    LOG.info("[DEBUG] on_preview() CALLED!")
    ...
```

## Most Likely Cause

Based on "Crop preview 126%" showing in UI but no result, the issue is likely:

**`schedule_preview()` returns early because `self.session.session_id` is None/empty**

The preview works because it's client-side cropping (line 1378-1382). But the result requires backend API which needs a session_id.

## Fix

Check session initialization in image upload flow. The session_id should be set when image is uploaded via `on_open_and_upload()`.

Verify:
1. Is `self.session.init()` being called?
2. Is session_id being set?
3. Is there an exception during upload that's swallowed?

## Test
Run app, load image, check terminal output for:
- "Session ID: ..." log
- Check if schedule_preview logs appear
- Check if on_preview logs appear
