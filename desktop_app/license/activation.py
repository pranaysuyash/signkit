"""Provider-neutral local activation and replay policy."""

from __future__ import annotations

from dataclasses import dataclass
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

    if not verify_receipt(receipt, public_keys=public_keys):
        raise ActivationError("entitlement receipt signature is not trusted")
    if not receipt.is_state_usable():
        raise ActivationError("entitlement receipt is not active at activation time")

    existing = load_license()
    if existing and existing.entitlement is not None:
        current_identity = _activation_identity(existing.entitlement)
        incoming_identity = _activation_identity(receipt)
        if current_identity != incoming_identity:
            raise ActivationError("a different entitlement is already activated")
        return ActivationResult(existing, replayed=True)

    save_license(
        key=receipt.activation_id or receipt.sale_id or receipt.order_number or receipt.product_id,
        email=receipt.email,
        tier=receipt.plan_id,
        add_ons=receipt.add_ons,
        entitlement=receipt,
    )
    activated = load_license()
    if activated is None or activated.entitlement != receipt:
        raise ActivationError("activated entitlement could not be reloaded")
    return ActivationResult(activated, replayed=False)


__all__ = ["ActivationError", "ActivationResult", "activate_receipt"]
