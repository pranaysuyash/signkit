# Controlled Signing Workflow Sprint Board (v1)

## Sprint structure

### Sprint 1 — Schema and contracts (P1)

- **Ticket W01: Migration-safe recipe schema**
  - Scope: `desktop_app/pdf/template_store.py`, `desktop_app/workflows/models.py`
  - Goal: support multi-field + versioned recipes with immutable approved versions.
  - Dependencies: none.
  - DoR: legacy template format identified; JSON migration strategy written.
  - DoD: import + round-trip tests pass for legacy and new recipe formats.

- **Ticket W02: Store and persistence layer**
  - Scope: `desktop_app/workflows/store.py`
  - Goal: durable `workflow_recipes`, `workflow_jobs`, `execution_grants`, and receipt tables.
  - Dependencies: W01.
  - DoR: schema migration plan and idempotent initialization agreed.
  - DoD: open-read-only schema and write path works in local smoke run.

- **Ticket W03: Data model regression tests**
  - Scope: tests
  - Goal: lock down schema invariants and migration corner cases.
  - Dependencies: W01, W02.
  - DoR: canonical fixtures created.
  - DoD: failing legacy path is guarded, corruption-resistant load behavior exists.

### Sprint 2 — Authorization and signer boundary (P1)

- **Ticket W04: Grant model and enforcement**
  - Scope: `desktop_app/workflows/authorization.py`
  - Goal: deny-by-default execution, expiry, usage caps, role checks.
  - Dependencies: W01, W02.
  - DoR: role taxonomy approved.
  - DoD: unauthorized execution blocked with auditable reason and code.

- **Ticket W05: Vault asset identity integration**
  - Scope: `desktop_app/processing/vault.py`, `desktop_app/workflows/models.py`
  - Goal: recipes reference vault asset IDs, not filesystem paths.
  - Dependencies: W01, W04.
  - DoR: vault retrieval utility available in workflow context.
  - DoD: execution resolves authorized asset via vault, no raw path writes.

- **Ticket W06: Secure store adapter + fail-closed adapter path**
  - Scope: `desktop_app/workflows/authorization.py`
  - Goal: OS-backed key store check before granting execution.
  - Dependencies: W04.
  - DoR: local secure store behavior profiled.
  - DoD: unavailable store blocks execution and surfaces operator warning.

### Sprint 3 — Engine and execution (P1)

- **Ticket W07: Matcher implementation**
  - Scope: `desktop_app/workflows/matcher.py`
  - Goal: exact-match class for v1 and deterministic family skeleton.
  - Dependencies: W02.
  - DoD: deterministic fixture coverage for true/false exact matches.

- **Ticket W08: State machine engine**
  - Scope: `desktop_app/workflows/engine.py`
  - Goal: run jobs through `discovered -> validating -> matched -> queued -> processing -> verifying -> completed`.
  - Dependencies: W02, W04, W07.
  - DoR: event/state contract finalized in interfaces doc.
  - DoD: duplicate prevention and idempotency key in place.

- **Ticket W09: Atomic signer contract update**
  - Scope: `desktop_app/pdf/signer.py`
  - Goal: structured result object and no blind output mutation.
  - Dependencies: W08.
  - DoR: result code schema with failure enums.
  - DoD: failure reasons are machine-readable and UI-ready.

### Sprint 4 — Folder operations and observability (P2)

- **Ticket W10: Folder monitor and queue recovery**
  - Scope: `desktop_app/workflows/folder_monitor.py`
  - Goal: watcher + reconciliation, stabilization, symlink/escape guard.
  - Dependencies: W08.
  - DoR: reconciliation scan interval and grace period set.
  - DoD: missed events recovered by periodic scan.

- **Ticket W11: Verifier and receipt lineage**
  - Scope: `desktop_app/workflows/verifier.py`, `desktop_app/pdf/db_audit.py`
  - Goal: output checks and hash lineage persistence.
  - Dependencies: W09.
  - DoR: hash/hash-algo policy approved.
  - DoD: output verification mismatch moves job to needs_review/failure.

- **Ticket W12: Job event/audit observability**
  - Scope: `desktop_app/pdf/db_audit.py`
  - Goal: event trail with state transitions and actor IDs.
  - Dependencies: W11.
  - DoR: reason code taxonomy final.
  - DoD: UI can query and render review state with evidence snippets.

### Sprint 5 — UX and launch readiness (P2)

- **Ticket W13: Workflow dashboard + grant controls**
  - Scope: `desktop_app/views/main_window_parts/workflow_console.py`
  - Goal: queue status, pause/lock actions, grant actions.
  - Dependencies: W10, W12.
  - DoR: interaction rules approved.
  - DoD: all failure/review actions are explicit in UI.

- **Ticket W14: Recipe builder + review controls**
  - Scope: `desktop_app/views/main_window_parts/recipe_builder.py`
  - Goal: multi-field builder, dry-run preview, version activation.
  - Dependencies: W13.
  - DoR: field-binding and role-binding UX spec finalized.
  - DoD: cannot publish with missing role/asset binding.

- **Ticket W15: Receipt export + launch pack**
  - Scope: `docs/.../workflows_launch_pack.md`, `desktop_app/pdf/db_audit.py`
  - Goal: exportable evidence bundle and incident-ready runbook.
  - Dependencies: W11, W12, W13.
  - DoR: legal-copy review complete.
  - DoD: compliant receipt includes recipe/grant/matcher/hash lineage.

### Sprint 6 — Platform parity and premium fit review (P2)

- **Ticket W16: macOS parity validation & premium UI polish decision**
  - Scope: `platform` packaging configuration, app shell, onboarding copy.
  - Goal: validate whether native mac packaging/perceived quality requirements demand a native runtime split.
  - Decision artifact: `gtm_mac_runtime_split_record.md`
  - Decision scoring: `w16_go_no_go_matrix.md`
  - Dependencies: W13, W14.
  - DoR: macOS usability/security review template signed by product and engineering.
  - DoD:
    - packaging and install UX is polished (bundle, permissions prompts, auto-update notes),
    - Keychain path security behavior is documented,
    - explicit go/no-go decision for native mac wrapper is recorded.

## Dependencies map

- W01 → W02 → W03
- W02 → W04 → W05 → W06
- W02/W04/W07 → W08 → W09
- W08 → W10 → W11 → W12
- W10/W12/W13/W14 → W15
- W13/W14 → W16

## Priority and sequencing rationale

- P1 tickets protect correctness and trust boundaries before operator-facing automation.
- P2 tickets optimize operator experience and readiness only after execution trust is proven.

## Exit criteria for moving sprint boundaries

- End of Sprint 2: no unauthorized execution can happen.
- End of Sprint 3: exact-match path is reproducible and recoverable.
- End of Sprint 4: queue reliability and evidence capture are reliable.
- End of Sprint 5: operators can run, stop, recover, and export evidence without raw internals.

## Developer task breakdown (v1 launch readiness)

Use this as the execution ledger for assignment and status tracking.

| Ticket | Primary files | Owner role (target) | Expected input from other stream | Output |
|---|---|---|---|---|
| W01 | `desktop_app/pdf/template_store.py`, `desktop_app/workflows/models.py` | Data model engineer | None | Immutable version model + migration contract |
| W02 | `desktop_app/workflows/store.py` | Data model engineer | W01 schema contract | Tables, migrations, queries |
| W03 | `tests/` | QA engineer | W01/W02 fixtures | Regression suite + corruption tests |
| W04 | `desktop_app/workflows/authorization.py` | Security engineer | Role model + grant policy | Deny-by-default authorization |
| W05 | `desktop_app/processing/vault.py`, `desktop_app/workflows/models.py` | Security engineer | W01 + W04 | Vault asset binding + asset-ID enforcement |
| W06 | `desktop_app/workflows/authorization.py` | Security engineer | OS key-store probe results | Fail-closed secure-store adapter |
| W07 | `desktop_app/workflows/matcher.py` | Engine engineer | W02 corpus assumptions | Exact-match matcher + deterministic checks |
| W08 | `desktop_app/workflows/engine.py` | Engine engineer | W02/W04/W07 | Job state machine + idempotency |
| W09 | `desktop_app/pdf/signer.py` | Engine engineer | W08 result contract | Structured signer result + atomic contract |
| W10 | `desktop_app/workflows/folder_monitor.py` | Engine engineer | W08 | Folder intake + recovery loop |
| W11 | `desktop_app/workflows/verifier.py`, `desktop_app/pdf/db_audit.py` | Engine engineer | W09 + W10 | Output checks + lineage persistence |
| W12 | `desktop_app/pdf/db_audit.py`, `desktop_app/workflows/engine.py` | Observability engineer | W11 reason codes | Render-ready event/audit trail |
| W13 | `desktop_app/views/main_window_parts/workflow_console.py` | UI engineer | W10/W12 | Dashboard + controls statefully wired |
| W14 | `desktop_app/views/main_window_parts/recipe_builder.py` | UI engineer | W13 + W07 | Multi-field builder + dry-run review |
| W15 | `desktop_app/pdf/db_audit.py`, `docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/workflows_launch_pack.md` | Product engineer | W11/W12/W13 | Receipt export + runbook updates |
| W16 | Packaging config (`desktop_app`, installer assets, docs) | Product engineer + release engineer | W13/W14 | W16 decision package + parity evidence |

### Cross-ticket acceptance dependency notes

- `W01` must finish before any runtime writes are made to workflow tables.
- `W08` state transitions can begin in UI only after `W12` reason codes are stable.
- `W14` has a hard guard: publish path must require all required bindings.
- `W15` is not complete without launch artifact and one successful export test from completed job + one from recoverable failed job.
