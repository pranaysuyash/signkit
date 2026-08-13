# Technical Spec: Signature Field Detection and Native PDF Editing

**Project:** Signature Extractor / SignKit  
**Date:** 2026-06-17  
**Status:** Draft technical design

## 1. Design Principles

- Keep the current image extraction workflow intact.
- Add PDF intelligence as an extension of the existing signature asset.
- Prefer a local-first, open-source-friendly stack.
- Store field detections and placements as reusable data, not as UI-only state.
- Avoid a second parallel signing pipeline.

## 2. Proposed Architecture

```text
Desktop UI
  -> PDF Viewer / Overlay Layer
  -> Field Detection Service
  -> Template Placement Engine
  -> PDF Edit / Save Engine
  -> OCR Cleanup Pipeline
  -> Optional Compliance Signing Layer
```

### Core Libraries

- `pypdfium2` for page rendering and viewer-quality rasterization.
- `pikepdf` for structural PDF editing, merge/split/rotate, and save operations.
- `OCRmyPDF` for searchable PDF creation and cleanup.
- `Tesseract` or `docTR` for OCR and layout-aware text extraction.
- `pyHanko` later for digital signing and certificate workflows.

## 3. Data Model

### 3.1 Signature Asset

Represents an extracted signature saved by the user.

```text
SignatureAsset
- id
- source_document_id
- image_path
- alpha_mask_path
- created_at
- tags
- quality_score
```

### 3.2 Field Candidate

Represents a likely signature, initials, date, or checkbox region.

```text
FieldCandidate
- id
- document_id
- page_number
- field_type
- bbox
- confidence
- source_reason
- label_text
- confirmed_by_user
```

### 3.3 Placement Template

Represents a reusable field-to-signature mapping.

```text
PlacementTemplate
- id
- name
- source_document_fingerprint
- page_selector
- relative_bbox
- absolute_bbox
- anchor_type
- signature_asset_id
- created_at
- updated_at
```

### 3.4 Edit Operation

Represents a saved PDF edit action.

```text
EditOperation
- id
- document_id
- operation_type
- page_number
- payload
- created_at
```

## 4. Field Detection Pipeline

### Step 1: Render And Preprocess

- Render page image.
- Normalize orientation.
- Optionally OCR-clean scanned content.
- Convert to grayscale or contrast-enhanced form.

### Step 2: Generate Candidates

Candidate sources:

- OCR text cues:
  - "signature"
  - "sign here"
  - "initial"
  - "date"
- geometry cues:
  - horizontal lines
  - boxed areas
  - underlines near labels
- document cues:
  - form widgets
  - repeated field locations across pages

### Step 3: Score Candidates

Score each candidate using:

- label proximity
- region shape
- nearby text patterns
- field-type keywords
- page position heuristics
- document history/template match

### Step 4: Present To User

- Show ranked overlays.
- Let the user accept, reject, or edit the region.
- Persist the choice as template metadata.

### Step 5: Reuse

- Use confirmed fields to auto-place on the next document.
- Fall back to heuristics if no template exists.

## 5. Native PDF Editing Pipeline

### Supported Operations In The First Pass

- rotate page
- merge/split documents
- place signature image
- place text/date stamp
- redact region
- fill existing form fields
- flatten final output

### Edit Flow

1. Load PDF into viewer.
2. Convert user interaction into page coordinates.
3. Build an edit operation.
4. Apply the edit to a copy of the PDF.
5. Save as a new file.
6. Verify the output opens correctly.

### Coordinate Mapping

Use a consistent transform between:

- view pixels
- rendered page pixels
- PDF page units

The viewer must always know:

- page size
- zoom factor
- scroll offset
- rotation

Without that mapping, placements will drift on export.

## 6. OCR And Layout Intelligence

### OCR Cleanup

- Use `OCRmyPDF` for scanned PDFs that need searchable text.
- Use `Tesseract` as a low-friction baseline.
- Use `docTR` when layout-aware detection matters more than raw OCR speed.

### Layout Analysis Targets

- page blocks
- headings
- tables
- form areas
- blank signing zones

### Why This Matters

- Field detection becomes more accurate.
- Document quality warnings become actionable.
- Smart placement templates become more reusable.

## 7. Error Handling And Safety

- Never overwrite the original PDF by default.
- Keep edited output as a new file.
- If OCR fails, still allow manual placement.
- If field detection confidence is low, surface a manual fallback.
- If a PDF cannot be edited structurally, degrade to image stamping only.

## 8. Testing Strategy

### Unit Tests

- field candidate scoring
- coordinate mapping
- template serialization
- edit operation construction

### Integration Tests

- PDF render to overlay to save
- scanned PDF OCR to field detection
- template apply to another PDF
- export and reopen output PDF

### Manual Verification

- open a real contract PDF
- locate a field
- place a signature
- save a new file
- reopen in a standard viewer

## 9. Open Questions

- Should the first PDF editor use `pikepdf` only, or should `PyMuPDF` be enabled as an optional path?
- Should form-field detection support AcroForm widgets before heuristic detection?
- Should templates be document-fingerprint-based or user-labeled by workflow type?
- Should digital signing be introduced immediately after the editing MVP, or after batch automation?

## 10. Recommended Implementation Sequence

1. PDF rendering and coordinate transforms.
2. Heuristic signature field detection.
3. Placement templates.
4. Native edit/save pipeline.
5. OCR cleanup and searchable PDFs.
6. Layout-aware field ranking.
7. Batch automation.
8. Digital signing.

