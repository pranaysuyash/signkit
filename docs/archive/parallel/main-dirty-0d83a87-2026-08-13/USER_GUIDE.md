# Signature Extractor - User Guide

## Quick Start

### Opening Images

**Method 1: Button**

1. Click the "📂 Choose Image" button
2. Select your image file
3. Image appears in the viewer

**Method 2: Drag & Drop** ✨

1. Drag an image file from Finder
2. Drop it anywhere on the app window
3. Image loads instantly

**Supported Formats:**

- PNG (.png)
- JPEG/JPG (.jpg, .jpeg)
- Any standard image format

### Extracting Signatures

1. **Draw Selection**

   - Click and drag to select the signature area
   - Selection appears as a blue rectangle
   - Adjust by redrawing if needed

2. **Adjust Settings**

   - **Threshold:** Controls black/white separation (default: 200)
   - **Auto:** Automatically calculates optimal threshold
   - **Color:** Choose target signature color (default: black)

3. **Preview**

   - Extracted signature appears in right pane
   - Transparent background automatically applied
   - Zoom in/out with +/- buttons or mouse wheel

4. **Export**
   - Click "💾 Export" to save as PNG
   - Or click "📥 Save" to add to Library
   - Metadata JSON saved alongside PNG

### Keyboard Shortcuts

| Action            | macOS       | Windows/Linux |
| ----------------- | ----------- | ------------- |
| Open Image        | Cmd+O       | Ctrl+O        |
| Export            | Cmd+E       | Ctrl+E        |
| Save to Library   | Cmd+S       | Ctrl+S        |
| Copy to Clipboard | Cmd+C       | Ctrl+C        |
| Rotate 90° CW     | Cmd+R       | Ctrl+R        |
| Rotate 90° CCW    | Cmd+Shift+R | Ctrl+Shift+R  |
| Undo              | Cmd+Z       | Ctrl+Z        |
| Redo              | Cmd+Shift+Z | Ctrl+Shift+Z  |
| Zoom In           | Cmd++       | Ctrl++        |
| Zoom Out          | Cmd+-       | Ctrl+-        |
| Fit to Window     | Cmd+0       | Ctrl+0        |

### Library Management

**Auto-Save Feature:**

- Every processed signature is automatically saved
- Access via "Library" tab
- Double-click to reopen any signature
- Right-click to delete

**Library Functions:**

- 📂 Browse all saved signatures
- 🔍 Preview thumbnails
- 🗑️ Delete unwanted entries
- 📤 Re-export in different formats

### Rotation

**When to Use:**

- Image is sideways or upside down
- Need to straighten scanned documents

**How to Rotate:**

1. Click rotate buttons (↶ ↷) in toolbar
2. Or use keyboard shortcuts
3. Image rotates 90° clockwise or counter-clockwise
4. Selection is preserved if possible

### Tips & Tricks

**Better Extraction:**

- Use high-resolution scans (300 DPI or higher)
- Ensure good contrast between signature and background
- Clean the document before scanning if possible
- Adjust threshold if signature is too thin/thick

**Threshold Guide:**

- Lower (100-150): Captures faint signatures
- Medium (150-200): Standard signatures
- Higher (200-255): Bold, dark signatures only
- Use "Auto" for quick optimization

**Performance:**

- Large images (>10 MB) may take a few seconds
- No internet required - works completely offline
- Processing happens locally on your Mac

### Troubleshooting

**Image won't open:**

- Check file format (PNG/JPEG only)
- File must be < 50 MB
- Try drag-and-drop instead of button

**Selection not working:**

- Ensure image is loaded first
- Click and drag to create selection
- Selection must be at least 10x10 pixels

**Export disabled:**

- Enter license key via Help → Enter License
- Test license: `pranay@example.com`
- Or purchase at [Gumroad Link]

**App won't launch on macOS:**

- Right-click → Open (first time only)
- Or: System Settings → Privacy & Security → Open Anyway
- This is normal for unsigned apps

**Backend offline:**

- App works offline - backend is optional
- Red "Offline" status is normal
- All features work without internet

### System Requirements

**macOS:**

- macOS 11.0 (Big Sur) or later
- Apple Silicon (M1/M2/M3/M4) OR Intel processor
- 4 GB RAM minimum
- 500 MB disk space

**Performance:**

- Optimized for Apple Silicon
- Intel Macs fully supported
- No GPU required
- Works on MacBook Air and up

### Privacy & Security

**What we collect:**

- Nothing. Zero data leaves your Mac.
- No analytics, tracking, or telemetry
- No account required
- No internet connection needed

**File Security:**

- All processing happens locally
- Files never uploaded to cloud
- Library stored in your Documents folder
- Full control over your data

### License & Updates

**Test License:**

- Email: `pranay@example.com`
- Unlocks all features for testing

**Production License:**

- One-time purchase: $29
- Covers all v1.x updates (forever)
- No subscription, no recurring fees
- 30-day money-back guarantee

**Updates:**

- Free updates for v1 lifetime
- Notification when update available
- Download from GitHub or Gumroad
- Major version (v2) sold separately

### Getting Help

**Documentation:**

- This guide
- Keyboard shortcuts cheat sheet (Help menu)
- FAQ on website

**Support:**

- Email: [your support email]
- GitHub Issues: [repo link]
- Response time: 24-48 hours

**Feature Requests:**

- Submit via GitHub Issues
- Or email with subject "Feature Request"
- We read every suggestion!

### Known Limitations

**Current Version (v1.0):**

- Single image processing (no batch)
- Basic thresholding only
- macOS only (Windows/Linux coming later)
- Manual install (no auto-updater yet)

**Planned Features:**

- Batch processing (v1.1)
- Advanced image processing (v1.2)
- AI-powered auto-detection (v2.0)
- Cloud sync & collaboration (v2.0)

### Credits

Built with:

- PySide6 (Qt for Python)
- OpenCV (image processing)
- PIL/Pillow (image loading)
- FastAPI (optional backend)

Open source components licensed under their respective terms.

---

**Version:** 1.0.0  
**Last Updated:** November 13, 2025  
**License:** Proprietary (with test license available)
