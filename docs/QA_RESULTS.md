# SignKit release QA results

Run date: 2026-08-13
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Runtime: repository `.venv`, Python 3.13
Scope: local reproducible matrix only unless stated otherwise

## Executed results

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| QA-01 | PASS | Tier 2, S1 | `tests/test_security.py` selected file-size case passed. The existing test uses a 51 MiB payload and verifies rejection before image decoding. |
| QA-02 | PASS | Tier 3, S1 | `backend/tests/test_extraction_router.py` dimension case passed. The route rejected the oversized dimension configuration and left the upload directory empty. |
| QA-03 | PASS | Tier 4 local Qt, S1 | `desktop_app/tests/test_main_window_logic.py -k exif` passed all 8 orientations. The test first failed because the RGB QImage stride was not explicit, then the loader was corrected and the full file passed `28 passed, 3 skipped`. |
| QA-04 | PASS | Tier 2, S1 | `desktop_app/tests/test_coordinate_mapping.py` sub-pixel case passed with a nonzero 1x1 selection. |
| QA-05 | PASS | Tier 3, S1 | Uploading valid PNG bytes with `application/pdf` returned 415 and wrote no artifact. The route now has an explicit unsupported-media contract. |
| QA-06 | PASS | Tier 3, S1 | Invalid extraction session returned 404 and wrote no metadata. |
| QA-07 | PASS | Tier 3, S1 | Workspace malformed and unkeyed document inspection cases returned 422. |
| QA-08 | PASS | Tier 2, S1 | Manual offline mode returned the typed offline error and the fake HTTP client was not called. The combined API and coordinate suite passed `25 passed`. |
| QA-09 | PASS | Tier 1 plus Tier 2, S1 | Configuration contract and backend manager checks passed `6 passed`; fresh SQLite migration to Alembic head also passed in the canonical environment. |
| QA-10 | PASS | Tier 3 local runtime | Fresh `bash scripts/test-deployment.sh http://127.0.0.1:8080` passed the root, 27 legacy redirects, wildcard routes, retained asset content types, and JavaScript content-type checks against the running canonical `serve.py`. This is not hosted proof. |
| QA-11 | PASS | Tier 3 local runtime | Fresh `./.venv/bin/python tools/test_deployed_surface.py --base-url http://127.0.0.1:8080 --json` returned `status: pass`, with the canonical document-registration-studio marker, 301 legacy redirects, current checkout assets, and no errors. This is not hosted proof. |
| QA-21 | PASS | Tier 2 local suite, S2 for shutdown regression | The canonical root command now collects `492` first-party tests and passes `488 passed, 4 skipped`, including the documentation truth-map and operator-state checks. The native-form module reports an explicit missing-optional-PyMuPDF skip. The destructor logging test failed under a deliberate reversion and passed after the fix. Prior `491 collected / 487 passed` and `487 collected / 484 passed` runs are preserved as historical evidence in the addenda. |
| QA-22 | PASS | Tier 2 local suite, S1 | `backend/tests/test_config_and_path_security.py backend/tests/test_extraction_router.py` passed `13 passed` with an isolated SQLite URL. The recovered security group removes hardcoded credential defaults, fails closed for incomplete production configuration, preserves local SQLite, and asserts POSIX owner-only data/sidecar permissions. |
| QA-23 | PASS | Tier 2 local suite, S1 | Signed entitlement receipt, receipt-owned plan/add-on grants, key-only fail-closed behavior, explicit test-mode isolation, replay, tamper, expiry, and second-entitlement conflict tests passed `15` focused checks. This is local code evidence only. |
| QA-24 | PASS | Tier 2 local offscreen-Qt contract, S1 | `tests/test_signature_candidate_dialog.py tests/test_color_signature_candidate.py` plus the auto-detect integration subset passed `8` checks. The UI exposes ranked candidates with clipped previews and requires explicit confirmation; the score remains labeled as non-probabilistic. This is not real-GUI, device, or assistive-technology observation. |
| QA-25 | PASS | Tier 2 local synthetic evaluation, S1 | `tools/evaluate_signature_corpus.py` ran against the six-case edge regression corpus and the three-case subject-disjoint validation and test slices. At IoU `0.5`, the edge set reached instance precision/recall/F1 `1.000/0.833/0.909` and mean IoU `0.840`; validation and test each reached `1.000/1.000/1.000` and mean IoU `0.784`. These are synthetic fixture measurements only and do not establish human, production, hosted, or calibrated-probability claims. See `docs/research/auto_detection_synthetic_baseline_2026-08-13.md`. |
| QA-26 | PASS | Tier 3 local native-GUI observation, S1 | `tools/run_candidate_picker_gui_proof.py` passed without offscreen Qt in the active macOS desktop session. It observed native preview rendering, candidate-selector keyboard focus, explicit Cancel rejection, OK confirmation of candidate 2, and `Preview unavailable` when the source image is absent. Screenshot SHA-256: `dc39ec722a10cc541cb5f5230b9882d87c9764eaa4803956200250ef7f087abe`. This does not establish assistive-technology, cross-platform, packaged, hosted, or full-workflow proof. See `docs/review/candidate_picker_native_gui_proof_2026-08-13.md`. |
| QA-27 | PASS with warnings | Tier 2 local static claim-surface audit, S1 | `tools/audit_public_surface.py --strict --json` reported `13` registered claim families, `0` errors, `27` legacy redirects, and `5` wildcard redirect groups. It intentionally retained warnings for legacy HTML checkout/high-risk claim content and `30` historical documentation references. This advances the local audit but does not close deployed redirect, artifact exclusion, legal wording, or hosted proof gates. |
| QA-28 | PASS | Tier 4 local disposable operator workflow, S1 | `tools/run_local_source_to_ready_proof.py` passed with extraction, encrypted Vault round trip, forced `ERR_SIGNING_FAILED` to `retry`, canonical retry to `completed`, metadata-only passports, and verified visual placement receipt. The manifest reported no hosted service contact and no document bytes in the browser workspace. See `docs/review/local_operator_state_proof_2026-08-13.md`; malformed-input, timeout, partial-export, deletion-cleanup, and companion-outage states remain open. |
| QA-29 | PASS | Tier 2 local operator-content contract, S1 | `tests/test_operator_content.py` passed `3` checks for human-facing state labels, bounded failure copy, terminal/retry wording, and absence of raw local paths or exception text in primary messages. The workflow console now consumes the canonical content layer; this does not close runtime failure-state or accessibility observation gates. |
| QA-30 | PASS | Tier 2 local companion-content contract, S1 | `tests/test_operator_content.py tests/test_topology_experience_contract.py` passed focused assertions for bounded online, starting, checking, and offline copy. Desktop extraction, main-window health, and onboarding now consume the canonical companion content layer; raw endpoint, health-error, and exception details are not used as primary outage copy. This closes the copy-binding sub-gate, not real outage recovery, assistive-technology, or packaged observation. |
| QA-31 | PASS | Tier 2 local malformed-input workflow contract, S1 | `desktop_app/tests/test_workflow_engine.py tests/test_operator_content.py` passed malformed non-PDF routing and bounded copy checks. The workflow persists `NEEDS_REVIEW` with `ERR_INPUT_INVALID`, does not consume a retry attempt, and does not retain parser exception text in the primary recovery message. This does not close timeout, partial-export, cleanup, or assistive-technology evidence. |
| QA-32 | PASS | Tier 2 local partial-export orchestration contract, S1 | `tests/test_pdf_export_recovery_contract.py tests/test_operator_content.py desktop_app/tests/test_export_mode_dispatch.py tests/test_artifact_receipt.py` passed the final verification and cleanup contract. The PDF save surface verifies output before recording success, removes a newly created failed output, and uses bounded export recovery copy. Producer-specific atomic behavior and packaged/device export observation remain separate gates. |
| QA-33 | PASS | Tier 2 local library deletion contract, S1 | `tests/test_library_deletion_contract.py desktop_app/tests/test_main_window_logic.py -k delete_selected_library tests/test_operator_content.py -k deletion_copy` passed complete sidecar cleanup, metadata-only deletion receipts, surfaced `cleanup_incomplete` behavior, path-boundary rejection, and structured Qt action handling. Explicit repair was added and verified separately as QA-44. Runtime permission/device and recovery-after-restart observation remain open. |
| QA-34 | PASS | Tier 2 local companion timeout/retry-control contract, S1 | `desktop_app/tests/test_main_window_logic.py -k 'companion_offline or backend_health or timeout' tests/test_topology_experience_contract.py tests/test_operator_content.py` passed bounded typed-timeout copy, explicit Retry local service visibility for offline state, hidden retry control after online recovery, and API-client interface fallback. This is a local UI/control contract; real process restart and packaged/device observation remain open. |
| QA-35 | PASS | Tier 4 local companion process recovery, S1 | The real `BackendManager` started an isolated local companion on port `8124`, passed health proof, restarted to a new process with health proof, and shut down cleanly with no managed process or health response remaining. See `docs/review/local_companion_restart_proof_2026-08-13.md`. This is not packaged, cross-platform, hosted, or assistive-technology evidence. |
| QA-36 | PASS with boundary | Tier 4 local real-Chrome accessibility contract plus Tier 2 static contracts, S1 | The canonical root and `/workspace-app/` now expose a stable main landmark and focused skip link across login/workspace views; the dynamic local PDF file control has an explicit label association. Focused contracts passed `13`; `node tools/run_local_product_browser_proof.mjs` passed at 1440x900, 390x844, and 320x844 for the root plus 390x844 for the workspace with no browser errors or overflow. See `docs/review/local_accessibility_audit_2026-08-13.md`. This is not VoiceOver, WCAG certification, packaged, cross-platform, hosted, or device evidence. |
| QA-37 | PASS with boundary | Tier 2 local PDF field-detection and documentation contract, S1 | `desktop_app/tests/test_pdf_field_detection.py tests/test_auto_detection_doc_coverage.py` passed `15` checks. A generated labeled AcroForm field was detected with confidence `>=0.90` and IoU `>=0.85`; shared coordinate-transform and dedupe contracts are enforced; image and PDF detector modules are documented. Synthetic image evaluation was rerun separately and retains the known multi-signature miss. See `docs/review/pdf_field_detection_contract_proof_2026-08-13.md`. This is not human/production PDF accuracy, calibrated confidence, unattended-placement safety, packaged, cross-platform, hosted, or assistive-technology evidence. |
| QA-38 | PASS | Tier 2 local configuration contract, S1 | `tests/test_configuration_contract.py tests/test_local_product_stack_contract.py` passed `6` checks. `.env.example`, backend settings, launcher defaults, desktop docs, and active local product analysis agree on port `8001`, SQLite local configuration, and required JWT replacement guidance. Historical `8000` references remain preserved and classified. See `docs/review/local_configuration_contract_proof_2026-08-13.md`. This does not prove hosted environment configuration, target migrations, production secrets, or deployment smoke. |
| QA-39 | FAIL, shared-tooling release blocker | Tier 2 command execution | A bounded `agent-start --skip-index --quiet` run returned `0` but selected workspace Doctrine 6.0, modified all six generated context files, and deleted the tracked project-local `motto_v5.md`; the shared Projects-root alias was absent. The project files were restored from `HEAD` after capture. `RECON-26` requires a source-selection/retention fix and two consecutive clean refreshes. See `docs/issue_review_agent_start_context_2026-08-13.md`. |
| QA-40 | PASS with boundary | Tier 2 local workflow and operator-content contract, S1 | `desktop_app/tests/test_workflow_engine.py tests/test_operator_content.py desktop_app/tests/test_workflow_screen_smoke.py` passed `36` checks. Old transient jobs recover explicitly to `NEEDS_REVIEW` with `ERR_WORKFLOW_INTERRUPTED` and a durable event; fresh jobs and invalid timestamps remain unchanged; no automatic retry occurs and primary copy requires planned-output review. See `docs/review/local_stale_workflow_recovery_proof_2026-08-13.md`. This does not prove packaged, cross-platform, filesystem, assistive-technology, hosted, or provider recovery. |
| QA-41 | PASS with boundary | Canonical local full suite, S1 | `./.venv/bin/python -m pytest -q` passed `522 passed, 4 skipped` after the agent-start contract, calibration slice, and local deletion-recovery slice. The four skips remain explicit for optional PyMuPDF and Qt event-loop boundaries. This is local evidence only and does not substitute for remote CI, packaged/cross-platform, hosted, provider, device, or assistive-technology proof. |
| QA-42 | PASS with boundary | Tier 4 local command execution plus Tier 2 static guard | Two bounded `agent-start --skip-index --quiet` refreshes returned `0`; both selected project-local `motto_v5.md`, retained its expected SHA-256, and preserved the workspace Doctrine 6.0 boundary. `/Users/pranay/Projects/motto_v5.md` resolved to the Downloads motto source. `tests/test_agent_start_doctrine_contract.py` guards the live wrapper source. Full retrieval/index health remains open under `RECON-06`. See `docs/review/agent_start_doctrine_contract_proof_2026-08-14.md`. |
| QA-43 | PASS with boundary | Tier 2 local calibration contract, S1; synthetic-only | `tests/test_calibration_harness.py tests/test_agent_start_doctrine_contract.py` passed `7` checks and `./.venv/bin/python -m calibration.run --self-test` completed. The harness validates one-to-one matching, PDF page indexes, split-boundary warnings, and pure-numpy calibration metrics. No real-data calibration, production accuracy, or threshold promotion is claimed. See `docs/review/calibration_harness_proof_2026-08-14.md` and `docs/calibration_dataset_spec.md`. |
| QA-44 | PASS with boundary | Tier 2 local deletion-recovery and operator-control contract, S1 | `tests/test_library_deletion_contract.py tests/test_operator_content.py desktop_app/tests/test_main_window_logic.py` passed `37` checks with `3` pre-existing event-loop skips. The explicit `Repair Cleanup` action repairs incomplete sidecar cleanup only after operator invocation, atomically updates metadata-only receipts, preserves unresolved directories and unsafe/malformed targets, and keeps bounded recovery copy. Permission/device, restart, packaged, assistive-technology, and hosted deletion evidence remain open. See `docs/review/local_library_cleanup_recovery_proof_2026-08-14.md`. |
| QA-45 | PASS with boundary | Tier 3 local shared-tooling runtime plus generated-context provenance | The documented workspace-memory setup produced Python `3.13.3` and `memsearch 0.4.17`; a real SignKit sync/index/search processed `588` files and `16042` chunks; full `agent-start` retrieval completed with `16047` project-collection chunks; and a bounded forced-retrieval refresh returned `0`. Generated context retained the project-local motto SHA and truthfully recorded unavailable shared-collection status. The prior Milvus database was preserved before initialization. Provider portability, all-project retrieval quality, hosted execution, and canonical generated snapshots after calibration reconciliation remain open. See `docs/review/agent_start_retrieval_runtime_proof_2026-08-14.md`. |
| QA-46 | PASS with boundary | Canonical local full suite, S1 | `./.venv/bin/python -m pytest -q` passed `523 passed, 4 skipped` after the local retrieval proof and documentation updates, while the concurrent calibration slice remained present but unstaged. The skips remain explicit for optional PyMuPDF and Qt event-loop boundaries. This is local evidence only and does not close remote CI, packaged/cross-platform, hosted, provider, device, assistive-technology, or external-corpus gates. |
| QA-47 | PASS with boundary | Tier 2 local commit-gate source and pre-commit execution | `bash -n` passed for `.githooks/pre-commit`, `.githooks/commit-msg`, and `.githooks/prepare-commit-msg`; the active `.githooks/pre-commit` then completed successfully against the staged documentation and preserved-hook blast radius. It refreshed project context and ran the objective checks. The hook intentionally stages the generated `.agent` compatibility mirror when present; the lower-case `docs/context/agent-start` snapshots and concurrent calibration implementation remain unstaged. Full prepare-commit, commit-msg, pre-push, and remote parity remain to be verified. |
| QA-48 | PASS with boundary | Full local commit and remote delivery gate | Commit `c06aefc` passed the configured `prepare-commit-msg`, pre-commit, and commit-message motto gates with full section attestation, then `git push origin main` succeeded. `git rev-parse HEAD`, `git rev-parse origin/main`, `git rev-list --left-right --count HEAD...origin/main`, and `git ls-remote origin refs/heads/main` all confirm parity at `c06aefce35d9bbebc9c8b24253dcde3c5abe2533`. This proves local Git delivery only; hosted deployment, remote CI, provider, packaging, and device evidence remain separate. |
| QA-49 | PASS with boundary | Tier 2 calibration artifact contract plus Tier 3 generated-fixture execution | `tests/test_calibration_artifact_policy.py tests/test_calibration_harness.py` passed `10` checks. The builder produced byte-identical eight-sample manifests in two independent output directories with recorded metadata and eight assets per detector; the loader rejects mismatched generation metadata. Git exposes manifests, reports, and notes while ignoring generated PNG/PDF assets. Four current 120-sample image/PDF reports reran successfully: image isotonic ECE `0.3000→0.0283`, PDF isotonic ECE `0.8289→0.0074`; PDF ROC-AUC remains `0.6032` and its Platt inversion is flagged. This is synthetic-labelled internal evidence only. See `docs/review/calibration_artifact_policy_proof_2026-08-14.md`. |
| QA-50 | PASS with boundary | Canonical local full suite, S1 | `./.venv/bin/python -m pytest -q` passed `526 passed, 4 skipped` after the calibration artifact policy, manifest metadata validation, and documentation updates. The four skips remain explicit for optional PyMuPDF and Qt event-loop boundaries. This is local evidence only and does not close remote CI, packaged/cross-platform, hosted, provider, device, assistive-technology, or external-corpus gates. |
| QA-51 | PASS with boundary | Tier 4 local operator workflow and real Chrome observation, S1 for the executable proof | `tools/run_local_product_stack.py` started the canonical landing and companion with isolated SQLite and filesystem data, and clean shutdown stopped both children. `node tools/run_local_product_browser_proof.mjs` passed at 1440x900, 390x844, and 320x844 with the document-registration-studio title, five-state rail, keyboard/pointer state changes, reduced motion, canonical workspace handoff, no overflow, and zero browser errors. `tools/run_local_source_to_ready_proof.py` passed with forced `ERR_SIGNING_FAILED` recovery, verified visual-placement receipt `sha256:0d3d13811121d716bcfae3c49f0240c06b265a82e59ce6f7d4cd3b0bbde96f2d`, and no hosted contact. `tools/run_local_workspace_bridge_browser_proof.mjs` passed with `401` unauthenticated rejection, `404` missing-job rejection, opaque receipt visibility, bounded retry recovery, no private path or document bytes, and zero browser errors. See `docs/review/local_product_operator_proof_2026-08-14.md`. Hosted, provider, packaged/cross-platform, assistive-technology, legal-signature, and real-user evidence remain separate. |
| QA-52 | PASS with boundary | Tier 2 ledger contract plus Tier 3 mutation sensitivity, S2/S3 | Red-first release-ledger identity tests first failed as intended (`3 passed, 2 failed`) before implementation. The final focused ledger suite passed `6 passed`; source SHA validation rejects non-commit identifiers, and duplicate artifact names and paths are rejected. The complete mutation manifest killed `16/16`, including `3/3` new ledger defects. See `docs/review/release_artifact_ledger_proof_2026-08-14.md`. Real platform artifacts, signing/notarization, launch smoke, rollback, remote CI, hosted, and provider evidence remain open. |

Additional touched-flow checks:

- `backend/tests/test_extraction_router.py`: `7 passed`.
- `backend/tests/test_extraction_hosted.py tests/test_extraction_service.py`:
  `13 passed`.
- `tests/test_integration_workflows.py`: `11 passed`.
- `tests/test_security.py`: `15 passed`.
- `tests/test_configuration_contract.py desktop_app/tests/test_backend_manager.py`:
  `6 passed`.
- `QT_QPA_PLATFORM=offscreen desktop_app/tests/test_main_window_logic.py`:
  `28 passed, 3 skipped`. The skips are pre-existing event-loop-dependent
  cases outside the EXIF loader check.
- Static compilation of changed Python modules and `git diff --check` passed.

CI-equivalent execution after binding the matrix into
`.github/workflows/test-data.yml`:

- Workflow contract, backend/configuration, desktop/API, security, and route
  checks passed `90 passed, 3 skipped` in one serialized run.
- `desktop_app/tests/test_extractor.py` passed `9 passed`, including the
  destructor-shutdown logging regression check.
- `tools/run_extraction_hosted_smoke.py` passed against a temporary SQLite
  database with all migrations through `9c4b7e2d1a6f` applied.
- `tools/mutation_check.py` passed `5/5 mutants killed` when run separately
  from ordinary tests. A first concurrent attempt was invalid because the
  mutation tool temporarily edits source files while tests are running; that
  run is not release evidence and was superseded by the serialized pass.
- YAML parsing, Python compilation, and `git diff --check` passed.

## Not closed by this run

| ID | Status | Evidence or next step |
| --- | --- | --- |
| QA-12 | PASS | Tier 4 local real-Chrome runtime | Fresh `node tools/run_local_product_browser_proof.mjs` passed at 1440x900, 390x844, and 320x844. The proof now asserts the main landmark, visible focused skip link and `#main-content` target, labeled five-state rail, canonical primary workspace CTA, keyboard focus/state transition, pointer state transition, reduced motion, no horizontal overflow, and zero browser errors. This is local browser evidence, not a full assistive-technology audit. |
| QA-13 | FAIL, release-blocking | The 2026-08-13 external probe still found the deployed root without the current canonical marker, legacy paths returning 200/308 instead of the required 301 policy, and checkout JavaScript paths returning HTML. Re-run after target deployment propagation. |
| QA-14 | OPEN | Local production-like migration and hosted smoke exist, but target-database application, live authenticated smoke, rollback, and operator receipt evidence remain open under L0-09. |
| QA-15 | OPEN | Provider-neutral entitlement code and research exist, but no configured product ID, controlled purchase, refund/revocation webhook, or provider-backed receipt evidence exists. |

## Interpretation

The local QA matrix is now reproducible and attached to the launch runbook.
It supports closing the documentation/task-creation portion of L2-05, but it
does not authorize a hosted launch. The public deployment, migration/recovery,
packaging, and provider gates remain separate release blockers.

## Addendum (2026-08-13): first-party test discovery

QA-21 closes the silent collection gap locally. The canonical `pytest.ini`
now includes `tests`, `backend/tests`, and `desktop_app/tests`; the CI release
matrix uses the same default collection. The full local result is `475 passed,
4 skipped` at S1, with S2 sensitivity for the destructor shutdown fix. The
four skips remain explicit and are not release claims: one is the optional
PyMuPDF native-form capability and three require a Qt event loop.

The decision and alternatives are recorded in
`docs/decisions/ADR-0149-first-party-test-discovery-and-optional-pdf-boundary.md`.

The matrix is now part of the canonical CI workflow. The latest local run
collected `487` tests and passed `484 passed, 4 skipped` after the signed
entitlement slice. A GitHub-hosted run is
still required before L1-09 can close; local workflow-contract and
CI-equivalent evidence cannot substitute for the remote runner, artifact URL,
or retained workflow receipt.

QA-12 is closed for the reusable local browser contract at Tier 4. A full
screen-reader, VoiceOver, device-browser, and manual assistive-technology pass
remains a separate release-quality follow-up; the proof does not claim those
surfaces from Playwright alone.

## Addendum (2026-08-13): canonical workspace accessibility semantics

The accessibility audit found and corrected a local workspace landmark gap:
the login view had no active main landmark or stable skip target even though
the authenticated view did. The canonical workspace now uses one
`main#main-content` around both view states, exposes a visible-on-focus skip
link, and explicitly associates the dynamically rendered PDF file input with
its label. The focused semantic suite passed `13` checks and the real Chrome
proof passed at the documented local viewports with no overflow or browser
errors.

This is a local semantic and browser-observable result. VoiceOver/screen-reader,
manual zoom/reflow, device, packaged, cross-platform, hosted, and formal WCAG
evidence remain open.

## Addendum (2026-08-13): fresh local public-surface gate

The strict local auditor also returned `status: pass` with `claim_count: 13`,
27 redirect legacy paths, 27 server legacy paths, and no blocking errors. Its
warnings remain intentionally visible: retained historical pages contain
legacy checkout references and unsupported claims, and 30 historical documents
reference retired routes. These warnings do not make the current local root
unready, but they remain part of the hosted artifact/release review and must
not be mistaken for current product claims.

## Addendum (2026-08-13): packaged local desktop runtime

QA-20 passed for the macOS ARM64 standard bundle. The focused packaging and
backend-manager contract suite passed `10` tests at S1; the complete mutation
manifest passed `13/13` at S3; and the full repository suite passed `181` tests
at S1 after the generated-build HTML boundary was corrected. The frozen
artifact reached `/health` with HTTP 200, served and rendered `/workspace-app/`
with HTTP 200, passed the local landing/workspace handoff and authenticated
bridge recovery browser flows, created isolated SQLite/JWT state, contained no
`.env`, passed local ad hoc `codesign --verify --deep --strict`, and left no
port-8001 listener after the bounded smoke.

The detailed evidence is in
`docs/review/local_packaging_runtime_proof_2026-08-13.md`. This closes only
the local ARM64 artifact contract. Intel/Windows/Linux, distribution signing
and notarization, clean installation, rollback, hosted deployment, and
provider activation remain open.

## Addendum (2026-08-13): signed local entitlement slice

QA-23 passed with `15` focused entitlement checks. The canonical full local
run then passed `484 passed, 4 skipped` from `487` collected tests. The new
evidence covers signed receipt canonicalization, keyring verification,
receipt-owned grants, explicit test-mode isolation, replay, tamper, expiry,
and conflict behavior. It remains Tier 2 local evidence; QA-15 is still open
for a configured provider, controlled purchase, and revocation/support flow.

## Addendum (2026-08-13): candidate confirmation slice

QA-24 closes the local code-contract portion of auto-detection. The existing
multi-candidate engine output now has a human confirmation dialog with bounded
previews, cancel behavior that preserves the manual selection, and explicit
copy that the ranking score is not a probability. It does not establish
real-GUI interaction, accessibility technology behavior, accuracy, recall, or
generalization. Those remain gated by a real-GUI check, a permissioned labeled
corpus, and an evaluation harness.
