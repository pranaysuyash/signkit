# Feature Expansion Roadmap: Signature Extraction to PDF and Document Intelligence

**Project:** Signature Extractor / SignKit  
**Date:** 2026-06-17  
**Status:** Research memo  
**Purpose:** List the most credible product expansion paths around signature field identification, native PDF editing, computer vision, and adjacent product lines.

## 1. Ground Truth From The Repo

Before expanding, it helps to anchor on what is already real in this codebase:

- The desktop app already has an OpenCV-based auto-detect flow for signatures in images in [`desktop_app/processing/extractor.py`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/desktop_app/processing/extractor.py).
- The current desktop UI already routes image extraction through the Qt app in [`desktop_app/views/main_window_parts/extraction.py`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/desktop_app/views/main_window_parts/extraction.py).
- The PDF stack is already present in dependencies, including `pypdfium2`, `pikepdf`, and `PyMuPDF` in [`desktop_app/requirements.txt`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/desktop_app/requirements.txt).
- Existing analysis already recommends a hybrid PDF stack in [`docs/analysis/PDF_LIBRARY_COMPARISON.md`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/analysis/PDF_LIBRARY_COMPARISON.md).
- Existing product docs already describe PDF signing and broader strategy in [`docs/PDF_FEATURE_IMPLEMENTATION.md`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/PDF_FEATURE_IMPLEMENTATION.md) and [`docs/DOMAIN_EXPANSION_STRATEGY.md`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/DOMAIN_EXPANSION_STRATEGY.md).

That means the most valuable next step is not "invent a new product." It is to extend the current signature workflow into adjacent PDF operations and document intelligence that reuse the same asset: the extracted signature library.

## 1.1 Implemented In This Pass

The repo already had the underlying CV and PDF primitives, and this pass surfaced them into the product surface by:

- making auto-detect an explicit extraction action in the Qt UI
- separating auto-threshold from auto-clean in the extraction workflow
- adding overlay preview mode for the extracted signature on top of the original crop
- keeping the canonical PDF signing path in one place instead of a duplicate tab
- adding vault usage-history metadata so reuse is visible in the UI

The remainder of the roadmap below stays valid as the longer-term expansion plan.

## 1.2 Execution Update (2026-06-17)

- Added durable bulk signature placement behavior in the PDF tab with:
  - field-aware adaptive replay across selected pages,
  - optional fixed-ratio replay for same-position mode,
  - run-level audit manifest for each bulk placement operation.
- Added SQLite run manifest support and audit log run IDs in `desktop_app/pdf/db_audit.py`.
- Added field overlay rendering and selection-aware placement helpers in `desktop_app/pdf/viewer.py`.
- Added explicit PDF tab hooks for detected field listing, native form field detection/fill, and richer control-state refresh flow in `desktop_app/views/main_window_parts/pdf.py`.
- Added regression coverage for audit runs and geometry helpers in:
  - `desktop_app/tests/test_db_audit.py`
  - `desktop_app/tests/test_pdf_field_detection.py`
- This run also formalizes the open-source stack preference around existing libraries (pypdfium2 + pikepdf + OCR tooling) and keeps full-editor scope constrained to signing workflows first.

## 2. Highest-Value Features To Add

### 2.1 Signature Field Identification

This is the feature you mentioned, and it is the strongest near-term expansion.

What it does:

- Detect likely signature lines, boxes, initials fields, and "sign here" regions inside PDFs or scanned documents.
- Highlight candidate fields in the viewer and suggest placement automatically.
- Let the user confirm, reject, or override suggestions.

Why it matters:

- Reduces the most annoying manual step in signing workflows.
- Makes the app feel intelligent without becoming a full DocuSign clone.
- Creates a clean bridge from extraction to signing.

Implementation path:

- Start with heuristics:
  - OCR text triggers such as "signature", "sign here", "initial", "date".
  - Line and box detection with OpenCV.
  - Relative positioning near labels.
- Add layout analysis:
  - Use OCR plus region detection for form-like pages.
  - Rank candidate regions by confidence.
- Add PDF-native anchors:
  - Detect form widgets / fields when present.
  - Store anchor metadata so templates can reapply across similar documents.

Best-fit open-source building blocks:

- `OCRmyPDF` for making scanned PDFs searchable and easier to analyze.
- `docTR` or `Tesseract` for OCR.
- `LayoutParser` for document layout detection.
- `pypdfium2` for rendering pages.

Suggested product shape:

- "Auto-find signature fields" button.
- Confidence overlay on page.
- One-click placement into the top-ranked field.

### 2.2 Native PDF Editing

This should be "targeted PDF editing," not a generic Acrobat replacement.

What it should include first:

- Page rotate, reorder, split, merge.
- Stamp a signature image.
- Add text, dates, and labels.
- Crop and flatten.
- Redact selected regions.
- Fill existing form fields.
- Insert a signature page or approval note.

Why it matters:

- Gives the app more reasons to exist after extraction.
- Supports common document workflows directly inside the product.
- Helps enterprise users who want one local tool instead of several.

Recommended scope:

- MVP: page ops, image stamping, redaction, and form filling.
- Later: annotations, comments, and diff/compare.

Best-fit open-source building blocks:

- `pikepdf` for fast PDF manipulation and repair.
- `PyMuPDF` for richer editing, redaction, annotations, and rendering if licensing is acceptable.
- `pypdfium2` for fast viewing and page rendering.

Tradeoff:

- `PyMuPDF` is powerful, but the repo license is AGPL. That is fine for internal tooling or a deliberate commercial-license path, but it is not the cleanest default for a commercial desktop app.
- `pypdfium2` plus `pikepdf` is the cleaner open-source-first default.

### 2.3 Searchable PDFs And OCR Cleanup

This is a very practical extension because many signature documents are scanned images.

What it does:

- Turn image-only PDFs into searchable PDFs.
- Deskew and clean low-quality scans.
- Improve text extraction for field detection and document analysis.

Why it matters:

- Makes the product more useful on messy real-world documents.
- Improves downstream field detection.
- Creates a better user experience for archive documents.

Best-fit open-source building blocks:

- `OCRmyPDF` for OCR, deskew, rotate, and PDF/A output.
- `Tesseract` for traditional OCR.
- `docTR` when higher-quality layout-aware OCR is needed.

### 2.4 Template-Based Placement

This is the natural next feature once field detection exists.

What it does:

- Save signature placements as reusable templates.
- Reapply placement by document type, page size, or detected field.
- Support relative coordinates so templates survive page-size changes.

Why it matters:

- Makes recurring signing workflows fast.
- Improves consistency for business users.
- Bridges single-document signing to batch workflows.

### 2.5 Batch And Watch-Folder Workflows

What it does:

- Process a folder of documents in one pass.
- Apply the same signature/template to many documents.
- Watch a folder for new documents and auto-process them.

Why it matters:

- This is the clearest productivity multiplier for business users.
- It turns the app into a repeatable workflow tool instead of a one-off utility.

Implementation notes:

- Reuse the existing batch research already documented in [`docs/research/batch_processing.md`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/research/batch_processing.md).
- Keep progress, retry, and cancel behavior visible.

## 3. Computer Vision Features Worth Adding

These are the best CV-adjacent expansions beyond the current signature extraction flow.

### 3.1 Form And Field Detection

- Detect signature lines, initials boxes, checkboxes, and date fields.
- Suggest field type based on nearby labels and shape.
- Allow manual correction and reuse of corrected templates.

### 3.2 Page Layout Analysis

- Detect headers, body text, tables, images, and margins.
- Improve placement suggestions based on page structure.
- Help with smart redaction and annotation placement later.

### 3.3 Document Quality Scoring

- Score blur, skew, low contrast, and crop quality before extraction.
- Warn users when the image is likely to produce a poor signature result.
- Suggest fixes automatically.

### 3.4 Signature And Ink Quality Assessment

- Measure signature legibility, stroke continuity, and noise.
- Flag scans that need cleanup.
- Offer auto-enhancement presets.

### 3.5 Signature Consistency Or Anomaly Detection

- Compare a newly captured signature against prior saved signatures.
- Flag outliers as "review suggested" rather than making legal fraud claims.
- Useful for internal trust workflows and enterprise review.

### 3.6 Handwriting And Initials Extraction

- Extract initials, not just full signatures.
- Detect handwritten notes or markups around forms.
- Useful for legal, finance, and admin workflows.

## 4. Open-Source PDF And Document Intelligence Repos To Watch

### PDF Editing / Viewing

1. [`pypdfium2`](https://github.com/pypdfium2-team/pypdfium2)
   - Best fit for fast rendering and a lightweight commercial-friendly viewer stack.
   - Good when paired with `pikepdf` for editing.

2. [`pikepdf`](https://github.com/pikepdf/pikepdf)
   - Best fit for PDF read/write/repair/transform operations.
   - Strong default for merge, split, rotate, and structural edits.

3. [`PyMuPDF`](https://github.com/pymupdf/PyMuPDF)
   - Strong all-in-one PDF manipulation library with annotations, redaction, and conversion.
   - Best when license strategy is acceptable.

4. [`Stirling-PDF`](https://github.com/Stirling-Tools/Stirling-PDF)
   - Broad PDF toolbox with edit, sign, redact, convert, OCR, and automation features.
   - Interesting as a benchmark or optional self-hosted companion service, not the main desktop dependency.

### OCR And Layout Analysis

1. [`OCRmyPDF`](https://github.com/ocrmypdf/OCRmyPDF)
   - Excellent for searchable PDFs, deskewing, rotation, and OCR cleanup.

2. [`docTR`](https://github.com/mindee/doctr)
   - Strong OCR pipeline for text detection and recognition.

3. [`LayoutParser`](https://github.com/Layout-Parser/layout-parser)
   - Good for layout detection and document image analysis.

4. [`Tesseract`](https://github.com/tesseract-ocr/tesseract)
   - Reliable baseline OCR engine with broad language support.

### Digital Signing

1. [`pyHanko`](https://github.com/MatthiasValvekens/pyHanko)
   - Best open-source fit for PAdES-style digital signing, stamp fields, and certificate-driven workflows.
   - Especially relevant if the roadmap includes legal-grade signatures and certificate validation.

## 5. Product Expansion Paths Beyond PDF

These are the adjacent product lines that fit the existing asset base and brand.

### 5.1 Identity And Brand Assets

- Email signature generator.
- Digital business card generator.
- Signature style transfer or brand styling.
- Signature stamp and seal builder.
- Letterhead and invoice footer generator.

### 5.2 Workflow Products

- Document preparation assistant.
- Multi-party signing workflow.
- Approval and reminder system.
- Audit trail and completion certificate.

### 5.3 Trust And Compliance

- Digital certificate signing.
- Timestamping.
- Password protection.
- Redaction.
- Version history.
- Tamper checks.

### 5.4 Integrations And Distribution

- Browser extension.
- API/SDK for automation.
- Cloud sync and team libraries.
- Mobile capture via QR or camera.
- Self-hosted companion service for heavy PDF jobs.

## 6. Recommended Priority Order

### Phase 1: Best Near-Term Wins

1. Signature field identification.
2. Native PDF editing primitives.
3. Searchable PDF/OCR cleanup.
4. Template-based placement.

### Phase 2: Workflow Multipliers

5. Batch processing and watch folders.
6. Layout analysis and smart field anchors.
7. Document quality scoring.
8. Signature consistency/anomaly checks.

### Phase 3: Platform Expansion

9. Digital certificate support.
10. API/SDK and integrations.
11. Cloud sync and team libraries.
12. Identity/brand products such as email signatures and digital business cards.

## 7. Recommendation

If we want the strongest product path, the best order is:

1. Turn the current signature library into a PDF-aware placement engine.
2. Add signature field identification and template re-use.
3. Add OCR and layout intelligence to make that detection reliable.
4. Extend into broader PDF editing only where it supports the signing workflow.
5. Expand into identity products after the core workflow is stronger.

That keeps the product centered on its unique advantage:

- capture real signatures once,
- find where they belong,
- place them correctly,
- and keep the workflow local, private, and fast.

## 8. References

- [`pypdfium2`](https://github.com/pypdfium2-team/pypdfium2)
- [`pikepdf`](https://github.com/pikepdf/pikepdf)
- [`PyMuPDF`](https://github.com/pymupdf/PyMuPDF)
- [`OCRmyPDF`](https://github.com/ocrmypdf/OCRmyPDF)
- [`docTR`](https://github.com/mindee/doctr)
- [`LayoutParser`](https://github.com/Layout-Parser/layout-parser)
- [`Tesseract`](https://github.com/tesseract-ocr/tesseract)
- [`pyHanko`](https://github.com/MatthiasValvekens/pyHanko)
- [`Stirling-PDF`](https://github.com/Stirling-Tools/Stirling-PDF)

## 9. Related Repo Docs

- [`docs/analysis/ROADMAP_30_60_90_2026-06-17.md`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/analysis/ROADMAP_30_60_90_2026-06-17.md)
- [`docs/analysis/IMPLEMENTATION_EPICS_2026-06-17.md`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/analysis/IMPLEMENTATION_EPICS_2026-06-17.md)
- [`docs/analysis/SIGNATURE_FIELD_AND_PDF_EDITING_SPEC_2026-06-17.md`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/analysis/SIGNATURE_FIELD_AND_PDF_EDITING_SPEC_2026-06-17.md)
