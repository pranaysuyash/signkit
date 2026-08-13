# Dodo-primary checkout and landing redesign — 2026-07-16

## Decision

Use Dodo Payments as SignKit's primary checkout and fulfilment provider for the
one-time Personal licence. Keep Gumroad as a visible but subordinate alternate
checkout. Dodo will provide payment collection, receipt, application downloads,
and licence-key delivery.

The static site uses Dodo's hosted product checkout rather than handling payment
details or calling a secret-bearing API from the browser:

`https://checkout.dodopayments.com/buy/{product_id}`

The public `pdt_...` identifier has one canonical configuration location:
`web/live/js/checkout-config.js`. The desktop app reads the same kind of public
identifier from `DODO_PRODUCT_ID` and falls back explicitly to Gumroad when it is
not configured.

## Why

- Hosted checkout keeps card and payment data outside SignKit's static site.
- Dodo can own the complete purchase-to-delivery outcome instead of leaving an
  unverified custom webhook/download pipeline in the critical path.
- One public configuration seam prevents checkout URLs from drifting across hero,
  pricing, footer, onboarding, menus, and licence dialogs.
- The fallback remains honest and usable during provider migration or outage.

## Landing hierarchy

1. Promise: finish sensitive signed-document work locally.
2. Proof: product UI, supported platforms, and local-processing boundary.
3. Primary conversion: Dodo-hosted one-time purchase.
4. Alternate conversion: Gumroad, labelled as a buyer-selected fallback.
5. Expansion path: recurring document workflows remain a separate enquiry rather
   than competing with the Personal checkout.

## Payment risk and verification contract

Risk class: high, because checkout, licence delivery, refunds, and customer-facing
payment claims are involved.

Before deployment, the owner must:

- create or confirm the live SignKit one-time product in Dodo;
- attach the correct macOS, Windows, and Linux deliverables;
- enable and test licence-key entitlement delivery;
- insert the live `pdt_...` identifier into `checkout-config.js` and deployment config;
- perform a Dodo test-mode purchase and verify receipt, download, licence key,
  cancellation, failure, refund, and duplicate/retry behavior;
- verify the desktop activation path accepts a Dodo-delivered key;
- have the provider/refund/privacy wording reviewed before production publication.

Until those checks pass, the implementation is structurally ready but the Dodo
payment flow is not production-verified.

## Three-pass review outcomes

### Pass 1 — immediate correctness

Centralized provider selection, removed Gumroad-only hero behavior, added Dodo and
fallback affordances, and aligned desktop purchase entry points.

### Pass 2 — architecture

Chose hosted checkout over browser-side API credentials or a new backend payment
route. Preserved the existing one-time licence model and external fulfilment boundary.

### Pass 3 — supervision readiness

Pending the real product identifier and live Dodo transaction evidence. No deployment
or payment-dashboard mutation is claimed by this repository change.
