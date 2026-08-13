# SignKit S-Tier Product Expansion Map

## Purpose

This document expands the current SignKit work beyond signature extraction alone.

Signature datasets, benchmark corpora, and model experiments are inputs into the product-improvement program. They are not the scope of the product itself.

The goal is to make SignKit an S-tier product across its entire useful surface:

- best-in-class signature extraction and cleanup
- robust document and PDF handling
- frictionless signature reuse and insertion
- batch and workflow automation
- local-first desktop excellence
- web parity where it creates value
- ML/research infrastructure that continuously improves quality
- developer/API surfaces
- enterprise-grade controls where justified
- horizontal document-image capabilities that reuse the same primitives
- vertical workflows where signature-centric problems are valuable enough to own end to end

The governing principle is not "add more features." It is:

> Build a coherent product system in which every expansion either improves the core signature job, compounds reusable technical primitives, unlocks a high-value workflow, or creates a defensible product advantage.

---

# 1. S-Tier Product Definition

SignKit should eventually satisfy the following product-level standard:

A user can give it almost any normal document containing one or more signatures, and the product can reliably find, extract, clean, preserve, organize, reuse, insert, transform, export, and automate those signatures with minimal intervention while remaining fast, local-first where possible, transparent about uncertainty, and robust across messy real-world inputs.

S-tier is therefore not a model score.

It is the combined result of:

- extraction quality
- detection recall
- false-positive control
- stroke preservation
- PDF/document fidelity
- usability
- speed
- reliability
- privacy
- offline behavior
- automation
- batch handling
- integration quality
- graceful fallback
- observability
- recovery
- consistency between desktop and web
- benchmarked superiority over realistic alternatives

---

# 2. Expansion Model

The product should be developed along two simultaneous axes.

## 2.1 Vertical Expansion

Vertical expansion means owning more of the complete signature-centric workflow.

Examples:

document intake
→ signature discovery
→ extraction
→ cleanup
→ verification
→ organization
→ reuse
→ placement
→ export
→ audit
→ workflow completion

This moves SignKit from "signature extraction utility" toward a complete signature operations product.

## 2.2 Horizontal Expansion

Horizontal expansion means reusing SignKit's underlying technical primitives for adjacent document/image problems.

Examples:

- stamps
- seals
- initials
- handwritten marks
- logos
- document regions
- form fields
- checkboxes
- annotations
- handwritten notes
- document object extraction
- reusable transparent assets
- document cleanup
- image-region segmentation
- document transformation

Horizontal expansion should happen only when the primitive already exists or when the adjacency materially strengthens the core product.

---

# 3. Core Signature Intelligence

This remains the quality foundation.

## 3.1 Signature Detection

Research and benchmark:

- current deterministic CV
- YOLO-family detectors
- RT-DETR
- RF-DETR
- D-FINE
- DINO-family approaches
- lightweight mobile/desktop detectors
- hybrid candidate-generation pipelines
- detector ensembles
- VLM-assisted candidate verification where justified

Required cases:

- single signature
- multiple signatures
- signatures with initials
- signatures near dates
- signatures over text
- signatures over lines
- signatures touching borders
- signatures near stamps
- low-contrast signatures
- blue ink
- black ink
- pencil
- compressed scans
- photocopies
- photographed documents
- rotated pages
- skew
- perspective distortion
- noisy scans
- tiny signatures
- oversized signatures

## 3.2 Segmentation

Detection boxes are not sufficient.

Benchmark:

- adaptive thresholding
- Sauvola
- Niblack
- color-space segmentation
- connected components
- morphology
- GrabCut-style refinement
- detector-guided segmentation
- U-Net-like segmentation
- SAM-family refinement
- stroke-aware segmentation
- hybrid CV + learned masks

Primary metrics:

- stroke recall
- stroke precision
- contamination
- background leakage
- printed-text leakage
- stamp leakage
- missing thin strokes
- edge truncation

## 3.3 Cleanup

Research:

- anti-alias preservation
- thin-stroke preservation
- background removal
- paper-texture removal
- compression artifact removal
- line removal
- printed-text suppression
- stamp suppression
- shadow correction
- de-skewing
- perspective correction
- crop padding
- transparent-background reconstruction
- ink-color preservation
- monochrome conversion
- edge smoothing without stroke destruction

## 3.4 Quality Scoring

Every extraction should have an internal quality score.

Potential signals:

- detector confidence
- segmentation confidence
- foreground continuity
- stroke fragmentation
- crop-edge intersection
- background contamination
- text overlap
- stamp overlap
- suspicious aspect ratio
- unusually low foreground density
- extremely high foreground density
- duplicate candidate similarity

The product should be able to say internally:

- strong extraction
- usable extraction
- uncertain extraction
- likely failure

This enables better UX and smarter fallbacks.

## 3.5 N-Best Candidates

Do not force the product to make one irreversible decision.

For ambiguous cases:

- retain top candidates
- rank them
- show alternative crops
- show alternative masks
- allow quick correction
- learn from correction

This is substantially better than returning one bad result with high confidence.

---

# 4. PDF and Document Intelligence

The product should not blindly rasterize every PDF.

## 4.1 Native PDF Inspection

Before rendering:

inspect for:

- embedded raster images
- vector paths
- annotations
- AcroForm fields
- XObjects
- digital-signature fields
- image masks
- transparency groups
- page objects

Preferred extraction order:

native object extraction
→ native vector/image reconstruction
→ rendered-page analysis
→ vision detector
→ manual fallback

This can dramatically improve fidelity and speed.

## 4.2 PDF Rendering Strategy

Benchmark:

- PDFium
- MuPDF
- Qt PDF
- platform-native rendering where available

Evaluate:

- fidelity
- speed
- memory
- malformed PDF handling
- encrypted PDFs
- huge documents
- unusual page sizes
- transparency
- annotations
- incremental saves

## 4.3 Document Preprocessing

Add intelligent preprocessing:

- orientation detection
- page rotation
- deskew
- perspective correction
- contrast normalization
- noise estimation
- DPI estimation
- scan-quality classification

The pipeline should choose preprocessing conditionally, not blindly.

---

# 5. Signature Reuse and Asset Management

Once extracted, signatures should become managed reusable assets.

Capabilities:

- signature library
- multiple versions
- original vs cleaned
- transparent PNG
- WebP
- high-resolution export
- monochrome variant
- ink-color-preserving variant
- scalable/vectorized representation where reliable
- tags
- names
- usage history
- favorites
- duplicate detection
- archival
- provenance
- local encryption where appropriate

Potential product concept:

Signature Asset

A signature becomes a first-class reusable object rather than a temporary image.

---

# 6. Signature Placement and Document Completion

Extraction and insertion should form one coherent workflow.

Capabilities:

- drag/drop placement
- intelligent snapping
- page-aware positioning
- size presets
- aspect-ratio lock
- rotation
- opacity
- ink-color matching
- multi-page insertion
- repeated placement
- saved placement templates
- undo/redo
- document preview
- export without fidelity loss

Research:

- automatic signature-field detection
- inferred placement zones
- form-field awareness
- spatial alignment
- baseline alignment
- nearby label recognition

Examples:

"Signature"
"Authorized Signatory"
"Signed by"
"Customer Signature"
"Applicant"
"Director"

---

# 7. Batch Workflows

S-tier means one-document workflows should scale.

Capabilities:

- batch import
- folder watch
- batch signature discovery
- extract all signatures
- per-file review
- duplicate grouping
- bulk cleanup
- bulk export
- batch naming
- batch PDF insertion
- batch result summary
- resume interrupted jobs
- failure queue

Potential high-value use cases:

- document archives
- legal paperwork
- scanned historical files
- office digitization
- back-office operations
- insurance documentation
- banking operations
- real-estate paperwork

---

# 8. Automation Surfaces

The desktop UI should not be the only execution surface.

## 8.1 CLI

Examples:

signkit detect file.pdf
signkit extract file.pdf
signkit batch ./folder
signkit clean signature.png
signkit insert contract.pdf signature.png

Useful for:

- testing
- automation
- power users
- CI
- internal workflows

## 8.2 Local API

A local HTTP/process API can let other desktop tools call SignKit without cloud processing.

## 8.3 SDK

Potential later:

Python
JavaScript/TypeScript

Only after APIs stabilize.

## 8.4 Web API

Cloud/API should be optional and clearly separated from local-first functionality.

Use where:

- automation volume matters
- server-side workflows matter
- team access matters
- integrations justify it

---

# 9. Desktop Product Excellence

The desktop application itself needs S-tier product quality.

Required surfaces:

- clear home screen
- recent projects
- open documents
- signature library
- import
- batch jobs
- extraction history
- recent exports
- settings
- model/runtime controls where appropriate
- help
- guided onboarding

Quality expectations:

- instant launch
- responsive UI
- no unexplained blocking
- recoverable jobs
- autosave
- reliable undo
- keyboard shortcuts
- drag/drop
- native file associations
- predictable exports
- crash recovery
- clear errors
- accessible controls

---

# 10. Web Product

Web should not simply duplicate desktop.

It should exist where web creates leverage.

Possible roles:

- lightweight extraction
- project access
- collaboration
- remote processing
- account management
- integrations
- API keys
- team workspace
- batch job monitoring
- browser-based insertion
- shared signature library
- centralized policies

Avoid forcing cloud dependence onto workflows where local processing is superior.

---

# 11. ML / Model Lab

Model Lab should be a first-class engineering capability.

It should support:

- model registry
- experiment tracking
- dataset version
- preprocessing version
- training config
- checkpoints
- inference benchmark
- accuracy benchmark
- CPU benchmark
- memory benchmark
- model-size benchmark
- failure gallery
- hard-negative library
- reproducibility
- deployment status

Candidate experiment families:

- object detection
- segmentation
- classification
- embeddings
- OCR-assisted reasoning
- VLM verification
- super-resolution
- denoising
- vectorization
- quality estimation

---

# 12. Hard-Negative Mining

False positives deserve their own dataset.

Collect:

- handwritten dates
- initials
- scribbles
- logos
- stamps
- seals
- checkmarks
- underlines
- decorative fonts
- handwritten notes
- OCR noise
- document borders
- table lines

Workflow:

prediction
→ false positive
→ categorize
→ hard-negative corpus
→ retraining/recalibration
→ regression fixture

This can produce a large product advantage over models trained only on positive examples.

---

# 13. Active Learning

User corrections should eventually improve the system.

Possible loop:

prediction
→ correction
→ anonymized/local training candidate
→ difficult-example pool
→ annotation
→ experiment
→ benchmark
→ deployment

The product does not need to upload documents to achieve this.

Local correction metadata can still reveal:

- failure category
- bounding-box adjustment
- candidate selected
- threshold changed
- cleanup method chosen

---

# 14. Benchmarking Program

A single benchmark number is not sufficient.

## 14.1 Detection Metrics

- precision
- recall
- F1
- AP50
- AP50:95
- IoU
- count accuracy
- false positives/page
- missed signatures/page

## 14.2 Extraction Metrics

- stroke recall
- contamination
- boundary completeness
- text leakage
- stamp leakage
- background cleanliness
- alpha-mask quality

## 14.3 Robustness Metrics

Measure by:

- DPI
- JPEG quality
- blur
- rotation
- skew
- perspective
- brightness
- contrast
- ink color
- noise
- occlusion

## 14.4 Performance Metrics

- latency/page
- p50
- p95
- memory
- startup cost
- CPU utilization
- model size
- application size

## 14.5 Product Metrics

- successful extraction without correction
- correction rate
- time-to-export
- batch completion rate
- failure recovery
- user steps
- manual interventions

---

# 15. Controlled Degradation Lab

Generate controlled failure curves.

Examples:

clean
→ 300 DPI
→ 200 DPI
→ 150 DPI
→ 100 DPI
→ 72 DPI

and:

JPEG 100
→ 80
→ 60
→ 40
→ 20

and combinations:

low DPI + blue ink
low contrast + printed overlap
stamp + signature overlap
perspective + shadow
blur + photocopy noise

This lets us measure robustness instead of merely saying the product is robust.

---

# 16. Horizontal Document-Object Extraction

The underlying pipeline can support other objects.

Candidate objects:

- initials
- stamps
- seals
- logos
- handwritten notes
- checkboxes
- dates
- document photos
- handwritten fields
- signatures
- table regions
- diagrams
- embedded images

The product should not become a generic document platform prematurely.

Instead:

build reusable primitives first
→ expose adjacent objects only when quality/use-case economics justify them.

---

# 17. Signature Verification and Forensics

This is adjacent but distinct from extraction.

Potential capabilities:

- similarity comparison
- same-writer estimation
- duplicate-signature detection
- copied/pasted signature detection
- suspicious reuse detection
- image manipulation clues
- signature provenance comparison

This requires much stricter evaluation and should not be presented as definitive identity/authenticity determination without very strong evidence.

Useful near-term product framing:

"similarity and anomaly analysis"

rather than legal authenticity determination.

---

# 18. Vertical Workflow Expansion

Potential verticals should be evaluated by pain, frequency, willingness to pay, and workflow fit.

Candidates:

## Legal

- extract signatures from executed agreements
- compare signature pages
- organize signatories
- prepare signature assets
- batch archive processing

## Insurance

- signature presence checks
- extract signatures from forms
- incomplete-form detection
- signature-field workflows

## Real Estate

- agreement/document signature handling
- batch executed-document processing
- signature-page extraction

## Banking / Finance

- signature-region detection
- document QA
- check/document processing

## Government / Records

- archival digitization
- signature extraction
- metadata workflows

## Back Office / BPO

- document intake
- signature detection
- document completion checks
- bulk processing

Do not build vertical-specific product surfaces until the workflow proves sufficiently valuable.

---

# 19. Enterprise Expansion

Enterprise capabilities should be earned by actual use cases.

Potential:

- role-based access
- policy controls
- audit trail
- model version pinning
- data retention settings
- network-disabled mode
- offline deployment
- centralized configuration
- batch policies
- export policies
- admin reporting
- deployment packaging
- MSI/PKG enterprise deployment
- update channels
- SSO where justified

---

# 20. Privacy and Security

Local-first remains a product advantage.

Principles:

- process locally by default where feasible
- explicit cloud boundary
- never silently upload documents
- minimize retained document data
- separate signature assets from source documents
- encrypted local storage where warranted
- clear deletion
- predictable caches
- no hidden telemetry containing document content

---

# 21. Observability

The product should know why extraction failed.

Internal diagnostics:

- detector stage
- preprocessing selected
- candidates found
- candidate confidence
- segmentation result
- cleanup method
- quality score
- fallback triggered
- latency by stage
- model version
- extraction version

This enables debugging and model improvement.

---

# 22. Fallback Architecture

S-tier systems degrade gracefully.

Example:

native PDF extraction
→ ML detector
→ classical CV
→ alternate preprocessing
→ VLM verification
→ user-assisted region selection

Each fallback should be measurable.

We should know:

- how often it triggers
- why
- whether it improves the result
- latency cost

---

# 23. Vectorization Research

Potentially high-value, but dangerous if it changes signature geometry.

Research:

- contour tracing
- centerline tracing
- Bézier fitting
- SVG generation
- stroke reconstruction

Acceptance criterion:

vector representation must preserve signature identity/shape better than simple high-resolution raster scaling.

Never "beautify" away distinctive strokes.

---

# 24. Enhancement / Restoration

Research separately from extraction.

Potential:

- deblur
- super-resolution
- denoise
- contrast restoration
- stroke recovery

Keep:

original
cleaned
enhanced

Never overwrite the original extraction.

---

# 25. Product UX

Core workflow should require very few decisions.

Potential primary flow:

Import
→ SignKit finds signatures
→ Review
→ Save / Insert / Export

Advanced controls remain available but should not dominate the default experience.

Important UX surfaces:

- confidence
- alternate candidates
- before/after
- extraction adjustments
- cleanup strength
- crop padding
- transparent background
- destination action

---

# 26. Project and History Model

SignKit should eventually distinguish:

Document
Signature Asset
Extraction
Project
Export
Batch Job

This enables:

- recovery
- history
- comparisons
- repeat workflows
- auditability
- reusable assets

---

# 27. Quality Gates

No improvement should ship solely because it looks better on a few examples.

Required gates:

1. deterministic regression
2. synthetic held-out
3. external benchmark
4. degradation benchmark
5. hard-negative benchmark
6. performance benchmark
7. product workflow regression
8. sensitivity/mutation checks where relevant

Changes should be rejected if they create a material regression on important product dimensions.

---

# 28. Research Questions

High-priority questions:

- Is detector + deterministic segmentation better than learned end-to-end segmentation?
- Which detector gives the best desktop Pareto frontier?
- How much does hard-negative mining reduce false positives?
- Can native PDF object analysis bypass vision for meaningful cases?
- Does SAM-style refinement improve stroke preservation enough to justify its cost?
- Can a lightweight quality model predict bad extractions?
- Which preprocessing should be conditionally selected?
- Can extraction quality be evaluated automatically with useful correlation to human review?
- Can user corrections drive active learning without collecting source documents?
- How small can the ML stack become without meaningful accuracy loss?
- Is a VLM useful as a verifier rather than primary detector?
- What failure classes dominate actual product usage?

---

# 29. Expansion Prioritization

## P0: Product Quality Foundation

- extraction benchmark
- detection benchmark
- segmentation benchmark
- quality metrics
- robustness lab
- hard-negative corpus
- current pipeline profiling
- PDF-native inspection
- end-to-end regression suite

## P1: Signature Workflow Excellence

- signature library
- extraction quality scoring
- N-best results
- insertion workflow
- batch processing
- project/history model
- export fidelity
- intelligent signature-field detection

## P1: ML Research Infrastructure

- model lab
- experiment registry
- inference benchmarks
- failure galleries
- dataset registry
- hard-negative mining
- active-learning loop
- model packaging tests

## P2: Automation

- CLI
- local API
- batch automation
- watched folders
- integrations

## P2: Web

- selected browser workflows
- project access
- optional processing
- team capabilities

## P3: Horizontal Expansion

- initials
- stamps
- seals
- handwritten marks
- document-region extraction
- document cleanup primitives

## P3+: Specialized Verticals

Only after product evidence.

- legal
- insurance
- real estate
- finance
- archival
- BPO

---

# 30. What Not To Do

Avoid:

- treating dataset acquisition as the main project
- optimizing only for mAP
- switching entirely to ML because it is newer
- replacing deterministic extraction without benchmark evidence
- building cloud dependency into local workflows unnecessarily
- expanding into generic document AI before signature workflows are excellent
- shipping forensic claims without proper validation
- mixing synthetic benchmark claims with real-world claims
- adding enterprise complexity before actual enterprise requirements
- adding horizontal objects merely because detection is technically possible

---

# 31. Immediate Execution Program

The next implementation sequence should be:

## Workstream A: Product Benchmark

Establish a single reproducible scoreboard for:

- current SignKit pipeline
- candidate CV pipeline
- candidate learned detector
- hybrid detector + cleanup
- segmentation alternatives

## Workstream B: Failure Taxonomy

Run all available corpora and classify every failure.

Create categories and frequency.

## Workstream C: Model Lab

Run controlled detector/segmentation experiments.

Record:

- accuracy
- latency
- memory
- size
- deployment complexity

## Workstream D: PDF Intelligence

Measure how often signatures/images can be extracted without full-page vision.

## Workstream E: Product Workflow Benchmark

Measure:

document → usable signature → export

not merely model inference.

## Workstream F: UX

Reduce intervention and expose uncertainty appropriately.

## Workstream G: Vertical/Horizontal Opportunity Map

Evaluate every candidate expansion by:

- customer pain
- adjacency
- shared primitives
- differentiation
- cost
- product complexity
- revenue leverage

---

# 32. Task Ledger

## Explicit

- [ ] Build end-to-end SignKit product benchmark.
- [ ] Benchmark current extractor as baseline.
- [ ] Build failure taxonomy.
- [ ] Benchmark classical CV variants.
- [ ] Benchmark modern detector families.
- [ ] Benchmark segmentation alternatives.
- [ ] Benchmark hybrid pipelines.
- [ ] Add extraction-quality metrics.
- [ ] Add quality scoring.
- [ ] Add hard-negative mining corpus.
- [ ] Add controlled degradation benchmark.
- [ ] Audit native PDF extraction opportunities.
- [ ] Benchmark PDF rendering backends.
- [ ] Design signature asset model.
- [ ] Audit signature insertion workflow.
- [ ] Audit batch-processing architecture.
- [ ] Define project/history model.
- [ ] Design CLI surface.
- [ ] Define local API boundary.
- [ ] Audit web/desktop responsibility split.
- [ ] Build ML Model Lab structure.
- [ ] Add experiment registry.
- [ ] Add model packaging/performance benchmarks.
- [ ] Add fallback telemetry.
- [ ] Explore vectorization.
- [ ] Explore enhancement/restoration.
- [ ] Explore active learning.
- [ ] Explore signature verification/anomaly analysis.
- [ ] Evaluate horizontal document-object extraction.
- [ ] Evaluate vertical workflow opportunities.
- [ ] Define S-tier acceptance gates.

## Implicit

- [ ] Preserve originals through all enhancement workflows.
- [ ] Ensure every model improvement has a regression comparison.
- [ ] Track CPU-only performance.
- [ ] Track package-size impact.
- [ ] Track memory impact.
- [ ] Keep external benchmark datasets out of Git.
- [ ] Keep synthetic and real evidence clearly separated.
- [ ] Track model/dataset/preprocessing versions.
- [ ] Track difficult examples.
- [ ] Convert important production-like failures into permanent regression fixtures.
- [ ] Prevent cloud dependencies from silently entering local workflows.
- [ ] Prevent horizontal expansion from diluting the signature product.
- [ ] Re-evaluate priorities as benchmark evidence changes.

---

# 33. Decision Rule

For every proposed feature, model, workflow, or expansion ask:

1. Does it materially improve the core user outcome?
2. Does it create a reusable capability?
3. Does evidence show the current product needs it?
4. Does it strengthen differentiation?
5. What complexity does it add?
6. What does it replace?
7. How will we benchmark it?
8. What is the stop condition?

If those questions cannot be answered, the work should remain research rather than becoming product scope.

---

# 34. North Star

The long-term target is not "a signature extractor."

It is a high-quality signature and document-object intelligence system whose first vertical is the complete signature workflow, with reusable local-first document intelligence primitives underneath it.

Extraction remains the technical foundation.

The product advantage comes from owning the entire workflow and continuously proving that every layer is better.

---

# Addendum: Product and ML Discussion Reconciliation (2026-08-13)

The referenced product-improvement discussion is now recorded in
`docs/SIGNKIT_PRODUCT_ML_DISCUSSION_2026-08-13.md`. It resolves the scope
boundary that datasets are ML/test inputs while the actual target is the whole
SignKit product.

The first autoresearch implementation decision is also recorded. SignKit will
borrow the fixed-harness, bounded-budget, one-hypothesis, keep/discard loop from
[Karpathy's autoresearch](https://github.com/karpathy/autoresearch), but will
adapt it to a multi-metric document-vision problem. The protocol and current
baseline ledger live in:

- `experiments/signkit_autoresearch/README.md`
- `experiments/signkit_autoresearch/program.md`
- `experiments/signkit_autoresearch/results.tsv`

The current status is:

| Workstream | State | Evidence or next closure condition |
|---|---|---|
| Product expansion map | Established | This document and the linked discussion record are the product-direction source. |
| Synthetic benchmark | Baseline established | Subject-disjoint held-out evidence is recorded; synthetic claims remain separate. |
| External document benchmark | Baseline established | SignverOD is private and external-only; current recall/AP show domain shift. |
| Test sensitivity | Established for this stage | Seven hand-curated mutants killed at S3. |
| Unified product scoreboard | Active | Use one metric schema across synthetic, external, degradation, hard-negative, and workflow populations. |
| Failure taxonomy | Active | Classify the SignverOD misses and false positives before choosing a model. |
| Autoresearch runner | Protocol established, implementation pending | First run should be a shadow candidate-generation experiment, not a production rewrite. |
| Model and segmentation lab | Queued | Compare learned detection and segmentation only after the baseline and failure taxonomy are stable. |
| PDF-native intelligence | Queued | Measure native image/vector/annotation extraction before full-page vision. |
| End-to-end product benchmark | Queued | Measure document to usable asset to export, including intervention and recovery. |

This addendum is intentionally additive. It does not replace the existing
vertical, horizontal, PDF, workflow, desktop, web, enterprise, or S-tier gate
sections above.
