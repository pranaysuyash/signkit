"""Provider-neutral entitlement and receipt primitives.

This module owns the local shape of a verified purchase. It does not call a
provider, embed a provider secret, or decide whether a product is configured.
Provider adapters must map their response into this contract before storage.
"""

from __future__ import annotations

import base64
import binascii
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


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


def _datetime_value(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value else None


def _decode_base64(value: str) -> Optional[bytes]:
    """Decode standard or URL-safe base64 without accepting malformed data."""

    try:
        encoded = value.encode("ascii")
        encoded += b"=" * (-len(encoded) % 4)
        return base64.b64decode(encoded, altchars=b"-_", validate=True)
    except (UnicodeEncodeError, ValueError, binascii.Error):
        return None


def _decode_public_key(value: bytes | str) -> Optional[bytes]:
    if isinstance(value, bytes):
        return value
    normalized = str(value or "").strip()
    if not normalized:
        return None
    decoded = _decode_base64(normalized)
    if decoded:
        return decoded
    try:
        return bytes.fromhex(normalized)
    except ValueError:
        return None


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
    plan_id: str = "trial"
    add_ons: tuple[str, ...] = ()
    sale_id: Optional[str] = None
    order_number: Optional[str] = None
    email: Optional[str] = None
    activation_id: Optional[str] = None
    issuer: Optional[str] = None
    key_id: Optional[str] = None
    signature: Optional[str] = None
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    offline_grace_until: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Normalize collection fields before they become signed evidence."""

        normalized_add_ons = tuple(
            sorted(
                {
                    str(value).strip().lower()
                    for value in self.add_ons
                    if str(value).strip()
                }
            )
        )
        object.__setattr__(self, "add_ons", normalized_add_ons)
        object.__setattr__(self, "provider", str(self.provider or "").strip())
        object.__setattr__(self, "product_id", str(self.product_id or "").strip())
        object.__setattr__(self, "plan_id", str(self.plan_id or "trial").strip().lower() or "trial")

    def signing_dict(self) -> dict[str, Any]:
        """Return the canonical receipt fields covered by the signature."""

        return {
            "schema_version": 1,
            "provider": self.provider,
            "product_id": self.product_id,
            "state": self.state.value,
            "plan_id": self.plan_id,
            "add_ons": list(self.add_ons),
            "sale_id": self.sale_id,
            "order_number": self.order_number,
            "email": self.email,
            "activation_id": self.activation_id,
            "issuer": self.issuer,
            "key_id": self.key_id,
            "issued_at": _datetime_value(self.issued_at),
            "expires_at": _datetime_value(self.expires_at),
            "verified_at": _datetime_value(self.verified_at),
            "last_checked_at": _datetime_value(self.last_checked_at),
            "offline_grace_until": _datetime_value(self.offline_grace_until),
        }

    def canonical_payload(self) -> bytes:
        """Return deterministic bytes for provider or test-key signing."""

        return json.dumps(
            self.signing_dict(), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")

    def has_valid_signature(self, public_key: bytes | str | None) -> bool:
        """Verify the receipt with a pinned Ed25519 public key."""

        if not self.key_id or not self.signature or public_key is None:
            return False
        key_bytes = _decode_public_key(public_key)
        signature_bytes = _decode_base64(self.signature)
        if key_bytes is None or signature_bytes is None:
            return False
        if len(key_bytes) != 32 or len(signature_bytes) != 64:
            return False
        try:
            Ed25519PublicKey.from_public_bytes(key_bytes).verify(
                signature_bytes, self.canonical_payload()
            )
        except (InvalidSignature, ValueError, TypeError):
            return False
        return True

    def is_state_usable(self, *, now: Optional[datetime] = None) -> bool:
        """Check lifecycle state and time bounds without cryptographic trust."""

        if (
            not self.provider
            or not self.product_id
            or not self.activation_id
            or self.issued_at is None
            or self.verified_at is None
        ):
            return False
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        expiry = self.offline_grace_until
        if expiry is not None and expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        receipt_expiry = self.expires_at
        if receipt_expiry is not None and receipt_expiry.tzinfo is None:
            receipt_expiry = receipt_expiry.replace(tzinfo=timezone.utc)
        issued_at = self.issued_at
        if issued_at.tzinfo is None:
            issued_at = issued_at.replace(tzinfo=timezone.utc)
        verified_at = self.verified_at
        if verified_at.tzinfo is None:
            verified_at = verified_at.replace(tzinfo=timezone.utc)
        if issued_at > current or verified_at > current:
            return False
        if receipt_expiry is not None and receipt_expiry <= current:
            return False
        if self.state is EntitlementState.VERIFIED:
            return True
        return (
            self.state is EntitlementState.OFFLINE_GRACE
            and expiry is not None
            and expiry > current
        )

    def is_usable(
        self,
        *,
        now: Optional[datetime] = None,
        public_key: bytes | str | None = None,
    ) -> bool:
        """Return whether signed evidence can grant access at the supplied instant."""

        return self.is_state_usable(now=now) and self.has_valid_signature(public_key)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the receipt without provider response payloads or secrets."""

        return {
            "schema_version": 1,
            "provider": self.provider,
            "product_id": self.product_id,
            "state": self.state.value,
            "plan_id": self.plan_id,
            "add_ons": list(self.add_ons),
            "sale_id": self.sale_id,
            "order_number": self.order_number,
            "email": self.email,
            "activation_id": self.activation_id,
            "issuer": self.issuer,
            "key_id": self.key_id,
            "signature": self.signature,
            "issued_at": _datetime_value(self.issued_at),
            "expires_at": _datetime_value(self.expires_at),
            "verified_at": _datetime_value(self.verified_at),
            "last_checked_at": _datetime_value(self.last_checked_at),
            "offline_grace_until": _datetime_value(self.offline_grace_until),
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
        raw_add_ons = data.get("add_ons")
        if isinstance(raw_add_ons, str):
            add_ons = (raw_add_ons,)
        elif isinstance(raw_add_ons, (list, tuple, set)):
            add_ons = tuple(raw_add_ons)
        else:
            add_ons = ()
        return cls(
            provider=_optional_string(data.get("provider")) or "",
            product_id=_optional_string(data.get("product_id")) or "",
            state=state,
            plan_id=_optional_string(data.get("plan_id")) or "trial",
            add_ons=add_ons,
            sale_id=_optional_string(data.get("sale_id")),
            order_number=_optional_string(data.get("order_number")),
            email=_optional_string(data.get("email")),
            activation_id=_optional_string(data.get("activation_id")),
            issuer=_optional_string(data.get("issuer")),
            key_id=_optional_string(data.get("key_id")),
            signature=_optional_string(data.get("signature")),
            issued_at=_parse_datetime(data.get("issued_at")),
            expires_at=_parse_datetime(data.get("expires_at")),
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
