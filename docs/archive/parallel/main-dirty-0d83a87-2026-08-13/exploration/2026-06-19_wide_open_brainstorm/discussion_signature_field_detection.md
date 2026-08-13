# Discussion Packet: Signature Field Detection + Confidence-based Placement

Date: 2026-06-21

## Status

Current focus in this session is the feature:

- Signature field detection and confidence-based placement.

Decision status:

- Scope lock: in progress
- Positioning lock: workflow engine only, no compliance/legal claims
- Next outcome target: `proceed`, `prototype`, `pause`, `kill`, or `reframe`

## Current Working Definition

The feature should make signature placement feel like an assisted workflow rather than an automatic one.

- Detect likely signature fields on PDF pages.
- Show confidence using a clear visual scale.
- Let users accept, skip, or edit every placement before export.
- Persist successful placements as memory for reuse.
- Keep full auditable trace for actions taken and user overrides.

## Why we picked this now

1. It is the highest-leverage feature for the current thesis:
- extract -> recognize -> place -> review -> export -> reuse.
2. It reduces repeated manual positioning in recurring document families.
3. It improves trust by separating suggestion and final user decision.

What this avoids:

- silent auto-commit at medium or low confidence
- legal/compliance positioning
- claiming any binding or certification capability

## Design Decisions Under Discussion

### 1) Detection model

Chosen direction:

- start with deterministic heuristics, then layer ML-assisted confidence scoring if helpful.

Rationale:

- predictable behavior for mixed PDF quality
- easier debugging and faster first release
- better failure transparency for operators

Alternative considered:

- ML-first model.

Tradeoff:

- better raw recall in some layouts but noisier false positives without stronger UX guardrails.

### 2) Recommendation count per page

Chosen direction:

- show a maximum of 3 candidate areas per page.

Rationale:

- lowers cognitive overload
- keeps operator actions fast
- easier to benchmark correction rate

### 3) Confidence UI semantics

Chosen direction:

- use confidence bands (low/medium/high) with one visual language across all document types.

Rationale:

- prevents over-reliance on arbitrary percentages
- supports quick decision-making by non-technical users

### 4) Commit model

Chosen direction:

- explicit user action required for medium and low confidence.
- one-click apply for high confidence with clear “edit before commit” option.

Rationale:

- keeps trust and reversibility
- lowers bad placements on noisy scans

## Expansion Question: Other Form Field Types and Open-Source Parsers

Short answer:

- Yes, expand to other form fields, but on a strict staged path.
- Yes, add open-source parser inputs first, but only when each one preserves local-first behavior.

### What to support first

1. Keep signature engine ownership and expand field classes inside the same detector.
2. Add non-signature form fields as typed candidates (`text`, `checkbox`, `date`, `initial`, `initials` labels).
3. Feed these into workflow hints first, not automatic mutation.

### Recommended parser stack (ordered by default posture)

1. Built-in AcroForm/widget read through local PDF libs.
2. Rendered geometry + OpenCV heuristics.
3. `pdfplumber` layout extraction for text/line/box ranking (opt-in).
4. `pytesseract` or scan OCR hints (opt-in).

### Open-source parser check for this product

1. `PyMuPDF` / `fitz` style parsers: useful but gate on licensing, packaging, and opt-in policy.
2. `pikepdf` and `pypdf`: strong default candidates for local, open-source processing.
3. `LlamaParse`, `LiteParse`, `OmniParse` style services: likely valuable, but likely cloud/API based; treat as secondary/opt-in only because they are not default local-first and may not align with current privacy posture.
4. Do not make external API parsers the default for a privacy-first default workflow.

### Full edits / annotations / richer logs

This is the correct next layer after candidate placement stabilizes:

1. Add app-owned operation model for editable annotations/comments.
2. Serialize through adapters (`pypdf` for defaults, opt-in advanced path for heavier engines).
3. Keep logs by operation type, source candidate, and user decision.

This keeps logs and history coherent without crossing into legal/PKI claims.

## Online Parser Sweep (2026-06-21)

This packet now includes explicit package checking for local/online-first behavior:

- local-first: `LiteParse` (open parser with OCR and bbox outputs, no required cloud calls),
- cloud-first: `LlamaParse` (API/managed-style service),
- local broad multimodal ingestion: `omniparse` (`adithya-s-k`) (Linux + GPU-heavy + GPL-3.0 + model-usage constraints),
- GUI-first parsers (Microsoft/OmniParser, AlibabaResearch/AdvancedLiterateMachinery): interesting for scene OCR, not a direct form-field parser for our core loop yet.

For this feature:

1. expand detector classes first;
2. keep default parser path local and conservative;
3. add `LiteParse` as optional local enrich stage when required;
4. add API parsers only behind explicit opt-in controls and export logs.

## Decision Proposal for this Discussion

Proceed with:

1. broader form-field classification in the detector,
2. conservative local parser stack first,
3. cloud/API parser adapters as later optional extensions only,
4. annotation/log expansion in the next phase after we lock placement acceptance quality.

## Acceptance Criteria

1. Candidate detection returns at least one plausible field in common contract and form templates.
2. High-confidence auto-suggestions can be applied in one step.
3. Medium and low confidence suggestions require user confirmation.
4. Candidate overlays are visually consistent and legible on rotated/scaled pages.
5. All suggestion/accept/skip/edit actions are written to session logs.
6. Accepted placements can be replayed from memory on a later document in the same family.
7. User can revert last placement action quickly.

## Risks and Guardrails

1. Too many false positives on visually noisy scans.
Guardrail: keep conservative candidate cap and mandatory review for non-high confidence.
2. Overconfident UX can hide uncertainty.
Guardrail: explicit confidence bands and manual override visibility.
3. Model drift across PDF styles.
Guardrail: maintain fallback heuristic path and store failure patterns in recovery notes.

## What to avoid

1. Any claim that this makes the signature legally binding.
2. “Certainty language” in placement copy for medium/low confidence states.
3. Any silent background write path without user-acknowledged placement.

## Decision Checklist (next 30-minute round)

1. Should we use 2 confidence bands or 3?
2. Is page-level candidate cap enough or do we need document-type dynamic cap?
3. Do we persist candidate-level confidence or only final-accepted confidence?
4. Do we expose a “show why suggested” explanation panel in phase 1?

## Recommended Next Step

Proceed with a prototype spec using:

1. heuristic-first detection,
2. max 3 suggestions per page,
3. three confidence bands,
4. explicit confirm controls for non-high confidence, and
5. logging that captures suggestion source, score band, and user action.

Outcome target:

- if operator review time is reduced and false accept rate is acceptable, mark `proceed`;
- if not, mark `reframe` to reduce scope before build.

## References

- [scope specificity and capabilities](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-06-19_wide_open_brainstorm/scope_specificity_and_capabilities.md)
- [Discussion map](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-06-19_wide_open_brainstorm/discussion_map.md)
