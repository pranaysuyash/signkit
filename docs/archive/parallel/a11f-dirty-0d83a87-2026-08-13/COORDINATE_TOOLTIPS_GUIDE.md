# Coordinate Tooltips Guide

## Overview

Coordinate tooltips show real-time pixel/page coordinates as you work with images and PDFs. This helps with precise positioning, sizing, and understanding the coordinate system.

## Extraction Tab (All Panes: Source, Preview, Result)

### Location

- **Toggle**: Left panel, under "Selection" section
- **Checkbox**: "Show coordinate tooltips" (enabled by default)
- **Applies to**: Source pane, Preview pane, and Result pane

### What You See

1. **Source pane - Hovering over the image**:

   - Shows: `x, y` (current pixel coordinates)
   - Example: `128, 74`

2. **Source pane - While dragging a selection**:

   - Shows: `x, y • Sel: (x1, y1) → (x2, y2) [W×H]`
   - Example: `150, 200 • Sel: (100, 150) → (200, 250) [100×100]`
   - Updates live as you drag

3. **Preview pane - Hovering over crop preview**:

   - Shows: `x, y` (pixel coordinates in cropped image)
   - Example: `64, 32`

4. **Result pane - Hovering over processed result**:
   - Shows: `x, y` (pixel coordinates in processed image)
   - Example: `72, 45`

### Use Cases

- Find exact pixel coordinates for extraction (Source)
- Verify selection size while dragging (Source)
- Check dimensions of cropped region (Preview)
- Measure processed result dimensions (Result)
- Understand coordinate mapping for metadata

## PDF Signing Tab

### Location

- **Toggle**: Left panel, below instructions
- **Checkbox**: "Show coordinate tooltips" (disabled by default)

### What You See

1. **Hovering over PDF page**:

   - Shows: `PDF: x, y`
   - Example: `PDF: 450, 600`

2. **Hovering over a placed signature**:

   - Shows: `PDF: x, y • Sig#1: W×H`
   - Example: `PDF: 450, 600 • Sig#2: 150×50`
   - Adds `[selected]` if that signature is selected

3. **While moving a signature**:

   - Shows: `PDF: x, y • Moving: (x, y)`
   - Example: `PDF: 460, 610 • Moving: (450, 600)`

4. **While resizing a signature**:

   - Shows: `PDF: x, y • Resizing: W×H`
   - Example: `PDF: 470, 620 • Resizing: 160×55`

5. **Placing a new signature (preview)**:
   - Shows: `PDF: x, y • Preview: W×H`
   - Example: `PDF: 300, 400 • Preview: 150×50`

### Use Cases

- Align signatures precisely across multiple pages
- Verify signature dimensions after resizing
- Check placement coordinates for consistency
- Debug coordinate mapping when saving PDFs

## Tips

- **Source tooltips on by default**: Immediately useful for extraction work
- **PDF tooltips off by default**: Reduces clutter; enable when you need precise positioning
- **Toggle anytime**: No need to reload or restart; takes effect immediately
- **Works with all mouse operations**: Hover, drag, resize—tooltips update in real time

## Technical Notes

- Coordinates are in **image pixel space** (Source) or **PDF page space** (PDF tab)
- Selection coordinates show **top-left (x1, y1)** and **bottom-right (x2, y2)**
- Width and height are computed as `x2 - x1` and `y2 - y1`
- Tooltips are throttled to avoid excessive updates (only shown when text changes)

---

**Quick Test**:

1. **Extraction Tab**:
   - Open an image → hover over Source pane → see coordinates
   - Drag a selection → see live selection box with dimensions
   - Click Preview → hover over Preview pane → see coordinates
   - Hover over Result pane → see coordinates
2. **PDF Signing Tab**:
   - Open a PDF → enable tooltips checkbox → hover to see coordinates
