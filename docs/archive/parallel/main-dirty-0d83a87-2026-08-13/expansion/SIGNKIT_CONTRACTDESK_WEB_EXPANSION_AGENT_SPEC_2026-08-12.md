# SignKit web expansion and ContractDesk workflow agent specification

Date: 2026-08-12
Status: Agent handoff for code inspection, architecture planning, and staged proof
Owner: Pranay

## 1. Objective

Inspect the current SignKit repository and produce an evidence-backed plan for a
web expansion that can support the ContractDesk conversation described in
`docs/sales/SIGNKIT_SALES_EXECUTION_BRIEF_2026-08-12.md`.

The expansion must make one contract-document workflow testable across:

1. extraction and cleanup;
2. completion or placement;
3. explicit signing-state transitions;
4. human review and exception handling;
5. audit evidence and export.

The result should support a paid workflow audit or implementation slice. It is not
permission to announce a web product, a cloud CLM, regulated e-signatures, or a
multi-tenant SaaS product before the relevant implementation and legal gates close.

## 2. Required first pass: repository and runtime inspection

Before proposing architecture or editing production code, inspect and document:

### Product and workflow sources

- `PRODUCT.md`
- `DESIGN.md`
- `docs/launch_claims/registry.md`
- `docs/PRICING.md`
- `docs/sales/SALES_OPERATING_SYSTEM.md`
- `docs/sales/SIGNKIT_SALES_EXECUTION_BRIEF_2026-08-12.md`
- `docs/wayfinder/SIGNKIT_WIDE_OPEN_BRAINSTORM_2026-07-31.md`

### Desktop and shared engine

- extraction service and image-processing modules;
- Vault storage and encryption boundaries;
- PDF viewer, coordinate mapping, signer, export, and document-session modules;
- workflow, recipe, grant, review, retry, quarantine, and audit models if present;
- standard and macOS Premium launch profiles;
- current tests and fixtures for each of the above.

### Backend and local services

- backend routes, schemas, database models, migrations, auth, and secret handling;
- local backend startup scripts and the actual API contract;
- upload, storage, retention, deletion, and error paths;
- any existing workspace-control-plane or authorization implementation.

### Web surface and deployment

- root `index.html` and the canonical `web/live/` surface;
- `web/live/js/checkout-config.js` and `web/live/js/checkout.js`;
- all web app or prototype directories, route maps, build scripts, and deployment
  configuration;
- whether a real interactive web workflow exists or whether the web surface is only
  a marketing page;
- current browser tests, analytics, and runtime evidence.

### Existing constraints

Record dirty files and parallel-owned work before editing. Do not overwrite or reset
existing changes. Do not create a second route, signing engine, checkout config,
pipeline, or manually maintained sales tracker.

## 3. Required output of the inspection

Create a dated report under `docs/expansion/` that separates:

- verified current capabilities;
- inferred capabilities or reusable modules;
- missing capabilities;
- architectural conflicts or duplicate paths;
- security, privacy, legal, and operational risks;
- the smallest credible web proof slice;
- the later production expansion path;
- explicit kill criteria.

Every claim must cite a repository file, test, runtime observation, or be labelled as
an inference or unknown.

## 4. Architecture questions the agent must answer

### 4.1 Execution boundary

Compare these options against the live code:

- browser-local processing;
- a user-controlled local desktop companion;
- a hosted processing service;
- a hybrid model where sensitive document processing remains local and only
  workflow metadata or user-approved artifacts cross a boundary.

For each option, specify:

- which files or services would own the canonical pipeline;
- whether the current extraction and PDF engines can be reused;
- upload and retention behavior;
- authentication and authorization needs;
- failure and recovery behavior;
- support and deployment burden;
- what ContractDesk would need to integrate;
- what claims would become legally or operationally unsafe.

Do not choose cloud processing merely because it is easier to demo. Local-first and
privacy boundaries are part of the current product position.

### 4.2 Canonical pipeline

Define one canonical pipeline from input to output:

`intake -> normalize -> extract -> complete -> state transition -> review or exception -> export -> audit receipt`

Map each stage to existing code. If a stage is absent, specify the new module or
extension point without creating a parallel implementation.

### 4.3 ContractDesk workflow contract

Design a synthetic, non-sensitive workflow specimen with these states:

`received`, `needs_correction`, `ready_for_review`, `approved`, `signed`, `exported`, `exception`

For every transition define:

- actor or service;
- input and output schema;
- validation rule;
- audit event;
- retry and idempotency behavior;
- human-review action;
- failure message and operator recovery;
- data retained and deletion behavior.

The specimen must demonstrate where SignKit can provide a local preparation or
evidence component alongside ContractDesk. It must not imply that SignKit is a CLM
or that a placed image signature is regulated, qualified, or universally legally
binding.

## 5. Staged expansion plan to produce

### Stage 0: evidence and feasibility

No product expansion yet. Repair or document the current demo path, run focused
checks, and create a capability matrix for desktop, backend, and web.

Deliverables:

- repository and runtime inventory;
- capability matrix;
- data-boundary diagram;
- current test and environment blockers;
- proposed proof-slice acceptance criteria.

### Stage 1: web proof slice

Build only the smallest interactive slice needed to show the ContractDesk workflow
using synthetic documents. The agent must decide whether the right first surface is
browser-local, local-companion, or a controlled hosted sandbox, and justify it.

The proof slice must include:

- document intake;
- one extraction or completion operation using the canonical engine;
- explicit state display;
- a human-review checkpoint;
- exception and retry behavior;
- an audit receipt or export manifest;
- clear indication of what is synthetic and what is production-ready.

### Stage 2: paid implementation slice

Only after the proof slice is coherent, prepare a ContractDesk-facing implementation
plan for one bounded workflow. Include:

- scope and exclusions;
- integration boundary;
- data-processing and retention terms;
- timeline and milestones;
- acceptance tests;
- operator handoff;
- support and rollback plan;
- customer-funded prerequisites.

### Stage 3: production web expansion

Plan, but do not assume approval for:

- authenticated workspaces;
- tenant isolation;
- role and grant management;
- controlled storage or selective sync;
- production audit exports;
- webhooks and external adapters;
- billing and licence entitlements;
- observability, abuse controls, and incident recovery.

Each item requires its own contract, tests, threat review, and operational owner.

## 6. Verification requirements

For the proof slice, require:

- static import and type checks;
- targeted unit tests for state transitions and schemas;
- integration verification from intake to export;
- manual browser or desktop runtime observation;
- duplicate submission and retry checks;
- invalid or malformed document checks;
- audit-record inspection;
- no sensitive document data in logs;
- clear operator recovery after a failed extraction, export, or review step.

A passing static test alone is not evidence that the web workflow works. State the
evidence tier for every conclusion and list anything that could not be verified.

## 7. Explicit non-goals

Do not build or promise these in the first expansion pass:

- generic cloud document storage;
- a DocuSign or CLM replacement;
- regulated or certificate-backed signing;
- public enterprise pricing;
- broad CRM, ERP, or legal-system integrations;
- autonomous document approval;
- silent cloud upload of customer documents;
- a second extraction or signing engine;
- a second web checkout or sales pipeline.

## 8. Decision gate

The agent must stop after the inspection and proposed Stage 1 plan if any of these
remain unresolved:

- the canonical processing engine is unclear;
- document data would cross a boundary without an explicit product and legal decision;
- state transitions cannot be audited;
- human review and recovery are undefined;
- the web surface would require duplicating the desktop signing pipeline;
- the ContractDesk workflow cannot be demonstrated with synthetic data;
- the proposed work cannot be scoped as a paid implementation slice.

The final report must recommend one path, list alternatives considered, state the
confidence level, and identify the exact next implementation task.
