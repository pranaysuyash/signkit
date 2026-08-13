# ADR-0143: Local Document Inspection Contract

- Date: 2026-08-13
- Status: Accepted
- Owner: Engineering

## Decision

Document inspection is an authenticated workspace operation available only to
executions with `topology=local`. The operation reads the uploaded PDF for page
validation, computes a SHA-256 fingerprint, returns a non-retained isolated
receipt, and stores only the receipt in the existing append-only
`workspace_execution_events` table.

The caller must provide an `Idempotency-Key`. Repeating the key with identical
bytes returns the original receipt with `replayed=true`; reusing it with
different bytes returns `409`. Cloud and hybrid executions fail closed with
`409` because this operation does not establish a hosted document-retention or
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
