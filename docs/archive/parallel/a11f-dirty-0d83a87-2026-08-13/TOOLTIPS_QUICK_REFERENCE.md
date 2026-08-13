# Quick Reference: Signature Coordinate Tooltips

## How to Use

1. **Extract and save a signature** in the Extraction tab
2. **Navigate to either tab** (Extraction or PDF Signing)
3. **Hover over any signature** in the library list
4. **View the tooltip** with coordinate and metadata info

## What You'll See

### Basic Info (Always)

- 📄 Filename
- 🕒 Last modified date/time
- 📐 Image dimensions (width × height in pixels)
- 🎨 Color mode (RGBA/RGB)
- 💾 File size

### Extraction Info (If Available)

- 📍 Selection coordinates from source
- 📏 Selection size
- 🖼️ Original source image size
- 🎨 Extraction color (hex)
- ⚙️ Threshold value
- 🔑 Session ID

## Demo Files

### Test PDF

Located at: **`demo_document.pdf`**

**Contents:**

- **Page 1**: Contract agreement with signature lines
- **Page 2**: Service details appendix with 1 signature line
- **Page 3**: Confidentiality agreement with 2 signature lines

**Total**: 3 pages, ~4KB

### Usage

1. Open `demo_document.pdf` in the PDF Signing tab
2. Select a signature from the library (hover to see coordinates!)
3. Click to place signatures on the document
4. Test drag/move functionality
5. Try bulk placement: "📄 Apply to Multiple Pages..."

## Testing Checklist

- [ ] Extract a signature and save to library
- [ ] Hover over signature in Extraction tab - see tooltip
- [ ] Switch to PDF Signing tab
- [ ] Hover over same signature - see tooltip
- [ ] Verify all coordinate info displays correctly
- [ ] Paste from clipboard - tooltip shows basic info only
- [ ] Old signatures (without JSON) - tooltip shows image dimensions

## Troubleshooting

**Q: Tooltip doesn't show extraction coordinates?**

- Old signatures saved before this feature won't have metadata
- Clipboard signatures don't have extraction context
- Manually added PNGs won't have metadata

**Q: Image size shows differently than selection size?**

- **Selection size** = area selected from source document
- **Image size** = final saved signature dimensions (may be scaled)

**Q: Metadata file missing?**

- Check `~/.signature_extractor/signatures/` for `.json` files
- Each PNG should have a matching JSON if saved with "Save to Library"
- JSON is optional - signatures work without it

## File Structure

```
~/.signature_extractor/signatures/
├── signature_20251031_143022.png  ← Image
├── signature_20251031_143022.json ← Metadata
├── signature_20251031_150134.png
└── signature_20251031_150134.json
```

## Related Features

- **Drag & Move**: Right-click signature to move after placement
- **Bulk Placement**: Apply to multiple pages at once
- **Color Preservation**: RGBA signatures maintain transparency and color

## Documentation

- **Full Guide**: `docs/COORDINATE_TOOLTIPS.md`
- **PDF Features**: `docs/PDF_FEATURE_IMPLEMENTATION.md`
- **Coordinate System**: `docs/COORDINATE_MAPPING.md`
