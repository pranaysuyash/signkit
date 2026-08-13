# SignKit Sales Operating System

**Baseline date:** 2026-07-22
**Status:** Initial operating system; prospect and conversion evidence still to be built.

## Commercial thesis

SignKit should be sold as a private desktop workflow for preparing, extracting,
organizing, and signing sensitive PDFs—not as a generic cloud e-signature platform.
The strongest initial promise is simple and verifiable: keep working files on the
customer's computer, reuse cleaned signatures, and complete ordinary PDF work without
a subscription.

The long-term product research describes a broader local-first document-execution
workstation with selectable trust modes. Sales must stay within the currently shipped
capability boundary until those stronger evidence and regulated-signature paths are
implemented and reviewed.

## Initial ICP priority

| Priority | Segment | Trigger/problem | Likely buyer | First offer angle |
| --- | --- | --- | --- | --- |
| 1 | Small legal teams | Repeated confidential PDFs, messy scans, missing signature pages | Managing attorney, paralegal, legal operations | Private local preparation and reusable signature assets |
| 2 | CA/accounting/tax practices | Repetitive client packs, approvals, sensitive financial documents | Practice owner, tax manager, senior assistant | Batch preparation without uploading client files |
| 3 | Real-estate transaction teams | Revisions, initials, disclosures, closing packets | Broker, transaction coordinator, conveyancer | Faster local completion and fewer missing fields |
| 4 | HR/people operations | Offer, NDA, onboarding, and exit documents | HR operations lead, founder | Local handling for sensitive employee documents |
| 5 | Document-service teams | Scan cleanup, asset extraction, repeated output work | Operations manager | High-volume local extraction and deterministic export |

## Qualification rubric

Score each dimension from 0 to 2:

- **Workflow frequency:** occasional (0), monthly (1), daily/weekly (2).
- **Sensitivity:** ordinary (0), confidential (1), regulated/client-sensitive (2).
- **Current friction:** no clear pain (0), workaround (1), active tool/problem search (2).
- **Local/offline fit:** cloud-first requirement (0), neutral (1), explicit local/privacy need (2).
- **Buyer access:** no public route (0), general inquiry route (1), identifiable business buyer route (2).

Start active outreach at 7/10 or higher. Keep 4–6 as nurture/research. Do not spend
time on rows below 4 until the segment thesis changes.

## Funnel stages

`discovered → qualified → approved → contacted → replied → discovery → trial/demo →
purchase → retained/referral`

Every active row needs a next action and a next-action date. A reply without a clear
workflow problem is not an opportunity. A purchase without activation feedback is not
yet a validated segment.

## First campaign design

Run one segment at a time with 20–30 carefully researched organizations. The first
campaign should test the problem and message, not maximize volume.

Suggested first test: small legal teams that handle confidential PDFs and routinely
reuse signature images or complete repeated document packs.

Success signals to capture:

- positive reply rate;
- workflow pain described in the prospect's own words;
- demo/trial acceptance;
- purchase rate and time to purchase;
- objection categories;
- refund/support friction;
- referral or second-user interest.

Do not use unsupported market-size or conversion projections as targets. Establish a
baseline from the first measured campaign.

## Tracking contract

`PROSPECT_PIPELINE.csv` is the canonical lightweight tracker for now. Every row should
include `source_url`, `fit_score`, `status`, `last_touch_at`, `next_action_at`, and
`evidence_note`. If the pipeline becomes multi-user or requires automation, migrate
this schema to a proper CRM without creating a second manually maintained truth source.

## Operating cadence

- **Research:** add and source-check a small batch of prospects.
- **Review:** approve the next batch and the exact message before outreach.
- **Follow-up:** record every response, opt-out, objection, and next step.
- **Learning:** update the research log weekly with observed language and segment
  evidence.
- **Conversion:** inspect checkout clicks, purchase events, activation, refunds, and
  support before changing the offer.

## Boundaries

- No claim that an image signature is universally legally binding.
- No claim that SignKit replaces DocuSign, Adobe Sign, a DSC, a qualified trust service,
  a notary, or a jurisdiction-specific filing portal.
- No subscription, team, regulated-signature, or integration offer until it exists and
  has passed the relevant product and legal-review gates.
- No automated cold outreach, scraping behind access controls, or purchased lists.
