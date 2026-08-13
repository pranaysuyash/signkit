# SignKit claim-surface inventory

Date: 2026-08-13  
Status: Open remediation register  
Owner: Product, Web Platform, Legal, and release engineering

## Purpose and method

This inventory separates canonical product claims from historical or reachable
surfaces. It was produced by inspecting the current checkout, the route
authorities, the claim registry, release workflows, legal documents, and the
deployed public surface. It is an analysis artifact, not proof that any claim is
legally approved.

The search covered `index.html`, desktop onboarding copy, `root.html`,
`buy.html`, `purchase.html`, `gum.html`, `web/live/index.html`,
`web/new_landing_page/index.html`, legal and policy documents, and release
workflow notes. Broad historical marketing documents were counted separately
because text presence alone does not prove customer reachability.

## Classification

| Surface | Current state | Evidence | Required disposition |
| --- | --- | --- | --- |
| Root `/` from `index.html` | Canonical source; local static contract passes | `tools/audit_public_surface.py --strict`; claim registry; 22 focused tests | Keep qualified wording and require deployed probe before release |
| `/index.html`, `/root`, `/buy`, `/purchase`, `/gum`, `/new`, retained workspace paths | Intended redirect-only surfaces; live deployment currently serves several as `200` or `308` | `_redirects`, `serve.py`, `tools/test_deployed_surface.py`, live probe 2026-08-13 | Block release until deployed redirects match the route contract |
| `root.html`, `buy.html`, `purchase.html`, `gum.html`, retained landing variants | Historical source files containing direct checkout links and absolute offline/ownership wording | `tools/audit_public_surface.py --strict --json` warnings and direct inspection | Classify as archive-only, scrub claims, or remove from the deployed artifact |
| Desktop onboarding | Source copy now uses a qualified local-processing boundary; product/legal confirmation remains open | `desktop_app/views/onboarding_dialog.py:118` and addendum below | Confirm wording against checkout, update, support, and optional hosted boundaries |
| `web/live/index.html` | Retained legacy page with “No cloud uploads” and absolute document locality wording | `web/live/index.html:680` | Keep unreachable, scrub, or label historical; never use as current proof |
| `docs/PRIVACY_POLICY.md` and `docs/TERMS_OF_SERVICE.md` | Documentation contains absolute no-cloud/offline wording | `docs/PRIVACY_POLICY.md:49`, `docs/TERMS_OF_SERVICE.md:119` | Reconcile against actual checkout, updates, enquiry, and optional hosted boundaries |
| `legal/PRIVACY_POLICY.md` and `legal/EULA.md` | Newer qualified local/cloud boundary exists, but terminology differs from docs | `legal/PRIVACY_POLICY.md:49`, `legal/PRIVACY_POLICY.md:110`, `legal/EULA.md` | Choose one canonical legal source and label historical documents |
| Release workflows | Source release notes now use qualified local-processing wording; tagged artifact claim scan and workflow proof remain open | `.github/workflows/build-all-platforms.yml` and release ledger spec | Run the tagged workflow and retain claim-scan and artifact-ledger evidence |

## Current findings

1. The local canonical root does not contain the retired absolute phrases and
   is covered by the claim registry.
2. The deployed root currently serves the older landing page. The live page is
   therefore customer-facing evidence of claim drift, not historical-only text.
3. The static auditor reports retained-page warnings but exits successfully.
   This is intentional for historical inventory, but it is insufficient while
   the deployment still exposes those paths.
4. The search found 33 files containing “100% offline” and 57 files containing
   “no cloud upload” across the scoped product and documentation trees. Most are
   historical documentation, so reachability must be determined from the route
   and release artifact rather than from text counts alone.

## Tasks derived from this inventory

These tasks are tracked in `docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`:

- `L0-13`: deployed root and checkout asset probe, in progress.
- `L1-07`: classify and reconcile all reachable, retained, legal, support,
  email, and release surfaces, in progress.
- `L1-08`: align operator-facing local/hosted vocabulary and recovery states,
  in progress.
- `L0-05` and `L0-14`: attach claim and artifact evidence to the release ledger,
  in progress.

## Closure criteria

The inventory closes only when:

- every source is labeled current, redirect-only, historical, or forbidden;
- all current claims have a registry row, implementation path, evidence tier, and
  enforcing check;
- current legal and customer copy uses qualified wording consistent with the
  actual local, checkout, update, enquiry, and hosted boundaries;
- the release artifact contains no unintended historical public pages;
- the deployed root and asset probe passes; and
- product/legal review decisions are recorded for PDF signing, authenticity,
  privacy, licensing, refunds, and optional connected services.

## Evidence boundary

This inventory is Tier 1 static analysis plus Tier 5 production-like observation
of the current live site. It does not establish legal approval, provider
fulfilment, or user comprehension.

## Addendum (2026-08-13): current checkout and desktop wording

The desktop onboarding wording listed above was qualified in
`desktop_app/views/onboarding_dialog.py`; it now describes core extraction and
PDF work as local by default and names checkout, updates, and support as
optional network boundaries. The release workflow wording was likewise
qualified and now depends on the artifact ledger gate. The original rows are
retained as historical findings from the audit pass.

The live probe still shows the older deployed root and HTML fallbacks for
checkout assets, so these source changes are not production proof. The retained
`web/live/index.html`, `root.html`, and older policy documents remain open for
qualification, archival, or an explicit legal/product disposition under
`L1-07`.

## Addendum (2026-08-13): local browser runtime observation

Using the repository Browser Daemon and Accessibility Auditor guidance against
`http://127.0.0.1:8080/`, the canonical page loaded with the expected title and
checkout assets, one `main`, one `h1`, a focusable skip link, and no unresolved
`aria-labelledby`, `aria-describedby`, or `aria-controls` references. The
browser console contained no errors during the observation. This is Tier 4
local runtime evidence for the inspected viewport, not WCAG certification,
screen-reader conformance, or deployed-surface proof.

## Addendum (2026-08-13): release claim gate binding

The tagged release workflow now runs the dependency-free canonical
public-surface auditor before generating the artifact ledger. A static contract
test verifies that the claim gate appears before the ledger command in
`.github/workflows/build-all-platforms.yml`. This prevents a release job from
creating a checksum ledger while silently skipping source claim parity. It does
not replace the external deployed probe or product/legal review.
