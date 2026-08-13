# ADR-0146: Provider-neutral entitlement receipt contract

Date: 2026-08-13
Status: Accepted for staged implementation, provider integration pending
Owners: Product and release engineering

## Decision

Represent a verified purchase locally as a provider-neutral
`EntitlementReceipt`, with an explicit `EntitlementState`. A provider adapter
must normalize its response into this contract before the desktop feature gate
uses it. Unknown states fail closed. A verified receipt may be cached for a
bounded offline grace period only when its expiry is explicit.

The legacy key-only path remains compatibility behavior when no entitlement
receipt is present. It is not treated as purchase evidence and must not be the
basis for claiming provider verification.

## Context

The current storage path accepts a non-empty key with a minimum length and has
a test-license branch. Gumroad research confirms that the application, not
the provider, must own activation, replay, offline grace, and interpretation
of refunded, disputed, and chargebacked responses. A provider-specific client
or a desktop-embedded secret before these boundaries are explicit would create
a second source of truth and make revocation difficult to explain.

## Chosen shape

`desktop_app/license/entitlements.py` defines provider, product, sale/order,
activation, verification timestamps, state, and offline-grace expiry. The
existing `desktop_app/license/storage.py` persists it under `entitlement` and
enforces receipt-backed states through `LicenseInfo.is_valid()`.

## Alternatives considered

- Keep minimum-length key acceptance as the production contract. Rejected:
  it cannot prove a purchase or represent provider revocation.
- Implement a Gumroad client directly in the desktop app. Rejected at this
  stage: it would require handling provider secrets, replay, support recovery,
  and policy changes in a distributed binary.
- Store raw provider responses. Rejected: unnecessary payment/provider data
  increases privacy and migration burden; normalized evidence is sufficient.

## Risks and tradeoffs

- The legacy compatibility path still exists, so release claims must not say
  that all activations are provider-verified.
- Offline grace can extend access after a provider revocation until expiry;
  the product decision must choose the duration and recovery messaging.
- The provider and product ID are not configured, and no controlled purchase
  has been observed. The receipt contract is code evidence, not entitlement
  proof.

## Validation and closure

- Focused receipt and storage tests cover round-trip persistence, unknown
  state fail-closed behavior, revoked states, and offline-grace expiry.
- A future provider adapter must add contract tests for success, 404, timeout,
  malformed response, refund, dispute, chargeback, replay, and recovery.
- Close this ADR only after a configured product ID, a secret-safe provider
  boundary, an idempotent activation record, documented support recovery, and
  a controlled sandbox or real purchase evidence record exist.
