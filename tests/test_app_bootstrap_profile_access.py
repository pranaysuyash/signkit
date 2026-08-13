from unittest.mock import Mock
import sys
import types

import pytest

pytest.importorskip("PySide6")

from desktop_app.launch_profile import get_profile



def test_resolve_workflow_access_uses_profile_premium_flag(monkeypatch):
    profile = get_profile()
    assert profile.profile_name == "standard"

    monkeypatch.setattr("desktop_app.app_bootstrap.LicenseValidator.can_use_workflow_automation", Mock(return_value=False))
    from desktop_app.app_bootstrap import _resolve_workflow_access

    assert _resolve_workflow_access(profile) is False

    premium_profile = get_profile("mac-premium")
    assert _resolve_workflow_access(premium_profile) is True


def test_resolve_workflow_access_falls_back_to_license_for_standard_profile(monkeypatch):
    profile = get_profile()
    monkeypatch.setattr("desktop_app.app_bootstrap.LicenseValidator.can_use_workflow_automation", Mock(return_value=True))
    from desktop_app.app_bootstrap import _resolve_workflow_access

    assert _resolve_workflow_access(profile) is True


def test_resolve_workflow_access_returns_false_if_license_checker_errors(monkeypatch):
    profile = get_profile()

    def _broken_checker():
        raise RuntimeError("license store inaccessible")

    monkeypatch.setattr("desktop_app.app_bootstrap.LicenseValidator.can_use_workflow_automation", _broken_checker)
    from desktop_app.app_bootstrap import _resolve_workflow_access

    assert _resolve_workflow_access(profile) is False


def test_run_with_profile_routes_profile_defaults_to_main_window_kwargs(monkeypatch):
    """Premium vs standard profile defaults should flow into MainWindow constructor."""

    from desktop_app.app_bootstrap import run_with_profile
    from desktop_app.launch_profile import get_profile

    calls = {}

    class FakeQApplication:
        def __init__(self, _argv):
            self._attributes = []
            self._style = None
            self._window_icon = None
            self._font = types.SimpleNamespace(
                setHintingPreference=lambda *_args, **_kwargs: None,
            )

        def setStyle(self, value):
            self._style = value

        def setAttribute(self, attribute, value):
            self._attributes.append((attribute, value))

        def font(self):  # pragma: no cover - bootstrap wiring only
            return self._font

        def setFont(self, font):  # pragma: no cover - bootstrap wiring only
            self._font = font

        def setStyleSheet(self, style):  # pragma: no cover - bootstrap wiring only
            self._stylesheet = style

        def setOrganizationName(self, value):  # pragma: no cover - wiring only
            pass

        def setOrganizationDomain(self, value):  # pragma: no cover - wiring only
            pass

        def setApplicationName(self, value):  # pragma: no cover - wiring only
            pass

        def setApplicationDisplayName(self, value):  # pragma: no cover - wiring only
            pass

        def setDesktopFileName(self, value):  # pragma: no cover - wiring only
            pass

        def setWindowIcon(self, _icon):  # pragma: no cover - wiring only
            pass

        def processEvents(self):  # pragma: no cover - wiring only
            pass

        def exec(self):
            return 0

    class _DummyCursorShape:
        ClosedHandCursor = object()

    class _DummyApplicationAttribute:
        AA_DontUseNativeMenuBar = object()

    class _DummyQt:
        ApplicationAttribute = _DummyApplicationAttribute
        CursorShape = _DummyCursorShape

    class FakeWindow:
        def __init__(self, *args, **kwargs):
            calls["kwargs"] = kwargs

        def setWindowIcon(self, _icon):  # pragma: no cover - wiring only
            pass

        def setMinimumSize(self, *_args):
            pass

        def resize(self, *_args):
            pass

        def show(self):
            pass

    monkeypatch.setattr("PySide6.QtWidgets.QApplication", FakeQApplication)
    monkeypatch.setattr("PySide6.QtGui.QIcon", lambda *_args, **_kwargs: object())
    monkeypatch.setattr("PySide6.QtCore.Qt", _DummyQt)

    fake_main_window_module = types.ModuleType("desktop_app.views.main_window")
    fake_main_window_module.MainWindow = FakeWindow
    monkeypatch.setitem(sys.modules, "desktop_app.views.main_window", fake_main_window_module)
    monkeypatch.setattr(
        "desktop_app.app_bootstrap.load_config",
        lambda: type(
            "Config",
            (),
            {
                "api_base_url": "http://127.0.0.1:8001",
                "allow_remote_document_upload": False,
                "debug": False,
                "log_level": "INFO",
                "enable_analytics": False,
            },
        )(),
    )
    monkeypatch.setattr("desktop_app.app_bootstrap.ApiClient", lambda *_, **__: None)
    monkeypatch.setattr("desktop_app.app_bootstrap.BackendManager", lambda *_, **__: type("BM", (), {"start": staticmethod(lambda: False), "port": 8001})())
    monkeypatch.setattr("desktop_app.app_bootstrap.SessionState", lambda: object())

    # Keep bootstrap from crashing on macos branch internals by preventing license checks.
    monkeypatch.setattr("desktop_app.app_bootstrap.LicenseValidator.can_use_workflow_automation", Mock(return_value=False))

    run_with_profile(get_profile("mac-premium"))
    assert calls["kwargs"]["onboarding_default_plan_id"] == "team"
    assert calls["kwargs"]["show_onboarding_upgrade_card"] is False
    assert calls["kwargs"]["workflow_premium_enabled"] is True

    calls.clear()
    run_with_profile(get_profile("standard"))
    assert calls["kwargs"]["onboarding_default_plan_id"] == "starter"
    assert calls["kwargs"]["show_onboarding_upgrade_card"] is True
    assert calls["kwargs"]["workflow_premium_enabled"] is False
