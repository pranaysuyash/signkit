# SignKit Product and ML Research Discussion

## Record

- Date: 2026-08-13
- Scope: internal product improvement, benchmarking, research, and learning
- Source discussion: ChatGPT conversation `6a7d798c-3ed8-83e8-9e8c-994df7d6f3c1`
- Related roadmap: `docs/SIGNKIT_S_TIER_PRODUCT_EXPANSION_MAP.md`
- Related test-data evidence: `docs/test_data_audit_addendum_2026-08-13.md`

This record turns the referenced discussion into project memory. It is a
decision and learning artifact, not a replacement for code, tests, or the
canonical product roadmap.

## 1. Scope correction

The initial discussion risked confusing two scopes. The correction is now
canonical:

- Signature datasets are inputs to testing and ML improvement.
- The product target is the complete SignKit product.
- The ML side project exists to improve product outcomes, not to become the
  product by itself.
- Internal use is the immediate objective. Public redistribution of raw
  benchmark data is not part of the objective.
- Basic provenance, privacy, source attribution, and storage controls still
  apply because internal-only use does not make unknown data suitable for
  accidental publication or customer workflows.

## 2. Product north star

SignKit should become a local-first signature and document-intelligence
product that can take a document or PDF through:

```text
intake -> native PDF inspection -> page normalization -> candidate discovery
-> signature localization -> pixel/stroke segmentation -> cleanup
-> quality scoring -> review or alternate candidate -> reusable asset
-> placement -> export -> audit/recovery
```

S-tier means the whole workflow is reliable, fast, understandable, recoverable,
and benchmarked. It does not mean that one detector has a high AP score.

## 3. Two-axis product expansion

### Vertical expansion

Own more of the signature workflow:

- document intake and normalization
- signature discovery and extraction
- cleanup and faithful preservation
- quality scoring and uncertainty handling
- signature asset management
- placement and PDF completion
- batch processing and resumability
- export, audit, and recovery
- local automation, CLI, and local API
- selected web and team capabilities where they add leverage

### Horizontal expansion

Reuse proven primitives for adjacent document objects only when they strengthen
the signature product or solve a demonstrated workflow:

- initials
- stamps and seals
- handwritten marks and notes
- logos and document regions
- form fields, checkboxes, and dates
- image cleanup and segmentation
- similarity or anomaly analysis, without unsupported authenticity claims

The rule is to build reusable primitives first and expose adjacent capabilities
only when evidence justifies their product complexity.

## 4. ML is a product-improvement system

The ML work is a first-class engineering program under the product roadmap.
It has three layers that must not be conflated:

1. Model: detector, segmenter, classifier, embedder, quality model, or verifier.
2. Pipeline: routing, preprocessing, fallback, validation, ranking, and
   recovery.
3. Data and configuration: datasets, annotations, transformations, thresholds,
   schemas, labels, benchmark splits, and experiment settings.

A better model cannot compensate for a broken pipeline or a weak benchmark.
A passing detector test cannot prove clean extraction. A clean crop cannot
prove a complete document workflow.

## 5. Product benchmark ladder

The benchmark program must keep evidence populations separate.

| Layer | Current role | Evidence boundary |
|---|---|---|
| Deterministic synthetic fixtures | Regression cases for blank, low-contrast, rotation, noise, occlusion, and multiple signatures | S1/S2 local behavior evidence; not real-world generalization |
| Subject-disjoint synthetic benchmark | Held-out pipeline and split evaluation | Three pages, four instances, presence and instance precision/recall `1.0/1.0`, AP `1.0`, mean IoU `0.7843`; synthetic only |
| SignverOD | Scanned-document localization and hard document context | 2,299 observed rows, 3,962 signature boxes, corrected AP `0.000584`, recall `0.0050`; strong domain-shift baseline, not a release gate |
| SigDetectVerifyFlow | Scale and multi-signature stress testing | Candidate for later acquisition and evaluation; no current result is claimed |
| Controlled degradation corpus | Robustness curves for DPI, blur, skew, shadows, compression, overlap, and ink variation | To be built and frozen before robustness claims |
| Internal production-like slice | Actual SignKit input distribution | Highest-value internal evidence; still to be created, redacted or consented, and versioned |
| End-to-end product benchmark | Document to usable asset to export | Required for S-tier product claims; not equivalent to detector AP |

Current source-controlled evidence is recorded in:

- `docs/test_data_benchmark_2026-08-13.md`
- `docs/test_data_external_research_2026-08-13.md`
- `docs/test_data_dataset_registry_2026-08-13.json`
- `experiments/signkit_autoresearch/results.tsv`

## 6. Research tracks

### Detection

Compare the current deterministic path with learned detectors such as
lightweight YOLO-family models, RT-DETR or D-FINE-style alternatives, and
document-specific baselines. Compare on recall, false positives per page,
multi-signature count accuracy, CPU latency, memory, and package size.

### Segmentation and cleanup

The product needs pixels and strokes, not only boxes. Compare adaptive and
color-space thresholding, connected components, morphology, stroke-aware
methods, lightweight learned masks, and detector-to-segmentation cascades.
Measure stroke recall, background contamination, printed-text leakage,
stamp leakage, alpha quality, and crop padding.

### Hard-negative mining

Maintain a categorized false-positive pool containing dates, initials, notes,
stamps, seals, logos, underlines, checkmarks, table lines, decorative fonts,
and OCR artifacts. Every important false positive should become either a
hard-negative example or a permanent regression fixture.

### Active learning

Keep correction metadata local by default. Useful metadata includes failure
category, candidate selected, box correction, threshold change, and cleanup
choice. Do not upload document bytes merely to learn from corrections.

### PDF intelligence

Benchmark the cheapest faithful route first:

```text
native image/vector/annotation extraction -> rendered-page analysis
-> learned detector -> classical fallback -> user-assisted region selection
```

The route must be observable so we know when each fallback triggers and whether
it improved the result.

### Quality and uncertainty

Return N-best candidates or an explicit review state when extraction quality is
uncertain. Useful signals include thin-stroke loss, stamp overlap, text
contamination, poor contrast, crop truncation, and conflicting detectors.

### Product workflow

Measure document -> usable signature -> export, including manual corrections,
time to completion, failure recovery, batch completion, and export fidelity.
The best model is not automatically the best product model.

## 7. Karpathy autoresearch adaptation

The project can use the core idea from Karpathy's
[autoresearch repository](https://github.com/karpathy/autoresearch): a small
agent-directed experiment loop with a fixed evaluation harness, a bounded run
budget, a single mutable experiment target, and a keep/discard decision based
on measured results.

We should not copy its language-model training assumptions into SignKit. The
original loop uses a fixed five-minute training budget and a single validation
objective. SignKit is a vision product with multiple coupled outcomes, so the
adaptation is documented in:

- `experiments/signkit_autoresearch/README.md`
- `experiments/signkit_autoresearch/program.md`
- `experiments/signkit_autoresearch/results.tsv`

The SignKit loop must use:

- frozen benchmark revisions and explicit train/evaluation separation;
- one candidate pipeline or configuration change per run;
- a fixed inference or wall-clock budget;
- primary metrics plus guardrails, not AP alone;
- automatic result capture and failure logs;
- comparison against synthetic, external, hard-negative, and performance
  baselines;
- no direct production promotion by an autonomous agent;
- no raw external data copied into the repository or web surfaces;
- no Git write operations by the experiment loop without explicit approval.

The correct acceptance rule is Pareto improvement or a documented tradeoff,
not blind optimization of one number.

## 8. Learning path for the project owner

This program is also a structured way to learn the ML and product system.

### Foundations

- image formation, pixels, color spaces, thresholding, morphology, contours
- coordinate systems, annotations, IoU, precision, recall, AP, calibration
- train/validation/test splits and subject or document leakage
- class imbalance and hard-negative sampling

### Production computer vision

- preprocessing selection and robustness curves
- object detection versus segmentation
- crop quality and alpha-mask reconstruction
- latency, memory, model size, CPU versus accelerator behavior
- deterministic fallbacks and failure observability

### Model experimentation

- transfer learning and augmentation
- detector architecture tradeoffs
- segmentation refinement
- confidence calibration and N-best ranking
- ablations, controlled experiments, and reproducibility
- Pareto frontiers across accuracy, fidelity, speed, and operational cost

### Product integration

- document/PDF route selection
- local-first boundaries and privacy-preserving learning
- review UX and uncertainty communication
- asset provenance and reversible transformations
- batch recovery, auditability, and desktop/web parity

The learning rule is to reproduce a baseline, change one thing, measure it,
explain the result, and preserve the experiment record before moving on.

## 9. Task ledger

### Closed or established

- [x] Create the broad vertical and horizontal S-tier product map.
- [x] Separate product scope from dataset and ML-input scope.
- [x] Build deterministic and subject-disjoint synthetic benchmarks.
- [x] Register external data candidates and preserve provenance fields.
- [x] Acquire and evaluate SignverOD outside Git and web surfaces.
- [x] Fix the grayscale fallback confidence-boundary defect.
- [x] Establish a seven-mutant S3 sensitivity gate.
- [x] Record the first external domain-shift baseline.
- [x] Define the SignKit autoresearch protocol and experiment ledger.

### Active next units

- [ ] Build a unified product scoreboard that runs every benchmark population
  through the same metric schema.
- [ ] Classify SignverOD false negatives and false positives by failure type.
- [ ] Build a controlled degradation generator and robustness report.
- [ ] Implement the first shadow candidate pipeline without changing the
  production extractor path.
- [ ] Run the first fixed-budget autoresearch batch on preprocessing and
  candidate-generation variants.
- [ ] Measure native PDF extraction opportunities before rasterizing pages.
- [ ] Add extraction-quality metrics beyond localization.

### Queued after the next evidence pass

- [ ] Train and compare at least one learned detector against the deterministic
  baseline.
- [ ] Compare detector plus deterministic cleanup against detector plus learned
  segmentation.
- [ ] Create a local hard-negative corpus from reviewed failures.
- [ ] Add quality scoring and N-best review behavior.
- [ ] Build the end-to-end document-to-export benchmark.
- [ ] Evaluate desktop, web, CLI, and local API responsibility boundaries.
- [ ] Evaluate horizontal objects and vertical workflows only after shared
  primitives and core workflow evidence are strong.

## 10. Decisions and boundaries

- Do not replace deterministic extraction with ML because ML is newer.
- Do not optimize only for mAP or a single public dataset.
- Do not mix synthetic and external results into one population claim.
- Do not let an autonomous experiment modify production behavior without a
  reviewed patch, tests, and benchmark evidence.
- Preserve original, cleaned, and enhanced representations separately.
- Keep local processing as the default where feasible and make any network
  boundary explicit.
- Keep forensic or authenticity language out of the product unless a separate
  high-evidence program supports it.
- Treat every model, pipeline, threshold, dataset, and benchmark change as a
  versioned product decision.

## 11. Current conclusion

The project is no longer primarily a dataset-acquisition task. It is a
SignKit Product and ML Research program. The highest-leverage sequence is:

```text
unified scoreboard -> failure taxonomy -> shadow candidate pipelines
-> autoresearch batch -> segmentation/cleanup comparison
-> PDF-native route benchmark -> end-to-end workflow benchmark
-> measured UX and vertical expansion
```

The current external baseline shows why this matters: a threshold bug could be
fixed quickly, but the remaining recall gap requires better candidates,
better data coverage, better segmentation, or a better pipeline. The evidence
must decide which one.

