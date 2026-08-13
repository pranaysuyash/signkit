# Landing exploration research: customer workbench direction

Date: 2026-07-31  
Status: design research used for a parallel concept, not a public claim source

## Brief correction

The customer-facing page must lead with the job: taking a document from source material to a ready PDF. It must not lead with a deployment choice, future platform strategy, or an internal vertical-validation thesis. Local processing is real and important, but it functions as substantiating proof after the visitor understands the product.

The prior customer-work concept failed two direct review points:

- `Why keep it local?` elevated a supporting property into the hero's second action.
- The final dark closing panel consumed a large amount of height without adding proof, navigation, or a decision.

## Live product references

| Reference | What was observed | Decision for SignKit |
| --- | --- | --- |
| [Linear homepage](https://linear.app/) | The page puts recognisable product states in the argument, then lets each section explain a concrete operating capability. | Use current SignKit captures as the primary visual proof, never abstract reconstructions or random crops. |
| [Linear’s UI redesign write-up](https://linear.app/now/how-we-redesigned-the-linear-ui) | The redesign prioritised less noise, stronger alignment, and information density so the product could grow without losing clarity. | Use a compact grid, normal letter spacing, and content-driven section heights. No cavernous poster panels. |
| [Raycast homepage](https://www.raycast.com/) | The page starts with a concise promise, then turns specific product qualities into an expressive rhythm. | Make the workflow interactive and current B2C in tone, but keep the interaction tied to actual product states. |
| [Landbook landing-page gallery](https://land-book.com/design/landing-page) | The current inspiration space includes motion, OS-app, large-type, and visible-border approaches, but those are styles rather than a product story. | Borrow neither a generic SaaS template nor empty visual novelty. The visual system has to serve the document-preparation sequence. |

## Conceptual exploration

Seven possible cultural systems were considered before selecting the parallel direction:

1. A document conservator's bench: evidence, tools, and sequence visible at once.
2. A photographic contact sheet: precise before-and-after examination.
3. An editorial production desk: the source, proof, and final layout as one focused surface.
4. A field notebook: purposeful sequencing, but potentially too casual for consequential documents.
5. A professional studio workbench: tactile, controlled, current, and broad enough for personal and professional work.
6. An industrial-label / streetwear grammar: energetic but likely to undermine the sober competence the target audience expects.
7. A security-control room: credible but too enterprise-coded and too far from the immediate job.

The selected direction is **the document workbench**: a calm, dense, black-ink and warm-paper system in which the real desktop app is the central tool. It avoids the previous neomorphic visual language and avoids treating any professional segment as the whole audience.

## Copy rules adopted

- Lead with an observable outcome, not a category claim: “From source to signed PDF.”
- Name the customer’s actions in sequence: find, refine, place.
- Put local-by-default processing in the assurance section, not in the hero CTA or page title.
- Show broad situations, not narrow public personas: a scan, a PDF due today, personal paperwork that needs care.
- No customer counts, benchmark metrics, testimonials, legal guarantees, regulated-signature claims, or cloud/hybrid roadmap claims.

## Explicit visual constraints

- The page must use current product captures from `Docs/review/assets/current-premium-runtime-capture-20260731/`.
- The workflow interaction may only swap among current screenshots, with appropriate alternative text and selected-tab state.
- Large display type must stay legible and not rely on tight tracking to look fashionable.
- No section gets a viewport-sized minimum height merely to create drama.
- Motion is limited to the image transition and normal hover feedback, and is disabled for reduced motion.

## Review questions for the parallel page

1. Does the hero communicate the job in a single glance before any implementation detail appears?
2. Do the real captures feel like proof rather than decoration?
3. Does local processing read as an honest trust property, not a fear-based or limiting product category?
4. Can a person with a time-sensitive document see themselves in the examples without being funnelled into an internal vertical?
5. Is every major panel doing work, especially the closing action?

## Build review record

### Pass 1: immediate customer clarity and completeness

- Replaced the hero's local-processing CTA with `See the real desktop app`.
- Kept local-by-default processing as a single assurance detail after the workflow is intelligible.
- Used three current runtime captures for source selection, extraction result, and completed PDF placement.
- Replaced profession labels with three familiar document moments. No Legal/HR wedge, topology, cloud, hybrid, validation-status, or roadmap language appears in the page.

### Pass 2: visual system and long-term fit

- Built a parallel workbench direction in `web/concepts/2026-07-31-workbench-experience/`; all previous concepts remain untouched.
- Removed the prior visual language's soft-card/neomorphic dependence. The new system uses a direct paper, ink, blue, and lime palette with a compact grid and actual product frames.
- After desktop inspection, collapsed an unused two-column header in the dark scenario section and reduced the closing panel's height. No section uses a viewport-sized minimum height.

### Pass 3: interaction, accessibility, and implementation checks

- The screenshot stepper updates selected-tab state, alternative text, visual caption, and tabpanel labelling for each current product image.
- Arrow keys move among workflow steps in addition to pointer input.
- Desktop, 390px touch viewport, and the requested Browser tool were exercised manually. The Browser pass confirmed navigation, the screenshot switch, and zero browser console errors after the favicon correction.
- `node /Users/pranay/.agents/skills/impeccable/scripts/detect.mjs --json web/concepts/2026-07-31-workbench-experience/index.html web/concepts/2026-07-31-workbench-experience/styles.css` returned `[]`.

## Deliberate non-claims

This is a non-live review concept. It does not add checkout, promise cloud or hybrid availability, claim regulated signing, imply universal suitability, or use unverified social proof. The page has no production purchase action because the current checkout configuration is not yet complete.

## Addendum: illustrative workspace direction

The runtime captures remain the source of truth for the current desktop app, but they are not being used as the visual target for a future web experience. The review concept now uses an image-generated **illustrative workspace direction** at `web/concepts/2026-07-31-workbench-experience/assets/signkit-future-workspace-concept.png`.

Every use of the image is labelled illustrative or concept. It depicts a polished source → refine → PDF workbench and is deliberately not presented as a currently shipped screen. The workflow stepper crops this one holistic visual in three ways to demonstrate the intended product emphasis without manufacturing three false runtime screenshots.

## Addendum (2026-07-31): learning recorded after Linear vs Raycast review

The prior research table correctly identified useful visual cues, but it
understated the decisive learning: **the design problem is information
architecture, not style selection**.

The landing must make a person understand the product and feel the relief of
finishing paperwork before they read a feature explanation. A static screenshot
or an image-generated workbench can establish art direction, but neither is the
final demonstration form. The production-quality pattern is living UI:
semantic components whose source, selection, cleanup, PDF placement, and ready
state visibly cause one another.

The consequent long-term architecture is documented in
[`2026-07-31_product_museum_experience_architecture.md`](../decisions/2026-07-31_product_museum_experience_architecture.md).
It records the chapter model, the single memorable interaction, the division
between current proof and illustrative direction, rejected alternatives, and
the production-concept acceptance contract.
