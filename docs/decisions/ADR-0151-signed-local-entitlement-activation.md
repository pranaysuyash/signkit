# ADR-0151: Signed local entitlement activation

Date: 2026-08-13
Status: Accepted for the local product slice; provider fulfilment remains open
Owners: Product and release engineering

## Decision

SignKit uses a local-first, fail-closed entitlement boundary:

- A paid grant is represented by `EntitlementReceipt` and its signed fields,
  not by the shape, length, email, or persistence of a license key.
- The receipt payload is canonical JSON signed with Ed25519. The desktop app
  may contain public verification keys, but never a provider API token or
  signing secret.
- The signed receipt owns the plan and add-on grants. Unsigned outer JSON
  fields cannot promote a customer from Trial to Starter, Team, or Business.
- A verified receipt can be used locally. A receipt in `OFFLINE_GRACE` requires
  an explicit future expiry. Revoked, refunded, disputed, chargebacked,
  expired, unknown, malformed, unsigned, and unknown-key receipts fail closed.
- Local activation is idempotent by `activation_id`, with a provider/product/
  sale fallback for receipts that do not provide one. Replaying the same
  activation returns the existing local record. A different second entitlement
  is rejected until an explicit account/device policy exists.
- Later signed lifecycle states use `reconcile_receipt`. The update must keep
  the activation identity and be newer than the stored signed state, so a
  refund, revocation, dispute, chargeback, expiry, or restoration cannot be
  spoofed or rolled back by replaying an older active receipt. An inactive
  receipt cannot be installed as the first entitlement.
- The local license file is a cache of normalized evidence, not the source of
  truth. A key-only record may remain for migration and support visibility but
  cannot unlock a paid feature.
- The old `pranay@example.com` test path is accepted only when
  `SIGNKIT_LICENSE_TEST_MODE=1` is explicitly set in a development/test
  process. It is not production purchase evidence and is not enabled by the
  packaged defaults.
- The desktop activation dialog accepts a signed receipt payload, not an
  arbitrary key. Provider-specific checkout and receipt delivery remain
  external adapters around this boundary.

## Why

The product direction is local-first document work with an optional hosted
metadata control plane. A mandatory hosted license check would couple local
document work to an unverified deployment and make privacy and availability
claims stronger than the evidence. An arbitrary local key would make a paid
claim unverifiable and make refunds or revocation impossible to explain.

The signed receipt preserves local operation while giving support and release
systems one stable object to inspect, replay, revoke, and migrate.

## Explicit non-claims

This ADR does not claim that a provider is configured, that a Dodo or Gumroad
product ID exists, that a controlled purchase has completed, or that refunds,
webhooks, support recovery, or device limits are operational. Those are
provider and release gates tracked by `L0-02`, `L2-03`, `QA-15`, and `RECON-09`.

It also does not make local feature gating tamper-proof against a modified
binary. The public key prevents an ordinary user from manufacturing a receipt;
artifact signing, packaging, and distribution controls remain separate gates.

## Validation

The local slice is covered by receipt canonicalization and Ed25519 verification,
unknown/malformed/unsigned/revoked/expired fail-closed, receipt-owned plan and
add-on, same-activation replay, different-entitlement conflict, legacy-key,
signed lifecycle reconciliation, stale rollback rejection, and
development-test-mode regression tests. The evidence is Tier 2 local
code/test evidence, not provider-flow, hosted, real-purchase, refund, or
production-release evidence.

## Revisit triggers

Revisit this ADR when a provider is selected, a product ID is configured, an
activation/device/account policy is approved, the provider requires a different
signature scheme, or hosted account recovery becomes a supported product flow.
The replacement must preserve the fail-closed boundary, replay identity,
receipt-owned grants, and explicit offline/revocation policy.

## Update log

- 2026-08-13: promoted the local-first signed-receipt contract from the
  provider-neutral scaffold into the enforced local activation boundary. No
  provider or deployment claim was added.
- 2026-08-14: added monotonic local signed lifecycle reconciliation for
  revocation, refund, dispute, chargeback, expiry, and restoration states. No
  provider delivery or hosted activation claim was added.
