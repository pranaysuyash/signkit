# Synthetic Benchmark Evidence: 2026-08-13

## Purpose

`tools/generate_signature_benchmark.py` creates a deterministic, privacy-safe
benchmark with twelve synthetic subjects split into six train, three
validation, and three held-out test subjects. The pages include negative,
single-signature, and multiple-signature cases. The subject IDs are explicit
so split leakage can be checked rather than assumed.

## Boundary

This benchmark is useful for regression, pipeline tuning, count behavior, and
split-policy checks. It is not evidence of real signer generalization,
production recall, legal approval, or human biometric performance. No human,
production, or third-party raw images are used.

## Reproduction

```bash
./.venv/bin/python tools/generate_signature_benchmark.py
./.venv/bin/python tools/validate_signature_corpus.py \
  --repo-root . \
  --corpus desktop_app/tests/fixtures/signature_benchmark_v1/metadata.json \
  --require-held-out \
  --require-subject-disjoint \
  --require-tag synthetic \
  --require-tag split:subject-disjoint \
  --require-tag signature_count:none \
  --require-tag signature_count:single \
  --require-tag signature_count:multiple
./.venv/bin/python tools/evaluate_signature_corpus.py \
  --repo-root . \
  --corpus desktop_app/tests/fixtures/signature_benchmark_v1/metadata.json \
  --split test
```

The test split is the only held-out performance slice in this artifact. It is
still synthetic and must not be combined with the private external corpus
metrics as if they were one population.

## Observed result

The 2026-08-13 held-out synthetic test slice contained three pages and four
ground-truth instances. It produced presence precision/recall `1.0/1.0`,
instance precision/recall `1.0/1.0`, count exact accuracy `1.0`, AP `1.0`, and
mean IoU `0.7843`. These are Tier 2/S1-style deterministic benchmark results,
not production or human-data evidence.
