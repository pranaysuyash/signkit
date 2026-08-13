"""Configuration-bound verification for provider-neutral entitlement receipts.

The desktop binary may contain public verification material, but it must never
contain a provider API token or a signing secret. Provider adapters should
deliver a normalized, signed receipt to this boundary. Until a public key is
configured, all receipts remain unusable and the app stays in evaluation mode.
"""

from __future__ import annotations

import base64
import binascii
import json
import os
from typing import Mapping

from .entitlements import EntitlementReceipt


PUBLIC_KEYS_ENV = "SIGNKIT_ENTITLEMENT_PUBLIC_KEYS"
LEGACY_PUBLIC_KEY_ENV = "SIGNKIT_ENTITLEMENT_PUBLIC_KEY"
KEY_ID_ENV = "SIGNKIT_ENTITLEMENT_KEY_ID"


def _decode_key(value: object) -> bytes | None:
    if isinstance(value, bytes):
        return value if len(value) == 32 else None
    normalized = str(value or "").strip()
    if not normalized:
        return None
    try:
        encoded = normalized.encode("ascii")
        encoded += b"=" * (-len(encoded) % 4)
        decoded = base64.b64decode(encoded, altchars=b"-_", validate=True)
        if len(decoded) == 32:
            return decoded
    except (UnicodeEncodeError, ValueError, binascii.Error):
        pass
    try:
        decoded = bytes.fromhex(normalized)
    except ValueError:
        return None
    return decoded if len(decoded) == 32 else None


def load_public_keys(environ: Mapping[str, str] | None = None) -> dict[str, bytes]:
    """Load an explicit keyring without silently inventing trust material."""

    source = os.environ if environ is None else environ
    keyring: dict[str, bytes] = {}
    raw_keyring = str(source.get(PUBLIC_KEYS_ENV, "") or "").strip()
    if raw_keyring:
        try:
            parsed = json.loads(raw_keyring)
        except json.JSONDecodeError:
            parsed = {}
        if isinstance(parsed, dict):
            for key_id, value in parsed.items():
                decoded = _decode_key(value)
                if decoded is not None and str(key_id).strip():
                    keyring[str(key_id).strip()] = decoded

    legacy_key = _decode_key(source.get(LEGACY_PUBLIC_KEY_ENV, ""))
    if legacy_key is not None:
        keyring[str(source.get(KEY_ID_ENV, "default") or "default").strip()] = legacy_key
    return keyring


def verify_receipt(
    receipt: EntitlementReceipt,
    *,
    public_keys: Mapping[str, bytes | str] | None = None,
) -> bool:
    """Verify a receipt against the configured or explicitly supplied keyring."""

    keys = load_public_keys() if public_keys is None else public_keys
    key = keys.get(receipt.key_id or "")
    return receipt.has_valid_signature(key)


__all__ = ["KEY_ID_ENV", "PUBLIC_KEYS_ENV", "verify_receipt", "load_public_keys"]
