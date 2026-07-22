# SignKit workflow conversion decision — 2026-07-16

## Decision

Keep SignKit Personal as the primary local-first product and add a subordinate,
privacy-safe path for people whose signature task is part of a recurring document
operation. Do not turn the desktop app into an advertisement and do not represent
SignKit as a generic OCR or document platform.

The first coherent implementation stage is:

- keep the Gumroad purchase CTA primary on the SignKit landing page;
- add a recurring-workflow decision block after product proof;
- add `Help → Recurring Document Workflows…` in the desktop app;
- send only explicit source/entry/intent query values to the external enquiry;
- never append filenames, local paths, document contents, results, or processing metadata;
- use the currently live `/contact` route until a dedicated, source-aware
  `/document-workflows` route exists on `pranaysuyash.com`.

## Why this path

The current product already has a coherent individual workflow: extract a signature,
store it locally, and place it into a PDF. Current batch, field-detection, and review
work show a credible Professional direction, but one-time Personal pricing and a
higher-value operational workflow must not share the same promise or price anchor.

This stage creates the missing qualification seam without inventing a second product,
duplicating processing pipelines, or weakening the local-first trust boundary.

## Options considered

1. Link directly to `/document-workflows` now. Rejected for this stage because the live
   route returned HTTP 404 on 2026-07-16.
2. Route to the broad homepage. Rejected because it loses the visitor's workflow intent.
3. Use the live contact route with explicit attribution. Chosen as a reversible bridge;
   it returns HTTP 200 and preserves `source`, `entry`, and `intent`.
4. Add an in-app promotional card or automatic telemetry. Rejected because it would add
   visual noise and create an unnecessary privacy/trust risk.

## Product architecture

- **SignKit Personal:** local extraction, cleanup, Vault, manual PDF placement, one-time licence.
- **SignKit Professional direction:** batch queues, templates/presets, structured exports,
  candidate detection, exception review, and audit history. Pricing and entitlement remain
  a separate future commercial decision.
- **Document workflow services:** discovery, preprocessing/OCR, classification, extraction,
  review design, integrations, and controlled deployment. This belongs on the portfolio site.

## Validation plan

- targeted PySide menu-action test;
- static landing smoke checks for CTA copy, attribution, and privacy boundary;
- desktop and mobile browser rendering;
- live HTTP check for the external destination;
- broader desktop and backend regression suites because the worktree already contains
  parallel extraction/performance changes.

## Revisit trigger

Replace the `/contact` destination only after the dedicated page exists, returns HTTP 200,
and preserves source-aware qualification through submission. Revisit Professional packaging
after enough real workflow enquiries establish repeated document types, volume, exceptions,
privacy constraints, and required output systems.

## Ownership and follow-up

- SignKit repo: maintain the privacy-safe entry surfaces and event naming.
- `pranaysuyash.com` repo: build the dedicated page and source-aware form before changing
  the destination URL here.
- Product owner: decide Professional pricing and entitlements after workflow evidence exists.

## Three-pass review outcomes

### Pass 1 — immediate correctness and completeness

Confirmed the purchase path remains primary, the workflow CTA carries explicit attribution,
and the desktop action sends no document-derived data. Added targeted tests for the menu
action and landing contract. Mobile rendering exposed a price-pill overflow, which was fixed.

### Pass 2 — architecture and long-term viability

Confirmed the change extends canonical surfaces rather than adding a route or processing
pipeline. Preserved the Personal/Professional/services boundary. Runtime inspection exposed
six unreadable batch controls in two three-button rows; replaced them with a consistent
two-column action grid and added a compact-window readability test.

### Pass 3 — rule compliance and supervision readiness

Rechecked the touched diff, targeted and broad test evidence, desktop/mobile render evidence,
live destination status, privacy language, documentation, and dirty-tree preservation. No
deployment, staging, commit, push, or personal-site mutation was performed. The dedicated
portfolio destination and source-aware form remain explicitly owned by the portfolio repo.
