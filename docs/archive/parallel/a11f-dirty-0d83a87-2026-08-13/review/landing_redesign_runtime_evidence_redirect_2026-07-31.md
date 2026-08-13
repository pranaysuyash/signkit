# Landing redesign runtime-evidence redirect

Date: 2026-07-31  
Status: binding redirect before any replacement landing implementation

## Operator correction

> "take the current product screenshots not old ones, this is neither first principle, long term or motto_v4 aligned what you just did"

## Decision

The former B2C concept must not use `web/live/assets/screenshots/` as its design
evidence without a fresh runtime capture. The running current desktop product is
the source of truth for any product proof, capability hierarchy, or landing-page
visual reference.

The homepage's conceptual front door is the shared job of preparing sensitive
PDFs locally and repeatedly, not a single persona or signature extraction as a
product category. The corresponding experience-system direction is recorded in
`Docs/review/signkit_experience_system_direction_2026-07-31.md`.

## Runtime evidence captured

The project virtual environment was used, not system Python:

```sh
./.venv/bin/python scripts/capture_current_product_surfaces.py \
  --profile mac-premium \
  --output Docs/review/assets/current-premium-product-surfaces-20260731
```

The command captured current `mac-premium` surfaces from the working tree:

- `01_signature_extraction_20260731_174419.png`
- `02_pdf_signing_20260731_174419.png`
- `03_workflow_dashboard_20260731_174419.png`
- `04_workflow_grants_20260731_174419.png`
- `05_recipe_builder_20260731_174419.png`
- `06_vault_20260731_174419.png`

The refreshed comprehensive harness also captured a current loaded-image and
selection state in `Docs/review/assets/current-premium-runtime-capture-20260731/`.
The harness initially failed because it referenced the removed `ImageView._pixmap`
attribute. It now uses the current `pixmap_item` and
`set_selection_from_coords()` APIs and accepts an explicit launch profile.

## Consequences for the landing replacement

1. Do not use fake paper, fictional consent sheets, generic SVG signatures, or
   invented product workbenches as product proof.
2. The replacement hero must show the current extraction or PDF placement product
   state, art-directed only through framing, cropping, annotation, and legitimate
   transition between real states.
3. Present current Premium workflow screens as capability evidence only after the
   core extract, clean, save, and place job is clear. Empty current workflow
   surfaces are not suitable hero proof.
4. The former review concept is retained untouched as a rejected direction and is
   not eligible for incremental polish.

## Evidence tier and remaining gap

- Tier 4: current desktop screens were rendered and visually inspected from the
  current `mac-premium` runtime.
- The captured empty Workflow Dashboard, Grants, and Recipe Builder surfaces have
  low visual legibility in the current theme. This is runtime evidence, not a
  landing claim. The landing must not conceal or cosmetically substitute these
  states as if they were shipped polished product proof.
- During the live selection capture, the desktop UI continued to respond, but
  its non-blocking backend selection sync logged a `model_attributes_type`
  validation error because an encoded selection string was received where the
  endpoint expected an object. This is a current integration fault, not a
  landing-page concern to conceal. It needs a separate runtime-verified repair
  before that sync behavior is described as reliable.
- A future landing build needs a fresh, successful end-to-end capture of a loaded
  PDF and a real placed-signature result from the same current profile before it
  claims that workflow visually.

## Anything else?

Yes. The runtime capture utility is now profile-aware and reusable, so subsequent
design reviews can refresh evidence rather than treating a previous screenshot
folder as product truth.
