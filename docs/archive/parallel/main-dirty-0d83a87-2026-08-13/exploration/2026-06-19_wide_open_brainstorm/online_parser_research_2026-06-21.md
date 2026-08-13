# Online Parser Research (motto_v3 + wide-open-brainstorm lane)

Date: 2026-06-21

This page is the current package-and-ecosystem check for online parser options, with a focus on:

- native/local suitability,
- legal/practical fit for commercial distribution,
- and whether the parser helps signature/field workflow work.

## What we can discuss and test next

1. Parser capability depth for form fields, signatures, text blocks, and layout.
2. Local-first vs API-first default behavior.
3. Licensing impact for distribution in a commercial desktop utility.
4. Optional optionality pattern: default conservative local stack + opt-in external engine for hard PDFs.

## Current evidence snapshot

### 1) `LiteParse` (`run-llama/liteparse`)

- Class: local document parser with OCR and layout/bbox outputs.
- Signal from source: advertised as standalone, local-first, no LLM dependency, no cloud default path.
- Practical use in this app:
  - Good first-class fit as the local enrichment layer.
  - Useful where we need bounding boxes for confidence overlays and candidate ranking.

### 2) `LlamaParse` (LlamaIndex API service)

- Class: API-first document parsing service (`upload/stream`, API clients, web UI, enterprise-style pricing and tiers).
- Signal from source: presented as managed cloud/parser service.
- Practical use in this app:
  - **Do not default-enable**.
  - Keep as optional / enterprise-integration adapter only, behind explicit user selection and policy gates.

### 3) `adithya-s-k/OmniParse`

- Class: broad ingestion platform (documents/media/web), local server model stack with Docker workflow.
- Signals from source:
  - Linux-only operational path.
  - GPU memory requirements.
  - `GPL-3.0` license.
  - Model usage and downstream commercial usage constraints called out in README.
- Practical use in this app:
  - Not default.
  - Too broad for current narrow thesis and risky due to license/usage constraints for long-term product distribution.

### 4) `Microsoft/OmniParser` and `AlibabaResearch/AdvancedLiterateMachinery`

- Class: visual text parsing / screen parsing ecosystems.
- These are not PDF-form-field pipelines by default.
- Practical use in this app:
  - Keep on watch-list, not core plan.
  - Evaluate only when we need generic document image understanding outside native PDF form extraction.

### 5) Local PDF/field libraries (baseline options)

- `pypdf` (BSD-3-Clause) for deterministic base manipulation + AcroForm read/inspect.
- `pdfplumber` (MIT) for text/line/rect geometry extraction.
- `pikepdf` (MPL-2.0) for merge/fill/edit-style operations and file-level manip.
- `ocrmypdf` (MPL-2.0) when scanned PDFs need text-layer recovery before detector pass.
- `PyMuPDF`/`pymupdf` available but AGPL/commercial-route (fits less well with our `no-compliance` and long-term distribution posture).

## Decision for this feature track

For this round, add parser breadth in this order:

1. Expand current detector to cover non-signature field classes.
2. Improve local parser stack reliability (`pypdf` + `pdfplumber` + OCR fallback) with deterministic thresholds.
3. Introduce `LiteParse` as an optional local parser adapter (for richer layout/quality).
4. Add `LlamaParse` and broader multimodal parsers as explicit opt-in only when the user is aware of API and data-ejection path.

## Follow-up research we should still do

- benchmark set for common hard cases:
  - scanned forms,
  - low-contrast signatures,
  - checkbox-heavy forms,
  - Arabic/Hindi/date-heavy signatures pages.
- latency/error-quality Pareto for each parser adapter and a quality/egress toggle matrix.
- integration guardrail for any cloud parser:
  - explicit user consent,
  - export of only needed bytes,
  - auditable request log with source type.
