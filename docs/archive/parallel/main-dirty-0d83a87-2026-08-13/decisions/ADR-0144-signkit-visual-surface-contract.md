---
title: SignKit visual surface contract
date: 2026-08-13
status: accepted for the canonical landing and metadata workspace
owners:
  - product
  - design
  - web-platform
related:
  - ../review/product_visual_direction_audit_2026-08-13.md
  - ../review/signkit_experience_system_direction_2026-07-31.md
  - ../BRAND_NARRATIVE_CONTRACT.md
  - ../PUBLIC_SURFACE_QA_MATRIX.md
---

# SignKit visual surface contract

## Decision

SignKit uses a calm document-operations studio language across public and
browser surfaces. The system shares semantic roles, type discipline, focus
behavior, motion rules, and evidence boundaries. It allows different surface
expressions where the user's task changes:

| Surface | Primary job | Visual expression |
| --- | --- | --- |
| Canonical landing | Understand the job, see current proof, choose the next action | Warm paper field, quiet editorial hierarchy, dark proof and purchase panels |
| Current local product proof | Inspect a precise document workflow | Dense dark tool surface with clear controls and real captures |
| Metadata workspace | Record and recover workflow state | Dark operational frame plus paper work area; metadata-first language |
| Future Cloud / Hybrid direction | Understand a possible topology without mistaking it for shipped capability | Abstract, status-labelled direction only |

The landing is not a security terminal, generic SaaS dashboard, consumer
signature marketplace, or dark-first identity. Its emotional target is relief
through control: a consequential document can move toward ready without a
fight.

## Semantic visual roles

The implementation must map values through roles rather than repeat literals:

- `paper`: warm, low-glare reading surface;
- `ink`: deep green-black authority surface;
- `muted-ink`: secondary copy with readable contrast;
- `local-signal`: current/local/ready state only;
- `attention`: price and review attention only;
- `action`: primary action or selected state only;
- `rule`: quiet dividers and boundaries;
- `error`: actionable failure state.

The same role may resolve differently by surface. This is intentional. A
workspace status signal may need a dark-frame value while the landing uses a
light badge. The role name remains stable so the product does not drift into
unbounded colour decoration.

## Typography roles

- Editorial display type is reserved for the job, chapter titles, and a small
  number of high-value statements.
- Neutral sans type carries body copy, controls, prices, forms, and actions.
- Utility mono or tracked sans type carries workflow labels, evidence captions,
  and explicit status language.
- Headings use balanced or pretty wrapping where supported. Body text remains
  readable at touch-mobile widths.

## Interaction and motion contract

- Actions use buttons. Navigation uses links.
- Every interactive control has a visible `:focus-visible` state.
- Motion reveals state or causality. Decorative entrance motion is not a
  product proof.
- `prefers-reduced-motion: reduce` disables non-essential motion while keeping
  the same semantic state and action order.
- Touch controls use a deliberate tap target and `touch-action: manipulation`.
- A public demo may show only current capability or visibly labelled
  illustrative direction. It must not simulate a shipped Cloud, Hybrid, AI,
  certificate-signing, or autonomous workflow.

## Evidence contract

- Current product proof comes from the release bundle or an authorized runtime
  capture.
- Public screenshot assets are governed by
  `docs/landing/PUBLIC_DEMO_ASSET_MANIFEST_2026-08-13.md`.
- A screenshot does not prove privacy, performance, customer adoption, or a
  regulated-signature guarantee.
- A screenshot state label must match the visible workflow. A PDF signing frame
  cannot be described as a cleaned extraction result.

## Options considered

1. **Keep the neo-brutalist launch page as the whole system.** Rejected because
   it makes price, badges, and card framing louder than document completion and
   does not scale to the metadata workspace.
2. **Make every surface a dark operational console.** Rejected because the
   acquisition page is document-heavy and must support reading, evidence
   inspection, and trust boundaries in bright environments.
3. **Use a generic premium SaaS system.** Rejected because gradients, equal
   cards, and invented dashboard metaphors would hide the real document job.
4. **Calm document-operations studio.** Selected because it preserves current
   product truth, gives the local workflow a credible material language, and
   allows the workspace to remain operationally dense without confusing roles.

## Derived scope

This decision requires the following implementation consequences in the same
work unit:

1. Canonical landing structure must expose the first action early on mobile,
   retain claim and checkout ownership, and use semantic focus, image, and
   reduced-motion primitives.
2. Metadata workspace must use the same role vocabulary and accessibility
   behavior without changing its metadata-only product contract.
3. Public demo state labels and asset hashes must be reviewed together.
4. Focused tests must assert the binding between the surface and the contract.
5. Browser verification must cover desktop, 390px touch-mobile, 320px narrow
   mobile, keyboard focus, and reduced motion.

## Revisit triggers

Revisit this ADR when:

- a real browser-native document execution contract ships;
- Cloud or Hybrid capability and proof gates close;
- the current local workflow changes materially;
- public user research shows that the calm studio language harms comprehension
  or conversion;
- a new surface needs a role that cannot be expressed without duplicating the
  token or evidence source of truth.

## Anything else?

Yes. Production route and claim parity remains a release gate outside this ADR.
This decision does not authorize a Cloudflare deployment, payment activation,
or public release without the evidence in `docs/PUBLIC_SURFACE_QA_MATRIX.md`.

## Update log

### 2026-08-13: application boundary corrected

The earlier implementation pass applied this contract directly to the legacy
root and current metadata workspace. The operator rejected that scope because
those surfaces are expected to be replaced. The contract remains useful as a
long-term role and truth reference, but replacement design selection is now
governed by
[`ADR-0145-signkit-replacement-visual-direction.md`](ADR-0145-signkit-replacement-visual-direction.md).

The replacement candidate is isolated and non-production. No route promotion or
legacy surface rewrite follows from this addendum.
