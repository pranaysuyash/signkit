# Gumroad entitlement contract research

Date: 2026-08-13
Status: Research complete; implementation and provider verification open
Scope: Gumroad fallback provider for SignKit Personal licensing

## Sources

- [Gumroad license keys](https://gumroad.com/help/article/76-license-keys)
- [Gumroad API application access](https://gumroad.com/help/article/280-create-application-api)
- [Gumroad purchase access and license-key delivery](https://gumroad.com/help/article/199-how-do-i-access-my-purchase)

These are external provider facts checked on 2026-08-13. They are not evidence
that SignKit's Gumroad product is configured or that a real SignKit purchase
has completed.

## Confirmed provider behavior

- The license verification API uses `product_id` for products created on or
  after 2023-01-09. A product permalink is not the correct verification input
  for those products.
- Verification accepts `license_key` and an optional
  `increment_uses_count` flag. Launch checks should use `false` unless the
  product policy deliberately treats each check as a use.
- A successful response includes purchase identity and state fields such as
  `sale_id`, `order_number`, `email`, `refunded`, `disputed`, and
  `chargebacked`. The application must decide how those states affect local
  entitlement.
- Gumroad does not enforce license use limits for the creator. SignKit must
  own its activation, device policy, replay behavior, offline grace, and
  revocation interpretation.
- Customers can receive license keys through the receipt, product/download
  page, or a Gumroad license-key lookup flow. Receipt delivery is therefore a
  provider workflow dependency, not proof that the desktop app has been
  activated.
- A Gumroad API access token is secret and must not be placed in the desktop
  binary or browser bundle. If server-side provider management is needed, it
  belongs behind the hosted control plane and requires its own deployment,
  secret, audit, and recovery gates.

## SignKit decision requirements

The current local license store accepts a non-empty key with a minimum length,
and includes a test-license path. That is local gating, not entitlement proof.
Before enabling a hard gate, SignKit must decide:

1. Whether Gumroad license verification is performed directly by the desktop
   client or through an authenticated SignKit service.
2. The configured Gumroad `product_id` and the exact product/version mapping.
3. Whether the first activation creates a receipt bound to an installation,
   account, or email, and how many activations are allowed.
4. What happens for duplicate activation, provider timeout, refunded,
   disputed, chargebacked, disabled, or missing purchases.
5. Whether offline use is allowed after a successful verification, for how
   long, and how revocation is eventually enforced.
6. What support can ask the customer for without collecting unnecessary
   documents or exposing the raw license key.

## Implementation path

- Add a provider-neutral entitlement contract and receipt schema before adding
  a Gumroad-specific client.
- Implement a Gumroad adapter that verifies `product_id` and `license_key`
  with `increment_uses_count=false`, normalizes provider state, and records
  the provider sale/order identifiers without storing unnecessary payment data.
- Make activation idempotent on provider sale/license identity plus the local
  installation policy. Replays must return the existing receipt.
- Keep the local store as a cache of a verified entitlement, not the source of
  truth. A test key must be explicitly test-mode configuration and impossible
  to accept in a production build.
- Add contract tests for success, provider 404, timeout, malformed response,
  refund, dispute, chargeback, replay, and offline grace. Add a sandbox or
  controlled real purchase before closing the release task.

## Evidence boundary

This document is Tier 1 external-source research. It is not Tier 2 code
evidence, Tier 3 provider-flow evidence, or Tier 5 purchase proof.

## Addendum (2026-08-13): provider-neutral contract landed

`desktop_app/license/entitlements.py` now provides the provider-neutral
`EntitlementReceipt` and `EntitlementState` contract. It records provider and
product identity, sale/order identifiers, verification timestamps, activation
identity, and an explicit offline-grace expiry. Unknown provider states map to
`unverified`; refunded, disputed, chargebacked, revoked, and expired states
cannot grant access. The local license store persists this receipt under an
`entitlement` field and fails closed when a receipt is present but not usable.

This is Tier 2 targeted code evidence only. It does not add a Gumroad client,
configure a product ID, verify a real purchase, enforce device activation, or
replace legacy key readability when no receipt exists. The next closure step is
a provider adapter and controlled purchase or sandbox record that exercises
replay, timeout, refund, dispute, chargeback, and offline-grace behavior.

## Addendum (2026-08-13): local-first activation implementation

The local product slice now uses an Ed25519-signed canonical receipt with
receipt-owned plan/add-on grants, explicit public-key configuration, bounded
offline-grace expiry, and a replay-safe `activate_receipt` path. Key-only
records remain readable but fail closed. The development test key requires
`SIGNKIT_LICENSE_TEST_MODE=1` and is not a packaged production default.

This is Tier 2 local code/test evidence. It does not upgrade the Tier 1
provider research into provider-flow evidence: no Gumroad product ID, Dodo
product ID, API adapter, webhook, controlled purchase, refund, device policy,
or support recovery receipt is present.
