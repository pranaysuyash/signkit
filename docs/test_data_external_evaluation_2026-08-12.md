# External Signature Corpus Internal Evaluation

Status: completed initial internal benchmark; production/legal review and independent population evidence remain open
Owner: Test Data Engineering
Date: 2026-08-12

## Scope and boundary

The user approved local, non-redistributive use of the Ultralytics Signature
Detection Dataset to improve the production extractor. Raw images, labels, the
archive, and generated reports remain outside the tracked repository at:

`/Users/pranay/Projects/Data_Science/computer_vision/proj6/.private/ultralytics_signature_v0.0.0/`

No source image or source annotation was copied into Git, a release artifact,
or a customer-facing product path.

## Provenance record

- Source: [Ultralytics Signature Detection Dataset](https://docs.ultralytics.com/datasets/detect/signature)
- Archive URL: `https://github.com/ultralytics/assets/releases/download/v0.0.0/signature.zip`
- Archive SHA-256: `6d7bfafd89bcfffb2fdf21f79df16e1988e30f5aa006b0a27d39b51f3bcae171`
- Intake date: `2026-08-12`
- Published license: `AGPL-3.0`
- Source split: 143 train images and 35 validation images, all 1920x1080
- Independent test split: none
- Subject-level consent and commercial provenance: not established by the published documentation
- Privacy decision: internal evaluation only, no redistribution; privacy/legal review is required before production deployment, external sharing, publication, or network-accessible use influenced by this corpus

## Reproduction commands

The archive is downloaded and extracted outside the repository. Conversion is
deterministic and stores only relative paths in the private metadata file:

```bash
./.venv/bin/python tools/import_ultralytics_signature_corpus.py \
  --dataset-root /absolute/path/to/private/ultralytics_signature/dataset \
  --output /absolute/path/to/private/ultralytics_signature/dataset/signkit_corpus.json \
  --archive-sha256 6d7bfafd89bcfffb2fdf21f79df16e1988e30f5aa006b0a27d39b51f3bcae171 \
  --intake-date 2026-08-12

./.venv/bin/python tools/validate_signature_corpus.py \
  --repo-root /absolute/path/to/private/ultralytics_signature/dataset \
  --corpus /absolute/path/to/private/ultralytics_signature/dataset/signkit_corpus.json \
  --require-tag external

./.venv/bin/python tools/evaluate_signature_corpus.py \
  --repo-root /absolute/path/to/private/ultralytics_signature/dataset \
  --corpus /absolute/path/to/private/ultralytics_signature/dataset/signkit_corpus.json \
  --output /absolute/path/to/private/ultralytics_signature/dataset/improved_report.json
```

The default synthetic coverage-tag gate is intentionally not used for this
external corpus. The `--require-held-out` gate is also intentionally not used:
the publisher does not provide an independent test split.

## Baseline and improvement evidence

The baseline was run before the production change. The improved run used the
same source images and labels.

- Baseline presence: precision `1.000`, recall `1.000`.
- Baseline localization at IoU 0.5: `0/178` matched; mean IoU `0.000`.
- Improved presence: precision `1.000`, recall `1.000`.
- Improved localization at IoU 0.5: `126/178` matched; mean IoU `0.898` among matched cases; median IoU `0.958`.
- Improved validation split: `27/35` matched; mean IoU `0.912` among matched cases and `0.703` with misses counted as zero.
- Improved bounded multi-candidate instance precision: `0.660`; recall: `0.708`; F1: `0.683` across the full corpus.
- Improved count exact accuracy: `0.927`; mean absolute count error: `0.073`.
- Average precision: `0.505` using all-points AP over deterministic per-image ranking scores; this is not a calibrated probability measure.

The production change adds a blue-ink candidate path using color dominance,
morphological stroke joining, and component scoring. The canonical
`auto_detect_signatures()` API returns up to two candidates at a minimum ranking
score of `0.75`; the existing grayscale envelope remains the fallback for
grayscale and synthetic inputs. Parameters were selected using the source
training split; the source validation split was used once for evaluation and
not for tuning.

## Interpretation and open work

This is Tier 3 integration evidence for the current extractor on a labeled,
production-like image flow, not Tier 5 production evidence and not a population
accuracy claim. The source corpus is single-class, single-box, photographic, and
has no independent test split. It does not establish multi-signature recall,
subject consent, commercial provenance, or legal fitness for a deployed product.
The AP score is a ranking benchmark only because candidate scores are not
calibrated probabilities.

Next closure requirements:

- Keep the synthetic corpus as the committed deterministic regression suite.
- Add a consented or contractually governed independent held-out corpus.
- Add an independently annotated multi-signature corpus before claiming
  multi-instance production quality, and calibrate candidate scores before
  using AP as a release threshold.
- Obtain privacy/legal review before any production deployment decision based on
  this external corpus.
- Investigate the host `ENOSPC` failure observed during a diagnostic shell
  here-document; no cache or data cleanup was performed because the data
  preservation boundary is not yet approved for deletion.

## Closure evidence for this work chunk

- Full local suite: `126 passed`.
- Focused extractor and data suite: `26 passed`.
- Focused web checkout/topology suite: `26 passed`.
- Desktop extraction module compiles after the concurrent indentation repair.
- Independent real-world held-out evidence, legal/privacy sign-off, and
  calibrated score thresholds remain intentionally open and are not represented
  as completed by the local test result.
