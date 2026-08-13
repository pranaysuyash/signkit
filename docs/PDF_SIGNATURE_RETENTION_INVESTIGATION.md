# PDF Signature Retention Investigation - November 2, 2025

## Issue Report

**User Report:** "the signed pdf that was saved did not retain the signature even though we had a success message"

**Symptoms:**
- Success message appears after saving
- File is created at output path
- When opening the PDF, signature is not visible

## Code Analysis

### PDF Signing Implementation

The app uses two possible backends for PDF signing:

#### 1. PyMuPDF (Preferred - HAS_PYMUPDF = True)
```python
# desktop_app/pdf/signer.py:95
page.insert_image(rect, filename=sig_image_path, keep_proportion=True, overlay=True)
```

**Strengths:**
- Industry-standard, reliable
- Properly embeds images into PDF structure
- Works with all PDF viewers including Adobe Acrobat

#### 2. pikepdf (Fallback)
```python
# desktop_app/pdf/signer.py:176-196
# Manually creates PDF stream with drawing commands
```

**Potential Issues:**
- More complex, manual stream manipulation
- May have edge cases with certain PDF structures

### Coordinate System

The code handles coordinate conversion:
```python
# From UI (top-left origin, pixels) to PDF (bottom-left origin, points)
y_pdf = page_height - y - height
```

## Potential Root Causes

### 1. ✅ Coordinate System Mismatch
**Likelihood:** LOW - Code properly converts coordinates
**Evidence:** Conversion code exists and looks correct
**Test:** Try placing signature at (0, 0) to see if it appears at corner

### 2. ⚠️  Image Format/Transparency Issues
**Likelihood:** MEDIUM
**Possible Causes:**
- Signature image has full transparency (alpha=0 everywhere)
- Image format not supported by PyMuPDF
- Color space issues (CMYK vs RGB)

**Test:**
```python
# Add logging before insert_image call
sig_img = PILImage.open(sig_image_path)
print(f"Image mode: {sig_img.mode}, size: {sig_img.size}")
print(f"Has transparency: {sig_img.mode in ('RGBA', 'LA')}")
```

### 3. ⚠️  Signature Placement Outside Page Bounds
**Likelihood:** MEDIUM
**Possible Causes:**
- x, y, width, height values place signature outside visible area
- DPI/scale calculation incorrect
- Page size mismatch

**Test:**
```python
# Add bounds checking
page_width = float(page.mediabox[2]) - float(page.mediabox[0])
page_height = float(page.mediabox[3]) - float(page.mediabox[1])
print(f"Page size: {page_width} x {page_height}")
print(f"Signature rect: ({x}, {y}, {width}, {height})")
```

### 4. ⚠️  PDF Save Issue
**Likelihood:** MEDIUM
**Possible Causes:**
- File not properly closed/flushed
- Incremental save vs full save
- Compression issues

**Current Implementation:**
```python
# PyMuPDF path
self._doc.save(output_path, deflate=True)

# pikepdf path
self._pdf.save(output_path)
```

### 5. ⚠️  Backend Not Available
**Likelihood:** LOW - Success message implies code ran
**Possible Cause:**
- PyMuPDF not installed, pikepdf fallback has bugs

**Test:**
```python
# Check which backend is being used
print(f"Using PyMuPDF: {HAS_PYMUPDF}")
```

### 6. ⚠️  Multiple Signature Overlay Issue
**Likelihood:** LOW
**Possible Cause:**
- Multiple signatures overwriting each other
- Z-order issues

### 7. ❌ PDF Viewer Issue
**Likelihood:** MEDIUM
**Possible Causes:**
- Some PDF viewers don't show overlays immediately
- Need to close and reopen file
- Viewer caching old version

**Test:**
- Try opening in multiple viewers (Preview, Adobe Acrobat, Chrome)
- Clear viewer cache
- Open in fresh viewer instance

## Recommended Debugging Steps

### Step 1: Add Comprehensive Logging

Modify `desktop_app/pdf/signer.py` to add detailed logging:

```python
import logging
LOG = logging.getLogger(__name__)

def add_signature(self, page_num, sig_image_path, x, y, width, height):
    LOG.info(f"=== Adding Signature ===")
    LOG.info(f"Backend: {'PyMuPDF' if HAS_PYMUPDF else 'pikepdf'}")
    LOG.info(f"Page: {page_num}")
    LOG.info(f"Image: {sig_image_path}")
    LOG.info(f"Position: ({x}, {y})")
    LOG.info(f"Size: {width} x {height}")

    if HAS_PYMUPDF and self._doc is not None:
        page = self._doc[page_num]
        page_rect = page.rect
        LOG.info(f"Page size: {page_rect.width} x {page_rect.height}")

        # Check if signature is within bounds
        if x < 0 or y < 0 or x + width > page_rect.width or y + height > page_rect.height:
            LOG.warning(f"Signature may be outside page bounds!")
            LOG.warning(f"  X range: {x} to {x+width} (page: 0 to {page_rect.width})")
            LOG.warning(f"  Y range: {y} to {y+height} (page: 0 to {page_rect.height})")

        # Check image
        try:
            img = PILImage.open(sig_image_path)
            LOG.info(f"Image loaded: mode={img.mode}, size={img.size}")
        except Exception as e:
            LOG.error(f"Failed to load image: {e}")

        rect = fitz.Rect(x, y, x + width, y + height)
        LOG.info(f"PyMuPDF rect: {rect}")

        page.insert_image(rect, filename=sig_image_path, keep_proportion=True, overlay=True)
        LOG.info("Signature inserted successfully")
```

### Step 2: Verify Save Operation

Add logging to save method:

```python
def save(self, output_path: str) -> None:
    LOG.info(f"=== Saving PDF ===")
    LOG.info(f"Output: {output_path}")

    if HAS_PYMUPDF and self._doc is not None:
        LOG.info("Using PyMuPDF save")
        self._doc.save(output_path, deflate=True, garbage=3, clean=True)
        LOG.info(f"Saved successfully, file size: {Path(output_path).stat().st_size} bytes")
    elif self._pdf is not None:
        LOG.info("Using pikepdf save")
        self._pdf.save(output_path)
        LOG.info(f"Saved successfully, file size: {Path(output_path).stat().st_size} bytes")
```

### Step 3: Test with Simple Case

Create a minimal test script:

```python
#!/usr/bin/env python3
"""Test PDF signing with minimal case."""

from desktop_app.pdf.signer import PDFSigner, HAS_PYMUPDF
from PIL import Image as PILImage
import tempfile
from pathlib import Path

# Create a simple test signature image
sig_img = PILImage.new('RGBA', (200, 100), (0, 0, 255, 255))  # Solid blue
sig_path = tempfile.mktemp(suffix='.png')
sig_img.save(sig_path)

print(f"Using PyMuPDF: {HAS_PYMUPDF}")
print(f"Test signature: {sig_path}")

# Sign a PDF
input_pdf = "path/to/test.pdf"  # Replace with actual PDF
output_pdf = tempfile.mktemp(suffix='.pdf')

try:
    signer = PDFSigner(input_pdf)

    # Place signature in top-left corner (should be very visible)
    signer.add_signature(
        page_num=0,
        sig_image_path=sig_path,
        x=50,  # 50pt from left
        y=50,  # 50pt from top
        width=200,
        height=100
    )

    signer.save(output_pdf)
    signer.close()

    print(f"✓ Signed PDF saved: {output_pdf}")
    print(f"  File size: {Path(output_pdf).stat().st_size} bytes")
    print(f"\nOpen this file in a PDF viewer to verify signature appears")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
```

### Step 4: Check PyMuPDF Installation

```python
# In Python console
try:
    import fitz
    print(f"PyMuPDF version: {fitz.version}")
    print(f"PyMuPDF location: {fitz.__file__}")

    # Test basic functionality
    doc = fitz.open()  # Empty document
    page = doc.new_page(width=595, height=842)  # A4 size

    # Try to insert an image
    test_img_path = "path/to/any/image.png"
    rect = fitz.Rect(50, 50, 250, 150)
    page.insert_image(rect, filename=test_img_path)

    doc.save("test_output.pdf")
    print("✓ PyMuPDF is working correctly")

except ImportError:
    print("✗ PyMuPDF not installed")
except Exception as e:
    print(f"✗ PyMuPDF error: {e}")
```

## Quick Fixes to Try

### Fix 1: Force Garbage Collection and Full Save

```python
# In signer.py:save()
if HAS_PYMUPDF and self._doc is not None:
    # More aggressive save options
    self._doc.save(
        output_path,
        garbage=4,  # Maximum garbage collection
        deflate=True,  # Compress streams
        clean=True,  # Clean up structure
        pretty=True,  # Pretty-print (for debugging)
    )
```

### Fix 2: Verify Image Before Insertion

```python
# In add_signature(), before insert_image:
# Verify image is valid and not fully transparent
from PIL import Image as PILImage
img = PILImage.open(sig_image_path)
if img.mode == 'RGBA':
    # Check if image has any non-transparent pixels
    alpha = img.split()[3]
    if alpha.getextrema()[1] == 0:
        raise ValueError("Signature image is fully transparent!")
```

### Fix 3: Add Bounds Clamping

```python
# In add_signature(), before insert_image:
if HAS_PYMUPDF and self._doc is not None:
    page = self._doc[page_num]
    page_rect = page.rect

    # Clamp coordinates to page bounds
    x = max(0, min(x, page_rect.width - width))
    y = max(0, min(y, page_rect.height - height))
    width = min(width, page_rect.width - x)
    height = min(height, page_rect.height - y)

    LOG.info(f"Clamped rect: ({x}, {y}, {width}, {height})")
```

### Fix 4: Explicit Close Before Opening

```python
# In UI code after saving
signer.save(output_path)
signer.close()
signer = None  # Force cleanup

# Wait a bit for file system
import time
time.sleep(0.1)

# Now safe to open in viewer
```

## Verification Steps

After implementing fixes, verify:

1. **File Size Check**
   - Original PDF: X bytes
   - Signed PDF: Should be X + (signature image size) bytes
   - If sizes are identical, signature wasn't embedded

2. **PDF Structure Check**
   ```bash
   # Use mutool to inspect PDF structure
   mutool show signed.pdf 1  # Show page 1 resources
   # Look for /XObject entries
   ```

3. **Visual Inspection**
   - Open in Preview (macOS)
   - Open in Adobe Acrobat
   - Open in Chrome/Firefox PDF viewer
   - Check all pages where signatures should be

4. **Console Log Review**
   - Check for any warnings about coordinates
   - Verify "Signature inserted successfully" message
   - Check final file size

## Implementation Priority

### High Priority (Do First)
1. ✅ Add logging to `add_signature()` - see Step 1
2. ✅ Add logging to `save()` - see Step 2
3. ✅ Run minimal test script - see Step 3

### Medium Priority (If Issue Persists)
4. Add bounds clamping - Fix 3
5. Verify image transparency - Fix 2
6. Use aggressive save options - Fix 1

### Low Priority (If All Else Fails)
7. Force pikepdf backend for comparison
8. Try different PDF viewers
9. Check macOS permissions (sandbox, file access)

## Expected Outcomes

After fixes:
- ✅ Signatures appear in saved PDFs
- ✅ Visible in all PDF viewers
- ✅ Detailed logs help diagnose any issues
- ✅ Bounds checking prevents out-of-view signatures

## Additional Resources

- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [pikepdf Documentation](https://pikepdf.readthedocs.io/)
- [PDF Reference 1.7](https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf)

---

**Date:** November 2, 2025
**Status:** 🔍 INVESTIGATING - Awaiting test results with enhanced logging
**Next:** User to test with logging enabled and report findings

## Addendum (2026-08-12)

- Scope for this session: restore editable signature placement when reopening signed PDFs by embedding placement metadata directly into the output PDF.
- Current fixes:
  - `desktop_app/pdf/signer.py`
    - `_apply_signature_manifest` now writes to a temp PDF and replaces the target atomically.
    - `sign_pdf` now calls `signer.save(...)` before metadata embedding and closes signer via `finally`.
    - Manifest embedding warning now includes the exception text.
  - `desktop_app/pdf/viewer.py`
    - Manifest image decode path uses the instance helper correctly.
    - Restoration safely handles missing/invalid manifest image data.
- Validation run:
  - `uv run pytest desktop_app/tests/test_pdf_features.py desktop_app/tests/test_pdf_improvements.py`
  - Result: `41 passed`
- Status:
  - ✅ Manifests are now written and preserved through reopen workflow.
  - ✅ Restored signatures can round-trip style and remain editable in viewer integration tests.
