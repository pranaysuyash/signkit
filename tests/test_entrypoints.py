"""Smoke tests for desktop entrypoint wiring."""

from __future__ import annotations

import sys
import pytest
from unittest.mock import patch

import desktop_app.main as main_entry
import desktop_app.main_macos_premium as mac_premium_entry


def test_main_entrypoint_uses_standard_profile():
    with patch("desktop_app.main._run_profile") as mock_run:
        with pytest.raises(SystemExit):
            main_entry.main()
        mock_run.assert_called_once_with("standard")


def test_macos_premium_entrypoint_uses_premium_profile(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    with patch("desktop_app.main_macos_premium._run_profile") as mock_run:
        with pytest.raises(SystemExit):
            mac_premium_entry.main()
        mock_run.assert_called_once_with("mac-premium")


def test_macos_premium_entrypoint_rejects_non_darwin(monkeypatch):
    monkeypatch.setattr("sys.platform", "linux")
    with pytest.raises(SystemExit) as exc:
        mac_premium_entry.main()
    assert exc.value.code == 1


def test_package_entrypoint_delegates_to_run_main():
    with patch("desktop_app.run.main") as mock_main:
        from desktop_app.__main__ import main as package_main

        package_main()
        mock_main.assert_called_once_with()
