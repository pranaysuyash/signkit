# ADR-0145: Canonical public-surface release gate

Status: Accepted for implementation, deployment proof pending
Date: 2026-08-13
Owners: Product, Web Platform, release engineering

## Decision

SignKit has one public acquisition and checkout surface at `/`. The repository
route authorities are `_redirects` for deployment, `serve.py` for local
preview, and the public-surface tests and probes for enforcement.

`/index.html` and retained landing, checkout, experiment, and workspace paths
are legacy paths and must return a root-relative `301` to `/` in the deployed
surface. The canonical root must return `200` HTML. Checkout configuration and
runtime assets must return JavaScript media types and contain their canonical
runtime markers. The deployed root must not contain retired absolute privacy,
offline, or ownership claims.

## Context

The repository already documented this policy in `docs/launch_claims/` and
implemented most of it in `_redirects` and `serve.py`, but the shell deployment
gate expected `/index.html` to return `200`. The deployed site currently serves
old `200` pages for several legacy paths and returns HTML for checkout JavaScript
paths. This allowed static success to coexist with a broken customer-facing
release surface.

## Options considered

1. Keep `/index.html` as a second `200` acquisition surface. Rejected because it
   creates parallel claim and checkout authority.
2. Accept any `2xx`, `3xx`, or content type in the release probe. Rejected because
   it hides route and asset fallback failures.
3. Keep one root surface, enforce the explicit redirect and asset contract, and
   fail the release gate when production diverges. Chosen.

## Consequences

- Local and deployed route behavior must remain synchronized.
- Cloudflare or another host may not silently normalize a required redirect to
  a different status without the release owner deciding and documenting that
  contract change.
- Historical pages may remain in the repository for recovery, but they cannot
  remain customer-reachable with unqualified claims.
- A passing local test remains only Tier 2 evidence until the deployed probe and
  browser/runtime review pass.

## Validation and falsifiers

The decision is falsified if any of the following occurs:

- `/` is not `200` HTML with the `public_surface_boundary` marker.
- A path listed as a legacy redirect does not return `301` to `/` while
  preserving approved query parameters.
- `web/live/js/checkout-config.js` or `web/live/js/checkout.js` returns HTML,
  lacks its canonical marker, or cannot configure the current provider state.
- The deployed root contains an absolute offline, privacy, or ownership claim
  that is not registered and approved.

Required checks:

```bash
python3 tools/audit_public_surface.py --strict
python3 -m pytest -p no:cacheprovider -q tests/test_deployed_surface_probe.py tests/test_public_surface_audit.py tests/test_launch_claim_registry.py
bash scripts/test-deployment.sh https://signkit.work
python3 tools/test_deployed_surface.py --base-url https://signkit.work --json
```

The first two commands are local Tier 2 evidence. The last two require the
release owner to deploy or inspect the live target and provide Tier 3 or higher
evidence.

## Rollback and revisit conditions

Do not publish a surface that fails the gate. If deployment has already changed
the live surface, roll back to the last artifact whose route, claim, and asset
ledger passed. Revisit this decision only if the acquisition topology changes,
the provider boundary changes, or the hosting platform requires a different
redirect contract and the replacement is documented with equivalent enforcement.
