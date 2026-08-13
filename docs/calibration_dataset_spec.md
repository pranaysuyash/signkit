# Calibration Dataset — Collection & Schema Spec

**Status (2026-08-14):** No labeled dataset exists yet. The calibration harness
(`calibration/`) is **already runnable** with zero data via
`python -m calibration.run --self-test`, which exercises the full pipeline on a
deterministic synthetic set. This document specifies the *real* dataset needed to
produce genuine calibration for the two shipped detectors.

---

## 1. Why this exists

Both detectors emit **uncalibrated, hand-ranked confidence** (not probabilities)
that drive auto-placement thresholds (image path: ~0.75 to surface, 0.9 to
auto-place; PDF path: `field_auto_place_confidence` filtered at 0.9). See
`docs/AUTO_DETECTION_ML.md` Open Question #3. Before those thresholds can be
trusted (or promoted to a default), we need:

- a **labeled dataset** of real documents with ground-truth signature boxes, and
- a **product accuracy bar** (target recall / precision / IoU, false-positive
  ceiling) that the calibrated thresholds must meet.

This spec defines the dataset; the accuracy bar is a **decision** recorded in §8.

---

## 2. Two independent datasets (do not merge)

The detectors operate on different inputs, so calibration is done **per detector**
with a separate dataset each:

| Dataset | Detector module | Input asset | GT coordinate space | GT bbox format |
|---|---|---|---|---|
| PDF fields | `desktop_app/pdf/field_detection.py` | `.pdf` file | PDF points, origin bottom-left | `(x, y, w, h)` |
| Image signatures | `desktop_app/processing/extractor.py` | raster image | pixels, origin top-left | `(x, y, w, h)` |

The harness maps each detector's native output to a normalized
`(x, y, w, h)` `Candidate`/`GroundTruth`, so IoU is always computed in one
sample's own coordinate space. The two datasets are never mixed in one run.

---

## 3. Directory layout (proposed)

```
datasets/
  pdf_fields/
    manifest.json            # points at samples + ground truth
    pdfs/                   # the .pdf assets (git-ignored if large)
    notes.md                # collection log: dates, sources, exclusions
  image_signatures/
    manifest.json
    images/                 # the raster assets (git-ignored if large)
    notes.md
```

Assets (PDFs/images) are typically large and possibly privacy-sensitive, so keep
them **out of git** (add to `.gitignore`); commit only the manifests + `notes.md`
so the calibration run is reproducible from the manifest alone.

---

## 4. Manifest schema

A manifest describes **one** detector's samples. Validated by
`calibration/dataset.py::load_manifest` (run the harness; it raises
`DatasetSpecError` on malformed input).

```json
{
  "name": "pdf-fields-v1",
  "detector": "pdf",                // "pdf" | "image" | "synthetic"
  "iou_match_threshold": 0.5,      // candidate is "positive" if IoU >= this
  "samples": [
    {
      "sample_id": "doc-001",
      "asset_path": "datasets/pdf_fields/pdfs/doc-001.pdf",
      "split": "train",             // train | val | test | all
      "ground_truth": [
        { "label": "signature", "page_index": 0, "bbox": [120.0, 200.0, 240.0, 44.0] }
      ]
    }
  ]
}
```

- **`detector`** must be one of `pdf`, `image`, `synthetic`.
- **`bbox`** is always `[x, y, w, h]` in the detector's native space (see §2).
  - PDF: PDF points, origin bottom-left (matches `SignatureFieldCandidate.x/y/w/h`).
  - Image: pixels, origin top-left.
- **`page_index`** is required for PDF samples (a field lives on a page); omit for
  image samples.
- **`ground_truth`** may be empty — that is an explicit **negative sample** (a
  document with *no* signature field / signature). Negatives are essential; do not
  only collect positives.
- **`split`** drives train/val/test separation. If a manifest has no `test` split,
  the harness evaluates on the training data and warns.

### Image-dataset example

```json
{
  "name": "image-sigs-v1",
  "detector": "image",
  "iou_match_threshold": 0.5,
  "samples": [
    {
      "sample_id": "img-001",
      "asset_path": "datasets/image_signatures/images/img-001.png",
      "split": "test",
      "ground_truth": [
        { "label": "signature", "bbox": [84.0, 410.0, 220.0, 96.0] }
      ]
    }
  ]
}
```

---

## 5. Annotation guidelines

- **Label every signature / signature field** in each sampled document, not just
  the "best" one. Missed labels become false negatives and corrupt calibration.
- **Tight boxes.** Draw the box around the signature stroke / field rectangle; for
  PDF AcroForm fields use the field's actual `/Rect`.
- **Include negatives deliberately:** documents that look like they *should* have a
  signature but don't, and documents with only printed text/logos/stamps near where
  a signature would go (these are the false-positive fuel).
- **Diverse sources:** scanned contracts, flattened forms, photographed documents,
  multi-page PDFs, low-quality scans (so the OCR-hint path is exercised).
- **One box per ground-truth entry.** IoU matching is 1:1 against candidates; if a
  document has 3 signature lines, list 3 GT boxes.
- **Coordinate sanity:** PDF y grows upward (bottom-left origin); image y grows
  downward (top-left). The harness assumes the space matches the detector's native
  output for that `detector` key.

---

## 6. Sizing & splits (recommendation, not a hard gate)

- **Minimum viable:** ~200 documents per detector (≈70/15/15 train/val/test),
  with at least ~30% negatives.
- **Target:** 500+ documents per detector, matching the ML-phase dataset size
  already cited in `AUTO_DETECTION_ML.md` Phase 2.
- Keep the **test split untouched** for threshold derivation; only `train` is used
  to fit the calibrator, `val` to tune the accuracy bar.

Tooling: LabelImg / CVAT / Roboflow for images; for PDFs, export each field's
`/Rect` (and page) directly from `pikepdf` into the manifest to avoid manual
box-drawing — a `scripts/export_pdf_field_gt.py` is a good future helper.

---

## 7. Privacy & consent (blocking prerequisite)

This is not optional — it gates the whole ML/calibration track per
`AUTO_DETECTION_ML.md` Open Question #2:

- Collect only with explicit user **consent**; offer an **anonymization** path
  (strip PII pages, redact) before storage.
- Provide a **kill-switch** to delete a user's contributed documents on request.
- Store assets **locally / access-controlled**; never upload to a cloud ML API
  without a separate, explicit, reviewed decision (conflicts with the
  privacy-first positioning).
- Record consent scope in `notes.md` per batch.

---

## 8. Product accuracy bar — the decision to make

Calibration itself is mechanical once data exists. What it **cannot** decide is
the bar. Record these in `notes.md` (and the harness will derive thresholds from
them via `--target-recall` / `--target-precision`):

| Decision | Meaning | Suggested starting point |
|---|---|---|
| **Target precision** (show) | Min precision to *surface* a candidate in the picker | 0.90 |
| **Target recall** (auto-place) | Min recall to *auto-place* without confirmation | 0.90 |
| **IoU floor for auto-place** | Min overlap to count a placement as correct | 0.85 |
| **False-positive ceiling** | Max acceptable wrong auto-placements per 100 docs | TBD by product |
| **Default-on?** | Promote calibrated detector to default, or keep confirm-dialog? | Keep confirm until bar met |

---

## 9. How to run

```bash
# 1) Smoke-test the pipeline with no data (must be green in CI):
python -m calibration.run --self-test

# 2) Calibrate the PDF field detector on a real manifest:
python -m calibration.run --dataset datasets/pdf_fields/manifest.json \
    --detector pdf --report calibration_report.json

# 3) Derive thresholds for an agreed accuracy bar:
python -m calibration.run --dataset datasets/pdf_fields/manifest.json --detector pdf \
    --target-precision 0.90 --target-recall 0.90 --report calibration_report.json
```

The JSON report contains `uncalibrated` vs `calibrated` ECE, ROC/PR AUC,
`recall_at_1`/`recall_at_3`, the recommended `thresholds`, and an
`ece_improvement` delta. Commit the report (not the assets) as regression
evidence, and re-run it whenever the detector's confidence logic changes.

---

## 10. Next actions (checklist)

- [ ] Decide the §8 accuracy bar (product/PM).
- [ ] Stand up consent + anonymization + kill-switch (privacy).
- [ ] Collect ≥200 PDFs and ≥200 images with the §5 guidelines; export GT.
- [ ] Write `datasets/*/manifest.json`; commit manifests + `notes.md` (assets git-ignored).
- [ ] Run §9 step 2–3; record thresholds; wire them into the detector's
      auto-placement gating (replacing the current hard-coded 0.9).
- [ ] Add a CI job that runs the harness on the (committed) manifests so future
      detector changes can't silently regress calibration.
