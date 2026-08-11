# Decision: topology-aware browser workspace foundation

**Date:** 2026-07-31  
**Status:** Accepted direction. First implementation stage built locally; no hosted service is released.  
**Owner:** Product owner  
**Evidence level:** Tier 3 local integration and Tier 4 browser-observed workflow. No hosted or production evidence exists.

## Context

The accepted 2026-07-16 local-first decision correctly rejected becoming a generic,
cloud-first envelope competitor. The newer product direction adds a separate need:
people may choose a complete local app, a complete browser-native Cloud product, or a
Hybrid product with explicit synchronization. Treating that requirement as a desktop
feature flag would create a dependency on local installation and leave Cloud buyers
with no coherent product.

This record supersedes only the earlier rejection of every Cloud workflow surface. It
does not supersede local-first trust, privacy, controlled workflows, or evidence
requirements in:

- `docs/analysis/2026-07-16_local_first_trust_architecture_decision.md`
- `docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/workflows_module_interfaces.md`
- `docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/template_to_recipe_migration_checklist.md`

## First-principles decision

Build one **topology-aware document-execution product** with one logical workflow
contract and explicit storage/execution topology. Do not build three drifting apps.

| Topology | Customer promise | Current implementation state |
| --- | --- | --- |
| Local | Complete desktop workflow with no sync | Existing primary product direction; not modified by this build. |
| Cloud | Complete browser workflow without a desktop dependency | The protected workspace control plane begins this path. Hosting, document storage, delivery, and signing remain unbuilt. |
| Hybrid | Local processing plus explicit, consented synchronization | Contract is reserved. Sync is not enabled or implied. |

The shared object is a versioned workflow execution: a template lineage, roles,
state transitions, minimal operational metadata, and a chronological receipt. A PDF,
signature asset, signing ceremony, external delivery, provider callback, and legal
assertion are separate capabilities that must attach to this contract through one
canonical pipeline when they are designed.

## What this implementation adds

- `backend/app/services/workspace.py`: code-owned, versioned HR Onboarding Core
  template catalog and fail-closed transition map.
- `backend/app/models/workspace.py`: owner-scoped execution and ordered event receipt
  persistence with no document/blob columns.
- `backend/app/routers/workspace.py`: one authenticated `/workspace` API for template
  discovery, owner-only execution reads/creates, and transitions.
- `web/cloud_workspace/`: separate browser-native app mounted at `/workspace-app`, not
  mixed into historical landing-page assets.
- `backend/alembic/versions/ca3107e4a9f1_add_workspace_control_plane.py`: durable
  production migration path, even though local `Base.metadata.create_all` remains a
  development compatibility behavior.

## Boundary and privacy design

The workspace stores only the data needed to operate its current workflow register:
participant name/email, reviewer name/email, effective date, operator note, template
version, current state, and owner-entered event receipt. It intentionally does not
store documents, extracted signature files, signer biometric data, signing intent,
identity proof, transmission evidence, or a completion certificate.

The UI names these actions "record" rather than "approve" or "sign" in a way that
would imply independent identity or legal verification. The current desktop privacy
policy remains accurate for the desktop local product and has not been reworded as a
Cloud policy. A hosted release needs a separate data map, retention schedule, data
subject rights mechanism, incident process, legal review, and customer-facing Cloud
privacy terms before any production claim.

## Why the initial HR template

HR onboarding has repeatable roles, controlled packet handoff, and a clear need to
make responsibility visible. This lets us test a vertical configuration without
forking a separate HR product or placing sensitive documents into the first web slice.
The template catalog is code-owned and versioned so every execution retains a stable
lineage while a later authoring system is designed.

## Alternatives considered

| Option | Outcome |
| --- | --- |
| Put a Cloud tab in the desktop app | Rejected. It cannot serve Cloud-only buyers and makes topology an accidental client feature. |
| Build a generic PDF uploader/signing route first | Rejected. It would create sensitive storage and legal/trust obligations before the control, evidence, and privacy pipeline exists. |
| Reuse historical landing assets as the app | Rejected. Those assets are marketing variants with stale pricing and checkout assumptions, not a protected product surface. |
| Build independent Local, Cloud, and Hybrid workflow models | Rejected. This creates contract drift and makes future sync unsafe. |

## Technical invariants

1. The `/workspace` router is the sole backend route family for workspace execution.
2. All reads and writes are scoped to the authenticated owner.
3. Each event has a unique sequence per execution and never contains document or
   signature payloads.
4. Terminal states fail closed. A completed or cancelled execution cannot advance.
5. A template code and version are copied to the execution at creation.
6. No browser action claims document transmission, approval authentication, signature,
   certificate, or legal completion.

## Next stages and gates

1. Add membership/participant authorization, workspaces, and explicit role claims
   before unassisted external actor actions.
2. Design a document-set and evidence-event contract, including retention/deletion,
   encryption, content integrity, and no-raw-path rules, before document upload.
3. Add a provider adapter and webhook verification only after a canonical signing
   ceremony state machine, retries, idempotency, and provider sandbox tests exist.
4. Define the Local/Cloud/Hybrid capability matrix and explicit sync consent model
   before Hybrid implementation.
5. Run target-user interviews and paid pilots. Revisit the Cloud path if users only
   want a commodity e-signature suite and do not value topology choice or the visible
   operational register.

## Rollback

The app mount and `/workspace` router can be disabled together without touching local
desktop processing. The migration downgrade removes its two tables in dependency
order. Any production rollback must export the workflow register under the future
retention and customer-notice policy; no such hosted operations process exists yet.

## Three-pass build review plan

### Pass 1: immediate correctness

Confirm catalog validation, transition legality, owner scoping, response schema, and
the UI’s create/select/advance workflow.

**Outcome (2026-07-31):** Passed. `backend/tests/test_workspace_service.py` covers
the versioned catalog, successful path, rejected terminal replay, and unknown-template
failure. Browser execution created a user and a real API-backed HR execution.

### Pass 2: architecture and long-term viability

Confirm no duplicate route or shadow workflow source exists; verify that the template
lineage, event order, topology field, and migration form one canonical path.

**Outcome (2026-07-31):** Passed with one legacy repair. Fresh Alembic execution
revealed that `fe07219460da_initial_migration.py` was a no-op, making the following
user migration impossible on a new database. Its bootstrap now idempotently creates
the existing base `users`, `images`, and `pdf_audit_logs` tables. A fresh SQLite run
then applied every revision through `ca3107e4a9f1`, including
`workspace_executions` and `workspace_execution_events`.

### Pass 3: supervision readiness

Confirm docs distinguish local integration proof from hosted Cloud claims, test output
is recorded, visual browser evidence is captured, and remaining security/privacy
gates remain explicit.

**Outcome (2026-07-31):** Passed for local development evidence. Playwright browser
control registered a new user, created an HR execution, recorded reviewer approval,
recorded participant confirmation, and observed the completed state with a three-event
receipt. Desktop (`1200px`) and mobile (`390px`) layouts were inspected, and the final
browser console had zero errors or warnings. The requested Computer plugin did not
expose a direct callable desktop-control tool in this session; the installed Playwright
browser-control surface was used instead.

## Verification record

| Check | Result | Evidence tier |
| --- | --- | --- |
| `JWT_SECRET=... DATABASE_URL=sqlite:///:memory: .venv/bin/python -m pytest backend/tests/test_workspace_service.py -q` | `3 passed` | Tier 2 |
| `PYTHONPATH=.. ... ../.venv/bin/alembic -c alembic.ini upgrade head` on a fresh SQLite database | Reached `ca3107e4a9f1`; base and workspace tables present | Tier 3 |
| Browser route `http://127.0.0.1:8765/workspace-app/` with isolated SQLite database | Register, create, record review, record confirmation, receipt observed | Tier 4 |
| Playwright desktop and mobile checks | Full-page screenshots captured for completed `1200px` and `390px` states; final console clean | Tier 4 |

The local visual server used an isolated `/tmp` SQLite database and was stopped after
the test. No production configuration, hosted deployment, external email delivery,
document upload, sync, provider integration, checkout, or desktop-local behavior was
changed or validated by this build.
