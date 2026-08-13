# SignKit sales execution brief

Date: 2026-08-12
Status: Agent handoff, proposed execution order
Owner: Pranay

## Immediate objective

Turn SignKit into evidence for the exact ContractDesk conversation: a bounded,
paid workflow audit or implementation slice around extraction, completion, signing
state, audit evidence, and human review.

The first deliverable is not a consumer showcase or another CLM. It must let Akshat
see one realistic contract-document exception path, distinguish what SignKit already
does from what would be implemented for ContractDesk, and evaluate a paid next step.

The broader web-expansion inspection and staged architecture plan are specified in
[`docs/expansion/SIGNKIT_CONTRACTDESK_WEB_EXPANSION_AGENT_SPEC_2026-08-12.md`](../expansion/SIGNKIT_CONTRACTDESK_WEB_EXPANSION_AGENT_SPEC_2026-08-12.md).

## What is verified in the repository

- The product purpose is extract, clean, save, and place signatures on PDFs locally
  by default (`PRODUCT.md`, `docs/launch_claims/registry.md`).
- The current Personal offer is $29 one time at launch, with $39 as the regular price.
  Team and Business offers are not public offers (`docs/PRICING.md`).
- Gumroad is the actionable checkout fallback because the Dodo product ID is empty
  (`web/live/js/checkout-config.js`).
- The current sales thesis prioritizes small legal teams, then CA/accounting/tax,
  real-estate transactions, HR, and document-service teams
  (`docs/sales/SALES_OPERATING_SYSTEM.md`).
- SignKit already has extraction, Vault, PDF placement, integration fixtures, YAML
  flow files, and a demo runner in the repository. These are implementation signals,
  not proof that a prospect has bought or adopted the product.
- The existing demo runner currently fails static compilation because
  `tools/demo_runner.py` has an indentation error after a `try:` statement. The
  integration test collection also requires `cv2`, which is not available in the
  current interpreter. These are launch-evidence blockers, not reasons to add more
  product surface.

## First wedge to test

Use one contract-completion exception lane. The specimen workflow is:

> Receive a contract PDF, extract or clean the required signature asset, complete the
> defined document step, record the signing state, route an exception to human review,
> and export an auditable result with the input, decision, and output linked.

The agent must label each step as either currently implemented in SignKit, a local
demonstrator, or proposed ContractDesk integration work. No missing capability may
be presented as shipped.

This wording does not claim regulated, qualified, or universally legally binding
signatures. It also does not claim that SignKit replaces a CLM or e-signature system.

## Agent work order

### 1. Model the ContractDesk workflow slice

Owner: workflow agent

- Create a synthetic contract packet and a small explicit state model: `received`,
  `needs_correction`, `ready_for_review`, `approved`, `signed`, `exported`, and
  `exception`.
- Map the current SignKit extraction, Vault, PDF placement, and export paths to those
  states. Record missing transitions rather than hiding them.
- Define the audit record for each transition: timestamp, actor, input hash or stable
  identifier, decision, output, and reason for exception.
- Define the human-review checkpoint and the acceptance test for one completed packet.

Acceptance: the repository contains one reviewable workflow contract that can be
discussed with ContractDesk without claiming a finished CLM integration.

### 2. Repair and prove the demo path

Owner: implementation agent

- Fix the syntax error in `tools/demo_runner.py` without creating a second runner.
- Make a deterministic ContractDesk-style fixture flow execute against the shared
  extraction and PDF pipeline.
- Add a small smoke check that proves the runner imports and the flow reaches the
  expected output path. If the full Qt stack is unavailable, report that separately
  and keep a non-UI pipeline proof.
- Produce a redacted sample input, cleaned signature output, final PDF, and a short
  run manifest containing source fixture, output paths, timestamp, and pass/fail.
- Preserve the existing shared extraction, Vault, and PDF signing pipeline.

Acceptance: a fresh agent can run one documented command and obtain the same named
artifacts, or the exact missing environment dependency is surfaced with a next step.

### 3. Build the ContractDesk proof pack

Owner: showcase agent

- Record one 60 to 90 second walkthrough using the repaired flow. Show the exception
  lane, not only a happy-path signature extraction.
- Show four beats: incoming contract, extraction/completion, state and human-review
  checkpoint, and audit-linked output.
- Add a one-page technical handoff under `docs/sales/` containing the workflow,
  implemented-versus-proposed boundary, data handling, and paid-slice acceptance
  criteria. The Personal price is background only, not the ContractDesk pitch.
- Use real screenshots or a real screen capture from the current runtime. Do not use
  fabricated customer counts, testimonials, benchmark speeds, or legal guarantees.
- Frame SignKit as a local preparation and evidence component that can complement
  ContractDesk, not as another CLM.

Acceptance: a prospect can understand the job and next action without a live verbal
explanation from the builder.

### 4. Make the paid ContractDesk path explicit

Owner: sales-surface agent

- Add a clearly bounded paid workflow proposal, not a generic demo CTA.
- Ask for one workflow, current manual exceptions, input/output format, data boundary,
  acceptance criteria, timeline, and budget. Do not publish Team or Business pricing.
- Keep the offer contract-first and customer-funded for any integration or custom work.

Acceptance: the agent can hand Akshat a concrete paid-slice proposal with scope,
deliverables, exclusions, data boundary, timeline, and acceptance test.

## ContractDesk-specific offer

If Akshat or the ContractDesk team responds, offer a paid, bounded discovery slice:

1. Map one document workflow from intake through completed PDF and audit evidence.
2. Identify manual corrections, signing-state ambiguity, and follow-up exceptions.
3. Implement or prototype one local extraction/completion component with explicit
   state transitions, human review, audit output, and a written acceptance test.

Do not pitch SignKit as a replacement CLM. The first question is which workflow still
creates manual corrections or follow-up work.

## Do not build yet

- Multi-user sync, SSO, cloud retention, browser extension, broad CLM integrations,
  regulated certificate signing, or public enterprise pricing.
- A second demo runner, second signing engine, or parallel checkout configuration.
- Generic landing-page variants before one proof pack is usable in outreach.
- Automated outreach or scraped contact lists.

## API positioning for ContractDesk outreach

- Stage 1 proof and discussion stay on the existing `/workspace` control-plane API
  (`backend/app/routers/workspace.py`) with metadata-first proof states.
- This is treated as a local-companion proof surface, not a separate hosted
  partner API product.
- A separate hosted API product can be proposed only after hosted-API gates are
  closed: tenancy and identity, idempotent transitions, structured errors,
  versioning/deprecation policy, observability, incident recovery, and legal/commercial
  gating.
- The decision log for this boundary is now in:
  - `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_API_PRODUCT_STRATEGY_2026-08-12.md`
  - `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_API_PRODUCT_TOPOLOGY_ADDENDUM_2026-08-12.md`
  - `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_EXPANSION_AGENT_TRACKER_2026-08-12.md`

## Evidence and review gates

- Static claim checks remain governed by `docs/launch_claims/registry.md`.
- The sales workspace remains `docs/sales/`; do not create a second pipeline truth.
- A passing unit or static test is not proof of a buyer-ready demo. Capture runtime or
  production-like evidence for the demo and checkout separately.
- Revisit the wedge after 20 to 30 qualified conversations, or earlier if a stronger
  repeated workflow signal appears.
