---
title: Product Museum living UI review
date: 2026-07-31
status: parallel concept verified, awaiting user review
related:
  - ../exploration/2026-07-31_product_museum_wide_open_brainstorm.md
  - ../decisions/2026-07-31_product_museum_experience_architecture.md
  - ../../web/concepts/2026-07-31-product-museum-living-ui/
  - ../../web/concepts/2026-07-31-workbench-experience/
---

# Product Museum living UI review

## Outcome

Created a separate, additive Product Museum prototype. It is not a replacement
for the existing workbench study and does not modify any current landing page.

The new prototype uses a real DOM state journey instead of image crops:

```text
inspect fictional source → adjust cleanup → save local asset in concept → place into visible PDF field → shown-ready receipt
```

The visitor can complete it with buttons and keyboard. A native drag-and-drop
gesture is supplementary, never required.

## What changed

| Artefact | Purpose |
| --- | --- |
| `web/concepts/2026-07-31-product-museum-living-ui/index.html` | Semantic landing prototype and visible capability-boundary copy |
| `web/concepts/2026-07-31-product-museum-living-ui/styles.css` | Responsive chapter grammar, high-contrast visual system, focus and reduced-motion rules |
| `web/concepts/2026-07-31-product-museum-living-ui/app.js` | DOM state changes, range preview, simulated local asset save, placement, receipt updates, and drag support |
| `Docs/exploration/2026-07-31_product_museum_wide_open_brainstorm.md` | Multi-persona review evidence and red-team constraints |

## Truth boundary

- Every fictional document is visibly labelled as sample material.
- The interactive state explicitly says it does not extract, save, or modify a
  real document.
- The product boundary labels present local capabilities, in-development
  repeatable workflow work, and research-only connected trust modes.
- It does not claim legal validity, regulated signing, automatic permission,
  cloud availability, universal PDF support, production security guarantees,
  testimonials, metrics, or a current checkout path.

## Visual and interaction verification

Visual tests were conducted in the open browser, not from source inspection
alone:

| Check | Evidence | Result |
| --- | --- | --- |
| Desktop visual composition | Chrome DevTools screenshot at 1440 × 980 | Hero, chapter transition, and three-panel operation read cleanly without overlap |
| Desktop case completion | Clicked Save, clicked Place, inspected DOM state | Receipt changed to saved local asset in concept and placement shown in concept |
| Keyboard operation | Focused slider, pressed ArrowRight, then Tab/Enter through Save and Place | Cleanup value, live status, receipt, and PDF field updated |
| Touch-mobile layout | Chrome DevTools screenshot at 390 × 844 with mobile and touch emulation | Workbench reflowed to a single readable column with no horizontal overflow seen |
| Browser plugin check | Playwright Browser navigation and screenshot | Concept loaded at the intended parallel URL |
| Console | Chrome DevTools console review | No errors or warnings |
| Accessibility | Lighthouse desktop snapshot | 100 accessibility, 100 best practices, 100 SEO, 100 agentic browsing after remediation |

The requested desktop Computer Use control was checked, but this session does
not expose a callable Computer Use tool. Chrome and Browser controls were
available and used for the visual checks above. That is a tooling limitation,
not a claim that Computer Use was used.

## Three review passes

### Pass 1: immediate correctness and completeness

Found and fixed an initial-state error in which the cleanup stage announced
itself before the visitor interacted. The initial state now correctly says
“inspect the source.” The core causal sequence, receipt, and user-facing
labels were then manually exercised.

### Pass 2: architecture and long-term viability

The prototype follows the Product Museum decision without publishing internal
scaling language. It makes the current local job primary, gives future work a
small explicit boundary, and keeps the illustrative workbench and living UI
as separate artefacts with distinct roles.

### Pass 3: rule compliance and supervision readiness

Lighthouse initially identified a prohibited ARIA use, a visible-label name
mismatch, and low-contrast microcopy. The prototype now uses a valid image
role for the non-semantic hero diagram, derives the brand link name from
visible text, and passes the desktop Lighthouse snapshot at 100 accessibility.

### Pass 4: density and reading rhythm

After the first desktop review, the large chapter padding and the collection
heading made the page feel more spacious than the task justified. The hero and
chapter vertical rhythm were tightened, the collection copy was shortened to
“Keep the useful version ready,” and the desktop visual check was repeated.

## Known gaps and hardening path

1. **Concept, not product proof.** The DOM case is explicitly simulated.
   Production would need current safe desktop captures or a live demo surface
   tied to the actual workflow.
2. **No customer comprehension study.** The red-team condition remains open.
   Test the live proof against a simpler real-product walkthrough before
   investing in a production interaction build.
3. **No screen-reader human session.** Semantics, keyboard behavior, focus,
   live regions, contrast, and Lighthouse were checked. A production candidate
   should receive a VoiceOver pass on macOS and a zoom/reflow pass at 200%.
4. **No production conversion path.** The concept intentionally avoids a buy
   CTA because the current checkout is not production-complete.

## User-facing, team, and operational value

- **Visitor value:** someone can understand the authorised source-to-PDF job
  and its boundary before being asked to trust a product claim.
- **Team value:** art direction and living interaction are independently
  reviewable instead of being conflated in one mockup.
- **Operational value:** the truth labels prevent a marketing concept from
  silently becoming a promise about unshipped connected or regulated work.

## Review URL

`http://127.0.0.1:4176/web/concepts/2026-07-31-product-museum-living-ui/index.html`

## Update log

- 2026-07-31: created after multi-persona review, DOM implementation, Browser
  and Chrome visual validation, and accessibility remediation.
