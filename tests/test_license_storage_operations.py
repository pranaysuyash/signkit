
from desktop_app.license.storage import LicenseFeature, LicenseValidator, OperationType, save_license, load_license


def test_workflow_automation_gated_by_license_tier(tmp_path, monkeypatch):
    """Workflow automation should require team/business tier features."""
    monkeypatch.setattr("desktop_app.license.storage._config_dir", lambda: str(tmp_path))

    save_license(key="team-lic-abc", email="ops@example.com", tier="team")

    # Team tier unlocks workflow automation.
    assert LicenseValidator.is_operation_allowed(OperationType.WORKFLOW_AUTOMATION)[0] is True

    # Starter tier should still fail for workflow automation.
    save_license(key="starter-lic", email="ops@example.com", tier="starter")
    assert LicenseValidator.is_operation_allowed(OperationType.WORKFLOW_AUTOMATION)[0] is False

    # Legacy aliases should remain compatible with existing callers.
    assert LicenseValidator.is_operation_allowed(LicenseFeature.WORKFLOW_AUTOMATION)[0] is False
