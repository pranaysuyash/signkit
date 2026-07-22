from __future__ import annotations

import logging
import os
import sys
from typing import Optional, cast, TYPE_CHECKING

from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QMessageBox, QWidget, QTabWidget

from desktop_app.api.client import ApiClient
from desktop_app.config import WORKFLOW_REVIEW_URL
from desktop_app.processing import SignatureExtractor
from desktop_app.resources.icons import get_icon
from desktop_app.state.session import SessionState
from desktop_app.views.onboarding_dialog import OnboardingDialog
from desktop_app.views.preferences_dialog import PreferencesDialog
from desktop_app.pdf.stack_profile import stack_install_hint
from desktop_app.views.main_window_parts import (
    ExtractionTabMixin,
    NativeDialogsMixin,
    PaneStatusMixin,
    PdfTabMixin,
    ThemeMixin,
    ToolbarMixin,
    PDF_AVAILABLE,
    PDF_IMPORT_ERROR,
)

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from desktop_app.backend_manager import BackendManager


from desktop_app.processing.vault import NotaryVault
from desktop_app.views.vault_tab import VaultTab

class MainWindow(
    QMainWindow,
    ThemeMixin,
    PaneStatusMixin,
    NativeDialogsMixin,
    ToolbarMixin,
    ExtractionTabMixin,
    PdfTabMixin,
):
    """Top-level window that orchestrates extraction and PDF signing flows."""

    def __init__(self, api_client: ApiClient, session_state: SessionState, backend_manager: Optional['BackendManager'] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.api_client = api_client
        self.session = session_state
        self.backend_manager = backend_manager
        
        # Initialize local processing engine
        self.local_extractor = SignatureExtractor()
        self.vault = NotaryVault()

        self.setWindowTitle("SignKit")
        app_icon = get_icon("file")
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)

        self._apply_theme()

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QHBoxLayout(central)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.tab_widget.setAccessibleName("Main workflow tabs")
        self.tab_widget.setAccessibleDescription("Switch between signature extraction and PDF signing workflows")
        if sys.platform == "darwin":
            self.tab_widget.setDocumentMode(True)
            self.tab_widget.setMovable(True)

        # Initialize status bar FIRST, before any UI setup that might use it
        self._init_status_bar()
        self._setup_menus()

        self._setup_extraction_ui()
        self._setup_pdf_ui()
        
        # Setup Vault Tab
        self.vault_tab = VaultTab(self.vault)
        self.tab_widget.addTab(self.vault_tab, "Vault")

        root.addWidget(self.tab_widget)
        
        # Force session_id_label to be initialized before any upload
        if hasattr(self, 'session_id_label'):
            self.session_id_label.setText("No session")
            self.session_id_label.setToolTip("")
        
        self._setup_main_toolbar()
        if PDF_AVAILABLE:
            self.status_bar.showMessage("Ready - PDF features enabled", 2000)
        else:
            detail = f"Ready - PDF features unavailable ({stack_install_hint()})"
            if PDF_IMPORT_ERROR:
                LOG.warning("PDF features disabled: %s", PDF_IMPORT_ERROR)
                detail = f"{detail}: {PDF_IMPORT_ERROR}"
            self.status_bar.showMessage(detail, 4000)

        # macOS palette needs reapplication after views exist (see docs/APPLE_NATIVE_IMPROVEMENTS.md)
        self._setup_dark_mode_support()

        self._backend_online = False
        # Set up periodic backend health checks
        self._backend_check_timer = QTimer()
        self._backend_check_timer.timeout.connect(self._check_backend_health)
        self._backend_check_timer.start(2000)  # Check every 2 seconds
        # Do first check after 500ms (let UI fully load first)
        QTimer.singleShot(500, self._check_backend_health)

        # Initialize responsive mode flags
        self._is_compact: bool = False
        self._is_narrow: bool = False

        # Restore window state from previous session
        self._restore_window_state()

        # Show onboarding dialog on first run
        QTimer.singleShot(500, self._maybe_show_onboarding)

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab-switching between extraction, PDF, and vault workflows."""
        try:
            if hasattr(self, "_update_toolbar_for_tab"):
                self._update_toolbar_for_tab(index)
            if hasattr(self, "_refresh_toolbar_action_states"):
                self._refresh_toolbar_action_states()

            extraction_index = getattr(self, "_extraction_tab_index", 0)
            pdf_index = getattr(self, "_pdf_tab_index", -1)

            if index == extraction_index and hasattr(self, "status_bar"):
                self.status_bar.showMessage("Ready — signature extraction", 1200)
            elif index == pdf_index and hasattr(self, "status_bar"):
                self.status_bar.showMessage("Ready — PDF signing", 1200)
        except Exception as error:
            LOG.debug("Tab change handler failed: %s", error)

    def _on_pdf_tab_open(self) -> None:
        """Backward-compatible PDF tab open hook used by toolbar and control wiring."""
        if hasattr(self, "on_pdf_open"):
            self.on_pdf_open()

    def _on_pdf_tab_save(self) -> None:
        """Backward-compatible PDF tab save hook used by toolbar and control wiring."""
        if hasattr(self, "on_pdf_save"):
            self.on_pdf_save()

    def _on_pdf_tab_close(self) -> None:
        """Backward-compatible PDF tab close hook used by toolbar and control wiring."""
        if hasattr(self, "on_pdf_close"):
            self.on_pdf_close()

    # ----- Backend Health Monitoring -----
    def _check_backend_health(self) -> None:
        """Check if backend is available and update status indicator."""
        try:
            is_available = self.backend_manager.is_available()
            
            if is_available and not self._backend_online:
                # Backend just came online
                self._backend_online = True
                self.extraction_view.backend_status_label.setText("Backend: Online")
                self.extraction_view.backend_status_label.setStyleSheet("color: #00cc00; padding: 2px 8px;")
                LOG.info("Backend is now online")
            elif not is_available and self._backend_online:
                # Backend went offline
                self._backend_online = False
                self.extraction_view.backend_status_label.setText("Backend: Checking...")
                self.extraction_view.backend_status_label.setStyleSheet("color: #666666; padding: 2px 8px;")
                LOG.info("Backend connection lost, will keep checking")
            elif not is_available and not self._backend_online:
                # Still waiting for backend to start
                self.extraction_view.backend_status_label.setText("Backend: Starting...")
                self.extraction_view.backend_status_label.setStyleSheet("color: #0066cc; padding: 2px 8px;")
        except Exception as e:
            LOG.debug(f"Backend health check failed: {e}")

    # ----- Onboarding -----
    def _maybe_show_onboarding(self) -> None:
        """Show onboarding dialog if this is the first run."""
        settings = QSettings("SignKit", "DesktopApp")
        should_show = settings.value("onboarding/show_on_startup", True, type=bool)

        if should_show:
            dialog = OnboardingDialog(self)

            # Set up backend health check callback
            def check_backend(callback):
                try:
                    if hasattr(self.api_client, "health_check"):
                        ok, payload = self.api_client.health_check(timeout=2.0)
                        if ok:
                            version = payload.get("version", "unknown") if isinstance(payload, dict) else "unknown"
                            callback(True, f"Version {version}")
                        else:
                            error = payload.get("error", "Unknown error") if isinstance(payload, dict) else str(payload)
                            callback(False, error)
                    else:
                        callback(True, "Connected")
                except Exception as e:
                    callback(False, str(e))

            dialog.set_backend_check_function(check_backend)

            # Show dialog and save preference
            if dialog.exec():
                settings.setValue("onboarding/show_on_startup", dialog.should_show_again())

    # ----- Window State Persistence -----
    def _restore_window_state(self) -> None:
        """Restore window geometry and last active tab from previous session."""
        settings = QSettings("SignKit", "DesktopApp")

        # Restore window geometry (size and position)
        geometry = settings.value("window/geometry")
        if geometry:
            try:
                self.restoreGeometry(geometry)
                LOG.debug("Restored window geometry from settings")
            except Exception as e:
                LOG.debug("Failed to restore window geometry: %s", e)
        else:
            # Default size if no saved geometry
            self.resize(1400, 900)

        # Restore window state (maximized, etc.)
        window_state = settings.value("window/state")
        if window_state:
            try:
                self.restoreState(window_state)
                LOG.debug("Restored window state from settings")
            except Exception as e:
                LOG.debug("Failed to restore window state: %s", e)

        # Restore last active tab
        last_tab_value = settings.value("window/last_tab", 0)
        try:
            if isinstance(last_tab_value, int):
                last_tab = last_tab_value
            elif isinstance(last_tab_value, str):
                last_tab = int(last_tab_value)
            else:
                last_tab = int(str(last_tab_value)) if last_tab_value is not None else 0
        except Exception:
            last_tab = 0

        if 0 <= last_tab < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(last_tab)
            LOG.debug("Restored last active tab: %d", last_tab)

    def _save_window_state(self) -> None:
        """Save window geometry and active tab for next session."""
        settings = QSettings("SignKit", "DesktopApp")

        # Save window geometry
        settings.setValue("window/geometry", self.saveGeometry())

        # Save window state
        settings.setValue("window/state", self.saveState())

        # Save current tab
        current_tab = self.tab_widget.currentIndex()
        settings.setValue("window/last_tab", current_tab)

        LOG.debug("Saved window state: tab=%d", current_tab)

    # ----- Responsive breakpoints -----
    def _apply_responsive_breakpoints(self) -> None:
        """Apply responsive layout changes based on window width.

        Breakpoints:
        - Wide (≥1400px): Full layout with all features visible
        - Compact (1000-1399px): Reduced sidebar, icon-heavy controls
        - Narrow (<1000px): Collapsed groups, single pane view
        """
        width: int = self.width()

        # Determine new states
        new_compact: bool = width < 1400
        new_narrow: bool = width < 1000

        # Only update if state changed
        if new_compact != self._is_compact or new_narrow != self._is_narrow:
            self._is_compact = new_compact
            self._is_narrow = new_narrow

            # Update sidebar if it exists
            if hasattr(self, '_left_panel'):
                self._left_panel.setProperty("compact", self._is_compact)
                self._left_panel.setProperty("narrow", self._is_narrow)

                # Adjust sidebar width
                if self._is_narrow:
                    self._left_panel.setFixedWidth(260)
                elif self._is_compact:
                    self._left_panel.setFixedWidth(280)
                else:
                    self._left_panel.setFixedWidth(300)

                # Refresh styles
                self._left_panel.style().unpolish(self._left_panel)
                self._left_panel.style().polish(self._left_panel)

            # Collapse/expand sections in narrow mode
            if hasattr(self, '_apply_narrow_mode'):
                self._apply_narrow_mode(self._is_narrow)

            LOG.debug("Responsive mode: compact=%s, narrow=%s, width=%d",
                     self._is_compact, self._is_narrow, width)

    # ----- Menu configuration -----
    def _setup_menus(self) -> None:
        menu_bar = self.menuBar()

        app_menu = menu_bar.addMenu("SignKit")
        about_action = QAction("About SignKit", self)
        about_action.setMenuRole(QAction.MenuRole.AboutRole)
        about_action.triggered.connect(self._show_about_dialog)
        app_menu.addAction(about_action)

        preferences_action = QAction("Preferences…", self)
        preferences_action.setMenuRole(QAction.MenuRole.PreferencesRole)
        preferences_action.setShortcut(QKeySequence.StandardKey.Preferences)
        preferences_action.triggered.connect(self._show_preferences_dialog)
        app_menu.addAction(preferences_action)
        app_menu.addSeparator()

        quit_action = QAction("Quit SignKit", self)
        quit_action.setMenuRole(QAction.MenuRole.QuitRole)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(lambda: QApplication.instance().quit())
        app_menu.addAction(quit_action)

        file_menu = menu_bar.addMenu("File")

        open_image_action = QAction("Open Image…", self)
        open_image_action.setShortcut(QKeySequence.StandardKey.Open)
        open_image_action.triggered.connect(self.on_open)
        file_menu.addAction(open_image_action)

        open_pdf_action = QAction("Open PDF…", self)
        open_pdf_action.setShortcut(QKeySequence("Meta+Shift+O"))
        open_pdf_action.triggered.connect(self.on_pdf_open)
        file_menu.addAction(open_pdf_action)

        file_menu.addSeparator()

        export_action = QAction("Export Signature…", self)
        export_action.setShortcut(QKeySequence("Meta+E"))
        export_action.triggered.connect(self.on_export)
        file_menu.addAction(export_action)

        save_library_action = QAction("Save to Library", self)
        save_library_action.setShortcut(QKeySequence.StandardKey.Save)
        save_library_action.triggered.connect(self.on_save_to_library)
        file_menu.addAction(save_library_action)

        save_pdf_action = QAction("Save Signed PDF…", self)
        save_pdf_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_pdf_action.triggered.connect(self.on_pdf_save)
        save_pdf_action.setEnabled(PDF_AVAILABLE)
        file_menu.addAction(save_pdf_action)

        file_menu.addSeparator()

        close_window_action = QAction("Close Window", self)
        close_window_action.setShortcut(QKeySequence.StandardKey.Close)
        close_window_action.triggered.connect(self.close)
        file_menu.addAction(close_window_action)

        edit_menu = menu_bar.addMenu("Edit")
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.setEnabled(False)
        edit_menu.addAction(undo_action)
        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.setEnabled(False)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()

        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self._handle_copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste Signature from Clipboard", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self._handle_paste_action)
        edit_menu.addAction(paste_action)

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self._handle_select_all_action)
        edit_menu.addAction(select_all_action)

        view_menu = menu_bar.addMenu("View")
        fit_action = QAction("Fit to View", self)
        fit_action.setShortcut(QKeySequence("Meta+1"))
        fit_action.triggered.connect(self._on_fit)
        view_menu.addAction(fit_action)

        reset_action = QAction("Reset Zoom", self)
        reset_action.setShortcut(QKeySequence("Meta+0"))
        reset_action.triggered.connect(self._on_reset_zoom)
        view_menu.addAction(reset_action)

        view_menu.addSeparator()

        full_screen_action = QAction("Enter Full Screen", self)
        full_screen_action.setShortcut(QKeySequence.StandardKey.FullScreen)
        full_screen_action.triggered.connect(self.showFullScreen)
        view_menu.addAction(full_screen_action)

        window_menu = menu_bar.addMenu("Window")
        minimize_action = QAction("Minimize", self)
        minimize_action.setShortcut(QKeySequence("Meta+M"))
        minimize_action.triggered.connect(self.showMinimized)
        window_menu.addAction(minimize_action)

        zoom_action = QAction("Zoom", self)
        zoom_action.triggered.connect(self._toggle_window_zoom)
        window_menu.addAction(zoom_action)

        window_menu.addSeparator()

        bring_all_action = QAction("Bring All to Front", self)
        bring_all_action.triggered.connect(self._bring_all_windows_to_front)
        window_menu.addAction(bring_all_action)

        help_menu = menu_bar.addMenu("Help")
        self.open_help_action = QAction("Help & Troubleshooting", self)
        self.open_help_action.triggered.connect(lambda: self._open_document("docs/HELP.md"))
        help_menu.addAction(self.open_help_action)

        self.open_shortcuts_action = QAction("Keyboard Shortcuts", self)
        self.open_shortcuts_action.triggered.connect(lambda: self._open_document("docs/SHORTCUTS.md"))
        help_menu.addAction(self.open_shortcuts_action)

        help_menu.addSeparator()

        self.workflow_review_action = QAction("Recurring Document Workflows…", self)
        self.workflow_review_action.setStatusTip(
            "Discuss recurring batches or custom document workflows without sharing document data"
        )
        self.workflow_review_action.triggered.connect(self._open_workflow_review)
        help_menu.addAction(self.workflow_review_action)

        help_menu.addSeparator()

        self.check_updates_action = QAction("Check for Updates…", self)
        self.check_updates_action.triggered.connect(self.on_check_updates)
        help_menu.addAction(self.check_updates_action)

        self.check_health_action = QAction("Open Backend Health", self)
        self.check_health_action.triggered.connect(lambda: self._open_url(f"{self.api_client.base_url}/health"))
        help_menu.addAction(self.check_health_action)

        license_menu = menu_bar.addMenu("License")

        # Check current license status
        from desktop_app.license.storage import is_licensed, load_license
        is_active = is_licensed()

        # License status action (non-clickable info)
        if is_active:
            license_info = load_license()
            email_text = f" ({license_info.email})" if license_info and license_info.email else ""
            status_action = QAction(f"✓ Licensed{email_text}", self)
            status_action.setEnabled(False)
            license_menu.addAction(status_action)
            license_menu.addSeparator()
        else:
            status_action = QAction("⚠ No License (Trial Mode)", self)
            status_action.setEnabled(False)
            license_menu.addAction(status_action)
            license_menu.addSeparator()

        self.enter_license_action = QAction("Enter License Key…", self)
        self.enter_license_action.triggered.connect(self.on_enter_license)
        # Disable "Enter License" if already licensed
        if is_active:
            self.enter_license_action.setEnabled(False)
            self.enter_license_action.setText("License Already Active")
        license_menu.addAction(self.enter_license_action)

        self.buy_license_action = QAction("Buy License…", self)
        self.buy_license_action.triggered.connect(self.on_buy_license)
        license_menu.addAction(self.buy_license_action)

        # Tools Menu
        tools_menu = menu_bar.addMenu("Tools")
        
        self.verify_sig_action = QAction("Verify Signature...", self)
        self.verify_sig_action.triggered.connect(self.on_verify_signature)
        tools_menu.addAction(self.verify_sig_action)

    def _open_workflow_review(self) -> None:
        """Open the source-attributed workflow enquiry without document metadata."""
        self._open_url(WORKFLOW_REVIEW_URL)

    def _show_about_dialog(self) -> None:
        QMessageBox.about(
            self,
            "About SignKit",
            "SignKit is a native desktop workflow for extracting signatures and signing PDFs.\n\n"
            "Designed to stay close to macOS conventions while keeping the processing surface local."
        )

    def _show_preferences_dialog(self) -> None:
        dialog = PreferencesDialog(self)
        dialog.exec()

    def _handle_paste_action(self) -> None:
        focus_widget = QApplication.focusWidget()
        if focus_widget and hasattr(focus_widget, "paste"):
            focus_widget.paste()
            return

        pdf_index = getattr(self, "_pdf_tab_index", -1)
        if PDF_AVAILABLE and pdf_index >= 0 and getattr(self, "tab_widget", None) and self.tab_widget.currentIndex() == pdf_index:
            if hasattr(self, "_on_pdf_paste_signature"):
                self._on_pdf_paste_signature()

    def _handle_copy_action(self) -> None:
        focus_widget = QApplication.focusWidget()
        if focus_widget and hasattr(focus_widget, "copy"):
            focus_widget.copy()
            return

        if hasattr(self, "on_copy"):
            self.on_copy()

    def _handle_select_all_action(self) -> None:
        focus_widget = QApplication.focusWidget()
        if focus_widget and hasattr(focus_widget, "selectAll"):
            focus_widget.selectAll()

    def _bring_all_windows_to_front(self) -> None:
        self.raise_()
        self.activateWindow()

    def _toggle_window_zoom(self) -> None:
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def on_check_updates(self):
        """Check for application updates by fetching updates.json from CDN."""
        from PySide6.QtWidgets import QMessageBox
        import json
        import re
        try:
            import requests
        except ImportError:
            QMessageBox.critical(
                self,
                "Update Check Failed",
                "The 'requests' library is required for update checking but is not installed.\n"
                "Please install it using: pip install requests"
            )
            return
        
        from desktop_app.config import APP_VERSION
        current_version = APP_VERSION

        # Try to read version from a version file if it exists
        try:
            version_path = os.path.join(os.path.dirname(__file__), "..", "..", "VERSION")
            if os.path.exists(version_path):
                with open(version_path, 'r') as f:
                    current_version = f.read().strip()
        except OSError:
            pass  # Use default version if file doesn't exist or can't be read
        
        # Define the updates URL - this should be configured via environment or config
        updates_url = os.getenv("UPDATES_URL", "https://cdn.signkit.work/updates.json")
        
        try:
            response = requests.get(updates_url, timeout=10)
            response.raise_for_status()
            update_data = response.json()
            
            latest_version = update_data.get("version", "")
            download_url = update_data.get("download_url", "")
            release_notes = update_data.get("release_notes", "")
            
            if not latest_version:
                QMessageBox.information(
                    self,
                    "Update Check",
                    "Could not determine latest version. Please try again later."
                )
                return
            
            # Compare versions using a simple approach
            def parse_version(v):
                # Convert version string to tuple of integers for comparison
                # e.g. "1.2.3" -> (1, 2, 3)
                return tuple(map(int, re.findall(r'\d+', v)))
            
            if parse_version(latest_version) > parse_version(current_version):
                # New version available
                message = f"New version available: {latest_version}\n\nCurrent version: {current_version}"
                if release_notes:
                    message += f"\n\nRelease notes:\n{release_notes}"
                
                reply = QMessageBox.question(
                    self,
                    "Update Available",
                    message,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes and download_url:
                    from PySide6.QtGui import QDesktopServices
                    from PySide6.QtCore import QUrl
                    QDesktopServices.openUrl(QUrl(download_url))
            else:
                # No updates available
                QMessageBox.information(
                    self,
                    "Update Check",
                    f"You are using the latest version ({current_version})."
                )
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(
                self,
                "Update Check Failed",
                f"Could not check for updates:\n{str(e)}\n\nPlease check your internet connection."
            )
        except json.JSONDecodeError:
            QMessageBox.critical(
                self,
                "Update Check Failed",
                "Invalid response from update server. Please try again later."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Update Check Failed",
                f"An error occurred while checking for updates:\n{str(e)}"
            )
            
    def on_verify_signature(self):
        """Open the signature verification dialog."""
        from desktop_app.views.verify_dialog import VerifyDialog
        dialog = VerifyDialog(self)
        dialog.exec()
    
    # ----- Qt overrides -----
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.defer_coordinate_update()
        self._apply_responsive_breakpoints()

    def closeEvent(self, event) -> None:
        """Save window state before closing."""
        self._save_window_state()
        super().closeEvent(event)


__all__ = ["MainWindow"]
