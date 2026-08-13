# Landing Deployment Process (Canonical Root)

## Current production contract (2026-08-02)

`/` is the only public SignKit landing route and serves the repository-root
`index.html` with HTTP 200. Cloudflare Pages remains the deployment platform;
the build output directory and every Wrangler publish command must be `.`.

The historical variant files remain in the repository for review only. Cloudflare
Pages must permanently redirect each extensionless, trailing-slash, and explicit
HTML form below to `/` with HTTP 301:

- `/root`, `/root/`, `/root.html`
- `/buy`, `/buy/`, `/buy.html`
- `/purchase`, `/purchase/`, `/purchase.html`
- `/gum`, `/gum/`, `/gum.html`
- `/test-variants`, `/test-variants/`, `/test-variants.html`

The retained alternative entrypoints also redirect to `/` when requested
directly: `/web/live/`, `/web/live/index.html`, `/web/new_landing_page/`,
`/web/new_landing_page/index.html`, `/web/cloud_workspace/`, and
`/web/cloud_workspace/index.html`. Their supporting assets remain available to
the files that need them; they are not second acquisition surfaces.

The policy also covers retained HTML under `deploy_dist/`, `docs/`,
`web/archives/`, `web/backups/`, and `web/concepts/` with wildcard redirects.
The route contract test inventories project HTML files, excluding virtual
environments and the canonical `index.html`/`404.html`, so a new artifact
cannot silently become a second public claim surface.

`web/live/js/checkout-config.js` owns the single public checkout configuration.
Only a valid `pdt_` Dodo product ID enables Dodo. An absent or malformed ID means
Dodo controls are unavailable and Gumroad is the actionable primary provider.
When Dodo is configured, it is primary and Gumroad remains an explicit fallback.
Do not add a second checkout config or make a disabled provider appear purchasable.

Before any publish, run:

```bash
./.venv/bin/pytest -q tests/test_landing_surface_contract.py
bash scripts/test-local-landing.sh
bash -n scripts/test-local-landing.sh scripts/test-deployment.sh
```

After a production publish, run `bash scripts/test-deployment.sh https://signkit.work`.
That production smoke test proves only HTTP routing and content types, not payment.

### Required Tier 3 payment gate before enabling Dodo

Static tests and route smoke tests are not purchase proof. Before setting a live
Dodo product ID, a controlled Tier 3 purchase/delivery/activation/retry/refund
run must prove the exact deployed surface: successful payment, receipt and
download delivery, desktop licence activation, cancellation/provider-error
handling, a safe duplicate or retry without a second entitlement, Gumroad fallback
availability, and the documented refund path with the resulting entitlement state.
Record the provider transaction references, delivery evidence, activation result,
retry result, and refund result in the release handoff. The release owner must not
claim Dodo is live until that gate passes.

### Anything else?

No. Legacy pages are intentionally preserved in the checkout but are no longer a
public route family; route tests and CI protect that boundary.

## Historical multi-page instructions (superseded 2026-08-02)

The following snapshot is retained to explain the former A/B setup. It must not
be used as active deployment guidance.

## Goal
Deploy a **static multi-page** marketing site with clean URLs and 4 A/B variants:

- `/root` → `root.html` (control)
- `/buy` → `buy.html` (embedded checkout)
- `/purchase` → `purchase.html` (SaaS landing)
- `/gum` → `gum.html` (redirect)

Supporting pages:

- `/` → `index.html` (entry + optional traffic split via `AUTO_SPLIT`)
- `/test-variants` → `test-variants.html` (QA dashboard)
- `/robots.txt` and `/sitemap.xml` must be real files at the site root.

## Source Of Truth
The deployable landing site is the **repo root**:

- `index.html`, `root.html`, `buy.html`, `purchase.html`, `gum.html`, `test-variants.html`
- `robots.txt`, `sitemap.xml`, `404.html`
- assets referenced by the HTML (notably `assets/` and `web/live/`)

## Cloudflare Pages Settings (Required)
In Cloudflare Pages project settings:

- **Framework preset:** None
- **Build command:** (empty)
- **Build output directory:** `/` (root)
- **Single-page application (SPA) fallback:** **OFF**
  - If SPA fallback is ON, unknown paths (and sometimes `sitemap.xml`) can incorrectly return HTML instead of proper file content.

Cloudflare handles extensionless URLs natively:

- `/purchase.html` → `/purchase` (canonical)
- `/test-variants.html` → `/test-variants` (canonical)

## Local QA
Run a local smoke test (serves files and checks the expected pages exist):

```bash
chmod +x scripts/test-local-landing.sh
./scripts/test-local-landing.sh
```

## Production QA
Smoke-test the deployed site:

```bash
chmod +x scripts/test-deployment.sh
./scripts/test-deployment.sh https://signkit.work
```

This validates:

- All variant routes return HTTP 200
- `robots.txt` is `text/plain`
- `sitemap.xml` is XML and starts with `<?xml`

## CI
GitHub Actions runs landing smoke tests via `.github/workflows/landing-smoke.yml`.
