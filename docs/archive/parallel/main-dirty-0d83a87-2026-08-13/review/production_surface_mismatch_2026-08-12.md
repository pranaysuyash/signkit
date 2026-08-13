# Production public-surface mismatch

Date: 2026-08-12
Severity: T4 systemic route and transaction trust debt
Owner: Web Platform / Cloudflare deployment owner
Status: Open external blocker

## Evidence

The live `https://signkit.work/` snapshot inspected during this audit still
serves the retired landing narrative: "100% offline," "your files never leave
your computer," direct Gumroad checkout, and "lifetime" language. It does not
contain the current repository's canonical public-surface marker or the
provider-neutral checkout boundary.

The live `/buy` path still returns a checkout-loading page rather than the
repository contract's 301 redirect to `/`. The repository's local handler and
`_redirects` file do return the intended redirect behavior.

The read-only Cloudflare Pages deployment list identifies the production
project as `signkit-landing` with recent deployments on the `landing-page`
branch, all approximately eight months old. The old deployment helper targeted
`main`; the canonical deployment wrapper now defaults to `landing-page` and
allows an explicit `DEPLOY_BRANCH` override.

This means the repository implementation is not production parity. The local
route and claim tests must not be reported as live-site verification.

## Customer and business impact

- Customers can receive stronger privacy, availability, and update promises
  than the governed product surface supports.
- Checkout attribution and provider-state messaging differ by entry path.
- Analytics comparisons based on the current live page do not describe the
  current repository implementation.
- Historical landing documents remain capable of misleading an operator about
  what should be deployed.

## Closure path

1. Confirm the Cloudflare Pages project and branch that serve `signkit.work`.
2. Review the release record and claim/legal approvals.
3. Run `DEPLOY_CONFIRM=signkit-landing DEPLOY_BRANCH=landing-page scripts/deploy_canonical_landing.sh`.
4. Run `python3 tools/test_deployed_surface.py --base-url https://signkit.work`.
5. Recheck root copy, `/buy`, `/purchase`, `/gum`, query preservation, and the
   deployed checkout asset in a browser/device smoke pass.
6. Record deployment ID, timestamp, cache purge status, and rollback target.

Deployment is intentionally not executed by this audit pass because it changes
external production state and requires the release owner to approve the exact
artifact and Cloudflare project.
