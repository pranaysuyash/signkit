# PDF Signature Resize Feature

## Implementation Complete ✅

**Date**: October 31, 2025

### Feature Overview

Added interactive resize handles to placed PDF signatures. Users can now:

- **Select** a signature by clicking on it
- **Resize** using 8 handles (4 corners + 4 edges)
- **Preserve aspect ratio** when dragging corner handles
- **Free resize** when dragging edge handles

### How to Use

1. **Place a signature** on a PDF page
2. **Click the signature** to select it (blue border appears)
3. **Resize handles appear** as white squares at corners and edges
4. **Drag a handle** to resize:
   - **Corner handles** (NW, NE, SW, SE): Resize while maintaining aspect ratio
   - **Edge handles** (N, S, E, W): Resize in one dimension only
5. **Click elsewhere** to deselect

### Visual Indicators

- **Selected signature**: Blue dashed border
- **Resize handles**: 8 white squares (8x8 pixels)
- **Cursor feedback**:
  - Diagonal arrows (↖↘↗↙) for corner handles
  - Vertical/horizontal arrows (↕↔) for edge handles
  - Open hand (✋) when hovering over signature
  - Closed hand (✊) when dragging

### Constraints

- **Minimum size**: 20×20 pixels (prevents collapsing)
- **Page bounds**: Signatures cannot extend beyond PDF page edges
- **Aspect ratio**: Preserved for corner resizing, free for edge resizing

### Technical Details

**New State Variables** (in `PDFPageView`):

```python
self.resizing_signature: Optional[int] = None
self.resize_handle: Optional[str] = None  # "nw", "ne", "sw", "se", "n", "s", "e", "w"
self.resize_start_pos: Optional[QPointF] = None
self.resize_orig_rect: Optional[Dict] = None
self.resize_aspect_ratio: Optional[float] = None
self.selected_signature: Optional[int] = None
```

**New Methods**:

- `_draw_resize_handles()`: Renders 8 white handles on selected signature
- `_get_resize_handle_at()`: Detects which handle (if any) is under mouse
- `_get_cursor_for_handle()`: Returns appropriate cursor shape for handle

**Modified Methods**:

- `paintEvent()`: Draws resize handles for selected signature
- `mousePressEvent()`: Detects handle clicks, initiates resize mode
- `mouseMoveEvent()`: Updates signature dimensions during resize
- `mouseReleaseEvent()`: Ends resize operation

### Resize Logic

**Corner Handles** (aspect ratio preserved):

1. Calculate new width based on horizontal drag
2. Compute new height using original aspect ratio: `h = w / ratio`
3. Adjust position for north handles (top stays fixed)

**Edge Handles** (free resize):

- **West/East**: Change width only
- **North/South**: Change height only

**Bounds Checking**:

```python
# Enforce minimum
if new_width >= 20 and new_height >= 20:
    # Apply changes

# Constrain to page
if x < 0:
    width += x
    x = 0
if x + width > page_width:
    width = page_width - x
```

### Usage Example

```python
# User workflow:
1. pdf_viewer.open("contract.pdf")
2. pdf_viewer.set_signature_for_placement(signature_pixmap, sig_path)
3. User clicks on PDF → signature placed
4. User clicks placed signature → becomes selected
5. User drags SE corner handle → signature resizes proportionally
6. User drags E edge handle → signature width changes
7. User clicks away → signature deselected
```

### Integration Points

- Works seamlessly with **drag/move** functionality
- Compatible with **bulk placement** feature
- Respects **coordinate tooltips** in library
- Resize affects final PDF output (via `sign_pdf()`)

### Testing

**Manual Test Cases**:

1. ✅ Place signature, select it, see handles
2. ✅ Drag corner handle → aspect ratio preserved
3. ✅ Drag edge handle → one dimension changes
4. ✅ Drag to minimum size → stops at 20px
5. ✅ Drag beyond page edge → constrained to bounds
6. ✅ Right-click → context menu still works
7. ✅ Drag signature → move still works
8. ✅ Click away → deselect, handles disappear

### Known Limitations

- No **Shift+drag** to temporarily disable aspect ratio lock
- No **Alt+drag** to resize from center
- No **numeric input** for precise dimensions
- No **undo/redo** for resize operations

### Future Enhancements

- [ ] Show dimensions tooltip during resize
- [ ] Snap to grid for alignment
- [ ] Uniform size option (all signatures same size)
- [ ] Keyboard shortcuts (Ctrl+Arrow to resize)
- [ ] Copy size between signatures

## Files Modified

| File                        | Changes                                                                   |
| --------------------------- | ------------------------------------------------------------------------- |
| `desktop_app/pdf/viewer.py` | Added resize state variables, handle detection, resize logic (~120 lines) |

## Related Features

- **Drag & Move**: Move signatures after placement
- **Bulk Placement**: Apply to multiple pages
- **Coordinate Tooltips**: View extraction metadata
- **Color Preservation**: RGBA transparency maintained

## Documentation

- **Full Guide**: `docs/PDF_FEATURE_IMPLEMENTATION.md`
- **Quick Reference**: `TOOLTIPS_QUICK_REFERENCE.md`
- **Implementation**: `COORDINATE_TOOLTIPS_IMPLEMENTATION.md`

---

**All PDF signature manipulation features now complete:**
✅ Place  
✅ Move  
✅ Resize  
✅ Delete  
✅ Bulk apply
