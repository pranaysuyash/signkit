# Claim-surface disposition proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Evidence scope: local strict-audit warning inventory

## Result

The strict public-surface auditor intentionally retains warnings for historical
HTML pages and historical documents. Those warnings now have a path-by-path
disposition register at `docs/launch_claims/retained_surface_dispositions.md`.
`tests/test_claim_surface_dispositions.py` executes the auditor and verifies
that every current warning path appears in that register.

The six retained HTML warning surfaces are classified as historical and
redirect-only. The 30 documentation paths are classified as preserved
historical archive material. Neither category is a current claim authority.

## Boundary

This closes only the local warning-inventory portion of `L1-07`. It does not
prove that a deployed provider serves the canonical JavaScript, that retained
HTML is excluded from a release artifact, that redirects return the required
status in production, or that legal and hosted claims have been approved.

## Source paths

- `tools/audit_public_surface.py`
- `docs/launch_claims/retained_surface_dispositions.md`
- `tests/test_claim_surface_dispositions.py`
- `docs/review/claim_surface_inventory_2026-08-13.md`
