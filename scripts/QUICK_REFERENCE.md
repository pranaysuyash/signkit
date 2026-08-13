# Screenshot Scripts - Quick Reference

## TL;DR

```bash
# Run this to capture all features:
python scripts/comprehensive_screenshots.py
```

**Output:** 7+ professional screenshots in `screenshots/` directory  
**Time:** ~20 seconds

---

## Three Scripts Available

### 1. Comprehensive (Recommended) 🌟

```bash
python scripts/comprehensive_screenshots.py
```

**Captures:**
- Main interface
- Image loaded
- Selection drawn
- Extraction result
- Signature library
- PDF tab
- PDF loaded

**Best for:** Marketing materials, product pages

---

### 2. Basic (Already Done)

```bash
python scripts/take_screenshots.py --auto
```

**Captures:**
- Main interface
- Image loaded
- Zoom view
- PDF loaded

**Best for:** Quick window states

---

### 3. Manual Guide

```bash
python scripts/quick_screenshots.py
```

**Provides:** Step-by-step instructions

**Best for:** Custom screenshots

---

## Quick Commands

```bash
# Comprehensive capture (recommended)
python scripts/comprehensive_screenshots.py

# Custom output directory
python scripts/comprehensive_screenshots.py --output my_shots

# View screenshots
open screenshots/

# List screenshots
ls -lh screenshots/

# Help
python scripts/comprehensive_screenshots.py --help
```

---

## What Gets Captured

| # | Screenshot | Description |
|---|-----------|-------------|
| 1 | Main interface | Empty state, ready to use |
| 2 | Image loaded | Signature document in viewer |
| 3 | Selection drawn | Rectangle around signature |
| 4 | Extraction result | Processed signature with preview |
| 5 | Signature library | Organized signature collection |
| 6 | PDF tab | PDF signing interface |
| 7 | PDF loaded | Document ready for signing |

---

## Requirements

**Dependencies:**
```bash
pip install PySide6
```

**Assets:**
- ✅ `desktop_app/resources/signature_template_synthetic_512.jpg` (present)
- ✅ `assets/demo_document.pdf` (present)

---

## Troubleshooting

**Script won't run:**
```bash
pip install PySide6
```

**Screenshots are blank:**
- Increase delay times in script
- Ensure window is visible

**Assets not found:**
- Check files exist in project root
- Update script paths if needed

---

## Next Steps

1. Run script: `python scripts/comprehensive_screenshots.py`
2. Review: `open screenshots/`
3. Process: Crop, compress, optimize
4. Upload: Gumroad product page

---

## Documentation

**Full guides:**
- `scripts/README_SCREENSHOTS.md` - Script comparison
- `docs/SCREENSHOT_AUTOMATION.md` - Complete guide
- `scripts/SCREENSHOT_STATUS.md` - Status details
- `SCREENSHOT_AUTOMATION_COMPLETE.md` - Summary

---

**Last Updated:** November 14, 2025
