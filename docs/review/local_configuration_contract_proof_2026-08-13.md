# Local configuration contract proof

Date: 2026-08-13
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Scope: local environment template, backend settings, launcher defaults, and active documentation
Evidence tier: Tier 2 local configuration contract

## Verified contract

- `API_BASE_URL` defaults to `http://127.0.0.1:8001`.
- `BACKEND_HOST` defaults to `127.0.0.1`.
- `BACKEND_PORT` defaults to `8001`.
- local `DATABASE_URL` defaults to `sqlite:///./signature_extractor.db`.
- `.env.example` documents the required JWT replacement step and distinguishes
  local defaults, optional integrations, and hosted-only configuration.
- `backend.app.config.Settings` honors an explicit `DATABASE_URL` and resolves
  the shared repository `.env` path.
- `scripts/run-backend-dev.sh` uses configurable `BACKEND_HOST` and
  `BACKEND_PORT` values with the same local defaults.

## Evidence

```text
./.venv/bin/python -m pytest \
  tests/test_configuration_contract.py \
  tests/test_local_product_stack_contract.py -q
6 passed
```

The active local setup references the same port and SQLite defaults in
`.env.example`, `docs/README.md`, `desktop_app/README.md`, and
`scripts/run-backend-dev.sh`. Remaining `8000` matches are historical status,
strategy, or launch notes, or millisecond timing constants. They are not
current local runtime instructions and remain preserved for provenance.

## Boundary

This closes the local configuration/documentation consistency slice represented
by `L0-07` and `L1-03`. It does not prove hosted environment configuration,
target-database migration, production secret management, or deployment smoke.
