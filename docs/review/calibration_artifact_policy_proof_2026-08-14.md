# Calibration artifact policy proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Scope: RECON-30 calibration fixture preservation and reproducibility
Evidence tier: Tier 2 artifact contract plus Tier 3 generated-fixture execution

## Decision

The calibration pipeline has three different artifact classes:

| Artifact | Git policy | Reason | Canonical owner |
| --- | --- | --- | --- |
| `scripts/build_calibration_dataset.py` | tracked source | deterministic fixture builder | repository source |
| `datasets/*/manifest.json` | tracked | labels, splits, schema, seed, generator, and asset policy | dataset contract |
| `datasets/*/calibration_report_*.json` | tracked | dated detector-output evidence and regression comparison | QA/research evidence |
| `datasets/*/notes.md` | tracked | provenance, use boundary, and regeneration command | research provenance |
| `datasets/*/images/*.png` and `datasets/*/pdfs/*.pdf` | ignored generated output | reproducible binaries, not a second editable source | builder output |

This policy keeps reviewable provenance and results in `main` while preventing
generated binary fixtures from becoming an unowned source of truth. A clean
checkout must run the builder before it runs the full manifest-based harness.
The manifest alone is not treated as a claim that ignored assets are present.

## Contract implemented

- `.gitignore` allows the two manifests, four reports, and two notes files to
  remain visible to Git while ignoring generated PNG/PDF assets.
- Each manifest records schema version, generator path, generator version,
  detector, sample count, seed, ground-truth classification, and artifact policy.
- The builder records the same metadata whenever it creates a manifest.
- The focused artifact-policy test builds two independent eight-sample datasets
  and requires byte-identical manifests, metadata, and eight generated assets
  per detector.
- The notes files state internal-use-only scope and the exact regeneration
  command.

## Verification

Focused command:

```text
./.venv/bin/python -m pytest \
  tests/test_calibration_artifact_policy.py \
  tests/test_calibration_harness.py -q
```

Result: `10 passed`.

The subsequent canonical full suite passed `526 passed, 4 skipped`; the four
skips are the known optional PyMuPDF and Qt event-loop boundaries.

The ignore boundary was checked directly:

- visible to Git: manifests, reports, and notes
- ignored by Git: `datasets/image_signatures/images/*.png`
- ignored by Git: `datasets/pdf_fields/pdfs/*.pdf`

The full generated fixture runs were then executed from the current manifests:

| Detector | Calibrator | Samples | ECE before | ECE after | ROC-AUC | PR-AUC | Boundary |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| image | isotonic | 120 | 0.3000 | 0.0283 | 0.8333 | 0.7996 | synthetic-labelled fixture |
| image | Platt | 120 | 0.3000 | 0.0608 | 0.8333 | 0.7996 | synthetic-labelled fixture |
| PDF | isotonic | 120 | 0.8289 | 0.0074 | 0.6032 | 0.2767 | synthetic-labelled fixture |
| PDF | Platt | 120 | 0.8289 | 0.7465 | 0.6032 | 0.2767 | inverted fit flagged |

The reports are evidence about the generated detector outputs only. They do
not establish real-signer accuracy, legal validity, production performance,
permission to use external documents, or safe unattended placement.

## Remaining gates

RECON-30 is closed for the local artifact-policy and reproducibility contract.
The following remain open under RECON-28 and the related product gates:

- permissioned real-world labeled documents and provenance;
- privacy, consent, anonymization, retention, and deletion governance;
- a product accuracy bar for showing and auto-placement;
- held-out evaluation with failure classes;
- PDF detector discrimination improvements before any unattended placement;
- CI execution from a clean checkout that regenerates ignored assets first.

The explicit-confirmation operator workflow remains the canonical fallback until
those gates are closed.
