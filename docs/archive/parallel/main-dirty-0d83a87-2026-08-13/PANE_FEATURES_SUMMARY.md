# Pane Features Summary

This document summarizes what you can do in each image pane (Source, Preview, Result) in the Extraction tab.

## Source Pane (Top)

The main working area where you upload and select regions.

### Available Actions

- **Upload**: Open & Upload Image (Ctrl/Cmd+O)
- **Select**: Drag to select a region (rectangle)
- **Zoom**: In/Out, Fit, Reset (Ctrl/Cmd +/-)
- **Pan**: Middle-click or switch to Pan mode
- **Rotate**: Rotates actual image data, re-uploads to backend, clears selection (Ctrl/Cmd+[/])
- **Coordinate Tooltips**: Shows pixel coordinates while hovering/selecting (toggle in left panel)

### What Happens on Rotate

- Image is rotated using PIL
- Rotated image is re-uploaded to backend
- **Selection is cleared** (coordinates are no longer valid)
- You must make a new selection after rotation

## Preview Pane (Middle)

Shows a crop preview of your selected region before processing.

### Available Actions

- **View**: Shows the cropped selection in real-time
- **Zoom**: In/Out, Fit, Reset
- **Pan**: Middle-click
- **Rotate**: View-only rotation (Ctrl/Cmd+[/]) - does NOT alter pixels
- **Coordinate Tooltips**: Shows pixel coordinates while hovering (toggle in left panel)

### Notes

- Appears automatically when you make a selection
- Always shows the raw crop (no processing)
- Useful for verifying your selection before hitting Preview

## Result Pane (Bottom)

Shows the processed result after clicking Preview (background removed, color applied).

### Available Actions

- **View**: Processed signature with background removal and color replacement
- **Zoom**: In/Out, Fit, Reset
- **Pan**: Middle-click
- **Rotate**: View-only rotation (Ctrl/Cmd+[/]) - does NOT alter pixels
- **Copy**: Copy to clipboard (Ctrl/Cmd+C)
- **Export**: Advanced export with background, trim, format options (Ctrl/Cmd+E)
- **Save to Library**: Quick save to local signature library
- **Coordinate Tooltips**: Shows pixel coordinates while hovering (toggle in left panel)

### Export Options (Ctrl/Cmd+E)

When you click Export, you get:

- **Format**: PNG (recommended), JPEG, PNG-8
- **Background**: Transparent, White, Black, Custom color
- **Trim**: Remove empty space around content + optional padding
- **Quality**: JPEG quality slider (1-100%)

## Crop/Trim Feature

**Not a separate action** - it's integrated into Export:

1. Process your selection (Preview button)
2. Click "Export..." (Ctrl/Cmd+E)
3. Check "Trim to content bounds (remove empty space)"
4. Optional: Add padding (0-100 pixels)
5. Choose format and background
6. Export

This trims the result to the actual content bounds, removing any empty/transparent pixels around the edges.

## Active Pane

- Click any pane to make it active (border turns blue)
- Rotation buttons apply to the **active pane**
- Zoom controls apply to the **active pane**
- Source rotation is **destructive** (re-uploads)
- Preview/Result rotation is **view-only** (display transform)

## Coordinate Tooltips

**Toggle**: Left panel, under "Selection" section

When enabled, shows:

- **Source**: `x, y` on hover; `x, y • Sel: (x1, y1) → (x2, y2) [W×H]` while dragging
- **Preview**: `x, y` on hover
- **Result**: `x, y` on hover

All coordinates are in **image pixel space**.

## Quick Reference

| Action               | Source | Preview | Result |
| -------------------- | ------ | ------- | ------ |
| Upload               | ✅     | ❌      | ❌     |
| Select Region        | ✅     | ❌      | ❌     |
| Zoom/Pan             | ✅     | ✅      | ✅     |
| Rotate (destructive) | ✅     | ❌      | ❌     |
| Rotate (view-only)   | ❌     | ✅      | ✅     |
| Copy                 | ❌     | ❌      | ✅     |
| Export               | ❌     | ❌      | ✅     |
| Save to Library      | ❌     | ❌      | ✅     |
| Coordinate Tooltips  | ✅     | ✅      | ✅     |

## Common Workflows

### Basic Extraction

1. Upload image (Source)
2. Select region (Source)
3. Preview appears automatically (Preview)
4. Click Preview button to process (Result)
5. Copy or Export (Result)

### With Rotation

1. Upload image (Source)
2. **Rotate if needed** (Source) - clears selection
3. Make selection (Source)
4. Preview + Process
5. **Optional**: Rotate result view for display (Result)
6. Export

### With Trim/Crop

1. Process selection normally
2. Click Export (Result)
3. Enable "Trim to content bounds"
4. Add padding if desired
5. Export

---

**Note**: The "crop" feature people often ask about is the **Trim to content bounds** option in the Export dialog. There's no separate crop action because:

- Preview pane already shows the crop (your selection)
- Result pane shows the processed crop
- Export → Trim removes any extra empty space around the content
