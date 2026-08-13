"""Regression coverage for composable commercial entitlements."""

import json
import base64

from desktop_app import config
from desktop_app.license import storage


def test_starter_license_can_receive_workflow_automation_add_on(
    monkeypatch, tmp_path, signed_receipt
) -> None:
    """A paid module augments a base plan without promoting the customer to Team."""

    license_path = tmp_path / "license.json"
    monkeypatch.setattr(storage, "_license_path", lambda: str(license_path))

    receipt, public_key = signed_receipt(
        plan_id="starter",
        add_ons=(storage.LicenseAddon.WORKFLOW_AUTOMATION.value,),
        activation_id="starter-addon-activation",
    )
    monkeypatch.setenv(
        "SIGNKIT_ENTITLEMENT_PUBLIC_KEYS",
        json.dumps({"test-key": base64.urlsafe_b64encode(public_key).decode("ascii")}),
    )
    storage.save_license("starter:customer-key", entitlement=receipt)

    loaded = storage.load_license()
    assert loaded is not None
    assert loaded.tier is storage.LicenseTier.STARTER
    assert loaded.has_add_on(storage.LicenseAddon.WORKFLOW_AUTOMATION)
    assert loaded.has_feature(storage.LicenseFeature.WORKFLOW_AUTOMATION)
    assert json.loads(license_path.read_text(encoding="utf-8"))["add_ons"] == ["workflow_automation"]


def test_unknown_persisted_add_on_is_ignored(monkeypatch, tmp_path) -> None:
    """Old and malformed local license payloads remain safe to load."""

    license_path = tmp_path / "license.json"
    license_path.write_text(
        json.dumps({"key": "starter:customer-key", "tier": "starter", "add_ons": ["unknown"]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(storage, "_license_path", lambda: str(license_path))

    loaded = storage.load_license()
    assert loaded is not None
    assert loaded.add_ons == set()
    assert not loaded.has_feature(storage.LicenseFeature.WORKFLOW_AUTOMATION)


def test_workflow_automation_offer_uses_its_own_checkout_configuration(monkeypatch) -> None:
    """The add-on is routable without treating it as the Team base plan."""

    monkeypatch.setenv("DODO_PRODUCT_ID_WORKFLOW_AUTOMATION", "pdt_AutomationPilot")

    offer = config.get_pricing_addon("workflow_automation")
    assert offer is not None
    assert config.get_pricing_offer_id(offer.addon_id) == offer.addon_id
    assert config.get_purchase_url(offer.addon_id) == "https://checkout.dodopayments.com/buy/pdt_AutomationPilot"
