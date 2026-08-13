# PDF field detection local contract proof

Date: 2026-08-13
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Scope: local PDF signature-field detection and auto-detection documentation contract
Evidence tier: Tier 2 local test contract, with synthetic evaluation kept separate

## Integrated slice

The preserved parallel implementation was reviewed and integrated into the
canonical local product because it improves the existing detector without
creating a second detection pipeline:

- one shared image-pixel to PDF-point coordinate transform serves rendered
  heuristics and OCR keyword hints;
- one shared overlap-dedupe helper serves dataclass and dictionary candidate
  representations;
- a generated labeled AcroForm field test verifies a known PDF-space rectangle;
- a documentation contract fails if the image or PDF detection modules disappear
  from the system-of-record document or if the shared helpers are forked.

The operator still confirms candidate placement. Confidence values remain
hand-ranked and uncalibrated.

## Evidence

Focused detector and documentation contracts:

```text
./.venv/bin/python -m pytest \
  desktop_app/tests/test_pdf_field_detection.py \
  tests/test_auto_detection_doc_coverage.py -q
15 passed
```

The positive labeled test generates a disposable PDF with a signature field at
`(120, 200, 240, 44)` PDF points, then requires a detected signature candidate
with confidence at least `0.90` and IoU at least `0.85`. The test deletes the
temporary PDF in a `finally` block.

The existing synthetic image evaluation was rerun separately:

- edge regression: 6 cases, instance precision/recall/F1 `1.000/0.833/0.909`,
  mean IoU `0.840`, with the known two-signature miss;
- subject-disjoint synthetic validation: 3 cases, instance recall `1.000`,
  mean IoU `0.784`;
- subject-disjoint synthetic test: 3 cases, instance recall `1.000`, mean IoU
  `0.784`.

## Boundary

This closes the local code, regression, and documentation contract for the PDF
field detector. It does not establish accuracy on human or production PDFs,
calibrated confidence, unattended placement safety, assistive-technology
behavior, cross-platform packaged behavior, hosted execution, or a product
threshold decision. Those remain separate under `RECON-24` and the broader
release gates.
