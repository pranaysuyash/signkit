"""Tests for launch-profile driven desktop startup configuration."""

from desktop_app.launch_profile import get_profile


def test_get_profile_defaults_to_standard():
    profile = get_profile()
    assert profile.profile_name == "standard"
    assert profile.application_name == "SignKit"
    assert profile.window_title is None


def test_get_profile_mac_premium_is_isolated():
    profile = get_profile("mac-premium")
    assert profile.profile_name == "mac-premium"
    assert profile.premium_ui is True
    assert profile.application_name == "SignKit Premium"
    assert profile.resolve_title() == "SignKit Premium"
    assert profile.default_plan_id == "team"


def test_get_profile_unknown_profile_raises():
    try:
        get_profile("beta")
    except ValueError as exc:
        assert "Unknown launch profile: beta" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown profile")
