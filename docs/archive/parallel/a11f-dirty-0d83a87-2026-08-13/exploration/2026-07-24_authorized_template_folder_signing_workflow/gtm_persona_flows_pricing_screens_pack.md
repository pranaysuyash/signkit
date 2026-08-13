# GTM, persona, flow, and screens pack

**Date:** 2026-07-24  
**Scope:** Productization inputs for the Controlled Signing Workflow v1

This is the concrete reusable artifact for your ask around:
- similar GTM ideas,
- user personas/use cases,
- revamped pricing,
- flows,
- screens.

Use it as the single brief to share with design/product/operator.

## Why this is different from generic automation

SignKit is not “auto-stamp PDFs.” It is a **controlled, reviewable recipe execution system** for recurring local documents.

- Trust-first: authorization is explicit, bounded, and logged.
- Frequency-first: recurring packets become operational flow.
- Evidence-first: every run has a lineage trail.
- Local-first: files stay on user device by default.

## Similar GTM patterns to borrow (without copying)

1. **Template guardrail pattern**  
   Borrow from mature automation products: strong default-deny + template version controls + approval lane.

2. **Queue-first workflow UX pattern**  
   Borrow from operations tooling: clear job states (`queued`, `review`, `failed`, `retry`, `completed`) and obvious recovery actions.

3. **Compliance-light bundle pattern**  
   Borrow from practical business tools: one-click receipt export + short incident response playbook.

4. **Persona-led pricing pattern**  
   Price by governance complexity, not by feature sparkle.

5. **Pilot-first expansion pattern**  
   Start in one exact-match mode and add advanced matching only after corpus evidence.

### Explicit pattern diff (what to copy vs what to skip)

| Pattern | What to copy | What to avoid |
|---|---|---|
| Cloud e-signature suites | review lanes, role separation, audit vocabulary | cloud-only trust assumptions, claims we cannot support today |
| RPA/batch automation | queue model, retry behavior, operator recovery loop | ambiguous auto-run defaults and opaque failure masking |
| Template libraries | versioning, draft/approval separation, deterministic naming | “save anywhere and hope it runs” behavior |
| Compliance tooling | permit/deny language, reason-codes, incident path | over-complex controls before core trust path is stable |

### What makes SignKit different (single-line GTM promise)

- Not “automate signing faster.”
- Automate **recurring local workflows** with explicit control boundaries and recoverable trust.

## Persona set (with concrete use cases)

### Persona A — Legal Ops Lead
- Problem: recurring legal packets with repeated signatures and variable document versions.
- Value from this workflow:
  - one approved recipe per packet family;
  - visible review gates;
  - receipt pack for audits.

### Persona B — HR Ops Coordinator
- Problem: repeated onboarding packets and role-specific approvals.
- Value from this workflow:
  - role-tagged fields and multiple signer roles;
  - deterministic folder replay;
  - clear recovery path.

### Persona C — Accounts Payable Analyst
- Problem: batching approval packs and unclear operator accountability.
- Value from this workflow:
  - grant lifecycle with expiry;
  - pause/retry/recover in one place;
  - signed-output provenance.

### Persona D — Compliance Lead
- Problem: pressure to “automate and forget” without controls.
- Value from this workflow:
  - hard-stop classes;
  - denied execution without authorization;
  - explicit legal-language guardrails.

## Use-case map

- Recurring legal contract packets.
- Onboarding/exit kits with 2-4 signer roles.
- Procurement attestations with date/signature/text mix.
- High-volume exception routing (manual review for ambiguity).
- Pilot-to-production rollout from exact-match only.

## Pricing model (revamped)

### Principle
Price the governance depth and operations control:
- roles
- policy complexity
- automation trust level
- audit/recovery quality

| Tier | Core rights | Suggested |
|---|---|---|
| Starter | 1 operator, 1 recipe, ~300 outputs/mo, manual confirm only | **$19/mo** |
| Team | 5 operators, 10 recipes, ~2,000 outputs/mo, grants + audit controls | **$59/mo** |
| Business | 20 operators, 40 recipes, ~10,000 outputs/mo, retention/folders rules | **$159/mo** |
| Enterprise | custom | quote |

### Packaging add-ons
- onboarding + policy template pack
- priority support
- implementation support for team rollout
- legal/compliance documentation support (if available)

### Pricing guardrails
- Never claim legal binding for visual-only workflows.
- No pricing promise based on unsafe unattended features.
- Upgrade path is unlocked by stronger trust controls (grants, policies, receipts).

### Premium packaging and retention framing

- Yearly plans can be offered later with the same control boundaries and a small discount incentive; no feature mismatch with monthly plans.
- Add-on packs should stay operational, not legal-hardcore:
  - onboarding + naming policy pack
  - implementation and recovery playbook
  - team rollout templates
- If conversion stalls, adjust unlock depth (grants, receipts, folder policy) before cutting price.

## Runtime strategy decision for premium positioning

At v1, we should ship a single shared UI/engine stack (PySide on all platforms) and add a **native mac premium polish pass** first.

- Use this path for fastest credible launch of controlled workflow features (templates, grants, queue/review, receipts).
- Measure mac-specific friction and premium perception in the first private pilot.
- Trigger native mac split only if the W16 evidence pack indicates meaningful value left on the table that cannot be solved within shared stack polish.
- Decision record: [gtm_mac_runtime_split_record.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/gtm_mac_runtime_split_record.md)

### Decision diff: shared PySide stack vs native mac runtime

- **Shared PySide (v1):** faster launch, shared engine/logic, and less variance in behavior.
- **Native mac runtime now:** better native feel but split maintenance risk and delayed trust-hardening work.

Recommendation in this cycle: prioritize shared stack + premium mac polish.

## High-confidence flows (v1)

### Manual-confirm flow
`Build recipe → Dry run → Approve fields → Grant active → Review job → Confirm → Verify → Emit output`

- every document reviewed
- deterministic placement visibility
- operator final action required before each run

### Exact-match unattended flow
`Build recipe → Dry run → Activate exact-match + grant → Folder monitor → Validate → Auto-sign → Verify → Output`

- only exact-match class can auto-run
- non-exact classes to review

### Recovery flow
`Failure state → reason shown with actor/context → Retry (preserve context) OR Quarantine`

- preserve job context and hashes
- retry/cancel without data corruption

## Screen map

### 1) Workflow Dashboard
- active/inactive state
- grant countdown
- queue by state
- emergency stop/pause

### 2) Recipe Builder
- source doc and matcher mode
- role binding per field
- vault asset binding per role
- output folder pair and naming policy
- dry-run preview with match class

### 3) Review Console
- failures, needs review, retry state list
- reason codes and one-click actions
- quarantine path and notes

### 4) Receipt View
- recipe/grant/job lineage
- hashes and match class
- exportable evidence pack

## Distribution strategy

### Primary launch wedge
- legal/HR/ops teams with recurring document packets
- direct outreach + private beta with one recipe each

### Sequence
1. publish promise: “local, controlled, reusable signing recipes”
2. run private pilot with exact-match only
3. publish metrics (time-to-first-success, recovery rate, false positives)
4. add second workflow mode when review metrics justify

### Channel focus
- 1:1 operator outreach
- 60-min controlled onboarding webinar
- proof-focused release notes (before/after process time + error recovery)

## Message architecture

Do:
- “Authorized visual signature automation for recurring local workflows.”
- “Unlock automation with control.”

Don’t:
- “legally binding automated signature”
- “no reviews needed”
- “guaranteed legal validity”

## Readiness to proceed to build

- If we can ship v1 with this set, this supports the premium narrative without a native mac runtime split.
- If user demand shows a persistent premium gap after macOS packaging + these screens, then run W16 decision check.

## Screen-by-screen acceptance checklist (v1)

### Workflow Dashboard
- shows lock/unlock state on open
- shows active grant count and queue counts
- allows queue filter by state in one click

### Recipe Builder
- validates input/output/review folders before save
- requires role + vault asset per binding row
- enforces at least one binding
- blocks nested or overlapping folder pairs

### Review Console
- captures failed/ambiguous outcomes with reason code
- supports Retry, Quarantine, Cancel
- preserves job/context lineage for every action

### Receipt View
- exports recipe/grant/job lineage and matcher evidence
- excludes raw signature binaries and full plaintext file paths
- supports successful and recovered-failure export cases

## Message variants for launch

- Positioning: “Controlled, local-first repeatable signing workflows.”
- Trust line: “No silent runs; review remains the default for ambiguous cases.”
- Upgrade line: “Premium unlock is governance and recovery, not brute-force automation.”
