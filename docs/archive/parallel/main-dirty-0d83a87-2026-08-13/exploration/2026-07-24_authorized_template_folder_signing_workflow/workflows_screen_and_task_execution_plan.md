# Workflow implementation execution plan (v1)

**Date:** 2026-07-24  
**Purpose:** Convert sprint tickets into developer-ready, screen-by-screen execution work.

This document is the immediate implementation sequencing layer requested: who does what, what to build first, and what exactly counts as done.

## 1) High-confidence execution plan

### Phase A — Foundation (start immediately)

1. Add core schema models and persistence:
   - `desktop_app/workflows/models.py`
   - `desktop_app/workflows/store.py`
2. Implement migration and backward compatibility tests:
   - `desktop_app/pdf/template_store.py` integration points
   - `tests/` fixtures + regression suite

### Phase B — Trust boundary

1. Authorization model and grant lifecycle:
   - `desktop_app/workflows/authorization.py`
2. Vault ID integration (no raw filesystem paths at runtime):
   - `desktop_app/processing/vault.py`

### Phase C — Engine + monitor

1. Matchers and state machine:
   - `desktop_app/workflows/matcher.py`
   - `desktop_app/workflows/engine.py`
2. Signer/result contract and atomic output behavior:
   - `desktop_app/pdf/signer.py`
3. Folder monitor, recoverability, verification and receipts:
   - `desktop_app/workflows/folder_monitor.py`
   - `desktop_app/workflows/verifier.py`
   - `desktop_app/pdf/db_audit.py`

### Phase D — Operator screens

1. Workflow dashboard:
   - `desktop_app/views/main_window_parts/workflow_console.py`
2. Recipe builder:
   - `desktop_app/views/main_window_parts/recipe_builder.py`
3. Receipt and evidence export:
   - `desktop_app/pdf/db_audit.py`
   - Launch artifacts

### Phase E — Launch hardening

1. W16 parity/packaging validation
2. Launch runbook + GTM alignment
3. End-to-end pilot instrumentation and rollout metrics

---

## 2) One developer can execute this in this order

### Workstream 1 (Data/Schema) — 1 engineer

- W01 → W02 → W03
- DoD gate before moving on: round-trip migration + corruption-guarded schema tests

### Workstream 2 (Security/Trust) — 1 engineer

- W04 → W05 → W06
- DoD gate before moving on: denied unauthorized and expired grants are auditable and visible in UI

### Workstream 3 (Engine) — 1 engineer

- W07 → W08 → W09 → W10 → W11 → W12
- DoD gate before moving on: deterministic exact-match, idempotent retry behavior, verified output promotion

### Workstream 4 (UI + Launch readiness) — 1 engineer

- W13 → W14 → W15 → W16
- DoD gate before launch: manual + unattended paths are explainable, recoverable, and exportable

## 3) Screen-by-screen acceptance matrix

### Screen 1: Dashboard (`workflow_console.py`)

**Acceptance checks**

1. Top-level state is always visible:
   - `Workflow Locked`
   - `Grant Active`
   - `Jobs in Retry`
   - `Need Review`
2. Operators can reach job detail from a queue item in ≤2 actions.
3. Pause and emergency stop are one action each and block next mutation.
4. Job list supports filters: queued, needs_review, failed, completed, retry, quarantined.
5. Queue counters update within bounded delay after file arrival (exact-match mode).
6. All blocked/failed reasons are human-readable and include next action.

**Dependency:** workstream 3 state persistence and reason-code model.

### Screen 2: Recipe Builder (`recipe_builder.py`)

**Acceptance checks**

1. Multi-field workflow building supports at least 3 fields in one draft.
2. Each field requires both:
   - signer role
   - vault asset ID
3. Matching mode controls exactly what can run unattended (`exact` only for auto-run).
4. Output folder, input folder, and review folder validation prevents nested/overlapping paths.
5. Dry-run output includes:
   - matched / unmatched field count
   - match class
   - expected filename
   - risk warnings
6. Activation is blocked when required fields are missing.
7. New recipe version is immutable; edits create draft version.

**Dependency:** workstreams 1–3 (models, matcher, signer contract).

### Screen 3: Review Console / Needs-Review lane

**Acceptance checks**

1. Failed and non-exact jobs are visible with:
   - input fingerprint
   - matcher class
   - failure reason
   - recommended recovery action
2. Operators can action:
   - Retry (preserve context)
   - Quarantine (no destructive overwrite)
   - Cancel (safe stop + no source mutation)
3. No destructive action proceeds without confirmation and visible traceability.
4. Review actions preserve job identity/hash lineage.

**Dependency:** workstream 3 event model + workstream 2 grants.

### Screen 4: Receipt View / Export

**Acceptance checks**

1. Export payload includes:
   - recipe version
   - grant ID
   - input/output hashes
   - matcher evidence
   - actor + timestamps + terminal state
2. Export excludes signature raw bytes and plain access tokens.
3. Export is possible from completed and failed-recovered jobs.
4. Operator can regenerate receipt after restart from persisted job trail.

**Dependency:** workstream 3 verifier + workstream 1 schema + workstream 4 DB audit extension.

## 4) Feature-level DoD for this implementation plan

- All v1 high-risk failure classes have visible recovery.
- Full manual path remains available at all times.
- Unattended path remains exact-match-only in v1.
- Unauthorized, expired, revoked, or stale grants never run.
- Output generation is atomic and verified before publish.
- Receipts are exportable and contain audit-relevant lineage.

## 5) Immediate first sprint target (for implementation kickoff)

**Kickoff bundle (parallelizable where possible):**

- `desktop_app/workflows/models.py` skeleton
- migration tests for template extension and legacy import
- authorization contract + reason-code enum
- signer result object + structured error path
- `workflow_console.py` minimal queue visualization (read-only state) behind feature flag if needed
- Main Window action now opens the dashboard tab directly (Help → Recurring Document Workflows…)
- Added `Recipe Builder` tab with draft save flow validation for role-vault binding and folder checks
- New smoke tests: `desktop_app/tests/test_workflow_screen_smoke.py`

This allows UI and engine teams to begin against a stable API, while reducing merge risk.
