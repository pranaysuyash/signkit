"""Sensitivity tests for provider-neutral entitlement receipts."""

from __future__ import annotations

from datetime import datetime, timezone

from desktop_app.license.entitlements import (
    EntitlementReceipt,
    EntitlementState,
    map_provider_state,
)
from desktop_app.license.storage import load_license, save_license


def test_verified_receipt_round_trips_and_is_usable() -> None:
    receipt = EntitlementReceipt(
        provider="gumroad",
        product_id="product-123",
        sale_id="sale-456",
        order_number="order-789",
        email="buyer@example.com",
        state=EntitlementState.VERIFIED,
        verified_at=datetime(2026, 8, 13, tzinfo=timezone.utc),
    )

    restored = EntitlementReceipt.from_dict(receipt.to_dict())

    assert restored == receipt
    assert restored.is_usable(now=datetime(2026, 8, 13, tzinfo=timezone.utc)) is True


def test_revoked_provider_states_are_not_usable() -> None:
    assert map_provider_state("refunded") is EntitlementState.REFUNDED
    assert map_provider_state("chargebacked") is EntitlementState.CHARGEBACKED
    assert map_provider_state("unknown-provider-state") is EntitlementState.UNVERIFIED

    receipt = EntitlementReceipt(
        provider="gumroad",
        product_id="product-123",
        state=EntitlementState.REFUNDED,
    )
    assert receipt.is_usable() is False


def test_offline_grace_requires_a_future_expiry() -> None:
    receipt = EntitlementReceipt(
        provider="gumroad",
        product_id="product-123",
        state=EntitlementState.OFFLINE_GRACE,
        offline_grace_until=datetime(2026, 8, 14, tzinfo=timezone.utc),
    )

    assert receipt.is_usable(now=datetime(2026, 8, 13, tzinfo=timezone.utc)) is True
    assert receipt.is_usable(now=datetime(2026, 8, 15, tzinfo=timezone.utc)) is False


def test_storage_preserves_receipt_and_fails_closed_for_unverified_receipt(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("desktop_app.license.storage._config_dir", lambda: str(tmp_path))
    receipt = EntitlementReceipt(
        provider="gumroad",
        product_id="product-123",
        state=EntitlementState.UNVERIFIED,
    )

    save_license(key="legacy-key", email="buyer@example.com", entitlement=receipt)
    loaded = load_license()

    assert loaded is not None
    assert loaded.entitlement == receipt
    assert loaded.is_valid() is False
