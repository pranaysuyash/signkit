# Local entitlement lifecycle reconciliation proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Evidence scope: local signed-receipt lifecycle only

## Result

The local entitlement boundary now has a separate `reconcile_receipt` path for
later signed lifecycle states. It verifies the receipt signature, requires the
same activation identity, orders updates by signed issue/verification/check
timestamps, and refuses an older active receipt from rolling back a revocation.
Refunded, revoked, disputed, chargebacked, expired, or otherwise unusable
states remain stored as signed evidence but fail closed for paid feature access.
An inactive receipt cannot be installed as a first entitlement.

## Evidence

- Focused entitlement suite: `./.venv/bin/python -m pytest
  tests/test_entitlement_activation.py tests/test_entitlement_receipts.py
  tests/test_license_storage_operations.py tests/test_license_dialog_contract.py
  -q` passed `15` tests.
- The regression tests cover initial signed activation, signed refund/revocation
  reconciliation, paid-feature denial after the update, stale active rollback
  rejection, inactive-first-state rejection, tamper rejection, replay, and
  different-entitlement conflict.
- Full canonical suite: `541 passed, 4 skipped`.

## Boundary and open gates

This is a local cryptographic and persistence contract. It does not prove a
Gumroad, Dodo, or other provider adapter, a configured product ID, refund or
webhook delivery, support recovery, account/device policy, hosted activation,
or production payment operations. Those remain open under `L0-02`, `QA-15`,
`L2-03`, and `RECON-09`.

## Source paths

- `desktop_app/license/activation.py`
- `desktop_app/license/__init__.py`
- `tests/test_entitlement_activation.py`
- `docs/decisions/ADR-0151-signed-local-entitlement-activation.md`
- `docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`
- `docs/QA_RESULTS.md`
