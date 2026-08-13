# W16 Go/No-Go Matrix: Native macOS Runtime Split (v1)

## Purpose
This is the final gate for `W16`. We only proceed to a native macOS runtime split if this matrix reaches a clear **Go**.

## Decision framing
- **Default for v1:** no native split.
- **Goal of W16:** prove whether native mac adds enough trust/fidelity/retention value to justify a second client runtime.

## Evaluation dimensions

### 1) Security/Compliance necessity (weight 35)

- **Can any critical requirement be solved only in a native mac app?**
  - examples: secure key lifecycle, OS policy enforcement, file type handler hardening
  - evidence required: reproducible issue, remediation blocked in shared stack

- **Decision scale**
  - 0 = not needed / solvable with shared stack changes
  - 1 = possible but workaround
  - 2 = risky workaround with compliance debt
  - 3 = hard requirement, currently blocking pilot

### 2) Perceived premium gap after mac polish (weight 25)

- **Measure over 2 weeks private pilot**:
  - CSAT on mac UX (target: ≥4.3/5)
  - “Would you pay more for premium UX?” positive intent (target: upward trend)
  - churn or drop-off tied to UI friction (target: no increase)

- **Decision scale**
  - 0 = neutral
  - 1 = mild friction
  - 2 = repeated feedback citing UI/runtime mismatch
  - 3 = sustained premium block despite parity fixes

### 3) Economic signal (weight 20)

- **Signals**
  - conversion rate by persona
  - upgrade from Starter → Team
  - drop on quoted objections (pricing vs UX)

- **Decision scale**
  - 0 = mixed/positive
  - 1 = weak
  - 2 = plateau despite value delivery
  - 3 = material pricing friction attributed to runtime feel

### 4) Operational cost and risk of split (inverse weight 20)

- **Decision scale**
  - 0 = clear low risk with high ROI
  - 1 = manageable but significant parallel maintenance
  - 2 = high coordination risk on auth/engine/audit parity
  - 3 = unacceptable duplication without stable shared service contract

This dimension is inverse: higher score means a **stronger case against** splitting now.

## Rules

- Compute total as weighted sum:
  - `Security*35 + Premium*25 + Economic*20 + (20 - SplitRisk*20)`
- Max score = 100.
- **Go threshold:** >= 78 and at least 2 of dimensions 1–3 are `3`.
- **No-Go threshold:** < 78 or dimension 3 = 0 while security/perceived premium scores are also low.

## Hard blockers that force No-Go regardless of score

- No secure fail-closed local key-store path with auditable fallback in current stack.
- No evidence that review, lock, grant, receipt, and queue flows are stable in shared stack.
- Any unresolved auth bypass identified in current trust path.

## Evidence bundle required before filing final W16 decision

1. Filled mac premium checklist from:
   - [mac_premium_readiness_checklist.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/mac_premium_readiness_checklist.md)
2. Pilot telemetry and feedback sample (minimum 2 weeks).
3. Current split decision record baseline:
   - [gtm_mac_runtime_split_record.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/gtm_mac_runtime_split_record.md)
4. Go/No-Go sign-off with owners and follow-up ticket ID.

## Decision outcomes

- **Go:** open W16-native ticket, add shared engine contract tasks first, then allocate native runtime build.
- **No-Go (preferred by default):** close W16 as `No-Go`, continue PySide parity + premium polish for mac, continue evidence gathering.
