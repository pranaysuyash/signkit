# Implementation Epics: PDF-Aware Signature Workflow

**Project:** Signature Extractor / SignKit  
**Date:** 2026-06-17  
**Status:** Draft backlog

## Epic 1: PDF Rendering And Viewer Foundation

### Goal

Provide a reliable PDF viewing layer for the desktop app.

### Scope

- Render PDF pages.
- Support zoom and pan.
- Map view coordinates to PDF coordinates.
- Load multi-page PDFs safely.

### Deliverables

- Page rendering service using `pypdfium2`.
- Viewer widget in the desktop app.
- Page index, zoom level, and viewport state.

### Acceptance Criteria

- A PDF page is visible at consistent quality.
- Click positions can be translated into PDF coordinates.
- Multi-page documents load without breaking the extraction workflow.

### Dependencies

- PDF library decision.
- Desktop UI integration point.

## Epic 2: Signature Field Identification

### Goal

Detect likely signature placement areas in PDFs and scanned documents.

### Scope

- OCR hint extraction.
- Line and box detection.
- Label-based ranking.
- Confidence scoring.

### Deliverables

- Candidate field detector.
- Overlay display for suggested fields.
- Accept/reject interaction.

### Acceptance Criteria

- At least one candidate field is identified on supported forms.
- Users can correct or dismiss a suggestion.
- Field metadata persists for later template reuse.

### Dependencies

- OCR pipeline.
- Viewer coordinate mapping.

## Epic 3: Template Placement Engine

### Goal

Reuse saved placements across recurring document types.

### Scope

- Save placements as templates.
- Reapply by page size, relative position, or field anchor.
- Track user-confirmed placement history.

### Deliverables

- Template storage format.
- Apply-template workflow.
- Relative coordinate mapping.

### Acceptance Criteria

- A template can be applied to a second PDF with a compatible layout.
- Templates survive page size changes when relative coordinates are used.

### Dependencies

- Field detection metadata.
- PDF rendering geometry.

## Epic 4: Native PDF Editing Primitives

### Goal

Enable practical PDF manipulation inside the app.

### Scope

- Rotate.
- Merge/split.
- Stamp signature images.
- Fill existing fields.
- Redact selected regions.

### Deliverables

- Editor module.
- Save/export pipeline.
- Safety checks to preserve the original file.

### Acceptance Criteria

- An edited PDF opens successfully after export.
- The original document remains untouched.
- Edits are visible in standard PDF viewers.

### Dependencies

- `pikepdf` or equivalent editing layer.
- Render/save architecture.

## Epic 5: OCR Cleanup And Searchable PDFs

### Goal

Improve scanned-document usability.

### Scope

- OCR text layer generation.
- Deskew and rotate correction.
- Scan cleanup pipeline.

### Deliverables

- OCR preprocessing job.
- Searchable PDF export.
- Scan quality warnings.

### Acceptance Criteria

- A scanned PDF becomes searchable.
- OCR output improves field detection on the same document.

### Dependencies

- OCR engine decision.

## Epic 6: Batch And Watch-Folder Automation

### Goal

Enable repeated processing at scale.

### Scope

- Process multiple files.
- Apply templates in bulk.
- Watch folders for new documents.

### Deliverables

- Job queue.
- Progress reporting.
- Retry/cancel behavior.

### Acceptance Criteria

- Multiple documents can be processed with one template.
- Failures are visible and recoverable.

### Dependencies

- Template engine.
- Native edit pipeline.

## Epic 7: Compliance-Grade Digital Signing

### Goal

Add legal-grade certificate-based PDF signing later in the roadmap.

### Scope

- Certificate import.
- Timestamping.
- PAdES signing.
- Verification.

### Deliverables

- Signing service.
- Certificate validation.
- Audit trail.

### Acceptance Criteria

- Signed PDFs can be validated cryptographically.
- The app distinguishes image-based signing from digital signing.

### Dependencies

- Compliance review.
- Signing library decision such as `pyHanko`.

## Epic 8: Product Expansion And Integrations

### Goal

Extend the signature asset into adjacent products.

### Scope

- Email signature generator.
- Digital business cards.
- API / SDK.
- Browser extension.
- Cloud sync.

### Deliverables

- Product direction spec.
- API boundary sketch.
- Shared asset model.

### Acceptance Criteria

- Adjacent products reuse the same signature asset and do not fork the workflow core.

### Dependencies

- Stable signature asset model.
- Workflow maturity.

