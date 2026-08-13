# Canonical public-surface addendum

Date: 2026-08-12
Status: Current operating truth

The historical landing and A/B documents in this directory describe earlier
route behavior. They are preserved for decision history and asset recovery.
They no longer describe the production route contract.

Current truth:

- `/` and `index.html` are the only public acquisition and checkout surface.
- `/root`, `/buy`, `/purchase`, `/gum`, `/new`, `/web/live`, and retained HTML
  variants redirect to `/`.
- Checkout is owned by `web/live/js/checkout-config.js` and
  `web/live/js/checkout.js`.
- Public claims are governed by `docs/launch_claims/registry.md`.
- Local and deployed route authorities must pass
  `tools/audit_public_surface.py --strict`.
- The current live deployment is not yet aligned; use
  `docs/review/production_surface_mismatch_2026-08-12.md` for the release
  closure path.

Use [`docs/launch_claims/public_surface_map.md`](../launch_claims/public_surface_map.md),
[`docs/BRAND_NARRATIVE_CONTRACT.md`](../BRAND_NARRATIVE_CONTRACT.md), and
[`docs/PUBLIC_SURFACE_QA_MATRIX.md`](../PUBLIC_SURFACE_QA_MATRIX.md) for current
implementation and release decisions.
