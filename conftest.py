"""Shared cryptographic fixtures for entitlement contract tests."""

from __future__ import annotations

import base64
import os
from dataclasses import replace
from datetime import datetime, timezone
from typing import Callable

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from desktop_app.license.entitlements import EntitlementReceipt, EntitlementState

try:
    from PySide6.QtWidgets import QApplication
except ModuleNotFoundError:  # pragma: no cover - environment-specific
    QApplication = None


@pytest.fixture(scope="session")
def qapp():
    """Create the shared offscreen Qt application for root UI contracts."""

    if QApplication is None:
        return None
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def signed_receipt() -> Callable[..., tuple[EntitlementReceipt, bytes]]:
    """Create a receipt and its disposable public key for contract tests."""

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()

    def factory(**overrides: object) -> tuple[EntitlementReceipt, bytes]:
        defaults: dict[str, object] = {
            "provider": "test-provider",
            "product_id": "signkit-personal-v1",
            "state": EntitlementState.VERIFIED,
            "plan_id": "starter",
            "activation_id": "activation-test-001",
            "key_id": "test-key",
            "issuer": "test-issuer",
            "issued_at": datetime(2026, 8, 13, tzinfo=timezone.utc),
            "verified_at": datetime(2026, 8, 13, tzinfo=timezone.utc),
        }
        defaults.update(overrides)
        unsigned = EntitlementReceipt(**defaults)
        signature = base64.urlsafe_b64encode(private_key.sign(unsigned.canonical_payload())).decode(
            "ascii"
        )
        return replace(unsigned, signature=signature), public_key

    return factory
