# SignKit public surface map

Date: 2026-08-12
Owner: Product, Web Platform, and Growth

## Canonical rule

`/` is the only public acquisition and checkout entry surface. Its source is
`index.html`, its claim contract is `docs/launch_claims/registry.md`, and its
checkout runtime is `web/live/js/checkout-config.js` plus
`web/live/js/checkout.js`.

The local preview server and the deployed `_redirects` file are intended to
enforce the same rule. The redirect is intentionally visible in the route
contract so query parameters used for attribution are preserved while the page
experience stays canonical. The live deployment must still pass
`tools/test_deployed_surface.py`; the current production snapshot has not yet
been proven to match this repository contract.

Checkout intent telemetry is emitted by that same runtime owner and records
the CTA placement, canonical entry path, and bounded UTM fields. The redirect
contract preserves those query parameters, so acquisition attribution does not
require a variant-specific checkout implementation.

## Retained but non-public paths

The following paths remain in the repository for historical review or asset
recovery. They are not valid acquisition surfaces and must redirect to `/`:

- `/index.html`
- `/root`, `/root.html`
- `/buy`, `/buy.html`
- `/purchase`, `/purchase.html`
- `/gum`, `/gum.html`
- `/test-variants`, `/test-variants.html`
- `/new`
- `/web/live`, `/web/live/`, `/web/live/index.html`
- `/web/new_landing_page`, `/web/new_landing_page/`, `/web/new_landing_page/index.html`
- `/web/cloud_workspace`, `/web/cloud_workspace/`, `/web/cloud_workspace/index.html`

Static assets under `web/live/js/`, `web/live/css/`, and `web/live/assets/`
remain reachable only as dependencies of the canonical root page. They are
not alternate landing pages.

## Change gate

Any new public route must either become the canonical root or be added to both
route authorities and the route-contract test. Any new customer-facing claim
must receive a registry row, a marker in `index.html`, an evidence tier, and an
enforcing test before publication.

The redirect contract is static evidence. A deployed redirect smoke check is
still required before claiming production parity.

## Addendum (2026-08-13): wildcard retained trees

The route authorities also cover retained HTML and generated trees through the
following wildcard rules: `/deploy_dist/*`, `/docs/*.html`,
`/web/archives/*`, `/web/backups/*`, and `/web/concepts/*`. `serve.py` now
matches those same classes locally, so the complete local deployment script
passes. The live deployment remains unproven and currently fails the deployed
probe because those rules and canonical assets have not propagated there.
