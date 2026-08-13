# Desktop App Bundling Analysis

## Executive Summary

**Question**: How do PDF libraries bundle with the executable app?

**Answer**: Both pypdfium2 and PyMuPDF bundle cleanly with PyInstaller/py2app, but with different size impacts:

- **pypdfium2**: Adds ~16-20 MB (includes native libpdfium binary)
- **PyMuPDF**: Adds ~40-45 MB (includes libmupdf + dependencies)
- **Both**: Auto-detected by PyInstaller, no special configuration needed

**Recommended**: pypdfium2 for smaller bundles (~85-95 MB total vs ~110-130 MB with PyMuPDF)

---

## Current App Bundle Size (No PDF)

### Base Components

```
Python 3.11 runtime:        ~25 MB
PySide6 (Qt6):              ~60 MB
  ├─ QtCore                 ~15 MB
  ├─ QtGui                  ~12 MB
  ├─ QtWidgets              ~10 MB
  ├─ QtNetwork              ~5 MB
  └─ Platform plugins       ~18 MB
OpenCV (cv2):               ~40 MB
NumPy:                      ~20 MB
Pillow (PIL):               ~5 MB
Requests + deps:            ~2 MB
App code + resources:       ~3 MB
─────────────────────────────────
Total (uncompressed):       ~155 MB
Total (compressed DMG):     ~95-105 MB
```

---

## With pypdfium2 + pikepdf

### Additional Components

```
pypdfium2:                  ~8 MB (Python wrapper)
libpdfium.dylib (macOS):    ~7 MB (native binary)
pikepdf:                    ~3 MB (Python wrapper)
libqpdf.29.dylib:           ~4 MB (native binary)
Additional deps:            ~2 MB
─────────────────────────────────
PDF additions:              ~24 MB
─────────────────────────────────
Total (uncompressed):       ~179 MB
Total (compressed DMG):     ~110-120 MB
```

### Bundle Structure (macOS)

```
SignatureExtractor.app/
├─ Contents/
│   ├─ MacOS/
│   │   └─ SignatureExtractor         (main executable)
│   │
│   ├─ Frameworks/
│   │   ├─ Python.framework/          (~25 MB)
│   │   ├─ QtCore.framework/          (~15 MB)
│   │   ├─ QtGui.framework/           (~12 MB)
│   │   ├─ QtWidgets.framework/       (~10 MB)
│   │   ├─ libpdfium.dylib            (~7 MB) ← PDF library
│   │   ├─ libqpdf.29.dylib           (~4 MB) ← PDF editing
│   │   ├─ libopencv_world.dylib      (~40 MB)
│   │   └─ ... (other shared libs)
│   │
│   ├─ Resources/
│   │   ├─ icon.icns
│   │   ├─ app_icon.png
│   │   └─ ... (resources)
│   │
│   └─ PlugIns/
│       ├─ platforms/
│       │   └─ libqcocoa.dylib        (Qt platform)
│       └─ imageformats/
│           ├─ libqjpeg.dylib
│           └─ libqpng.dylib
```

---

## With PyMuPDF (Alternative)

### Additional Components

```
PyMuPDF (fitz):             ~10 MB (Python wrapper)
libmupdf.dylib (macOS):     ~25 MB (native binary)
Additional deps:            ~5 MB
─────────────────────────────────
PDF additions:              ~40 MB
─────────────────────────────────
Total (uncompressed):       ~195 MB
Total (compressed DMG):     ~125-140 MB
```

### Key Difference

PyMuPDF's libmupdf is ~3x larger than libpdfium because it includes:

- More font handling (CJK fonts embedded)
- More format support (XPS, EPUB, CBZ, etc.)
- More rendering options

---

## Platform-Specific Bundles

### macOS (.app → .dmg)

**pypdfium2 approach:**

```
Development build:
  SignatureExtractor.app    ~179 MB (uncompressed)

After optimization:
  Strip debug symbols        -10 MB
  UPX compression           -30 MB
  ────────────────────────
  Optimized .app            ~139 MB

DMG distribution:
  UDZO compression          ~65% ratio
  ────────────────────────
  Final DMG                 ~90-95 MB
```

**PyMuPDF approach:**

```
Final DMG:                  ~115-125 MB
```

### Windows (.exe)

**pypdfium2 approach:**

```
SignatureExtractor.exe + folder structure

Folder contents:
├─ SignatureExtractor.exe    ~5 MB (bootstrapper)
├─ python311.dll             ~3 MB
├─ Qt6Core.dll               ~6 MB
├─ Qt6Gui.dll                ~7 MB
├─ Qt6Widgets.dll            ~5 MB
├─ pdfium.dll                ~7 MB ← PDF library
├─ qpdf29.dll                ~4 MB ← PDF editing
├─ opencv_world460.dll       ~40 MB
├─ numpy core DLLs           ~15 MB
└─ ... (many other DLLs)
──────────────────────────────────
Total folder:                ~170 MB

NSIS Installer (LZMA):       ~105-115 MB
```

**PyMuPDF approach:**

```
+ mupdf.dll                  ~25 MB
──────────────────────────────────
NSIS Installer:              ~130-145 MB
```

### Linux (AppImage)

**pypdfium2 approach:**

```
SignatureExtractor.AppImage structure:

usr/
├─ bin/
│   └─ SignatureExtractor
├─ lib/
│   ├─ python3.11/
│   ├─ libQt6Core.so.6
│   ├─ libQt6Gui.so.6
│   ├─ libQt6Widgets.so.6
│   ├─ libpdfium.so          ~7 MB ← PDF library
│   ├─ libqpdf.so.29         ~4 MB ← PDF editing
│   └─ libopencv_world.so
└─ share/
    ├─ applications/
    └─ icons/
──────────────────────────────────
AppImage (squashfs):         ~110-120 MB
```

---

## PyInstaller Configuration

### Automatic Detection (Works Out of Box)

PyInstaller **automatically detects** native libraries from:

- pypdfium2 → finds `libpdfium.dylib/dll/so`
- pikepdf → finds `libqpdf.dylib/dll/so`
- PyMuPDF → finds `libmupdf.dylib/dll/so`

**No special configuration needed!**

### Basic build.spec

```python
# build.spec
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['desktop_app/main.py'],
    pathex=[],
    binaries=[],  # Auto-detected, leave empty
    datas=[
        ('desktop_app/resources', 'resources'),
        ('desktop_app/license', 'license'),
    ],
    hiddenimports=[
        'pypdfium2',           # PDF library
        'pypdfium2._helpers',
        'pikepdf',             # PDF editing
        'pikepdf._core',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unused heavy modules
        'matplotlib',
        'scipy',
        'pandas',
        'tkinter',
        'test',
        'unittest',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SignatureExtractor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,              # Remove debug symbols
    upx=True,                # Compress with UPX
    console=False,           # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='desktop_app/resources/icons/app_icon.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='SignatureExtractor',
)

# macOS only
app = BUNDLE(
    coll,
    name='SignatureExtractor.app',
    icon='desktop_app/resources/icons/app_icon.icns',
    bundle_identifier='com.yourcompany.signatureextractor',
    version='1.0.0',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'PDF Document',
                'CFBundleTypeRole': 'Viewer',
                'LSItemContentTypes': ['com.adobe.pdf'],
                'LSHandlerRank': 'Alternate',
            }
        ],
    },
)
```

### Build Commands

```bash
# Install PyInstaller
pip install pyinstaller

# Initial build (test)
pyinstaller build.spec

# Clean rebuild
pyinstaller --clean --noconfirm build.spec

# Check what was bundled
ls -lh dist/SignatureExtractor.app/Contents/Frameworks/

# Expected to see:
# libpdfium.dylib    ~7 MB
# libqpdf.29.dylib   ~4 MB
```

---

## Verification After Build

### 1. Check Native Libraries Were Included

**macOS:**

```bash
# List frameworks
ls -lh dist/SignatureExtractor.app/Contents/Frameworks/

# Should see:
# libpdfium.dylib
# libqpdf.29.dylib

# Verify dependencies
otool -L dist/SignatureExtractor.app/Contents/MacOS/SignatureExtractor | grep pdfium
```

**Windows:**

```cmd
# List DLLs
dir dist\SignatureExtractor\*.dll

# Should see:
# pdfium.dll
# qpdf29.dll
```

**Linux:**

```bash
# List shared objects
ls -lh dist/SignatureExtractor/lib/

# Should see:
# libpdfium.so
# libqpdf.so.29

# Verify RPATH
patchelf --print-rpath dist/SignatureExtractor/SignatureExtractor
```

### 2. Test PDF Functionality

```python
# test_bundle.py (run from built app)
import sys
import pypdfium2
import pikepdf

# Test pypdfium2
pdf = pypdfium2.PdfDocument("test.pdf")
print(f"PDF has {len(pdf)} pages")
pdf.close()

# Test pikepdf
with pikepdf.open("test.pdf") as pdf:
    print(f"PDF metadata: {pdf.docinfo}")

print("✓ PDF libraries loaded successfully")
```

Run from bundle:

```bash
# macOS
dist/SignatureExtractor.app/Contents/MacOS/SignatureExtractor test_bundle.py

# Should print page count without errors
```

### 3. Check Bundle Size

```bash
# macOS
du -sh dist/SignatureExtractor.app
# Expected: ~140-180 MB (pypdfium2) or ~195-220 MB (PyMuPDF)

# Create DMG and check
hdiutil create -volname "Signature Extractor" \
    -srcfolder dist/SignatureExtractor.app \
    -ov -format UDZO test.dmg

du -sh test.dmg
# Expected: ~90-120 MB (pypdfium2) or ~115-140 MB (PyMuPDF)
```

---

## Edge Cases & Troubleshooting

### Issue 1: "Library not found" error

**Symptom:**

```
ImportError: DLL load failed while importing _pypdfium2_raw
```

**Cause:** Native library not included or wrong path

**Fix:**

```python
# In build.spec, explicitly add binary
a = Analysis(
    # ...
    binaries=[
        # Find where library is installed
        ('.venv/lib/python3.11/site-packages/pypdfium2_raw/libpdfium.dylib', '.'),
    ],
)
```

### Issue 2: Large bundle size

**Symptom:** Bundle is >250 MB

**Cause:** Unnecessary modules included

**Fix:**

```python
# In build.spec, exclude more
excludes=[
    'matplotlib',
    'scipy',
    'pandas',
    'IPython',
    'jupyter',
    'notebook',
    'tkinter',
    'test',
    'unittest',
    'email',
    'xml',
    'xmlrpc',
    'distutils',
    'setuptools',
    'wheel',
    'pip',
]
```

### Issue 3: Slow startup

**Symptom:** App takes >5 seconds to launch

**Cause:** Using `--onefile` mode

**Fix:** Use `--onedir` (folder mode):

```python
# In build.spec
exe = EXE(
    # ...
    exclude_binaries=True,  # Don't pack into one file
)

coll = COLLECT(  # Create folder distribution
    exe,
    a.binaries,
    # ...
)
```

### Issue 4: Missing Qt plugins

**Symptom:** Black window or no rendering

**Cause:** Qt platform plugin not found

**Fix:**

```python
# In build.spec
datas=[
    # Explicitly include Qt plugins
    ('.venv/lib/python3.11/site-packages/PySide6/Qt/plugins/platforms', 'PySide6/Qt/plugins/platforms'),
]
```

---

## Size Optimization Strategies

### 1. Use UPX Compression

```bash
# Install UPX
brew install upx  # macOS
choco install upx  # Windows
sudo apt install upx-ucl  # Linux

# Enable in spec
exe = EXE(
    # ...
    upx=True,
    upx_exclude=[],
)
```

**Savings:** ~30-40% size reduction

**Note:** May trigger some antivirus false positives

### 2. Strip Debug Symbols

```python
exe = EXE(
    # ...
    strip=True,  # Remove debug symbols
)

coll = COLLECT(
    # ...
    strip=True,
)
```

**Savings:** ~5-10 MB

### 3. Exclude Unused Modules

See "excludes" list in build.spec above

**Savings:** ~10-30 MB depending on what you exclude

### 4. Use One-Folder Distribution

Folder mode is faster and same size when compressed:

```python
# Folder mode (recommended)
exclude_binaries=True  # in EXE()
# Creates: dist/SignatureExtractor/ folder

# vs One-File mode
exclude_binaries=False
# Creates: dist/SignatureExtractor (single file)
# But slower startup (extracts to temp on launch)
```

### 5. Lazy Load Heavy Modules

```python
# desktop_app/main.py
def main():
    # Load UI first (fast)
    from PySide6.QtWidgets import QApplication
    from desktop_app.views.main_window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Load PDF libraries after window is shown
    QTimer.singleShot(100, load_pdf_capabilities)

    return app.exec()

def load_pdf_capabilities():
    """Lazy load PDF libraries."""
    global pypdfium2, pikepdf
    try:
        import pypdfium2
        import pikepdf
        print("✓ PDF capabilities loaded")
    except ImportError as e:
        print(f"⚠ PDF features unavailable: {e}")
```

**Benefit:** Faster perceived startup time (psychological, not actual size)

---

## Final Size Comparison

| Configuration             | macOS DMG     | Windows Installer | Linux AppImage |
| ------------------------- | ------------- | ----------------- | -------------- |
| **Base (no PDF)**         | ~95-105 MB    | ~100-110 MB       | ~105-115 MB    |
| **+ pypdfium2 + pikepdf** | ~110-120 MB   | ~115-125 MB       | ~120-130 MB    |
| **+ PyMuPDF**             | ~125-140 MB   | ~130-145 MB       | ~135-150 MB    |
| **Difference**            | **+15-20 MB** | **+15-20 MB**     | **+15-20 MB**  |

---

## Recommendation

**Use pypdfium2 + pikepdf** because:

1. **Smaller bundles**: ~15-20 MB less than PyMuPDF across all platforms
2. **Better licensing**: Apache 2.0 (no commercial license needed)
3. **Same features**: Viewing, rendering, signature placement all work
4. **Same performance**: Both use native C libraries (PDFium vs MuPDF)
5. **Easier distribution**: No AGPL compliance burden

**Total impact**: Your app grows from ~100-110 MB to ~115-125 MB (installer size)

**User impact**: Minimal - modern apps are commonly 100-500 MB, and users expect rich functionality

---

## Next Steps

1. **Add pypdfium2 + pikepdf to requirements.txt**

   ```bash
   pip install pypdfium2 pikepdf
   pip freeze > requirements.txt
   ```

2. **Create build.spec** (use template above)

3. **Test local build**

   ```bash
   pyinstaller --clean build.spec
   ```

4. **Verify PDF libraries are bundled**

   ```bash
   ls dist/SignatureExtractor.app/Contents/Frameworks/ | grep -E "pdfium|qpdf"
   ```

5. **Test on clean machine** (VM or friend's computer without Python)

6. **Optimize and measure**

   ```bash
   # Before optimization
   du -sh dist/SignatureExtractor.app

   # After strip + UPX
   pyinstaller --clean --strip --upx build.spec
   du -sh dist/SignatureExtractor.app
   ```

7. **Create distributable**
   ```bash
   hdiutil create -volname "Signature Extractor" \
       -srcfolder dist/SignatureExtractor.app \
       -ov -format UDZO SignatureExtractor-1.0.0.dmg
   ```

You're ready to bundle! 🚀
