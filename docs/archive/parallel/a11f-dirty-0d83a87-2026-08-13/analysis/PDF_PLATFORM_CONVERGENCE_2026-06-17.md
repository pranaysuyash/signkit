# PDF Platform Convergence Plan

Date: `2026-06-17`

## Thesis

The long-term product is not just a signature extractor. It is converging into a
PDF workspace with four major surfaces:

- reading and rendering
- editing and annotations
- signing and form placement
- detection and understanding

That means the right strategy is not "pick one library." The right strategy is
to own the product architecture and combine a small number of focused upstream
projects behind a canonical capability layer.

## Why This Matters

The current repo already points in this direction:

- `desktop_app/pdf/stack_profile.py` centralizes runtime capability selection.
- `desktop_app/pdf/signer.py` handles signature placement and fallback saving.
- `desktop_app/pdf/field_detection.py` handles layout and OCR-assisted hints.
- `desktop_app/pdf/storage.py` already records audit logs.

So the next step is not a random dependency swap. The next step is to turn the
PDF stack into an explicit platform with owned roles.

## Commercial License Posture

The product strategy remains commercially viable only if we keep the default
stack on permissive or commercially usable open-source terms.

### Safe default set

- `pypdfium2` for rendering
- `pikepdf` for fallback signing and structural edits
- `pypdf` for pure-Python utilities and annotations
- `pdf.js` for browser rendering
- `pdf-lib`, `pdfmake`, `PDFKit` for browser/Node export and reporting
- `pdfplumber` for layout-aware extraction
- `docTR`, `Docling`, `pdf2image`, `EasyOCR` for document/OCR exploration
- `OCRmyPDF` if we want searchable PDF preprocessing

### Not default

- `PyMuPDF`

Reason:

- the project is better served by a baseline that does not depend on AGPL or a
  commercial license decision
- keeping `PyMuPDF` opt-in preserves optional access to its strengths without
  forcing the whole product into that posture

## Feature Map

| Feature | Current status | Likely owning layer |
| --- | --- | --- |
| Render PDFs | Implemented | `pypdfium2` primary, `pdf.js` as browser-view reference |
| Sign PDFs | Implemented | `pikepdf` fallback, `PyMuPDF` opt-in advanced path |
| Highlight and comments | Not yet exposed as a full UI | `PyMuPDF`, `pypdf`, `pikepdf` annotation support |
| Redaction | Not yet exposed as a full UI | `PyMuPDF` or `pikepdf` |
| Audit logging | Implemented at storage layer | App-owned JSONL logs |
| Field detection | Implemented at baseline | `pikepdf` metadata + `pypdfium2` rendering + optional OCR |
| Browser-safe export | Not yet implemented | `pdf-lib`, `pdfmake`, `PDFKit` depending on layout style |
| Structured doc understanding | Exploration stage | `pdfplumber`, `docTR`, `Docling`, `OCRmyPDF` |

## Upstream Candidates By Role

### Reading and rendering

- `pypdfium2` is the best current desktop renderer.
- `pdf.js` is the best browser-native renderer.
- `pdf2image` is useful as a conversion fallback, but not a primary viewer.

### Editing and annotations

- `pikepdf` is best for structural edits and deterministic save operations.
- `pypdf` is strong for pure-Python transforms and annotations.
- `PyMuPDF` is the most ergonomic for highlights, notes, redaction, and page-level editing, but remains opt-in because of licensing posture.

### Signing and form placement

- `pikepdf` is the default fallback path and keeps the OSS-default stack clean.
- `PyMuPDF` is the advanced path if the project explicitly enables it.
- `pdf-lib` becomes relevant for browser-side form filling and flattening.

### Detection and understanding

- `pdfplumber` is the best next step for layout-aware extraction.
- `docTR` is a strong model-based OCR option.
- `OCRmyPDF` is the right choice if searchable PDF preprocessing becomes a first-class product feature.
- `Docling` is the right choice if the product grows toward document intelligence and structured extraction.

### Browser-safe report/export generation

- `pdf-lib` is best when we want a browser-safe manipulation/export engine.
- `pdfmake` is best for declarative report layouts with headers, footers, and tables.
- `PDFKit` is best for lower-level programmatic control in Node/browser export flows.

## Combined Architecture

The product should own the following internal abstractions:

### 1. Capability registry

One canonical registry should answer:

- what library owns rendering
- what library owns structural edits
- what library owns annotations
- what library owns OCR/detection
- what library owns browser export

This already starts in `stack_profile.py`, but it should become the public
contract for the app.

### 2. Adapter layer

Each feature should have a small adapter with a stable internal API:

- `RendererAdapter`
- `AnnotationAdapter`
- `SignerAdapter`
- `DetectionAdapter`
- `ExportAdapter`
- `AuditAdapter`

The adapters should isolate the app from individual library churn.

### 3. Feature-specific pipelines

Use different pipelines for different jobs:

- view pipeline
- edit pipeline
- sign pipeline
- detection pipeline
- report/export pipeline

Do not force one library to own every role.

### 4. Policy flags

Keep explicit policy switches for advanced paths:

- `SIGNKIT_ALLOW_PYMUPDF_SIGNING`
- `SIGNKIT_PDF_SCAN_PREPROCESS`

Add future flags the same way instead of hiding behavior behind imports.

## Recommended Ownership By Feature

| Feature | Recommended owner | Why |
| --- | --- | --- |
| Render and preview | `pypdfium2` | Best desktop balance of speed and packaging |
| Sign and fallback save | `pikepdf` | OSS-default safe baseline |
| Advanced annotations / redaction | `PyMuPDF` opt-in | Best ergonomics, but not default |
| Browser-side PDF mutation | `pdf-lib` | Browser-safe, pure JavaScript |
| Declarative report creation | `pdfmake` | Better for structured reports with repeated sections |
| Programmatic PDF generation | `PDFKit` | Better when we want direct layout control |
| Layout extraction | `pdfplumber` | Better than a simple OCR wrapper for machine-generated PDFs |
| Deep OCR | `docTR` | Better model-based OCR path |
| Searchable-PDF preprocessing | `OCRmyPDF` | Strong pipeline for scan cleanup and OCR |
| Document intelligence | `Docling` | Best fit when the product moves beyond PDFs into structured documents |

## What The App Should Own Internally

These are product capabilities, not library dependencies:

- session state
- audit logs
- operation history
- annotation list persistence
- signature placement history
- user-facing policy and fallback messages
- report/export templates

That means the repo should own the workflow semantics even if the upstream
libraries change later.

## What To Build Next

If the goal is to converge this app into a real PDF workspace, I would build in
this order:

1. Annotation editor MVP
2. Highlight/comment persistence
3. Redaction workflow
4. Browser-safe export path
5. Layout-aware detection using `pdfplumber`
6. OCR enhancement using `docTR` or `OCRmyPDF`
7. Document intelligence path using `Docling`

## What Not To Do

- Do not let one library become the implicit owner of every PDF feature.
- Do not duplicate the rendering/signing/editing pipeline in parallel.
- Do not hide feature gating behind imports alone.
- Do not make browser export a side effect of desktop signing code.

## Current Coverage Gaps

The current app already covers:

- rendering
- signing
- detection
- audit logging

The current app does not yet fully cover:

- annotation UI
- comments/review threads
- redaction
- browser report generation
- structured document understanding

## How This Helps Long-Term

This approach gives us a product architecture that can combine multiple upstream
repos without turning into a dependency grab bag. Each library gets a narrow
role, and the app keeps the real product logic.

That is the durable path if we want to become a full PDF editing and document
workspace over time.

## Cross-References

- [PDF Library Exploration](PDF_LIBRARY_EXPLORATION_2026-06-17.md)
- [PDF Stack Setup](../PDF_SETUP.md)
- [Implementation Epics](IMPLEMENTATION_EPICS_2026-06-17.md)
