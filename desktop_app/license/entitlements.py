"""Provider-neutral entitlement and receipt primitives.

This module owns the local shape of a verified purchase. It does not call a
provider, embed a provider secret, or decide whether a product is configured.
Provider adapters must map their response into this contract before storage.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class EntitlementState(Enum):
    """State used by feature gates after provider response normalization."""

    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    OFFLINE_GRACE = "offline_grace"
    REVOKED = "revoked"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    CHARGEBACKED = "chargebacked"
    EXPIRED = "expired"


_PROVIDER_STATE_MAP = {
    "active": EntitlementState.VERIFIED,
    "paid": EntitlementState.VERIFIED,
    "valid": EntitlementState.VERIFIED,
    "verified": EntitlementState.VERIFIED,
    "chargeback": EntitlementState.CHARGEBACKED,
    "chargebacked": EntitlementState.CHARGEBACKED,
    "dispute": EntitlementState.DISPUTED,
    "disputed": EntitlementState.DISPUTED,
    "expired": EntitlementState.EXPIRED,
    "invalid": EntitlementState.REVOKED,
    "not_found": EntitlementState.REVOKED,
    "refunded": EntitlementState.REFUNDED,
    "revoked": EntitlementState.REVOKED,
}


def map_provider_state(provider_state: str) -> EntitlementState:
    """Map a provider response label without allowing unknown states to grant access."""

    normalized = str(provider_state or "").strip().lower().replace("-", "_")
    return _PROVIDER_STATE_MAP.get(normalized, EntitlementState.UNVERIFIED)


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


@dataclass(frozen=True)
class EntitlementReceipt:
    """Persistable purchase evidence used by the local feature gate."""

    provider: str
    product_id: str
    state: EntitlementState = EntitlementState.UNVERIFIED
    sale_id: Optional[str] = None
    order_number: Optional[str] = None
    email: Optional[str] = None
    activation_id: Optional[str] = None
    verified_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    offline_grace_until: Optional[datetime] = None

    def is_usable(self, *, now: Optional[datetime] = None) -> bool:
        """Return whether this receipt can grant access at the supplied instant."""

        if not self.provider.strip() or not self.product_id.strip():
            return False
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        if self.state is EntitlementState.VERIFIED:
            return True
        expiry = self.offline_grace_until
        if expiry is not None and expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return (
            self.state is EntitlementState.OFFLINE_GRACE
            and expiry is not None
            and expiry > current
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the receipt without provider response payloads or secrets."""

        return {
            "provider": self.provider,
            "product_id": self.product_id,
            "state": self.state.value,
            "sale_id": self.sale_id,
            "order_number": self.order_number,
            "email": self.email,
            "activation_id": self.activation_id,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "last_checked_at": self.last_checked_at.isoformat() if self.last_checked_at else None,
            "offline_grace_until": (
                self.offline_grace_until.isoformat() if self.offline_grace_until else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Any) -> "EntitlementReceipt":
        """Restore a receipt defensively, defaulting unknown state to unverified."""

        if not isinstance(data, dict):
            raise ValueError("entitlement receipt must be an object")
        try:
            state = EntitlementState(str(data.get("state", "unverified")).strip().lower())
        except ValueError:
            state = EntitlementState.UNVERIFIED
        return cls(
            provider=_optional_string(data.get("provider")) or "",
            product_id=_optional_string(data.get("product_id")) or "",
            state=state,
            sale_id=_optional_string(data.get("sale_id")),
            order_number=_optional_string(data.get("order_number")),
            email=_optional_string(data.get("email")),
            activation_id=_optional_string(data.get("activation_id")),
            verified_at=_parse_datetime(data.get("verified_at")),
            last_checked_at=_parse_datetime(data.get("last_checked_at")),
            offline_grace_until=_parse_datetime(data.get("offline_grace_until")),
        )


def _optional_string(value: Any) -> Optional[str]:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


__all__ = ["EntitlementReceipt", "EntitlementState", "map_provider_state"]
