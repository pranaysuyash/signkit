# Entitlement provider decision refresh

Date: 2026-08-14
Scope: primary-source provider research for the SignKit entitlement decision
Status: research complete, product-owner selection still required

## Executive finding

The local signed `EntitlementReceipt` and monotonic lifecycle reconciliation
remain the correct product boundary regardless of provider. Provider choice
changes the adapter and operational evidence required around that boundary; it
must not replace the local receipt contract with an arbitrary key check or a
browser-held provider secret.

## Primary-source comparison

| Question | Gumroad | Dodo Payments | SignKit implication |
| --- | --- | --- | --- |
| Software license primitive | Official license keys are intended for software. Verification uses `product_id`, `license_key`, and optional `increment_uses_count`. | License Key is an Entitlement with activation limit, expiry, and customer instructions. | The adapter must normalize provider identity, product identity, activation identity, plan, and lifecycle state into a signed local receipt. |
| Revocation signal | The verification response exposes `refunded`, `disputed`, `dispute_won`, `chargebacked`, and related subscription timestamps. Gumroad says license enforcement is up to the creator. | License grants are disabled on refund, subscription cancellation/expiry, and manual revoke; the documented lifecycle includes grant revocation events. | A provider adapter must map every provider terminal or suspended state to a signed `reconcile_receipt` update and retain the fail-closed rule. |
| Activation model | Gumroad documents usage counting and multi-seat license behavior; the creator controls how verification calls enforce usage. | Dodo documents public activate, validate, and deactivate endpoints plus activation limits and per-key instances. | A device/account/seat policy is still a product decision. Do not infer it from the provider API. |
| Secret boundary | Gumroad API access tokens are account secrets and must stay server-side. | Dodo’s one-time integration requires merchant API credentials and a webhook secret; its public license endpoints do not require an API key. | Browser and packaged clients must not receive provider secrets. Public validation still needs an explicit privacy, availability, and offline policy. |
| Operational path | Configure a product with license keys, acquire the product ID, verify a controlled purchase, and test refund/dispute handling. | Create a merchant account and product entitlement, configure API/webhook credentials, test one-time and subscription lifecycle, and verify grant events. | Neither provider is configured or production-proven in this checkout. The P0 remains open. |

## Decision inputs still requiring product-owner authority

1. Select Gumroad or Dodo as the initial provider, or explicitly defer
   provider activation while shipping local early access.
2. Approve one-time Personal semantics, major-version update policy, and any
   future subscription or team-seat model.
3. Approve activation policy: one device, a bounded device count, account
   recovery, transfer, and support override behavior.
4. Approve the privacy and availability posture for provider validation,
   including offline grace and what happens after a refund, dispute,
   chargeback, or provider outage.
5. Provide the configured product ID, sandbox credentials, webhook endpoint and
   secret, refund policy, and an authorized controlled purchase or test event.

Until those inputs exist, SignKit must retain the current qualified claims:
local signed-receipt code evidence is not provider activation, purchase,
refund, webhook, hosted, or production payment evidence.

## Sources

- [Gumroad license keys](https://gumroad.com/help/article/76-license-keys)
- [Gumroad API application and access-token guidance](https://gumroad.com/help/article/280-create-application-api)
- [Gumroad refund handling](https://gumroad.com/help/article/47-how-to-refund-a-customer)
- [Dodo Payments license keys](https://docs.dodopayments.com/features/license-keys)
- [Dodo Payments entitlements](https://docs.dodopayments.com/features/entitlements/introduction)
- [Dodo Payments one-time integration prerequisites](https://docs.dodopayments.com/developer-resources/integration-guide)

## Evidence boundary

This is primary-source research captured on 2026-08-14. Documentation describes
provider capabilities, not SignKit configuration or operational success. A
future implementation must add secret-safe adapter tests, signature or
webhook verification, idempotent event handling, controlled sandbox evidence,
support recovery evidence, and customer-safe claim review.
