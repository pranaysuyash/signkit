# CDO Execution Passport Unit

Date: 2026-08-12
Product: SignKit local-first signing workflow and planned browser workspace
Status: Contract, read-only projections, and browser presentation implemented

## Why this unit exists

The CDO audit identified a systemic split between the real Local workflow
engine and the metadata-only browser workspace. The product needs one shared
explanation of an execution before it needs shared document storage or shared
execution. The Execution Passport is that explanation.

It is a read-only projection of identity, topology, state, safe event receipts,
recovery guidance, and opaque evidence references. It is not a document
container, upload contract, signing API, or sync mechanism.

## Canonical contract

The dependency-light contract lives in
`contracts/execution_passport.py`. Its required system-level concepts are:

- execution identity and passport version
- topology and source of truth
- owner role and versioned template identity
- aggregate state and optional child-job state
- correlation and idempotency receipts
- input fingerprint and opaque output reference
- attempts, safe evidence, recovery action, and timestamps
- explicit metadata-only data boundary

The contract rejects unsupported topology values and any data boundary other
than `metadata_only_no_document_bytes`.

## Implemented projections

- Local `WorkflowJob` plus `WorkflowJobEvent` projects through
  `desktop_app/workflows/passport.py`.
- Browser workspace `WorkspaceExecution` plus event receipts projects through
  `backend/app/services/passport.py`.
- The existing workspace execution response now includes `passport`; no second
  route or parallel persistence path was created.
- Local filesystem paths and local error messages are excluded. A completed
  local output is represented as `local-output:<job_id>`, not as a path or
  document payload.

## Verification

- `python3 -m pytest tests/test_execution_passport_contract.py -q` -> `4 passed`
- The focused tests cover metadata-only serialization, redacted local errors,
  recovery actions, topology rejection, workspace authority, and idempotency
  receipt mapping.
- Evidence tier: Tier 2 targeted contract tests, with S2 red-to-green evidence
  for the new passport invariants.
- Backend ORM route execution remains unverified in this interpreter because
  the available system Python does not have SQLAlchemy installed. The adapter
  and response schema compile statically; a dependency-complete backend test
  run is still required before claiming Tier 3 API proof.
- Browser consumer contract: `5 passed` across the Passport and workspace
  presentation tests.
- `node --check web/cloud_workspace/app.js` passed.
- Live browser inspection reached the workspace over the local static server:
  one main landmark, no horizontal overflow, no console errors, and the
  synthetic proof flow visibly rendered boundary, source of truth, status, and
  recovery fields. This is Tier 4 evidence for the presentation path only,
  not proof of authenticated API execution.

## Task ledger

- [x] Define one Execution Passport contract for Local and browser metadata.
- [x] Map Local job state and safe evidence without leaking file paths.
- [x] Map browser aggregate state and idempotency receipt without claiming
  document execution.
- [x] Enrich the existing workspace response without adding a duplicate route.
- [x] Add focused contract tests and document evidence limits.
- [x] Add the browser Passport presentation hook for source of truth, status,
  boundary, and recovery guidance without a document claim.
- [x] Preserve a missing-Passport state as unavailable instead of fabricating
  live authority or recovery values.
- [ ] Connect the presentation to an authenticated live workspace fetch path;
  closure requires the existing API response to be consumed at runtime, not
  synthetic state alone.
- [ ] Add a local-to-browser transport decision only after ownership,
  authentication, retry, offline recovery, and operator visibility are
  designed. This remains intentionally outside this metadata-only slice.

## Next product unit

The next non-deployment, non-commit unit is authenticated response wiring for
the browser consumer: feed the existing `passport` response into the current
workspace state and prove the rendered values in the browser. It must remain
read-only and must not imply that Local document bytes are present in the
browser.

## Addendum (2026-08-13)

The authenticated response wiring is now present through the existing
`refreshWorkspace()` flow. The `/workspace/executions` response is retained on
each execution and `renderPassport()` reads `execution.passport` directly.
Synthetic proof packets receive a clearly labeled proof-only Passport so the
fixture remains distinguishable from live authority.

Verification completed:

- Passport and browser contract tests: `5 passed`.
- Topology and landing regression tests: `8 passed`.
- `node --check web/cloud_workspace/app.js` passed.
- Local browser runtime: one main landmark, no horizontal overflow, no console
  errors, and visible boundary, source, status, and recovery fields in the
  proof flow. Evidence tier: Tier 4 for presentation behavior.
- Authenticated backend API execution remains unverified. The current system
  interpreter lacks SQLAlchemy, so the dependency-complete workspace route
  suite still needs to run in the project backend environment before Tier 3
  API evidence is claimed.

Next product unit: dependency-complete API contract proof and then a live
authenticated browser fetch using the existing workspace account flow. No
document bytes, local file paths, sync, deployment, or commit work is part of
that unit.

## Addendum (2026-08-13, API proof completed)

The dependency-complete proof and authenticated browser fetch are now closed.

Verification:

- Workspace service tests: `8 passed`.
- Workspace router tests: `7 passed` after hardening the document-inspection
  receipt ID to serialize UUIDs as strings.
- Full focused CDO/backend suite: `47 passed`.
- Browser authenticated fetch returned HTTP `200` with a Passport containing
  version `1.0`, `cloud` topology, `workspace_control_plane` authority,
  `pending_review` then `awaiting_participant` state, and one then two evidence
  receipts after the existing reviewer-approval action.
- The response exposed no `document_bytes`, `input_path_ref`, or
  `output_path_ref` keys. The `data_boundary` value explicitly remained
  `metadata_only_no_document_bytes`.
- Browser runtime showed the same Passport status and boundary with no console
  errors, no horizontal overflow, and one main landmark.

Evidence tiers:

- Tier 2: focused tests, including the red-to-green UUID receipt regression.
- Tier 3: dependency-complete service/router/API contract execution.
- Tier 4: authenticated browser creation, fetch, state transition, and UI
  rendering.

Runtime artifact note: one synthetic local workspace account and one metadata
execution were created for this proof. No document was uploaded or retained.

The next product unit is now not another Passport wiring task. It is the next
customer workflow slice: make the browser's metadata record explain the
handoff to the Local desktop boundary without implying that the browser can
inspect, sign, or store the document.
