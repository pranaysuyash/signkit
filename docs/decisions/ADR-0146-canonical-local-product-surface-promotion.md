# ADR-0146: Promote the document registration studio into the local canonical surface

Status: Accepted for local product development, hosted promotion deferred
Date: 2026-08-13
Owners: Product, design, desktop, web-platform

## Decision

The long-term local product direction is now represented by the canonical root
surface at `/`. The root uses the document registration studio language and
shows one bounded chain: source, mark, clean, place, and ready. It points local
operators to the existing backend-mounted `/workspace-app/` surface, which
remains the sole browser workspace implementation and remains metadata-first.

This is a local product promotion, not a deployment or hosted-capability claim.
The root preview is illustrative. The desktop application remains the source of
truth for extraction, cleanup, reusable marks, PDF placement, and export. The
browser workspace may inspect a local PDF through the local companion contract,
but it is not a browser signing engine and does not retain document bytes in
the workspace surface.

## Context

The selected visual direction had previously been isolated under
`web/concepts/2026-08-13-document-registration-studio/`, while `/index.html`
still used the older launch-page model. That separation preserved design review
history, but it left the local product entry path pointing at a superseded
mental model. The existing web workspace already had a tested local-companion
runtime and a canonical `/workspace-app` mount, so creating another app would
have duplicated ownership.

## Options considered

1. Keep the old root and continue reviewing the candidate in isolation. Rejected:
   it leaves the local product on the superseded visual and information model.
2. Make the concept folder a second public route. Rejected: it creates another
   landing truth source and conflicts with the public-surface route contract.
3. Promote the selected direction into `/`, keep the existing workspace route,
   and preserve the candidate as design history. Chosen: it aligns the local
   product, avoids duplicate application ownership, and keeps hosted claims
   gated separately.

## Derived implementation scope

- `/index.html` is the local canonical acquisition and product-orientation
  surface.
- `web/canonical_landing/` owns the root interaction and visual tokens. The
  candidate concept remains preserved for comparison and research history.
- Existing `web/live/js/checkout-config.js` and `checkout.js` remain the only
  checkout owners.
- Existing `backend/app/main.py` and `web/cloud_workspace/` remain the only
  workspace mount and browser control-plane owners.
- The root must retain the launch-claim registry markers and qualified product
  boundary copy.
- Local browser verification must cover desktop, 390px, 320px, keyboard state
  changes, reduced motion, and the landing-to-workspace handoff.
- Local development must provide one recoverable startup path for the root and
  companion so the operator workflow does not depend on undocumented process
  choreography. The launcher may manage process lifecycle but must not become
  a proxy or second route owner.

## Verification and evidence

- Static contract suite: 24 focused local-product contract tests passed, S1,
  after updating the
  canonical landing contract.
- JavaScript syntax: `node --check web/canonical_landing/app.js` and
  `node --check web/live/js/checkout.js` passed, S1.
- Public claim audit: `tools/audit_public_surface.py --strict` passed locally,
  with warnings limited to retained historical pages, S1/Tier 1.
- Browser Daemon observed the new root title, state transition, checkout state,
  no horizontal overflow at 390px, and the local workspace link target, Tier 4.
- The backend proof runner observed `/workspace-app/`, its assets, and the
  metadata-only surface on local port 8001, Tier 3. The browser workspace
  390px no-overflow check also passed, Tier 4.

## Remaining gates

This ADR does not close user comprehension research, screen-reader testing,
real provider purchase evidence, signed packaging, hosted deployment parity, or
the actual disposable-fixture source-to-ready operator receipt across the
desktop execution owner and browser orientation surface. The latter remains
tracked as `RECON-17` / `QA-17`; none of these gates are implied by the root
promotion.
The root local workspace link assumes the documented local companion port
contract, defaulting to 8001. The process-level local launcher is now provided
by `tools/run_local_product_stack.py`; a unified single-origin topology remains
a separate deployment concern.

The desktop source-to-ready proof remains the execution-owner proof, while the
browser proof now includes the explicit local bridge. The bridge projects the
desktop passport through `/workspace/local-jobs`, preserves the desktop store
and `WorkflowEngine` as owners, and excludes document bytes, paths, and event
messages. Hosted deployment and packaged release claims remain separate.

## Local startup addendum: 2026-08-13

`tools/run_local_product_stack.py` is the canonical local operator/developer
entrypoint. It starts the existing FastAPI app and `serve.py`, waits for health
and root readiness, uses isolated SQLite and filesystem data defaults under
`.codex-test-tmp/` regardless of ambient database or data-directory
environment, prints both URLs, and terminates both child processes together.
Alternate local resources require explicit `--database-url` or `--data-dir`
options. It does not introduce a proxy, duplicate route, or hosted claim.

Evidence: `--once` startup/cleanup passed with an ambient database and data
directory deliberately overridden, and logs showed uploads under
`.codex-test-tmp/local-product-stack-data/`. A long-running stack then passed
the Tier 4 local browser proof at all three root viewports plus the workspace.

## Revisit triggers

Revisit when the local execution contract changes, the browser workspace gains
verified document execution, moderated comprehension research falsifies the
registration-studio direction, or the product's primary job changes from local
document preparation to a different workflow.
