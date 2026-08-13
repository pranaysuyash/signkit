# ContractDesk web API topology addendum (local-companion first, hosted API gated)

Date: 2026-08-12
Owner: workflow agent (API TPM lens + existing platform architecture)
Status: ACTIVE - Stage 1 lock for web proof
Spec reference: `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_EXPANSION_AGENT_SPEC_2026-08-12.md`

## 1) Stage 1 topology lock

- Stage 1 web proof remains on the existing metadata control-plane API and does not claim full hosted signing/document execution parity.
- The scope is: local document preparation remains in the desktop execution model, and `/workspace` exposes workflow control metadata with contract-specific synthetic states.
- This is a **local-companion control-plane** choice for proof, not a separate third production API product.

## 2) Canonical pipeline and owner mapping (first-party for Stage 1)

| Stage | Responsibility | Owner now | API surface | Notes |
| --- | --- | --- | --- | --- |
| intake | document packet definition, metadata capture, owner/context | desktop workflow + `/workspace` creation | `POST /workspace/executions` | Keep packet metadata only; no document file upload in Stage 1 claim scope. |
| normalize | template/version binding and preflight state | desktop job layer + workspace execution template data | no public contract change yet | Ensure template version appears in both execution metadata and events. |
| extract | image cleanup / detection / placement | desktop engine (`desktop_app/...`) | private/local adapter only | Reused for now as a local engine contract; avoid duplicate browser engine in proof. |
| complete | placement decision and signature completion marker | desktop completion path + metadata event | workspace event for “completed” aggregate state | No new public claim of hosted placement until recovery and audit gates close. |
| state transition | human checkpoint, correction flow, approval | `backend/app/services/workspace.py` | `POST /workspace/executions/{id}/transitions` | Requires explicit synthetic ContractDesk actions and transition guards. |
| review/exception | exception classification, retry visibility, owner action | workspace route + UI | transitions + event timeline | Add `needs_correction` and `exception` with explicit operator recovery action. |
| export | receipt/output artifact materialization | local export + metadata manifest | export manifest API/event | Export manifest required for synthetic proof evidence. |
| audit receipt | ordered immutable event trail | `workspace_execution_events` and UI timeline | no schema change required for Stage 1 | Add ContractDesk-relevant event reasons and correlation fields. |

## 3) Why this does not mean “separate third production API” yet

- The current `/workspace` route family is already mounted for auth-protected web control (`backend/app/main.py`) and consumed by `web/cloud_workspace`.
- A separate hosted API would require additional non-trivial layers that are currently incomplete:
  - tenancy and service account model,
  - explicit API product ownership and entitlements,
  - retry/idempotency contract with replay safety,
  - versioning and deprecation policy,
  - structured machine-readable errors,
  - external incident/operations handoff and SLA policy,
  - legal data boundary and retention governance.
- Therefore, a separate third production API is considered **deferred** until these are complete and review-complete.

## 4) Hosted API readiness checklist (precondition, not implementation)

Hosted API (separate product) can be considered only when all items below are CLOSED:

1. Identity and tenancy model with recoverability and role claims (including participant/member behavior).
2. Document boundary policy that explicitly defines what crosses local/cloud.
3. Duplicate transition protection with idempotency keys and deterministic replay behavior.
4. Error model with versioned error codes, remediation, and telemetry mapping.
5. Contracted transition event schema with correlation IDs and source actor identity.
6. Test evidence at Tier 3+ for invalid input, duplicate retry, timeout, partial failure, and failure recovery.
7. Commercial + legal approval on pricing, entitlement, retention, and legal disclaimers.

Open items are tracked in:
- `A-4`: hosted API readiness gates
- `B-6`: transition idempotency command path
- `D-3`: sales positioning and packaging implications

## 5) Immediate tracker updates implemented here

- `TASK-0F`: explicit addendum publication and sales alignment work is in progress.
- `A-2`: canonical pipeline mapping now points to this addendum.
- `A-3`: API-product claim safety review is the next legal/product gate.
- `A-4`: readiness checklist for hosted API is created in this scope as a direct follow-up action.

## 6) Confidence update

Confidence on Stage 1 web API topology: **0.72**.
Known uncertainty remains on hosted-API safety gates and transition idempotency implementation status.

## Addendum: enforceable runtime boundary (2026-08-13)

The local document-inspection route is now registered only when the backend is
started with `SIGNKIT_RUNTIME_PROFILE=local_companion`. A hosted instance keeps
the metadata `/workspace` routes but does not expose the document-inspection
route. Setting `topology=local` in a hosted request cannot activate local PDF
processing.

The desktop loopback manager sends a per-instance health token and verifies the
HMAC proof returned by `/health`. A generic healthy HTTP response is not
accepted as the SignKit companion. This is a local process-identity check, not
an OS-level sandbox claim.

The earlier Stage 1 text describing "no document file upload in claim scope" is
preserved as historical scope. The dated local-companion extension is a
separate, bounded capability with its own route registration, receipt contract,
and evidence record. Hosted API readiness remains open.
