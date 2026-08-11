# SignKit B2C Landing Redesign Lab

Date: 2026-07-31  
Status: approval prototype only. `web/live` is not modified.

## Why a separate lab

The existing public page demonstrates the product but loses its information
architecture after the first content blocks: browser inspection showed large blank
regions before the footer. This lab is deliberately isolated so a visual world can
be assessed without overwriting the incumbent implementation or active worktree
changes.

## Product truth held constant

- Local-first signature extraction, Vault, and PDF placement are real.
- The primary public scene is an individual handling a sensitive document.
- $29 launch / $39 Personal and a 30-day refund are documented; the current Dodo
  product ID is blank, so no concept presents a working purchase flow.
- Do not imply that a placed signature is legally sufficient in every context.

## External research synthesis

- B2C productivity leaders such as Raycast lead with a tangible interaction and
  the lived benefit, not a generic capability inventory.
- Current landing-page practice favors a single clear action and real product
  demonstration over a collection of decorative effects.
- Motion has to be a product explanation, not ambient clutter: use compositor-
  friendly transforms and opacity, support `prefers-reduced-motion`, and give the
  visitor control over any substantial demonstration.
- WCAG 2.2 focus appearance, touch target, contrast, and semantic navigation are
  functional requirements, not an afterthought.

Sources are recorded in the final handoff and include W3C WCAG 2.2, MDN/web.dev
motion guidance, Webflow’s recent landing-page examples, and current Raycast/
CleanShot product patterns.

## Seven explored visual worlds

These are distinct systems, not a list of colors applied to the same hero.

1. **The desktop shortcut**: a focused command-overlay composition where a document
   becomes a signature through one keyboard-like action. Strong utility signal,
   but risks understating the tactile precision of cleanup.
2. **Private studio desk**: real paper, a signature nib, and a carefully lit work
   surface. Intimate and emotional, but can become faux-skeuomorphism if it does
   not expose the actual desktop workflow.
3. **The living document**: layered page fragments choreograph the journey from
   source scan to clean mark to placed PDF. Strong explanation, but the hierarchy
   can become too editorial for a quick purchase decision.
4. **Trust boundary**: a spatial divide makes local processing visibly different
   from “upload and wait.” Precise and differentiating, but too security-centric
   as the main B2C emotional register.
5. **Signature collection**: a personal archive of marks and documents gives the
   Vault personality. Warm and memorable, but risks de-emphasizing PDF placement.
6. **Gesture Field**: the selected world. A living, responsive ink line physically
   pulls a trapped mark out of paper and lands it on a document. It turns the
   unique workflow into a delightful consumer interaction without inventing an AI
   claim or hiding the real task.
7. **The quiet atelier**: a high-craft typographic composition with sparse object
   photography and deliberate whitespace. It can feel premium, but it is weaker at
   proving this product’s mechanism before asking for a purchase.

## Direction decision

The concept-seed process assigned exploration 6. **Gesture Field** also won the
only two decision axes required for the public prototype:

| Direction | Audience identification | Product clarity | Result |
| --- | --- | --- | --- |
| Gesture Field | A sensitive document visibly becomes a reusable signature | The extract → clean → place sequence is directly manipulated | Build |
| Private studio desk | Strong personal B2C warmth | Relies more on metaphor than workflow | Explore as alternate |
| Trust boundary | Strong privacy recognition | Risks making privacy the whole product | Explore as alternate |

The three first-view studies live in `explorations.html`; the fully realized,
approval-ready direction lives in `index.html`.

## Chosen system: Gesture Field

- **Physical scene:** a private desk at dusk. Ink black workspace, warm paper,
  cobalt blue selection light, and a vermilion action cue.
- **Typography:** an intentionally compact, technical-but-human display face
  paired with a quiet sans UI face and a mono measurement face for genuine state
  labels only.
- **Signature interaction:** a range input drives the visible transformation from
  trapped mark to clean mark to placed PDF. Pointer parallax only moves decorative
  paper layers, never reading content or controls.
- **Narrative:** demonstrate the workflow first, then establish privacy, then
  show repeat use through the Vault, then state the one-time purchase clearly.
- **Motion contract:** all nonessential motion stops for reduced-motion users;
  the workflow remains comprehensible without it. No autoplaying video or
  infinite attention-seeking loop.

## Feature-atlas addendum

Gesture Field remains the acquisition scene, but it is not a universal visual
system. Applying its paper-and-ink language to every capability would turn a
real product roadmap into decorative sameness. The isolated prototype now changes
visual grammar with the job being explained:

| Work mode | Product state | Visual posture | Evidence boundary |
| --- | --- | --- | --- |
| Make a mark | Available desktop workflow | Tactile paper and recovered ink | Extraction, cleanup, local Vault, and placement only |
| Work the PDF | Available desktop workflow | Restrained precision workbench | PDF placement, templates, and field-aware placement where supported |
| Run a packet | In development | Local route map with visible exception states | Controlled recipes, grants, folders, review, retry, and quarantine; not a public plan |
| Higher-trust signing | Research horizon | Quiet editorial horizon | No certificate, regulated-signature, or legal-validity promise |
| Hybrid workspaces and adapters | Later, with proof | Quiet editorial horizon | No sync, integration, or team-operation promise without a proved boundary |

The atlas deliberately avoids a generic enterprise dashboard. It uses operational
information only where the product has a real operational concept, and labels
that concept as in development. The future horizon is explanatory, not a pricing
or lead-generation surface.

## Review passes

1. **Immediate correctness:** product claims are constrained to local extraction,
   Vault, and PDF placement. Purchase actions are honest previews until checkout
   configuration is complete.
2. **Architecture:** no existing route, asset, checkout, or production CSS is
   modified. The lab is self-contained and can be promoted only after approval.
3. **Supervision:** browser review must check desktop, mobile, keyboard focus,
   motion reduction, interaction state, console errors, tab interaction, and link
   behavior before a move is proposed.

## Mechanical-detector note

The detector reports one `dark-glow` warning in the **Private studio desk**
alternate. This is a reasoned deviation, not a final-world pattern: the non-zero,
warm offset shadow describes the physical desk light on a paper object. It is not a
zero-offset chromatic halo, is confined to a non-selected exploration, and has no
role in Gesture Field. The selected direction passes without that visual language.

## Browser acceptance evidence

Browser-controlled checks on `http://127.0.0.1:4175/` recorded:

- Desktop at 1440px: full page content is present, primary navigation is not
  duplicated, and no console errors were observed.
- Mobile at 390px: the menu opens, the page has zero horizontal overflow, and the
  workflow, privacy, Vault, and pricing sections reflow in a readable sequence.
- Interaction: setting the transformation control to 85% changes the announced
  state to “Signature is clean and placed on the PDF,” with the clean mark fading
  in and the source paper fading back.
- Reduced motion: `prefers-reduced-motion` is honored, ambient animation resolves
  to `none`, and all content remains visible.
- Keyboard and semantics: the first Tab reaches “Skip to content”; the document
  contains one `main`, one `h1`, seven `h2` elements, navigation landmarks, a
  labelled range control, and one keyboard-operable three-tab work-mode switcher.
- Feature atlas: desktop and mobile browser runs confirmed zero horizontal
  overflow. Selecting the precision-PDF and controlled-packet modes exposes only
  the chosen panel and updates the tab’s selected state. The controlled-packet
  panel retains its “in development / not a public plan” boundary.
- Open Browser review: the isolated `http://127.0.0.1:4175/#pricing` tab was
  reloaded after the atlas was added, and its accessibility tree exposed the
  new work-mode navigation, product-state labels, and future-boundary copy.
  Clicking “Run a packet” showed the correct controlled-operations panel.
- Lighthouse snapshot audit on that Browser tab: Accessibility 100, Best
  Practices 100, SEO 100. The audit first exposed low-contrast accent labels;
  the final CSS uses darker state accents and passed after retest. The separate
  Agentic Browsing 0 is from absent WebMCP registration, which is not a product
  requirement for this static approval prototype.

## Final review passes

1. **Correctness:** fixed the desktop duplicate-navigation selector and removed
   scroll-gated hidden content after the first full browser capture exposed both.
2. **Long-term shape:** the lab remains a self-contained, static review artifact
   with no production checkout or route replacement.
3. **Supervision readiness:** approval is the only required next decision. Promote
   the isolated files only after explicit approval and after replacing illustrative
   product panels with current, verified app captures where appropriate. The
   feature atlas should be revisited if controlled packet operations change from
   in-development to a public offer.

## Anything else?

The current evidence does not justify customer logos, testimonials, star ratings,
or performance claims. The finished production page should use real app captures
or a recorded workflow before replacing the illustrative product panels.
