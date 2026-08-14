# Claim registry provenance proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Evidence scope: canonical-root claim source-control contract

## Result

The canonical root claim registry now records a full source commit for every
registered claim family. `tests/test_launch_claim_registry.py` verifies that:

- the registry has one provenance value for every claim ID;
- the canonical wording snapshot equals the latest Git commit touching
  `index.html`;
- every row provenance value is a full 40-character commit identifier; and
- every row identifier exists as a Git commit in the checkout.

The focused registry suite passed `17` checks. The existing registry binding
checks still require one marker, one row, one enforcing test, and one evidence
tier per canonical claim.

## Boundary

This closes the local source-provenance portion of `L2-06`. It does not prove
that the hosted page matches the canonical source, that a payment provider is
configured or fulfils an order, or that legal reviewers have approved every
customer-facing statement. Those remain separate release and product gates.

## Source paths

- `docs/launch_claims/registry.md`
- `tests/test_launch_claim_registry.py`
- `index.html`
- `docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`
- `docs/QA_RESULTS.md`
