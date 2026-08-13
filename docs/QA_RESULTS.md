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

The matrix is now part of the canonical CI workflow. A GitHub-hosted run is
still required before L1-09 can close; local workflow-contract and
CI-equivalent evidence cannot substitute for the remote runner, artifact URL,
or retained workflow receipt.

QA-12 is closed for the reusable local browser contract at Tier 4. A full
screen-reader, VoiceOver, device-browser, and manual assistive-technology pass
remains a separate release-quality follow-up; the proof does not claim those
surfaces from Playwright alone.

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
