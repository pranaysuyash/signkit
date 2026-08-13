
import base64
import json

from desktop_app.license.storage import LicenseFeature, LicenseValidator, OperationType, save_license, load_license


def test_workflow_automation_gated_by_license_tier(tmp_path, monkeypatch, signed_receipt):
    """Workflow automation should require team/business tier features."""
    monkeypatch.setattr("desktop_app.license.storage._config_dir", lambda: str(tmp_path))

    team_receipt, public_key = signed_receipt(plan_id="team", activation_id="team-activation")
    monkeypatch.setenv(
        "SIGNKIT_ENTITLEMENT_PUBLIC_KEYS",
        json.dumps({"test-key": base64.urlsafe_b64encode(public_key).decode("ascii")}),
    )
    save_license(key="team-lic-abc", email="ops@example.com", tier="team", entitlement=team_receipt)

    # Team tier unlocks workflow automation.
    assert LicenseValidator.is_operation_allowed(OperationType.WORKFLOW_AUTOMATION)[0] is True

    # Starter tier should still fail for workflow automation.
    starter_receipt, _ = signed_receipt(plan_id="starter", activation_id="starter-activation")
    save_license(
        key="starter-lic",
        email="ops@example.com",
        tier="starter",
        entitlement=starter_receipt,
    )
    assert LicenseValidator.is_operation_allowed(OperationType.WORKFLOW_AUTOMATION)[0] is False

    # Legacy aliases should remain compatible with existing callers.
    assert LicenseValidator.is_operation_allowed(LicenseFeature.WORKFLOW_AUTOMATION)[0] is False


def test_legacy_key_shape_never_grants_paid_access(tmp_path, monkeypatch):
    monkeypatch.setattr("desktop_app.license.storage._config_dir", lambda: str(tmp_path))

    save_license(key="LICENSE-KEY-123", tier="business")

    loaded = load_license()
    assert loaded is not None
    assert loaded.tier.value == "trial"
    assert loaded.is_valid() is False
    assert LicenseValidator.is_operation_allowed(OperationType.EXPORT)[0] is False


def test_test_license_requires_explicit_development_opt_in(tmp_path, monkeypatch):
    monkeypatch.setattr("desktop_app.license.storage._config_dir", lambda: str(tmp_path))
    save_license(key="pranay@example.com")
    assert load_license().is_valid() is False

    monkeypatch.setenv("SIGNKIT_LICENSE_TEST_MODE", "1")
    save_license(key="pranay@example.com")
    assert load_license().is_valid() is True
