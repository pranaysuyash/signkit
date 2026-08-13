# ContractDesk web API product strategy and topology decision

Date: 2026-08-12
Status: Active strategy draft (evidence-backed)
Owner: workflow agent + API TPM framing

## 1. Decision question

For the first web-based ContractDesk proof slice, should SignKit:

1. Extend the existing local-core authentication API into a signed workspace surface for synthetic metadata + state visibility,
2. build a separate cloud API-only product, or
3. implement a third, managed API platform first and treat web as a secondary client?

## 2. Verified evidence snapshot (Tier 1 unless stated)

- The repository already has an authenticated workspace API in `backend/app/routers/workspace.py` and metadata-only models in `backend/app/models/workspace.py` (workspace, status transitions, events).
- Existing workspace lifecycle is constrained to `pending_review -> awaiting_participant -> completed/cancelled` in `backend/app/schemas/workspace.py`/`backend/app/services/workspace.py`.
- The backend exposes extraction endpoints in `backend/app/routers/extraction.py`, but these are local-processing endpoints and do not yet represent a multi-tenant production API product contract.
- The public web control-plane and API are the same auth/protected service when users visit `/workspace-app` (mounted in `backend/app/main.py`).
- Marketing checkout and offer remains on the launch page in `index.html` and `web/live/js/checkout-*`, while web/local execution concerns remain in separate surfaces.
- Wayfinder policy already states the product decision space is Local/Cloud/Hybrid, with integration/API expansion as a top-level unresolved lane (`docs/wayfinder/SIGNKIT_SCALING_EXPANSION_WAYFINDER_MAP.md`).
- Wayfinder ticket `choose-integration-architecture-and-privacy-boundary.md` explicitly blocks treating the current extraction API as hosted document boundary.

Unknowns/constraints (to resolve before claiming API-ready):
- tenancy and account-recovery model for Cloud/Hybrid surfaces,
- legal/data-retention obligations across topology boundaries,
- idempotency/retry behavior for workflow jobs,
- public versioning policy for API schema changes,
- external support and operator recovery model.

## 3. API fit alternatives

### Option A — Extend the existing workspace API as the Stage 1 web proof layer

**What it is now:** reuse current metadata-oriented control-plane API for contract packets and synthetic state transitions, and optionally extend schemas for ContractDesk states while keeping document bytes out of API payloads.

**Users:** existing desktop+web-control-plane internal workflows first, then ContractDesk prospect evaluation.

**Pros:**
- Lowest implementation risk for a first proof because route contract already exists.
- Strong alignment with current source-of-truth rule and “no duplicate API route” rule.
- Clear boundary with marketing claims (`local_processing_boundary` remains intact).

**Cons:**
- Not a public external partner API yet; developer onboarding is currently absent.
- Limited commercial surface unless entitlement and pricing hooks are added.

**Implementation burden:** medium.

### Option B — Separate Cloud/Hosted public API product as the first web surface

**What it is:** stand up a third API service dedicated to browser-native document execution and partner integrations.

**Users:** external integrators, teams with cloud-first requirements.

**Pros:**
- Clear commercial moat if tenancy/governance is finished.
- Independent ops model for cloud workloads.

**Cons:**
- High risk today because it requires auth, retention, audit, recovery, legal, observability, and support systems that are explicitly not yet implemented.
- Would likely duplicate current desktop engine until canonical contracts are split cleanly.

**Implementation burden:** very high (current stage).

### Option C — Separate third internal API platform first (control-plane API + partner APIs), then build web as client

**What it is:** decouple internal APIs and external APIs now, while web is kept as consumer.

**Users:** internal teams first, then external later.

**Pros:**
- cleaner long-term ownership if tenancy and rate-governance are committed to early.

**Cons:**
- Adds a coordination layer before core ContractDesk proof is stabilized.
- Contradicts current wayfinder direction that integration/API work should wait on topology and packaging gates.

**Implementation burden:** high, with significant proof obligations before user-facing value.

## 4. Recommended path

**Primary choice for Stage 1 web proof:** Option A.

Rationale:
- It reuses an existing, tested route model and avoids building a parallel execution surface.
- It does not imply hidden cloud document processing.
- It creates a credible path to prove synthetic states (`received`, `needs_correction`, `ready_for_review`, `approved`, `signed`, `exported`, `exception`) and audit traces by extending existing model + transitions.
- It preserves the local-first moat while still building web proof and sales articulation.

This recommendation is operationalized in:
- `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_API_PRODUCT_TOPOLOGY_ADDENDUM_2026-08-12.md`.

**Longer-term option when to switch to Option B/C:** only after explicit proof gates in Section 6 are cleared.

## 5. API TPM-style boundary model (local-first first)

### Capability and ownership mapping

| Capability | Option A owner now | Option B/C owner later |
| --- | --- | --- |
| Intake metadata creation | Workspace API (`POST /workspace/executions`) | API gateway + tenant policy layer |
| Synthetic state transitions | Workspace transition endpoint (`POST /workspace/executions/{id}/transitions`) | Versioned API state machine service |
| Receipt/audit lineage | Existing event log model + workspace events | Immutable audit ledger with retention policy |
| Extraction/placement execution | Desktop desktop/local workflow today; web control plane coordinates metadata | API-orchestrated or adapter execution contract with explicit locality flag |
| Exception/review/retry | Owner-only transitions + new event types (to be added) | Typed workflow incidents + idempotent replay semantics |
| Policy/entitlements | Existing user/license seam + explicit packaging gates | Product entitlements + tenant entitlement graph |

### Error, idempotency, and onboarding implications

- **Error model (now):** endpoint-level `HTTPException` with machine-readable `detail` strings; no structured error code taxonomy yet.
- **Idempotency (now):** not explicitly implemented for transitions; duplicate submission risk exists.
- **Onboarding (now):** user registration/login + token-based access to own workspace executions only.
- **Onboarding for API product later:** should add API keys/service accounts, rate limits, quotas, webhook contracts, and explicit environment policies before opening public integration docs.

## 6. What must be in place before claiming a separate hosted API product

The following conditions must be closed before any Option B/C claim:

1. **Identity + tenancy:** owner recovery, service-account model, and explicit role matrix.
2. **Data boundary contract:** what crosses local/cloud boundaries, retention windows, redaction guarantees.
3. **Idempotent state transitions:** duplicate-safe `execution_id` or idem-key strategy and dedupe behavior.
4. **Structured API errors:** machine-readable error codes + remediation guidance.
5. **Versioning + deprecation policy:** explicit breaking-change path.
6. **Observability + incident recovery:** failed transitions, retries, manual recovery logs.
7. **Packaging lock:** pricing and commercial ownership (who owns metering, support, SLA).
8. **Legal gates:** claims around evidence, retention, and workflow records reviewed before public promises.
9. **Launch-claim gate:** public API claims must align with `docs/launch_claims/registry.md` and `tests/test_launch_claim_registry.py`.

## 7. Actioned tracker updates (parallel to this strategy)

- Add Stage 1 contract states to workspace status enum and schema as synthetic states with compatibility-safe migration.
- Add explicit idempotency and retry semantics for transition writes.
- Add API error payload model and machine-readable error taxonomy for transition failures.
- Add a deterministic manifest test for synthetic flow execution and audit export.
- Add a separate architecture ADR before evaluating Option B/C.
- Publish the topology addendum and map hosted-API readiness gates to tracker items `TASK-0F`, `A-4`, and `B-6`.

## 8. Tracking confidence and next decision points

Current confidence for Stage 1 recommendation is **0.72**.

- Medium confidence that Option A is correct for the current ContractDesk proof requirement.
- Low confidence that we can ship Option B/C this cycle without additional work.

Next decision owner:
- Pranay to confirm product boundary for “API as product vs API as control plane” after this strategy + tracker updates are synchronized with sales conversation notes and hosted-API gate closure status.
