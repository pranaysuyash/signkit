from __future__ import annotations

import os
import sys
from threading import Thread
from typing import Final

from desktop_app.config import load_config
from desktop_app.state.session import SessionState
from desktop_app.api.client import ApiClient
from desktop_app.backend_manager import BackendManager
from desktop_app.license.storage import LicenseValidator
from desktop_app.launch_profile import LaunchProfile


def _resource_path(relative: str) -> str:
    """Return the absolute path to a bundled or local resource path."""

    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, relative)


def _resolve_workflow_access(profile: LaunchProfile) -> bool:
    """Return whether workflow automation UI should be unlocked for this run."""

    if profile.premium_ui:
        return True

    try:
        return bool(LicenseValidator.can_use_workflow_automation())
    except Exception:
        return False


def run_with_profile(profile: LaunchProfile) -> int:
    """Start the desktop app with the given launch profile."""

    os.environ.setdefault("QT_MAC_APPLICATION_NAME", profile.qt_mac_application_name)
    os.environ.setdefault("QT_MAC_WANTS_LAYER", "1")

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    if sys.platform == "darwin":
        # Use native macOS style
        try:
            app.setStyle("macOS")
        except Exception:
            pass

        # Enable native menu bar
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeMenuBar, False)
        except AttributeError:
            pass

        # Set font rendering for better text on macOS
        from PySide6.QtGui import QFont, QPalette

        app_font = app.font()
        app_font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        app.setFont(app_font)
        app.setStyleSheet("")  # Clear styles and use system palette

    # Reinforce metadata after QApplication construction (Qt caches some values)
    app.setOrganizationName(profile.organization_name)
    app.setOrganizationDomain(profile.organization_domain)
    app.setApplicationName(profile.application_name)
    app.setApplicationDisplayName(profile.application_display_name)
    try:
        app.setDesktopFileName(profile.desktop_file_name)
    except AttributeError:
        pass

    # Set dock/app icon from bundled assets if available
    for rel in profile.icon_preference:
        path = _resource_path(rel)
        if os.path.exists(path):
            app.setWindowIcon(QIcon(path))
            break

    cfg = load_config()
    session = SessionState()
    client = ApiClient(
        cfg.api_base_url,
        session,
        allow_remote_document_upload=cfg.allow_remote_document_upload,
    )
    backend_manager: Final = BackendManager(port=8001, auto_start=True)

    def _start_backend() -> None:
        try:
            if backend_manager.start():
                # Point client to the dynamically selected backend port
                client.update_base_url(f"http://127.0.0.1:{backend_manager.port}")
                print(f"Backend started successfully at {client.base_url} - local companion available")
            else:
                print("Backend not available - running in offline mode")
        except Exception as error:
            print(f"Backend startup failed: {error} - running in offline mode")

    backend_thread = Thread(target=_start_backend, name="BackendStartup", daemon=True)
    backend_thread.start()

    from desktop_app.views.main_window import MainWindow

    # Start UI without forcing login
    window_title = profile.resolve_title()
    window = MainWindow(
        client,
        session,
        backend_manager,
        window_title=window_title,
        workflow_premium_enabled=_resolve_workflow_access(profile),
        onboarding_default_plan_id=profile.default_plan_id,
        show_onboarding_upgrade_card=not profile.premium_ui,
    )

    for rel in profile.icon_preference:
        path = _resource_path(rel)
        if os.path.exists(path):
            window.setWindowIcon(QIcon(path))
            break

    window.setMinimumSize(*profile.min_window_size)
    window.resize(*profile.initial_window_size)
    window.show()

    app.processEvents()
    return app.exec()


def run(profile: LaunchProfile) -> int:
    """Compatibility alias for profile-based launch."""

    return run_with_profile(profile)
