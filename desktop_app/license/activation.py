"""Provider-neutral local activation and replay policy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

from .entitlements import EntitlementReceipt
from .storage import LicenseInfo, load_license, save_license
from .verification import verify_receipt


class ActivationError(ValueError):
    """Raised when a receipt cannot become the local entitlement."""


@dataclass(frozen=True)
class ActivationResult:
    license_info: LicenseInfo
    replayed: bool


def _activation_identity(receipt: EntitlementReceipt) -> str:
    """Return the stable identity used for local idempotency."""

    if receipt.activation_id:
        return receipt.activation_id
    return ":".join(
        (
            receipt.provider,
            receipt.product_id,
            receipt.sale_id or receipt.order_number or "",
        )
    )


def _has_receipt_identity(receipt: EntitlementReceipt) -> bool:
    """Require lifecycle fields before accepting a signed state update."""

    return bool(
        receipt.provider
        and receipt.product_id
        and receipt.activation_id
        and receipt.issued_at is not None
        and receipt.verified_at is not None
    )


def _as_utc(value: datetime) -> datetime:
    """Compare provider timestamps consistently even when legacy data is naive."""

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _receipt_version(receipt: EntitlementReceipt) -> tuple[datetime, datetime, datetime]:
    """Return the monotonic version tuple for a signed lifecycle update."""

    assert receipt.issued_at is not None
    assert receipt.verified_at is not None
    checked_at = receipt.last_checked_at or receipt.verified_at
    return (_as_utc(receipt.issued_at), _as_utc(receipt.verified_at), _as_utc(checked_at))


def _store_receipt(
    receipt: EntitlementReceipt,
    *,
    public_keys: Mapping[str, bytes | str] | None,
    allow_inactive_update: bool,
) -> ActivationResult:
    """Verify, order, and persist one signed local entitlement state."""

    if not verify_receipt(receipt, public_keys=public_keys):
        raise ActivationError("entitlement receipt signature is not trusted")
    if not _has_receipt_identity(receipt):
        raise ActivationError("entitlement receipt is missing lifecycle identity")
    if not allow_inactive_update and not receipt.is_state_usable():
        raise ActivationError("entitlement receipt is not active at activation time")

    existing = load_license()
    if (
        allow_inactive_update
        and (existing is None or existing.entitlement is None)
        and not receipt.is_state_usable()
    ):
        raise ActivationError("inactive receipt cannot be installed without an active entitlement")
    if existing and existing.entitlement is not None:
        current = existing.entitlement
        if _activation_identity(current) != _activation_identity(receipt):
            raise ActivationError("a different entitlement is already activated")
        if current == receipt:
            return ActivationResult(existing, replayed=True)
        if _receipt_version(receipt) <= _receipt_version(current):
            raise ActivationError("entitlement receipt update is older than the stored state")

    save_license(
        key=receipt.activation_id or receipt.sale_id or receipt.order_number or receipt.product_id,
        email=receipt.email,
        tier=receipt.plan_id,
        add_ons=receipt.add_ons,
        entitlement=receipt,
    )
    updated = load_license()
    if updated is None or updated.entitlement != receipt:
        raise ActivationError("entitlement state could not be reloaded")
    return ActivationResult(updated, replayed=False)


def activate_receipt(
    receipt: EntitlementReceipt,
    *,
    public_keys: Mapping[str, bytes | str] | None = None,
) -> ActivationResult:
    """Install one verified receipt, replaying the same activation safely.

    The local store intentionally supports one active entitlement. A different
    activation is rejected rather than silently replacing a customer's access
    or creating a second source of truth. A future account/device policy can
    replace this explicit boundary with a server-side activation ledger.
    """

    return _store_receipt(
        receipt,
        public_keys=public_keys,
        allow_inactive_update=False,
    )


def reconcile_receipt(
    receipt: EntitlementReceipt,
    *,
    public_keys: Mapping[str, bytes | str] | None = None,
) -> ActivationResult:
    """Apply a newer signed lifecycle state to the current local entitlement.

    This is the local boundary for a future provider adapter's refund,
    revocation, dispute, chargeback, expiry, or restoration notification. It
    never calls a provider and cannot install an inactive receipt as a first
    entitlement. A matching activation identity and strictly newer signed
    timestamps are required, so an old active receipt cannot roll back a local
    revocation.
    """

    return _store_receipt(
        receipt,
        public_keys=public_keys,
        allow_inactive_update=True,
    )


__all__ = ["ActivationError", "ActivationResult", "activate_receipt", "reconcile_receipt"]
