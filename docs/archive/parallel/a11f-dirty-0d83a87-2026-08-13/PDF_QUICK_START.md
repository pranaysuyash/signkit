# PDF Feature Implementation - Quick Start

## 📋 Overview

This plan adds PDF signing capability to your signature extractor app **without breaking existing features**.

For the long-term product boundary and workflow-ownership model, see [Long-Term PDF Workspace Architecture](analysis/LONG_TERM_PDF_WORKSPACE_ARCHITECTURE_2026-06-18.md).

## 🎯 What Users Get

1. **Open PDFs** and view them page-by-page
2. **Select signatures** from their existing library
3. **Click on PDF** to place signatures anywhere
4. **Save signed PDFs** (original stays unchanged)
5. **Audit logs** track every operation for compliance

## 🏗️ Architecture

This guide documents the implementation slice; the preserved architecture memo captures the broader first-principles workspace direction.

```
┌─────────────────────────────────────┐
│  Signature Extractor Desktop App    │
├─────────────────────────────────────┤
│  Tab 1: Extract Signatures          │ ← EXISTING (unchanged)
│   • Open image → Extract → Save     │
│                                      │
│  Tab 2: Sign PDFs                   │ ← NEW
│   • Open PDF → Place sigs → Save    │
│                                      │
│  Shared: Signature Library           │ ← Both tabs use it
└─────────────────────────────────────┘
```

## ✅ Zero Impact on Existing Features

- All current functionality moves to "Extract Signatures" tab
- PDF features live in separate "Sign PDFs" tab
- Signature library shared (read-only in PDF tab)
- No changes to backend, API, or database

## 🚀 Quick Implementation Steps

### Step 1: Install Dependencies (5 min)

```bash
# Add the current OSS-first baseline to your app environment
python -m pip install pypdfium2 pikepdf

# Optional advanced path (enable intentionally)
python -m pip install -r desktop_app/requirements-pymupdf-optional.txt

# Optional annotations/OCR helpers (if needed)
python -m pip install -r desktop_app/requirements-pdf-optional.txt

# Install
pip install -r desktop_app/requirements.txt
```

### Step 2: Create PDF Module (1 day)

```bash
mkdir -p desktop_app/pdf
touch desktop_app/pdf/__init__.py
touch desktop_app/pdf/renderer.py    # PDF → QPixmap
touch desktop_app/pdf/viewer.py      # Viewer widget
touch desktop_app/pdf/signer.py      # Embed signatures
touch desktop_app/pdf/storage.py     # Audit logs
```

### Step 3: Implement Components (3-4 days)

**Day 1**: `renderer.py` - PDF page rendering  
**Day 2**: `viewer.py` - PDF viewer widget with navigation  
**Day 3**: `signer.py` - Signature embedding using pikepdf  
**Day 4**: `storage.py` - Audit logging system

### Step 4: Integrate into Main Window (2-3 days)

**Day 1**: Add tab widget, move existing UI to tab 1  
**Day 2**: Create PDF tab (tab 2) with controls  
**Day 3**: Wire up all event handlers

### Step 5: Test (2 days)

**Day 1**: Regression testing (ensure nothing broke)  
**Day 2**: New feature testing (PDF workflow)

## 📁 New Files Created

```
desktop_app/pdf/
├── __init__.py
├── renderer.py        # 150 lines - PDF rendering
├── viewer.py          # 350 lines - Viewer widget
├── signer.py          # 200 lines - PDF signing
└── storage.py         # 250 lines - Audit logs

docs/
└── PDF_FEATURE_IMPLEMENTATION.md  # Full implementation guide
```

## 🔍 Code Changes

### Modified Files

1. **`desktop_app/state/session.py`**

   - Add `pdf_state: Optional[PDFState]` field
   - 100% backwards compatible (None by default)

2. **`desktop_app/views/main_window.py`**
   - Replace central widget with QTabWidget
   - Move existing UI to `_setup_extraction_tab()`
   - Add new `_setup_pdf_tab()`
   - Add PDF event handlers

### No Changes Needed

- ✅ `desktop_app/library/storage.py` - used as-is
- ✅ `desktop_app/widgets/image_view.py` - unchanged
- ✅ `desktop_app/api/client.py` - unchanged
- ✅ `backend/` - no backend changes

## 🎨 User Workflow

### Tab 1: Extract Signatures (Existing)

```
1. Open image
2. Select signature region
3. Adjust threshold/color
4. Extract → Preview
5. Save to library
```

### Tab 2: Sign PDFs (New)

```
1. Click "Open PDF"
2. Navigate pages (prev/next)
3. Click signature from library
4. Click on PDF to place it
5. Repeat for more signatures
6. Click "Save Signed PDF"
7. View audit logs (optional)
```

## 🔐 Audit Logging

Every operation is logged:

```json
{
  "timestamp": "2025-10-31T14:23:45",
  "operation": "place_signature",
  "pdf_path": "/path/to/contract.pdf",
  "details": {
    "page": 0,
    "signature_file": "signature_20251031.png",
    "position": { "x": 100, "y": 500 },
    "size": { "width": 150, "height": 50 }
  },
  "user_email": "user@example.com"
}
```

Logs stored in: `~/.signature_extractor/audit_logs/`

## 📦 Bundle Size Impact

| Configuration  | Current | With PDF | Increase |
| -------------- | ------- | -------- | -------- |
| macOS DMG      | ~100 MB | ~115 MB  | +15 MB   |
| Windows Setup  | ~105 MB | ~120 MB  | +15 MB   |
| Linux AppImage | ~110 MB | ~125 MB  | +15 MB   |

**Why pypdfium2?**

- ✅ Smaller (16 MB vs PyMuPDF's 40 MB)
- ✅ Apache 2.0 license (vs AGPL-3.0)
- ✅ Same performance (Chrome's PDF engine)

## ⚠️ Risk Mitigation

| Risk                       | Mitigation                                    |
| -------------------------- | --------------------------------------------- |
| Breaking existing features | Separate tabs, comprehensive regression tests |
| PDF library issues         | Lazy loading, graceful degradation            |
| Large bundle size          | Use pypdfium2 (smaller), UPX compression      |
| Coordinate confusion       | Helper functions, clear documentation         |

## 🧪 Testing Checklist

### Existing Features (Must Pass)

- [ ] Open image works
- [ ] Upload works
- [ ] Extract works
- [ ] Library save/delete works
- [ ] Export PNG/JSON works
- [ ] All keyboard shortcuts work

### New Features

- [ ] Open PDF displays correctly
- [ ] Page navigation works
- [ ] Signature placement at correct position
- [ ] Multiple signatures on one page
- [ ] Save creates valid PDF
- [ ] Audit logs capture all operations

## 📚 Documentation

Created/Updated:

- ✅ `docs/PDF_FEATURE_IMPLEMENTATION.md` - Full implementation guide
- ✅ `docs/BUNDLING_ANALYSIS.md` - Bundle size analysis
- ✅ `docs/analysis/PDF_LIBRARY_COMPARISON.md` - Library comparison
- 📝 TODO: Update `docs/HELP.md` with PDF workflow
- 📝 TODO: Update `README.md` with new features

## ⏱️ Timeline

**Total: 2-3 weeks**

- Week 1: Foundation (renderer, viewer)
- Week 2: Integration (signer, main window)
- Week 3: Polish (audit logs, testing, docs)

## 🎯 Success Criteria

✅ All existing features work identically  
✅ PDF signing uses existing signature library  
✅ All operations logged with timestamps  
✅ Intuitive tab-based UI  
✅ Signed PDFs work in all viewers  
✅ Bundle size <150 MB  
✅ Complete documentation

## 🚦 Ready to Start?

1. **Review**: Read full plan in `docs/PDF_FEATURE_IMPLEMENTATION.md`
2. **Install**: Run `pip install pypdfium2 pikepdf`
3. **Test**: Verify PDF libraries work: `python -c "import pypdfium2; import pikepdf; print('✓ Ready')"`
4. **Code**: Start with Phase 1 (Foundation)

---

**Questions?** Check the full implementation guide or ask!

**Next Command**: `pip install pypdfium2 pikepdf && python -c "import pypdfium2; import pikepdf; print('✓ Ready')"` 🚀
