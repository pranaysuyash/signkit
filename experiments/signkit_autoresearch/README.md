# SignKit Autoresearch Lab

This directory adapts the useful control loop from Karpathy's
`autoresearch` to SignKit's document and signature pipeline.

## Why this is an adaptation

Karpathy's reference project is a compact single-GPU language-model loop with
a fixed training budget and one validation objective. SignKit is different:
it is a local-first vision product, its expensive step is often inference and
annotation evaluation, and its quality is multi-dimensional.

The lab therefore fixes the evaluation harness and varies one candidate
pipeline or configuration at a time. It does not let an agent silently change
the production extractor, benchmark definition, privacy boundary, or web
behavior.

## Current state

- Protocol: documented in `program.md`.
- Results ledger: `results.tsv`.
- Baseline: current SignKit plus synthetic held-out and SignverOD evidence.
- Autonomous runs: not started.
- GPU training: not required for the first preprocessing and candidate-
  generation experiments.

## Run contract

Every experiment must declare:

- run ID and hypothesis;
- candidate pipeline or configuration;
- code revision or immutable experiment snapshot;
- dataset IDs, revisions, hashes, and split policy;
- preprocessing and threshold configuration;
- fixed run budget;
- primary metrics and guardrails;
- result, failure log, and decision;
- next action or reason for stopping.

Raw external data stays in the protected external directory recorded by the
dataset registry. Only metadata, derived metrics, and non-sensitive failure
summaries belong in the repository.

## Promotion gates

An experiment can become a product candidate only if it:

1. beats or makes a clearly justified Pareto tradeoff against the current
   baseline on the target population;
2. does not regress deterministic synthetic coverage or hard-negative safety;
3. records CPU latency, memory, and packaging impact when relevant;
4. passes the affected focused tests and the full suite;
5. has a reviewed implementation patch and updated documentation;
6. is manually or runtime checked on the relevant local/web surface before
   being called production-ready.

No autonomous agent may commit, push, deploy, or promote an experiment without
explicit approval under the project Git and release rules.
