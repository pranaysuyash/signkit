"""Tests for profile-aware launcher behavior."""

from __future__ import annotations

from desktop_app import run as launcher


def test_resolve_profile_defaults_to_platform(monkeypatch):
    assert launcher._resolve_profile_name(requested_profile=None, platform_name="darwin") == "mac-premium"
    assert launcher._resolve_profile_name(requested_profile=None, platform_name="linux") == "standard"


def test_resolve_profile_obeys_env_then_cli(monkeypatch):
    assert launcher.resolve_profile("auto", platform_name="linux").profile_name == "standard"

    monkeypatch.setenv("SIGNKIT_PROFILE", "standard")
    assert launcher.resolve_profile("auto", platform_name="darwin").profile_name == "standard"


def test_resolve_profile_invalid_profile_is_rejected():
    try:
        launcher._resolve_profile_name("enterprise", platform_name="linux")
    except ValueError as exc:
        assert "Unknown launch profile: enterprise" in str(exc)
    else:
        raise AssertionError("expected unknown profile to fail")


def test_run_lists_profiles(capsys):
    assert launcher.run(["--list-profiles"]) == 0
    output = capsys.readouterr().out
    assert "standard" in output
    assert "mac-premium" in output


def test_run_invokes_app_bootstrap_with_resolved_profile(monkeypatch):
    called = {}

    def _mock_run(profile):
        called["name"] = profile.profile_name
        return 0

    monkeypatch.setattr(launcher, "run_with_profile", _mock_run)
    assert launcher.run(["--profile", "standard"]) == 0
    assert called["name"] == "standard"


def test_run_rejects_mac_premium_on_non_macos():
    # emulate non-mac host to prove we block mac premium on unsupported platforms
    old_platform = launcher._PLATFORM_NAME
    launcher._PLATFORM_NAME = "linux"
    try:
        assert launcher.run(["--premium"]) == 1
    finally:
        launcher._PLATFORM_NAME = old_platform
