---
title: SignKit replacement visual direction
date: 2026-08-13
status: accepted for a non-production replacement candidate
owners:
  - product
  - design
  - web-platform
related:
  - ../review/product_visual_direction_strategy_2026-08-13.md
  - ../review/product_visual_direction_task_register_2026-08-13.md
  - ADR-0144-signkit-visual-surface-contract.md
  - ../review/signkit_experience_system_direction_2026-07-31.md
---

# ADR-0145: SignKit replacement visual direction

## Decision

Build the replacement candidate as a document registration studio.

The landing candidate combines the job clarity and current-product evidence of
`web/concepts/2026-07-31-customer-work-experience` with a bounded registration
frame inspired by `web/concepts/2026-07-31-product-museum-living-ui`.

The web-app candidate uses the precision and document context of the workbench
concept with the actual metadata-only boundary of `web/cloud_workspace`.

The replacement candidate is additive and non-production. It must not become a
second public route or a second workspace API. Promotion will require a later
route decision and release gate.

## Context

The repository has a route owner, a live browser metadata workspace, several
landing concepts, and a large dirty worktree. The route owner and the desired
future design are not the same fact. The previous pass spent the visual persona
on the legacy root and current workspace. The operator rejected that direction.

## Options considered

1. Keep polishing the legacy root and workspace. Rejected. This reinforces the
   wrong visual target and makes legacy tests look like replacement evidence.
2. Promote one existing concept unchanged. Rejected. Each concept solves only
   one part of the product problem or carries an evidence limitation.
3. Build a generic dark SaaS landing and web app. Rejected. It hides the actual
   document job and duplicates category conventions.
4. Build a composed registration-studio replacement candidate. Selected. It
   combines the strongest verified parts while preserving product boundaries.

## Derived scope

- Add a project-local `DESIGN.md` for the replacement system.
- Keep legacy root, `web/live`, and current metadata workspace files unchanged
  during the replacement-candidate build unless a separate defect blocks the
  candidate.
- Create an isolated candidate surface with landing and app views.
- Use native controls and one bounded source-to-ready interaction.
- Label simulated states and use current captures only where authorized.
- Add candidate-specific static and browser tests.
- Document route promotion, checkout, asset authorization, and app-parity gates
  as follow-up decisions.

## Risks and tradeoffs

- An isolated candidate creates temporary duplication. This is accepted because
  the user explicitly requested replacement exploration and promotion is gated.
  The candidate must have a declared expiry or promotion path.
- The registration frame may be more distinctive than familiar PDF tools. The
  fallback is a simpler ordered step list, not decorative animation.
- Current screenshots may contain sample data or incomplete states. The asset
  manifest and captions must control their use.
- The browser app remains metadata-only. The candidate must not imply that its
  visual polish closes the execution contract.

## Validation plan

- Static contract tests for ownership, truth labels, controls, images, and state
  binding.
- S2 mutation checks for the registration-frame state contract.
- Browser Tier 4 checks at desktop, 390px, and 320px widths.
- Keyboard path for every preview state.
- Reduced-motion browser context.
- Console, network, and overflow checks.
- No deployment claim until the promoted route and production parity are tested.

## Revisit triggers

- user research rejects the document-registration metaphor;
- the commercial wedge changes to regulated or team signing;
- browser execution becomes real and needs a different app contract;
- current asset authorization or runtime evidence fails;
- the candidate requires a second source of truth to become production-ready.

## Update log

### 2026-08-13: replacement direction selected

Selected after a full landing and web-app inventory and a Product Visual
Direction Strategist pass. This decision supersedes the earlier assumption that
the legacy root visual treatment was the design target. The operator's redirect
was: “you are wasting the persona on something we are going to replace”.

### 2026-08-13: candidate implementation and evidence

The selected direction is implemented as an isolated non-production candidate
at `web/concepts/2026-08-13-document-registration-studio/`. The landing uses a
bounded source-to-ready registration case. The related workspace uses the
actual metadata-first boundary and labels all state as illustrative. No
production route, checkout, API, or legacy surface was changed by this
candidate implementation.

Verification is Tier 2 plus S2 mutation evidence for the static contract and
Tier 4 for local Chrome. The browser matrix covered 1440, 390, and 320 pixel
widths with reduced motion, keyboard stage movement, record selection, and
review filtering. All six checks returned HTTP 200 with no overflow or
console/page errors. The candidate is not approved for route promotion.

## Anything else?

Yes. This ADR selects a replacement candidate. It does not authorize production
route promotion, checkout activation, deployment, or deletion of prior concepts.
