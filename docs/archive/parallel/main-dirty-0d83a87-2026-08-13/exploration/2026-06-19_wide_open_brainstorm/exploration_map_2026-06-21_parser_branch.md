# Exploration Map: Parser + Field Expansion Branch

Date: 2026-06-21

This is the active exploration branch for the question:

> If we are building a local-first PDF signature workspace, how far should parser support expand beyond signatures, and which parser stack should become the default?

This is an exploration artifact, not a commitment to ship every option.

## Starting Position

We are not starting from scratch.

The current thesis already survived the room:

`extract -> recognize -> place -> review -> export -> reuse`

The parser branch exists to improve that loop, not replace it.

## Exploration Goals

1. Expand field detection beyond signatures without losing the narrow product thesis.
2. Decide which parser stack becomes the default local path.
3. Keep cloud/API parsers optional and explicitly gated.
4. Preserve trust, reversibility, and recovery in every parser decision.

## Questions We Are Exploring

### Scope

1. Which non-signature field classes should be first-class?
2. Should form field detection stay inside the signature engine or split into a shared field layer?
3. What is the smallest parser set that gives us robust local behavior?

### Product

1. Do parser improvements help the recurring signature workflow enough to justify complexity?
2. Where does parser richness improve operator speed versus add noise?
3. What gets better for the user if we can also detect text, checkbox, date, and initials fields?

### Architecture

1. Which local parser can be trusted as the baseline?
2. Which optional parser should be first behind a toggle?
3. What is the clean fallback chain when OCR or geometry extraction fails?

### Policy

1. What stays local by default?
2. What requires explicit opt-in?
3. What gets excluded because it would turn the product into a broader compliance or cloud document platform?

## Working Hypotheses

1. Signature detection should become a subset of a broader field detection layer.
2. Local deterministic parsing should remain the default path.
3. OCR and layout extraction should be additive, not mandatory.
4. `LiteParse` is the best first optional parser enhancement.
5. `LlamaParse` and similar managed services are opt-in only.
6. GUI-vision parsers are useful for later expansion, not the core local PDF loop.

## Exploration Stages

### Stage 1: Ground Truth

Inspect real PDFs and classify the kinds of fields that appear:

- signature lines and boxes,
- initials,
- text inputs,
- checkboxes,
- dates,
- multiline text areas,
- page-level anchors and notes.

Outcome:

- a practical taxonomy of field types we actually see.

### Stage 2: Local Parser Baseline

Test the current local-first stack against those PDFs:

- `pypdf` for AcroForm and widget inspection,
- `pdfplumber` for geometry/text extraction,
- `pikepdf` for file-level manip and save flows,
- OCR fallback for scanned pages.

Outcome:

- a stable baseline decision and failure map.

### Stage 3: Optional Enrichment

Compare a richer local parser adapter:

- `LiteParse` for layout-rich parsing and bbox outputs.

Outcome:

- whether it improves confidence overlays, candidate ranking, and field grouping enough to justify integration.

### Stage 4: External Parser Gate

Evaluate API-style parsers only as opt-in adapters:

- `LlamaParse`,
- any similar managed parser with clear request logs and consent gates.

Outcome:

- explicit decision on whether the extra quality is worth egress, cost, and integration complexity.

## Adapter Seams

The exploration now has a real code seam for the parser branch:

- `desktop_app/pdf/parser_adapters.py`
- `LiteParseAdapter` for the optional local enrichment path
- `ManagedParserAdapter` for explicit opt-in cloud-style parsers

This keeps the branch local-first while leaving the upgrade path open.

## What We Will Measure

1. Field recall on real recurring document families.
2. False positives on visually busy scans.
3. Time-to-confidence for operators.
4. How often the parser improves or worsens placement speed.
5. How much fallback complexity is added per parser.
6. Whether the default path remains understandable and supportable.

## Decision Gates

### Proceed

If local parsing plus optional enrichment clearly improves the repeatable signature workflow without making the UI noisy or brittle.

### Prototype

If a parser is promising but needs a small real-doc benchmark before it can be trusted.

### Pause

If the parser adds complexity without meaningfully improving the core loop.

### Reframe

If parser expansion starts turning the app into a generic document platform.

### Kill

If a parser option cannot fit the local-first, recoverable, operator-visible contract.

## Immediate Next Exploration Tasks

1. Expand the benchmark corpus beyond one AcroForm file into a small family of field-heavy PDFs.
2. Compare local extraction outputs on the same sample set.
3. Decide whether non-signature field detection belongs in the signature engine or a shared field layer.
4. Prototype the optional `LiteParse` integration path.
5. Write the opt-in/cloud parser gate contract before any API path becomes default.

## First Pass Status

The first real-fixture pass has started and produced an initial baseline:

- `demo_document.pdf` shows rich text-native structure but no native form widgets;
- `sample.pdf` shows no text layer and no native widgets;
- `signed_output.pdf` shows image-only pages with no native widgets;
- `native_form_benchmark.pdf` now covers real AcroForm widgets for the native-field track;
- `checkbox_heavy_benchmark.pdf`, `mixed_layout_benchmark.pdf`, and `scan_like_benchmark.pdf` broaden the corpus;
- the current heuristic detector is now capped to a small number of suggestions per page;
- the native form field path works, but the signature detector and form-widget detector should remain distinct layers.

- [First-pass findings](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-06-19_wide_open_brainstorm/parser_branch_first_pass_2026-06-21.md)
- [Parser baseline comparison](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-06-19_wide_open_brainstorm/parser_comparison_matrix_2026-06-21.md)

## Linkback

- [Discussion Map](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-06-19_wide_open_brainstorm/discussion_map.md)
- [Online Parser Research](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-06-19_wide_open_brainstorm/online_parser_research_2026-06-21.md)
- [Signature Field Detection Discussion](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-06-19_wide_open_brainstorm/discussion_signature_field_detection.md)
