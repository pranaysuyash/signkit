# Parser Branch First Pass: Real PDF Fixtures

Date: 2026-06-21

This is the first concrete exploration pass for the parser/field-expansion branch.

It uses the real PDFs already present in the repo:

- [`assets/demo_document.pdf`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/assets/demo_document.pdf)
- [`desktop_app/tests/fixtures/sample.pdf`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/desktop_app/tests/fixtures/sample.pdf)
- [`desktop_app/tests/fixtures/signed_output.pdf`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/desktop_app/tests/fixtures/signed_output.pdf)
- [`desktop_app/tests/fixtures/native_form_benchmark.pdf`](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/desktop_app/tests/fixtures/native_form_benchmark.pdf)

## What we checked

1. Page count, text layer presence, and page geometry.
2. Native form widgets / AcroForm fields.
3. Existing signature-field detector output.
4. Native form-field editor output.

## Corpus Observations

### `demo_document.pdf`

- 6 pages.
- Text layer exists and is rich.
- No native form widgets were found.
- The current heuristic detector now returns a small, capped set of candidates on page 1 instead of flooding the page.

Interpretation:

- This is a text-native, template-like PDF with signature lines and form-like regions in plain text.
- It is useful for testing label/line heuristics.
- It still shows why confidence gating and per-page caps need to stay strict.

### `sample.pdf`

- 2 pages.
- No text layer detected by `pypdf` or `pdfplumber`.
- No native form widgets were found.
- The current signature detector returns no candidates.

Interpretation:

- This is effectively a blank or image-sparse fixture from the parser’s perspective.
- It is not yet a useful form-field benchmark because it does not exercise the detector well.

### `signed_output.pdf`

- 2 pages.
- No text layer detected by `pypdf` or `pdfplumber`.
- One image per page was detected by `pdfplumber`.
- No native form widgets were found.
- The current signature detector returns two `field_box` candidates, one per page.

Interpretation:

- This behaves like an image-only PDF with embedded page graphics.
- It is useful for testing raster and layout heuristics, but not native form widgets.

### `native_form_benchmark.pdf`

- 1 page.
- Native AcroForm widgets are present and readable.
- `PdfFormFieldEditor` detects `full_name`, `agree_terms`, `country`, and `plan`.
- The current signature detector keeps the widget signal and now caps heuristic noise to a small set on the same page.

Interpretation:

- This is the first true native-form benchmark in the repo.
- It proves the form-field pipeline works for text, checkbox, combo, and radio widgets.
- It also shows the signature detector and the form-widget detector should be treated as separate but cooperating layers, not one merged confidence stream yet.

## First-Pass Findings

1. The repo now has a real AcroForm benchmark, and the native form field path works.
2. The current detector is still mostly heuristic-driven on the non-form PDFs we have.
3. Text-native pages can create many false-positive field boxes if heuristics are not constrained.
4. The signature detector should not be treated as a surrogate for native widget detection.
5. Scan/image-only pages still need a broader benchmark set before parser ranking decisions are trustworthy.
6. Per-page heuristic caps materially improve legibility without removing the signal we do want.

## What This Means For The Exploration

The parser branch should now split into two tracks:

1. Native field extraction track:
   - real AcroForm / widget detection,
   - explicit field typing,
   - form fill support.
2. Heuristic fallback track:
   - signature lines,
   - rectangular form-like regions,
   - OCR hints for scanned documents.

## Immediate Next Experiments

1. Add or generate at least one PDF with actual AcroForm text/check/signature widgets.
2. Tighten the heuristic detector on text-native templates so it does not flood the UI.
3. Compare local parser options on the same benchmark set.
4. Decide whether native form fields belong in a shared field layer or remain in a form-specific module.

## Decision So Far

The exploration should continue.

- `proceed` for field taxonomy and local parser benchmarking.
- `prototype` for native form widget extraction.
- `pause` cloud/API parser defaults until the local baseline is trustworthy.
