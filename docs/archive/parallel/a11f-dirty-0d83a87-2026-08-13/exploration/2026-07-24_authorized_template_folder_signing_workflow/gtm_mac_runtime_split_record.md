# Mac Runtime Split Decision Record (2026-07-24)

## Decision needed
Should we start a separate native macOS app while keeping PySide for Windows/Linux for the controlled workflow launch?

## Options evaluated

### Option A — Native mac app only (SwiftUI/TCA or AppKit) + separate Windows/Linux app

**Pros**
- Best-in-class mac UX and feel
- Best chance for long-term premium perception on macOS
- Native integration depth (permissions, notarization, launch services)

**Cons**
- Two codebases for UI + duplicate workflow logic unless a shared engine service is introduced
- Highest implementation and maintenance cost early
- Slower first delivery; high risk of drifting behavior between clients
- Delayed feature launch (especially for the workflow and authorization stack)

### Option B — PySide shared desktop app for all platforms, with a hard mac premium pass

**Pros**
- Fastest path to parity and feature launch
- Shared engine and UI logic for signing + workflow + auth flows
- Lower cost for validation of core trust model and folder automation
- Cleaner sequencing: prove feature trust boundaries before investing in native rewrite

**Cons**
- Native polish is capped by Qt/mac integration limits
- May leave some mac buyers unconvinced at premium pricing until further polish
- Some mac-specific controls (first-run prompts, tray/menu affordances) may require manual tuning

---

## Recommendation (now)

**Do not start a separate native mac codebase yet.**

Ship the controlled workflow on top of PySide for all desktop platforms first, but execute a **premium mac pass**:

1. native-feel shell + stable bundle packaging
2. deterministic lock/grant UX and queue states
3. improved permission/error clarity
4. receipts, audit, and recovery path quality
5. pilot evidence collection on mac

Then run **W16** with hard metrics. Move to a native mac rewrite only if one of the three gates in `mac_premium_readiness_checklist.md` and this decision record is tripped.

---

## Strategic rationale

The workflow is high-risk-high-value (authorization, unattended execution, auditability). We need to reduce this risk with one code path and one schema first.

A native mac rewrite *before* this validation increases scope risk and could preserve a weak workflow with a shiny shell. The safer sequence is:

- **Control-first first**: workflow schema, auth/grant policy, matcher, receipts, and recovery.
- **Premium-mac pass second**: feel, polish, and friction reduction.
- **Native split third**: only if evidence proves demand and measurable perception gaps.

---

## What “Split later” would require (so it doesn’t become a rework)

- Shared non-UI engine package (`desktop_engine`) consumed by mac, PySide, and possible future apps
- Stable CLI or service contract for job execution and state operations
- Signed schema and migration compatibility for recipes/jobs/grants
- Cross-platform acceptance tests that are platform-agnostic by design
- Migration plan for settings/receipts/templates

Without this foundation, native split should be blocked.

---

## Decision criteria for revisiting this in 4–8 weeks

- Private mac pilot with 10+ workflows/week and >90% successful run-through completion
- Quantified premium sentiment gap despite the mac polish pass
- Measurable friction points that are impossible or unsafe in PySide (not merely cosmetic)
- At least one blocking mac-specific technical requirement from security/compliance/product that cannot be solved on shared stack

If any criterion is reached, open W16-native and scope a separate mac implementation.

---

## Similar GTM pattern fit

Use the same pricing and go-to-market logic we already defined: price by **governance depth** and **automation trust**, not raw speed.

- Starter: control + manual confidence
- Team: grant + review + receipt controls
- Business: multi-folder/policy + recovery confidence at scale

This means premium value comes from trust and recoverability, which both stacks can support.
