# Unique Positioning Brief (From Existing Code, 2026-06-17)

## What makes this product different right now

1. **Single canonical signature pipeline across all intake paths**
   - File import and webcam capture both route through the same extraction flow (`_load_image_from_path` → local session creation → `_on_upload_finished`), so behavior is identical for quality and troubleshooting.
   - This reduces edge-case drift between desktop ingestion modes.

2. **Extraction-to-PDF placement loop (one product, not one-off tools)**
   - Extract once, then reuse the same signature in the PDF tab via shared library assets and placement workflow.
   - Placement supports manual clicks and detected-field snapping (`desktop_app/pdf/viewer.py`, `desktop_app/views/main_window_parts/pdf.py`).

3. **Native PDF intelligence baked into the same app, not bolted on**
   - Signature field detection is implemented for PDF page content (`desktop_app/pdf/field_detection.py`).
   - Native form widget inspection and editing are implemented via `PdfFormFieldEditor` (`desktop_app/pdf/form_fields.py`).
   - Signing uses native embedding in `desktop_app/pdf/signer.py` and collects placements through `PDFViewer.get_placed_signatures()`.

4. **True offline/private workflow bias**
   - The core extraction path and PDF signing flow are local-first and do not require cloud upload for normal use.
   - Pricing/reasoning is positioned as ownership-first, no subscription.

5. **Operational memory in vault metadata**
   - Signature usage tracking (count + last used metadata) already exists in the vault and is surfaced from library actions.

## Current pricing stance that supports this moat

- Launching at **$29** preserves the “fast-first-mover” wedge for early buyers.
- The product moves toward **$39 lifetime** after the launch window because the workflow includes a full extraction + PDF-signing loop and the premium is for time savings + privacy + ownership.
- This is reinforced in: `docs/PRICING.md`, `index.html`, `purchase.html`, `web/live/index.html`.

## Practical next step (v3-aligned)

Keep the same architecture and make this proposition explicit in sales copy:
- “Capture. Extract. Place. Lock.”
- Emphasize the 1) offline processing, 2) field-aware PDF placement, and 3) native form completion as the three-part differentiator.
