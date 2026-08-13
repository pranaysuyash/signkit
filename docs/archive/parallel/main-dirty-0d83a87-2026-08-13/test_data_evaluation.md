# Labeled Signature Corpus Evaluation

Status: benchmark scaffold active; population-quality claim not established
Owner: Test Data Engineering
Last updated: 2026-08-12

## Why this exists

Regression tests answer whether known engineered cases still satisfy their
contracts. A labeled corpus answers a different question: how often the
extractor finds real target instances, how often its claims are wrong, and how
accurately it localizes them. These must not be conflated.

The current corpus is synthetic and intentionally small. Its results are a
reproducible baseline for implementation behavior, not a claim about accuracy
on a representative population.

## Evaluation contract

The canonical evaluator is
[`tools/evaluate_signature_corpus.py`](../tools/evaluate_signature_corpus.py).
It consumes the generated labels in
[`desktop_app/tests/fixtures/signature_edge_cases/metadata.json`](../desktop_app/tests/fixtures/signature_edge_cases/metadata.json).
Boxes use half-open pixel coordinates: `[x1, y1, x2, y2]`.

### Metrics

- Image-level presence precision: among images predicted to contain a
  signature, the fraction that have at least one ground-truth signature.
- Image-level presence recall: among images with at least one ground-truth
  signature, the fraction predicted to contain one.
- Instance precision/recall/F1: one-to-one ground-truth/prediction matches at
  IoU >= `0.50`; unmatched predictions are false positives and unmatched labels
  are false negatives.
- Localization: mean and median IoU over matched boxes only. Unmatched boxes do
  not receive an artificial IoU of zero.
- Count quality: exact count accuracy, mean absolute count error, and maximum
  count error per image.
- Average precision: intentionally unsupported for the current extractor,
  which returns one unscored heuristic box rather than ranked candidates.

IoU is intersection area divided by union area. Matching is greedy, global, and
one-to-one, selecting the highest-IoU eligible pairs first. The threshold is a
CLI parameter and defaults to `0.50`; changing it creates a different
evaluation configuration and must be recorded.

## Current synthetic baseline

Command:

```bash
./.venv/bin/python tools/evaluate_signature_corpus.py \
  --repo-root . \
  --corpus desktop_app/tests/fixtures/signature_edge_cases/metadata.json
```

Observed on 2026-08-12:

| measure | result |
| --- | ---: |
| cases | 6 |
| image-level presence precision | 1.0000 |
| image-level presence recall | 1.0000 |
| instance precision | 1.0000 |
| instance recall | 0.8333 |
| instance F1 | 0.9091 |
| matched mean IoU | 0.8396 |
| matched median IoU | 0.8991 |
| exact count accuracy | 0.8333 |
| mean absolute count error | 0.1667 |

The multi-signature case intentionally exposes the current one-box contract:
the extractor detects the image as positive and matches one of two labels, but
does not produce two independently localized predictions. This is a useful
engineering finding, not a failure of the benchmark.

Evidence classification: Tier 2 targeted runtime evaluation, test sensitivity
S1. The corpus is synthetic, small, and authored from the generator itself; it
does not establish Tier 5 production-like quality or a population estimate.

## Research and decision record

Scikit-learn defines precision as the ability not to label negative samples as
positive and recall as the ability to find positive samples; its documented
definitions are consistent with the TP/FP/FN formulas used here:
[scikit-learn model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html#precision-recall-and-f-measures).

The COCO evaluation implementation is the reference influence for explicit IoU
thresholding and one-to-one detection evaluation, but this project does not
adopt the full COCO dependency or AP contract while the extractor emits only a
single unscored box: [COCO API `cocoeval.py`](https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocotools/cocoeval.py).

Decision: use a dependency-free evaluator with explicit, inspectable metrics
that match the current extractor contract. Revisit COCO-style AP/mAP only when
the pipeline emits multiple ranked candidates with confidence scores and the
corpus contains representative annotations.

## Corpus expansion path

1. Keep the synthetic corpus as a deterministic regression and mutation probe.
2. Add a privacy-reviewed, held-out corpus with annotations for no-signature,
   one-signature, multi-signature, clutter, low contrast, rotation, occlusion,
   and scan noise strata.
3. Record annotator protocol, annotation version, disagreement handling, image
   dimensions, provenance, and train/development/evaluation separation.
4. Run the exact evaluator on the held-out split and report per-stratum plus
   aggregate results. Do not tune extractor thresholds on the held-out split.
5. If confidence-ranked candidate boxes are added, extend the evaluator with
   precision-recall curves and AP, preserving the current fixed-threshold
   metrics for continuity.

## Open risks

- The synthetic labels are approximate intended mark envelopes, not independent
  human annotations.
- The current auto-detection API returns one box, so multi-instance recall is
  structurally capped until the API evolves.
- No production-like corpus has been approved or evaluated.
- No confidence score exists, so threshold curves and AP are not meaningful.

