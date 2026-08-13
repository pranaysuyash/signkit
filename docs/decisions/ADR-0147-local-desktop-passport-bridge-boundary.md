# ADR-0147: Keep the local desktop execution owner and browser workspace bridge explicit

Status: Accepted for local product development; hosted bridge deferred
Date: 2026-08-13
Owners: Product, desktop, web-platform, operations
Related tasks: RECON-17, RECON-18, QA-17, QA-18

## Decision

The desktop workflow engine remains the canonical execution owner for the
local source-to-ready flow. The browser workspace remains the canonical
metadata-first orientation and control-plane surface. A local bridge now
projects desktop job state into the browser workspace as an explicit
local-companion integration rather than a second signing engine, another
workflow store, or a hosted-service assumption.

The two proofs remain named separately because they prove different owners,
and the bridge proof joins them only at the metadata boundary:

- `tools/run_local_source_to_ready_proof.py` proves local extraction, cleanup,
  vault round-trip, PDF placement, retry, execution passports, and the visual
  artifact receipt.
- `tools/run_local_product_browser_proof.mjs` proves the browser landing and
  metadata-only workspace boundary, including responsive and reduced-motion
  behavior.

The combined local browser proof is now the end-to-end operator evidence for
the local bridge. It is not hosted deployment, packaged-installation, or
cryptographic-signature evidence.

## Context

The local product now presents the document registration studio at `/` and
the local companion exposes `/workspace-app/`. The desktop store at
`desktop_app/workflows/store.py` owns local jobs in the local application data
directory. The browser workspace routers and SQLAlchemy models own browser
workspace executions in the backend database. The shared
`contracts/execution_passport.py` intentionally carries metadata only and
rejects document bytes at the boundary.

The new disposable-fixture source-to-ready proof found and fixed a real
workflow defect: retry transitions were not incrementing the job attempt
counter. The corrected engine now accounts for `RETRY`, `FAILED`, and
`CANCELLED` transitions. This makes the local execution proof useful as a
recovery receipt, but it does not create a cross-surface projection.

## Bridge requirements

The implemented RECON-18 bridge satisfies the following local requirements:

1. Use the existing local companion route family and canonical passport
   projection. Do not add a duplicate workspace route or a second workflow
   pipeline.
2. Identify a desktop job with a stable execution identifier and project only
   metadata, state transitions, attempt counts, error class, timestamps,
   receipt references, and operator recovery instructions.
3. Never send document bytes, private filesystem paths, vault secrets, or
   extracted source images through the browser workspace boundary.
4. Require an explicit local authorization binding between the browser
   session and the desktop companion. A browser link alone is not proof of
   ownership.
5. Keep retry and recovery actions owned by `WorkflowEngine`; the browser
   surface may request an action but must not mutate the local JSON store or
   duplicate transition logic.
6. Define disconnected, stale, missing-job, concurrent-retry, and companion
   shutdown behavior. Each state must be visible to the operator and
   recoverable without guessing.
7. Add targeted tests plus a deliberate mutation or failure test proving that
   the bridge cannot expose document bytes and cannot bypass authorization.
8. Re-run the local browser proof with the opaque `artifact_id` from the
   source-to-ready manifest and verify that the browser-visible passport points
   to that receipt reference while preserving the separate evidence tiers.

## Options considered

1. Read the local JSON job store directly from the hosted or browser backend.
   Rejected: it breaks the local/hosted boundary, creates an undocumented
   filesystem dependency, and risks exposing private state.
2. Copy desktop jobs into a second browser-only database and let both sides
   mutate state. Rejected: it creates parallel workflow ownership and makes
   retries, stale state, and audit reconciliation ambiguous.
3. Move local execution into the browser workspace. Deferred and currently
   rejected: it would change the product's local-processing boundary and
   require a separate migration, retention, security, and operator-recovery
   decision.
4. Keep the surfaces separate indefinitely. Acceptable fallback only if
   operator research shows that a bridge adds more confusion than value. It
   would require updating the product orientation and release backlog to
   state that limitation plainly.
5. Add a local-companion, metadata-only projection with one execution owner.
   Preferred next research direction: it preserves local processing, gives
   operators one understandable status surface, and avoids duplicate routes
   and pipelines.

## Verification plan and closure criteria

RECON-18 is closed at the local evidence tier. The route tests cover exact
owner binding, hosted-profile rejection, metadata-only projection, path and
message exclusion, retry delegation, and non-retryable state handling. The
11-mutant S3 manifest kills both bridge invariants. The fresh real-browser
proof demonstrates the complete operator sequence: authenticated local job
projection, direct URL and missing-job failure, browser retry, terminal
recovery guidance, an opaque reference to the source-to-ready artifact receipt,
document-byte exclusion, and zero browser errors.

The local proof is Tier 4 for observed browser behavior and Tier 3 for the
cross-surface HTTP sequence. Hosted deployment, packaging, provider, and
external-research gates remain open elsewhere in the backlog.

## Addendum (2026-08-13): retry idempotency and concurrency hardening

The local bridge now treats retry as a keyed mutation of the canonical desktop
workflow store. `POST /workspace/local-jobs/{job_id}/retry` accepts an optional
`Idempotency-Key`; when omitted, the bridge derives a bounded key from the job
and the attempt observed before lock acquisition. The route revalidates the
authorized job under a re-entrant process and OS file lock, checks the durable
retry-receipt collection, delegates one execution to `WorkflowEngine`, and
persists the returned job snapshot before responding. A repeated key therefore
returns the original result without invoking the engine again, including after
the job reaches a terminal state.

The passport exposes the opaque request key as metadata only. It does not carry
paths, document bytes, or raw failure messages. The JSON store remains the only
local source of truth; the retry receipt is an internal replay record, not a
second workflow state machine. Receipt retention and compaction remain a future
store-maintenance decision if high-volume local automation requires it.

Verification added in this pass covers same-key replay, store reload, two
concurrent keyed requests converging on one engine call, invalid key lengths,
and a deliberate replay mutant in the S3 sensitivity manifest. The focused
suite passes `32` tests at S1, and the complete mutation manifest kills
`12/12` mutants at S3. A fresh source-to-ready proof passes at Tier 4 with
artifact receipt `sha256:7872316227d38d452962120ed99d93dc5b9850d1721c7627bdbb093d4201c6c5`;
the real-Chrome bridge proof also passes at Tier 4 with `401` unauthenticated
rejection, `404` missing-job rejection, retry recovery, no browser errors, and
no document bytes in the browser workspace.

This closes local retry idempotency at the current JSON-store evidence tier. It
does not close hosted retry, provider retry, packaged-process supervision, or
cross-machine coordination.

## Revisit triggers

Revisit this ADR when the desktop UI exposes a stable, user-approved job
identity, when the companion authorization mechanism is selected, when the
browser workspace contract changes, or when operator comprehension research
shows that separate local and browser status surfaces are preferable.
