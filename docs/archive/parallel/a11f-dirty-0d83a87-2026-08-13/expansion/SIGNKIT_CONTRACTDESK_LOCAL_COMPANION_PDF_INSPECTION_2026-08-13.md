# ContractDesk local-companion PDF inspection

Date: 2026-08-13
Status: Implemented local integration boundary

## Contract

`POST /workspace/executions/{execution_id}/document-inspections` is an extension
of the canonical workspace route. It accepts one PDF only when the execution
topology is explicitly `local`.

The operation performs:

`transient intake -> PDF structure validation -> isolated PDFium field inspection -> metadata receipt`

The input is bounded to 25 MB, must have a PDF extension and `%PDF-` header,
and requires an `Idempotency-Key`. The bytes are written to a temporary
directory only for the worker call. The temporary directory is removed when
the call ends. The database stores the content hash, page, candidate metadata,
runtime mode, replay key, and receipt result. It does not store the source PDF.

## Evidence boundary

The route integration test is Tier 3 because it crosses the HTTP route,
validation/service layer, actual child-process worker, and SQLite event ledger.
It covers new success, replay, conflicting retry, cloud rejection, malformed
input, and missing idempotency key.

This is not Tier 3 hosted production evidence. It does not prove tenant
isolation under deployment, external object storage deletion, cancellation of a
remote job, production rate limiting, legal artifact claims, or real browser
manual upload. Those are explicit hosted gates, not hidden assumptions.

## Parallel integration decision

The implementation that appeared during the work was retained because it used
the canonical workspace route and event ledger. It was hardened in place:

- pikepdf remains the structural preflight, not the canonical field engine;
- PDFium field detection runs through `IsolatedDocumentRuntime`;
- receipt results are JSON-safe and durable for replay;
- input reads are bounded;
- cloud topology is rejected before document processing;
- no second route, signer, or extraction pipeline was introduced.

## Operator and browser behavior

The existing `/workspace-app` form now lets the operator choose `Local
companion` or `Cloud metadata-only`. Local executions show a transient PDF
inspection control and a receipt result. Cloud executions do not show a file
control and remain metadata-only. The browser does not claim signing,
identity verification, or hosted storage.

## Remaining gates

1. Add a browser automation run that uploads a synthetic PDF through the local
   companion form and verifies the visible receipt.
2. Add cancellation and a separate asynchronous job record before any large or
   unattended batch flow.
3. Keep hosted API work behind the acceptance gate in
   `SIGNKIT_CONTRACTDESK_WEB_HOSTED_API_ACCEPTANCE_GATE_2026-08-12.md`.

Anything else? Yes: the local route is synchronous and page-scoped by design.
It is a proof and controlled companion boundary, not permission to expose
arbitrary hosted document processing or to call this a signing service.
