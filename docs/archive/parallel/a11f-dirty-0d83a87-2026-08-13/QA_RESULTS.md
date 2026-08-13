# SignKit release QA results

Run date: 2026-08-13  
Checkout: `/Users/pranay/.codex/worktrees/a11f/signature-extractor-app`  
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
| QA-10 | PASS | Tier 3 local runtime | The local deployment route matrix passed in the preceding release-gate run. This is not hosted proof. |
| QA-11 | PASS | Tier 3 local runtime | The local deployed-surface probe passed in the preceding release-gate run. This is not hosted proof. |

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
| QA-12 | OPEN | Local browser/accessibility evidence exists for the canonical root, but a fresh device and narrow-viewport pass is still needed. |
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
