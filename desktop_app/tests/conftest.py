"""Shared fixtures for desktop_app tests."""

import os
import pytest

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings
except ModuleNotFoundError:  # pragma: no cover - environment-specific
    QApplication = None
    QSettings = None


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for the test session."""
    if QApplication is None:
        return None

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture(autouse=True)
def _disable_onboarding(qapp):
    """Disable onboarding dialog for all tests."""
    if QSettings is None:
        yield
        return

    settings = QSettings("SignKit", "DesktopApp")
    settings.setValue("onboarding/show_on_startup", False)
    yield
