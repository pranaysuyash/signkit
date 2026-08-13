# Long-Term PDF Workspace Architecture

Date: `2026-06-18`
Status: Architecture and research memo
Scope: Open-source-only PDF/document workspace direction for SignKit

## Executive Position

SignKit should not become a generic Acrobat clone. The durable long-term product
is a local-first document completion workspace:

```text
extract signature -> understand document/form -> place/fill/review -> export -> audit -> reuse
```

The app should own workflow semantics. Upstream libraries should own specialized
PDF mechanics.

This matters because the current codebase is already beyond "signature
extraction only." It now has PDF rendering, field detection, signature placement,
form-field work, templates, and audit logging. The next architectural step is not
to add more libraries randomly. The next step is to make the capability layer
explicit enough that each feature has one owner, one policy decision, and one
verification path.

## First-Principles Product Boundary

### What SignKit should own

These are product semantics, not upstream library responsibilities:

- signature asset model, library, vault, and provenance
- PDF/session state and active document lifecycle
- coordinate system normalization across renderer, viewer, signer, and templates
- placement history, template reuse, and field-anchor behavior
- user-visible capability policy, dependency status, and fallback messages
- audit logs, operation manifests, and export receipts
- annotation/comment/redaction review model
- approval states such as suggested, accepted, rejected, applied, exported
- local-first privacy and no-cloud-by-default behavior
- test fixtures and acceptance checks for each document operation

### What upstream libraries should own

These are implementation mechanics that should stay behind adapters:

- page rasterization and browser rendering
- PDF object read/write and repair
- annotation serialization
- image stamping and page content mutation
- form-field inspection/fill where commercially safe
- OCR and scan preprocessing
- certificate-based digital signatures
- browser-side PDF generation and export
- structured document parsing and model-based OCR

The key architectural rule is simple:

```text
One user workflow may combine multiple engines, but each engine gets one explicit role.
```

## Current Repo Truth

Static inspection shows these active or near-active surfaces:

- `desktop_app/pdf/renderer.py` uses `pypdfium2` for desktop page rendering.
- `desktop_app/pdf/field_detection.py` combines AcroForm/widget inspection,
  rendered-page heuristics, OpenCV signals, and optional OCR hints.
- `desktop_app/pdf/signer.py` uses a `pikepdf` baseline and an opt-in `fitz`
  path for image stamping.
- `desktop_app/pdf/stack_profile.py` is the emerging capability registry.
- `desktop_app/pdf/db_audit.py` stores PDF audit runs and event logs in SQLite.
- `desktop_app/pdf/template_store.py` stores reusable relative/field-anchored
  signature placements.
- `desktop_app/views/main_window_parts/pdf.py` exposes field detection, form
  detection, widget fill/sign, templates, bulk placement, and save flows.
- `desktop_app/processing/pdf_engine.py` appears to be an older/parallel PDF
  engine path using `pypdfium2` plus `pikepdf`.

Observed architecture gap:

- `desktop_app/pdf/form_fields.py` imports `fitz` unconditionally. That conflicts
  with the newer "PyMuPDF is opt-in" policy in `desktop_app/pdf/stack_profile.py`
  and `docs/PDF_SETUP.md`.

Observed documentation drift:

- Some older docs still describe PyMuPDF as a normal bundled/default dependency.
- The newer `docs/PDF_SETUP.md` correctly treats PyMuPDF as opt-in because of
  AGPL/commercial licensing.
- `docs/analysis/PDF_LIBRARY_EXPLORATION_2026-06-17.md` labels `docTR` as MIT in
  one table, but current primary sources show `docTR` as Apache-2.0.

## Capability Matrix

| Capability | Current repo coverage | Recommended owner | Default posture | Licensing note |
| --- | --- | --- | --- | --- |
| Desktop PDF rendering | Implemented | `pypdfium2` | Default | Verified Apache-2.0 / BSD-3-Clause from PyPI. |
| Browser PDF rendering | Not implemented | `pdf.js` | Deferred | Verified Apache-2.0 from Mozilla GitHub. Use for future web/hybrid viewer only. |
| Signature image stamping | Implemented | `pikepdf` baseline; `PyMuPDF` opt-in | Default via `pikepdf`; opt-in for `PyMuPDF` | `pikepdf` MPL-2.0 is commercially usable; `PyMuPDF` is AGPL/commercial and should not be default. |
| Structural PDF edits | Partial | `pikepdf`, with `pypdf` for pure-Python transforms | Default | `pikepdf` handles repair/rewrite/low-level edits; `pypdf` BSD-3-Clause is good for split/merge/rotate/annotations. |
| Native form inspection/fill | Partial | `pikepdf`/`pypdf` where possible; `PyMuPDF` opt-in for ergonomic widgets | Default inspection, opt-in advanced editing | Current unconditional `fitz` import must be removed before default posture is true. |
| Field/placement detection | Implemented baseline | App-owned detector using `pikepdf`, `pypdfium2`, OpenCV, optional OCR | Default | OpenCV is Apache-2.0; OCR should remain opt-in. |
| OCR keyword hints | Implemented opt-in hooks | `pytesseract` plus system Tesseract | Opt-in | `pytesseract` is Apache-2.0; system binary packaging still matters. |
| Searchable scanned PDFs | Not implemented | `OCRmyPDF` | Deferred / opt-in | MPL-2.0; commercially usable, publish modifications to OCRmyPDF itself. |
| Highlighting | Not implemented as full UI | `pypdf` default annotation adapter | Next default slice | `pypdf` has documented annotation APIs and BSD-3-Clause licensing. |
| Comments / sticky notes | Not implemented | App-owned comment model plus `pypdf` annotations | Next default slice | Store app comment state separately from serialized PDF annotations. |
| Redaction | Not implemented | App-owned guarded workflow; engine TBD, likely `pikepdf` baseline and `PyMuPDF` opt-in | Deferred | Must verify content removal, not just visual covering. |
| Audit logging | Implemented | App-owned SQLite/JSONL-style audit layer | Default | Library-independent product capability. |
| Certificate/PAdES signing | Not implemented | `pyHanko` | Deferred / opt-in | MIT; distinct from visible image stamping. |
| Layout-aware extraction | Not implemented | `pdfplumber` | Opt-in after annotation layer | MIT; best for machine-generated PDFs and field-ranking signals. |
| Deep OCR | Not implemented | `docTR` or `EasyOCR` | Deferred | `docTR` Apache-2.0; EasyOCR Apache-2.0 but heavier PyTorch footprint. |
| Document intelligence | Not implemented | `Docling` | Deferred | MIT codebase; model package licenses must be checked per model. |
| Browser-side PDF mutation | Not implemented | `pdf-lib` | Deferred | MIT; best when a real browser/web surface exists. |
| Declarative report generation | Not implemented | `pdfmake` | Deferred | MIT; best for structured audit/report PDFs. |
| Programmatic PDF generation | Test/dev only via `reportlab` | `ReportLab` Python, `PDFKit` JS depending surface | Opt-in by surface | ReportLab BSD; PDFKit MIT. |

## Candidate Comparison By Role

### Rendering

`pypdfium2` should remain the default desktop renderer. It is already in the
repo and has the right role: fast rasterization into the Qt viewer. `pdf.js`
should not replace it inside the desktop app unless the UI becomes browser-based
or hybrid. `pdf2image` is useful as a fallback/conversion tool, but it adds
Poppler packaging concerns and is weaker as an in-process viewer foundation.

Default: `pypdfium2`

Opt-in/deferred: `pdf.js` for web/hybrid, `pdf2image` for conversion fallback

Avoid as default: `PyMuPDF` for rendering because license posture is wrong for
the open-source-only default.

### Structural Editing

`pikepdf` is the right default for low-level object work, repair, rewrite,
metadata, and fallback save operations. `pypdf` should be added as a focused
adapter for common pure-Python tasks: split, merge, rotate, annotations, simple
metadata, page transforms. They are not redundant if their roles are explicit:

- `pikepdf`: correctness, repair, low-level PDF surgery, deterministic rewrite.
- `pypdf`: safer high-level Python API for routine page/annotation operations.

Default: `pikepdf`, add `pypdf` for annotation/utility adapter

Avoid: a second custom stream-writing pipeline outside the canonical PDF adapter.

### Signing

The product must distinguish image-based "visible signing" from cryptographic
digital signing.

- Visible signing: place an extracted signature image and export an audited PDF.
- Digital signing: certificate-backed PDF signature, validation, timestamps, and
  PAdES-style workflows.

For visible signing, keep the current `pikepdf` baseline. PyMuPDF is useful but
must stay opt-in. For digital signing, `pyHanko` is the correct future package,
not another image-stamping path.

Default: visible signing via current app + `pikepdf`

Opt-in later: `pyHanko` for digital signatures

Avoid: marketing image stamping as cryptographic/legal-grade signing.

### Fields, Forms, And Placement Detection

Field detection is a product-owned ranking problem, not just a PDF parser
problem. It should combine multiple evidence sources:

- native AcroForm/widget metadata
- rendered geometry: lines, boxes, whitespace, labels
- OCR keyword hints for scans
- user correction history
- template anchors

The current `SignatureFieldDetector` is aligned with this. The long-term upgrade
is to add a layout-aware extraction adapter, probably `pdfplumber`, for
machine-generated documents. This gives text/rect/line evidence without jumping
straight to ML.

Default: current detector plus `pikepdf` and `pypdfium2`

Opt-in next: `pdfplumber` for layout-aware ranking

Deferred: `Docling` or `docTR` until real-world samples prove the heuristic layer
is not enough.

### Annotations And Comments

This is the best next durable expansion because it turns the PDF tab into a
document workspace without duplicating rendering, signing, or detection.

The app should own an annotation/comment operation model:

```text
operation_id
document_id / file hash
page_index
type: highlight | note | rectangle | approval | redaction_candidate
rect / quadpoints
author/session
status
created_at / updated_at
export_state
```

Then one adapter serializes supported items into PDF annotations. `pypdf` is the
best default starting point because it is commercially safe and has documented
annotation APIs. PyMuPDF can remain an opt-in advanced adapter for richer
annotation and redaction ergonomics.

Default next: app-owned annotation model + `pypdf` adapter

Avoid: painting annotations only in the Qt overlay without persistence/export.

### Redaction

Redaction is high risk. It must not be treated as a drawing feature. The product
needs two separate concepts:

- redaction candidate: a visible proposed region pending review
- applied redaction: content actually removed, with verification evidence

The default implementation should wait until the app has:

- annotation/comment operation model
- audit event model for pending/applied redactions
- export verification that text/image content is not recoverable from the region

Deferred: real redaction workflow

Avoid: black rectangle overlays marketed as secure redaction.

### OCR And Document Intelligence

OCR should enter in layers:

1. Keyword OCR hints for scanned forms using `pytesseract`.
2. Searchable-PDF preprocessing using `OCRmyPDF`.
3. Model-based OCR using `docTR` only when needed.
4. Full structured document understanding with `Docling` only when the product
   moves beyond signing/forms into document extraction or AI workflows.

Default: OCR off unless explicitly enabled

Opt-in: scan mode for users who need it

Deferred: heavy model pipelines

### Browser-Side PDF Generation And Editing

Browser-side packages are not currently part of the desktop core. They become
valuable only if SignKit grows a web/hybrid surface or local browser export
tools.

- `pdf-lib`: best for browser-safe mutation, images, pages, forms.
- `pdfmake`: best for declarative documents with repeated sections and tables.
- `PDFKit`: best for low-level drawing and layout control in Node/browser export.

## What Should Be Preserved In The Repo

These are the durable artifacts this memo depends on:

- `desktop_app/pdf/stack_profile.py`
- `desktop_app/pdf/renderer.py`
- `desktop_app/pdf/field_detection.py`
- `desktop_app/pdf/signer.py`
- `desktop_app/pdf/storage.py`
- `desktop_app/pdf/template_store.py`
- `desktop_app/views/main_window_parts/pdf.py`
- `docs/PDF_SETUP.md`
- `docs/analysis/PDF_LIBRARY_EXPLORATION_2026-06-17.md`

## What Not To Do

- Do not turn every PDF capability into one mega-library dependency.
- Do not hide capability policy behind ad hoc imports.
- Do not make browser export a side effect of the desktop signing pipeline.
- Do not add a second parallel PDF architecture next to the canonical one.

## Cross-References

- [PDF Stack Setup](../PDF_SETUP.md)
- [PDF Library Exploration](PDF_LIBRARY_EXPLORATION_2026-06-17.md)
- [PDF Platform Convergence](PDF_PLATFORM_CONVERGENCE_2026-06-17.md)
