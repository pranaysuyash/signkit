"""Sensitivity tests for provider-neutral entitlement receipts."""

from __future__ import annotations

from datetime import datetime, timezone

from desktop_app.license.entitlements import (
    EntitlementReceipt,
    EntitlementState,
    map_provider_state,
)
from desktop_app.license.storage import load_license, save_license


def test_verified_receipt_round_trips_and_is_usable(signed_receipt) -> None:
    receipt = EntitlementReceipt(
        provider="gumroad",
        product_id="product-123",
        activation_id="activation-456",
        sale_id="sale-456",
        order_number="order-789",
        email="buyer@example.com",
        state=EntitlementState.VERIFIED,
        plan_id="starter",
        key_id="test-key",
        verified_at=datetime(2026, 8, 13, tzinfo=timezone.utc),
    )
    signature, public_key = signed_receipt(
        provider=receipt.provider,
        product_id=receipt.product_id,
        activation_id=receipt.activation_id,
        sale_id=receipt.sale_id,
        order_number=receipt.order_number,
        email=receipt.email,
        state=receipt.state,
        plan_id=receipt.plan_id,
        key_id=receipt.key_id,
        verified_at=receipt.verified_at,
    )

    restored = EntitlementReceipt.from_dict(signature.to_dict())

    assert restored == signature
    assert restored.is_usable(
        now=datetime(2026, 8, 13, tzinfo=timezone.utc), public_key=public_key
    ) is True


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


def test_offline_grace_requires_a_future_expiry(signed_receipt) -> None:
    receipt, public_key = signed_receipt(
        state=EntitlementState.OFFLINE_GRACE,
        offline_grace_until=datetime(2026, 8, 14, tzinfo=timezone.utc),
    )

    assert receipt.is_usable(
        now=datetime(2026, 8, 13, tzinfo=timezone.utc), public_key=public_key
    ) is True
    assert receipt.is_usable(
        now=datetime(2026, 8, 15, tzinfo=timezone.utc), public_key=public_key
    ) is False


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


def test_unsigned_verified_receipt_is_not_usable() -> None:
    receipt = EntitlementReceipt(
        provider="gumroad",
        product_id="product-123",
        activation_id="activation-123",
        state=EntitlementState.VERIFIED,
    )

    assert receipt.is_state_usable() is False
    assert receipt.is_usable() is False
