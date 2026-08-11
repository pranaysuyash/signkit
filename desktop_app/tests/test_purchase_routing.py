"""Tests for plan-aware purchase routing in buy flows."""

from __future__ import annotations

import webbrowser
from unittest.mock import Mock

import pytest
PySide6 = pytest.importorskip("PySide6")

from PySide6.QtWidgets import QWidget, QDialog

from desktop_app.api.client import ApiClient
from desktop_app.state.session import SessionState
from desktop_app.views.main_window import MainWindow
from desktop_app.views.license_restriction_dialog import LicenseRestrictionDialog
from desktop_app.license.storage import OperationType


PySide6 = pytest.importorskip("PySide6")


def _build_window(monkeypatch, onboarding_default_plan_id: str = "starter") -> MainWindow:
    mock_client = Mock(spec=ApiClient)
    mock_client.base_url = "http://127.0.0.1:8001"
    mock_session = Mock(spec=SessionState)
    return MainWindow(mock_client, mock_session, onboarding_default_plan_id=onboarding_default_plan_id)


def test_main_window_buy_license_uses_profile_default_plan(monkeypatch, qapp):
    captured = {}

    def _fake_purchase_url(plan_id: str | None = None) -> str:
        captured["plan"] = plan_id
        return f"https://example.test/checkout/{plan_id}"

    def _fake_open_url(url: object) -> bool:
        # Accept both QUrl and mockable objects that implement toString.
        captured["opened"] = str(getattr(url, "toString", lambda: str(url))())
        return True

    monkeypatch.setattr("desktop_app.config.get_purchase_url", _fake_purchase_url)
    monkeypatch.setattr("desktop_app.views.main_window_parts.extraction.QDesktopServices.openUrl", _fake_open_url)

    window = _build_window(monkeypatch, onboarding_default_plan_id="business")
    window.on_buy_license()

    assert captured.get("plan") == "business"
    assert captured.get("opened") == "https://example.test/checkout/business"

    window.close()


class _PlanAwareParent(QWidget):
    def get_default_purchase_plan_id(self) -> str:
        return "team"


def test_license_restriction_dialog_uses_parent_plan(monkeypatch, qapp):
    captured = {}

    def _fake_purchase_url(plan_id: str | None = None) -> str:
        captured["plan"] = plan_id
        return f"https://example.test/restriction/{plan_id}"

    def _fake_web_open(url: str) -> bool:
        captured["opened"] = str(url)
        return True

    monkeypatch.setattr("desktop_app.views.license_restriction_dialog.get_purchase_url", _fake_purchase_url)
    monkeypatch.setattr("desktop_app.views.license_restriction_dialog.webbrowser.open", _fake_web_open)

    parent = _PlanAwareParent()
    dialog = LicenseRestrictionDialog(OperationType.EXPORT, parent=parent)
    dialog.on_buy_license()

    assert captured.get("plan") == "team"
    assert captured.get("opened") == "https://example.test/restriction/team"
    assert isinstance(dialog, QDialog)
