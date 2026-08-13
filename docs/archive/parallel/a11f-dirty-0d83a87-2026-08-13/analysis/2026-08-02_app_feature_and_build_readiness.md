# SignKit app feature and build readiness contract

Date: 2026-08-02  
Status: implementation contract, not a launch approval  
Scope: live desktop app, local workflow substrate, optional backend and browser workspace foundation, commercial routing, and release build surfaces.

## Decision and release posture

SignKit has a credible local desktop core: signature extraction, encrypted local Vault storage, PDF placement/export, and a controlled local workflow foundation. The current checkout, entitlement, and build evidence does **not** establish a shippable commercial release across macOS, Windows, and Linux. This contract keeps one local-first core and one canonical workspace route family. It does not introduce another signing engine, checkout route, cloud document store, or parallel workflow pipeline.

The next implementation order is:

1. qualify a fresh desktop release bundle and its platform installation path;
2. make purchase, entitlement issuance, revocation, and refund state one verifiable contract before monetized features are offered;
3. harden the local folder-workflow store and monitor before workflow automation is sold or enabled for operational use;
4. treat Cloud workspace as a separately gated metadata-only control plane, not as hosted document signing.

## Evidence legend

| Tier | Meaning used here |
| --- | --- |
| Tier 1 | Current static inspection of the named path. |
| Tier 2 | A fresh focused test passed in this audit. |
| Tier 3 | Integration or end-to-end flow verified. |
| Tier 4 | Manual runtime observation. This document only cites the recorded 2026-07-31 rebuilt macOS run; it was not re-run today. |
| Tier 5 | Production-like or real-provider evidence. None was obtained in this audit. |

## Current implementation map and truth status

| Surface | Current interface and owner | Status | Evidence and boundary |
| --- | --- | --- | --- |
| Desktop launch | `desktop_app/__main__.py` delegates to `desktop_app/run.py`; `desktop_app/main.py` starts `standard`; `desktop_app/main_macos_premium.py` accepts only macOS and starts `mac-premium`. `desktop_app/launch_profile.py` is the profile registry. | Implemented and tested | Tier 2: `tests/test_entrypoints.py`, `tests/test_launch_profile.py`, and `tests/test_build_profile.py` passed in the profile suite below. The profile mapping is not a release artifact. |
| Bootstrap and offline boundary | `desktop_app/app_bootstrap.py` creates `MainWindow`, starts `desktop_app/backend_manager.py` in a daemon thread, and leaves local UI usable when startup fails. `BackendManager` uses a loopback health check and user-writable data directory. | Implemented and tested | Tier 2 profile access tests pass. A new packaged-app launch must still prove that the embedded backend, SQLite fallback, and offline UI work in that bundle. |
| Extraction | `desktop_app/processing/extractor.py::SignatureExtractor` is the local engine. It validates magic bytes, file size, dimensions, and pixels, then supports selection, clean-up, and auto-detection. | Implemented and tested | Tier 2 focused extractor tests pass. Tier 4, recorded in `docs/review/runtime_qa_audit_2026-07-31.md`, proved the supplied sample at `(14,15)-(507,175)` only. It is not a generalized detection benchmark. |
| Vault | `desktop_app/processing/vault.py::NotaryVault` stores encrypted blobs and metadata under `~/.signkit/vault`; `desktop_app/views/vault_tab.py` provides list, preview, and delete UI. | Implemented; focused local workflow coverage exists | Tier 1 current path inspection and Tier 2 workflow tests. No fresh destructive delete/recovery walkthrough was run in this audit. |
| PDF workflow | `desktop_app/views/main_window_parts/pdf.py` owns open, viewer state, placement persistence, audit logging, and save gating. `desktop_app/pdf/viewer.py` renders/places; `desktop_app/pdf/signer.py` uses PyMuPDF first and pikepdf fallback. | Implemented and tested | Tier 2 focused PDF tests pass. The recorded Tier 4 macOS run showed `Page 1 of 6` after opening the demo document. It does not prove every PDF, legal-signature validity, or certificate signing. |
| Local workflow console | `desktop_app/views/main_window_parts/recipe_builder.py`, `grant_manager.py`, and `workflow_console.py` call the canonical `desktop_app/workflows/` model, authorization, monitor, engine, and store modules. | Implemented and tested; not public-workflow-launch ready | Tier 2 focused engine, folder-monitor, and screen-smoke tests pass. Tier 4 recorded runtime evidence is empty-state UI only. A populated operator UI run is still open. |
| Local workflow data and controls | `desktop_app/workflows/store.py` persists recipes, grants, jobs, and events in one JSON file at `~/.signature_extractor/workflow_store.json`; `authorization.py` checks recipe/version, subject, asset, folder, expiry, and quota; `engine.py` creates state events and retry/review outcomes. | Foundation implemented; high-risk hardening incomplete | Tier 1: JSON replacement is atomic per write, but job state and event writes are separate, no inter-process lock exists, and scan deduplication only checks `queued` jobs in `folder_monitor.py`. Do not call this a multi-operator or unattended-workflow release. |
| Browser workspace | `backend/app/main.py` mounts one authenticated `/workspace` route family and `/workspace-app`; `backend/app/routers/workspace.py`, `models/workspace.py`, `schemas/workspace.py`, and `services/workspace.py` own the contract. | Metadata-only foundation implemented and tested | Tier 2: `backend/tests/test_workspace_service.py` is in the focused suite. It stores owner-scoped metadata and event receipts, not documents, signature assets, signing consent, identity proof, or legal completion. No hosted runtime evidence was obtained in this audit. |
| Checkout routing | `desktop_app/config.py::get_purchase_url` resolves a valid Dodo product identifier or Gumroad fallback. `web/live/js/checkout-config.js` is the public configuration owner, and `web/live/js/checkout.js` changes only link state and intent analytics. | Routing shape implemented and tested; fulfilment absent | Tier 2 checkout and claim tests pass. Tier 1 search found no provider webhook, verified order, receipt-to-license issuance, revocation, or refund synchronization implementation under `backend/` or `desktop_app/`. Empty `dodoProductId` is current public configuration. |
| License enforcement | `desktop_app/license/storage.py` stores a local JSON license and grants feature flags; UI gates are in `desktop_app/license/restrictions.py` and `desktop_app/views/license_restriction_dialog.py`. | Development-grade local gate, not production entitlement | Tier 1: non-test keys with length at least six are treated as valid, and `app_bootstrap.py::_resolve_workflow_access` enables workflow access for the mac-premium profile without a verified receipt. This cannot support a customer payment, access-control, or refund claim. |
| Build profiles | `build-tools/build.py` maps `standard` to macOS, Windows, and Linux specs and maps `mac-premium` only to `build-tools/SignatureExtractor_macOS_Premium.spec`. CI definitions are in `.github/workflows/build-all-platforms.yml` and `build-macos.yml`. | Build definitions implemented and tested; artifacts not currently proven | Tier 2 profile mapping tests pass. Tier 1 inspection found no `dist/` directory or current macOS bundle. A historical `SignKit-Windows/SignKit_Windows.zip` exists, dated 2025-11-15 and containing one executable, but it was not rebuilt, signed, installed, or run in this audit. No current Linux artifact exists. |

## Platform build reality

| Platform | Current build contract | Actual evidence now | Required release proof |
| --- | --- | --- | --- |
| macOS Apple Silicon Premium | `build-tools/SignatureExtractor_macOS_Premium.spec` packages `desktop_app/main_macos_premium.py` as `work.signkit.premium.app`; `build-tools/build_macos.sh premium` is the supported local wrapper. | Tier 4 historical rebuilt-bundle evidence exists in `docs/review/runtime_qa_audit_2026-07-31.md`; Tier 1 current checkout has no `dist/SignKitPremium.app`. The spec currently sets `codesign_identity=None` and `entitlements_file=None`. | Fresh build, exact architecture inspection, Developer ID signing identity, `codesign --verify --deep --strict`, Gatekeeper assessment, notarization/stapling when distributed outside local QA, clean-install launch, backend-online and offline fallback walkthrough. |
| macOS standard and Intel | Specs exist at `build-tools/SignatureExtractor_macOS.spec` and `build-tools/SignatureExtractor_Intel.spec`; CI names corresponding ARM64 and Intel jobs. | Tier 1 only. No current DMG or installed bundle was found. | Build and install on each named architecture. Do not infer Intel compatibility from Apple Silicon code or CI YAML. |
| Windows x64 | `build-tools/SignatureExtractor_Windows.spec` and the CI Windows job produce `SignKit_Windows.zip`. | Tier 1: the dated 11 MB archive exists and contains `SignKit_Windows.exe`; there is no current build, Authenticode verification, SmartScreen assessment, or runtime check. | Fresh Windows build, signed executable assessment, clean-user install/launch, extraction and PDF smoke, backend fallback, and uninstall/update recovery. |
| Linux x64 | `build-tools/SignatureExtractor_Linux.spec` and the CI Linux job define a tarball bundle. | Tier 1 only. No `dist/SignKit_Linux.tar.gz` was found. | Fresh Ubuntu-compatible build, extraction, PDF, local-data-path, Qt dependency, and archive-install smoke on the declared support baseline. |

## Prioritized implementation units

### U1. Reproducible desktop release qualification

- Priority: P0 for any downloadable desktop release.
- Owner surface: `build-tools/build.py`, platform specs, CI workflows, and release publishing scripts. Keep profile-to-entrypoint resolution canonical in `build-tools/build.py`.
- Contract: one release manifest must bind version, commit identity, profile, platform/architecture, artifact checksum, signing status, and manual QA record. The build must not silently use a stale interpreter or emit a profile different from the selected entrypoint.
- Dependencies: stable dirty-work ownership, maintained `.venv`, platform runners, signing/notarization credentials, and a release destination.
- Failure behavior: fail the release gate before upload if the artifact is missing, unsigned when required, wrong architecture, missing the backend/resources, or fails clean-install smoke. Preserve failed logs and artifact metadata.
- Operator visibility: an artifact matrix records build ID, SHA-256, signer, notarization/Gatekeeper result, install result, backend mode, and test outcome for each platform.
- Acceptance criteria: build all declared release targets fresh; verify the macOS premium and standard profile names at runtime; install each resulting artifact on its target platform; exercise local extraction, Vault retrieval, PDF open/save, and offline backend fallback; attach output checksums and signing evidence.
- Tests and release gate: retain the current profile test suite, then add build-artifact inspection tests and per-platform clean-install smoke jobs. No public platform-download claim advances beyond Tier 1 until this gate reaches Tier 3 or higher per platform.

### U2. Canonical checkout-to-entitlement contract

- Priority: P0 for any paid Personal, Team, Business, or workflow offer.
- Owner surface: the existing checkout configuration owner (`web/live/js/checkout-config.js`, `web/live/js/checkout.js`, and `desktop_app/config.py`) plus one new, documented backend fulfilment boundary. Do not add a second checkout configuration or a client-side activation bypass.
- Contract: provider event or verified order lookup creates an immutable purchase record, maps an explicit offer to a license tier/add-on, issues a signed/verifiable entitlement, supports revocation/refund, and records idempotency/provider event identity. The desktop verifies this material locally and exposes a receipt/status rather than accepting arbitrary six-character strings.
- Dependencies: provider product setup, a chosen provider of record, webhook/signature specification, legal refund procedure, secure secret storage, and an ADR defining offline grace/recovery behavior.
- Failure behavior: invalid or replayed provider events are rejected and auditable; an unknown or revoked entitlement fails closed for paid automation while leaving non-destructive local data accessible; checkout failure gives a support-safe message with no document metadata.
- Operator visibility: purchase ID, provider event ID, offer, entitlement state, issuance/revocation time, and support correlation ID. Never log license secrets, document paths, or document contents.
- Acceptance criteria: provider sandbox success, decline, timeout, duplicate-event, retry, refund/revocation, device migration, offline grace expiry, and desktop activation are each traceable to the same receipt record.
- Tests and release gate: fixture and signature-verification tests, provider sandbox integration, and desktop end-to-end activation test. Until then, routing tests prove only URL selection. Public copy remains limited to configured-provider routing, exactly as `docs/launch_claims/registry.md` requires.

### U3. Transactional local workflow execution substrate

- Priority: P0 before recurring folder automation is offered, bundled as a premium entitlement, or operated by more than one person/process.
- Owner surface: retain the `desktop_app/workflows/store.py` API as the single store boundary, migrate its JSON document to a transactionally durable local store with migration/export support, then update `engine.py`, `folder_monitor.py`, `authorization.py`, and the three workflow UI surfaces through that boundary.
- Contract: one recipe version plus input fingerprint yields one durable execution identity. State transition and audit receipt commit together. Scan, manual run, retry, cancellation, and quarantine are idempotent. `FolderConfig.require_stable_size` becomes an actual two-observation readiness check rather than unused configuration.
- Dependencies: a data-migration ADR, a backup/export format, and a decision on the supported concurrency model. Existing records must migrate without losing recipes, grants, jobs, or events.
- Failure behavior: a file changing during intake stays queued or needs review; a duplicate fingerprint reports the existing job; a crash rolls back or resumes without duplicate signing; output collision and revoked grant remain terminal/auditable. No source signature or input document is deleted by cleanup.
- Operator visibility: show fingerprint, recipe version, grant, actor, each state change, retry count, review copy, output path reference, and a recoverable error code. The console already has a state summary and last-reason column; the next unit must make it enough to explain duplicate and recovery outcomes.
- Acceptance criteria: real-PDF fixture proves input stability, grant revocation race, process restart, duplicate scan after completed/retry states, partial write, output collision, quarantine, and source-asset preservation. A fresh populated UI run covers recipe creation through folder scan, authorized output, retry/quarantine, and receipt export.
- Tests and release gate: add concurrency/crash and migration tests to the existing `desktop_app/tests/test_workflow_*.py` suite. A passing empty-state smoke test does not open the workflow launch gate.

### U4. Local extraction and PDF quality boundary

- Priority: P1 for broad auto-detection marketing; P0 only if auto-detection is represented as reliable without manual review.
- Owner surface: `desktop_app/processing/extractor.py`, `desktop_app/tests/fixtures/auto_detect_golden.json`, PDF viewer/signer modules, and their existing test suites.
- Contract: retain manual selection as the dependable local path. Treat auto-detection as an assistive proposal with a user-visible crop, confidence, and recovery path until a versioned, representative corpus establishes thresholds. PDF placement remains visual image placement, not a legal, certificate-backed, or regulated-signature assertion.
- Dependencies: labeled corpus with provenance/consent, expected regions, IoU/false-positive thresholds, and test fixtures that cover scans, photos, faint ink, disconnected strokes, rotations, and adversarial inputs.
- Failure behavior: uncertain detection requires review rather than exporting a silent crop; unreadable PDFs or unavailable optional libraries produce an actionable local error; saved PDFs have a readable result/audit state but no invented legal guarantee.
- Operator visibility: selection bounds, confidence/candidate information, renderer state, chosen signer backend, and local audit record. The current PDF audit and status controls are useful foundations but need release-level evidence.
- Acceptance criteria: dataset benchmark meets declared threshold, manual fallback works for every failed detector fixture, PDF save output opens independently, and validation covers both PyMuPDF and pikepdf fallback where supported.
- Tests and release gate: expand existing extractor/PDF tests with the corpus, negative golden cases, and independent viewer validation. Do not publish accuracy, speed, or legal-effect claims before appropriate Tier 3 or Tier 5 proof.

### U5. Hosted workspace safety gate

- Priority: P1 research/implementation gate, P0 before any hosted Cloud or Hybrid claim.
- Owner surface: the existing `backend/app/routers/workspace.py` route family, its model/schema/service modules, `backend/alembic/versions/ca3107e4a9f1_add_workspace_control_plane.py`, and `web/cloud_workspace/`. Extend this canonical route family rather than adding a parallel workspace API.
- Contract: continue storing workflow metadata only until a signed-off document/evidence model exists. Add explicit workspace membership/roles, record-level authorization, transactional ordered events or a retry strategy for the unique event sequence, retention/deletion/export controls, secure production configuration, and operator incident views before hosted use.
- Dependencies: Cloud privacy policy, data map, retention schedule, security review, migrations, hosted observability, and legal review. A document upload, signature asset, certificate, identity, or provider callback requires a separate ADR first.
- Failure behavior: owner-scope violations return no record; invalid/replayed transitions fail closed; unique-sequence conflicts are retried or surfaced without losing a receipt; unavailable hosting leaves local desktop work unaffected.
- Operator visibility: execution owner, template version, state, ordered receipt, transition rejection, deployment revision, retention state, and incident correlation. Do not include document contents in logs.
- Acceptance criteria: authenticated API integration covers cross-owner access denial, concurrent transition collision, migration from empty database, restart/retry, retention/export/delete behavior, and a deployed environment with secrets and logs checked. Browser use is described only as recording workflow metadata.
- Tests and release gate: preserve `backend/tests/test_workspace_service.py`, add router/auth/migration concurrency tests, then run a hosted staging smoke. The current three-state HR template is not a signature ceremony and must not be marketed as one.

### U6. Claim, release-note, and deployment reconciliation

- Priority: P0 for public copy or a GitHub release.
- Owner surface: `docs/launch_claims/registry.md`, `tests/test_launch_claim_registry.py`, root `index.html`, checkout scripts, release workflow bodies, and deployment smoke scripts.
- Contract: every public claim has a registry entry, enforcing test, evidence tier, and release state. Release notes must use the same qualified local-first language as the root page.
- Current risk: Tier 1 static inspection of `.github/workflows/build-all-platforms.yml` and `.github/workflows/build-macos.yml` still finds absolute offline and placeholder/test-license wording in release bodies. That conflicts with the current registry's qualified boundary and must be reconciled before those workflows publish a release.
- Acceptance criteria: current published checkout scripts return JavaScript, the configured provider route is manually/sandbox verified, release body contains no unsupported privacy, legal-signature, platform, or fulfilment claim, and fresh deployment smoke passes.
- Tests and release gate: `tests/test_launch_claim_registry.py` stays mandatory; add workflow/release-body static checks and a deployment smoke that verifies content type and action destination. A static claim test alone is never proof of provider fulfilment.

## Data, configuration, and operator boundary register

| Boundary | Current canonical location | Rule for the next unit |
| --- | --- | --- |
| Desktop launch/profile config | `desktop_app/launch_profile.py`, `desktop_app/config.py` | Keep profile mapping and checkout routing in these owners. Version should flow from one release manifest, not duplicated literals. |
| Local license state | `~/.signature_extractor/license.json` via `desktop_app/license/storage.py` | Replace permissive local-key semantics only through the canonical storage/validator contract and a migration path. |
| Vault data | `~/.signkit/vault` via `desktop_app/processing/vault.py` | Preserve encrypted blobs and metadata; provide export/recovery and deletion verification before broad workflow automation depends on it. |
| Workflow data | `~/.signature_extractor/workflow_store.json` via `desktop_app/workflows/store.py` | Migrate atomically through one store interface; do not keep JSON and a new database as independently editable truths. |
| Local backend data | platform user-data directory via `desktop_app/backend_manager.py` and `backend/app/paths.py` | Maintain loopback-only assumptions for bundled use. Do not repurpose `/uploads/images` as a public multi-tenant store. |
| Cloud workspace data | `workspace_executions` and `workspace_execution_events` through the existing migration and service | Metadata only. Any document/evidence expansion needs a separate privacy, retention, and trust decision. |
| Checkout configuration | `web/live/js/checkout-config.js` and `desktop_app/config.py` | Product identifiers are configuration, not proof of activation. Provider secrets and webhook signing keys stay server-side. |

## Concrete verification record from this audit

| Command | Outcome | Evidence |
| --- | --- | --- |
| `./.venv/bin/pytest -q tests/test_build_profile.py tests/test_entrypoints.py tests/test_launch_profile.py tests/test_app_bootstrap_profile_access.py` | `15 passed in 0.70s` | Tier 2 profile, entrypoint, and bootstrap wiring. |
| `./.venv/bin/pytest -q desktop_app/tests/test_extractor.py desktop_app/tests/test_pdf_features.py desktop_app/tests/test_workflow_engine.py desktop_app/tests/test_folder_monitor.py desktop_app/tests/test_workflow_screen_smoke.py desktop_app/tests/test_checkout_config.py desktop_app/tests/test_purchase_routing.py backend/tests/test_workspace_service.py tests/test_launch_claim_registry.py` | `79 passed in 3.17s` | Tier 2 focused feature contracts. This is not a packaged runtime, provider, hosted deployment, or cross-platform install proof. |
| `find dist ...` plus bundle checks | `dist directory absent`; `dist/SignKitPremium.app absent`; only `SignKit-Windows/SignKit_Windows.zip` was found. | Tier 1 artifact inventory. No current release artifact was claimed. |
| `unzip -l SignKit-Windows/SignKit_Windows.zip` | One `SignKit_Windows.exe`, archive timestamp 2025-11-15, size 11 MB. | Tier 1 historical artifact inspection only. |
| Current-path search for provider terms | Checkout routing exists in desktop and static-page owners; no webhook or provider fulfilment surface was found under `backend/` or `desktop_app/`. | Tier 1 architecture finding. |

The runtime evidence ceiling is the recorded Tier 4 macOS run in `docs/review/runtime_qa_audit_2026-07-31.md`: rebuilt Premium app launch, backend-online indication, supplied-sample extraction, PDF `Page 1 of 6`, and empty-state workflow controls. Its falsifier is a fresh build and clean-instance runtime walkthrough. It must be re-run after any release-candidate change.

## Explicit release decisions

- **Personal local desktop release:** not approved today. Current code and tests support a fresh release-qualification attempt, but there is no current macOS bundle in `dist/`, no current Windows/Linux runtime proof, and no verified purchase-to-license fulfilment.
- **Paid workflow automation:** blocked by U2 and U3. The current UI, grants, and integration tests are valuable foundations, but the JSON concurrency/idempotency boundary and commercial enforcement are not release-grade.
- **Hosted Cloud or Hybrid workspace:** blocked by U5. The current browser workspace is a metadata-only, owner-scoped foundation. It is not a hosted signing, document-storage, sync, or compliance product.
- **Auto-detection quality claim:** blocked by U4. The canonical sample is tested; generalized accuracy is not established.

## Review passes

1. **Immediate correctness and completeness:** mapped each requested desktop, workflow, checkout, backend workspace, and build interface to a live path; ran the required profile suite and the focused cross-surface suite.
2. **Architecture and long-term viability:** kept one desktop engine, one local workflow store boundary, one workspace route family, and one checkout configuration owner. Identified release boundaries where the current implementation is a foundation rather than a customer promise.
3. **Rule compliance and supervision readiness:** separated Tier 1 inspection, Tier 2 tests, recorded Tier 4 runtime evidence, and absent Tier 3/Tier 5 proof. Every proposed implementation unit names failure behavior, operator visibility, and a falsifiable release gate.

## Anything else?

Yes. The strongest immediate risk is not a missing UI control. It is a mismatch between a polished desktop surface and unproven operating contracts: a buyer can be routed to checkout, but the repository does not currently show provider-backed entitlement issuance; workflow state can be displayed, but the local JSON store does not yet establish transaction-level recovery and deduplication; platform jobs are declared, but current artifacts are absent. Keep the customer promise narrow until U1, U2, and the relevant feature gate close with fresh evidence.

## Update log

- 2026-08-02: created this implementation contract from current static inspection, fresh focused tests, current artifact inventory, and the recorded 2026-07-31 native runtime audit. No application code, test, configuration, build spec, entitlement, or external deployment was changed by this audit.
