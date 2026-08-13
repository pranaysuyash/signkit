# SignKit release QA checklist

Date established: 2026-08-13
Owner: Product and engineering
Scope: local desktop extraction, local backend contracts, offline behavior, and
the hosted/public release gates that must be run by the release owner.

This checklist is an execution surface, not a claim that every row is already
closed. Each result must identify its evidence tier and test sensitivity. A
passing test is recorded as S1 unless a deliberate breaking mutation is shown
to fail it. Local evidence does not close a hosted or provider gate.

## Reproducible local matrix

Run from the repository root with the canonical `.venv` and a test-only secret.
The backend commands must use an isolated SQLite database and must not use a
customer or hosted database.

| ID | Scenario | Command | Pass condition | Required evidence |
| --- | --- | --- | --- | --- |
| QA-01 | Large payload over 10 MiB | `.venv/bin/pytest -q tests/test_security.py -k file_size` | A payload above the 50 MiB local limit is rejected before decode | Test output plus S1 label |
| QA-02 | Large image dimensions over 4000 px | `.venv/bin/pytest -q backend/tests/test_extraction_router.py -k dimensions` | Oversized dimensions are rejected and no private artifact is written | Test output plus artifact-directory assertion |
| QA-03 | EXIF orientations 1 through 8 | `QT_QPA_PLATFORM=offscreen .venv/bin/pytest -q desktop_app/tests/test_main_window_logic.py -k exif` | Rotated and mirrored orientations produce the same pixels as `ImageOps.exif_transpose` | Test output, S1; promote to S3 before release if this gate is release-blocking |
| QA-04 | Tiny selection below 10 px | `QT_QPA_PLATFORM=offscreen .venv/bin/pytest -q desktop_app/tests/test_coordinate_mapping.py -k subpixel` | A sub-pixel drag becomes a nonzero 1x1 selection | Test output plus coordinate assertions |
| QA-05 | Unsupported image media type | `JWT_SECRET='<32+ chars>' DATABASE_URL='sqlite:///./.codex-test-tmp/qa.db' .venv/bin/pytest -q backend/tests/test_extraction_router.py -k media_type` | `application/pdf` upload returns 415 and creates no artifact | Test output plus response and filesystem assertions |
| QA-06 | Missing extraction asset | `JWT_SECRET='<32+ chars>' DATABASE_URL='sqlite:///./.codex-test-tmp/qa.db' .venv/bin/pytest -q backend/tests/test_extraction_router.py -k invalid_session` | Unknown asset/session returns 404 and writes no metadata | Test output plus no-write assertion |
| QA-07 | Malformed workspace input | `JWT_SECRET='<32+ chars>' DATABASE_URL='sqlite:///./.codex-test-tmp/qa.db' .venv/bin/pytest -q backend/tests/test_workspace_router.py -k malformed` | Malformed or unkeyed document inspection returns 422 | Test output plus response detail |
| QA-08 | Offline mode with no backend request | `QT_QPA_PLATFORM=offscreen .venv/bin/pytest -q desktop_app/tests/test_api_client.py -k offline` | Manual offline mode returns a typed failure without attempting HTTP | Test output plus request-count assertion |
| QA-09 | Shared environment and launcher contract | `.venv/bin/pytest -q tests/test_configuration_contract.py desktop_app/tests/test_backend_manager.py` | Root `.env`, SQLite local default, port 8001, and launcher defaults agree | Test output plus static contract assertions |

## Runtime and release-owner checks

These rows require a running process, browser/device, target deployment, or
provider account. They are not closed by the local pytest matrix.

| ID | Scenario | Command or procedure | Pass condition | Owner |
| --- | --- | --- | --- | --- |
| QA-10 | Full local route and asset smoke | `bash scripts/test-deployment.sh http://127.0.0.1:8080` | Root, legacy redirects, retained paths, content types, and assets match the canonical policy | Engineering |
| QA-11 | Local deployed claim probe | `.venv/bin/python tools/test_deployed_surface.py --base-url http://127.0.0.1:8080` | Root marker, JavaScript content types, and retired claims pass locally | Engineering |
| QA-12 | Browser accessibility and narrow viewport | Start `serve.py`, use Browser Daemon, inspect keyboard path and narrow viewport | Main landmark, skip link, labels, focus path, and primary CTA remain usable | Product and QA |
| QA-13 | Hosted deployment smoke | `bash scripts/test-deployment.sh https://signkit.work` and `.venv/bin/python tools/test_deployed_surface.py --base-url https://signkit.work --json` | Target host has canonical root, redirects, JavaScript assets, and current markers | Release owner |
| QA-14 | Hosted extraction migration and recovery | Apply Alembic head to the target database, run `tools/run_extraction_hosted_smoke.py`, attach receipts and rollback evidence | Migration, authenticated upload/select/process/export/delete, replay, and recovery pass on the real topology | Engineering and ops |
| QA-15 | Provider purchase and entitlement recovery | Configure a real product ID or controlled sandbox, purchase, verify, revoke/refund, and retry | Provider receipt maps to the entitlement contract and support can recover the account | Commercial owner |

## Known limits and release interpretation

- The local matrix proves code-path behavior only. It does not prove a clean
  install on macOS, Windows, or Linux, a signed package, a hosted migration, a
  real purchase, or legal approval.
- The public hosted probe remains a release blocker while `signkit.work`
  serves the older root/redirect/content-type state. Record the exact probe
  output in the release review rather than weakening the gate.
- EXIF coverage now includes all eight values in the desktop loader. A full
  visual device pass is still required for camera files with vendor-specific
  metadata and for high-DPI rendering.
- The local backend defaults to SQLite for development. Hosted or multi-user
  deployment requires PostgreSQL configuration, migrations, backup/rollback
  evidence, and operator ownership.
- Entitlement storage is provider-neutral. It is not evidence of a configured
  Gumroad/Dodo product, controlled purchase, refund webhook, or production
  activation flow.
