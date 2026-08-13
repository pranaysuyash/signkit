# ADR-0142: Authenticated Extraction Asset Contract

- Date: 2026-08-12
- Status: Accepted for application implementation; hosted rollout pending
- Owner: Engineering

## Decision

Use the existing `/extraction` router as the single canonical asset pipeline and
make every hosted asset operation authenticated and owner-scoped. Persist asset
ownership on `Image.user_id`, optionally link an asset to a `WorkspaceExecution`
only when that execution belongs to the same owner, and record durable operation
receipts in `ExtractionAuditEvent`.

The contract includes:

- JWT authentication for list, upload, select, process, export, delete, and audit.
- Private filesystem artifacts; response paths are internal and never public URLs.
- Database-backed idempotency keyed by owner, operation, and request key.
- Soft deletion plus physical artifact cleanup, with audit receipts retained for
  owner-visible recovery and explanation.
- Export as an explicit receipt-backed operation containing the original asset
  and a manifest, rather than an untracked file response.

## Context

The previous extraction path was suitable for local processing but did not prove
hosted authorization, lifecycle control, or retry convergence. A public static
uploads mount would make an opaque asset identifier insufficient. In-memory
deduplication would also fail across workers and concurrent requests.

## Alternatives considered

1. Keep filesystem-only sessions and rely on an opaque UUID. Rejected because
   opacity is not authorization and does not provide deletion or audit proof.
2. Add a second hosted extraction route. Rejected because it creates parallel
   validation, storage, and retry behavior.
3. Store idempotency only in process memory. Rejected because worker restarts and
   concurrent requests can duplicate artifacts or receipts.
4. Hard-delete all database records. Rejected because it removes the owner's
   ability to inspect what happened after cleanup.

## Consequences and risks

Positive consequences are explicit ownership, cross-owner denial, durable retry
convergence, private artifacts, and operator-readable receipts. The migration
adds nullable compatibility columns to the existing `images` table and a new
append-only audit table.

Remaining risks are target-database rollout, filesystem cleanup failure after a
successful soft delete, and absence of live hosted deployment evidence. Cleanup
status is recorded in the delete receipt; operations must monitor that status
and retry failed cleanup through the canonical asset service.

## Verification and rollout

- Tier 3: `backend/tests/test_extraction_router.py` plus
  `backend/tests/test_extraction_hosted.py`, 10 passing after an initial red
  run exposed and fixed response classification defects.
- Tier 2: desktop API assertions for stable idempotency headers.
- Tier 2: isolated SQLite Alembic upgrade through `e42b7f8c91aa`.
- Reproducible local release proof: `tools/run_extraction_hosted_smoke.py` applies
  the migration head and exercises the real FastAPI app; it requires the
  complete backend runtime, including Alembic.
- 2026-08-13 update: the local smoke passed after repairing the project runtime;
  target-database migration and live hosted smoke remain unverified.
- 2026-08-13 update: the current local Alembic head is `9c4b7e2d1a6f`, the
  migration-backed smoke passes through that head, and the full repository suite
  passes `145 tests`. This remains local evidence, not target deployment proof.
- Required before hosted readiness: apply the migration to the target database,
  run authenticated upload/select/process/export/delete/audit smoke, exercise
  duplicate and recovery behavior, and attach receipts to backlog item `L0-09`.

## Revisit trigger

Revisit this ADR if the application gains browser document upload, multi-user
workspace membership, object storage, background processing, or a requirement
for legal-grade immutable export/audit retention. Those changes require a new
ownership/membership and storage decision, not a parallel extraction route.
