# Screenshot Capture Scripts

This directory contains automated screenshot capture scripts for SignKit marketing materials.

## Scripts

### 1. `take_screenshots.py` - Basic Automated Capture
**Status:** ✅ Completed (4 screenshots captured on Nov 14, 2025)

Captures basic window states:
- Main interface (empty)
- Image loaded
- Zoom view
- PDF loaded

**Usage:**
```bash
python scripts/take_screenshots.py --auto
```

**Output:** `screenshots/` directory with timestamped PNG files

---

### 2. `comprehensive_screenshots.py` - Full Feature Capture
**Status:** 🆕 New comprehensive script

Captures all key features and workflows:
- ✅ Main interface (empty state)
- ✅ Image loaded in viewer
- ✅ Selection rectangle drawn
- ✅ Extraction result with preview
- ✅ Signature library populated
- ✅ PDF signing tab
- ✅ PDF document loaded (if available)

**Usage:**
```bash
# Run with default settings
python scripts/comprehensive_screenshots.py

# Specify custom output directory
python scripts/comprehensive_screenshots.py --output my_screenshots
```

**Features:**
- Automated UI interaction (loads images, draws selections, triggers extraction)
- Simulates real user workflow
- Captures all major features
- Handles missing assets gracefully
- Timestamped filenames for version tracking

---

### 3. `quick_screenshots.py` - Manual Guide
Provides step-by-step instructions for manual screenshot capture with detailed guidance on what to capture and how.

**Usage:**
```bash
python scripts/quick_screenshots.py
```

---

## Output

All scripts save screenshots to the `screenshots/` directory by default.

**Filename format:** `{number}_{description}_{timestamp}.png`

Example:
```
00_01_main_interface_empty_20251114_170143.png
01_02_image_loaded_20251114_170149.png
02_03_selection_drawn_20251114_170150.png
```

---

## Comparison

| Feature | take_screenshots.py | comprehensive_screenshots.py | quick_screenshots.py |
|---------|-------------------|----------------------------|---------------------|
| Automation | Partial | Full | Manual guide |
| Screenshots | 4 basic | 7+ comprehensive | User-defined |
| UI Interaction | Limited | Full workflow | Manual |
| Selection Drawing | ❌ | ✅ | Manual |
| Extraction | ❌ | ✅ | Manual |
| Library | ❌ | ✅ | Manual |
| PDF Features | Basic | Full | Manual |

---

## Recommendations

**For quick marketing screenshots:**
```bash
python scripts/comprehensive_screenshots.py
```

**For custom/manual screenshots:**
```bash
python scripts/quick_screenshots.py  # Read the guide
# Then manually capture screenshots
```

**For basic window states only:**
```bash
python scripts/take_screenshots.py --auto
```

---

## Requirements

- PySide6 (Qt framework)
- SignKit desktop app dependencies
- Test assets:
  - `desktop_app/resources/signature_template_synthetic_512.jpg` (signature image)
  - `assets/demo_document.pdf` (PDF document)

---

## Tips for Great Screenshots

1. **Clean environment:** Close other windows, hide desktop clutter
2. **Consistent sizing:** All scripts use 1400x900px window size
3. **High resolution:** Retina/HiDPI displays produce better results
4. **Good lighting:** Avoid screen glare if photographing screen
5. **Professional appearance:** Use demo data, no personal information

---

## Post-Processing

After capturing screenshots:

1. **Review:** Check all screenshots for quality
2. **Crop:** Remove menu bars or desktop elements if needed
3. **Resize:** Max 2000px wide for web use
4. **Compress:** Use ImageOptim or TinyPNG
5. **Upload:** Add to Gumroad product page

---

## Troubleshooting

**"PySide6 not installed"**
```bash
pip install PySide6
```

**"Signature image not found"**
- Ensure `desktop_app/resources/signature_template_synthetic_512.jpg` exists in project root
- Or update the script to point to your test image

**"PDF not found"**
- Ensure `assets/demo_document.pdf` exists
- PDF screenshots will be skipped if not available

**Screenshots are blank/black**
- Increase delay times in the script
- Check window is visible and not minimized
- Try running on a different display

---

## Next Steps

1. Run `comprehensive_screenshots.py` to capture all features
2. Review screenshots in `screenshots/` directory
3. Edit/crop as needed
4. Upload to Gumroad product page
5. Update product description with feature highlights

---

**Last Updated:** November 14, 2025
