# Screenshot Automation Guide

## Overview

SignKit includes three screenshot capture approaches for creating marketing materials:

1. **Basic Automated** (`take_screenshots.py`) - ✅ Already completed
2. **Comprehensive Automated** (`comprehensive_screenshots.py`) - 🆕 New full-feature capture
3. **Manual Guide** (`quick_screenshots.py`) - Step-by-step instructions

---

## Quick Start

### Run Comprehensive Capture (Recommended)

```bash
python scripts/comprehensive_screenshots.py
```

This will automatically:
- Launch the app
- Load a signature image
- Draw a selection rectangle
- Process the extraction
- Show the signature library
- Switch to PDF tab
- Load a PDF document
- Capture 7+ professional screenshots

**Time:** ~20 seconds  
**Output:** `screenshots/` directory

---

## Script Comparison

### 1. Basic Automated (`take_screenshots.py`)

**What it captures:**
- Main interface (empty)
- Image loaded
- Zoom view
- PDF loaded

**Pros:**
- Simple and fast
- Already completed (4 screenshots on Nov 14)

**Cons:**
- Limited feature coverage
- No UI interaction
- No extraction workflow

**When to use:** Quick window state captures

---

### 2. Comprehensive Automated (`comprehensive_screenshots.py`) 🆕

**What it captures:**
1. Main interface (empty state)
2. Image loaded in viewer
3. Selection rectangle drawn
4. Extraction result with preview
5. Signature library populated
6. PDF signing tab
7. PDF document loaded

**Pros:**
- Full workflow automation
- Simulates real user actions
- Captures all major features
- Professional marketing quality
- Handles missing assets gracefully

**Cons:**
- Slightly longer execution time (~20s)
- Requires test assets

**When to use:** Creating complete marketing screenshot set

**Features:**
```python
✅ Automated image loading
✅ Selection rectangle simulation
✅ Extraction processing
✅ Library management
✅ PDF tab navigation
✅ PDF document loading
✅ Timestamped filenames
✅ Error handling
```

---

### 3. Manual Guide (`quick_screenshots.py`)

**What it provides:**
- Step-by-step instructions
- Screenshot checklist
- Quality tips
- Post-processing guide

**Pros:**
- Full control over captures
- Can capture edge cases
- Custom scenarios

**Cons:**
- Time-consuming
- Manual effort required
- Inconsistent results

**When to use:** Custom screenshots, special features, edge cases

---

## Captured Screenshots

### Current Status (Nov 14, 2025)

**Basic Script (completed):**
```
✅ 00_01_main_interface_20251114_170143.png (220KB)
✅ 01_02_image_loaded_20251114_170149.png (214KB)
✅ 02_03_zoom_view_20251114_170150.png (214KB)
✅ 03_04_pdf_loaded_20251114_170150.png (214KB)
```

**Comprehensive Script (recommended to run):**
```
📸 01_main_interface_empty
📸 02_image_loaded
📸 03_selection_drawn
📸 04_extraction_result
📸 05_signature_library
📸 06_pdf_tab_empty
📸 07_pdf_loaded
```

---

## Usage Examples

### Comprehensive Capture (Default)

```bash
# Run with default settings
python scripts/comprehensive_screenshots.py

# Output: screenshots/*.png
```

### Custom Output Directory

```bash
# Save to custom directory
python scripts/comprehensive_screenshots.py --output marketing_shots

# Output: marketing_shots/*.png
```

### Basic Capture

```bash
# Run basic automated capture
python scripts/take_screenshots.py --auto

# Output: screenshots/*.png
```

### Manual Guide

```bash
# Show manual screenshot guide
python scripts/quick_screenshots.py

# Follow on-screen instructions
```

---

## Screenshot Quality Guidelines

### Window Size
- **Width:** 1400px (optimal for web)
- **Height:** 900px (good aspect ratio)
- **Consistent:** All screenshots use same size

### File Format
- **Format:** PNG (lossless, supports transparency)
- **Resolution:** Retina/HiDPI when available
- **Compression:** Optimize after capture

### Content
- **Clean:** No personal information
- **Professional:** Demo data only
- **Consistent:** Same window size and theme
- **Clear:** High contrast, readable text

---

## Post-Processing Workflow

1. **Review**
   ```bash
   open screenshots/
   # Check all screenshots for quality
   ```

2. **Crop** (if needed)
   - Remove menu bars
   - Remove desktop elements
   - Focus on app content

3. **Resize** (if needed)
   - Max 2000px wide for web
   - Maintain aspect ratio
   - Use high-quality scaling

4. **Compress**
   ```bash
   # Using ImageOptim (macOS)
   open -a ImageOptim screenshots/
   
   # Or use online tools
   # - TinyPNG.com
   # - Squoosh.app
   ```

5. **Upload**
   - Gumroad product page
   - Website
   - Social media

---

## Troubleshooting

### Script Won't Run

**Error:** `PySide6 not installed`
```bash
pip install PySide6
```

**Error:** `Signature image not found`
- Check `desktop_app/resources/signature_template_synthetic_512.jpg` exists
- Or update script with your test image path

**Error:** `PDF not found`
- Check `assets/demo_document.pdf` exists
- PDF screenshots will be skipped if missing

### Screenshots Are Blank

**Possible causes:**
- Window not visible
- Timing too fast
- Display issues

**Solutions:**
- Increase delay times in script
- Ensure window is not minimized
- Try different display
- Check window is in focus

### Poor Quality

**Possible causes:**
- Low resolution display
- Window too small
- Compression artifacts

**Solutions:**
- Use Retina/HiDPI display
- Ensure 1400x900 window size
- Save as PNG (not JPG)
- Avoid over-compression

---

## Asset Requirements

### Required Assets

1. **Signature Image**
   - Path: `desktop_app/resources/signature_template_synthetic_512.jpg`
   - Format: JPG/PNG
   - Content: Sample signature for extraction

2. **PDF Document** (optional)
   - Path: `assets/demo_document.pdf`
   - Format: PDF
   - Content: Sample document for signing

### Creating Test Assets

If assets are missing:

```bash
# Create demo signature image
# Use any signature image (scanned or digital)
cp /path/to/your/signature.jpg desktop_app/resources/signature_template_synthetic_512.jpg

# Create demo PDF
# Use any PDF document
mkdir -p assets
cp /path/to/your/document.pdf assets/demo_document.pdf
```

---

## Automation Details

### Comprehensive Script Workflow

```
1. Initialize app (1s)
   ↓
2. Load signature image (2.5s)
   ↓
3. Capture: Image loaded (3.5s)
   ↓
4. Draw selection rectangle (5s)
   ↓
5. Capture: Selection drawn (6s)
   ↓
6. Trigger extraction (7.5s)
   ↓
7. Capture: Extraction result (9s)
   ↓
8. Refresh library (10.5s)
   ↓
9. Capture: Library view (11.5s)
   ↓
10. Switch to PDF tab (13s)
    ↓
11. Capture: PDF tab (14s)
    ↓
12. Load PDF (15.5s)
    ↓
13. Capture: PDF loaded (17s)
    ↓
14. Finalize and exit (19s)
```

**Total time:** ~20 seconds

---

## Best Practices

### Before Capture

- [ ] Close other applications
- [ ] Hide desktop clutter
- [ ] Ensure good lighting
- [ ] Check display resolution
- [ ] Verify test assets exist

### During Capture

- [ ] Don't move mouse
- [ ] Don't click anything
- [ ] Let script complete
- [ ] Watch for errors

### After Capture

- [ ] Review all screenshots
- [ ] Check for quality issues
- [ ] Crop if needed
- [ ] Compress for web
- [ ] Organize by feature

---

## Marketing Use Cases

### Gumroad Product Page

**Recommended screenshots:**
1. Main interface (hero image)
2. Image loaded (show workflow)
3. Selection drawn (show interaction)
4. Extraction result (show output)
5. Signature library (show organization)
6. PDF signing (show PDF features)

**Upload order:** Feature progression (workflow)

### Website/Landing Page

**Recommended screenshots:**
1. Main interface (above fold)
2. Extraction result (feature highlight)
3. PDF signing (feature highlight)
4. Library view (feature highlight)

**Format:** Optimized PNG, max 1200px wide

### Social Media

**Recommended screenshots:**
1. Extraction result (visual impact)
2. PDF signing (practical use)

**Format:** Square crop (1:1), 1080x1080px

---

## Next Steps

1. **Run comprehensive capture:**
   ```bash
   python scripts/comprehensive_screenshots.py
   ```

2. **Review screenshots:**
   ```bash
   open screenshots/
   ```

3. **Process and upload:**
   - Crop/resize as needed
   - Compress for web
   - Upload to Gumroad
   - Update product description

4. **Iterate if needed:**
   - Re-run script for updates
   - Capture additional features manually
   - Create custom scenarios

---

## Support

**Issues with scripts:**
- Check `scripts/README_SCREENSHOTS.md`
- Review error messages
- Verify dependencies installed
- Check asset paths

**Questions:**
- See `docs/HELP.md`
- Check `docs/TROUBLESHOOTING.md`

---

**Last Updated:** November 14, 2025  
**Scripts Version:** 2.0 (Comprehensive automation added)
