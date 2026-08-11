# Controlled Signing Workflow — Full Build Pack (v2)

**Date:** 2026-07-24
**Goal:** Product, pricing, UX, and GTM blueprint for the recurring signing workflow
**Scope:** Implemented now: workflow store + model compatibility groundwork

## 1) Executive summary (what to build first)

Ship a **local, controlled automation workflow** before native split:

- users define reusable, role-aware signing recipes,
- only authorized grants can run unattended,
- ambiguous/exception cases go to human review,
- every run emits recoverable lineage.

Premium narrative: this is sold as **governed automation infrastructure**, not generic PDF batching.

## 2) Similar GTM ideas to borrow (with what to copy vs avoid)

### A) Template-guard rails (borrow)
- Borrow: approval/activation gates before power workflows.
- Borrow: queue-first dashboard with explicit state and clear exceptions.
- Avoid: unlimited automation defaults that create trust debt.

### B) Compliance-light workflows (borrow)
- Borrow: short receipts/export packs after each run.
- Borrow: “exact-match only” for first auto-run.
- Avoid: claiming legal binding or legal enforceability for image placement.

### C) Persona-driven licensing (borrow)
- Borrow: price by governance capability (operators, retries, audit depth), not just volume.
- Borrow: upgrade gates as unlocks (draft→approved→auto-run).
- Avoid: bundling advanced controls into top tier only.

### D) Pilot-first confidence loops (borrow)
- Borrow: private pilot + cohort metrics + phased rollout by risk class.
- Borrow: explicit go/no-go matrix before adding higher automation features.
- Avoid: enabling full auto modes without recovery metrics.

## 3) User personas and key use cases

### Persona A — Legal Ops Lead
- **Problem:** recurring contract packs must be consistent and traceable.
- **Use case:** exact-match folder replay with required review lane and grant expiry.
- **Primary value:** controls + auditability.

### Persona B — HR Ops Coordinator
- **Problem:** recurring onboarding packets, rotating signers.
- **Use case:** multi-role field bindings (signature + date + initials).
- **Primary value:** repeatability with human handoff visibility.

### Persona C — Accounts Payable Analyst
- **Problem:** high-volume packet batches create bottlenecks and mistakes.
- **Use case:** queue-driven processing and retry/quarantine workflow.
- **Primary value:** throughput with recovery and no silent failures.

### Persona D — Compliance Lead
- **Problem:** pressure to automate faster despite regulatory/audit concerns.
- **Use case:** grant logs, role boundaries, review-only failures, immutable receipts.
- **Primary value:** risk reduction and explainable behavior.

## 4) Product flows (v1 sequence)

### Flow 1 — Standard (manual confirmed)
`Build recipe → dry run → approve recipe → activate grant → queue document → review → run → verify → signed output`

### Flow 2 — Exact-match unattended
`Build recipe → dry run → approve recipe → create bounded grant (exact-only, expiry, max jobs) → folder scan → run → verify → emit output`

### Flow 3 — Recovery
`Failure occurs → clear reason code + actor → action chooser: Retry / Quarantine / Cancel → restart-safe continuation`

### Flow 4 — Audit/receipt
`Job complete or recovered → export audit pack (recipe id/version, grant id, matcher class, timestamps, state transitions, error codes)`

## 5) Screen map (required in v1 UI)

1. **Workflow Dashboard**
   - Workflow lock status
   - Active grants + expiry countdown
   - Queue state filters: queued/review/fail/retry/completed
   - Pause / emergency stop

2. **Recipe Builder**
   - Recipe metadata + field bindings grid
   - Input/output/review folder selectors
   - matcher mode selector (`exact` default)
   - role + asset-id assignment per field
   - dry-run preview + warnings + save draft

3. **Review Console**
   - All review-only + failed jobs
   - reason code + next action
   - Retry / Quarantine / Cancel actions

4. **Receipt View / Evidence**
   - Lineage tree: recipe → grant → job → event trail
   - input/output hashes + verification outcome
   - one-click export JSON/CSV/PDF receipt

## 6) Pricing (revamped)

Price by **control depth and operational capability**.

| Tier | Suggested price | Positioning |
|---|---:|---|
| Starter | $19/mo | one operator, 1 recipe, manual confirm only |
| Team | $59/mo | up to 5 operators, 10 recipes, grants + review queue |
| Business | $159/mo | 20 operators, 40 recipes, audit/receipts + retry controls |
| Enterprise | Custom quote | policy-first onboarding, support, custom retention |

### Upgrade unlocks
- Starter → Team: multi-user grants + retry/review queue.
- Team → Business: receipt exports + folder policy controls.
- Business → Enterprise: advanced policy/ops support and implementation help.

## 7) Mac premium positioning decision

**Current stance:** implement shared-engine now, then add native mac premium pass once v1 trust gates are stable.

This means:
- same workflow model on all platforms,
- shared receipts and store contracts,
- mac-specific polish (native shelling, macOS style, packaging)
- native split only after evidence of real premium friction reduction in W16 metrics.

## 8) Implementation readout (what’s now done)

- Workflow persistence model: in place.
- Workflow storage contract: in place.
- Template compatibility: partial compatibility path started (`model` parsing + migration-ready store entrypoints).
- Tests to add: `desktop_app/tests/test_workflow_store.py` (round-trip, grants, jobs/events, invalid payload, expiry guard).

## 9) Decision pack for next review

Approve the following in order:
1. v1 acceptance of this pack for release scope.
2. Parallel build of model/store + authorization+engine with this contract.
3. Private pilot cohort setup.
4. W16 go/no-go on native mac split using measured premium evidence.
