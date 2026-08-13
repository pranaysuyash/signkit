# SignKit ContractDesk web expansion tracker and working plan

Date: 2026-08-12
Owner: Pranay
Spec source: [SIGNKIT_CONTRACTDESK_WEB_EXPANSION_AGENT_SPEC_2026-08-12.md](./SIGNKIT_CONTRACTDESK_WEB_EXPANSION_AGENT_SPEC_2026-08-12.md)

Status: active

## 0) Working model and tracking rule

- `DONE` means implemented, documented, and evidence-backed.
- `IN_PROGRESS` means actively being worked and partially complete.
- `BLOCKED` means waiting for external evidence or a decision.
- `ADDED` in each line marks new inferred tasks not explicitly listed in the spec.
- Every claim in this file is labelled with source evidence or marked `UNKNOWN` when inferred.

## 1) Required output from the spec (tracked)

| Task ID | Type | Scope | Owner | Status | Evidence / notes |
| --- | --- | --- | --- | --- | --- |
| TASK-0A | explicit | Create dated expansion report under `docs/expansion` | workflow agent | DONE | New file created: this tracker contains verified capabilities, inferred/missing items, risks, proof slice, and kill criteria. |
| TASK-0B | explicit | Separate verified/inferred/unknown findings | workflow agent | DONE | Verified evidence references are included in section 3 below. Unknowns are tagged with `UNKNOWN` status lines. |
| TASK-0C | explicit | Map explicit launch boundary and no-go claims | workflow agent | DONE | Claim registry alignment in `docs/launch_claims/registry.md` and `tests/test_launch_claim_registry.py`; root page markers observed in `index.html`. |
| TASK-0D | explicit | Add explicit and inferred TODOs for Stage 0-3 | workflow agent | DONE | Task registry below contains explicit/implicit labels and dependencies. |
| TASK-0E | explicit | Evaluate API-as-product topology for Stage 1 and document recommendation for local vs hosted web/API option. | workflow agent | DONE | Decision stored in `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_API_PRODUCT_STRATEGY_2026-08-12.md`. |
| TASK-0F | explicit | Publish API-product topology addendum (local-control-plane scope + hosted-API preconditions) and wire to sales/roadmap docs. | workflow agent | DONE | Addendum is created and `docs/sales/SIGNKIT_SALES_EXECUTION_BRIEF_2026-08-12.md` now includes API boundary section. |
| TASK-0G | explicit | Close dependency blockers that block targeted workspace transition verification. | workflow agent | DONE | `.venv/bin/pytest backend/tests/test_workspace_service.py -q` passes (10 passed). Missing dependency symptoms were from running tests in global Python. |

## 2) Stage 0: evidence and feasibility (actively updated)

### 2.1 Verified capabilities (Tier 1 static + Tier 2 tests)

- Desktop extraction and signature cleanup pipeline exists and is API-exposed at `backend/app/routers/extraction.py` (upload, region selection, image processing). Evidence: route handlers and tests in `backend/tests`.
- Workspace control plane exists in backend and web shell under `/workspace-app` with auth-required API in `backend/app/routers/workspace.py`.
- Workflow state model now includes ContractDesk synthetic states and transitions. Evidence: `backend/app/schemas/workspace.py` and `backend/app/services/workspace.py`.
- Control-plane records metadata and event lineage only (no PDF/signature payload retention). Evidence: `backend/app/models/workspace.py` docstring + fields.
- Root landing page is the launch claim source of truth with 12 registered claim markers. Evidence: `index.html` markers and `tests/test_launch_claim_registry.py`.
- Checkout boundary is config-driven and currently publishes fallback-first when Dodo is unset. Evidence: `web/live/js/checkout-config.js`, `web/live/js/checkout.js`.
- Existing desktop demo runner is importable after the B-1 syntax repair. The web proof now has its own deterministic launch/probe command in `tools/run_contractdesk_web_proof.py`.
- Workspace web surface is proof-oriented and intentionally metadata-only. Evidence: `web/cloud_workspace/index.html` + `web/cloud_workspace/app.js`.
- ContractDesk synthetic transition proof is covered by route-level smoke path test (`backend/tests/test_workspace_router.py::test_contractdesk_proof_slice_smoke_path`) and fixture manifest file (`web/cloud_workspace/proof-fixtures.json`).

### 2.2 Inferred or reusable capability candidates (Tier 0/1)

- Existing workspace execution API can likely host an explicit ContractDesk synthetic transition layer by extending enums and adding explicit transition actions, but this is not yet implemented.
- The root claim registry can be preserved as canonical even while a new web proof slice is added, if no new public claim IDs are introduced.
- Desktop extraction fixtures and PDF pipeline can be reused for synthetic proof workflows once deterministic fixture inputs are formalized.

### 2.3 Missing capabilities and explicit blockers

- API caller-level duplicate-replay coverage is now present at route level (`backend/tests/test_workspace_router.py`).
- Exception/retry handling in web control-plane UI for ContractDesk states is now implemented in `web/cloud_workspace/app.js` via status actions and recovery guidance (`C-2`).
- Fresh-context browser evidence covers the mounted synthetic proof manifest export path; local certificate-backed signed artifact production is now implemented in the desktop/PDF lane, while hosted integration remains a separate gate.
- A combined Qt/PDF UI regression invocation once hit a native `pypdfium2` segmentation fault during field-detection teardown. The application-level serialization and explicit-close fix is now implemented; five guarded combined fresh-process runs passed, while process isolation remains the escalation if a native crash recurs.
- Demo runner is currently not executable due syntax/runtime import fragility (syntax + dependency expectations).

### 2.4 Architectural conflicts / duplicate paths

- No duplicate route file for workspace is observed; the canonical route is `backend/app/routers/workspace.py`.
- There is a clear boundary risk: marketing web and control-plane web are separate surfaces.
  - Marketing: root `index.html` and `web/live`.
  - Control plane: `web/cloud_workspace` with `workspace-app` mount in backend.
  - This can be healthy, but the staged plan must explicitly prevent claim conflation.

### 2.5 Security/legal/ops risks

- Existing launch claims are controlled by registry and tests; any new ContractDesk proof claims must not exceed existing tested statements.
- Stage 1 proof must not imply regulated signing.
- The control plane currently stores personal contact details and notes in workflow records; data handling scope should be explicit.

### 2.6 Stage 0 acceptance evidence path

- `tests/test_launch_claim_registry.py` (claim marker + wording integrity).
- `backend/tests/test_workspace_router.py -k contractdesk_proof_slice_smoke_path` for deterministic API replay verification.
- Static inspection of backend web/control-plane routes, schema, and DB models.
- `tools/run_contractdesk_web_proof.py --keep-running` followed by a fresh browser context for repeatable local proof capture.

## 3) Parallel work lanes and task register

### 3.1 Product/architecture lane

| Task ID | Type | Owner | Status | Description | Dependency |
| --- | --- | --- | --- | --- | --- |
| A-1 | implicit | Product/Workflow | DONE | Selected Stage 1 topology for proof as **local-companion control-plane API extension** with no hosted-signing parity claim. | TASK-0D |
| A-2 | explicit | Architecture | DONE | Added canonical `intake -> normalize -> extract -> complete -> state transition -> review/exception -> export -> audit receipt` mapping across local desktop and `/workspace` API tiers in the new topology addendum. | A-1 |
| A-3 | explicit | Product/Legal | DONE | Confirmed launch-safe API-product claims alignment against `docs/launch_claims/registry.md` for Stage 1 API scope. | A-2 |
| A-4 | explicit | Product/Legal | DONE | Defined the hosted API acceptance matrix and pilot entry criteria in `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_HOSTED_API_ACCEPTANCE_GATE_2026-08-12.md`; hosted API remains deferred until all gates have evidence. | A-3 |

### 3.2 Backend/runtime lane

| Task ID | Type | Owner | Status | Description | Dependency |
| --- | --- | --- | --- | --- | --- |
| B-1 | explicit | Implementation | DONE | Fix `tools/demo_runner.py` syntax blocker so the existing demo runner is importable and executable by CI/manual flow. | --- |
| B-2 | explicit | Implementation | DONE | Added a backend proof smoke test covering deterministic synthetic path events (`received -> ready_for_review -> needs_correction -> ready_for_review -> approved -> signed -> exported`) with replay check in `backend/tests/test_workspace_router.py:67` and status/event assertions on each transition. | A-2 |
| B-3 | explicit | Implementation | DONE | Added synthetic ContractDesk states/actions plus transition coverage in `backend/app/schemas/workspace.py` and `backend/app/services/workspace.py`; service-level replay tests now include duplication checks in `backend/tests/test_workspace_service.py`. Verified in `.venv` (`10 passed`). | A-2 |
| B-4 | explicit | QA/Runtime | DONE | Captured deterministic proof artifact manifest in `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_IDEMPOTENCY_PROOF_MANIFEST_2026-08-12.md` with input hashes, output paths, timestamp, and pass/fail. | B-1 |
| B-5 | explicit | Implementation | ADDED | Extend transition domain for contract states only after hosted API preconditions are explicit and backward-compatible migration plan is approved. | A-4 |
| B-6 | explicit | API/Operations | DONE | Runtime idempotency implementation is complete in `backend/app/services/workspace.py`, `backend/app/models/workspace.py`, `backend/app/routers/workspace.py`, and migration `backend/alembic/versions/d8a6c2f1b4a3_add_workspace_event_idem_key.py`. Verified in `.venv` (`.venv/bin/pytest backend/tests/test_workspace_service.py -q`, 10 passed). | B-3 |
| B-7 | explicit | QA/Runtime | DONE | Define reproducible backend test execution contract as: use repository `.venv` interpreter (`.venv/bin/pytest ...`) for backend transition/runtime tests until a shared command helper is added. | B-3 |
| B-8 | explicit | API/Operations | DONE | Added runtime-focused route tests for idempotent transition replay and 409 behavior in `backend/tests/test_workspace_router.py` using FastAPI TestClient and seeded auth/db fixtures. | B-6 |
| B-9 | explicit | QA/Runtime | DONE | Added negative owner-scope idempotency regression for actor-local replay scope: same actor replay is idempotent, while the same `idem_key` can still be reused on actor-owned executions as documented. Evidence: `backend/tests/test_workspace_service.py::test_transition_idem_key_lookup_is_scoped_to_actor_not_global`. | B-8 |
| B-10 | explicit | QA/Runtime | DONE | Added `tools/package_contractdesk_proof.py` and `tests/test_contractdesk_proof_tools.py` for atomic, content-addressed synthetic manifest and receipt packaging with explicit `synthetic=true` and `signature_status=not_signed`. | B-4 |
| B-11 | explicit | Desktop/PDF/API | DONE | Implemented the local `ArtifactReceipt` integrity contract plus explicit certificate-backed PAdES signing in `desktop_app/pdf/digital_signer.py`, with PKCS#12 loading, fail-closed verification, signed-revision tamper detection, certificate fingerprinting, atomic output promotion, and cryptographic receipt semantics. Evidence: `desktop_app/tests/test_digital_signer.py`, `tests/test_artifact_receipt.py`, and `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_SIGNED_ARTIFACT_CONTRACT_2026-08-12.md`. | A-4, B-10 |
| B-12 | explicit | Security/Legal/Operations | IN PROGRESS | Hardened configured trust-root enforcement, fail-closed output promotion, and operator-visible validity/integrity/trust failure reasons. B-13 UI/export integration is complete; remaining scope is signer identity and key custody, public/enterprise trust-chain and revocation policy, timestamping/LTV where required, retention/recovery, legal claim review, and Tier 3 production-like artifact evidence before any hosted claim. | A-4, B-11 |
| B-13 | explicit | Desktop/UI | DONE | Added `desktop_app.workflows.engine.export_pdf_artifact` as the single explicit visual-versus-certificate dispatch seam and routed `PdfTabMixin.on_pdf_save` through it. The UI keeps visual placement as the default, labels it non-cryptographic, and requires a PKCS#12 path plus passphrase for certificate-backed PAdES mode. Evidence: 11 workflow-screen tests, 6 PDF field/UI tests, 7 combined export/signing tests, and compilation passed in `.venv`. | B-11, B-12 |
| B-14 | explicit | Security/Operations | IN PROGRESS | Added `desktop_app/pdf/credentials.py` with a credential-provider protocol, redacted PKCS#12 compatibility provider, macOS Keychain generic-password adapter, fixed argument-list invocation, timeout, secret-safe errors, and optional signer-subject authorization enforced before output promotion. Remaining scope: rotation/revocation runbook, hardware/remote key custody decision, and recovery drill. Closure: provider contract, negative secret-handling tests, and recovery drill. | B-12 |
| B-15 | explicit | PDF/Security | IN PROGRESS | Added explicit timestamp-provider configuration to the certificate signer: `timestamp_url` creates an HTTP timestamp provider, `timestamper` supports injected providers, ambiguous sources are rejected, and baseline signing remains network-free by default. Remaining scope: RFC 3161 TSA configuration, revocation material, DSS/VRI embedding, long-term validation retention, and profile-specific Tier 3 evidence. | B-12, B-14 |
| B-16 | explicit | Legal/Product/API | ADDED | Convert certificate-backed signing into a truthful hosted/product claim with jurisdiction, signer identity, trust model, retention, support, and responsibility explicitly documented. Closure: approved claim registry entry, API contract, operator runbook, and production-like artifact acceptance. | B-13, B-14, B-15 |
| B-17 | explicit | Desktop/PDF Runtime | DONE | Resolved the Qt/PDFium native-race boundary with process-wide PDFium serialization, explicit document close across renderer, detector, and legacy engine, and concurrent lifecycle regression coverage. Evidence: `desktop_app/tests/test_pdfium_runtime.py`, 5 repeated guarded combined runs with 19 tests each, 33 PDF/runtime tests, and the incident review `docs/issue_review_pdfium_qt_native_crash_2026-08-12.md`. | B-12, B-13 |
| B-18 | implicit | Desktop/PDF Runtime | DONE for local-companion profile | Integrated the reusable isolated PDFium worker into the canonical local-companion `/workspace/executions/{id}/document-inspections` route. The route is registered only by `SIGNKIT_RUNTIME_PROFILE=local_companion`; the hosted profile does not register it. It bounds input, rejects non-local execution metadata before reading bytes, validates with pikepdf, executes field inspection in a disposable PDFium process, stores only hash/result metadata, deletes temporary bytes, and reconciles idempotent replay/conflict. Browser control-plane proof passes; authenticated browser upload and reload recovery remain separate gates. | B-17, A-1 |
| B-21 | implicit | Security/Runtime | DONE | Made locality a server capability and added per-instance HMAC health proof verification so the desktop manager rejects a generic loopback `200 /health` impostor. This is process identity and route-exposure control, not an OS sandbox. | B-18 |
| B-22 | implicit | Evidence/Contracts | IN PROGRESS | Reconcile ADR-0143, topology addendum, browser proof, and hosted acceptance language so local route evidence, hosted readiness, signing, and synthetic control-plane evidence remain separate. | B-18, B-20, B-21 |
| B-23 | implicit | Desktop Privacy/API | DONE for default boundary | Remote document uploads are blocked by default in `desktop_app/api/client.py`; explicit connected mode is required to send document bytes to a non-loopback API. Loopback companion uploads remain available. | B-18, B-20 |
| B-24 | implicit | QA/Test Sensitivity | DONE | Extended the curated S3 gate to hosted route exclusion and bounded candidate output. After authorized Playwright-cache-only storage recovery, `TMPDIR=/var/tmp .venv/bin/python tools/mutation_check.py` passed with `7/7 mutants killed`; every source was restored. | B-21, B-22, B-23 |
| B-19 | implicit | Desktop/PDF Runtime | DONE | Evaluated qpdf preflight, PDF.js, MuPDF/PyMuPDF, persistent workers, process pools, and dual-engine fallback. Bound PDFium as canonical processing, disposable workers as the isolation seam, PDF.js as preview-only, and qpdf as an optional structural preflight. Decision record: `docs/research/pdf_document_runtime_options_2026-08-12.md`; adapter/tests: `desktop_app/pdf/preflight.py`, `desktop_app/tests/test_pdf_preflight.py`. | B-17, B-18 |
| B-20 | implicit | Hosted API | ADDED | Keep hosted/cloud document execution gated. Closure requires tenant/auth boundary, retention/deletion/recovery, structured API errors, rate limits, observability, production artifact custody, legal review, and Tier 3+ deployment evidence. The local-companion route is not hosted API proof. | A-4, B-18 |

### 3.3 Web lane

| Task ID | Type | Owner | Status | Description | Dependency |
| --- | --- | --- | --- | --- | --- |
| C-1 | explicit | Frontend | DONE | Documented current proof-capable web control plane and required delta for human review + exception visibility in previous pass (`web/cloud_workspace/app.js`). | A-2 |
| C-2 | explicit | Frontend | DONE | Added status-aware ContractDesk action lanes and recovery guidance in execution passport for `needs_correction`, `exception`, and related synthetic states. | C-1 |
| C-3 | explicit | Frontend | DONE | Added deterministic synthetic ContractDesk fixture seed + manifest display in `/workspace-app` with one-click load in `web/cloud_workspace/app.js` and `web/cloud_workspace/index.html`; added manifest card in execution passport and synthetic replay-safe transition behavior. | C-2 |
| C-4 | explicit | Frontend | DONE | Added explicit topology labeling in operator UI (`local-control-plane`, `local-companion` context, hosted-API boundary note) to keep operator context accurate against scope claims. | C-2 |
| C-5 | explicit | QA/Frontend | DONE | Completed fresh-context browser proof against the canonical SignKit backend mount, including auth, fixture load, all synthetic ContractDesk state transitions, manifest/export receipt, and readable invalid-input handling. Evidence: `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_RUNTIME_PROOF_2026-08-12.md`. | C-3 |
| C-6 | implicit | QA/Operations | DONE | Added `tools/run_contractdesk_web_proof.py` with deterministic port `8871`, health/mount/asset/fixture checks, clean shutdown, and `--keep-running` browser handoff. Fresh-context browser proof completed with no console errors. | C-5 |

### 3.4 Sales/Delivery lane

| Task ID | Type | Owner | Status | Description | Dependency |
| --- | --- | --- | --- | --- | --- |
| D-1 | explicit | Sales/Docs | DONE | Refresh one-page discovery proposal path for ContractDesk and map “implemented vs proposed” boundaries. | B-2 |
| D-3 | explicit | Sales/Docs | DONE | Added API boundary section to ContractDesk discovery brief and linked strategy/addendum/tracker evidence. | A-1 |
| D-2 | explicit | Sales/Docs | DONE | Reviewed the public surface and claim registry condition; no benchmark or social-proof placeholder requiring replacement was found, so no customer-facing claim change was made. | D-1 |
| D-4 | explicit | Sales/Docs | DONE | Completed implemented/proposed handoff in `docs/sales/SIGNKIT_SALES_EXECUTION_BRIEF_2026-08-12.md` and tied API topology choice (local-control-plane now, hosted API later) to acceptance gates. | D-3 |

## 4) Stage 1 minimum proof slice (first bounded deliverable)

1. Intake one synthetic contract packet. ✅ (already via control-plane creation path)
2. Run at least one completion operation via canonical extraction pipeline. ✅ implemented for synthetic control-plane states (`mark_received -> request_review -> request_correction -> request_review -> approve -> sign -> export`) via proof fixture and route smoke test; desktop extraction execution remains pending by design.
3. Show explicit state display and audit receipt in control plane. ✅ (fresh-context browser proof observed the state sequence and receipt trail)
4. Add exception + retry path for `needs_correction` and recovery. ✅ implemented in control-plane passport actions with guided operators (exception/retry actions and inline recovery copy).
5. Add audit manifest linking input, decision, output. ✅ implemented via deterministic manifest JSON in `web/cloud_workspace/proof-fixtures.json` and passport display; backend event-level receipt remains metadata-first in this lane.

Confidence for this stage is not reported as one aggregate number. Current
per-capability evidence is: metadata control-plane browser proof **Tier 3**;
local-companion route-to-worker-to-receipt **Tier 3**; hosted document API
**OPEN**; authenticated browser upload/reload recovery **OPEN**; production
trust and signing custody **OPEN**.

## 5) Stage 0 decision gate (current hold/continue checks)

- Canonical processing engine for proof slice is confirmed for metadata control-plane and desktop extraction/PDF; full deterministic web proof path is now observed through the mounted backend, including UI state transitions and manifest export.
- Document boundary explicitness: controlled via root claim markers and `local_processing_boundary` language.
- State transitions auditable: yes for implemented synthetic and existing metadata states; no external/public API contract yet.
- Human review and recovery: partially confirmed as metadata review only.
- Browser proof requiring duplicative extraction/signing: no; control plane is distinct and metadata-first, which is consistent with rule against second signing engine.
- Local artifact integrity: yes for the typed `ArtifactReceipt` contract and existing PDF producer regression checks; local cryptographic signing and signed-revision verification are also covered by targeted tests.
- Synthetic artifact packaging, the repository-local proof runner, the local artifact receipt contract, and the local PKCS#12/PAdES signing path are complete; production trust, custody, hosted integration, and legal-operational readiness remain tracked as B-12 with explicit gates.
- Paid slice scope: still to be finalized after A-2 and B-3.

## 6) Add-to-task policy

- New tasks should be added to the lane table with `ADDED` once evidence surfaces (example: security/legal review task for synthetic manifests, fixture governance task, operator recovery task).
- Every added task must include dependency, owner, and failure condition.

## 7) Evidence matrix for this tracker

| Area | Evidence tier | What confirms it |
| --- | --- | --- |
| Control-plane metadata model | 1 | `backend/app/models/workspace.py` docstring and schema fields |
| Launch claim boundary | 2/3 | `docs/launch_claims/registry.md`, `tests/test_launch_claim_registry.py`, `index.html` markers |
| Checkout state handling | 1/2 | `web/live/js/checkout-config.js`, `web/live/js/checkout.js` |
| Demo runner baseline status | 0 | `tools/demo_runner.py` syntax + import path |
| End-to-end proof evidence | 4 | Fresh-context browser replay against backend `8001` covered auth, fixture load, state sequence, six-event receipt trail, and synthetic manifest export; local signed-output verification is covered separately in the desktop/PDF test lane. |
| Reproducible runner and synthetic package | 2/4 | `tools/run_contractdesk_web_proof.py` passed health/mount/asset/fixture checks on deterministic port `8871`; package output is recorded in `docs/expansion/artifacts/contractdesk_stage1_synthetic_receipt`. |
| Local artifact and signing contract | 2 | `.venv` evidence: credential/provider and digital/trust tests passed 9, export-mode tests passed 3, receipt tests passed 3, existing PDF signing tests passed 3 selected, focused PDF integration passed 1, workflow-screen tests passed 11, PDF field/UI tests passed 6, compilation passed, and `pip check` reported no broken requirements. |
| Local-companion PDF inspection | 3 | `backend/tests/test_workspace_router.py::test_local_document_inspection_is_isolated_replay_safe_and_cloud_rejected` drives the authenticated route, actual pikepdf validation, disposable PDFium worker, durable event receipt, replay/conflict handling, and cloud rejection; malformed/unkeyed paths are also covered. |

## 8) Acceptance criteria for this tracker pass

- Explicit tasks listed above have status updates and owners.
- No duplicated control-plane route or second signing engine is introduced.
- Stage 1 proof remains metadata-safe and no customer-facing claim inflation is introduced without registry update.
- A follow-up task exists for each non-complete task with owner and dependency before entering Stage 1 execution.

## 8.1 Three-pass continuation notes

- Pass 1, correctness: browser runtime found and fixed wrong asset-root assumptions and unreadable object-shaped API errors; fresh-context proof then passed through `EXPORTED`.
- Pass 2, architecture: proof stayed on the existing `/workspace-app`, `/auth`, and `/workspace` canonical paths; no duplicate route or parallel signing pipeline was added.
- Pass 3, supervision: runtime evidence, static checks, deterministic runner, synthetic package hashes, local receipt semantics, certificate-backed signing evidence, environment limitations, and B-12 closure criteria are recorded in the expansion docs; synthetic export and embedded-signer trust remain explicitly non-production claims.

## Addendum (2026-08-13): local-companion PDF worker integration

The user asked to continue and questioned why the PDF worker evidence was not
Tier 3. The distinction is now bound in code and evidence:

- The previous worker tests were Tier 2 because they called the worker boundary
  directly.
- The new local-companion route test reaches the authenticated workspace route,
  validates the uploaded PDF, invokes the real disposable PDFium child process,
  persists a metadata-only event receipt, replays the stored result, rejects a
  conflicting idempotency reuse, and rejects cloud topology. That is Tier 3
  integration evidence for this local path.
- It does not prove hosted/API production readiness. Hosted document bytes,
  tenant operations, deployment isolation, retention/recovery, legal claims,
  and production artifact custody remain B-20 gates.

## Addendum: boundary and evidence reconciliation (2026-08-13)

- The local document route is a local-companion runtime capability, not a
  request-controlled locality claim. Hosted profile route absence is covered by
  `backend/tests/test_runtime_profile.py`.
- Desktop loopback identity is strengthened by an HMAC health proof and an
  impostor rejection test in `desktop_app/tests/test_backend_manager.py`.
- The current browser proof uses system Chrome against the canonical
  keep-running backend surface and verifies the workspace title, local-companion
  boundary, cloud metadata-only boundary, and source-byte deletion wording.
- This is browser control-plane evidence, not authenticated browser file-picker
  upload, receipt rehydration, hosted document execution, or signing proof.
- B-22 remains open until the final route, profile, browser, and hosted gate
  documents have one consistent capability matrix.

Parallel-work reconciliation: the existing `backend/app/services/document_inspection.py`
and workspace route were preserved and hardened. No duplicate `document_jobs`
service or duplicate workspace route was introduced.
