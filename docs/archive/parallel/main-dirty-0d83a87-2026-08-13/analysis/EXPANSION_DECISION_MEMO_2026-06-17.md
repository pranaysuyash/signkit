# Expansion Decision Memo: What To Build First

**Project:** Signature Extractor / SignKit  
**Date:** 2026-06-17  
**Status:** Decision memo  

## Summary

The best first expansion is:

1. Signature field identification.
2. Targeted native PDF editing primitives.
3. OCR cleanup and searchable PDFs.
4. Template reuse.

That sequence keeps the product centered on the app's strongest asset:

- extracting a real signature once,
- recognizing where it belongs in a document,
- and placing it safely into a PDF workflow.

This is a better first move than building a general PDF editor or a cloud platform because it is:

- closer to the current codebase,
- easier to validate locally,
- more differentiated,
- and less likely to pull the product away from its core identity.

## What We Should Start With

### 1. Signature Field Identification

Build the feature that finds likely signature, initials, and date fields in PDFs or scanned documents.

Why this first:

- It is the clearest extension of the current extractor.
- It gives the user immediate time savings.
- It makes the app feel intelligent without requiring a full Acrobat-style editor.
- It creates the input data for templates and automation later.

Minimum useful version:

- OCR labels like "sign here", "signature", "initial", "date".
- Shape detection for lines and boxes.
- Ranked candidate overlays with accept/reject.

### 2. Targeted Native PDF Editing

Add only the editing actions that support signing workflows:

- rotate
- merge/split
- stamp signature
- fill form fields
- redact regions
- flatten final output

Why this second:

- It closes the loop from detection to output.
- It makes the product useful even when a PDF has no obvious signature field.
- It creates a commercial feature path without becoming a generic editor.

### 3. OCR Cleanup And Searchable PDFs

Add scanned-PDF cleanup so field detection gets better on real-world documents.

Why this third:

- Many signature documents are scans.
- OCR improves both searchability and field detection.
- It makes the whole workflow more reliable without changing the user model.

### 4. Template Reuse

Let users save placement decisions and reuse them on similar documents.

Why this fourth:

- It turns a one-time action into a repeatable workflow.
- It is the bridge to batch processing.
- It is a strong premium feature, but only after detection works.

## Product Values

These are the values I would use to guide the roadmap:

- Local-first before cloud-first.
- Workflow completeness before feature breadth.
- Narrow, excellent tooling before generic replacement products.
- Reuse existing assets before inventing new ones.
- Open-source-friendly defaults unless the license tradeoff is clearly worth it.
- High-confidence automation only after the manual path is reliable.

## What Not To Build First

- A full Acrobat replacement.
- Cloud sync before the local PDF workflow works.
- Heavy ML before heuristics are validated.
- A second parallel signing system.
- Browser/API surface area before the desktop core is strong.

## Open-Source Repos To Watch

### PDF Rendering And Editing

- [`pypdfium2`](https://github.com/pypdfium2-team/pypdfium2) - fast PDF rendering and a good viewer core.
- [`pikepdf`](https://github.com/pikepdf/pikepdf) - structural PDF editing, repair, merge/split, and safe save operations.
- [`PyMuPDF`](https://github.com/pymupdf/PyMuPDF) - powerful editing/rendering option, but AGPL/commercial-license tradeoff matters.
- [`Stirling-PDF`](https://github.com/Stirling-Tools/Stirling-PDF) - useful benchmark for breadth; better as a companion/service idea than a desktop dependency.

### OCR And Layout

- [`OCRmyPDF`](https://github.com/ocrmypdf/OCRmyPDF) - scanned PDFs to searchable PDFs.
- [`docTR`](https://github.com/mindee/doctr) - deep-learning OCR with text detection and recognition.
- [`LayoutParser`](https://github.com/Layout-Parser/layout-parser) - document layout analysis for form and field detection.
- [`Tesseract`](https://github.com/tesseract-ocr/tesseract) - dependable OCR baseline with broad adoption.

### Signing And Trust

- [`pyHanko`](https://github.com/MatthiasValvekens/pyHanko) - digital PDF signing, PAdES-style workflows, and certificate-based signing.

### Vision Basics

- [`OpenCV`](https://github.com/opencv/opencv) - the right default for line detection, contour detection, cleanup, and geometric heuristics.

## Best Stack For The First Slice

If we want the lowest-risk stack for the first expansion slice:

- Viewer: `pypdfium2`
- Editor: `pikepdf`
- OCR cleanup: `OCRmyPDF`
- OCR fallback: `Tesseract`
- Layout-aware OCR: `docTR`
- Heuristics and geometry: `OpenCV`

This keeps the implementation local-first, commercially practical, and aligned with the current repo.

## Bottom Line

Start with signature field identification, then add the smallest possible PDF editing layer needed to place signatures safely.

That gives us the strongest product story:

**extract signature -> find field -> place signature -> save PDF -> reuse template**

Everything else should serve that loop, not distract from it.
