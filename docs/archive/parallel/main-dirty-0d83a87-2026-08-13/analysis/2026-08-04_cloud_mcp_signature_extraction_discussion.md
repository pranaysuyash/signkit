# SignKit Cloud MCP and Signature Extraction Discussion

Date: 2026-08-04
Status: Proposed exploration. No implementation or launch approval.
Scope: Future Cloud and Hybrid expansion only. This record does not change the
current local desktop product or its offline promise.

## Why this record exists

This record captures the discussion that started from an external inquiry from
Max at MCPMeter.

Source inquiry: Max `<max@mcpmeter.com>`, 2026-07-01, subject
`SignKit - Offline Signature Extraction + MCPMeter`. The inquiry asked whether
SignKit exposes an MCP server or API and whether SignKit is charging for it.
MCPMeter offered a free wiring period of approximately 500 calls, with auth,
per-call metering, and publisher payouts through its proxy.

External references reviewed on 2026-08-04:

- [MCPMeter publisher documentation](https://mcpmeter.com/docs/publishers)
- [MCPMeter server-building documentation](https://mcpmeter.com/docs/build)
- [MCPMeter privacy policy](https://mcpmeter.com/privacy)

The inquiry asked whether SignKit's "Offline Signature Extraction" product has
an MCP server or API that is already charged per call. The initial answer was
that the current desktop product has an internal local HTTP service but no
supported public MCP server or hosted API.

The product direction was then clarified: SignKit has a planned Cloud and
Hybrid expansion in addition to the local desktop product. The question is
therefore not whether the current desktop app should be put behind MCPMeter.
The question is whether a future Cloud or Hybrid SignKit surface should expose
signature extraction as an MCP capability and use MCPMeter as one distribution
and metering channel.

## Discussion record

The following operator direction is the scope boundary for this exploration:

> "like i said earlier this is for when we do the cloud based expansion work to signkit, also document everything we are discussing"

The resulting clarification is:

- Signature extraction through MCP is a future Cloud/Hybrid capability.
- It is not a request to expose the current localhost service.
- It is not a request to change the current $29 or one-time local product.
- The discussion, alternatives, risks, and open decisions belong in the
  repository, not only in chat.

## Current architecture evidence

The accepted SignKit architecture defines three topologies over one execution
system:

- Local keeps document bytes, signature assets, PDF processing, and operator
  outputs on the user's machine by default.
- Cloud stores authenticated workflow metadata, role state, event receipts, and
  operator visibility in the protected workspace control plane.
- Hybrid permits future explicit-consent synchronization after ownership,
  retention, encryption, and deletion rules are defined.

The canonical execution object is versioned, owner-scoped, event-backed, and
idempotent. Integrations must attach to this contract instead of creating a
second workflow state machine. See
`docs/decisions/ADR-0140-super-app-vertical-horizontal-integration.md`.

The browser workspace exists as a local development surface with authenticated,
metadata-only workflow execution. It is not yet a hosted Cloud product. The
current extraction router is not a safe hosted document boundary: it accepts
uploads, is not owner-scoped, and serves an uploads mount. Browser extraction
has no current web caller, retention contract, or browser PDF output. See
`docs/analysis/2026-08-03_super_app_feature_matrix.md`.

The local extraction engine in `desktop_app/processing/extractor.py` remains the
product-owned extraction path. The server-side renderer in
`backend/app/services/extraction.py` is a provisional adapter until parity
fixtures, canonical-core selection, migration, deprecation, and rollback exist.
Browser extraction remains disabled until that decision is complete.

## Proposed product shape

Signature extraction is a credible MCP capability for the future Cloud and
Hybrid product because it is a concrete, repeatable action that an agent can
request as part of a larger document workflow. It must not be exposed as a
generic unauthenticated image-to-PNG endpoint.

The proposed boundary is:

```text
MCP client
  -> SignKit MCP adapter
  -> canonical extraction contract
  -> approved Cloud job or trusted local-agent job
  -> preview/result reference
  -> explicit user-confirmed asset save
```

The MCP adapter is a transport and product adapter. It is not the extraction
engine, the workspace source of truth, the entitlement authority, or the
privacy policy.

## Topology options

### Cloud MCP

A hosted SignKit MCP endpoint exposes owner-scoped workflow and extraction
tools. The caller supplies an approved asset reference or uploads through a
separate authenticated asset path. The MCP call contains an opaque asset ID,
not a document blob, whenever possible.

The Cloud path requires:

- tenant and owner authorization;
- role claims for every mutating operation;
- owner-scoped asset storage;
- content validation and malware handling;
- retention, deletion, export, and recovery rules;
- job status, retry, timeout, and partial-failure states;
- extraction parity with the local canonical core;
- audit receipts without logging document bytes or signature pixels;
- customer-facing Cloud privacy terms and operational support.

### Hybrid MCP

A hosted control plane exposes policy, template, status, and job commands. A
trusted local agent receives the permitted metadata and executes extraction on
the customer's device. The local agent returns a receipt and result reference.
Sensitive document bytes remain local unless the customer explicitly enables a
separate asset policy.

This is the strongest fit with SignKit's trust position, but it requires device
identity, agent registration, key rotation, update safety, offline behavior,
replay protection, operator visibility, and recovery from a disconnected agent.

### Local MCP

A local MCP server can expose the desktop extraction engine through stdio or a
localhost transport. This is technically useful, but it is outside the current
MCPMeter opportunity because MCPMeter expects a public upstream endpoint. A
local MCP should be part of a future SignKit license or add-on, not a reason to
send local documents through a metering proxy.

## Candidate MCP tools

The first Cloud/Hybrid contract should be narrow and explicit:

| Tool | Purpose | Mutation | Initial status |
| --- | --- | --- | --- |
| `extract_signature_preview` | Run extraction with bounded parameters and return a preview reference | No persistent write | Candidate first tool |
| `get_extraction_status` | Read an asynchronous extraction job | Read-only | Candidate first tool |
| `get_extraction_result` | Read the completed result reference or image resource | Read-only | Candidate first tool |
| `save_signature_asset` | Save a verified result to the user's Vault or Cloud asset store | Yes | Requires explicit confirmation |
| `list_signature_assets` | List owner-scoped saved assets and provenance metadata | Read-only | Requires asset contract |
| `start_workflow_execution` | Attach extraction to an approved template workflow | Yes | Requires shared execution contract |

Do not expose `sign_pdf`, silent Vault writes, or legal-signature claims in the
first MCP. Extraction and PDF placement are separate trust and authorization
steps. A visual extracted signature must not be described as a certificate,
regulated signature, identity proof, or completed signing ceremony.

For slow Cloud processing, use an asynchronous triple:

1. `start_signature_extraction` returns a `job_id`.
2. `get_extraction_status` returns state, progress, and failure information.
3. `get_extraction_result` returns a bounded result or a controlled asset
   reference.

MCPMeter's current publisher documentation describes this pattern for image
   work, request IDs for idempotency, and tool-level pricing. These are useful
   integration inputs, not acceptance evidence for SignKit.

## Data and transport boundary

The preferred Cloud flow is:

1. The client uploads an asset directly to the authenticated SignKit asset
   service, or the local agent retains the bytes locally.
2. SignKit returns an opaque asset ID and content fingerprint.
3. The MCP call contains the asset ID plus bounded extraction parameters.
4. SignKit runs the canonical extraction job.
5. The MCP response returns a job state, preview resource, or short-lived
   result reference.
6. The user confirms any persistent save or downstream placement.

Sending raw PDF or image bytes inside an MCP request should be a separately
   reviewed option. A metering proxy may not persist bodies, but it remains a
   third-party transit and processing trust boundary. MCPMeter's documentation
   says it forwards JSON-RPC bodies and records metadata such as status,
   duration, and byte counts. This is acceptable for metadata-first tools only
   after security, privacy, and contractual review.

## Authorization, safety, and observability requirements

The MCP adapter must use the same authorization and validation stack as the
canonical Cloud API. It must not trust the MCPMeter bearer key as proof of a
SignKit owner, tenant, or role.

Required controls include:

- a SignKit account or tenant token mapped to the MCP consumer;
- owner and role checks on every read and write;
- bounded file size, dimensions, format, and processing parameters;
- malformed, adversarial, duplicate, stale, and missing asset tests;
- correlation ID and idempotency key propagation;
- safe retry behavior for start, status, save, and result operations;
- explicit timeout and partial-failure states;
- no raw filesystem paths in tool input or output;
- no document bytes, signature pixels, or bearer secrets in logs;
- an operator-visible audit receipt for every mutation;
- user confirmation before persistence, export, or PDF placement;
- rollback by disabling the adapter while preserving native Cloud and local
  stores.

MCP tool annotations such as read-only and idempotent are useful descriptions,
but they are hints. Authorization and server-side enforcement remain required.

## Commercial fit

Signature extraction has three possible commercial boundaries:

- Local MCP extraction is included in the local product or a local add-on.
- Cloud extraction can use a subscription, usage allowance, or per-extraction
  charge after cost-to-serve and buyer demand are established.
- MCPMeter can be one marketplace and per-call billing channel for the Cloud
  MCP, but it must not become the only billing, entitlement, audit, or customer
  identity system.

Reads such as status and result metadata should be free or low-cost. Expensive
extraction and transformation operations can be metered. Pricing should be
defined per tool or operation, not as an accidental flat price for every MCP
call. The pricing decision remains open.

## Decision status and staged path

Decision status: **Proposed exploration only**.

This discussion does not authorize code, deployment, a public listing, a new
Cloud price, or a customer-facing claim. The proposed dependency order is:

1. Accept the Cloud/Hybrid authority, data, and storage contracts.
2. Complete extraction parity fixtures and select the canonical processing core.
3. Complete owner, tenant, role, idempotency, audit, and recovery contracts.
4. Implement a metadata-only Cloud MCP adapter against the existing `/workspace`
   contract.
5. Prove an async extraction MCP with synthetic or explicitly sanitized fixtures.
6. Run buyer and agent workflow tests, including willingness to pay and support
   burden.
7. Review MCPMeter's current terms, privacy, fee, payout, regional, and upstream
   authentication behavior before a listing.
8. Publish only after Tier 3 integration evidence and Tier 4 runtime evidence.

## Open questions

- Which Cloud customer and repeated workflow justifies signature extraction as a
  paid operation?
- Should the first release be Cloud-only, Hybrid-first, or both behind one
  capability contract?
- How will SignKit map MCP consumers to tenants and roles?
- Does the Cloud asset service support direct upload without exposing raw bytes
  to the MCP proxy?
- What retention, deletion, export, residency, and incident commitments can
  SignKit operate and support?
- Should previews be ephemeral, stored, or returned as short-lived resources?
- What operations require human confirmation in each client?
- What is the pricing model for extraction, polling, previews, and result
  retrieval?
- What is the rollback path if the MCP listing or upstream becomes unavailable?
- Is MCPMeter the right first channel, or should SignKit validate direct Cloud
  API demand before marketplace distribution?

## Evidence and falsifiers

Current evidence is Tier 1 static architecture inspection plus current MCPMeter
publisher documentation. The Cloud workspace has local Tier 2 and Tier 3
evidence, but no hosted deployment or production API proof.

The following checks would falsify the proposed readiness claim:

- no owner-scoped Cloud asset contract;
- extraction parity fixtures fail between local and Cloud paths;
- duplicate calls can create duplicate assets or advance a workflow twice;
- a retry, timeout, or partial failure cannot be explained and recovered;
- document bytes or signature pixels appear in logs or third-party retention;
- the tool can persist or place a signature without explicit authorization;
- MCP consumer identity cannot be mapped to a SignKit tenant and role;
- the Cloud path cannot support deletion, export, or incident response;
- buyer interviews do not identify a repeated, paid workflow.

## Related documents

- `docs/decisions/ADR-0140-super-app-vertical-horizontal-integration.md`
- `docs/analysis/2026-07-31_topology_aware_workspace_foundation.md`
- `docs/analysis/2026-08-03_super_app_feature_matrix.md`
- `docs/wayfinder/SIGNKIT_SCALING_EXPANSION_EVIDENCE_BASELINE.md`
- `docs/wayfinder/tickets/choose-integration-architecture-and-privacy-boundary.md`
- `docs/wayfinder/tickets/define-local-cloud-hybrid-capability-contract.md`

## Anything else?

Yes. MCP is a transport and distribution opportunity, not the product
definition. The durable SignKit value remains a trustworthy document-execution
system with one canonical pipeline, explicit topology, user control, and
explainable recovery. The MCP surface should make that system easier for agents
to use without creating a second extraction engine, a second workspace model,
or a hidden cloud dependency.
