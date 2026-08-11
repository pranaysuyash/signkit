# Topology-led SignKit experience review

Date: 2026-07-31  
Status: parallel concept for founder review, not a live-site replacement

## Why this concept exists

The earlier workspace concept was materially better than the rejected theatrical
landing, but its rounded display type, isolated image crops, and shallow product
story still read as a product launch page for a local utility. That is too small
for SignKit's documented product boundary.

This separate concept responds to the current Wayfinder direction:

- SignKit has one canonical product and workflow model, with Local, Cloud, and
  Hybrid as delivery and data-authority choices.
- The desktop local workflow is current product evidence.
- Cloud and Hybrid are future direction, not current availability claims.
- Legal and HR are the high-consequence validation wedge.
- Templates, controlled batch execution, receipts, account operations, and
  adapters are horizontal value surfaces, not a licence to become a generic PDF
  product or DocuSign clone.

## Artifact

`web/concepts/2026-07-31-topology-experience/`

The original rejected exploration and the first job-led workspace concept both
remain untouched. This does not modify `web/live/`.

## Design decisions

1. **Serious typography:** the rounded display face is replaced with a restrained
   editorial serif and a neutral sans. Surfaces are squared, ruled, and
   intentionally spare rather than soft, inflated, or neomorphic.
2. **Screenshots as evidence:** current source-selection and loaded-PDF screens
   are shown as full application frames with explicit captions. They are not
   random decorative cutouts or recreated browser UI.
3. **Current versus direction:** every delivery mode has a visible status.
   Local is available now. Cloud and Hybrid state their unresolved capability,
   authority, identity, sync, and proof requirements.
4. **Scalable narrative:** the page makes the vertical validation wedge,
   horizontal modules, and anti-drift boundaries legible without claiming a
   fully decided public roadmap.

## Browser evidence

Served from the repository root with the project environment:

```sh
./.venv/bin/python -m http.server 4176 --directory .
```

Visual browser inspection passed at `1440×920` and `390×844`:

`http://127.0.0.1:4176/web/concepts/2026-07-31-topology-experience/index.html`

- Tier 4 desktop: serif display treatment, full current desktop screen, and
  Local status were visibly legible.
- Tier 4 mobile: the job-led opening and the full screenshot remained readable
  and did not rely on a desktop-only crop.
- Tier 4 interaction: selecting Cloud updated the accessible tab state and
  panel with direction-only status, Cloud execution, authority, and caveat.
- Browser console: clear after load and interaction.
- Static check: `node --check web/concepts/2026-07-31-topology-experience/app.js` passed.

## Evidence sources

- `Docs/wayfinder/SIGNKIT_SCALING_EXPANSION_WAYFINDER_MAP.md`
- `Docs/wayfinder/tickets/establish-local-execution-web-control-plane-boundary.md`
- `Docs/wayfinder/tickets/define-local-cloud-hybrid-capability-contract.md`
- `Docs/wayfinder/tickets/validate-legal-hr-vertical-wedge.md`
- `Docs/wayfinder/tickets/rank-horizontal-value-surfaces.md`
- Fresh current runtime captures in `Docs/review/assets/`

## Remaining limits and closure path

- This is a strategy-aware experience concept, not approval to publicly market
  Cloud or Hybrid. Keep those labels as direction until the capability contract
  and proof gates close.
- The current source screenshot visibly contains a sample signature and is a
  transparent runtime capture. Before any public release, replace it with a
  deliberately prepared, authorized demonstration document while preserving the
  same actual UI evidence standard.
- The exact Legal or HR packet workflow remains an open validation question.
  It must be researched and tested before vertical-specific customer claims or
  conversion paths are introduced.

## Anything else?

Yes. The landing should remain an expression of the canonical delivery model.
When Cloud or Hybrid implementation begins, its capability matrix and proof
receipts should feed the same page rather than creating another marketing truth.
