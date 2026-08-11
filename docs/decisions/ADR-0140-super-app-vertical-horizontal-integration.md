# ADR-0140: Vertical and horizontal integration for SignKit

Date: 2026-08-03
Status: accepted architecture direction; implementation and release gates remain open
Scope: desktop workflow, browser workspace, backend control plane, release/build

## Decision

Build SignKit as one execution system with three explicit topologies:

- **Local:** document bytes, signature assets, PDF processing, and operator
  outputs remain on the user's machine by default.
- **Cloud:** authenticated workflow metadata, role state, event receipts, and
  operator visibility are stored in the protected workspace control plane.
- **Hybrid:** future explicit-consent synchronization of versioned assets and
  execution state, with ownership, retention, encryption, and deletion rules
  defined before any document upload.

These are topology choices over one domain model, not three products. The
canonical execution object is versioned, owner-scoped, event-backed, and
idempotent. Desktop workflows and browser workspace actions must map to that
contract instead of creating separate state machines.

## Why this path

The repository already has strong vertical depth in extraction, Vault storage,
PDF placement, field detection, workflow recipes, grants, folder monitoring,
retry/quarantine, and audit records. It also has a metadata-only FastAPI
workspace with authentication, a versioned template catalog, explicit state
transitions, and chronological event receipts. The leverage is to connect those
surfaces through shared contracts, not to add more disconnected screens.

The public landing remains a separate acquisition surface. It must not become a
workspace shell, document upload route, or source of truth for product state.

## Canonical ownership

| Concern | Owner | Rule |
| --- | --- | --- |
| Extraction and cleanup | `desktop_app/processing/` | One algorithm and validation path; browser calls a future adapter, not a fork. |
| Vault and signature assets | `desktop_app/processing/vault.py`, `desktop_app/library/` | Local encrypted assets first; sync requires a versioned asset contract. |
| PDF placement and export | `desktop_app/pdf/` | One coordinate and PDF adapter contract. |
| Local workflow execution | `desktop_app/workflows/` | Local operator engine with explicit states, retry, quarantine, and audit. |
| Cloud workflow metadata | `backend/app/routers/workspace.py`, `services/workspace.py`, `schemas/workspace.py` | One `/workspace` route family and one versioned execution/event contract. |
| Browser workspace UI | `web/cloud_workspace/` | Consumer of the protected API; no document pipeline duplication. |
| Checkout and entitlements | `web/live/js/checkout-config.js`, `web/live/js/checkout.js`, `desktop_app/license/` | One public checkout config and one entitlement boundary. |
| Packaging | `build-tools/`, `.github/workflows/` | Profile-specific builds with artifact, signing, install, and launch evidence. |

## Integration contract

Every execution must expose:

- stable execution ID and template code/version;
- topology and owner identity;
- explicit status, allowed transition, attempt, and idempotency key;
- ordered event receipt with actor, timestamp, previous state, next state,
  reason, and correlation ID;
- source/output/review references without placing document bytes in cloud events;
- retention, deletion, and export policy;
- operator-visible failure and recovery action.

### Execution hierarchy

The existing models represent different levels and must not be collapsed by
name alone. A cloud `WorkspaceExecution` is an aggregate packet/register
(`backend/app/models/workspace.py`), while a local `WorkflowJob` is a child file
processing job (`desktop_app/workflows/models.py`). The integration contract is
therefore:

- `ExecutionAggregate`: owner, template/version, topology, aggregate status,
  correlation ID, and aggregate event receipt;
- `ExecutionChildJob`: input fingerprint, recipe/version, file state, attempt,
  output reference, and child events;
- an explicit mapping from aggregate state to child-job summary, never an
  implicit reuse of one enum;
- aggregate transitions are idempotent commands that may enqueue child jobs;
  child retries cannot advance the aggregate twice;
- migration starts as read-only projections from existing local jobs and cloud
  executions, with rollback by disabling cross-topology commands and retaining
  each native store.

The first implementation must define these schemas and mapping tests before
claiming that desktop and browser executions advance identically.

### Extraction ownership decision

`desktop_app/processing/extractor.py` is the product-owned local extraction path.
`backend/app/services/extraction.py` currently contains a server-side renderer
and validation path. It is treated as a provisional adapter, not a second
product engine. Before any browser document feature, parity fixtures must prove
equivalent validation and output behavior, then one shared processing core must
be selected. The migration must include a deprecation warning for the losing
path, caller migration, and a rollback window. Until that work lands, browser
extraction remains disabled.

Role names such as reviewer and participant are not identity proof. Before an
external reviewer or participant can act directly, the backend needs membership,
role claims, authorization checks, and audit coverage.

## Staged implementation sequence

### Slice 1: observable, reproducible release substrate

Make the root deployment and browser asset contract deterministic. Publish the
canonical `_redirects`, verify JavaScript content types, add a workspace-aware
web test target, and record deployment URL, commit, route status, asset state,
and provider state. This is a release prerequisite, not product polish.

### Slice 2: shared execution and role/event contract

Complete the local vertical execution contract in this slice: folder ingestion,
matching, signature placement, review, retry/quarantine, audited export, and
the supported batch progress/cancel and placement-template paths. Then extend
the existing `/workspace` schemas and desktop workflow models with
membership, role claims, correlation IDs, idempotency keys, and retry-safe event
receipts. Add integration tests for owner isolation, invalid transitions,
terminal replay, duplicate retry, and operator visibility. Keep `/workspace` as
the sole workspace route family.

### Slice 3: topology convergence without document bytes

Map `WorkspaceExecution` aggregates to local `WorkflowJob` children through an
explicit projection and command envelope. Prove creation, review, completion,
retry, cancellation, and replay behavior with metadata-only fixtures. Do not
upload documents or signatures in this slice.

### Slice 4: privacy-safe asset path

Before exposing browser documents, define owner-scoped storage, content hashes,
retention, deletion/export, encryption, malware/content validation, quarantine,
partial failure, and recovery. Extend the canonical extraction pipeline only
after a separate privacy/storage ADR is explicitly marked **Accepted** by its
owner and reviewers and its Tier 3 security/integration evidence is attached.
Until that gate passes, cloud document bytes are prohibited: the workspace may
carry metadata and opaque references only, and browser extraction remains
disabled. A public static uploads mount is not an acceptable cloud document
boundary.

### Slice 5: horizontal surfaces after the core contract

Add integrations, notifications, reporting, billing/entitlements, and
administration as adapters around the execution/event contract. Each adapter
must declare retry, idempotency, credential ownership, rate limits, failure
visibility, and rollback. Do not add an integration merely because a connector
exists.

## Non-goals

- No second extraction engine, signing engine, workspace route family, or
  checkout configuration.
- No cloud document storage, sync, certificate-backed signature, identity
  verification, or compliance promise before Tier 3 evidence.
- No public Team, Business, or Automated Packet Ops pricing before fulfilment,
  support, retention, and payment contracts exist.
- No concept tree becomes canonical by visual preference alone.

## Risks and rollback

The largest risk is coupling document bytes to a cloud workflow before ownership,
retention, and recovery are defined. Roll back by keeping cloud executions
metadata-only and disabling asset adapters while preserving local processing.

The second risk is state divergence between desktop and browser workflows. Roll
back by rejecting cross-topology transitions until the shared execution/event
contract and idempotency tests pass.

## Alternatives, assumptions, and governance

Alternatives considered:

1. **Three independent products:** rejected because it duplicates execution
   state, audit, and support semantics.
2. **Cloud-first document workspace:** rejected because the current privacy,
   retention, ownership, and recovery contract is incomplete.
3. **Desktop-only expansion:** rejected as the long-term shape because it cannot
   provide controlled remote metadata, operator visibility, or integrations.

Assumptions: local document processing remains the trust anchor; the current
workspace metadata model is useful but not proof of a hosted product; and any
future sync is opt-in and reversible. Tradeoff: the shared aggregate/child
model adds migration work now but prevents divergent state machines later.

Owner: product/engineering owner for the SignKit repository. Required reviewers:
desktop workflow owner, backend/security owner, and launch/release owner. Related
records are [`docs/analysis/2026-07-16_local_first_trust_architecture_decision.md`](../analysis/2026-07-16_local_first_trust_architecture_decision.md),
[`docs/analysis/2026-07-31_topology_aware_workspace_foundation.md`](../analysis/2026-07-31_topology_aware_workspace_foundation.md),
and [`docs/analysis/2026-08-03_super_app_feature_matrix.md`](../analysis/2026-08-03_super_app_feature_matrix.md).
This ADR supersedes no earlier decision; it extends those local-first and
workspace foundation records and must be linked from any future execution or
storage ADR. Revisit when the first cross-topology integration test passes, when
a privacy or legal requirement changes, or when the local/backend extraction
parity decision is resolved.

## Decision acceptance and implementation evidence

This ADR records the architecture decision now. It does not declare the product
or any slice release-ready. Implementation acceptance for Slices 1 to 3 requires
Tier 3 integration evidence; browser behavior requires Tier 4 observation; and
desktop release artifacts require build, signing, install, and launch proof.
Current local code and tests are Tier 2, with selected prior desktop runtime
evidence at Tier 4. Hosted routing, workspace deployment, role authorization,
private document storage, and signed cross-platform artifacts remain open.

## Anything else?

Yes. The super-app is not a larger landing page. It is a trustworthy execution
system whose horizontal capabilities compound the vertical document workflow.
The next implementation unit is the local vertical execution contract plus its
aggregate/child mapping, not another surface or integration.

## Update log

- 2026-08-03: recorded the Local/Cloud/Hybrid topology decision, canonical
  ownership boundaries, staged slices, non-goals, rollback path, and evidence
  gates. Derived from the current feature matrix and live repository inspection.
- 2026-08-04: recorded a proposed Cloud/Hybrid MCP exploration for signature
  extraction in `docs/analysis/2026-08-04_cloud_mcp_signature_extraction_discussion.md`.
  This does not authorize implementation or change the local-first boundary.
