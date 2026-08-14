# Local extraction ownership and recovery smoke proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Evidence scope: disposable local production-like contract only

## Result

The canonical extraction smoke passed from the current `main` checkout:

```text
./.venv/bin/python tools/run_extraction_hosted_smoke.py
status: passed
```

The smoke created a temporary SQLite database, applied every migration through
Alembic head `9c4b7e2d1a6f`, and used temporary upload and region-metadata
directories. No project database, user data, hosted endpoint, or provider was
contacted.

## Checks observed

- Public health response with HTTP 200.
- Registration and login for two users.
- Authenticated owner upload.
- Durable upload replay with the same idempotency key.
- Cross-owner region-selection denial.
- Owner region selection.
- Owner image processing.
- Export archive containing `manifest.json`.
- Owner deletion with complete cleanup status.
- Post-delete audit receipt containing upload, selection, processing, export,
  and delete events.
- Cross-owner deletion denial.

This is Tier 3 local command-execution evidence for the application contract.
It is stronger than a unit-only route test because it exercises migrations,
FastAPI routing, authentication, a temporary database, filesystem writes,
replay, export, cleanup, and audit behavior together.

The reusable subprocess contract at
`tests/test_extraction_hosted_smoke_tool.py` asserts that the smoke reports a
passing health check and the key lifecycle receipts. The dedicated mutation
probe `extraction-smoke-health-gate` killed the deliberately broken health
expectation, so the health assertion is S3-sensitive rather than merely
present in the script. The complete repository mutation manifest passed
`17/17`, including this probe.

## Boundary and remaining gates

The result proves the disposable local application contract only. It does not
prove that the target hosted database has received migration `9c4b7e2d1a6f`,
that the deployed service uses the same code, that production secrets and
retention settings are correct, or that rollback and operator recovery work on
the real deployment topology. Live authenticated smoke, target migration,
hosted public-surface parity, rollback, and production receipt review remain
open under `L0-09`, `L0-03`, `L0-04`, and `RECON-07`.

## Source paths

- `tools/run_extraction_hosted_smoke.py`
- `backend/alembic/versions/e42b7f8c91aa_add_extraction_asset_ownership_receipts.py`
- `backend/alembic/versions/9c4b7e2d1a6f_add_metadata_fields_for_local_document_inspection_receipts.py`
- `backend/app/routers/extraction.py`
- `backend/tests/test_extraction_router.py`
- `backend/tests/test_extraction_hosted.py`
- `tests/test_extraction_hosted_smoke_tool.py`
- `tools/mutation_check.py`
- `docs/QA_RESULTS.md`
- `docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`
