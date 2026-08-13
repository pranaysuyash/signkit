# SignKit ContractDesk Hosted API Acceptance Gate

Date: 2026-08-12
Status: Decision record for future hosted API product, not an authorization to launch it
Owner: API Product / Architecture / Legal / Operations

## Decision

SignKit will not create a separate third production API product during the Stage 1 web proof. The current canonical path is the existing authenticated `/workspace` API with the backend-mounted `/workspace-app` control plane. A hosted ContractDesk API may be evaluated later only when every gate below has direct evidence and an accountable owner.

This keeps the local-companion proof useful while preventing a second API surface, second signing pipeline, or customer-facing claim that the current system cannot operationally support.

## Hosted API entry gates

| Gate | Required contract | Evidence required before pilot | Current status |
| --- | --- | --- | --- |
| Identity and tenancy | Authenticated principal, tenant isolation, actor-scoped access, account lifecycle | Security tests for unauthorized, cross-tenant, legacy, and missing-data paths | OPEN |
| Resource model | Versioned workspace, execution, transition, receipt, and manifest resources with one canonical route per resource | OpenAPI contract reviewed against existing `/auth` and `/workspace` routes | OPEN |
| Mutation safety | Idempotency keys, retry semantics, conflict behavior, partial-failure recovery, and audit correlation | Tier 3 route/integration evidence including duplicate, timeout, and replay cases | PARTIAL: local transition idempotency exists |
| Versioning | Explicit API version policy, deprecation window, compatibility contract, and migration owner | Versioned contract fixture plus consumer compatibility check | OPEN |
| Validation and errors | Shared schema validation and machine-readable problem details without leaking sensitive data | Invalid, malformed, oversized, and unauthorized request suite | PARTIAL: local validation exists; hosted contract not frozen |
| Data and retention | Document versus metadata boundary, storage location, retention, deletion, export, and backup policy | Data classification, threat review, deletion/recovery drill, and operator runbook | OPEN |
| Observability | Request correlation, state transitions, retries, fallbacks, provider errors, operator actions, and customer impact | Searchable logs/event ledger and incident reconstruction exercise | OPEN |
| Artifact and signing boundary | Signer identity, cryptographic provider, artifact integrity, storage, certificate/receipt semantics, and recovery | Tier 3+ production-like artifact test and legal review | PARTIAL: local PKCS#12/PAdES signing and cryptographic receipt verification exist; production custody, public/enterprise trust, timestamp/revocation, recovery, and legal review remain open |
| Legal and commercial | Terms, pricing, support/SLA, data processing, jurisdiction, claim language, and responsibility for signing | Named business/legal approval recorded with claim registry links | OPEN |
| Operations | Rate limits, abuse controls, key rotation, incident response, support escalation, and rollback | Operator readiness review and failure-recovery drill | OPEN |

## Pilot entry criteria

The hosted API gate can move from `OPEN` to `PILOT-READY` only when:

1. No duplicate route or parallel pipeline is needed to expose the approved resource contract.
2. Identity, tenancy, idempotency, validation, versioning, and audit behavior have Tier 3 evidence.
3. Real signed-artifact semantics are implemented and reviewed; the current synthetic package is not accepted as a substitute.
4. Customer-facing claims are linked to the launch claim registry and approved wording.
5. Operators can reconstruct, retry, quarantine, or recover every meaningful failure mode.
6. A rollback and data-retention plan exists for partial rollout and customer deletion requests.

## Revisit triggers

Reopen this decision when a buyer requires hosted execution, a partner requires a stable API contract, local-companion limits block a paid workflow, or the real artifact/signing boundary is ready for integration. The local signing boundary is now implemented; the remaining trigger is production trust and hosted integration readiness. Any trigger requires a new dated decision record and an updated acceptance matrix before implementation.

## Standards research applied

- OpenAPI Specification `3.1.1` is the appropriate contract baseline for a future versioned API description, reusable security schemes, and explicit request/response schemas: [OpenAPI Specification v3.1.1](https://spec.openapis.org/oas/v3.1.1.html).
- HTTP errors should be designed as machine-readable problem details rather than implementation-debug output. RFC 9457 defines the `application/problem+json` model, problem type, title, detail, status, and occurrence instance fields: [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html).
- The Idempotency-Key header guidance is currently an active IETF Internet-Draft, not a final RFC. It is useful input for the future contract, but the hosted API must pin and document its own server behavior rather than claim standards finality: [draft-ietf-httpapi-idempotency-key-header-07](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/07/).

These findings reinforce the existing gates; they do not authorize a hosted API launch or change the current canonical route topology.
