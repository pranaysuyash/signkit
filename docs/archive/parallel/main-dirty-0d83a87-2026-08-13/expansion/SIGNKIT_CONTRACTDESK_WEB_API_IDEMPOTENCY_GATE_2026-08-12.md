# ContractDesk transition idempotency and retry safety gate

Date: 2026-08-12
Owner: workflow + backend owners
Status: Ready for design sign-off before hosted API claims
Spec links:
- `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_API_PRODUCT_STRATEGY_2026-08-12.md`
- `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_API_PRODUCT_TOPOLOGY_ADDENDUM_2026-08-12.md`

## Scope

Stage 1 currently requires deterministic transition outcomes for duplicate POSTs on
`/workspace/executions/{id}/transitions` and explicit replay behavior.

## Current gap

- Route-level duplicate/conflict checks now pass at API boundary (`backend/tests/test_workspace_router.py`) across seeded keyed transition edges.
- Service-level actor-scope idempotency behavior is now captured (`backend/tests/test_workspace_service.py::test_transition_idem_key_lookup_is_scoped_to_actor_not_global`) and currently documents per-actor scoping.
- Hosted API reliability claims remain gated until duplicate/error semantics are proven for external API-product conditions (tenancy, legal/commercial, structured errors, operations/runbook) and explicit policy is documented for any cross-actor retry reuse.

## Proposed v1 design (implemented)

1. Extend transition request with `idem_key` (string, optional, max 80).
2. Persist `idem_key` in event-level metadata (requires `workspace_execution_events` extension)
   so duplicate calls with same key are treated as replay-safe no-ops.
3. Enforce dedupe checks before state mutation:
   - if latest successful transition for `(execution_id, idem_key)` exists, return current
     execution and latest event metadata.
   - if no existing idem record, continue and persist key with emitted transition event.
4. Return stable conflict errors for missing/invalid transition requests with structured
   reason and action-state tuple.

## Compatibility note

No hosted API promise can be made until this gate is closed.

## Decision requirement

- Requires schema/API change review
- Requires evidence that duplicate retries do not advance state on already-completed
  segments
- Requires migration plan for event table change and rollback behavior

## Open owner decisions

- Backend/ops: decide whether to keep actor-scoped dedupe (`execution_id`, `actor_user_id`, `action`, `idem_key`) as canonical or migrate to a shared-token model for downstream API contracts.
- Product/legal: confirm whether replay observability is part of acceptance for partner
  API docs.

## Current implementation status (2026-08-12)
- ✅ Route-level replay/409 verification added: `backend/tests/test_workspace_router.py` (`5 passed`).
- ✅ Service-level replay verification remains: `backend/tests/test_workspace_service.py` (`10 passed`) and route/transition regression coverage now brings combined backend transition suite to `13 passed` in one deterministic run.

- ✅ Route contract now accepts `idem_key` in `WorkspaceExecutionTransition`.
- ✅ `transition_execution(...)` returns replay-safe no-op when the same `(execution_id, actor_user_id, action, idem_key)` event already exists.
- ✅ `WorkspaceExecutionEvent` now stores `idem_key` and is indexed.
- ✅ Migration `backend/alembic/versions/d8a6c2f1b4a3_add_workspace_event_idem_key.py` adds `idem_key` plus dedupe index.
- ✅ Replay-safe behavior now has service-level tests in `backend/tests/test_workspace_service.py` (execution + duplicate-call assertions).
- ✅ `.venv`-scoped service verification completed: `.venv/bin/pytest backend/tests/test_workspace_service.py -q` (10 passed).
- ⚠️ Gate remains open for hosted API claims until recovery semantics, structured machine-readable errors, and API-product legal/commercial gates are completed.

- Reproduction command: `./.venv/bin/pytest backend/tests/test_workspace_router.py backend/tests/test_workspace_service.py -q --junitxml=docs/expansion/artifacts/contractdesk_api_idempotency_2026-08-12.xml`
- New hardening tasks before hosted API claims:
  - enforce structured API errors with machine-readable codes,
  - finalize legal/commercial productization gates.
