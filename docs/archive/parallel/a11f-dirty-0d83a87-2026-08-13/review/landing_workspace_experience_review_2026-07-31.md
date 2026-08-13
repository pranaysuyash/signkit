# Job-led workspace experience concept review

Date: 2026-07-31  
Status: parallel concept for review, not a live-site replacement

## Artifact

`web/concepts/2026-07-31-workspace-experience/`

This is a new concept. It does not modify `web/live/` and it does not alter the
preserved rejected exploration at `web/concepts/2026-07-31-b2c-redesign/`.

## What changed in the concept

- The front door is the shared document-preparation job: a private PDF
  workspace, rather than a legal, HR, or "signature extractor" persona page.
- The hero uses a fresh current desktop selection capture. The workspace
  switcher loads fresh current extraction, loaded-PDF, and Vault captures.
- The product is positioned as a document operations workspace whose first
  demonstrated workflow is extraction and placement.
- Workspace, vault, emerging repeated work, assistance, and trust have
  deliberately different surface treatments within one type, colour, motion,
  and spacing system.
- Emerging and future surfaces are explicitly labelled. No simulated dashboard
  is presented as a current product screen.
- Interaction is limited to anchor navigation, restrained pointer parallax, and
  a real-state workflow switcher. Reduced-motion preferences disable motion.

## Browser and runtime evidence

The concept was served from the repository root using the project environment:

```sh
./.venv/bin/python -m http.server 4176 --directory .
```

Visual browser inspection was performed at `1440×920` and `390×844` on:

`http://127.0.0.1:4176/web/concepts/2026-07-31-workspace-experience/index.html`

Observed evidence:

- Tier 4 desktop: the hero framed the current selection workspace correctly;
  product images loaded directly from current runtime-capture assets.
- Tier 4 interaction: the stage switcher correctly changed from extraction to
  loaded PDF, then Vault, and updated accessible tab state, caption, image alt
  text, and counter.
- Tier 4 mobile: the trust section and stacked content stayed legible at
  390 pixels wide.
- Browser console: clear after an inline concept favicon was added.

Static checks passed:

```sh
node --check web/concepts/2026-07-31-workspace-experience/app.js
./.venv/bin/python -m py_compile scripts/capture_current_product_surfaces.py
```

## Three review passes

### Pass 1: Immediate product and copy correctness

Removed persona-led positioning and the theatrical signature metaphor. Current
screens are evidence, not invented UI. The concept does not claim signing
validity, consent, cloud collaboration, certificate signing, or autonomous AI.

### Pass 2: Long-term architecture

The page uses the experience-system direction: hero, workspace, vault,
automation, assistance, and trust can evolve independently without changing
the product category. The direct image references avoid introducing a second
asset copy or a shadow source of truth.

### Pass 3: Review readiness

The concept is isolated, uses semantic regions and tabs, supports reduced
motion, and has live browser evidence. It remains review-only until the user
approves a direction. A live replacement needs a fresh completed PDF-placement
capture from the current premium profile and a separate fix for the discovered
selection-sync validation fault.

## Known limits and closure path

- The Vault capture is a real empty current state, so it is used only in the
  switcher as a candid capability surface, never as a polished populated Vault
  claim. Closure: capture a real authorized populated runtime state.
- The repeated-work and assistance panels are conceptual system expressions,
  marked as emerging or guided. Closure: replace conceptual language or labels
  with runtime evidence as each capability ships.
- No final purchase or download CTA is connected. Closure: attach the approved
  live conversion flow only after product and commercial owners confirm it.

## Anything else?

Yes. This should be judged as the first page inside an experience system. A
future live handoff should extract its visual primitives and motion rules into
the canonical landing implementation rather than copying this isolated concept
piecemeal.
