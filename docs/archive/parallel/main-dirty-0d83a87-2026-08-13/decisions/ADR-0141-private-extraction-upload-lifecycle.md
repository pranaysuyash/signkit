# ADR-0141: Private extraction upload lifecycle

Date: 2026-08-12  
Status: accepted for the local/private extraction companion; hosted API use remains blocked

## Decision

Keep extraction upload artifacts private and short-lived. The canonical
`/extraction` route now reads only up to the configured upload limit plus one
byte, writes validated bytes through a private temporary file, atomically
renames the result, applies owner-readable permissions, and removes stale
image/region artifacts using a configurable retention window.

The default retention window is 24 hours and can be changed with
`SIGNKIT_UPLOAD_RETENTION_SECONDS`, subject to a one-minute minimum. Cleanup
runs during backend startup and after successful uploads. Unknown files are
preserved for operator review rather than removed by a broad directory sweep.

## Context

The desktop app can use the backend as a local companion, but the route does
not currently authenticate a principal or persist an owner/workspace scope.
Therefore a UUID session is an opaque locator, not an authorization boundary.
Removing the public static mount and nulling `file_path` prevents one class of
accidental disclosure, but it does not make the route suitable for a hosted
multi-user claim.

## Alternatives considered

- Keep direct writes and indefinite retention: rejected because partial files,
  abandoned sessions, and disk growth would remain unexplained operational
  risks.
- Add unauthenticated deletion or public asset retrieval: rejected because
  deletion and retrieval would still lack owner scope.
- Build hosted authentication, storage ownership, export, deletion receipts,
  and idempotent job orchestration in this slice: rejected as a scope jump;
  that requires a dedicated privacy/storage contract and migration plan.

## Follow-up acceptance criteria for hosted use

- Authenticated principal and owner/workspace scope are enforced on upload,
  selection, processing, retrieval, and deletion.
- Retry identity is explicit and idempotent without allowing cross-owner
  replay.
- Retention, export, deletion, recovery, and operator audit events are
  versioned and tested against stale, duplicate, and partial-failure cases.
- Tier 3 integration evidence exists for unauthorized access, concurrent
  retry, cleanup, deletion, and operator recovery.

## Rollback and observability

The change is reversible by restoring the previous write path, but doing so
would reintroduce partial-file and retention risks. Cleanup reports only a
count and never logs image contents or absolute asset paths. Upload failures
continue to return a generic server error while detailed exception context
stays in the server log.
