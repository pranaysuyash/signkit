# ADR-0143: Local Document Inspection Contract

- Date: 2026-08-13
- Status: Accepted for the local-companion runtime profile; hosted route registration is explicitly excluded
- Owner: Engineering

## Decision

Document inspection is an authenticated workspace operation registered only by
the `local_companion` server capability and available only to executions with
`topology=local`. The operation reads the uploaded PDF for page
validation, computes a SHA-256 fingerprint, returns a non-retained isolated
receipt, and stores only the receipt in the existing append-only
`workspace_execution_events` table.

The receipt stores a request hash and serialized result payload in the existing
event row. Migration `9c4b7e2d1a6f` adds these fields; it is an integrated
parallel-agent change, not a second document-retention store.

The caller must provide an `Idempotency-Key`. Repeating the key with identical
bytes returns the original receipt with `replayed=true`; reusing it with
different bytes returns `409`. Cloud and hybrid executions fail closed with
`409` in the local profile, while the hosted profile does not register the
route at all. The request field is workflow metadata, not proof of locality.
This operation does not establish a hosted document-retention or
external-processing contract.

## Rationale

The workspace control plane already owns execution topology, owner scope, event
sequence, and idempotency. Reusing that canonical event ledger avoids a second
document store and keeps the local privacy boundary explicit. Persisting only a
fingerprint and receipt preserves operator evidence without retaining source
documents.

## Consequences

Local inspection is useful for controlled validation but is not a cloud document
processing promise. A future hosted document workflow must introduce a separate
reviewed storage, retention, malware/content, export, deletion, and operator
recovery decision rather than weakening this local-only contract.

## Verification

- Tier 2: `backend/tests/test_workspace_router.py::test_local_document_inspection_is_isolated_replay_safe_and_cloud_rejected` passed.
- Tier 2: `tests/test_test_environment_validator.py backend/tests desktop_app/tests/test_api_client.py` passed `42 tests`.
- Syntax compilation passed for the new service, router, and hosted smoke tool.
- Tier 2: migration-backed hosted smoke passed against temporary SQLite after
  applying Alembic head `9c4b7e2d1a6f`.

## Options and boundary decision

The alternatives considered were:

1. Keep document inspection in the shared hosted application and trust
   `topology=local`. Rejected because a hosted caller could upload bytes while
   merely declaring local metadata.
2. Keep one route but require a request-only local header. Rejected because a
   header is not a server capability or deployment boundary.
3. Register the existing route only in a local-companion runtime profile and
   keep hosted `/workspace` metadata-only. Chosen because it preserves one
   canonical route implementation while making exposure a startup capability.
4. Create a separate third API product. Deferred until hosted tenancy,
   retention, cancellation, observability, artifact custody, and legal gates
   have direct evidence.

The desktop loopback manager also verifies a per-instance HMAC health proof.
This prevents accepting an arbitrary local process that only returns generic
`200` health data. It is process identity evidence for the local companion, not
an OS sandbox or hostile-document security guarantee.

## Threat model and rollback

The boundary protects against accidental or configuration-driven document
egress through a hosted profile and against a generic loopback-port impostor.
It does not claim protection from a privileged local attacker, a compromised
desktop process, or native PDFium vulnerabilities. Rollback is to metadata-only
workspace behavior by setting `SIGNKIT_RUNTIME_PROFILE=hosted` and omitting the
local router registration; no database migration is required for that switch.

Revisit this decision when a hosted document requirement has an owner, a
versioned contract, deployment sandbox evidence, durable cancellation and
retention proof, operator recovery evidence, and legal/product approval.

## Addendum: verification after runtime-boundary correction (2026-08-13)

- Tier 3: a subprocess-imported hosted profile proves the local document route
  is absent, while the local-companion profile registers it.
- S2: the profile-boundary test was added after the locality gap was identified;
  both hosted exclusion and local registration pass.
- S2: the desktop health-manager impostor test rejects a generic healthy
  response because the HMAC proof is missing.
