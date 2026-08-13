# SignKit product visual direction strategy

Date: 2026-08-13
Persona: Product Visual Direction Strategist
Scope: replacement landing direction and replacement web-app direction
Evidence: Tier 1 static inventory, Tier 4 local browser inspection, prior Tier 4 desktop-runtime evidence
Status: selected for replacement candidate work; production promotion not approved

## Executive direction

SignKit should become a **document registration studio**.

The visual system should make a sensitive document feel like a physical object
being registered, prepared, and moved to a known place. The product should feel
serious, calm, exact, and human. It should have one memorable product-specific
gesture: a registration frame that follows the mark from source, through
cleanup, into the PDF field, then into a visible ready receipt.

This is not a generic SaaS dashboard, a security control room, an electronic
signature marketplace, or a dark marketing site. The emotional result is:

> I can see what I selected, what changed, where it will go, and what is ready.

## Observed facts

1. The desktop app is the current source of truth for extraction, cleanup,
   reusable local marks, PDF placement, and signing-related work.
2. The browser workspace is a real metadata-first control plane. It does not
   host document signing or establish browser-native PDF execution.
3. The root page is the current route owner, but it has a bright neo-brutalist,
   card-heavy launch treatment. Route ownership does not make it the desired
   replacement design.
4. The repository contains multiple concepts. They vary in emotional intensity,
   visual metaphor, proof model, and product truth.
5. Existing concept reviews consistently reject fictional product proof, silent
   Cloud or Hybrid claims, and generic platform language.
6. The current local browser renders all inspected candidates without horizontal
   overflow at 390px. This is runtime layout evidence only. It is not evidence
   of comprehension, assistive-technology behavior, or production readiness.

## Candidate comparison

Scores are decision inputs, not user research. A score of 5 is stronger for the
criterion. The selected system combines candidates. It does not promote one
existing concept unchanged.

| Candidate | Job clarity | Product proof | Distinctiveness | App continuity | Claim safety | Long-term fit | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Legacy root | 3 | 3 | 4 | 2 | 3 | 2 | Preserve route authority; replace visual system |
| `web/live` | 2 | 2 | 2 | 1 | 1 | 1 | Historical only |
| `web/new_landing_page` | 2 | 2 | 2 | 2 | 2 | 2 | Reject as generic variant |
| B2C redesign | 3 | 1 | 5 | 2 | 2 | 2 | Preserve as rejected theatrical history |
| Customer work | 5 | 5 | 3 | 4 | 4 | 4 | Select landing information architecture |
| Product Museum | 4 | 2 | 5 | 4 | 4 | 4 | Select causal preview grammar, not capability proof |
| Workbench | 4 | 2 | 4 | 4 | 3 | 4 | Select precision and density references |
| Workspace experience | 4 | 4 | 4 | 4 | 3 | 4 | Keep as bridge reference |
| Topology experience | 2 | 4 | 4 | 3 | 3 | 4 | Secondary strategy explanation only |
| Current cloud workspace | 3 | 3 | 4 | 5 | 4 | 4 | Keep as real metadata app foundation; simplify its entry experience |

## Audience and usage model

### Primary audience

Individuals and small teams who prepare sensitive or consequential documents on a
desktop. They need a finished document, not a broad signing platform.

### Primary job

Extract or recover a signature mark, clean it, keep it available, and place it
where it belongs in a PDF.

### Usage intensity

- Landing: 30 seconds to 3 minutes. The visitor must understand the job and
  trust the boundary quickly.
- Causal preview: 1 to 3 minutes. The visitor may inspect the sequence.
- Browser workspace: 10 minutes to 2 hours for a metadata and review register.
- Desktop app: repeated 10-minute to 2-hour work sessions. The visual language
  must remain calm at working distance.

## Personality profile

| Dimension | Direction |
| --- | ---: |
| Serious to playful | 82% serious |
| Conservative to experimental | 58% experimental |
| Warm to clinical | 48% warm, 52% clinical |
| Minimal to expressive | 68% minimal |
| Premium to utilitarian | 70% premium |
| Human to technical | 55% human |
| Calm to energetic | 84% calm |
| Familiar to distinctive | 66% distinctive |

The product earns distinction from the registration-frame interaction and the
document material metaphor. It does not need decorative novelty.

## Theme and color

Use a daylight-neutral field as the primary landing surface. Use carbon ink for
high-consequence proof panels and the operational app frame. Use registration
blue for selection, focus, and active workflow state. Use proof yellow only for
current or ready signals. Use coral only for destructive or attention states.

Proposed semantic palette:

| Role | Value | Use |
| --- | --- | --- |
| `paper` | `#F1F2EE` | low-glare document field |
| `carbon` | `#131922` | authority, proof frame, app shell |
| `muted-ink` | `#5A6472` | supporting text and captions |
| `registration` | `#3157D5` | selection, focus, active stage |
| `proof` | `#D7F23E` | current, ready, or approved signal |
| `attention` | `#F06B54` | errors, destructive action, review attention |

This palette avoids the generic purple-gradient SaaS treatment and avoids
using one accent for every semantic meaning.

## Typography

- Display: a heavy, compact grotesk for the document job and chapter thesis.
- Body: a readable neutral sans for explanations and forms.
- Utility: a mono or tracked sans for evidence captions, page identifiers,
  workflow states, and local-boundary labels.
- No decorative script as a product-state indicator. Handwriting may appear only
  inside a clearly labelled document sample.

The replacement should use heading balance and predictable wrapping. Large type
is allowed only when the surrounding action remains visible.

## Geometry, layout, and signature element

- Use registration lines, crop marks, field outlines, and measured gutters as
  structural elements. Each line must explain document position or workflow
  state.
- Use moderate radius only for controls that need a clear hit area. Avoid
  floating-card recursion and soft decorative blobs.
- Landing layout: one job-led hero, one registration-frame preview, three
  chapters, one boundary section, one conversion path.
- App layout: persistent document context, visible next action, compact state
  rail, and a quiet evidence panel. Do not copy the landing page's hero rhythm
  into a high-density work surface.

Signature element: **the registration frame**. It is a rectangular crop/field
frame with a visible source label, an active mark, a target field, and a state
receipt. The frame connects the landing preview, desktop proof captions, and app
review language.

## Motion and interaction

- Motion shows causality: the frame moves from source to mark to clean to place.
- The same state must be available by native buttons and keyboard input.
- Reduced motion keeps the state change and removes parallax, drag dependence,
  and decorative transitions.
- Dragging is optional. It must have a non-drag alternative.
- The public preview must state whether it is current runtime proof or an
  illustrative simulation.

## Product and truth boundary

The replacement landing may demonstrate the mental model. It may not claim that
the browser performs local extraction, saves a local asset, or edits a visitor's
PDF unless the runtime contract actually does so.

The replacement web app may show metadata and review state. It must not present
`signed`, `exported`, or `completed` metadata as proof that a document was
signed. Those labels need a product-specific explanation or a narrower state
vocabulary.

Cloud and Hybrid remain future directions until their execution, storage,
recovery, audit, support, and privacy contracts are proven.

## What is rejected

- Legacy root visual system as the future target.
- `web/live` as a design source.
- Dark SaaS gradients and generic feature-card composition.
- Cybersecurity terminal styling.
- Theatrical signature transformation without product evidence.
- Illustrative workbench imagery presented as a current product screen.
- Topology as the first explanation a visitor must understand.
- Browser workspace styling that implies browser-native document signing.

## Required replacement gates

1. Create a new replacement candidate surface. Do not modify the legacy root
   while direction work is under review.
2. Use current authorized desktop captures for product proof. Mark all simulated
   states as illustrative.
3. Give the candidate one conversion path that uses the governed checkout
   contract only after copy and pricing review.
4. Define a separate metadata-app visual contract and state vocabulary.
5. Add tests for source-to-ready state binding, product truth, focus, reduced
   motion, responsive layout, and asset semantics.
6. Run browser review at 1440x900, 390x844, and 320px width, including keyboard
   interaction and reduced motion.
7. Promote a route only after product review, claim review, and deployed parity
   checks pass.

## Evidence and uncertainty

Observed: source inventory, route redirects, local browser screenshots, current
concept copy, app/backend contracts, and dated concept reviews.
Inferred: the registration-studio direction is the strongest long-term fit.
Not proven: conversion, user comprehension, willingness to pay, screen-reader
quality, production parity, and browser-native execution.

Falsifiers:

- user research shows the dominant job is regulated e-signature rather than
  local preparation;
- current desktop evidence cannot be authorized or maintained;
- the registration frame lowers comprehension in moderated testing;
- the browser workspace gains a verified document execution contract;
- the product changes from personal preparation to recurring team operations as
  its primary commercial wedge.

## Research sources reviewed

- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/), reviewed 2026-08-13. WCAG 2.2
  applies to different devices and includes reflow, focus, target-size, text
  alternatives, and keyboard-related success criteria.
- [WAI-ARIA Authoring Practices: Developing a Keyboard Interface](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/),
  reviewed 2026-08-13. Custom widgets need an intentional keyboard model. The
  replacement therefore prefers native ordered steps when a tab widget is not
  needed.
- [Apple Preview: Fill out and sign PDF forms](https://support.apple.com/en-ie/guide/preview/prvw35725/mac),
  reviewed 2026-08-13. The adjacent desktop mental model includes capture,
  saving, placement, dragging, and resizing. SignKit should differentiate on
  preparation and local control, not imitate a recipient-envelope platform.
- [Adobe Acrobat Sign](https://www.adobe.com/acrobat/business/sign.html),
  [DocuSign eSignature](https://www.docusign.com/products/electronic-signature),
  and [Dropbox Sign](https://sign.dropbox.com/products/dropbox-sign), reviewed
  2026-08-13. These category leaders emphasize sending, recipients, templates,
  audit trails, integrations, and legally oriented signature workflows. That is
  a boundary for SignKit's current preparation-first position, not evidence that
  SignKit supports those capabilities.

## Anything else?

Yes. The replacement should not be selected because it is the most attractive
concept in isolation. It must make the product model easier to understand,
reduce claim risk, and create a coherent bridge from landing to desktop and
metadata workspace.

## Implementation addendum: 2026-08-13

The direction was applied only to the isolated replacement candidate at
`web/concepts/2026-08-13-document-registration-studio/`. The landing makes
source, mark, clean, place, and ready visible as one bounded case. The app
candidate makes metadata, evidence, owner, boundary, and recovery visible
without presenting a signing session.

The first implementation pass intentionally uses CSS document studies rather
than current product screenshots. This keeps the visual direction honest while
asset authorization and production-parity decisions remain open.

Evidence: 4 focused contract tests passed after one real failure was fixed for
an over-broad `outline:none` assertion. An S2 mutation probe detected removal
of the illustrative truth label. Chrome local checks at 1440, 390, and 320
pixels passed with reduced motion, no overflow, no page or console errors, and
working state and filter interactions. These results are local candidate
evidence only.

Remaining gates are product comprehension, claim review, asset authorization,
route migration, checkout governance, backend execution contracts, and
deployed parity. The old root and web-app surfaces remain historical/current
evidence, not the replacement design target.
