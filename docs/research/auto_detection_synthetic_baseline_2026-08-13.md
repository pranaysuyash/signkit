# Auto-detection synthetic baseline

Date: 2026-08-13  
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`  
Commit under test: `ab2ae64`  
Evidence tier: Tier 2 local synthetic evaluation

## Purpose

This report records the first reproducible measurements for the shipped
traditional-CV signature candidate detector. It advances `RECON-24` by making
the existing synthetic fixtures measurable, while leaving the permissioned
corpus and product-threshold decisions open.

The results do not establish accuracy on human signatures, real documents,
production traffic, hosted execution, or assistive technology. The fixtures
are deliberately synthetic and are useful for regression detection and
evaluation-tool validation only.

## Inputs and protocol

The evaluator was run with IoU threshold `0.5`, at most two candidates per
image, and the detector's minimum confidence threshold shown below. Ground
truth boxes use the repository's `[x1, y1, x2, y2]` source-pixel schema.

```text
TMPDIR="$PWD/.codex-test-tmp" ./.venv/bin/python tools/evaluate_signature_corpus.py \
  --repo-root . \
  --corpus desktop_app/tests/fixtures/signature_edge_cases/metadata.json \
  --iou-threshold 0.5 --max-candidates 2 --min-confidence 0.4

TMPDIR="$PWD/.codex-test-tmp" ./.venv/bin/python tools/evaluate_signature_corpus.py \
  --repo-root . \
  --corpus desktop_app/tests/fixtures/signature_benchmark_v1/metadata.json \
  --split validation \
  --iou-threshold 0.5 --max-candidates 2 --min-confidence 0.75

TMPDIR="$PWD/.codex-test-tmp" ./.venv/bin/python tools/evaluate_signature_corpus.py \
  --repo-root . \
  --corpus desktop_app/tests/fixtures/signature_benchmark_v1/metadata.json \
  --split test \
  --iou-threshold 0.5 --max-candidates 2 --min-confidence 0.75
```

The edge corpus is the six-case regression set in
`desktop_app/tests/fixtures/signature_edge_cases/metadata.json`. Its metadata
states `synthetic only; no production-derived strokes` and covers blank,
low-contrast, tilted, noisy, partially occluded, and multi-signature cases.

The benchmark corpus is the twelve-case procedural set in
`desktop_app/tests/fixtures/signature_benchmark_v1/metadata.json`. Its metadata
states that it contains procedurally generated strokes with no production or
human data, and defines subject-disjoint train, validation, and test splits.
The validation and test measurements below each contain only three cases, so
they are held-out fixture checks, not statistically meaningful estimates.

## Results

| Corpus and split | Cases | Confidence | Presence precision / recall / F1 | Instance precision / recall / F1 | Mean IoU | Count exact accuracy | AP |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Edge regression | 6 | 0.40 | 1.00 / 1.00 / 1.00 | 1.00 / 0.833 / 0.909 | 0.840 | 0.833 | 0.833 |
| Synthetic benchmark validation | 3 | 0.75 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 0.784 | 1.00 | 1.00 |
| Synthetic benchmark test | 3 | 0.75 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 0.784 | 1.00 | 1.00 |

The edge regression's single instance false negative is the second signature
in `multi_signature`. The detector returned one candidate for two labeled
signatures, producing count absolute error `1` for that case. The other five
edge cases had one-to-one matches, with IoU values from approximately `0.774`
to `0.950`.

The evaluator reports all-points average precision from deterministic ranking
scores. Those scores are not calibrated probabilities and must not be exposed
as probability or confidence claims without calibration work.

## Interpretation and limits

The measurements support these narrow statements:

- The evaluator executes reproducibly against checked-in, hash-recorded,
  synthetic fixtures.
- The current detector handles the checked-in single-signature edge cases at
  the selected IoU threshold and exposes a known multi-signature miss.
- The subject-disjoint synthetic benchmark currently passes its three-case
  validation and three-case test slices under the recorded settings.

They do not support these statements:

- a `60 to 70 percent` real-document or human-signer accuracy claim;
- production recall, precision, IoU, latency, or failure-rate claims;
- safety or suitability for unattended auto-application;
- generalization beyond the generated backgrounds, stroke generator, image
  sizes, and fixture cases;
- a decision to promote `0.75` as the product default threshold.

## RECON-24 status

`RECON-24` is now `in-progress`, not done. The synthetic baseline closes the
local measurement-tool and regression-evidence subtask. Closure still requires
a permissioned labeled corpus or an explicit product decision to remain
synthetic-only, documented provenance and retention/deletion rules, an agreed
accuracy bar, a held-out evaluation protocol with failure classes, and a
review of whether any threshold or default should change. Real-GUI behavior
remains the separate `RECON-23` gate.

No user documents were collected, copied, or added to the repository for this
measurement.
