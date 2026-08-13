# ADR-0150: Fail Closed for Hosted Database Configuration and Protect Local PII Paths

Date: 2026-08-13
Status: accepted for the current local and hosted-contract code paths
Owner: Product and engineering

## Context

The recovered parallel security work identified three related boundaries in
the backend configuration and local filesystem path layer:

1. `backend/app/config.py` carried real-looking default database credentials.
2. The import-time settings singleton made environment changes invisible to
   tests and some long-lived process seams.
3. User-data, upload, and selection-sidecar directories relied only on the
   process umask, even though they contain signature images and metadata.

These are not hosted-readiness claims. They are local code guarantees that
reduce accidental credential use and cross-account local disclosure while the
separate migration, deployment, and provider gates remain open.

## Decision

- Remove hardcoded database username/password defaults. A production
  configuration without a complete `DATABASE_URL` must provide both explicit
  credentials and otherwise fail closed.
- Keep local development able to use an explicit SQLite `DATABASE_URL` without
  Postgres component credentials.
- Provide `get_settings()` and `reload_settings()` as a narrow, testable
  configuration seam. Existing process-wide settings behavior remains the
  default; production code should not mutate settings at runtime.
- Set owner-only permissions on POSIX user-data and upload/selection-sidecar
  directories (`0700`) and selection metadata files (`0600`). Permission
  hardening is best-effort on platforms where POSIX modes are unavailable.

## Alternatives rejected

### Keep example credentials for local convenience

Rejected. A default credential is indistinguishable from an intended
credential at the configuration boundary and can leak into a deployment or
operator receipt.

### Require Postgres credentials in every environment

Rejected. The local product path intentionally supports isolated SQLite
runtime data. The production fail-closed rule preserves that boundary without
making local development depend on hosted infrastructure.

### Rely only on the process umask

Rejected. Umask is ambient and can be permissive. Explicit owner-only modes
make the local PII boundary observable and testable.

## Evidence and acceptance

- `backend/tests/test_config_and_path_security.py` covers absent default
  credentials, production failure, complete-URL configuration, reload seam,
  owner-only data directories, and owner-only selection sidecars.
- Targeted security and extraction contract run: `13 passed` at Tier 2/S1.
- The full canonical root run after integration passes `475 passed, 4 skipped`
  locally. The optional PyMuPDF and Qt event-loop skips remain explicit.
- The random audit that led to this work is preserved at
  `docs/audits/random_document_audit_AUTO_DETECTION_ML_2026-08-13.md`; its
  findings are treated as hypotheses until confirmed by current code/tests.

## Remaining boundary and rollback

This decision does not claim a live production database, migration, hosted
deployment, secret-manager, or multi-user OS verification. Those remain under
`L0-03`, `L0-04`, `L0-05`, and `L0-09` in the product-owner backlog. Rollback
means reverting this ADR's code group while preserving the tests and backlog
record, but doing so would knowingly restore weaker credential and local-PII
defaults and requires explicit review.
