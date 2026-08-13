# Controlled Signing Workflow — Launch Deck (v1)

**Date:** 2026-07-24
**Audience:** Product, Sales, Design, Ops
**Use:** Direct copy/paste for leadership brief and internal launch discussion

## Slide 1 — Problem & promise
**Headline:** Repetitive signing is not the problem. Uncontrolled repetition is.

**Subhead:** Recurring legal, HR, and operations documents need speed, but not at the cost of control.

**Proof points:**
- Teams still manually apply signatures across recurring packets
- Mistakes happen on the wrong file, wrong role, wrong version
- Current tools assume one-off actions, not recurring control

**Promise:** Controlled Signature Recipes that keep documents local, automate repeatable work, and make every execution reviewable.

---

## Slide 2 — Product category and why now
**Headline:** Not generic template automation. Not full legal e-signature replacement.

**Positioning matrix (one-line):**
- **Cloud e-sign:** strong identity routing, often cloud-dependent and ceremony-heavy
- **Generic batch tools:** fast, less control, weak trust model
- **SignKit v1:** local-first, reusable recipe engine + explicit authorization + receipts

**What changes for users:**
- Define once, run safely repeatedly
- Keep docs local by default
- Decide where risk should stay manual vs unattended

---

## Slide 3 — Who this is for
**Headline:** Teams with recurring signing packets and strict operator control.

**Primary personas:**
1. Legal Operations Lead — “I need traceable recurring completion.”
2. HR Operations Coordinator — “I need role-level reusable packet flows.”
3. AP Analyst — “I need batch throughput with accountability.”
4. Compliance Lead — “I need hard stops and recovery, not silent automation.”

**Use-case line-up:**
- legal packets, onboarding kits, procurement attestations, high-volume exception handling

---

## Slide 4 — Core GTM flow
**Headline:** Start small, go trusted, then scale automation.

1. Build recipe with multi-role field bindings
2. Run dry run and review matches
3. Publish/activate + bounded grant
4. Folder intake with exact-match auto mode
5. Review only ambiguous/review-required jobs
6. Emit signed output + receipt lineage

**Go-to-market sequence:**
- private beta with 2–3 teams
- exact-match only first
- publish pilot metrics (time saved, false positives, recovery rate)
- unlock richer matching only after evidence

---

## Slide 5 — Pricing and commercial model
**Headline:** Premium pricing is earned through governance, not just automation speed.

| Tier | Right now value proposition | Suggested price |
|---|---|---|
| Starter | one operator, one active recipe, manual confirm | **$19/mo** |
| Team | five operators, 10 active recipes, grants + audit controls | **$59/mo** |
| Business | 20 operators, 40 recipes, multiple folders & retention policies | **$159/mo** |
| Enterprise | custom policy onboarding and support | **custom** |

**Commercial guardrail:**
- No legal-binding claims for visual placement
- No pricing tied to unsafe unattended behavior
- Upgrades map to stronger controls (grants, audit, recovery)

---

## Slide 6 — Productized screens (v1)
**Headline:** Trust is visible at every step.

**Dashboard:** lock status, grant countdown, queue, emergency stop
**Recipe Builder:** signer roles + vault asset bindings + dry-run preview
**Review Console:** review/fail/retry/quarantine by job state
**Receipt View:** lineage hash, grant, matcher class, exportable proof pack

**Success metrics (first 30 days):**
- 0 unauthorized run attempts accepted
- median time-to-first-success down
- exact-match false-positive rate in targets
- review recovery time improved

**Decision ask for this release:**
- approve DR-2026-07-24-01 and move from exploration to Sprint-1 implementation
