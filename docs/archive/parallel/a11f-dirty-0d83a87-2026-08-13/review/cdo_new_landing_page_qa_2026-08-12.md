# CDO New Landing Page QA

Date: 2026-08-12
Surface: `web/new_landing_page/index.html`
Mode: solo operator with agents; product, brand, and customer experience treated as one system

## Scope decision

This pass applies the Chief Design Officer audit to the explicitly named new page, not the old root landing page. Deployment, route promotion, and commit work are intentionally outside this task.

## Baseline findings

- The new page loaded with no console errors and no missing local assets in the browser check.
- Lighthouse baseline was Accessibility 100, SEO 100, Best Practices 77, and Agentic Browsing 100 mobile / 86 desktop.
- The page used absolute or high-risk claims: 100% offline, never uploading, lifetime pricing, free updates forever, and a provider-specific security badge.
- The page had six `href="#"` footer placeholders, creating false affordances in the post-purchase trust layer.
- Purchase links bypassed the shared checkout state and did not expose provider fallback behavior or checkout intent telemetry.

## Completed tasks

- Reframed the narrative around local-first document workflows and a clear checkout boundary.
- Removed unsupported release, privacy, lifetime, forever-update, and provider-security wording.
- Added shared checkout configuration and runtime to the new page.
- Added provider-aware primary and fallback purchase links for navigation, hero, and pricing.
- Added purchase-delivery context at the checkout boundary without adding legal or certification work.
- Replaced placeholder footer links with real in-page destinations for purchase, workflow, privacy boundary, and return navigation.
- Added a contract test covering copy, checkout wiring, placeholder links, landmark structure, and image alt text.
- Added a topology section connecting the current Local product to explicitly labelled Cloud and Hybrid planned directions.
- Added a topology contract covering the browser workspace boundary and the page's future-capability language.

## Task ledger

| Task | Status | Evidence |
| --- | --- | --- |
| Audit the new page as a product/brand/CX system | Complete | Browser snapshot, network audit, Lighthouse, this record |
| Align claims with the current SignKit trust contract | Complete | Updated page copy and contract test |
| Make checkout behavior provider-aware | Complete | Shared checkout scripts and provider data attributes |
| Remove dead-end navigation | Complete | Footer now resolves to page sections |
| Preserve solo-operator scope | Complete | No legal, certification, deployment, or commit task added |
| Re-run browser QA after the edit | Complete | No console errors, local assets 200, no overflow, checkout fallback interaction observed |

## Remaining local work

There is no remaining local implementation work in this slice. Any future content change should update this ledger and the governed brand narrative together.

## Final verification

- Focused current suite: 27 passed across the new-page contract, topology contract, governed claim registry, landing surface, and public-surface audit.
- Static checks: Python compilation and Node syntax checks passed.
- Browser: no console errors; all page-local assets and shared checkout scripts returned 200.
- Checkout: `gumroad-primary` state observed; Dodo primary links were correctly disabled with an explanatory configuration destination; Gumroad fallback was actionable and captured the expected `pricing-fallback` intent.
- Responsive: no horizontal overflow at the browser's mobile and desktop resize checks; one `main` landmark and zero `href="#"` placeholders.
- Product direction: Local is labelled available now; Cloud and Hybrid are labelled planned direction; pricing describes signature extraction and PDF placement rather than a vague recurring-operations promise.
- Lighthouse after edit: Accessibility 100, SEO 100, Best Practices 77, Agentic Browsing 97 mobile / 99 desktop. Best Practices remains affected by third-party analytics behavior, not the new page's product or navigation contract.

## Evidence boundary

Static claims are Tier 1 until the focused test passes. Browser load, console, network, responsive, and checkout interaction checks are Tier 4 evidence when observed after the edit. This document does not claim public route promotion or production availability.
