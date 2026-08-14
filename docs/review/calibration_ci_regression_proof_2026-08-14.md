# Calibration clean-checkout regression proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Scope: synthetic-labelled detector calibration regression only
Evidence tier: Tier 2 contract plus Tier 3 local generated-fixture execution

## Decision

The repository tracks calibration manifests and reports as reviewable evidence,
while generated PNG/PDF fixtures remain ignored. A clean checkout therefore
needs one canonical command that recreates the ignored assets, runs the real
detector adapters, and rejects unreviewed report drift. The command is:

```bash
./.venv/bin/python tools/run_calibration_regression.py --repo-root .
```

The gate reads the sample counts and seed from tracked manifest metadata,
regenerates both fixtures in an isolated temporary directory, checks that the
generated manifests equal the tracked manifests, runs image and PDF detection
with isotonic and Platt calibration, and compares all four generated reports
with the tracked baselines.

## Local result

The command passed locally with all four reports matching exactly:

```text
Calibration regression PASS: 4 tracked reports match
```

The focused contract tests passed `2` checks. The changed-baseline test fails
when a report value is deliberately altered, demonstrating that the gate is
sensitive to detector or generator drift rather than merely checking that a
report file exists. The canonical suite passed `543 passed, 4 skipped` after
the gate and documentation changes.

The CI implementation is a step in
`.github/workflows/test-data.yml` and reuses the project `.venv` dependencies.
The workflow has not been claimed as remotely executed by this local proof;
GitHub run completion remains a separate delivery gate.

## Evidence boundary

This gate proves reproducibility and regression detection on the generated
internal synthetic-labelled fixtures. It does not prove human accuracy,
permission to use external or customer documents, privacy/consent readiness,
production detector performance, legal validity, or a safe auto-placement
threshold. Those remain under `RECON-24` and `RECON-28`, with the product
accuracy-bar decision still required before any threshold promotion.
