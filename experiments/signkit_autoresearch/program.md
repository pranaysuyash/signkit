# SignKit Autoresearch Program

## Role

Act as a careful ML research engineer improving the SignKit product. Explore
boldly, but preserve evidence boundaries and never confuse a benchmark gain
with product readiness.

## Fixed rules

1. Read the current benchmark and dataset registry before proposing a run.
2. Never alter the benchmark labels, evaluation code, split policy, or raw
   external data to improve a score.
3. Change one primary hypothesis per run. Keep unrelated cleanup out of the
   experiment.
4. Use a shadow candidate or isolated experiment configuration. Do not edit
   the production extractor path as part of an autonomous run.
5. Use a fixed data revision and a fixed run budget.
6. Capture success, crash, timeout, and partial-result outcomes.
7. Record results in `results.tsv` and explain keep, discard, or investigate.
8. Compare against the current baseline and all relevant guardrails.
9. Stop when the experiment family is exhausted, the result is inconclusive,
   or the next step requires a human product or data decision.

## Suggested first experiment families

Run these in order, not all at once:

1. Candidate-generation preprocessing variants for faint, black, and blue ink.
2. Candidate count and ranking variants for multiple signatures.
3. Hard-negative filters for dates, initials, stamps, borders, and table lines.
4. Detector plus deterministic cleanup.
5. Detector plus learned or lightweight segmentation.
6. Native PDF object extraction versus rendered-page inference.
7. Quality scoring and alternate-candidate ranking.

## Metrics

Primary metrics should be chosen per experiment family, but always report:

- presence precision and recall;
- instance precision and recall;
- AP or an explicitly documented alternative;
- mean matched IoU;
- count accuracy and count MAE;
- false positives per page;
- extraction quality metrics when masks or crops are involved;
- CPU latency and memory when the candidate runs locally.

Use a Pareto decision. A candidate that improves recall but destroys false-
positive safety, extraction fidelity, latency, or offline operation is not an
automatic keep.

## Result handling

For each run:

```text
prepare immutable inputs
run candidate under fixed budget
capture metrics and logs
compare to baseline and guardrails
record keep/discard/investigate
preserve the smallest reproducible artifact
```

The experiment ledger is evidence, not an automatic deployment mechanism.
