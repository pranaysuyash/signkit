# SignKit public demo asset manifest

Date: 2026-08-13  
Owner: Product Ops / Web Platform  
Status: Review required before public promotion

## Purpose

This manifest records the evidence role, visual state, source, and known risks
for assets used by the canonical landing page. Public screenshots are product
claims. They must have a known source, an authorization decision, and a
replacement trigger.

## Current asset inventory

| Asset family | Current role | Dimensions | Evidence state | Risk / action |
| --- | --- | --- | --- | --- |
| `step1-upload.*` | Historical upload/extraction opening | 1200x767 PNG; responsive WebP derivatives | Product workflow capture | Confirm whether the upload state is still current before adding to the canonical story |
| `step2-select.*` | Current extraction selection proof | 1200x767 PNG; responsive WebP derivatives | Tier 4 runtime capture exists | Prepare an authorized public demo document and record approval |
| `step3-clean.*` | Intended cleaned-result proof | 1200x767 PNG; responsive WebP derivatives | Current file is visually a PDF-signing state, not a cleaned-result state | P1: replace with a real cleaned transparent result or rename the semantic role and copy together |
| `step4-sign.*` | PDF placement/signing proof | 1200x767 PNG; responsive WebP derivatives | Tier 4 runtime capture exists | Prepare an authorized public demo document and record approval |
| `signkit_icon_*` | Brand identity/favicon | multiple sizes | Static asset | Keep aligned with the canonical brand mark |

## Integrity observations

The following file families currently share content hashes:

```text
step3-clean.png and step4-sign.png
step3-clean-1200.webp and step4-sign-1200.webp
step3-clean-768.webp and step4-sign-768.webp
step3-clean-380.webp and step4-sign-380.webp
```

Visual inspection shows the shared image is a PDF-signing screen with a
signature placed on a sample document. This is not a safe basis for calling the
asset a cleaned extraction result. The duplicate is preserved for recovery and
is not deleted in this pass.

## Authorization fields required for each replacement

Before a screenshot becomes current public evidence, record:

- capture date and application/release version;
- source workflow and exact state represented;
- demonstration document provenance and permission to publish;
- whether the visible signature is synthetic, authorized, or redacted;
- whether personal, customer, or test data is visible;
- reviewer and approval date;
- target asset paths and responsive derivative hashes;
- replacement trigger when the UI, workflow, or claim changes.

## Public evidence rules

1. A screenshot may prove a current capability only when its state is current
   and the release bundle supports the named workflow.
2. A concept or generated screen must be visibly labelled `Illustrative`,
   `Concept`, or equivalent and must not be used as shipped-product proof.
3. A screenshot does not prove privacy, performance, customer adoption, or
   regulated-signature guarantees.
4. The public page must use the semantic state name that matches the visible
   workflow. Do not describe a PDF-signing frame as a cleaned extraction frame.
5. When a screenshot is replaced, update this manifest and the public-surface
   release record in the same change.

## Closure commands

After asset replacement or role correction:

```bash
file web/live/assets/screenshots/*
shasum -a 256 web/live/assets/screenshots/*
python3 tools/audit_public_surface.py --strict
python3 -m pytest tests/test_launch_claim_registry.py tests/test_public_surface_audit.py -q
```

Then run the browser screenshot and responsive checks described in
`docs/PUBLIC_SURFACE_QA_MATRIX.md`, and attach the current screenshot paths and
hashes to the release record.

## Decision and remaining gap

Decision: preserve the existing assets, do not silently delete or overwrite
them, and treat the `step3-clean` semantic mismatch as a P1 release-quality
finding. The closure path is either to provide a genuine cleaned-result asset,
or to change the page's state label and copy to match the current PDF-signing
capture, with the claim registry and visual evidence reviewed together.

## Anything else?

Yes. The current page's `srcset` work is useful only when each derivative is a
faithful rendition of the same semantic state. Responsive variants are not
independent design references. Hash and state checks must remain part of the
asset release gate.
