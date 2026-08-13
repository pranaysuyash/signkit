"""Contract tests for the canonical local receipt activation boundary."""

import base64
import json
from dataclasses import replace

import pytest

from desktop_app.license.activation import ActivationError, activate_receipt
from desktop_app.license.storage import load_license


def _configure_key(monkeypatch, public_key: bytes) -> None:
    monkeypatch.setenv(
        "SIGNKIT_ENTITLEMENT_PUBLIC_KEYS",
        json.dumps({"test-key": base64.urlsafe_b64encode(public_key).decode("ascii")}),
    )


def test_activation_persists_signed_grant_and_replays_without_mutation(
    monkeypatch, tmp_path, signed_receipt
) -> None:
    monkeypatch.setattr("desktop_app.license.storage._config_dir", lambda: str(tmp_path))
    receipt, public_key = signed_receipt(plan_id="team", activation_id="activation-replay-001")
    _configure_key(monkeypatch, public_key)

    first = activate_receipt(receipt)
    second = activate_receipt(receipt)

    assert first.replayed is False
    assert second.replayed is True
    assert second.license_info.entitlement == receipt
    assert load_license() == first.license_info


def test_activation_rejects_tampered_receipt(monkeypatch, tmp_path, signed_receipt) -> None:
    monkeypatch.setattr("desktop_app.license.storage._config_dir", lambda: str(tmp_path))
    receipt, public_key = signed_receipt(plan_id="starter")
    _configure_key(monkeypatch, public_key)
    tampered = replace(receipt, plan_id="business")

    with pytest.raises(ActivationError, match="signature"):
        activate_receipt(tampered)


def test_activation_rejects_a_different_second_entitlement(
    monkeypatch, tmp_path, signed_receipt
) -> None:
    monkeypatch.setattr("desktop_app.license.storage._config_dir", lambda: str(tmp_path))
    first, public_key = signed_receipt(activation_id="activation-one")
    second, _ = signed_receipt(activation_id="activation-two", sale_id="sale-two")
    _configure_key(monkeypatch, public_key)
    activate_receipt(first)

    with pytest.raises(ActivationError, match="different entitlement"):
        activate_receipt(second)
