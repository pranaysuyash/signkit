---
title: Product Museum living-UI wide-open brainstorm
date: 2026-07-31
status: completed for parallel concept review, not a production decision
related:
  - ../decisions/2026-07-31_product_museum_experience_architecture.md
  - ../review/landing_inspiration_research_2026-07-31.md
  - ../../web/concepts/2026-07-31-workbench-experience/
  - ../../web/concepts/2026-07-31-product-museum-living-ui/
---

# Product Museum living-UI wide-open brainstorm

## Method and limits

The `carl-tools:wide-open-brainstorm` skill was used after the user asked for a
review beyond an internal product lens. Its external-model detection found no
available external LLM CLI in this session. The review was therefore run as a
deliberately separated role room, not represented as independent external
consensus.

The roles covered strategist, champion, cartographer, trickster, future self,
customer whisperer, outsider, operator, skeptic, and executioner. The work was
considered at six-month, twelve-month, twenty-four-month, and leapfrog
horizons. This is exploration evidence, not customer research or a product
claim.

## Shared starting point

The question was not how to make SignKit look more like a fashionable landing
page. It was how a visitor could understand an authorised, local document
preparation job before having to trust marketing copy.

The recurring workflow is:

```text
source material → inspect selection → refine asset → place in a PDF → inspect result
```

The signature is an important object in that journey, but not the protagonist.
The document handoff is the real source of urgency, repeat value, and trust.

## What the roles agreed on

### Customer and copy lens

- The first five seconds must answer whether this is an e-signature service,
  PDF editor, image editor, or a tool for preparing a signature image for a
  PDF. Category clarity comes before poetry.
- The visitor must see a source scan, intended region, cleaned asset, and
  destination PDF in one connected causal narrative.
- “Local” earns trust when it describes a visible boundary in the operation.
  It should support, not replace, the task-led headline.
- The right emotional promise is relief from a risky, irritating document
  handoff. B2C polish here means confidence and clarity, not playfulness.

### Art-direction lens

- The page should have chapter-specific postures rather than one repeated
  neomorphic or card-grid visual language: documentary source, precise
  workbench, quiet personal archive, then an explicit horizon.
- The memorable moment is selecting a prepared local asset and seeing it land
  in a visible PDF field, with a compact status receipt. Sliders and parallax
  should never be the point of the experience.
- “Product Museum” is a structural metaphor only. It must not become a literal
  gallery theme.

### Product, operator, and skeptic lens

- A source region is a user decision. The landing must not suggest every mark
  visible in a document is authorised for reuse.
- A cleanup control represents inspection, not a claim of perfect extraction.
- The real choice after cleanup is one-off output or a saved local asset.
- A placement is only meaningful when the destination page and field remain
  visible. Automation, cloud, hybrid, and regulated signing are not current
  sales claims.
- The page must distinguish available work, in-development work, and research
  directions without forcing internal product planning language onto visitors.

## Red-team constraint

The Executioner role would abandon this direction if it became expensive brand
theatre that substitutes for a real walkthrough, validated buyer, and a
production purchase path. The limited parallel prototype is allowed only as a
truth-bearing comprehension experiment. It does not approve an elaborate
marketing build.

The evidence that would justify a production investment is deliberately
outside this prototype:

1. target customers can describe a recent authorised signature-preparation job
   and their current workaround;
2. representative users can complete the actual local workflow and explain
   its legal boundary accurately;
3. checkout, licensing, and refund terms are production-valid; and
4. the interactive proof improves comprehension or purchase intent compared
   with a simple real-product walkthrough.

## Horizon synthesis

| Horizon | Product proof that belongs on a landing page | What must remain out of the sales path |
| --- | --- | --- |
| 6 months | Real local extract, clean, save, place, and template proof | Generic cloud workspace promises and integration logos |
| 12 months | Document-family templates, reviewable repeat work, receipts | Broad vertical claims before validated workflow evidence |
| 24 months | Explicit choice of local, selected hybrid, or governed cloud modes | Any ambiguity over data authority, recovery, or permission model |
| Leapfrog | Permission-aware document execution with asset and action provenance | A claim that such provenance is already shipped or legally sufficient |

## Chosen experiment

The new parallel concept at
`web/concepts/2026-07-31-product-museum-living-ui/` implements the smallest
coherent version of the recommendation:

- a task-led entrance that names the authorised signature-image and PDF job;
- a semantic DOM case with source, refine, target, receipt, visible states,
  live announcements, keyboard controls, and an optional drag gesture;
- a calm local asset chapter rather than a decorative Vault shelf; and
- a compact boundary chapter that separates present, in-development, and
  research status without exposing internal “topology” language.

It preserves the illustrated workbench at
`web/concepts/2026-07-31-workbench-experience/`. The two artefacts answer
different questions: the workbench is art direction; the living UI proves a
causal interaction pattern.

## Non-obvious insight

Trust is not a visual mood in this product category. It is the visitor being
able to inspect the source, understand the change, control the destination,
and see where the system stops. A compelling SignKit experience may therefore
feel quieter than a typical B2C landing page while being much more memorable.

## Update log

- 2026-07-31: created from the requested wide-open, multi-persona review and
  used as the design input for the separate living-UI concept.
