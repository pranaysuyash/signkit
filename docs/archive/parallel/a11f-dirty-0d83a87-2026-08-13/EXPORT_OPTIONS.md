# Export Options Documentation

## Overview

The signature extractor now includes professional-grade export capabilities inspired by industry-standard tools like Adobe Photoshop and Affinity Photo.

## Button Clarifications

### 👁 Preview Button

**What it does:** Processes the selected region with current threshold and color settings, then displays the result.

This is **not** just a crop preview—it sends your selection to the backend `/extraction/process_image` API which:

1. Applies the color replacement algorithm
2. Applies the threshold filter
3. Returns a transparent PNG with your signature isolated

**When to use:** After selecting a region, adjust threshold/color settings and click Preview to see the processed result.

### 📤 Export Button

**What it does:** Opens an advanced export dialog with professional options.

**Features:**

- **Format Options:**

  - PNG (Recommended) - 24-bit with full transparency
  - JPEG (No Transparency) - Smaller files, solid background required
  - PNG-8 (Smaller) - 256 colors, smaller file size

- **Background Options:**

  - Transparent (PNG only) - Default for signatures
  - White - Common for document embedding
  - Black - Good for testing visibility
  - Custom Color - Pick any background color

- **Canvas Options:**

  - Trim to content bounds - Removes all empty/transparent space
  - Padding - Add pixels around trimmed content (0-100px)

- **Quality:**
  - JPEG Quality slider (1-100%) - Higher = better quality but larger files

**Defaults to `.png` extension** when saving.

### 📁 Save to Library Button

**What it does:** Quick-save with sensible defaults:

- Auto-generates filename: `signature_YYYYMMDD_HHMMSS.png`
- Defaults to PNG format with transparency
- Opens save dialog pre-configured for PNG
- Will eventually save to `~/.signature_extractor/signatures/` directory

**When to use:** When you just want to quickly save the result without choosing export options.

## Best Practices

### For Signatures

✅ **Recommended:**

- Format: PNG
- Background: Transparent
- Trim: Yes, with 5-10px padding
- Use case: Digital signatures, watermarks, overlays

### For Document Embedding

✅ **Recommended:**

- Format: PNG or JPEG
- Background: White or match document color
- Trim: Optional (depends on layout)
- Use case: Inserting into Word docs, PDFs, contracts

### For Web Use

✅ **Recommended:**

- Format: PNG-8 (smaller) or PNG
- Background: Transparent
- Trim: Yes
- Use case: Website assets, email signatures

### For Printing

✅ **Recommended:**

- Format: PNG or JPEG (high quality)
- Background: White
- Trim: No (preserve original dimensions)
- Quality: 95-100% for JPEG
- Use case: Physical documents, letterheads

## Technical Details

### Trim Algorithm

The trim function:

1. Extracts the alpha channel from the RGBA image
2. Finds the bounding box of non-transparent pixels using `PIL.Image.getbbox()`
3. Adds symmetric padding (if specified)
4. Crops to the final bounding box

### Background Compositing

When applying a solid background:

1. Creates a new image with the background color
2. Uses `PIL.Image.alpha_composite()` to blend the signature onto the background
3. Preserves anti-aliasing and semi-transparent pixels

### Format Conversion

- **PNG-8:** Uses adaptive palette quantization with 256 colors
- **JPEG:** Converts to RGB mode, applies optimization, respects quality setting
- **PNG-24:** Native RGBA format, optimized compression

## Comparison with Industry Tools

| Feature                | Adobe Photoshop | Affinity Photo | Signature Extractor |
| ---------------------- | --------------- | -------------- | ------------------- |
| Transparent PNG        | ✅              | ✅             | ✅                  |
| Background options     | ✅              | ✅             | ✅                  |
| Trim to bounds         | ✅              | ✅             | ✅                  |
| Multiple formats       | ✅              | ✅             | ✅                  |
| Quality control        | ✅              | ✅             | ✅                  |
| Quick save             | ✅              | ✅             | ✅                  |
| File size optimization | ✅              | ✅             | ✅                  |

## Future Enhancements

- [ ] Batch export multiple signatures
- [ ] SVG export with vector tracing
- [ ] PDF export with embedded metadata
- [ ] Copy to clipboard (PNG/SVG)
- [ ] Export presets (save favorite settings)
- [ ] DPI/resolution control for printing
- [ ] Color profile management (sRGB, Adobe RGB)
