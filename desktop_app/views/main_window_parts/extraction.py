from __future__ import annotations

import atexit
import io
import logging
import os
import sys
from uuid import uuid4
from tempfile import NamedTemporaryFile
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Optional, Protocol, Tuple, cast

import numpy as np
from PIL import Image as PILImage

# Standalone utilities extracted to separate modules
from desktop_app.views.main_window_parts.extraction_utils import (
    AsyncRunner,
    dispatch,
    run_async,
    run_signature_preview,
    _rgba,
    _create_button,
    _clear_layout,
)
from desktop_app.views.main_window_parts.extraction_widgets import ElidingButton

from PySide6.QtCore import QObject, Signal
from PySide6.QtCore import QTimer, Qt, QPoint, QBuffer, QIODevice, QUrl, QEvent
from PySide6.QtGui import QColor, QDesktopServices, QFont, QFontMetrics, QImage, QKeySequence, QPalette, QPixmap, QShortcut, QTransform
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSizePolicy,
    QStatusBar,
    QVBoxLayout,
    QToolButton,
    QWidget,
)

from desktop_app.api.client import ApiClient
from desktop_app.api.errors import ApiContractError
from desktop_app.library import storage as lib
from desktop_app.license.storage import is_licensed
from desktop_app.resources.icons import get_icon, set_button_icon
from desktop_app.widgets.glass_panel import GlassPanel
from desktop_app.widgets.image_view import ImageView
from desktop_app.widgets.modern_mac_button import ModernMacButton
from desktop_app.views.export_dialog import ExportDialog
from desktop_app.views.help_dialog import HelpDialog
from desktop_app.views.license_dialog import LicenseDialog
from desktop_app.views.signature_candidate_dialog import SignatureCandidateDialog
from desktop_app.workflows.operator_content import (
    companion_status_label,
    companion_status_message,
    companion_tooltip,
    deletion_outcome_message,
)

if TYPE_CHECKING:
    from PySide6.QtCore import QEvent

    class _MainWindowProtocol(Protocol):
        """Protocol defining methods from QMainWindow that mixins depend on."""
        api_client: ApiClient
        status_bar: QStatusBar
        tab_widget: Any
        session: Any

        def palette(self) -> QPalette: ...
        def setPalette(self, palette: QPalette) -> None: ...
        def setWindowFilePath(self, path: str) -> None: ...
        def setStyleSheet(self, styleSheet: str) -> None: ...
        def resizeEvent(self, event: QEvent) -> None: ...

LOG = logging.getLogger(__name__)

ShortcutKey = QKeySequence | QKeySequence.StandardKey | str


class _SignatureCaptureDialog(QDialog):
    """Capture a signature from webcam and return a local image path."""

    _FRAME_INTERVAL_MS = 33

    def __init__(self, parent: Optional[QWidget] = None, *, camera_index: int = 0) -> None:
        super().__init__(parent)
        self.setWindowTitle("Capture Signature")
        self.setObjectName("captureDialog")
        self.setMinimumSize(640, 520)
        self.setModal(True)
        self._camera_index = camera_index
        self._captured_path: str | None = None
        self._last_error: str | None = None
        self._frame_bgr: Any | None = None
        self._cap: Any | None = None
        self._cv2 = None
        self._frame_errors = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._preview = QLabel("Starting camera...")
        self._preview.setMinimumSize(600, 420)
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setStyleSheet(
            "background: #111; color: #fff; border-radius: 8px; border: 1px solid #666;"
        )
        layout.addWidget(self._preview)

        hint = QLabel("Position the signature in frame, then click Capture.")
        hint.setObjectName("captureHint")
        layout.addWidget(hint)

        button_row = QHBoxLayout()
        self._capture_button = _create_button("Capture", cast(QWidget, self), primary=True)
        self._capture_button.setObjectName("captureButton")
        self._capture_button.clicked.connect(self._capture_current_frame)
        self._cancel_button = _create_button("Cancel", cast(QWidget, self))
        self._cancel_button.clicked.connect(self.reject)
        button_row.addWidget(self._capture_button)
        button_row.addWidget(self._cancel_button)
        layout.addLayout(button_row)

        self._timer = QTimer(self)
        self._timer.setInterval(self._FRAME_INTERVAL_MS)
        self._timer.timeout.connect(self._update_frame)
        self._start_camera()
        self.finished.connect(self._stop_camera)

    def _start_camera(self) -> None:
        try:
            import cv2
            self._cv2 = cv2
        except Exception as exc:
            self._handle_error(str(exc))
            self._capture_button.setEnabled(False)
            return

        candidates = [self._camera_index, 0, 1, 2]
        opened_cap = None
        for index in dict.fromkeys(c for c in candidates if c >= 0):
            cap = self._cv2.VideoCapture(
                index,
                self._cv2.CAP_DSHOW if hasattr(self._cv2, "CAP_DSHOW") else self._cv2.CAP_ANY,
            )
            if cap.isOpened():
                opened_cap = cap
                LOG.debug("Opened camera index %s", index)
                break
            cap.release()

        if opened_cap is None:
            self._handle_error(
                "No camera available. Connect a webcam and grant camera permission."
            )
            self._capture_button.setEnabled(False)
            return

        opened_cap.set(self._cv2.CAP_PROP_FRAME_WIDTH, 1280)
        opened_cap.set(self._cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self._cap = opened_cap
        self._timer.start()

    def _stop_camera(self) -> None:
        if self._timer.isActive():
            self._timer.stop()
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def _handle_error(self, message: str) -> None:
        self._last_error = message
        self._preview.setText(message)
        self._capture_button.setEnabled(False)

    def _frame_to_rgb(self, frame: Any) -> Any:
        """Normalize a camera frame into an RGB array suitable for Qt preview."""
        if self._cv2 is None:
            raise RuntimeError("Camera backend is unavailable")
        if frame is None:
            raise ValueError("No camera frame available")

        if hasattr(frame, "ndim") and frame.ndim == 2:
            return self._cv2.cvtColor(frame, self._cv2.COLOR_GRAY2RGB)

        if hasattr(frame, "ndim") and frame.ndim == 3:
            channels = frame.shape[2]
            if channels == 3:
                return self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2RGB)
            if channels == 4:
                return self._cv2.cvtColor(frame, self._cv2.COLOR_BGRA2RGBA)
            if channels == 1:
                return self._cv2.cvtColor(frame, self._cv2.COLOR_GRAY2RGB)

        raise ValueError(f"Unsupported camera frame shape: {getattr(frame, 'shape', None)}")

    def _update_frame(self) -> None:
        if self._cap is None or self._cv2 is None:
            return
        try:
            ret, frame = self._cap.read()
            if not ret or frame is None:
                self._frame_errors += 1
                if self._frame_errors >= 10:
                    self._handle_error("Camera read failed. Retry or switch source.")
                return
            self._frame_errors = 0
            self._frame_bgr = frame
            frame_rgb = self._frame_to_rgb(frame)
            h, w = frame_rgb.shape[:2]
            channels = 1 if frame_rgb.ndim == 2 else frame_rgb.shape[2]
            bytes_per_line = channels * w
            if channels == 1:
                fmt = QImage.Format.Format_Grayscale8
            elif channels == 4:
                fmt = QImage.Format.Format_RGBA8888
            else:
                fmt = QImage.Format.Format_RGB888
            qimg = QImage(
                frame_rgb.data,
                w,
                h,
                bytes_per_line,
                fmt,
            ).copy()
            pix = QPixmap.fromImage(qimg)
            self._preview.setPixmap(
                pix.scaled(self._preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
        except Exception as exc:
            LOG.exception("Camera preview update failed")
            self._handle_error(f"Camera preview failed: {exc}")

    def _capture_current_frame(self) -> None:
        if self._frame_bgr is None or self._cv2 is None:
            self._handle_error("No frame available. Wait for camera preview.")
            return
        frame_copy = self._frame_bgr.copy()
        try:
            _, encoded = self._cv2.imencode(".png", frame_copy)
            with NamedTemporaryFile(suffix=".png", delete=False) as output:
                output.write(encoded.tobytes())
                self._captured_path = output.name
            self.accept()
        except Exception as exc:
            self._handle_error(f"Failed to capture frame: {exc}")

    def capture_path(self) -> Optional[str]:
        if self.exec() == QDialog.DialogCode.Accepted:
            return self._captured_path
        return None


class ExtractionTabMixin:
    """Signature extraction tab, color handling, and library management.

    This mixin is designed to be used with QMainWindow and provides
    the extraction tab UI and functionality. For type checking purposes,
    it expects the including class to provide QMainWindow methods.
    """

    # Signal for pane focus changes (used by context menus and status updates)
    pane_focus_changed = Signal(str)

    # Declare attributes that will be provided by QMainWindow or other mixins
    # Using 'Any' to avoid circular imports and mypy issues with mixins
    api_client: Any
    backend_manager: Any
    local_extractor: Any
    status_bar: Any
    tab_widget: Any
    session: Any

    # Visual feedback system attributes
    _feedback_timers: dict[str, QTimer]
    _progress_dialogs: dict[str, Any]

    # Declare methods that will be provided by other mixins
    def _install_pane_click_filter(self, view: 'ImageView', pane_name: str) -> None:
        """Install event filter for pane click detection with enhanced interaction."""
        if not hasattr(self, '_pane_event_filters'):
            self._pane_event_filters = {}

        # Enable custom context menu for the view
        view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        view.customContextMenuRequested.connect(lambda pos: self._on_pane_context_menu(view, pane_name, pos))

        # Create event filter for this pane
        class PaneEventFilter(QObject):
            def __init__(self, parent_extraction, pane_name):
                super().__init__()
                self.parent = parent_extraction
                self.pane_name = pane_name
                self._press_pos = None

            def eventFilter(self, obj, event):
                # Handle mouse press for pane activation
                if event.type() == event.Type.MouseButtonPress:
                    if event.button() == event.MouseButton.LeftButton:
                        self._press_pos = event.pos()
                        return False  # Let the event propagate

                # Handle mouse release for pane activation
                elif event.type() == event.Type.MouseButtonRelease:
                    if (event.button() == event.MouseButton.LeftButton and
                        self._press_pos is not None):
                        # Only activate pane if it's a click (not a drag)
                        click_distance = (event.pos() - self._press_pos).manhattanLength()
                        if click_distance < 3:  # Threshold for click vs drag
                            QTimer.singleShot(50, lambda: self.parent._on_pane_clicked(self.pane_name))
                        self._press_pos = None
                        return False  # Let the event propagate

                return False  # Don't block any events

        # Install the event filter
        event_filter = PaneEventFilter(self, pane_name)
        view.installEventFilter(event_filter)
        self._pane_event_filters[pane_name] = event_filter
    def _update_coordinate_display(self): ...
    def _update_pane_borders(self) -> None:
        """Update visual borders to indicate the active pane with clear visual feedback."""
        if not hasattr(self, '_active_pane'):
            return

        # Get theme-appropriate colors
        is_dark_mode = self._is_dark_mode()
        if is_dark_mode:
            active_color = QColor(0, 122, 255, 180)  # Vibrant blue for dark mode
            active_border = QColor(0, 122, 255, 220)
            hover_color = QColor(0, 122, 255, 60)
        else:
            active_color = QColor(0, 122, 255, 40)   # Subtle blue for light mode
            active_border = QColor(0, 122, 255, 120)
            hover_color = QColor(0, 122, 255, 20)

        # Reset all borders to default
        default_style = """
            ImageView {
                border: 1px solid rgba(128, 128, 128, 0.3);
                border-radius: 4px;
                background: transparent;
            }
        """

        # Apply default styling to all panes
        if hasattr(self, 'src_view'):
            self.src_view.setStyleSheet(default_style)
        if hasattr(self, 'preview_view'):
            self.preview_view.setStyleSheet(default_style)
        if hasattr(self, 'res_view'):
            self.res_view.setStyleSheet(default_style)

        # Highlight active pane with enhanced visual feedback
        active_style = f"""
            ImageView {{
                border: 2px solid {active_border.name()};
                border-radius: 6px;
                background-color: {active_color.name()};
                position: relative;
            }}
            ImageView::hover {{
                background-color: {hover_color.name()};
            }}
        """

        # Apply active styling to the current active pane
        if self._active_pane == "source" and hasattr(self, 'src_view'):
            self.src_view.setStyleSheet(active_style)
        elif self._active_pane == "preview" and hasattr(self, 'preview_view'):
            self.preview_view.setStyleSheet(active_style)
        elif self._active_pane == "result" and hasattr(self, 'res_view'):
            self.res_view.setStyleSheet(active_style)

    def _on_pane_clicked(self, pane: str) -> None:
        """Handle pane click with proper focus management and visual feedback."""
        if not hasattr(self, '_active_pane') or self._active_pane != pane:
            self._active_pane = pane
            self._update_pane_borders()

            # Update status bar with context-aware message
            status_messages = {
                "source": "📷 Source pane active - Click and drag to select signature area",
                "preview": "🔍 Preview pane active - Selection preview with current settings",
                "result": "✨ Result pane active - Processed signature ready for export"
            }

            if hasattr(self, 'statusBar'):
                self.statusBar().showMessage(status_messages.get(pane, f"{pane.title()} pane active"))

            # Emit focus change signal for context menus
            if hasattr(self, 'pane_focus_changed'):
                self.pane_focus_changed.emit(pane)

    def _get_active_view(self) -> Optional['ImageView']:
        """Get the currently active image view for context operations."""
        if self._active_pane == "source":
            return getattr(self, 'src_view', None)
        elif self._active_pane == "preview":
            return getattr(self, 'preview_view', None)
        elif self._active_pane == "result":
            return getattr(self, 'res_view', None)
        return None

    def _on_pane_context_menu(self, view: 'ImageView', pane_name: str, pos: QPoint) -> None:
        """Show smart context menu based on the current pane and state."""
        menu = QMenu(cast(QWidget, self))
        def _shortcut(mac: str, other: str) -> str:
            return mac if sys.platform == "darwin" else other

        if pane_name == "source":
            # Source pane: image-related actions
            if hasattr(self, 'rotate_cw_btn') and self.rotate_cw_btn.isEnabled():
                rotate_cw_action = menu.addAction("↻ Rotate 90° CW")
                rotate_cw_action.triggered.connect(lambda: self.on_rotate(90))
                rotate_cw_action.setShortcut(QKeySequence(_shortcut("Meta+]", "Ctrl+]")))

                rotate_ccw_action = menu.addAction("↺ Rotate 90° CCW")
                rotate_ccw_action.triggered.connect(lambda: self.on_rotate(-90))
                rotate_ccw_action.setShortcut(QKeySequence(_shortcut("Meta+[", "Ctrl+[")))

                menu.addSeparator()

            if hasattr(self, 'fit_btn') and self.fit_btn.isEnabled():
                fit_action = menu.addAction("⛶ Fit to View")
                fit_action.triggered.connect(self._on_fit)
                fit_action.setShortcut(QKeySequence(_shortcut("Meta+0", "Ctrl+0")))

                reset_action = menu.addAction("⟲ Reset Viewport")
                reset_action.triggered.connect(self._on_reset_zoom)
                reset_action.setShortcut(QKeySequence(_shortcut("Meta+1", "Ctrl+1")))

            menu.addSeparator()

            # Image properties
            if hasattr(self, '_current_image_data') and self._current_image_data:
                props_action = menu.addAction("ℹ Image Properties")
                props_action.triggered.connect(self._show_image_properties)

        elif pane_name == "preview":
            # Preview pane: selection and processing actions
            if hasattr(self, 'src_view') and self.src_view.has_image() and self.src_view.has_selection():
                clear_action = menu.addAction("✕ Clear Selection")
                clear_action.triggered.connect(self.on_clear_selection)
                clear_action.setShortcut(QKeySequence("Delete"))

                # Add processing actions
                process_action = menu.addAction("⚡ Process Selection")
                process_action.triggered.connect(self.on_preview)
                process_action.setShortcut(QKeySequence(_shortcut("Meta+P", "Ctrl+P")))

                menu.addSeparator()

                # Threshold adjustments
                if hasattr(self, 'threshold_slider'):
                    auto_threshold_action = menu.addAction("🎯 Auto Threshold")
                    auto_threshold_action.triggered.connect(self._auto_adjust_threshold)

                # Color adjustments
                if hasattr(self, 'color_picker_btn'):
                    invert_action = menu.addAction("🔄 Invert Colors")
                    invert_action.triggered.connect(self._invert_colors)

        elif pane_name == "result":
            # Result pane: export and save actions
            if hasattr(self, '_last_result_png') and self._last_result_png:
                export_action = menu.addAction("💾 Export PNG...")
                export_action.triggered.connect(self.on_export)
                export_action.setShortcut(QKeySequence(_shortcut("Meta+E", "Ctrl+E")))

                copy_action = menu.addAction("📋 Copy to Clipboard")
                copy_action.triggered.connect(self._copy_result_to_clipboard)
                copy_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Copy))

                menu.addSeparator()

                save_lib_action = menu.addAction("📚 Save to Library")
                save_lib_action.triggered.connect(self.on_save_to_library)
                save_lib_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Save))

        # Common actions for all panes
        menu.addSeparator()

        # Zoom controls
        if hasattr(self, 'zoom_in_btn'):
            zoom_in_action = menu.addAction("🔍+ Zoom In")
            zoom_in_action.triggered.connect(self._on_zoom_in)
            zoom_in_action.setShortcut(QKeySequence(_shortcut("Meta++", "Ctrl++")))

            zoom_out_action = menu.addAction("🔍- Zoom Out")
            zoom_out_action.triggered.connect(self._on_zoom_out)
            zoom_out_action.setShortcut(QKeySequence(_shortcut("Meta+-", "Ctrl+-")))

        # Show the menu
        menu.exec(view.mapToGlobal(pos))

    if TYPE_CHECKING:
        # Tell mypy that at runtime, self will be a QWidget with these methods
        def palette(self) -> QPalette: ...
        def setWindowFilePath(self, path: str) -> None: ...

    def _setup_extraction_ui(self) -> None:
        extraction_tab = QWidget()
        extraction_layout = QHBoxLayout(extraction_tab)

        # Cast self to QWidget for type checking (self will be a QMainWindow at runtime)
        parent_widget = cast(QWidget, self)
        left_panel = QWidget(parent_widget)
        left_panel.setObjectName("extractionControlsPanel")
        left_panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        left_panel.setFixedWidth(300)  # Fixed width prevents compression
        controls = QVBoxLayout(left_panel)
        controls.setContentsMargins(16, 18, 16, 18)
        controls.setSpacing(10)

        # Store reference for responsive breakpoints
        self._left_panel = left_panel

        # Install event filter for responsive sizing
        left_panel.installEventFilter(self)

        # Compute section and pane label colors for both macOS and non-macOS
        palette = cast(QWidget, self).palette()
        group = palette.currentColorGroup()
        text_color = palette.color(group, QPalette.ColorRole.WindowText)

        # Detect dark vs light mode
        base_color = palette.color(group, QPalette.ColorRole.Window)
        is_dark_mode = base_color.lightness() < 120

        # Section labels: use translucent only in dark mode, opaque in light mode
        section_color = QColor(text_color)
        if is_dark_mode:
            section_color.setAlpha(180)  # Subtle in dark mode
        else:
            section_color.setAlpha(235)  # Nearly opaque for readability in light mode
        section_color_hex = _rgba(section_color)
        pane_label_color = _rgba(text_color)

        if sys.platform == "darwin":
            left_panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            border_color = palette.color(group, QPalette.ColorRole.Mid)

            if is_dark_mode:
                # Vibrant dark mode: deep, rich background with subtle blue tint
                panel_color = QColor(28, 28, 32, 248)
            else:
                # Vibrant light mode: bright, crisp white with warmth
                panel_color = QColor(251, 251, 253, 250)

            # Vibrant button styling with better contrast
            button_bg = QColor(panel_color)
            button_bg = button_bg.lighter(115 if is_dark_mode else 108)
            button_bg.setAlpha(220 if is_dark_mode else 180)
            button_bg_str = _rgba(button_bg)

            button_hover = QColor(button_bg)
            button_hover = button_hover.lighter(120 if is_dark_mode else 112)
            button_hover.setAlpha(min(button_hover.alpha() + 30, 255))
            button_hover_str = _rgba(button_hover)

            button_border = QColor(border_color)
            button_border = button_border.lighter(130 if is_dark_mode else 120)
            button_border.setAlpha(100 if is_dark_mode else 80)
            button_border_str = _rgba(button_border)

            disabled_bg = QColor(panel_color)
            disabled_bg.setAlpha(95)
            disabled_bg_str = _rgba(disabled_bg)

            # Disabled text: higher alpha in light mode for readability
            disabled_text = QColor(text_color)
            if is_dark_mode:
                disabled_text.setAlpha(120)  # More subtle in dark mode
            else:
                disabled_text.setAlpha(180)  # More readable in light mode (darker gray)
            disabled_text_str = _rgba(disabled_text)

            field_bg = QColor(panel_color)
            field_bg = field_bg.lighter(118)
            field_bg.setAlpha(185)
            field_bg_str = _rgba(field_bg)

            subtle_line = QColor(border_color)
            subtle_line.setAlpha(70)
            subtle_line_str = _rgba(subtle_line)

            left_panel.setStyleSheet(
                "QWidget#extractionControlsPanel {"
                f"  background-color: {_rgba(panel_color)};"
                f"  border-right: 1px solid {subtle_line_str};"
                f"  color: {text_color.name()};"
                "  font-size: 12px;"
                "}"
                "#extractionControlsPanel QLabel,"
                "#extractionControlsPanel QStatusBar,"
                "#extractionControlsPanel QToolButton {"
                "  background-color: transparent;"
                "  border: none;"
                f"  color: {text_color.name()};"
                "}"
                "#extractionControlsPanel QLineEdit,"
                "#extractionControlsPanel QComboBox {"
                f"  background-color: {field_bg_str};"
                f"  border: 1px solid {subtle_line_str};"
                "  border-radius: 6px;"
                "  padding: 6px 8px;"
                f"  color: {text_color.name()};"
                "  selection-background-color: rgba(0, 122, 255, 0.2);"
                "}"
                "#extractionControlsPanel QLineEdit:focus,"
                "#extractionControlsPanel QComboBox:focus {"
                f"  border: 2px solid {'#007AFF' if is_dark_mode else '#0051D5'};"
                "  outline: none;"
                "  background-color: rgba(255, 255, 255, 0.05);"
                "}"
                "#extractionControlsPanel QComboBox::drop-down {"
                "  width: 24px;"
                "  border: none;"
                "  background: transparent;"
                "}"
                "#extractionControlsPanel QComboBox::down-arrow {"
                "  image: none;"
                "  border-left: 4px solid transparent;"
                "  border-right: 4px solid transparent;"
                f"  border-top: 4px solid {text_color.name()};"
                "  margin-right: 6px;"
                "}"
                "#extractionControlsPanel QComboBox::down-arrow:hover {"
                f"  border-top-color: {'#007AFF' if is_dark_mode else '#0051D5'};"
                "}"
                "#extractionControlsPanel QComboBox QAbstractItemView {"
                f"  background-color: {field_bg_str};"
                f"  border: 1px solid {subtle_line_str};"
                "  border-radius: 6px;"
                "  selection-background-color: rgba(0, 122, 255, 0.2);"
                "  selection-color: inherit;"
                "  padding: 4px;"
                "}"
                "#extractionControlsPanel QComboBox QAbstractItemView::item {"
                "  padding: 6px 8px;"
                "  border-radius: 3px;"
                "  margin: 1px;"
                "}"
                "#extractionControlsPanel QComboBox QAbstractItemView::item:hover {"
                "  background-color: rgba(0, 122, 255, 0.1);"
                "}"
                "#extractionControlsPanel QComboBox QAbstractItemView::item:selected {"
                "  background-color: rgba(0, 122, 255, 0.2);"
                "}"
                "#extractionControlsPanel QListWidget:focus {"
                f"  border: 2px solid {'#007AFF' if is_dark_mode else '#0051D5'};"
                "}"
                "#extractionControlsPanel QListWidget::item:selected {"
                f"  background-color: {button_hover_str};"
                f"  color: {text_color.name()};"
                "}"
                "#extractionControlsPanel QSlider::groove:horizontal {"
                "  background: rgba(100, 100, 100, 180);"  # Visible gray groove
                "  height: 6px;"
                "  border-radius: 3px;"
                "  margin: 0;"
                "}"
                "#extractionControlsPanel QSlider::handle:horizontal {"
                "  background: rgba(255, 255, 255, 230);"  # Bright white handle
                "  border: 1px solid rgba(180, 180, 180, 200);"
                "  width: 16px;"
                "  height: 16px;"
                "  margin: -6px 0;"
                "  border-radius: 8px;"
                "}"
                # Standard QPushButton styling (excludes ModernMacButton which uses custom paintEvent)
                f"QWidget#extractionControlsPanel QPushButton:not([objectName='ModernMacButton']) {{ padding: 7px 14px; border-radius: 8px; border: 1px solid {button_border_str}; background-color: {button_bg_str}; color: {text_color.name()}; font-weight: 500; }}"
                f"QWidget#extractionControlsPanel QPushButton[primary=\"true\"]:not([objectName='ModernMacButton']) {{ background-color: {'#007AFF' if is_dark_mode else '#0051D5'}; color: white; border-color: {'#007AFF' if is_dark_mode else '#0051D5'}; }}"
                f"QWidget#extractionControlsPanel QPushButton[destructive=\"true\"]:not([objectName='ModernMacButton']) {{ background-color: #DC3545; color: white; border-color: #DC3545; }}"
                f"QWidget#extractionControlsPanel QPushButton[compact=\"true\"]:not([objectName='ModernMacButton']) {{ padding: 5px 10px; min-height: 26px; font-size: 12px; }}"
                f"QWidget#extractionControlsPanel QPushButton:not([objectName='ModernMacButton']):pressed {{ filter: brightness(0.95); }}"
                f"QWidget#extractionControlsPanel QPushButton:not([objectName='ModernMacButton']):focus {{ box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.35); }}"
                f"QWidget#extractionControlsPanel QPushButton:not([objectName='ModernMacButton']):hover {{ background-color: {button_hover_str}; }}"
                f"QWidget#extractionControlsPanel QPushButton[primary=\"true\"]:not([objectName='ModernMacButton']):hover {{ background-color: {'#0056CC' if is_dark_mode else '#0041A8'}; }}"
                f"QWidget#extractionControlsPanel QPushButton[destructive=\"true\"]:not([objectName='ModernMacButton']):hover {{ background-color: #C82333; }}"
                f"QWidget#extractionControlsPanel QPushButton:not([objectName='ModernMacButton']):focus {{ border: 2px solid {'#007AFF' if is_dark_mode else '#0051D5'}; outline: none; }}"
                f"QWidget#extractionControlsPanel QPushButton:disabled {{ color: {disabled_text_str}; background-color: {disabled_bg_str}; border-color: {subtle_line_str}; }}"
                f"QWidget#extractionControlsPanel QCheckBox {{ color: {text_color.name()}; spacing: 6px; }}"
            )

        self.open_btn = _create_button("", parent_widget, primary=True)
        set_button_icon(self.open_btn, "open", "Choose Image", use_emoji=False)
        self.open_btn.setObjectName("openFileButton")
        self.open_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.open_btn.clicked.connect(self.on_open)

        self.capture_btn = _create_button("Capture Signature", parent_widget)
        self.capture_btn.setObjectName("captureSignatureButton")
        self.capture_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.capture_btn.setToolTip("Open webcam and capture signature")
        self.capture_btn.clicked.connect(self.on_capture_signature)

        self.sample_btn = _create_button("Try with sample signature", parent_widget)
        self.sample_btn.setObjectName("sampleButton")
        self.sample_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.sample_btn.setToolTip("Load a sample signature image to try the extraction")
        self.sample_btn.clicked.connect(self._load_sample_image)

        controls.addWidget(self._make_section_label("Upload", section_color_hex, top_margin=0))
        controls.addWidget(self.open_btn)
        controls.addWidget(self.capture_btn)
        controls.addWidget(self.sample_btn)

        controls.addWidget(self._make_section_label("Batch Queue", section_color_hex))
        self.batch_add_btn = _create_button("Add to Queue", parent_widget)
        self.batch_add_btn.setObjectName("batchAddButton")
        self.batch_add_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.batch_add_btn.setToolTip("Add multiple image files to the processing queue")
        self.batch_add_btn.setProperty("compact", True)
        self.batch_add_btn.clicked.connect(self.on_add_to_batch_queue)

        self.batch_process_selected_btn = _create_button("Process Selected", parent_widget)
        self.batch_process_selected_btn.setObjectName("batchProcessSelectedButton")
        self.batch_process_selected_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.batch_process_selected_btn.setToolTip("Load the selected queue item into the extraction workspace")
        self.batch_process_selected_btn.setProperty("compact", True)
        self.batch_process_selected_btn.setEnabled(False)
        self.batch_process_selected_btn.clicked.connect(self.on_batch_process_selected)

        self.batch_process_next_btn = _create_button("Process Next", parent_widget)
        self.batch_process_next_btn.setObjectName("batchProcessNextButton")
        self.batch_process_next_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.batch_process_next_btn.setToolTip("Load the next queued item into the extraction workspace")
        self.batch_process_next_btn.setProperty("compact", True)
        self.batch_process_next_btn.clicked.connect(self.on_batch_process_next)

        self.batch_process_all_btn = _create_button("Process Queue", parent_widget, primary=True)
        self.batch_process_all_btn.setObjectName("batchProcessAllButton")
        self.batch_process_all_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.batch_process_all_btn.setToolTip("Process all queued items in order")
        self.batch_process_all_btn.setProperty("compact", True)
        self.batch_process_all_btn.clicked.connect(self.on_batch_process_all)

        self.batch_remove_btn = _create_button("Remove Selected", parent_widget)
        self.batch_remove_btn.setObjectName("batchRemoveButton")
        self.batch_remove_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.batch_remove_btn.setToolTip("Remove selected queue items")
        self.batch_remove_btn.setProperty("compact", True)
        self.batch_remove_btn.setEnabled(False)
        self.batch_remove_btn.clicked.connect(self.on_batch_remove_selected)

        self.batch_clear_btn = _create_button("Clear Queue", parent_widget, destructive=True)
        self.batch_clear_btn.setObjectName("batchClearButton")
        self.batch_clear_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.batch_clear_btn.setToolTip("Clear all queued items")
        self.batch_clear_btn.setProperty("compact", True)
        self.batch_clear_btn.clicked.connect(self.on_batch_clear)

        queue_actions = QGridLayout()
        queue_actions.setHorizontalSpacing(8)
        queue_actions.setVerticalSpacing(8)
        queue_actions.addWidget(self.batch_add_btn, 0, 0)
        queue_actions.addWidget(self.batch_process_selected_btn, 0, 1)
        queue_actions.addWidget(self.batch_process_next_btn, 1, 0)
        queue_actions.addWidget(self.batch_process_all_btn, 1, 1)
        queue_actions.addWidget(self.batch_remove_btn, 2, 0)
        queue_actions.addWidget(self.batch_clear_btn, 2, 1)
        queue_actions.setColumnStretch(0, 1)
        queue_actions.setColumnStretch(1, 1)
        controls.addLayout(queue_actions)

        self.batch_status_label = QLabel("Queue: 0 / 0 done")
        self.batch_status_label.setObjectName("batchStatusLabel")
        self.batch_status_label.setToolTip("Tracks queue progress during batch processing")
        self.batch_status_label.setStyleSheet("color: rgba(150, 150, 150, 0.85);")
        controls.addWidget(self.batch_status_label)

        self.batch_queue_list = QListWidget()
        self.batch_queue_list.setObjectName("batchQueueList")
        self.batch_queue_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.batch_queue_list.itemDoubleClicked.connect(self._on_batch_queue_item_open)
        self.batch_queue_list.itemSelectionChanged.connect(self._update_batch_queue_controls)
        self.batch_queue_list.setMinimumHeight(120)
        self.batch_queue_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.batch_queue_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        controls.addWidget(self.batch_queue_list)

        controls.addWidget(self._make_section_label("Extraction Mode", section_color_hex))
        self.mode_combo = QComboBox()
        self.mode_combo.setObjectName("modeCombo")
        self.mode_combo.addItems(["Standard (Threshold)", "Forensic (Ink Separation)"])
        self.mode_combo.setToolTip("Choose between fast thresholding or advanced AI clustering")
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        controls.addWidget(self.mode_combo)

        self.threshold_label = self._make_section_label("Threshold", section_color_hex)
        controls.addWidget(self.threshold_label)
        threshold_row = QHBoxLayout()
        self.threshold = QSlider(Qt.Orientation.Horizontal)
        self.threshold.setObjectName("thresholdSlider")
        self.threshold.setRange(0, 255)
        self.threshold.setValue(200)
        self.threshold.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        threshold_row.addWidget(self.threshold, 1)
        self.threshold_value_label = QLabel("200")
        self.threshold_value_label.setMinimumWidth(30)  # Reduced from 35 for better flexibility
        self.threshold_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.threshold_value_label.setToolTip("Current threshold value")
        threshold_row.addWidget(self.threshold_value_label, 0)

        # Auto-threshold badge - hidden until auto mode is enabled
        self.auto_threshold_badge = QLabel("")
        self.auto_threshold_badge.setMinimumWidth(45)  # Reduced from 50 for better flexibility
        self.auto_threshold_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.auto_threshold_badge.setStyleSheet(
            "border: 1px solid rgba(0, 122, 255, 80);"
            "background-color: rgba(0, 122, 255, 20);"
            "color: rgba(0, 122, 255, 200);"
            "border-radius: 6px;"
            "padding: 2px 6px;"
            "font-size: 10px;"
            "font-weight: 600;"
        )
        self.auto_threshold_badge.setVisible(False)
        threshold_row.addWidget(self.auto_threshold_badge, 0)

        self.auto_threshold_cb = QCheckBox("Auto Threshold")
        self.auto_threshold_cb.setObjectName("autoThresholdCheck")
        self.auto_threshold_cb.setToolTip("Compute an optimal threshold from the selected pixels")
        self.auto_threshold_cb.setChecked(False)
        self.auto_threshold_cb.stateChanged.connect(self._on_auto_threshold_toggled)
        threshold_row.addWidget(self.auto_threshold_cb, 0)

        self.auto_clean_cb = QCheckBox("Auto Clean")
        self.auto_clean_cb.setObjectName("autoCleanCheck")
        self.auto_clean_cb.setToolTip("Use adaptive thresholding and despeckle cleanup for scanned signatures")
        self.auto_clean_cb.setChecked(False)
        threshold_row.addWidget(self.auto_clean_cb, 0)
        controls.addLayout(threshold_row)

        self.color_label = QLabel("Color: #000000")
        self.color_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.pick_color_btn = _create_button(parent=parent_widget)
        set_button_icon(self.pick_color_btn, "color", "Pick Color", use_emoji=False)
        self.pick_color_btn.setObjectName("pickColorButton")
        self.pick_color_btn.clicked.connect(self.on_pick_color)
        color_row = QHBoxLayout()
        color_row.addWidget(self.color_label, 1)
        color_row.addWidget(self.pick_color_btn, 0)
        controls.addLayout(color_row)

        swatch_row = QHBoxLayout()
        swatch_row.setSpacing(8)
        swatch_row.addWidget(self._make_secondary_label("History", section_color_hex))
        self.color_history_layout = QHBoxLayout()
        self.color_history_layout.setSpacing(6)
        swatch_row.addLayout(self.color_history_layout)
        swatch_row.addWidget(self._make_secondary_label("Presets", section_color_hex))
        self.color_presets_layout = QHBoxLayout()
        self.color_presets_layout.setSpacing(6)
        swatch_row.addLayout(self.color_presets_layout)
        swatch_row.addStretch(1)
        controls.addLayout(swatch_row)

        controls.addWidget(self._make_section_label("View", section_color_hex))
        view_row1 = QHBoxLayout()
        self.zoom_in_btn = _create_button("+", parent_widget)
        self.zoom_in_btn.setObjectName("zoomInButton")
        self.zoom_in_btn.setToolTip("Zoom In (Ctrl/Cmd +)")
        self.zoom_out_btn = _create_button("−", parent_widget)
        self.zoom_out_btn.setObjectName("zoomOutButton")
        self.zoom_out_btn.setToolTip("Zoom Out (Ctrl/Cmd −)")
        self.zoom_combo = QComboBox()
        self.zoom_combo.setObjectName("zoomCombo")
        self.zoom_combo.setEditable(True)
        self.zoom_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.zoom_combo.addItems(["25%", "50%", "75%", "100%", "125%", "150%", "200%", "Fit"])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.setToolTip("Set zoom for the active pane. Enter a percentage or choose Fit.")
        self.zoom_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.zoom_combo.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.zoom_combo.setMinimumWidth(60)  # Ensure minimum width for usability
        self.zoom_combo.setMinimumContentsLength(4)  # Ensure uniform item sizes
        line_edit = self.zoom_combo.lineEdit()
        if line_edit is not None:
            line_edit.setPlaceholderText("Zoom")
            if sys.platform == "darwin":
                try:
                    line_edit.setClearButtonEnabled(True)
                except AttributeError:
                    pass
        view_row1.addWidget(self.zoom_in_btn)
        view_row1.addWidget(self.zoom_out_btn)
        view_row1.addWidget(self.zoom_combo)
        # Set compact property for zoom buttons for macOS compact variant
        self.zoom_in_btn.setProperty("compact", True)
        self.zoom_out_btn.setProperty("compact", True)
        controls.addLayout(view_row1)

        view_row2 = QHBoxLayout()
        self.fit_btn = _create_button("Fit", parent_widget)
        self.fit_btn.setObjectName("fitButton")
        self.fit_btn.setToolTip("Fit image (Ctrl/Cmd 1)")
        self.reset_view_btn = _create_button("Reset", parent_widget)
        self.reset_view_btn.setObjectName("resetViewButton")
        self.reset_view_btn.setToolTip("Reset view (Ctrl/Cmd 0)")
        view_row2.addWidget(self.fit_btn)
        view_row2.addWidget(self.reset_view_btn)
        controls.addLayout(view_row2)

        controls.addWidget(self._make_section_label("Image", section_color_hex))
        rotate_row = QHBoxLayout()
        self.rotate_ccw_btn = _create_button("↺", parent_widget)
        self.rotate_ccw_btn.setObjectName("rotateCCWButton")
        self.rotate_ccw_btn.setToolTip("Rotate CCW (Ctrl/Cmd [)")
        self.rotate_cw_btn = _create_button("↻", parent_widget)
        self.rotate_cw_btn.setObjectName("rotateCWButton")
        self.rotate_cw_btn.setToolTip("Rotate CW (Ctrl/Cmd ])")
        rotate_row.addWidget(self.rotate_ccw_btn)
        rotate_row.addWidget(self.rotate_cw_btn)
        controls.addLayout(rotate_row)

        controls.addWidget(self._make_section_label("Selection", section_color_hex))
        self.toggle_mode_btn = ElidingButton()
        self.toggle_mode_btn.setObjectName("toggleModeButton")
        self.toggle_mode_btn.setToolTip("Toggle between Select and Pan modes")
        self.toggle_mode_btn.setCheckable(True)
        self.toggle_mode_btn.setChecked(True)
        self.toggle_mode_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        set_button_icon(self.toggle_mode_btn, "mode_select", "Selection Mode: Select", use_emoji=False)
        self.clear_sel_btn = ElidingButton("Clear Selection")
        self.clear_sel_btn.setObjectName("clearSelectionButton")
        self.clear_sel_btn.setToolTip("Clear current selection")
        self.clear_sel_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.clear_sel_btn.setProperty("compact", True)
        self.auto_detect_btn = ElidingButton("Auto Detect")
        self.auto_detect_btn.setObjectName("autoDetectSelectionButton")
        self.auto_detect_btn.setToolTip("Auto-detect the signature region in the current image")
        self.auto_detect_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.auto_detect_btn.setProperty("compact", True)
        self.clean_session_btn = ElidingButton("Clean Viewport")
        self.clean_session_btn.setObjectName("cleanViewportButton")
        self.clean_session_btn.setToolTip("Clear the current upload and reset all panes")
        self.clean_session_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.clean_session_btn.setProperty("compact", True)
        controls.addWidget(self.toggle_mode_btn)
        controls.addWidget(self.auto_detect_btn)
        controls.addWidget(self.clear_sel_btn)
        controls.addWidget(self.clean_session_btn)

        # Health Score Badge
        self.health_badge = QLabel("Quality: Unknown")
        self.health_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.health_badge.setStyleSheet(
            "background-color: rgba(128, 128, 128, 0.2);"
            "color: #888;"
            "border-radius: 6px;"
            "padding: 4px;"
            "font-weight: bold;"
            "font-size: 11px;"
        )
        self.health_badge.setToolTip("Signature Quality Analysis (DPI, Blur, Contrast)")
        self.health_badge.setVisible(False)
        controls.addWidget(self.health_badge)

        controls.addWidget(self._make_section_label("Export & Save", section_color_hex))
        export_row_1 = QHBoxLayout()
        self.export_btn = _create_button("Export Signature", parent_widget, primary=True)
        self.export_btn.setObjectName("exportButton")
        self.export_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        export_icon = get_icon("export")
        if not export_icon.isNull():
            self.export_btn.setIcon(export_icon)
        self.export_btn.setToolTip("Export with advanced options (background, trim, format) - Ctrl/Cmd E")
        self.export_btn.clicked.connect(self.on_export)
        self.export_btn.setEnabled(False)
        self.copy_btn = _create_button("Copy", parent_widget, primary=True)
        self.copy_btn.setObjectName("copyButton")
        self.copy_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        copy_icon = get_icon("copy")
        if not copy_icon.isNull():
            self.copy_btn.setIcon(copy_icon)
        self.copy_btn.setToolTip("Copy result to clipboard (preserves transparency) - Ctrl/Cmd C")
        self.copy_btn.clicked.connect(self.on_copy)
        self.copy_btn.setEnabled(False)
        export_row_1.addWidget(self.export_btn)
        export_row_1.addWidget(self.copy_btn)
        controls.addLayout(export_row_1)

        export_row_2 = QHBoxLayout()
        self.save_to_library_btn = _create_button("Save to Library", parent_widget, primary=True)
        self.save_to_library_btn.setObjectName("saveToLibraryButton")
        self.save_to_library_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        save_icon = get_icon("save")
        if not save_icon.isNull():
            self.save_to_library_btn.setIcon(save_icon)
        self.save_to_library_btn.setToolTip("Quick save as PNG to local library")
        self.save_to_library_btn.clicked.connect(self.on_save_to_library)
        self.save_to_library_btn.setEnabled(False)
        
        self.save_to_vault_btn = _create_button("Save to Vault", parent_widget, primary=True)
        self.save_to_vault_btn.setObjectName("saveToVaultButton")
        self.save_to_vault_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        vault_icon = get_icon("lock")
        if not vault_icon.isNull():
            self.save_to_vault_btn.setIcon(vault_icon)
        self.save_to_vault_btn.setToolTip("Encrypt and store in secure local vault")
        self.save_to_vault_btn.clicked.connect(self.on_save_to_vault)
        self.save_to_vault_btn.setEnabled(False)

        self.export_json_btn = _create_button("Export JSON", parent_widget)
        self.export_json_btn.setObjectName("exportJsonButton")
        self.export_json_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        export_json_icon = get_icon("export")
        if not export_json_icon.isNull():
            self.export_json_btn.setIcon(export_json_icon)
        self.export_json_btn.setToolTip("Save selection, threshold, color, and session info to JSON")
        self.export_json_btn.clicked.connect(self.on_export_json)
        self.export_json_btn.setEnabled(False)
        export_row_2.addWidget(self.save_to_library_btn)
        export_row_2.addWidget(self.export_json_btn)
        controls.addLayout(export_row_2)

        self.overlay_preview_cb = QCheckBox("Overlay preview")
        self.overlay_preview_cb.setObjectName("overlayPreviewCheck")
        self.overlay_preview_cb.setToolTip("Show the extracted signature over the original crop in the preview pane")
        self.overlay_preview_cb.setChecked(True)
        controls.addWidget(self.overlay_preview_cb)

        self.sign_pdf_btn = _create_button("Sign a PDF with this", parent_widget)
        self.sign_pdf_btn.setObjectName("signPdfButton")
        self.sign_pdf_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.sign_pdf_btn.setToolTip("Switch to the PDF Signing tab and use this extracted signature")
        self.sign_pdf_btn.clicked.connect(self._sign_pdf_with_extracted)
        self.sign_pdf_btn.setEnabled(False)
        controls.addWidget(self.sign_pdf_btn)

        # Store section label for responsive hiding
        self._library_section_label = self._make_section_label("My Signatures", section_color_hex)
        controls.addWidget(self._library_section_label)
        self.library_list = QListWidget()
        self.library_list.setObjectName("libraryList")
        # Make selection more evident and allow multi-selection for deletion
        self.library_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.library_list.itemDoubleClicked.connect(self.on_library_item_open)
        self.library_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.library_list.customContextMenuRequested.connect(self.on_library_context_menu)
        self.library_list.itemSelectionChanged.connect(self._update_library_controls)
        self.library_list.setMinimumHeight(80)  # Reduced from 120 for better flexibility on small screens
        self.library_list.setTextElideMode(Qt.TextElideMode.ElideRight)  # Elide long filenames
        self.library_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Enhance selection visibility across platforms
        selection_style = (
            "QListWidget#libraryList {"
            "background-color: rgba(255, 255, 255, 20);"
            "border: 1px solid rgba(255, 255, 255, 30);"
            "border-radius: 8px;"
            "padding: 6px;"
            "}"
            "QListWidget#libraryList::item { height: 26px; border-radius: 8px; margin: 2px; padding: 2px 6px; }"
            "QListWidget#libraryList::item:selected {"
            " background-color: rgba(0,122,255,0.25);"
            " color: white;"
            " outline: none;"
            " border: 1px solid rgba(0,122,255,0.6);"
            "}"
            "QListWidget#libraryList::item:hover { background-color: rgba(255,255,255,0.12); }"
        )
        self.library_list.setStyleSheet(selection_style)
        controls.addWidget(self.library_list)

        self.delete_from_library_btn = _create_button("Delete Selected", parent_widget)
        self.delete_from_library_btn.setObjectName("deleteLibraryButton")
        delete_icon = get_icon("delete")
        if not delete_icon.isNull():
            self.delete_from_library_btn.setIcon(delete_icon)
        self.delete_from_library_btn.setToolTip("Remove the selected signature from My Signatures")
        self.delete_from_library_btn.clicked.connect(self.on_delete_selected_library)
        self.delete_from_library_btn.setEnabled(False)
        controls.addWidget(self.delete_from_library_btn)
        
        controls.addSpacing(20)
        
        # Add modern welcome/help text with clean design
        welcome_label = QLabel(
            "<span style='font-size: 14px; font-weight: 600; color: #ffffff; margin-bottom: 8px;'>Get Started</span><br><br>"
            "<span style='color: rgba(255, 255, 255, 0.9);'>1. Open or capture signature</span><br>"
            "<span style='color: rgba(255, 255, 255, 0.9);'>2. Select signature area</span><br>"
            "<span style='color: rgba(255, 255, 255, 0.9);'>3. Preview automatically</span><br>"
            "<span style='color: rgba(255, 255, 255, 0.9);'>4. Export when ready</span><br><br>"
            "<span style='color: rgba(255, 255, 255, 0.7); font-size: 12px; font-style: italic;'>💡 Adjust threshold and color for best results</span>"
        )
        welcome_label.setObjectName("instructionsPanel")  # Let theme system style it
        welcome_label.setWordWrap(True)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        welcome_label.setTextFormat(Qt.TextFormat.RichText)
        # Store Quick Start for responsive hiding
        self._welcome_label = welcome_label
        controls.addWidget(welcome_label)
        controls.addStretch(1)

        if sys.platform == "darwin":
            accent = cast(QWidget, self).palette().color(cast(QWidget, self).palette().currentColorGroup(), QPalette.ColorRole.Highlight).name()
            # Adapt button styling to dark/light mode
            if is_dark_mode:
                btn_border = "rgba(255, 255, 255, 13)"
                btn_bg = "rgba(255, 255, 255, 20)"
            else:
                btn_border = "rgba(0, 0, 0, 20)"
                btn_bg = "rgba(0, 0, 0, 8)"

            self.toggle_mode_btn.setStyleSheet(
                "QPushButton#toggleModeButton {"
                "padding: 6px 12px;"
                "border-radius: 8px;"
                f"border: 1px solid {btn_border};"
                f"background-color: {btn_bg};"
                "}"
                f"QPushButton#toggleModeButton:checked {{ background-color: {accent}; color: white; }}"
            )
            for btn in (
                self.open_btn,
                self.batch_add_btn,
                self.batch_process_selected_btn,
                self.batch_process_next_btn,
                self.batch_process_all_btn,
                self.batch_remove_btn,
                self.batch_clear_btn,
                self.pick_color_btn,
                self.zoom_in_btn,
                self.zoom_out_btn,
                self.fit_btn,
                self.reset_view_btn,
                self.rotate_ccw_btn,
                self.rotate_cw_btn,
                self.toggle_mode_btn,
                self.clear_sel_btn,
                self.clean_session_btn,
                self.export_btn,
                self.copy_btn,
                self.save_to_library_btn,
                self.export_json_btn,
                self.delete_from_library_btn,
            ):
                btn.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)

        self._images_layout = QVBoxLayout()
        self._src_container = QWidget()
        # Name the source container so theme can target the main canvas area
        self._src_container.setObjectName("sourcePanel")
        src_layout = QVBoxLayout(self._src_container)
        src_layout.setContentsMargins(0, 0, 0, 0)
        self.source_label = QLabel("Source")
        self.source_label.setObjectName("sourcePaneLabel")
        if sys.platform == "darwin":
            self.source_label.setStyleSheet(
                f"font-size: 13px; font-weight: 600; letter-spacing: 0.3px; color: {pane_label_color};"
            )
        src_layout.addWidget(self.source_label)
        self.src_view = ImageView(parent_widget)
        self.src_view.setObjectName("sourceImageView")
        self.src_view.setAccessibleName("Source image pane")
        self.src_view.setAccessibleDescription("Source image pane with selection tool. Click and drag to select signature area for extraction.")
        self._install_pane_click_filter(self.src_view, "source")
        self.src_view.fileDropped.connect(self._on_source_file_dropped)
        src_layout.addWidget(self.src_view)
        self._images_layout.addWidget(self._src_container, stretch=3)

        self.preview_container = QWidget()
         # Name the preview container for consistent theming
        self.preview_container.setObjectName("previewPanel")
        preview_layout = QVBoxLayout(self.preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_label = QLabel("Crop preview")
        self.preview_label.setVisible(False)
        self.preview_label.setObjectName("previewPaneLabel")
        if sys.platform == "darwin":
            self.preview_label.setStyleSheet(
                "font-size: 12px; font-weight: 600; letter-spacing: 0.4px;"
                f"color: {pane_label_color};"
            )
        preview_layout.addWidget(self.preview_label)
        self.preview_view = ImageView(self)
        self.preview_view.setObjectName("previewImageView")
        self.preview_view.setAccessibleName("Preview pane")
        self.preview_view.setAccessibleDescription("Preview of selected signature area")
        self.preview_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_view.toggle_selection_mode(False)
        self.preview_view.setVisible(False)
        self._install_pane_click_filter(self.preview_view, "preview")
        self._install_pane_click_filter(self.preview_container, "preview")
        preview_layout.addWidget(self.preview_view)
        # Add empty-state overlay for preview with modern styling
        self.preview_empty = QLabel("Select an area to see the preview")
        self.preview_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Use modern styling that matches the overall design theme
        self.preview_empty.setStyleSheet(
            "color: rgba(140, 140, 140, 0.8); "
            "font-size: 13px; "
            "font-weight: 500; "
            "padding: 32px; "
            "background: rgba(255, 255, 255, 0.02); "
            "border: 1px solid rgba(255, 255, 255, 0.08); "
            "border-radius: 8px; "
            "margin: 16px;"
        )
        self.preview_empty.setVisible(False)
        preview_layout.addWidget(self.preview_empty)
        self.preview_container.setVisible(False)

        result_container = QWidget()
        # Name the result container for consistent theming
        result_container.setObjectName("resultPanel")
        result_layout = QVBoxLayout(result_container)
        result_layout.setContentsMargins(0, 0, 0, 0)
        self.result_label = QLabel("Result")
        self.result_label.setVisible(False)
        self.result_label.setObjectName("resultPaneLabel")
        if sys.platform == "darwin":
            self.result_label.setStyleSheet(
                "font-size: 12px; font-weight: 600; letter-spacing: 0.4px;"
                f"color: {pane_label_color};"
            )
        result_layout.addWidget(self.result_label)
        self.res_view = ImageView(self)
        self.res_view.set_drag_source(True)
        self.res_view.setObjectName("resultImageView")
        self.res_view.setAccessibleName("Result image pane")
        self.res_view.setAccessibleDescription("Final processed signature ready for export")
        self.res_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.res_view.toggle_selection_mode(False)  # Disable selection mode for result view
        self._install_pane_click_filter(self.res_view, "result")
        self.res_view.setVisible(False)
        result_layout.addWidget(self.res_view)
        # Add empty-state overlay for result with modern styling
        self.result_empty = QLabel("Process selection to extract signature")
        self.result_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Use modern styling that matches the overall design theme
        self.result_empty.setStyleSheet(
            "color: rgba(140, 140, 140, 0.8); "
            "font-size: 13px; "
            "font-weight: 500; "
            "padding: 32px; "
            "background: rgba(255, 255, 255, 0.02); "
            "border: 1px solid rgba(255, 255, 255, 0.08); "
            "border-radius: 8px; "
            "margin: 16px;"
        )
        self.result_empty.setVisible(False)
        result_layout.addWidget(self.result_empty)

        self.preview_result_panel = GlassPanel(parent_widget)
        self.preview_result_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        stack_layout = QVBoxLayout(self.preview_result_panel)
        stack_layout.setContentsMargins(16, 16, 16, 16)
        stack_layout.setSpacing(12)
        stack_layout.addWidget(self.preview_container, 1)
        stack_layout.addWidget(result_container, 1)
        self._images_layout.addWidget(self.preview_result_panel, stretch=2)

        # Wrap left panel in scroll area for responsive behavior
        left_scroll = QScrollArea(parent_widget)
        left_scroll.setWidget(left_panel)
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        left_scroll.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        left_scroll.setFixedWidth(320)  # Slightly wider to account for scrollbar

        extraction_layout.addWidget(left_scroll, 0)
        extraction_layout.addLayout(self._images_layout, 1)

        self._extraction_tab_index = self.tab_widget.addTab(extraction_tab, "📝 Signature Extraction")

        self.zoom_in_btn.clicked.connect(self._on_zoom_in)
        self.zoom_out_btn.clicked.connect(self._on_zoom_out)
        self.fit_btn.clicked.connect(self._on_fit)
        self.reset_view_btn.clicked.connect(self._on_reset_zoom)
        self.toggle_mode_btn.clicked.connect(self.on_toggle_mode)
        self.clear_sel_btn.clicked.connect(self.on_clear_selection)
        self.clean_session_btn.clicked.connect(self.on_clean_session)
        self.rotate_cw_btn.clicked.connect(lambda: self.on_rotate(90))
        self.rotate_ccw_btn.clicked.connect(lambda: self.on_rotate(-90))
        self.zoom_combo.activated.connect(self._on_zoom_combo_activated)
        line_edit = self.zoom_combo.lineEdit()
        if line_edit is not None:
            line_edit.editingFinished.connect(self._on_zoom_combo_edit_finished)

        self.sel_info = QLabel("Selection: –")
        if sys.platform == "darwin":
            # Use semi-transparent version of text color instead of hardcoded white
            self.sel_info.setStyleSheet(f"font-size: 11px; color: {pane_label_color}; padding: 4px;")
        else:
            self.sel_info.setStyleSheet("font-size: 11px; color: #666; padding: 4px;")
        controls.addWidget(self.sel_info)

        self.source_coord_tooltips_cb = QCheckBox("Show coordinate tooltips")
        self.source_coord_tooltips_cb.setToolTip("Display image pixel coordinates while hovering or selecting")
        self.source_coord_tooltips_cb.setChecked(True)
        self.source_coord_tooltips_cb.stateChanged.connect(self._on_source_coord_tooltips_toggled)
        controls.addWidget(self.source_coord_tooltips_cb)

        # Set up logical tab order for keyboard navigation
        self._setup_tab_order()

        self._set_preview_panel_visible(False)
        self._init_extraction_state()

        # Initialize active pane visual indicators
        QTimer.singleShot(100, self._update_pane_borders)  # Delay to ensure UI is fully constructed

        # Initialize accessibility improvements
        QTimer.singleShot(200, self._setup_accessibility)  # Slight delay after UI construction

    def _init_extraction_state(self) -> None:
        self._color_hex = "#000000"
        self._update_color_ui()
        self._color_history: list[str] = []
        self._color_presets = ["#000000", "#007AFF", "#FF7A59", "#FFFFFF"]
        self._refresh_color_history()
        self._populate_color_presets()
        self._remember_color(self._color_hex, suppress_preview=True)
        self._last_result_png: bytes | None = None
        self._last_local_path: str | None = None
        self._current_image_data: bytes | None = None
        self._current_crop_preview_pixmap: QPixmap | None = None
        self._licensed = is_licensed()
        self._active_pane = "source"
        self._auto_threshold_enabled = False
        self._updating_zoom_combo = False
        self._last_valid_zoom_text = "100%"
        self._temp_files: list[str] = []
        self._backend_session_id: str | None = None
        self._batch_queue_items: list[dict[str, Any]] = []
        self._batch_current_index: int | None = None
        self._batch_auto_processing = False

        # Rotation coordinate mapping state
        self._current_rotation_angle = 0  # Track current rotation in degrees
        self._pre_rotation_zoom = 1.0     # Store zoom state before rotation
        self._pre_rotation_transform = None  # Store view transform before rotation
        self._pending_rotation_degrees = 0  # Store rotation angle for upload completion
        self._last_rotation_degrees = 0     # Store last rotation for feedback

        atexit.register(self._cleanup_temp_files)

        # Initialize visual feedback system
        self._feedback_timers = {}
        self._progress_dialogs = {}

        self._preview_timer = QTimer(cast(QWidget, self))
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self.on_preview)
        # Monotonic id guarding against stale background preview results
        # (e.g. two schedule_preview() calls firing before the first worker
        # finishes). Only the result matching the latest id is applied.
        self._preview_request_id = 0

        # Health check timer - check backend every 15 seconds
        self._health_timer = QTimer(cast(QWidget, self))
        self._health_timer.setInterval(15000)  # 15 seconds
        self._health_timer.timeout.connect(self._check_backend_health)
        self._health_timer.start()
        # Initialize health check retry counters
        self._health_check_attempt = 0
        self._max_health_check_attempts = 5
        # Initial health check
        self._check_backend_health()

        self.src_view.selectionChanged.connect(self.on_selection_changed)
        self.src_view.zoomChanged.connect(self._update_coordinate_display)
        self.src_view.viewChanged.connect(self._update_coordinate_display)
        self.src_view.zoomChanged.connect(self._update_pane_labels_with_zoom)
        self.preview_view.zoomChanged.connect(self._update_coordinate_display)
        self.preview_view.viewChanged.connect(self._update_coordinate_display)
        self.preview_view.zoomChanged.connect(self._update_pane_labels_with_zoom)
        self.res_view.zoomChanged.connect(self._update_coordinate_display)
        self.res_view.viewChanged.connect(self._update_coordinate_display)
        self.res_view.zoomChanged.connect(self._update_pane_labels_with_zoom)
        self.threshold.valueChanged.connect(self.on_adjustment_changed)
        self.auto_detect_btn.clicked.connect(self._auto_detect_current_region)
        self.auto_clean_cb.stateChanged.connect(lambda _: self.schedule_preview())

        self._update_action_states()
        self._refresh_library_list()
        self._refresh_batch_queue_list()
        self._update_library_controls()
        self._update_batch_queue_controls()
        self._update_pane_borders()

        # Apply initial breakpoint labels
        QTimer.singleShot(0, self._apply_left_panel_breakpoint)

    def _setup_tab_order(self) -> None:
        """Configure logical tab order for keyboard navigation through extraction controls."""
        # Main workflow order: Open → Mode toggle → Clear → View controls → Processing controls
        parent_widget = cast(QWidget, self)
        parent_widget.setTabOrder(self.open_btn, self.toggle_mode_btn)
        parent_widget.setTabOrder(self.toggle_mode_btn, self.capture_btn)
        parent_widget.setTabOrder(self.capture_btn, self.sample_btn)
        parent_widget.setTabOrder(self.sample_btn, self.batch_add_btn)
        parent_widget.setTabOrder(self.batch_add_btn, self.batch_process_selected_btn)
        parent_widget.setTabOrder(self.batch_process_selected_btn, self.batch_process_next_btn)
        parent_widget.setTabOrder(self.batch_process_next_btn, self.batch_process_all_btn)
        parent_widget.setTabOrder(self.batch_process_all_btn, self.batch_remove_btn)
        parent_widget.setTabOrder(self.batch_remove_btn, self.batch_clear_btn)
        parent_widget.setTabOrder(self.batch_clear_btn, self.clear_sel_btn)
        parent_widget.setTabOrder(self.clear_sel_btn, self.zoom_in_btn)
        parent_widget.setTabOrder(self.zoom_in_btn, self.zoom_out_btn)
        parent_widget.setTabOrder(self.zoom_out_btn, self.fit_btn)
        parent_widget.setTabOrder(self.fit_btn, self.reset_view_btn)
        parent_widget.setTabOrder(self.reset_view_btn, self.zoom_combo)
        parent_widget.setTabOrder(self.zoom_combo, self.rotate_ccw_btn)
        parent_widget.setTabOrder(self.rotate_ccw_btn, self.rotate_cw_btn)
        parent_widget.setTabOrder(self.rotate_cw_btn, self.pick_color_btn)
        parent_widget.setTabOrder(self.pick_color_btn, self.threshold)
        parent_widget.setTabOrder(self.threshold, self.auto_threshold_cb)
        parent_widget.setTabOrder(self.auto_threshold_cb, self.auto_clean_cb)
        parent_widget.setTabOrder(self.auto_clean_cb, self.copy_btn)
        parent_widget.setTabOrder(self.copy_btn, self.export_btn)
        parent_widget.setTabOrder(self.export_btn, self.save_to_library_btn)
        parent_widget.setTabOrder(self.save_to_library_btn, self.library_list)
        parent_widget.setTabOrder(self.library_list, self.delete_from_library_btn)
        parent_widget.setTabOrder(self.delete_from_library_btn, self.clean_session_btn)
        parent_widget.setTabOrder(self.clean_session_btn, self.source_coord_tooltips_cb)

        parent_qobject = cast(QObject, self)
        def _shortcut(mac: str, other: str) -> str:
            return mac if sys.platform == "darwin" else other

        shortcut_specs: list[tuple[ShortcutKey, Callable[[], None]]] = [
            (QKeySequence.StandardKey.Open, self.on_open),
            (QKeySequence.StandardKey.Copy, self.on_copy),
            (QKeySequence.StandardKey.ZoomIn, self._on_zoom_in),
            (QKeySequence.StandardKey.ZoomOut, self._on_zoom_out),
            (_shortcut("Meta+0", "Ctrl+0"), self._on_reset_zoom),
            (_shortcut("Meta+1", "Ctrl+1"), self._on_fit),
            (_shortcut("Meta+Shift+C", "Ctrl+Shift+C"), self.on_capture_signature),
            (_shortcut("Meta+E", "Ctrl+E"), self.on_export),
            (_shortcut("Meta+D", "Ctrl+D"), self.on_clear_selection),
            (_shortcut("Meta+Shift+X", "Ctrl+Shift+X"), self.on_clean_session),
            (_shortcut("Meta+T", "Ctrl+T"), self.on_toggle_mode),
            (_shortcut("Meta+Shift+A", "Ctrl+Shift+A"), self._auto_detect_current_region),
            (_shortcut("Meta+L", "Ctrl+L"), self.on_save_to_library),
        ]
        self._shortcuts: list[QShortcut] = []
        for key_spec, handler in shortcut_specs:
            shortcut = QShortcut(QKeySequence(key_spec), parent_qobject)
            shortcut.activated.connect(handler)
            self._shortcuts.append(shortcut)

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files created during rotation and library operations."""
        for temp_path in self._temp_files:
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    LOG.debug("Cleaned up temp file: %s", temp_path)
            except Exception as e:
                LOG.warning("Failed to clean up temp file %s: %s", temp_path, e)
        self._temp_files.clear()

    def _track_temp_file(self, file_path: str) -> None:
        """Track a temporary file for cleanup. Cleans up old temp files before adding new one."""
        # Clean up old temp files first (except _last_local_path which may still be in use)
        old_temps = [f for f in self._temp_files if f != self._last_local_path]
        for temp_path in old_temps:
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    LOG.debug("Cleaned up old temp file: %s", temp_path)
            except Exception as e:
                LOG.warning("Failed to clean up old temp file %s: %s", temp_path, e)
        self._temp_files = [f for f in self._temp_files if f == self._last_local_path]

        # Track the new temp file
        self._temp_files.append(file_path)

    def on_open(self):
        # If login is required, uncomment the following block:
        # if not self.session.access_token:
        #     QMessageBox.warning(self, "Not authenticated", "Please login first (Menu > Login)")
        #     return
        try:
            file_path = self._native_open_file("Select image", "Images (*.png *.jpg *.jpeg)")
            if not file_path:
                return
            self._load_image_from_path(file_path)
        except KeyboardInterrupt:
            # User cancelled dialog or operation
            self.status_bar.showMessage("Upload cancelled", 2000)
            return
        except Exception as e:
            if self._offer_camera_fallback(
                "Upload failed. We can capture a signature from your camera instead and continue with the same extraction pipeline."
            ):
                return
            # Immediately flip health indicator to offline on upload failure
            if hasattr(self, "backend_status_label"):
                self.backend_status_label.setText("Local service: Offline")
                self.backend_status_label.setStyleSheet("color: #cc0000; padding: 2px 8px;")
            self._handle_backend_exception(e, context="Upload failed")
            self.status_bar.showMessage("Upload failed", 3000)

    def on_add_to_batch_queue(self) -> None:
        """Select and enqueue files for batch processing."""
        try:
            file_paths = self._native_open_multiple_files("Select images for queue", "Images (*.png *.jpg *.jpeg)")
            if not file_paths:
                return
            self._add_to_batch_queue(file_paths)
        except Exception as e:
            LOG.error("Failed to add files to queue: %s", e, exc_info=True)
            self.status_bar.showMessage("Failed to add files to queue", 3000)

    def _add_to_batch_queue(self, file_paths: list[str]) -> None:
        if not file_paths:
            return

        normalized: list[str] = []
        for path in file_paths:
            if not path:
                continue
            if not os.path.exists(path):
                LOG.warning("Skipping missing file for batch queue: %s", path)
                continue
            if not os.path.isfile(path):
                LOG.warning("Skipping non-file entry for batch queue: %s", path)
                continue
            normalized.append(os.path.abspath(path))

        if not normalized:
            self.status_bar.showMessage("No valid files selected for queue", 2000)
            return

        existing_paths = {item.get("path") for item in self._batch_queue_items}
        added_count = 0
        for path in normalized:
            if path in existing_paths:
                self.status_bar.showMessage(f"Skipping duplicate path: {os.path.basename(path)}", 2000)
                continue
            self._batch_queue_items.append({
                "id": uuid4().hex,
                "path": path,
                "name": os.path.basename(path),
                "status": "pending",
                "session_id": None,
                "error": None,
            })
            existing_paths.add(path)
            added_count += 1

        if added_count:
            self._refresh_batch_queue_list()
            self.status_bar.showMessage(f"Added {added_count} file(s) to queue", 2500)

    def on_batch_remove_selected(self) -> None:
        selected_items = self.batch_queue_list.selectedItems()
        if not selected_items:
            return

        selected_indices = []
        for item in selected_items:
            data = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(data, int):
                selected_indices.append(data)

        if not selected_indices:
            return

        for idx in sorted(set(selected_indices), reverse=True):
            if 0 <= idx < len(self._batch_queue_items):
                self._batch_queue_items.pop(idx)

        self._batch_current_index = None
        self._refresh_batch_queue_list()
        self.status_bar.showMessage("Queue updated", 1500)

    def on_batch_clear(self) -> None:
        if not self._batch_queue_items:
            return
        self._batch_queue_items = []
        self._batch_current_index = None
        self._batch_auto_processing = False
        self.batch_process_all_btn.setText("Process Queue")
        self._refresh_batch_queue_list()
        self.status_bar.showMessage("Queue cleared", 2000)

    def on_batch_process_selected(self) -> None:
        selected = self.batch_queue_list.selectedItems()
        if not selected:
            return
        data = selected[0].data(Qt.ItemDataRole.UserRole)
        if not isinstance(data, int):
            return
        self._start_batch_queue_item(data)

    def on_batch_process_next(self) -> None:
        next_index = self._get_next_batch_index()
        if next_index is None:
            self.status_bar.showMessage("No pending queue items", 1500)
            return
        self._start_batch_queue_item(next_index)

    def on_batch_process_all(self) -> None:
        if self._batch_auto_processing:
            self._batch_auto_processing = False
            self.batch_process_all_btn.setText("Process Queue")
            self.status_bar.showMessage("Batch queue processing stopped", 1500)
            return

        next_index = self._get_next_batch_index(start_from=0)
        if next_index is None:
            self.status_bar.showMessage("No pending queue items", 2000)
            return

        self._batch_auto_processing = True
        self.batch_process_all_btn.setText("Stop Queue")
        self._start_batch_queue_item(next_index, auto_advance=True)

    def _on_batch_queue_item_open(self, item: QListWidgetItem) -> None:
        if not item:
            return
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, int):
            self._start_batch_queue_item(data)

    def _start_batch_queue_item(self, queue_index: int, *, auto_advance: bool = False) -> None:
        if queue_index < 0 or queue_index >= len(self._batch_queue_items):
            return

        item = self._batch_queue_items[queue_index]
        self._update_batch_item_status(queue_index, "processing")
        self._batch_current_index = queue_index
        self._refresh_batch_queue_controls()

        file_path = item.get("path", "")
        display = str(item.get("name", os.path.basename(file_path)))
        if not file_path:
            self._update_batch_item_status(queue_index, "failed", "Missing file path")
            self._continue_batch_queue_if_needed(auto_advance)
            return

        try:
            self.status_bar.showMessage(f"Loading {display} from queue", 0)
            session_id = self._load_image_from_path(file_path)
            item["session_id"] = session_id
            self._update_batch_item_status(queue_index, "done")
            self.status_bar.showMessage(f"Loaded: {display}", 1500)
        except Exception as exc:
            LOG.warning("Batch queue item failed: %s", exc)
            item["error"] = str(exc)
            self._update_batch_item_status(queue_index, "failed")
            self.status_bar.showMessage(f"Batch item failed: {display}", 2000)
        finally:
            self._continue_batch_queue_if_needed(auto_advance)

    def _continue_batch_queue_if_needed(self, auto_advance: bool) -> None:
        if not auto_advance or not self._batch_auto_processing:
            return

        next_index = self._get_next_batch_index(start_from=(self._batch_current_index or 0) + 1)
        if next_index is None:
            self._batch_auto_processing = False
            self.batch_process_all_btn.setText("Process Queue")
            self.status_bar.showMessage("Batch queue completed", 2200)
            self._refresh_batch_queue_controls()
            return

        QTimer.singleShot(250, lambda: self._start_batch_queue_item(next_index, auto_advance=True))

    def _get_next_batch_index(self, start_from: int = 0) -> int | None:
        for index in range(start_from, len(self._batch_queue_items)):
            if self._batch_queue_items[index].get("status") in {"pending", "failed"}:
                return index
        return None

    def _update_batch_item_status(self, queue_index: int, status: str, error: str | None = None) -> None:
        if queue_index < 0 or queue_index >= len(self._batch_queue_items):
            return
        item = self._batch_queue_items[queue_index]
        item["status"] = status
        if error is not None:
            item["error"] = error
        self._refresh_batch_queue_list()
        self._refresh_batch_queue_controls()

    def _refresh_batch_queue_list(self) -> None:
        self.batch_queue_list.clear()
        self.batch_queue_list.setDisabled(True)

        if not self._batch_queue_items:
            empty = QListWidgetItem("No queue items yet")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            empty.setForeground(Qt.GlobalColor.gray)
            self.batch_queue_list.addItem(empty)
            self.batch_queue_list.setEnabled(False)
        else:
            for idx, item in enumerate(self._batch_queue_items):
                status = str(item.get("status", "pending"))
                status_label = {
                    "pending": "○",
                    "processing": "◑",
                    "done": "✓",
                    "failed": "✗",
                }.get(status, "•")

                text = f"{status_label} {item.get('name', 'Unknown file')}"
                path = str(item.get("path", ""))
                queue_item = QListWidgetItem(text)
                queue_item.setData(Qt.ItemDataRole.UserRole, idx)
                queue_item.setData(Qt.ItemDataRole.UserRole + 1, item.get("id"))
                queue_item.setToolTip(
                    f"{path}\nStatus: {status}\n"
                    f"Session: {item.get('session_id') or 'N/A'}"
                    f"{'\\nError: ' + str(item.get('error')) if item.get('error') else ''}"
                )
                self.batch_queue_list.addItem(queue_item)
            self.batch_queue_list.setEnabled(True)

        self._refresh_batch_queue_controls()
        self._update_batch_status_label()

    def _refresh_batch_queue_controls(self) -> None:
        selected_items = self.batch_queue_list.selectedItems()
        selected_has_item = any(
            item.flags() & Qt.ItemFlag.ItemIsSelectable and isinstance(item.data(Qt.ItemDataRole.UserRole), int)
            for item in selected_items
        )
        has_pending_next = self._get_next_batch_index(start_from=0) is not None
        current_selected_status = None
        if selected_items:
            index = selected_items[0].data(Qt.ItemDataRole.UserRole)
            if isinstance(index, int) and 0 <= index < len(self._batch_queue_items):
                current_selected_status = self._batch_queue_items[index].get("status")
        selected_process_enabled = selected_has_item and (current_selected_status in {"pending", "failed"})

        self.batch_process_selected_btn.setEnabled(selected_process_enabled)
        self.batch_remove_btn.setEnabled(selected_has_item)
        self.batch_process_next_btn.setEnabled(has_pending_next)
        self.batch_process_all_btn.setEnabled(self._batch_auto_processing or has_pending_next)

    def _update_batch_queue_controls(self) -> None:
        """Backward-compatible alias for older signal wiring."""
        self._refresh_batch_queue_controls()

    def _update_batch_status_label(self) -> None:
        done_count = sum(1 for item in self._batch_queue_items if item.get("status") == "done")
        total_count = len(self._batch_queue_items)
        self.batch_status_label.setText(f"Queue: {done_count}/{total_count} done")

    def _offer_camera_fallback(self, message: str) -> bool:
        """Offer webcam capture when upload/load fails.

        Returns:
            True if the user chose to continue with camera capture.
        """
        try:
            reply = QMessageBox.question(
                cast(QWidget, self),
                "Upload unavailable",
                f"{message}\n\nWould you like to capture the signature from your webcam instead?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
        except Exception as error:
            LOG.debug("Camera fallback prompt failed: %s", error)
            return False

        if reply != QMessageBox.StandardButton.Yes:
            return False

        try:
            self.on_capture_signature()
        except Exception as error:
            LOG.debug("Camera fallback capture failed: %s", error)
            self._handle_backend_exception(error, context="Camera fallback failed")
            self.status_bar.showMessage("Capture fallback failed", 3000)
            return False

        return True

    def _load_sample_image(self) -> None:
        """Generate and load a sample signature image for first-time users."""
        try:
            from desktop_app.resources.sample_signature import generate_sample_signature
            file_path = generate_sample_signature()
            self.status_bar.showMessage("Loading sample signature...", 0)
            self._load_image_from_path(file_path)
            self.status_bar.showMessage("Sample loaded — try adjusting the threshold slider", 4000)
            self.sample_btn.setEnabled(False)
            self.sample_btn.setText("Sample loaded")
        except Exception as e:
            LOG.error(f"Failed to load sample image: {e}", exc_info=True)
            self.status_bar.showMessage(f"Failed to load sample: {str(e)[:50]}", 3000)

    def _load_image_from_path(self, file_path: str, *, auto_select: bool = True) -> str | None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        self._last_local_path = file_path

        with open(file_path, "rb") as f:
            self._current_image_data = f.read()

        if sys.platform == "darwin":
            cast(QWidget, self).setWindowFilePath(file_path)

        # Load and display image immediately (UI thread)
        image = self._load_image_with_exif(file_path)
        if image.isNull():
            raise RuntimeError("Could not load selected image into viewer")

        self.src_view.set_image(image)

        # Reset rotation state when opening new image
        self._current_rotation_angle = 0
        self._pre_rotation_zoom = 1.0
        self._pre_rotation_transform = None
        self._current_crop_preview_pixmap = None

        # Re-apply modern styling after image loading to maintain design consistency
        QTimer.singleShot(25, lambda: self._update_pane_borders())

        # Auto-fit with margin for better initial view
        QTimer.singleShot(50, lambda: self.src_view.fit(margin_percent=5.0))
        self._on_pane_clicked("source")
        self._set_backend_session_id(None)

        # Process image locally (offline-first approach)
        self.status_bar.showMessage("Loading image...", 0)
        self.open_btn.setEnabled(False)  # Disable during processing
        if hasattr(self, "capture_btn"):
            self.capture_btn.setEnabled(False)  # Disable alternate source while loading
        self.open_btn.setText("Loading...")

        try:
            # Use local extractor instead of backend API
            LOG.info(f"Creating local session for: {file_path}")
            session_id = self.local_extractor.create_session(file_path)
            LOG.info(f"Local session created successfully: {session_id}")
            
            # Simulate the upload finished payload for compatibility
            payload = {
                "id": session_id,
                "filename": os.path.basename(file_path),
                "file_path": file_path
            }
            
            # Call the existing upload finished handler
            loaded_session_id = self._on_upload_finished(file_path, payload, auto_select=auto_select)
            self._sync_backend_session(file_path)
            return loaded_session_id
        except Exception as e:
            LOG.error(f"Failed to create local session: {e}", exc_info=True)
            self.open_btn.setEnabled(True)
            if hasattr(self, "capture_btn"):
                self.capture_btn.setEnabled(True)
            self.open_btn.setText("Choose Image")  # Reset button text
            self.status_bar.showMessage(f"Failed to load image: {str(e)[:50]}", 5000)
            raise

    def _on_upload_finished(self, file_path: str, payload, *, auto_select: bool = True) -> str | None:
        """Handle completion of async upload."""
        self.open_btn.setEnabled(True)  # Re-enable
        if hasattr(self, "capture_btn"):
            self.capture_btn.setEnabled(True)  # Re-enable capture while extraction is ready
        self.open_btn.setText("Choose Image")  # Reset button text
        try:
            LOG.info(f"Upload finished. Payload type: {type(payload)}, Payload: {payload}")

            # Try multiple possible keys for session/image ID
            session_id = payload.get("id") or payload.get("session_id") or payload.get("image_id")

            # If nested in 'data' key
            if not session_id and "data" in payload:
                session_id = payload["data"].get("id") or payload["data"].get("session_id") or payload["data"].get("image_id")

            if not session_id:
                LOG.warning(f"No session id found in payload. Creating fallback local session. Payload was: {payload}")
                # Fallback to local session ID so UI doesn't break
                import time
                session_id = f"local-{int(time.time())}"

            LOG.info(f"Setting session_id to: {session_id}")
            self.session.set_extraction_session(session_id)
            LOG.info(f"Session ID set successfully: {self.session.session_id}")
            
            if hasattr(self, "session_id_label"):
                self.session_id_label.setText(f"Session: {session_id[:8]}...")
                self.session_id_label.setToolTip(f"Full session ID: {session_id}")
                LOG.info(f"Updated session_id_label to: Session: {session_id[:8]}...")
            else:
                LOG.warning("session_id_label not found - status bar not properly initialized")
                
            # Debug: check session state
            LOG.info(f"After upload - session.session_id: '{self.session.session_id}' (type: {type(self.session.session_id)})")
            
            self.status_bar.showMessage("Image loaded successfully", 3000)

            # Auto-detect signature region for direct loads; library items opt out.
            if auto_select:
                QTimer.singleShot(100, lambda: self._auto_select_signature(session_id))

            self._last_result_png = None
            self.preview_view.clear_image()
            self.res_view.scene().clear()
            self._current_crop_preview_pixmap = None
            self.export_btn.setEnabled(False)
            self.save_to_library_btn.setEnabled(False)
            # Keep panel mounted but show empty overlays
            self._set_preview_panel_visible(True)
            self.preview_label.setVisible(True)
            self.result_label.setVisible(True)
            self.preview_view.setVisible(False)
            self.res_view.setVisible(False)
            self.preview_empty.setVisible(True)
            self.result_empty.setVisible(True)

            self._update_action_states()
            self._update_view_actions_enabled()
            self._update_coordinate_display()
            self._update_pane_borders()
            return session_id
        except Exception as e:
            # Immediately flip health indicator to offline on upload failure
            if hasattr(self, "backend_status_label"):
                self.backend_status_label.setText("Local service: Offline")
                self.backend_status_label.setStyleSheet("color: #cc0000; padding: 2px 8px;")
            self._handle_backend_exception(e, context="Upload failed")
            self.status_bar.showMessage("Upload failed", 3000)
            return None

    def _on_upload_error(self, file_path: str, error) -> None:
        """Handle error in async upload."""
        LOG.error(f"Upload error for {file_path}: {error}")
        self.open_btn.setEnabled(True)  # Re-enable
        if hasattr(self, "capture_btn"):
            self.capture_btn.setEnabled(True)
        self.open_btn.setText("Choose Image")  # Reset button text

        if self._offer_camera_fallback(
            "Upload failed. We can capture a signature from your camera instead and continue with the same extraction workflow."
        ):
            return

        # Immediately flip health indicator to offline on upload failure
        if hasattr(self, "backend_status_label"):
            self.backend_status_label.setText("Local service: Offline")
            self.backend_status_label.setStyleSheet("color: #cc0000; padding: 2px 8px;")
        self._handle_backend_exception(error, context="Upload failed")
        self.status_bar.showMessage("Upload failed", 3000)

    def _set_backend_session_id(self, session_id: Optional[str]) -> None:
        self._backend_session_id = session_id if session_id else None

    def _session_id_from_upload(self, upload_result) -> Optional[str]:
        """Read session_id from upload response while supporting client stubs in tests."""
        if hasattr(upload_result, "session_id"):
            return str(upload_result.session_id)

        if isinstance(upload_result, dict):
            session_id = (
                upload_result.get("session_id")
                or upload_result.get("id")
                or upload_result.get("image_id")
            )
            if session_id:
                return str(session_id)

        return None

    def _sync_backend_session(self, file_path: str) -> None:
        """Upload/refresh the backend session for the current image when possible."""
        self._set_backend_session_id(None)

        if self.api_client.is_offline():
            LOG.debug("Skipping backend session sync because API client is offline")
            return

        try:
            result = self.api_client.upload_image(file_path)
            session_id = self._session_id_from_upload(result)
            if not session_id:
                raise ApiContractError("Upload response missing session identifier")

            self._set_backend_session_id(session_id)
            LOG.info("Backend upload session synced: %s", session_id)
            if hasattr(self, "backend_status_label"):
                self.backend_status_label.setText("● Local service: Online")
                self.backend_status_label.setStyleSheet("color: #2e7d32; padding: 2px 8px;")
                self.backend_status_label.setToolTip(
                    f"Local processing service active for session {session_id[:8]}..."
                )
        except Exception as exc:
            LOG.warning("Backend session sync failed: %s", exc)
            self._set_backend_session_id(None)
            if hasattr(self, "backend_status_label"):
                self.backend_status_label.setText("○ Local service: Offline")
                self.backend_status_label.setStyleSheet("color: #666666; padding: 2px 8px;")
                self.backend_status_label.setToolTip(
                    "Local companion service unavailable. Core document work remains available locally."
                )

    def _persist_selection_to_backend(
        self,
        *,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        threshold: int,
        color: str,
    ) -> None:
        """Best-effort sync of selection to backend session metadata."""
        if not self._backend_session_id:
            return
        if self.api_client.is_offline():
            return
        if not hasattr(self.api_client, "select_region"):
            return

        try:
            self.api_client.select_region(
                session_id=self._backend_session_id,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                color=color,
                threshold=threshold,
            )
            LOG.debug("Selection synchronized to backend session %s", self._backend_session_id)
        except Exception as exc:
            # Keep local processing as source of truth for immediate UX.
            LOG.warning("Backend selection sync failed (non-blocking): %s", exc)

    def on_capture_signature(self) -> None:
        """Capture signature from camera and run the same import pipeline."""
        try:
            dialog = _SignatureCaptureDialog(cast(QWidget, self))
            captured_path = dialog.capture_path()
            if not captured_path:
                self.status_bar.showMessage("Camera capture cancelled", 1500)
                return
            self._track_temp_file(captured_path)
            self._load_image_from_path(captured_path)
        except Exception as e:
            self._handle_backend_exception(e, context="Camera capture failed")
            self.status_bar.showMessage("Camera capture failed", 3000)

    def _on_source_file_dropped(self, file_path: str) -> None:
        try:
            self._load_image_from_path(file_path)
        except Exception as exc:
            if self._offer_camera_fallback("Upload via drag-and-drop failed."):
                return
            self._handle_backend_exception(exc, context="Upload via drag-and-drop failed")
            self.status_bar.showMessage("Upload failed", 3000)

    def _auto_select_signature(self, session_id: str) -> None:
        """Auto-detect and select the signature region on the loaded image."""
        try:
            region = self.local_extractor.auto_detect_signature(session_id)
            if region:
                x1, y1, x2, y2 = region
                self.src_view.set_selection_from_coords(x1, y1, x2, y2)
                self.status_bar.showMessage(f"Signature detected — adjust threshold to extract", 3000)
                # Trigger preview after a short delay
                QTimer.singleShot(300, self.schedule_preview)
            else:
                self.status_bar.showMessage("Select the signature area to extract", 4000)
        except Exception as e:
            LOG.debug(f"Auto-detect failed (non-critical): {e}")
            self.status_bar.showMessage("Select the signature area to extract", 4000)

    # Demo helpers for automated flows (no dialogs/backends)
    def demo_load_image(self, file_path: str) -> None:
        """Load an image into the Source pane without opening dialogs or calling backend.

        Assigns a deterministic session id suitable for offline demo flows.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        with open(file_path, "rb") as f:
            self._current_image_data = f.read()
        image = self._load_image_with_exif(file_path)
        if image.isNull():
            raise RuntimeError("Could not load image")
        self.src_view.set_image(image)

        # Re-apply modern styling after demo image loading
        QTimer.singleShot(25, lambda: self._update_pane_borders())

        self._on_pane_clicked("source")
        self.session.set_extraction_session("demo-session")
        self.status_bar.showMessage("Demo image loaded", 1500)
        self._update_action_states()
        self._update_coordinate_display()
        if sys.platform == "darwin":
            cast(QWidget, self).setWindowFilePath(file_path)

    def demo_create_sample_image(self, width: int = 400, height: int = 300, color: str = "#ffffff") -> None:
        """Create a simple in-memory image and load it into Source."""
        from PySide6.QtGui import QImage, QColor
        img = QImage(width, height, QImage.Format.Format_RGB32)
        img.fill(QColor(color))
        self._current_image_data = None
        self.src_view.set_image(img)

        # Re-apply modern styling after sample image creation
        QTimer.singleShot(25, lambda: self._update_pane_borders())

        self._on_pane_clicked("source")
        self.session.set_extraction_session("demo-session")
        self.status_bar.showMessage("Demo image created", 1200)
        self._update_action_states()
        self._update_coordinate_display()
        self._update_pane_borders()
        if sys.platform == "darwin":
            cast(QWidget, self).setWindowFilePath("")

    def demo_select_rect(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Programmatically set a selection rectangle in image/scene coordinates."""
        from PySide6.QtCore import QRectF, QPointF, QRect
        rect_scene = QRectF(QPointF(x1, y1), QPointF(x2, y2)).normalized()
        tl_view = self.src_view.mapFromScene(rect_scene.topLeft())
        br_view = self.src_view.mapFromScene(rect_scene.bottomRight())
        self.src_view._last_rect = QRect(tl_view, br_view).normalized()
        xs = [rect_scene.left(), rect_scene.right()]
        ys = [rect_scene.top(), rect_scene.bottom()]
        self.src_view._last_rect_scene_bounds = QRectF(QPointF(min(xs), min(ys)), QPointF(max(xs), max(ys)))
        # Trigger downstream preview/update like a user selection
        self.on_selection_changed(self.src_view._last_rect)

    def _get_source_selection(self, *, require_selection: bool = True) -> Tuple[int, int, int, int]:
        """Return the current source-image selection and validate it when required."""
        x1, y1, x2, y2 = self.src_view.selected_rect_image_coords()
        if x1 == x2 or y1 == y2:
            if require_selection:
                raise ValueError("No selection")
            return 0, 0, 0, 0
        if x1 > x2 or y1 > y2:
            raise ValueError(f"Invalid selection ({x1},{y1})→({x2},{y2})")
        return x1, y1, x2, y2

    def demo_generate_local_result(self) -> None:
        """Generate a PNG result locally from the current selection (no backend)."""
        from PySide6.QtCore import QBuffer, QIODevice
        if not self.src_view.has_image():
            raise RuntimeError("No source image")
        try:
            x1, y1, x2, y2 = self._get_source_selection()
        except ValueError:
            raise RuntimeError("No selection")
        cropped = self.src_view.crop_selection()
        if not cropped or cropped.isNull():
            raise RuntimeError("Invalid crop")
        buf = QBuffer()
        if not buf.open(QIODevice.OpenModeFlag.WriteOnly):
            raise RuntimeError("Buffer open failed")
        cropped.save(buf, b"PNG")
        # QBuffer.data() -> QByteArray; call .data() again to get Python bytes for mypy/runtime
        self._last_result_png = buf.data().data()
        buf.close()
        self.res_view.load_image_bytes(self._last_result_png)
        self._on_pane_clicked("result")
        self._update_action_states(preview_ready=True)
        self.status_bar.showMessage("Local result generated", 1500)
        self._update_coordinate_display()
        self._update_pane_borders()

    def _load_image_with_exif(self, file_path: str) -> QImage:
        """Load image and apply EXIF orientation correction."""
        try:
            # Use PIL to read EXIF and rotate if needed
            pil_img = cast(PILImage.Image, PILImage.open(file_path))
            
            # Check for EXIF orientation tag
            exif = pil_img.getexif()
            if exif:
                orientation = exif.get(0x0112)  # 274 is the Orientation tag
                if orientation:
                    # Apply rotation based on EXIF orientation
                    if orientation == 3:
                        pil_img = pil_img.rotate(180, expand=True)
                    elif orientation == 6:
                        pil_img = pil_img.rotate(270, expand=True)
                    elif orientation == 8:
                        pil_img = pil_img.rotate(90, expand=True)
            
            # Convert PIL image to QImage, preserving alpha if present
            has_alpha = pil_img.mode in ('RGBA', 'LA') or (pil_img.mode == 'P' and 'transparency' in pil_img.info)
            if has_alpha:
                pil_img = pil_img.convert("RGBA")
                data = pil_img.tobytes("raw", "RGBA")
                qimage = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
            else:
                pil_img = pil_img.convert("RGB")
                data = pil_img.tobytes("raw", "RGB")
                qimage = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGB888)
            return qimage.copy()  # Make a deep copy
        except Exception as e:
            # Fallback to basic QImage loading if EXIF fails
            LOG.warning("EXIF orientation correction failed: %s, using basic load", e)
            return QImage(file_path)

    def on_pick_color(self):
        # Initialize color picker with current color
        color_hex = self._native_color_picker(self._color_hex)
        if color_hex:
            self._color_hex = color_hex  # already #RRGGBB
            self._update_color_ui()
            self._last_result_png = None
            self.res_view.clear_image()
            self._update_action_states(preview_ready=False)
            self.schedule_preview()
            self._remember_color(self._color_hex)

    def _on_mode_changed(self, index: int):
        """Handle extraction mode change."""
        is_forensic = index == 1
        # Disable threshold controls in forensic mode as it uses clustering
        self.threshold.setEnabled(not is_forensic)
        self.threshold_label.setEnabled(not is_forensic)
        self.threshold_value_label.setEnabled(not is_forensic)
        self.auto_threshold_cb.setEnabled(not is_forensic)
        self.auto_clean_cb.setEnabled(not is_forensic)
        
        # Trigger preview update
        self.schedule_preview()

    def on_preview(self):
        """Process the selected region and show the result.

        Extraction, backend sync, and quality analysis run on a QThreadPool
        worker (see run_signature_preview) so the UI thread never blocks on
        cv2/K-Means work or a network call. Only UI reads/writes (selection
        coords, threshold widget, cursor/status) happen here on the main
        thread; everything CPU/IO-bound is dispatched to the worker and its
        result is applied by _on_preview_worker_finished.
        """
        self.status_bar.showMessage("Processing selection...", 0)
        if not self.session.session_id:
            QMessageBox.warning(cast(QWidget, self), "No image uploaded", "Please open & upload an image first")
            return
        # Selection
        try:
            x1, y1, x2, y2 = self._get_source_selection()
        except ValueError:
            self.status_bar.showMessage("Select an area on the source image to extract signature", 4000)
            LOG.warning("on_preview called with zero-size/invalid selection")
            return

        # Debug logging
        LOG.debug("on_preview called")
        LOG.debug("Session ID: %s", self.session.session_id)
        LOG.debug("Selection coords: (%d, %d) → (%d, %d)", x1, y1, x2, y2)
        LOG.debug("Color: %s, Threshold: %d", self._color_hex, self.threshold.value())

        if x1 == x2 or y1 == y2:
            self.status_bar.showMessage("Select an area on the source image to extract signature", 4000)
            LOG.warning("on_preview called with zero-size selection: (%d,%d)→(%d,%d)", x1, y1, x2, y2)
            return

        # Validate coordinates
        if x1 >= x2 or y1 >= y2:
            LOG.error("Invalid selection coordinates: x1=%d >= x2=%d or y1=%d >= y2=%d", x1, x2, y1, y2)
            QMessageBox.warning(cast(QWidget, self), "Invalid selection", "Selection coordinates are invalid. Please try again.")
            return

        # Process locally (offline-first approach)
        self.status_bar.showMessage("Processing...", 0)
        self.export_btn.setEnabled(False)  # Disable during processing
        cast(QWidget, self).setCursor(Qt.CursorShape.WaitCursor)

        import time
        start_time = time.time()

        # Check extraction mode
        is_forensic = self.mode_combo.currentIndex() == 1
        threshold_value = int(self.threshold.value())

        if not is_forensic and self.auto_threshold_cb.isChecked():
            # Auto-threshold reads/writes the threshold widget, which must
            # stay on the UI thread; resolve it before dispatching the worker.
            computed = self._compute_auto_threshold()
            if computed is not None:
                threshold_value = int(round(computed))
                self.threshold.blockSignals(True)
                self.threshold.setValue(threshold_value)
                self.threshold.blockSignals(False)

        self._preview_request_id += 1
        request_id = self._preview_request_id

        persist_fn = partial(
            self._persist_selection_to_backend,
            x1=x1, y1=y1, x2=x2, y2=y2,
            threshold=threshold_value,
            color=self._color_hex,
        )
        worker_func = partial(
            run_signature_preview,
            extractor=self.local_extractor,
            is_forensic=is_forensic,
            session_id=self.session.session_id,
            x1=x1, y1=y1, x2=x2, y2=y2,
            threshold_value=threshold_value,
            color_hex=self._color_hex,
            auto_clean=self.auto_clean_cb.isChecked(),
            persist_fn=persist_fn,
            request_id=request_id,
            start_time=start_time,
        )

        # IMPORTANT: Store runner as instance variable to prevent garbage collection
        self._preview_runner = AsyncRunner(worker_func)
        self._preview_runner.finished.connect(self._on_preview_worker_finished)
        self._preview_runner.error.connect(self._on_preview_worker_error)
        dispatch(self._preview_runner)

    def _on_preview_worker_finished(self, result: dict) -> None:
        """Apply a completed preview worker result on the UI thread."""
        request_id = result.get("request_id")
        if request_id != self._preview_request_id:
            LOG.debug(
                "Ignoring stale preview result (request %s, current %s)",
                request_id, self._preview_request_id,
            )
            return

        start_time = result.get("start_time", 0.0)

        if not result.get("ok"):
            exc = result.get("error")
            LOG.error(f"Local processing failed: {exc}")
            self.export_btn.setEnabled(True)
            cast(QWidget, self).unsetCursor()
            self.status_bar.showMessage("Processing failed", 3000)
            self._on_process_error(exc, start_time)
            return

        png_bytes = result["png_bytes"]
        self._on_process_finished(png_bytes, start_time)
        cast(QWidget, self).unsetCursor()

        quality = result.get("quality")
        if quality is not None:
            self._update_health_badge(quality)
        else:
            LOG.error(f"Quality analysis failed: {result.get('quality_error')}")
            self.health_badge.setVisible(False)

    def _on_preview_worker_error(self, exc: Exception) -> None:
        """Handle a failure in the worker harness itself.

        run_signature_preview captures all extraction/analysis failures into
        its returned dict, so this only fires for a genuine bug in the
        harness/closure (e.g. a TypeError building the call). There is no
        request_id available here to check staleness, so this always resets
        the UI defensively.
        """
        LOG.error(f"Unexpected preview worker failure: {exc}")
        self.export_btn.setEnabled(True)
        cast(QWidget, self).unsetCursor()
        self.status_bar.showMessage("Processing failed", 3000)

    def _update_health_badge(self, quality: dict):
        """Update the health badge based on quality metrics."""
        rating = quality.get("rating", "Unknown")
        issues = quality.get("issues", [])
        score = quality.get("score", 0)
        
        self.health_badge.setVisible(True)
        
        if rating == "Excellent":
            color = "#2e7d32" # Green
            bg = "rgba(46, 125, 50, 0.15)"
            text = "✓ Excellent Quality"
        elif rating == "Good":
            color = "#f57f17" # Orange
            bg = "rgba(245, 127, 23, 0.15)"
            text = "⚠ Good Quality"
        else:
            color = "#c62828" # Red
            bg = "rgba(198, 40, 40, 0.15)"
            text = "✕ Poor Quality"
            
        self.health_badge.setText(text)
        self.health_badge.setStyleSheet(
            f"background-color: {bg};"
            f"color: {color};"
            "border-radius: 6px;"
            "padding: 4px;"
            "font-weight: bold;"
            "font-size: 11px;"
            f"border: 1px solid {color};"
        )
        
        tooltip = f"Score: {score}/100\n"
        if issues:
            tooltip += "\nIssues:\n" + "\n".join([f"- {i}" for i in issues])
        else:
            tooltip += "\nNo issues detected."
            
        self.health_badge.setToolTip(tooltip)

    def _on_process_finished(self, png_bytes, start_time: float) -> None:
        """Handle completion of async processing."""
        try:
            import time
            elapsed = time.time() - start_time
            LOG.debug("Received %d bytes from backend in %.2f seconds", len(png_bytes), elapsed)

            self._last_result_png = png_bytes
            self.res_view.load_image_bytes(png_bytes)
            if self.overlay_preview_cb.isChecked() and self._current_crop_preview_pixmap is not None:
                overlay_pixmap = self._build_overlay_preview_pixmap(self._current_crop_preview_pixmap, png_bytes)
                if overlay_pixmap is not None:
                    self.preview_view.set_image(overlay_pixmap.toImage())
                    self.preview_view.fit()
            # Show result view, hide empty overlay
            self.result_empty.setVisible(False)
            self.res_view.setVisible(True)
            # Enable actions now that a preview exists
            self._update_action_states(preview_ready=True)
            self.status_bar.showMessage("Preview ready", 2000)
        except Exception as e:
            LOG.error("Processing failed: %s", e, exc_info=True)
            # Immediately flip health indicator to offline on processing failure
            if hasattr(self, "backend_status_label"):
                self.backend_status_label.setText("Local service: Offline")
                self.backend_status_label.setStyleSheet("color: #cc0000; padding: 2px 8px;")
            self._handle_backend_exception(e, context="Process failed")
            self.status_bar.showMessage("Processing failed", 3000)

    def _on_process_error(self, error, start_time: float) -> None:
        """Handle error in async processing."""
        LOG.error("Processing failed: %s", error, exc_info=True)
        # Immediately flip health indicator to offline on processing failure
        if hasattr(self, "backend_status_label"):
            self.backend_status_label.setText("Local service: Offline")
            self.backend_status_label.setStyleSheet("color: #cc0000; padding: 2px 8px;")
        self._handle_backend_exception(error, context="Process failed")
        self.status_bar.showMessage("Processing failed", 3000)

    def _handle_escape_cancel(self) -> None:
        """Cancel transient interaction state and clear source selection."""
        self.on_clear_selection()
        if hasattr(self, "pdf_viewer") and self.pdf_viewer:
            resetter = getattr(self.pdf_viewer, "clear_signature_placement", None)
            if callable(resetter):
                resetter()
        if hasattr(self, "_reset_pdf_signature_selection_state"):
            self._reset_pdf_signature_selection_state(reset_controls=True)
        self.status_bar.showMessage("Selection cleared", 1200)

    def on_clear_selection(self):
        self.src_view.clear_selection()
        self.sel_info.setText("Selection: –")
        self.preview_view.clear_image()
        self._current_crop_preview_pixmap = None
        self.export_btn.setEnabled(False)
        self.save_to_library_btn.setEnabled(False)
        # Don't collapse panel - just show empty overlays
        self.preview_view.setVisible(False)
        self.preview_empty.setVisible(True)
        self.res_view.setVisible(False)
        self.result_empty.setVisible(True)
        self._update_view_actions_enabled()
        self._update_coordinate_display()

    def _check_backend_health(self) -> None:
        """Check backend availability with graceful degradation."""
        # Check if we have a backend manager
        if hasattr(self, 'backend_manager') and self.backend_manager:
            # Use backend manager for health check
            backend_available = self.backend_manager.is_available()
            
            if backend_available:
                self._on_backend_online()
            else:
                # Try to start backend if auto-start is enabled
                if self.backend_manager.auto_start:
                    if self.backend_manager.start():
                        self._on_backend_online()
                    else:
                        self._on_backend_offline("Backend auto-start failed")
                else:
                    self._on_backend_offline("Backend not running")
        else:
            # Fallback to API client health check
            def _do_health_check():
                try:
                    if hasattr(self.api_client, "health_check"):
                        return self.api_client.health_check(timeout=2.0)
                    else:
                        return True, {"status": "assumed-healthy"}
                except Exception as e:
                    return False, {"error": str(e)}

            # IMPORTANT: Store runner as instance variable to prevent garbage collection
            self._health_check_runner = AsyncRunner(_do_health_check)
            self._health_check_runner.finished.connect(self._on_health_check_finished)
            self._health_check_runner.error.connect(self._on_health_check_error)
            dispatch(self._health_check_runner)
    
    def _on_backend_online(self) -> None:
        """Handle backend online state."""
        self._backend_online = True
        
        if hasattr(self, "backend_status_label"):
            self.backend_status_label.setText(f"● {companion_status_label('online')}")
            self.backend_status_label.setStyleSheet("color: #2e7d32; padding: 2px 8px;")
            self.backend_status_label.setToolTip(companion_tooltip("online"))
        
        # Enable cloud features if any
        self._update_cloud_features_availability(True)
    
    def _on_backend_offline(self, reason: str = "Backend unavailable") -> None:
        """Handle backend offline state with graceful degradation."""
        self._backend_online = False
        
        if hasattr(self, "backend_status_label"):
            self.backend_status_label.setText(f"○ {companion_status_label('offline')}")
            self.backend_status_label.setStyleSheet("color: #666666; padding: 2px 8px;")
            self.backend_status_label.setToolTip(companion_tooltip("offline"))
        
        # Disable cloud features but keep core functionality
        self._update_cloud_features_availability(False)
        
        # Show user-friendly message about offline mode
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage("Local mode - core document work available", 3000)
    
    def _update_cloud_features_availability(self, available: bool) -> None:
        """Update availability of cloud-dependent features.
        
        Args:
            available: True if cloud features should be enabled
        """
        # Update API client offline mode
        if hasattr(self, 'api_client'):
            self.api_client.set_offline_mode(not available)
        
        # Here you can disable/enable specific cloud features
        # For now, core features work offline, so no changes needed
        pass

    def _on_health_check_finished(self, result) -> None:
        """Handle completion of async health check."""
        ok, payload = result
        self._backend_online = bool(ok)

        if hasattr(self, "backend_status_label"):
            if ok:
                # Success - reset attempt counter
                self._health_check_attempt = 0

                # Extract version if available
                version = payload.get("version", "unknown") if isinstance(payload, dict) else "unknown"

                self.backend_status_label.setText("● Local service: Online")
                self.backend_status_label.setStyleSheet("color: #2e7d32; padding: 2px 8px;")
                self.backend_status_label.setToolTip(
                    f"Connected to {self.api_client.base_url}\n"
                    f"Version: {version}\n"
                    f"Click to open health page"
                )
                # Make clickable
                self.backend_status_label.mousePressEvent = lambda e: self._open_url(f"{self.api_client.base_url}/health")

                # Enable actions that depend on backend
                self.open_btn.setEnabled(True)
                if hasattr(self, "capture_btn"):
                    self.capture_btn.setEnabled(True)
            else:
                # Failure - check if we should retry
                if self._health_check_attempt < self._max_health_check_attempts:
                    # Exponential backoff: 100ms, 500ms, 1s, 2s, 5s
                    delays = [100, 500, 1000, 2000, 5000]
                    delay = delays[min(self._health_check_attempt - 1, len(delays) - 1)]

                    LOG.debug("Health check failed (attempt %d/%d), retrying in %dms",
                             self._health_check_attempt, self._max_health_check_attempts, delay)

                    # Schedule retry
                    QTimer.singleShot(delay, self._check_backend_health)
                else:
                    # Max attempts reached - mark as offline
                    self.backend_status_label.setText(f"● {companion_status_label('offline')}")
                    self.backend_status_label.setStyleSheet("color: #c62828; padding: 2px 8px;")
                    self.backend_status_label.setToolTip(companion_tooltip("offline"))
                    # Make clickable
                    self.backend_status_label.mousePressEvent = lambda e: self._open_document("docs/HELP.md")
                    # Core local functionality stays available even when backend is unreachable.
                    self.open_btn.setEnabled(True)
                    if hasattr(self, "capture_btn"):
                        self.capture_btn.setEnabled(True)

    def _on_health_check_error(self, error) -> None:
        """Handle health check exception."""
        LOG.error("Health check error: %s", error, exc_info=True)
        # Treat as failed check
        self._on_health_check_finished((False, {"error": str(error)}))

    def _handle_backend_exception(self, e: Exception, *, context: str = "Error") -> None:
        """Show user-friendly errors for backend/network issues."""
        # Default detail
        detail = companion_status_message("offline")
        title = context

        # Map common request exceptions to helpful messages
        cls = e.__class__
        mod = getattr(cls, "__module__", "")
        name = getattr(cls, "__name__", "")
        if mod.startswith("requests") and name in {"ConnectionError", "Timeout"}:
            detail = companion_status_message("offline")
        elif isinstance(e, FileNotFoundError):
            detail = "The selected local resource is unavailable. Choose it again or continue with another source."

        QMessageBox.critical(cast(QWidget, self), title, detail)
        # Update backend status indicator after errors
        try:
            self._check_backend_health()
        except Exception:
            pass

    def on_clean_session(self):
        if not (self.src_view.has_image() or self.preview_view.has_image() or self.res_view.has_image() or self.session.session_id):
            return
        self.src_view.clear_image()
        self.preview_view.clear_image()
        self.res_view.clear_image()
        if self._batch_auto_processing:
            self._batch_auto_processing = False
            self.batch_process_all_btn.setText("Process Queue")
            self._refresh_batch_queue_controls()
        self._current_crop_preview_pixmap = None
        # Keep panel mounted to prevent layout jump - show empty overlays instead
        self.preview_view.setVisible(False)
        self.preview_empty.setVisible(True)
        self.res_view.setVisible(False)
        self.result_empty.setVisible(True)
        self.sel_info.setText("Selection: –")
        self.session.clear_extraction_session()
        self._set_backend_session_id(None)
        if hasattr(self, "session_id_label"):
            self.session_id_label.setText("No session")
            self.session_id_label.setToolTip("")
        self._last_result_png = None
        self._current_image_data = None
        self._last_local_path = None
        self.status_bar.showMessage("Viewport cleaned", 3000)
        self._update_action_states()
        self._update_view_actions_enabled()
        self._update_coordinate_display()
        if sys.platform == "darwin":
            cast(QWidget, self).setWindowFilePath("")

    def on_selection_changed(self, _rect) -> None:
        # Update selection info and crop preview
        x1, y1, x2, y2 = self._get_source_selection(require_selection=False)
        w, h = max(0, x2 - x1), max(0, y2 - y1)
        if w > 0 and h > 0:
            self.sel_info.setText(f"Selection: {w}×{h} at ({x1},{y1})")
            # Show preview/result panes now that we have a selection
            self._set_preview_panel_visible(True)

            # Reset preview and result view rotations when making a new selection
            # This ensures the crop preview is shown in the correct orientation
            self.preview_view.setTransform(QTransform())
            self.preview_view._rotation = 0.0
            self.res_view.setTransform(QTransform())
            self.res_view._rotation = 0.0

            cropped = self.src_view.crop_selection()
            if cropped and not cropped.isNull():
                LOG.debug("Crop preview size: %d×%d", cropped.width(), cropped.height())
                # Convert once and reuse the QPixmap for both the cached
                # overlay-compositing source and the visible preview, instead
                # of converting the same QImage twice (this path runs on
                # every selection-drag frame).
                self._current_crop_preview_pixmap = QPixmap.fromImage(cropped)
                self.preview_view.set_pixmap(self._current_crop_preview_pixmap)
                self.preview_view.fit()
                # Show preview view, hide empty overlay
                self.preview_view.setVisible(True)
                self.preview_empty.setVisible(False)
            else:
                self._current_crop_preview_pixmap = None
                self.preview_view.clear_image()
            if self._auto_threshold_enabled:
                if self._apply_auto_threshold():
                    self.status_bar.showMessage("Selection changed - scheduling preview (auto threshold)", 1000)
                    self.schedule_preview()
                else:
                    self.status_bar.showMessage("Selection changed - scheduling preview (auto threshold failed)", 1000)
                    self.schedule_preview()
            else:
                self.status_bar.showMessage("Selection changed - scheduling preview", 1000)
                self.schedule_preview()
        else:
            self.sel_info.setText("Selection: –")
            self.preview_view.clear_image()
            self._current_crop_preview_pixmap = None
            self.save_to_library_btn.setEnabled(False)
            # Don't collapse panel - just show empty overlay
            self.preview_view.setVisible(False)
            self.preview_empty.setVisible(True)
        self._update_view_actions_enabled()
        self._update_coordinate_display()

    def on_adjustment_changed(self, value: int) -> None:
        # Update the threshold value label and badge
        if self._auto_threshold_enabled:
            self.threshold_value_label.setText(str(value))
            self.auto_threshold_badge.setText(f"AUTO")
            self.auto_threshold_badge.setVisible(True)
        else:
            self.threshold_value_label.setText(str(value))
            self.auto_threshold_badge.setVisible(False)
        # Debounce live preview when threshold changes
        self.schedule_preview()

    def schedule_preview(self):
        # Only schedule if we have a valid selection and an uploaded session
        LOG.info(f"schedule_preview called - checking session_id: '{self.session.session_id}' (type: {type(self.session.session_id)}, bool: {bool(self.session.session_id)})")
        if not self.session.session_id:
            LOG.warning(f"schedule_preview blocked: no session id - self.session.session_id is: {repr(self.session.session_id)}")
            self.status_bar.showMessage("Preview not scheduled - no session", 1500)
            return
        x1, y1, x2, y2 = self._get_source_selection(require_selection=False)
        if x1 == x2 or y1 == y2:
            LOG.warning(f"schedule_preview blocked: zero size selection ({x1},{y1})→({x2},{y2})")
            self.status_bar.showMessage("Make a selection to see preview", 1500)
            return
        # Debounce 200ms - stop any existing timer first to prevent restart issues
        self._preview_timer.stop()
        LOG.info(f"Scheduling preview in 200ms for selection ({x1},{y1})→({x2},{y2})")
        self.status_bar.showMessage("Updating preview...", 1000)
        self._preview_timer.start(200)

    def _on_auto_threshold_toggled(self, state: int):
        enabled = bool(state)
        self._auto_threshold_enabled = enabled
        self.threshold.setDisabled(enabled)

        if enabled:
            applied = self._apply_auto_threshold()
            if applied:
                # Show badge in auto mode
                self.threshold_value_label.setText(str(self.threshold.value()))
                self.auto_threshold_badge.setText("AUTO")
                self.auto_threshold_badge.setVisible(True)
                self.schedule_preview()
            else:
                self.status_bar.showMessage("Auto threshold needs a selection", 2000)
        else:
            # Back to manual mode - hide badge
            self.threshold_value_label.setText(str(self.threshold.value()))
            self.auto_threshold_badge.setVisible(False)
            self.status_bar.showMessage("Manual threshold control enabled", 2000)
            self.schedule_preview()

    def _apply_auto_threshold(self) -> bool:
        computed = self._compute_auto_threshold()
        if computed is None:
            return False
        value = int(round(computed))
        # Avoid unnecessary updates if value unchanged
        if value == self.threshold.value():
            return True
        self.threshold.blockSignals(True)
        self.threshold.setValue(value)
        self.threshold.blockSignals(False)
        self.status_bar.showMessage(f"Auto threshold applied: {value}", 2000)
        return True

    def _compute_auto_threshold(self) -> Optional[float]:
        cropped = self.src_view.crop_selection()
        if not cropped or cropped.isNull():
            return None
        buffer = QBuffer()
        if not buffer.open(QIODevice.OpenModeFlag.WriteOnly):
            return None
        cropped.save(buffer, "PNG")
        # Convert QByteArray to Python bytes explicitly for type checkers
        data = buffer.data().data()
        buffer.close()
        try:
            pil_img = PILImage.open(io.BytesIO(data))
            gray = pil_img.convert("L")
            arr = np.array(gray)
            if arr.size == 0:
                return None
            return float(self._otsu_threshold(arr))
        except Exception as exc:
            logging.warning("Auto threshold computation failed: %s", exc)
            return None

    def _otsu_threshold(self, gray: np.ndarray) -> int:
        # Optimize for large crops: downscale to max 512px on longest side before computing Otsu
        # This keeps latency predictable while maintaining accuracy
        h, w = gray.shape[:2] if gray.ndim >= 2 else (gray.size, 1)
        max_dim = max(h, w)
        if max_dim > 512:
            scale = 512 / max_dim
            new_h, new_w = int(h * scale), int(w * scale)
            if new_h > 0 and new_w > 0:
                from PIL import Image as PILImage
                gray_img = PILImage.fromarray(gray.astype(np.uint8))
                gray = np.array(gray_img.resize((new_w, new_h), PILImage.Resampling.BILINEAR))

        histogram, _ = np.histogram(gray, bins=256, range=(0, 256))
        total = gray.size
        if total == 0:
            return 0
        sum_total = float(np.dot(np.arange(256), histogram))
        sum_background = 0.0
        weight_background = 0
        max_variance = 0.0
        threshold = 0

        for level in range(256):
            weight_background += histogram[level]
            if weight_background == 0:
                continue
            weight_foreground = total - weight_background
            if weight_foreground == 0:
                break
            sum_background += level * histogram[level]
            mean_background = sum_background / weight_background
            mean_foreground = (sum_total - sum_background) / weight_foreground
            variance_between = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2
            if variance_between > max_variance:
                max_variance = variance_between
                threshold = level

        return threshold

    def on_toggle_mode(self):
        """Toggle between selection mode and pan mode."""
        current_mode = self.src_view._selection_mode
        new_mode = not current_mode
        self.src_view.toggle_selection_mode(new_mode)
        if new_mode:
            self.toggle_mode_btn.setChecked(True)
            set_button_icon(self.toggle_mode_btn, 'mode_select', "Selection Mode: Select", use_emoji=False)
        else:
            self.toggle_mode_btn.setChecked(False)
            set_button_icon(self.toggle_mode_btn, 'mode_pan', "Pan Mode", use_emoji=False)

    def _on_source_coord_tooltips_toggled(self, state: int) -> None:
        """Toggle coordinate tooltips in Source, Preview, and Result image views."""
        enabled = bool(state)
        if hasattr(self, 'src_view') and self.src_view:
            self.src_view.enable_coordinate_tooltips(enabled)
        if hasattr(self, 'preview_view') and self.preview_view:
            self.preview_view.enable_coordinate_tooltips(enabled)
        if hasattr(self, 'res_view') and self.res_view:
            self.res_view.enable_coordinate_tooltips(enabled)

    def on_export(self):
        """Open the export dialog with professional options."""
        if not self._last_result_png:
            return
        if not self._require_export_gate("Export"):
            return
        
        # Define SVG generator callback
        def svg_generator() -> str:
            x1, y1, x2, y2 = self._get_source_selection()
            return self.local_extractor.process_selection_svg(
                session_id=self.session.session_id,
                x1=x1, y1=y1, x2=x2, y2=y2,
                threshold=int(self.threshold.value()),
                color=self._color_hex,
                auto_clean=self.auto_clean_cb.isChecked()
            )
        
        self.status_bar.showMessage("Opening export dialog...", 1000)
        dialog = ExportDialog(self._last_result_png, self, svg_generator=svg_generator)
        if dialog.exec():
            self.status_bar.showMessage(f"Exported successfully", 3000)
        else:
            self.status_bar.showMessage("Export cancelled", 2000)
    
    def on_save_to_vault(self):
        """Encrypt and save the current signature to the local vault."""
        if not self._last_result_png:
            return
            
        try:
            # Get metadata
            source_name = os.path.basename(self.session.file_path) if self.session.file_path else "Unknown"
            
            # Get health score if available
            health_score = 0
            health_rating = "Unknown"
            if hasattr(self, 'health_badge') and self.health_badge.isVisible():
                tooltip = self.health_badge.toolTip()
                # Parse score from tooltip "Score: 80/100"
                import re
                match = re.search(r"Score: (\d+)/100", tooltip)
                if match:
                    health_score = int(match.group(1))
                    
                text = self.health_badge.text()
                if "Excellent" in text: health_rating = "Excellent"
                elif "Good" in text: health_rating = "Good"
                elif "Poor" in text: health_rating = "Poor"
            
            meta = {
                "source_name": source_name,
                "health_score": health_score,
                "health_rating": health_rating,
                "extraction_mode": self.mode_combo.currentText() if hasattr(self, 'mode_combo') else "Standard",
                "auto_threshold": bool(self.auto_threshold_cb.isChecked()),
                "auto_clean": bool(self.auto_clean_cb.isChecked()),
            }
            
            # Access vault from main window (self is mixed into MainWindow)
            if hasattr(self, 'vault'):
                self.vault.store_signature(self._last_result_png, meta)
                
                # Refresh vault tab
                if hasattr(self, 'vault_tab'):
                    self.vault_tab.refresh_list()
                    
                self.status_bar.showMessage("Signature encrypted and saved to Vault", 3000)
                
                # Visual feedback
                orig_text = self.save_to_vault_btn.text()
                self.save_to_vault_btn.setText("Saved!")
                QTimer.singleShot(1500, lambda: self.save_to_vault_btn.setText(orig_text))
            else:
                LOG.error("Vault not initialized")
                QMessageBox.critical(cast(QWidget, self), "Error", "Vault not initialized")
                
        except Exception as e:
            LOG.error(f"Failed to save to vault: {e}")
            QMessageBox.critical(cast(QWidget, self), "Vault Error", f"Failed to save signature: {e}")

    def on_export_json(self):
        """Export basic metadata as JSON (selection, color, threshold, session, image size)."""
        try:
            x1, y1, x2, y2 = self._get_source_selection()
            img = self.src_view.image()
            meta = {
                "session_id": self.session.session_id or "",
                "selection": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                "threshold": int(self.threshold.value()),
                "color": self._color_hex,
                "auto_threshold": bool(self.auto_threshold_cb.isChecked()),
                "auto_clean": bool(self.auto_clean_cb.isChecked()),
                "image_size": {"width": int(img.width()) if img else 0, "height": int(img.height()) if img else 0}
            }
            import json
            default_name = "signature.json"
            file_path = self._native_save_file("Export Metadata As", default_name, "JSON (*.json)")
            if not file_path:
                return
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
            self.status_bar.showMessage(f"Saved metadata: {file_path}", 3000)
        except Exception as e:
            QMessageBox.critical(cast(QWidget, self), "Export JSON Failed", str(e))
    
    def on_save_to_library(self):
        """Quick save to library with default PNG format and metadata."""
        if not self._require_export_gate("Save to Library"):
            return
        if getattr(self, "tab_widget", None) and self.tab_widget.currentIndex() != getattr(self, "_extraction_tab_index", 0):
            return
        if not self._last_result_png:
            return
        self.status_bar.showMessage("Saving to library...", 0)
        try:
            # Collect metadata from current extraction
            metadata = None
            try:
                x1, y1, x2, y2 = self._get_source_selection()
                img = self.src_view.image()
                metadata = {
                    "session_id": self.session.session_id or "",
                    "selection": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                    "threshold": int(self.threshold.value()),
                    "color": self._color_hex,
                    "auto_threshold": bool(self.auto_threshold_cb.isChecked()),
                    "auto_clean": bool(self.auto_clean_cb.isChecked()),
                    "image_size": {"width": int(img.width()) if img else 0, "height": int(img.height()) if img else 0}
                }
            except Exception:
                pass  # Save without metadata if extraction fails
            
            saved_path = lib.save_png_to_library(self._last_result_png, metadata)
            self.status_bar.showMessage(f"Saved: {saved_path}", 4000)
            self._refresh_library_list()
            if hasattr(self, "_refresh_toolbar_action_states"):
                self._refresh_toolbar_action_states()
        except Exception as e:
            QMessageBox.critical(cast(QWidget, self), "Save failed", str(e))
            self.status_bar.showMessage("Save failed", 3000)

    def _sign_pdf_with_extracted(self) -> None:
        """Save extracted signature and switch to the canonical PDF Signing tab."""
        if not self._last_result_png:
            self.status_bar.showMessage("Extract a signature first", 2000)
            return
        try:
            import tempfile
            tmp = tempfile.mktemp(suffix=".png")
            with open(tmp, "wb") as f:
                f.write(self._last_result_png)
            # Switch to the canonical PDF Signing tab
            pdf_tab_index = -1
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == "📄 PDF Signing":
                    pdf_tab_index = i
                    break
            if pdf_tab_index >= 0:
                self.tab_widget.setCurrentIndex(pdf_tab_index)
                pdf_tab = self.tab_widget.widget(pdf_tab_index)
                if hasattr(pdf_tab, 'set_signature_image'):
                    pdf_tab.set_signature_image(tmp)
                self.status_bar.showMessage("Signature ready — open a PDF to sign", 4000)
            else:
                self.status_bar.showMessage("PDF Signing tab not found", 3000)
        except Exception as e:
            LOG.error(f"Failed to pass signature to PDF tab: {e}")
            self.status_bar.showMessage("Could not switch to PDF Signing", 3000)
    
    def _refresh_library_list(self):
        """Refresh library list in Extraction tab with coordinate tooltips."""
        self.library_list.clear()
        items = list(lib.list_items(limit=50))
        if not items:
            # Show friendly empty state with guidance
            empty1 = QListWidgetItem("📝 No signatures in your library yet")
            empty1.setFlags(Qt.ItemFlag.NoItemFlags)
            empty1.setForeground(Qt.GlobalColor.gray)
            empty1.setToolTip("After extracting a signature preview, click 'Save to Library' to add it here.")
            self.library_list.addItem(empty1)

            empty2 = QListWidgetItem("Tip: Hover saved items to see coordinates & metadata")
            empty2.setFlags(Qt.ItemFlag.NoItemFlags)
            empty2.setForeground(Qt.GlobalColor.gray)
            self.library_list.addItem(empty2)
        else:
            for it in items:
                text = f"{it.display_name}  ·  {it.pretty_time}"
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, it.path)
                item.setToolTip(it.tooltip_text)  # Add coordinate tooltip
                self.library_list.addItem(item)
        self._update_library_controls()

    def _update_library_controls(self):
        has_selection = bool(self.library_list.selectedItems())
        self.delete_from_library_btn.setEnabled(has_selection)

    def _set_preview_panel_visible(self, visible: bool) -> None:
        """Show or collapse the preview/result stack - natural resize to content."""
        self.preview_result_panel.setVisible(visible)
        self.preview_container.setVisible(visible)
        self.preview_label.setVisible(visible)
        self.preview_view.setVisible(visible)
        self.result_label.setVisible(visible)
        self.res_view.setVisible(visible)
        if visible:
            self.preview_result_panel.updateGeometry()
            self.preview_result_panel.adjustSize()

    def on_library_item_open(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        if not path:
            return
        try:
            self._load_image_from_path(path, auto_select=False)
            self.status_bar.showMessage("Loaded into Source from library", 3000)
        except Exception as e:
            self._handle_backend_exception(e, context="Open failed")

    def _on_library_upload_finished(self, tmp_path: str, payload) -> None:
        """Handle completion of async library item upload."""
        try:
            session_id = payload.get("id") or ""
            if not session_id:
                raise RuntimeError("Upload succeeded but no session id returned")

            self.session.set_extraction_session(session_id)
            if hasattr(self, "session_id_label"):
                self.session_id_label.setText(f"Session: {session_id[:8]}...")
                self.session_id_label.setToolTip(f"Full session ID: {session_id}")

            # Clear any previous result/preview; user can select and it will auto-preview
            self._last_result_png = None
            self.preview_view.clear_image()
            self.res_view.scene().clear()
            self._current_crop_preview_pixmap = None
            # Keep stack visible with empty overlays
            self._set_preview_panel_visible(True)
            self.preview_label.setVisible(True)
            self.result_label.setVisible(True)
            self.preview_view.setVisible(False)
            self.res_view.setVisible(False)
            self.preview_empty.setVisible(True)
            self.result_empty.setVisible(True)

            self._update_action_states(preview_ready=False)
            self._update_view_actions_enabled()
            self._update_library_controls()
            self.status_bar.showMessage("Loaded into Source from library", 3000)
        except Exception as e:
            if hasattr(self, "backend_status_label"):
                self.backend_status_label.setText("Local service: Offline")
                self.backend_status_label.setStyleSheet("color: #cc0000; padding: 2px 8px;")
            self._handle_backend_exception(e, context="Open failed")
            self.status_bar.showMessage("Upload failed", 3000)

    def _on_library_upload_error(self, tmp_path: str, error) -> None:
        """Handle error in async library item upload."""
        if hasattr(self, "backend_status_label"):
            self.backend_status_label.setText("Local service: Offline")
            self.backend_status_label.setStyleSheet("color: #cc0000; padding: 2px 8px;")
        self._handle_backend_exception(error, context="Open failed")
        self.status_bar.showMessage("Upload failed", 3000)

    def on_library_context_menu(self, pos: QPoint):
        item = self.library_list.itemAt(pos)
        if not item:
            return
        path = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(cast(QWidget, self))
        open_act = menu.addAction("Open")
        del_act = menu.addAction("Delete")
        act = menu.exec(self.library_list.mapToGlobal(pos))
        if act == open_act:
            self.on_library_item_open(item)
        elif act == del_act:
            result = lib.delete_item_with_result(path)
            if result.primary_deleted:
                self._refresh_library_list()
                message = deletion_outcome_message(result.status)
                self.status_bar.showMessage(message, 3000)
                if not result.cleanup_complete:
                    QMessageBox.warning(cast(QWidget, self), "Cleanup needs attention", message)
            else:
                QMessageBox.warning(cast(QWidget, self), "Delete failed", deletion_outcome_message(result.status))
        self._update_library_controls()

    def on_delete_selected_library(self):
        items = self.library_list.selectedItems()
        if not items:
            return
        confirm = QMessageBox.question(
            self,
            "Delete signature",
            "Remove the selected signature from My Signatures?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        failed = 0
        incomplete = 0
        for item in items:
            path = item.data(Qt.ItemDataRole.UserRole)
            if not path:
                continue
            result = lib.delete_item_with_result(path)
            if not result.primary_deleted:
                failed += 1
            elif not result.cleanup_complete:
                incomplete += 1

        self._refresh_library_list()
        self._update_library_controls()

        if failed or incomplete:
            parts = []
            if failed:
                parts.append(f"{failed} signature(s) could not be removed.")
            if incomplete:
                parts.append(f"{incomplete} signature(s) were removed but need cleanup review.")
            QMessageBox.warning(cast(QWidget, self), "Deletion needs attention", " ".join(parts))
            return

        self.status_bar.showMessage(deletion_outcome_message("deleted"), 3000)

    def on_rotate(self, degrees: int):
        """Rotate the active pane. Source rotates image+session, others rotate display only."""
        active = self._active_pane

        if active == "source":
            if not self._current_image_data:
                QMessageBox.information(cast(QWidget, self), "No image", "Open an image first.")
                return

            # Backup state before rotation in case upload fails
            old_image_data = self._current_image_data
            old_local_path = self._last_local_path
            old_session_id = self.session.session_id
            old_backend_session_id = self._backend_session_id
            self._set_backend_session_id(None)
            self._rotation_backup = {
                'old_image_data': old_image_data,
                'old_local_path': old_local_path,
                'old_session_id': old_session_id,
                'old_backend_session_id': old_backend_session_id,
            }

            try:
                from tempfile import NamedTemporaryFile
                from PIL import Image as PILImage

                with PILImage.open(io.BytesIO(self._current_image_data)) as pil_img:
                    pil_img.load()
                    has_transparency = (
                        "A" in pil_img.getbands()
                        or "transparency" in pil_img.info
                    )
                    if has_transparency:
                        working = pil_img.convert("RGBA")
                        rotated = working.rotate(-degrees, expand=True, fillcolor=(0, 0, 0, 0))
                    else:
                        if pil_img.mode not in ("RGB", "L"):
                            working = pil_img.convert("RGB")
                        else:
                            working = pil_img
                        rotated = working.rotate(-degrees, expand=True)

                buffer = io.BytesIO()
                rotated.save(buffer, format="PNG")
                png_bytes = buffer.getvalue()

                tmp = NamedTemporaryFile(suffix=".png", delete=False)
                tmp.write(png_bytes)
                tmp.flush()
                tmp.close()

                self._current_image_data = png_bytes
                self._last_local_path = tmp.name
                self._track_temp_file(tmp.name)

                # Process rotation locally (offline-first approach)
                self.status_bar.showMessage("Processing rotated image...", 0)
                self.rotate_cw_btn.setEnabled(False)  # Disable during processing
                self.rotate_ccw_btn.setEnabled(False)

                try:
                    # Store rotation angle for use in completion handler
                    self._pending_rotation_degrees = degrees

                    # Use local extractor for rotation
                    new_session_id = self.local_extractor.rotate_image(self.session.session_id, degrees)

                    # Simulate the rotation upload finished payload for compatibility
                    payload = {
                        "id": new_session_id,
                        "filename": os.path.basename(tmp.name),
                        "file_path": tmp.name
                    }

                    # Call the existing rotation finished handler
                    self._on_rotate_upload_finished(tmp.name, payload)
                    
                except Exception as e:
                    LOG.error(f"Local rotation failed: {e}")
                    # Revert state on rotation failure
                    self._current_image_data = old_image_data
                    self._last_local_path = old_local_path
                    self.session.set_extraction_session(old_session_id)
                    self._set_backend_session_id(old_backend_session_id)
                    
                    # Re-enable rotation buttons
                    self.rotate_cw_btn.setEnabled(True)
                    self.rotate_ccw_btn.setEnabled(True)
                    self.status_bar.showMessage("Rotation failed", 3000)
                    self._rotation_backup = {
                        'old_image_data': old_image_data,
                        'old_local_path': old_local_path,
                        'old_session_id': old_session_id,
                        'old_backend_session_id': old_backend_session_id,
                    }
            except Exception as e:
                # Revert state on rotation/save failure
                self._current_image_data = old_image_data
                self._last_local_path = old_local_path
                self.session.set_extraction_session(old_session_id)
                self._set_backend_session_id(old_backend_session_id)
                LOG.warning("Rotation failed, reverted to previous state: %s", e)
                self._handle_backend_exception(e, context="Rotate failed")
                self.status_bar.showMessage("Rotate failed - state reverted", 3000)
                self._rotation_backup = {
                    'old_image_data': old_image_data,
                    'old_local_path': old_local_path,
                    'old_session_id': old_session_id,
                    'old_backend_session_id': old_backend_session_id,
                }
                self._update_view_actions_enabled()
            return

        # Preview/result pane — view-only rotation
        view = self._get_active_view()
        if view:
            view.rotate_view(degrees)
            self.status_bar.showMessage(f"Rotated view {degrees}°", 2000)

    def _on_rotate_upload_finished(self, tmp_path: str, payload) -> None:
        """Handle completion of async rotation upload."""
        # Re-enable rotation buttons
        self.rotate_cw_btn.setEnabled(True)
        self.rotate_ccw_btn.setEnabled(True)

        try:
            session_id = payload.get("id") or ""
            if not session_id:
                raise RuntimeError("Upload succeeded but no session id returned")

            qimg = self._load_image_with_exif(tmp_path)
            if qimg.isNull():
                raise RuntimeError("Could not load rotated image into viewer")

            # Store current zoom state before rotation
            self._pre_rotation_zoom = self.src_view.get_zoom_percent() / 100.0
            self._pre_rotation_transform = self.src_view.transform()

            # Update rotation angle tracking
            if hasattr(self, '_pending_rotation_degrees'):
                self._current_rotation_angle = (self._current_rotation_angle + self._pending_rotation_degrees) % 360
                self._last_rotation_degrees = self._pending_rotation_degrees  # Store for feedback
                self._pending_rotation_degrees = 0  # Reset after use

            self.src_view.set_image(qimg)

            # Restore zoom state after rotation instead of auto-fitting
            # This preserves user's zoom level and viewport position
            QTimer.singleShot(50, lambda: self._restore_view_state_after_rotation())

            # Re-apply modern styling after rotation to maintain design consistency
            QTimer.singleShot(75, lambda: self._update_pane_borders())

            self.session.set_extraction_session(session_id)
            if hasattr(self, "session_id_label"):
                self.session_id_label.setText(f"Session: {session_id[:8]}...")
                self.session_id_label.setToolTip(f"Full session ID: {session_id}")
            self._sync_backend_session(tmp_path)

            # Reset previous outputs and CLEAR SELECTION (coordinates no longer valid)
            self._last_result_png = None
            self.preview_view.clear_image()
            self.res_view.scene().clear()
            self._current_crop_preview_pixmap = None
            # Keep stack visible with empty overlays
            self._set_preview_panel_visible(True)
            self.preview_label.setVisible(True)
            self.result_label.setVisible(True)
            self.preview_view.setVisible(False)
            self.res_view.setVisible(False)
            self.preview_empty.setVisible(True)
            self.result_empty.setVisible(True)
            self.src_view.clear_selection()
            self.sel_info.setText("Selection: –")
            self._update_action_states()
            self._update_view_actions_enabled()
            self.status_bar.showMessage("Rotated source and re-uploaded - make a new selection", 3000)
            if sys.platform == "darwin":
                cast(QWidget, self).setWindowFilePath(self._last_local_path or "")

            # Clear backup state on success
            if hasattr(self, '_rotation_backup'):
                delattr(self, '_rotation_backup')
        except Exception as e:
            # Revert to backup state on upload failure
            if hasattr(self, '_rotation_backup'):
                backup = self._rotation_backup
                self._current_image_data = backup['old_image_data']
                self._last_local_path = backup['old_local_path']
                self.session.set_extraction_session(backup['old_session_id'])
                self._set_backend_session_id(backup.get('old_backend_session_id'))
                delattr(self, '_rotation_backup')
                LOG.warning("Rotation upload failed, reverted to previous state: %s", e)
            if hasattr(self, "backend_status_label"):
                self.backend_status_label.setText("Local service: Offline")
                self.backend_status_label.setStyleSheet("color: #cc0000; padding: 2px 8px;")
            self._handle_backend_exception(e, context="Rotate failed")
            self.status_bar.showMessage("Rotate failed - state reverted", 3000)
            self._update_view_actions_enabled()

    def _on_rotate_upload_error(self, tmp_path: str, error) -> None:
        """Handle error in async rotation upload."""
        # Re-enable rotation buttons
        self.rotate_cw_btn.setEnabled(True)
        self.rotate_ccw_btn.setEnabled(True)

        # Revert to backup state on upload failure
        if hasattr(self, '_rotation_backup'):
            backup = self._rotation_backup
            self._current_image_data = backup['old_image_data']
            self._last_local_path = backup['old_local_path']
            self.session.set_extraction_session(backup['old_session_id'])
            self._set_backend_session_id(backup.get('old_backend_session_id'))
            delattr(self, '_rotation_backup')
            LOG.warning("Rotation upload failed, reverted to previous state: %s", error)
        if hasattr(self, "backend_status_label"):
            self.backend_status_label.setText("Local service: Offline")
            self.backend_status_label.setStyleSheet("color: #cc0000; padding: 2px 8px;")
        self._handle_backend_exception(error, context="Rotate failed")
        self.status_bar.showMessage("Rotate failed - state reverted", 3000)
        self._update_view_actions_enabled()

    def _update_color_ui(self):
        # Update color label text and swatch background
        hexc = self._color_hex
        self.color_label.setText(f"Color: {hexc}")
        # Choose text color based on luminance for readability
        try:
            r = int(hexc[1:3], 16); g = int(hexc[3:5], 16); b = int(hexc[5:7], 16)
            lum = 0.299*r + 0.587*g + 0.114*b
            text_color = '#000000' if lum > 186 else '#ffffff'
        except Exception:
            text_color = '#000000'
        self.color_label.setStyleSheet(f"background-color: {hexc}; color: {text_color}; border: 1px solid #ccc; padding: 4px 8px; border-radius: 8px;")

    def _remember_color(self, color: str, suppress_preview: bool = False) -> None:
        qcolor = QColor(color)
        if not qcolor.isValid():
            return
        normalized = qcolor.name().upper()
        if normalized in self._color_history:
            self._color_history.remove(normalized)
        self._color_history.insert(0, normalized)
        self._color_history = self._color_history[:3]
        self._refresh_color_history()

    def _refresh_color_history(self) -> None:
        _clear_layout(self.color_history_layout)
        if not self._color_history:
            return
        for color in self._color_history:
            btn = self._make_color_button(color)
            btn.setToolTip(f"Recent: {color}")
            btn.clicked.connect(partial(self._apply_color_from_button, color))
            self.color_history_layout.addWidget(btn)

    def _populate_color_presets(self) -> None:
        _clear_layout(self.color_presets_layout)
        for color in self._color_presets:
            btn = self._make_color_button(color)
            btn.setToolTip(f"Preset: {color}")
            btn.clicked.connect(partial(self._apply_color_from_button, color))
            self.color_presets_layout.addWidget(btn)

    def _apply_color_from_button(self, color: str) -> None:
        qcolor = QColor(color)
        if not qcolor.isValid():
            return
        normalized = qcolor.name()
        if normalized != self._color_hex:
            self._color_hex = normalized
            self._update_color_ui()
        self._remember_color(normalized, suppress_preview=True)
        self._last_result_png = None
        self.res_view.clear_image()
        self._update_action_states(preview_ready=False)
        self.schedule_preview()

    def _make_section_label(self, text: str, color_hex: Optional[str], *, top_margin: int = 12) -> QLabel:
        label = QLabel(text.upper())
        label.setProperty("class", "heading")
        margin = max(top_margin, 0)
        if color_hex is None:
            # Use bright white for maximum contrast
            color_hex = "#FFFFFF"
        label.setStyleSheet(
            "font-size: 10px; font-weight: 700; letter-spacing: 1.2px;"
            f"margin-top: {margin}px; margin-bottom: 4px; color: {color_hex};"
        )
        return label

    def _make_secondary_label(self, text: str, color_hex: Optional[str]) -> QLabel:
        label = QLabel(text)
        label.setProperty("class", "subheading")
        if color_hex is None:
            # Use bright white for readability instead of calculated dim color
            color_hex = "#FFFFFF"
        label.setStyleSheet(
            "font-size: 11px; font-weight: 500; letter-spacing: 0.3px;"
            f"color: {color_hex};"
        )
        return label

    def _make_color_button(self, color: str) -> QToolButton:
        btn = QToolButton(cast(QWidget, self))
        btn.setAutoRaise(True)
        btn.setFixedSize(22, 22)
        btn.setStyleSheet(
            "QToolButton {"
            f"background-color: {color};"
            "border: 1px solid rgba(0,0,0,64);"
            "border-radius: 8px;"
            "}"
            "QToolButton:hover {"
            "border-color: rgba(0,0,0,115);"
            "}"
        )
        return btn

    # -------- License/Evaluation helpers --------
    def _update_action_states(self, preview_ready: bool = False):
        """Enable or disable actions based on whether a processed preview exists."""
        has_preview = bool(preview_ready or self._last_result_png)
        from desktop_app.license import is_export_allowed
        export_allowed = bool(is_export_allowed())
        self.export_btn.setEnabled(has_preview and export_allowed)
        self.export_json_btn.setEnabled(True)  # Allow exporting metadata even without preview
        self.save_to_library_btn.setEnabled(has_preview and export_allowed)
        if hasattr(self, 'save_to_vault_btn'):
            self.save_to_vault_btn.setEnabled(has_preview)
        self.copy_btn.setEnabled(has_preview and export_allowed)
        if hasattr(self, 'sign_pdf_btn'):
            self.sign_pdf_btn.setEnabled(has_preview)
        self._update_export_tooltips()  # Update tooltips based on license status
        if hasattr(self, "_update_trial_notice"):
            self._update_trial_notice(export_allowed=export_allowed)
        self._update_view_actions_enabled()
        self._adjust_pane_layout()  # Dynamically adjust layout based on content
        if hasattr(self, "_refresh_toolbar_action_states"):
            self._refresh_toolbar_action_states()
    
    def _update_export_tooltips(self):
        """Update export-related tooltips based on license status."""
        from desktop_app.license import is_export_allowed
        
        if is_export_allowed():
            # Licensed - show normal tooltips
            self.export_btn.setToolTip("Export with advanced options (background, trim, format) - Ctrl/Cmd E")
            self.copy_btn.setToolTip("Copy result to clipboard (preserves transparency) - Ctrl/Cmd C")
            self.save_to_library_btn.setToolTip("Quick save as PNG to local library")
        else:
            # Trial mode - indicate license required
            self.export_btn.setToolTip("Export with advanced options - Requires License")
            self.copy_btn.setToolTip("Copy result to clipboard - Requires License")
            self.save_to_library_btn.setToolTip("Save to library - Requires License")

    def _require_export_gate(self, action_label: str) -> bool:
        """Return True if the current session is allowed to perform premium export actions."""
        from desktop_app.license import check_and_enforce_export_license
        if check_and_enforce_export_license(self):
            return True
        self.status_bar.showMessage(f"Evaluation mode — {action_label} is locked", 2500)
        return False

    def _adjust_pane_layout(self):
        """Intelligently resize panes: minimize source, maximize result when extraction active.

        Note: This method is disabled to allow users to manually resize panes.
        The automatic resizing was interfering with user control.
        """
        # DISABLED: Automatic layout adjustment was preventing manual resizing
        # Original behavior kept panes changing size automatically which was confusing
        # Users should have full control over pane sizes
        pass

    def _update_pane_labels_with_zoom(self):
        """Update pane labels to show current zoom percentage."""
        if self.src_view.has_image():
            zoom = self.src_view.get_zoom_percent()
            self.source_label.setText(f"Source {zoom:.0f}%")
        else:
            self.source_label.setText("Source")

        if self.preview_view.has_image():
            zoom = self.preview_view.get_zoom_percent()
            self.preview_label.setText(f"Crop preview {zoom:.0f}%")
        else:
            self.preview_label.setText("Crop preview")

        if self.res_view.has_image():
            zoom = self.res_view.get_zoom_percent()
            self.result_label.setText(f"Result {zoom:.0f}%")
        else:
            self.result_label.setText("Result")

    def _update_view_actions_enabled(self):
        """Enable/disable zoom and rotate buttons based on active pane and content."""
        has_source = self.src_view.has_image()
        has_preview = self.preview_view.has_image()
        has_result = self.res_view.has_image()

        active_has_image = {
            "source": has_source,
            "preview": has_preview,
            "result": has_result,
        }.get(self._active_pane, False)

        for btn in (self.zoom_in_btn, self.zoom_out_btn, self.fit_btn, self.reset_view_btn):
            btn.setEnabled(active_has_image)
        self.zoom_combo.setEnabled(active_has_image)

        rotate_enabled = False
        if self._active_pane == "source":
            rotate_enabled = self._current_image_data is not None
        elif self._active_pane == "preview":
            rotate_enabled = has_preview
        elif self._active_pane == "result":
            rotate_enabled = has_result

        self.rotate_cw_btn.setEnabled(rotate_enabled)
        self.rotate_ccw_btn.setEnabled(rotate_enabled)
        has_any = has_source or has_preview or has_result or bool(self.session.session_id)
        self.clean_session_btn.setEnabled(has_any)

    def on_copy(self):
        if not self._require_export_gate("Copy to clipboard"):
            return
        if not self._last_result_png:
            return
        try:
            img = QImage.fromData(self._last_result_png, "PNG")
            if img.isNull():
                raise RuntimeError("Could not decode result image for clipboard")

            # Ensure proper alpha handling across platforms
            # Convert to ARGB32_Premultiplied to avoid dim colors on Windows
            if img.hasAlphaChannel():
                img = img.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)

            QApplication.clipboard().setPixmap(QPixmap.fromImage(img))
            self.status_bar.showMessage("Copied to clipboard", 2000)
        except Exception as e:
            QMessageBox.critical(cast(QWidget, self), "Copy Failed", str(e))

    def on_enter_license(self):
        dlg = LicenseDialog(self)
        if dlg.exec():
            self._licensed = is_licensed()
            self.status_bar.showMessage("Thanks! License saved.", 3000)
            # Refresh entitlement-driven UI states after license changes
            self._update_action_states(preview_ready=bool(self._last_result_png))

    def on_buy_license(self):
        from desktop_app.config import get_purchase_url, get_pricing_plan

        default_plan = self._resolve_purchase_plan_id(get_pricing_plan("starter").plan_id)
        QDesktopServices.openUrl(QUrl(get_purchase_url(default_plan)))

    def _resolve_purchase_plan_id(self, fallback: str) -> str:
        """Resolve plan id from main window override or safe fallback."""
        from desktop_app.config import get_pricing_plan as resolve_plan

        if hasattr(self, "get_default_purchase_plan_id"):
            get_plan = getattr(self, "get_default_purchase_plan_id")
            if callable(get_plan):
                try:
                    return resolve_plan(get_plan()).plan_id
                except Exception:
                    return resolve_plan(fallback).plan_id

        return resolve_plan(fallback).plan_id

    # No activation prompt; purchase is optional and handled via menu link.

    def _open_document(self, relative_path: str) -> None:
        """Open a markdown document in a nice dialog with rendered HTML."""
        try:
            dialog = HelpDialog(relative_path, self)
            dialog.exec()
        except Exception as exc:
            QMessageBox.warning(cast(QWidget, self), "Unable to open document", str(exc))

    def _open_url(self, url: str) -> None:
        try:
            QDesktopServices.openUrl(QUrl(url))
        except Exception as exc:
            QMessageBox.warning(cast(QWidget, self), "Unable to open URL", str(exc))

    def _on_zoom_in(self):
        """Zoom in on active pane."""
        active_view = self._get_active_view()
        if active_view and active_view.has_image():
            active_view.zoom_in()
            # Sync zoom combo to reflect new zoom level
            zoom_percent = active_view.get_zoom_percent()
            zoom_text = f"{zoom_percent:.0f}%"
            self._updating_zoom_combo = True
            self.zoom_combo.setCurrentText(zoom_text)
            self._last_valid_zoom_text = zoom_text
            self._updating_zoom_combo = False
        self._update_coordinate_display()
    
    def _on_zoom_out(self):
        """Zoom out on active pane."""
        active_view = self._get_active_view()
        if active_view and active_view.has_image():
            active_view.zoom_out()
            # Sync zoom combo to reflect new zoom level
            zoom_percent = active_view.get_zoom_percent()
            zoom_text = f"{zoom_percent:.0f}%"
            self._updating_zoom_combo = True
            self.zoom_combo.setCurrentText(zoom_text)
            self._last_valid_zoom_text = zoom_text
            self._updating_zoom_combo = False
        self._update_coordinate_display()
    
    def _on_reset_zoom(self):
        """Reset zoom to 100% on active pane."""
        active_view = self._get_active_view()
        if active_view and active_view.has_image():
            active_view.reset_zoom()
            active_view.centerOn(active_view.sceneRect().center())
            # Sync zoom combo to show 100%
            self._updating_zoom_combo = True
            self.zoom_combo.setCurrentText("100%")
            self._last_valid_zoom_text = "100%"
            self._updating_zoom_combo = False
        self._update_coordinate_display()

    def _on_fit(self):
        """Fit to window on active pane."""
        active_view = self._get_active_view()
        if active_view and active_view.has_image():
            active_view.fit()
            # Sync zoom combo to show "Fit"
            self._updating_zoom_combo = True
            self.zoom_combo.setCurrentText("Fit")
            self._last_valid_zoom_text = "Fit"
            self._updating_zoom_combo = False
        self._update_coordinate_display()

    def _on_zoom_combo_activated(self, index: int):
        if self._updating_zoom_combo:
            return
        text = self.zoom_combo.itemText(index)
        self._apply_zoom_text(text)

    def _on_zoom_combo_edit_finished(self):
        if self._updating_zoom_combo:
            return
        text = self.zoom_combo.currentText()
        self._apply_zoom_text(text)

    def _apply_zoom_text(self, text: str):
        text = (text or "").strip()
        if not text:
            return
        if text.lower() == "fit":
            self._on_fit()
            # Update combo to show "Fit" and cache it
            self._updating_zoom_combo = True
            self.zoom_combo.setCurrentText("Fit")
            self._last_valid_zoom_text = "Fit"
            self._updating_zoom_combo = False
            return

        # Get current valid zoom before attempting change
        active_view = self._get_active_view()
        if not active_view or not active_view.has_image():
            self._update_coordinate_display()
            return
        current_zoom = active_view.get_zoom_percent()

        if text.endswith("%"):
            text = text[:-1]
        try:
            value = float(text)
        except ValueError:
            self.status_bar.showMessage("Invalid zoom value - enter a number like 150 or 'Fit'", 3000)
            # Restore last valid value from cache
            fallback = getattr(self, "_last_valid_zoom_text", f"{current_zoom:.0f}%")
            self._updating_zoom_combo = True
            self.zoom_combo.setCurrentText(fallback)
            self._updating_zoom_combo = False
            self._update_coordinate_display()
            return
        if value <= 0:
            self.status_bar.showMessage("Zoom value must be greater than 0", 3000)
            # Restore last valid value from cache
            fallback = getattr(self, "_last_valid_zoom_text", f"{current_zoom:.0f}%")
            self._updating_zoom_combo = True
            self.zoom_combo.setCurrentText(fallback)
            self._updating_zoom_combo = False
            self._update_coordinate_display()
            return

        active_view.set_zoom_percent(value)
        # Normalize combo text to show actual applied zoom (may differ slightly due to rounding)
        actual_zoom = active_view.get_zoom_percent()
        display_text = f"{actual_zoom:.0f}%"
        self._updating_zoom_combo = True
        self.zoom_combo.setCurrentText(display_text)
        self._last_valid_zoom_text = display_text
        self._updating_zoom_combo = False
        self._update_coordinate_display()

    def _apply_left_panel_breakpoint(self):
        """Apply responsive breakpoints based on available width."""
        if not hasattr(self, '_left_panel'):
            return

        # Get available width for responsive behavior
        available_width = self._left_panel.width()
        is_narrow = available_width < 280  # Breakpoint for narrow layouts

        if is_narrow:
            # Shorten button texts for narrow layouts
            self.open_btn.setText("Open")
            self.toggle_mode_btn.setText("Mode")
            self.clear_sel_btn.setText("Clear")
            self.clean_session_btn.setText("Clean")
            self.export_btn.setText("Export")
            self.save_to_library_btn.setText("Save")
            self.export_json_btn.setText("JSON")
            self.delete_from_library_btn.setText("Delete")

            # Hide non-essential sections in narrow mode
            if hasattr(self, '_welcome_label'):
                self._welcome_label.hide()
            if hasattr(self, '_library_section_label'):
                self._library_section_label.hide()
            if hasattr(self, 'library_list'):
                self.library_list.hide()
            if hasattr(self, 'delete_from_library_btn'):
                self.delete_from_library_btn.hide()
        else:
            # Restore full button texts
            self.open_btn.setText("Choose Image")
            # Update toggle mode text based on current state
            if self.toggle_mode_btn.isChecked():
                self.toggle_mode_btn.setText("Selection Mode: Select")
            else:
                self.toggle_mode_btn.setText("Pan Mode")
            self.clear_sel_btn.setText("Clear Selection")
            self.clean_session_btn.setText("Clean Viewport")
            self.export_btn.setText("Export Signature")
            self.save_to_library_btn.setText("Save to Library")
            self.export_json_btn.setText("Export JSON")
            self.delete_from_library_btn.setText("Delete Selected")

            # Show all sections when not narrow
            if hasattr(self, '_welcome_label'):
                self._welcome_label.show()
            if hasattr(self, '_library_section_label'):
                self._library_section_label.show()
            if hasattr(self, 'library_list'):
                self.library_list.show()
            if hasattr(self, 'delete_from_library_btn'):
                self.delete_from_library_btn.show()

    def eventFilter(self, obj, event):
        """Handle events for responsive behavior."""
        if obj == self._left_panel and event.type() == QEvent.Type.Resize:
            # Apply breakpoint when panel resizes
            QTimer.singleShot(0, self._apply_left_panel_breakpoint)

        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Defer update to ensure layouts settle before querying viewport sizes
        QTimer.singleShot(0, self._update_coordinate_display)
        QTimer.singleShot(0, self._apply_left_panel_breakpoint)

    # Enhanced Visual Feedback System

    def _show_feedback(self, message: str, feedback_type: str = "info", duration: int = 3000) -> None:
        """Show enhanced visual feedback with color coding and animations."""
        if not hasattr(self, 'statusBar'):
            return

        # Color coding for different feedback types
        colors = {
            "success": "#28a745",    # Green
            "error": "#dc3545",      # Red
            "warning": "#ffc107",    # Yellow
            "info": "#17a2b8",       # Blue
            "processing": "#6f42c1"  # Purple
        }

        # Create styled message with color
        color = colors.get(feedback_type, colors["info"])
        styled_message = f'<span style="color: {color}; font-weight: bold;">{message}</span>'

        # Show in status bar
        self.statusBar().showMessage(styled_message, duration)

        # Add temporary highlight effect to active pane
        if feedback_type in ["success", "error", "warning"]:
            self._flash_active_pane(feedback_type)

    def _flash_active_pane(self, feedback_type: str) -> None:
        """Add a brief flash effect to the active pane for visual emphasis."""
        if not hasattr(self, '_active_pane'):
            return

        # Flash colors for different feedback types
        flash_colors = {
            "success": QColor(40, 167, 69, 60),     # Green with transparency
            "error": QColor(220, 53, 69, 60),       # Red with transparency
            "warning": QColor(255, 193, 7, 60),     # Yellow with transparency
        }

        flash_color = flash_colors.get(feedback_type)
        if not flash_color:
            return

        # Apply flash effect
        active_view = self._get_active_view()
        if active_view:
            original_style = active_view.styleSheet()
            flash_style = f"ImageView {{ border: 3px solid {flash_color.name()}; border-radius: 6px; }}"

            active_view.setStyleSheet(flash_style)

            # Remove flash after brief delay
            if "pane_flash" not in self._feedback_timers:
                self._feedback_timers["pane_flash"] = QTimer(cast(QWidget, self))
                self._feedback_timers["pane_flash"].setSingleShot(True)

            self._feedback_timers["pane_flash"].timeout.connect(
                lambda: self._restore_pane_style(active_view, original_style)
            )
            self._feedback_timers["pane_flash"].start(300)  # 300ms flash

    def _restore_pane_style(self, view: 'ImageView', original_style: str) -> None:
        """Restore original pane style after flash effect."""
        view.setStyleSheet(original_style)
        # Ensure active pane styling is reapplied
        self._update_pane_borders()

    def _show_progress(self, operation: str, title: str = "Processing") -> str:
        """Show progress dialog for long-running operations."""
        from PySide6.QtWidgets import QProgressDialog

        # Create unique progress ID
        progress_id = f"{operation}_{id(self)}"

        # Create progress dialog
        progress = QProgressDialog(title, "Cancel", 0, 100, cast(QWidget, self))
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setAutoClose(False)
        progress.setMinimumDuration(1000)  # Show after 1 second

        # Add custom styling
        progress.setStyleSheet("""
            QProgressDialog {
                background-color: palette(window);
                border: 1px solid palette(mid);
                border-radius: 6px;
            }
            QProgressBar {
                border: 1px solid palette(mid);
                border-radius: 3px;
                text-align: center;
                background-color: palette(base);
            }
            QProgressBar::chunk {
                background-color: #007AFF;
                border-radius: 2px;
            }
        """)

        # Store reference
        self._progress_dialogs[progress_id] = progress

        return progress_id

    def _update_progress(self, progress_id: str, value: int, message: str = "") -> None:
        """Update progress dialog value and message."""
        if progress_id in self._progress_dialogs:
            progress = self._progress_dialogs[progress_id]
            progress.setValue(value)
            if message:
                progress.setLabelText(message)

    def _hide_progress(self, progress_id: str) -> None:
        """Hide and cleanup progress dialog."""
        if progress_id in self._progress_dialogs:
            progress = self._progress_dialogs[progress_id]
            progress.close()
            del self._progress_dialogs[progress_id]

    # Accessibility Improvements

    def _setup_accessibility(self) -> None:
        """Configure comprehensive accessibility features."""
        # Enable high contrast mode if system is configured for it
        if self._is_high_contrast_enabled():
            self._enable_high_contrast_mode()

        # Set up keyboard navigation
        self._setup_keyboard_navigation()

        # Configure screen reader announcements
        self._setup_screen_reader_announcements()

        # Add focus indicators to key widgets
        self._enhance_focus_indicators()

    def _is_high_contrast_enabled(self) -> bool:
        """Check if system has high contrast mode enabled."""
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            palette = app.palette()
            # Check if high contrast by examining color differences
            window_color = palette.color(QPalette.ColorRole.Window)
            window_text_color = palette.color(QPalette.ColorRole.WindowText)

            # Calculate contrast ratio (simplified)
            contrast = abs(window_color.lightness() - window_text_color.lightness())
            return contrast > 200  # High contrast threshold
        return False

    def _enable_high_contrast_mode(self) -> None:
        """Enable high contrast styling for better visibility."""
        high_contrast_style = """
            ImageView {
                border: 3px solid palette(text);
                border-radius: 4px;
                background-color: palette(base);
            }
            QPushButton {
                border: 2px solid palette(text);
                border-radius: 4px;
                padding: 6px;
                background-color: palette(button);
                color: palette(button-text);
            }
            QPushButton:focus {
                border: 3px solid palette(highlight);
                outline: 2px solid palette(highlight);
            }
            QLabel {
                color: palette(text);
                font-weight: bold;
            }
        """

        # Apply high contrast styles to all image views
        for view_name in ['src_view', 'preview_view', 'res_view']:
            if hasattr(self, view_name):
                view = getattr(self, view_name)
                view.setStyleSheet(high_contrast_style)

    def _setup_keyboard_navigation(self) -> None:
        """Set up comprehensive keyboard shortcuts and navigation."""
        def _shortcut(mac: str, other: str) -> str:
            return mac if sys.platform == "darwin" else other

        # Pane switching shortcuts
        shortcut_source = QShortcut(QKeySequence(_shortcut("Meta+1", "Ctrl+1")), cast(QWidget, self))
        shortcut_source.activated.connect(lambda: self._on_pane_clicked("source"))

        shortcut_preview = QShortcut(QKeySequence(_shortcut("Meta+2", "Ctrl+2")), cast(QWidget, self))
        shortcut_preview.activated.connect(lambda: self._on_pane_clicked("preview"))

        shortcut_result = QShortcut(QKeySequence(_shortcut("Meta+3", "Ctrl+3")), cast(QWidget, self))
        shortcut_result.activated.connect(lambda: self._on_pane_clicked("result"))

        # Action shortcuts
        shortcut_escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), cast(QWidget, self))
        shortcut_escape.activated.connect(self._handle_escape_cancel)
        self._shortcuts.append(shortcut_escape)

        shortcut_clear = QShortcut(QKeySequence("Delete"), cast(QWidget, self))
        shortcut_clear.activated.connect(self.on_clear_selection)

        shortcut_export = QShortcut(QKeySequence(_shortcut("Meta+E", "Ctrl+E")), cast(QWidget, self))
        shortcut_export.activated.connect(self.on_export)

        shortcut_open = QShortcut(QKeySequence(_shortcut("Meta+O", "Ctrl+O")), cast(QWidget, self))
        shortcut_open.activated.connect(self.on_open)

        shortcut_save = QShortcut(QKeySequence.StandardKey.Save, cast(QWidget, self))
        shortcut_save.activated.connect(self.on_save_to_library)

        # Accessibility help shortcut
        shortcut_help = QShortcut(QKeySequence("F1"), cast(QWidget, self))
        shortcut_help.activated.connect(self._show_accessibility_help)

    def _setup_screen_reader_announcements(self) -> None:
        """Configure announcements for screen readers."""
        def _shortcut(mac: str, other: str) -> str:
            return mac if sys.platform == "darwin" else other

        # Update pane descriptions to be more descriptive
        if hasattr(self, 'src_view'):
            self.src_view.setAccessibleDescription(
                "Source image pane. Contains the original document image. "
                "Press Tab to focus, then use arrow keys to navigate, "
                "press and hold Enter to start selection mode, use arrow keys to adjust selection."
            )

        if hasattr(self, 'preview_view'):
            self.preview_view.setAccessibleDescription(
                "Preview pane. Shows the selected signature area with current processing settings. "
                "Use Tab to access processing controls."
            )

        if hasattr(self, 'res_view'):
            self.res_view.setAccessibleDescription(
                "Result pane. Displays the final processed signature ready for export. "
                f"Press {_shortcut('⌘E', 'Ctrl+E')} to export or "
                f"{_shortcut('⌘C', 'Ctrl+C')} to copy to clipboard."
            )

    def _enhance_focus_indicators(self) -> None:
        """Add clear focus indicators to all interactive elements."""
        focus_style = """
           :focus {
                border: 2px solid #007AFF;
                outline: 2px solid #007AFF;
                outline-offset: 2px;
            }
        """

        # Apply focus styles to all image views
        for view_name in ['src_view', 'preview_view', 'res_view']:
            if hasattr(self, view_name):
                view = getattr(self, view_name)
                current_style = view.styleSheet() or ""
                view.setStyleSheet(current_style + focus_style)

        # Enhance button focus indicators
        if hasattr(self, 'zoom_in_btn'):
            self.zoom_in_btn.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            self.zoom_in_btn.setAccessibleName("Zoom In button")

        if hasattr(self, 'zoom_out_btn'):
            self.zoom_out_btn.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            self.zoom_out_btn.setAccessibleName("Zoom Out button")

        if hasattr(self, 'clear_sel_btn'):
            self.clear_sel_btn.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            self.clear_sel_btn.setAccessibleName("Clear Selection button")

    def _show_accessibility_help(self) -> None:
        """Show accessibility help dialog."""
        from PySide6.QtWidgets import QMessageBox

        def _shortcut(mac: str, other: str) -> str:
            return mac if sys.platform == "darwin" else other

        help_text = """
        <h3>Accessibility Help</h3>

        <h4>Keyboard Navigation</h4>
        <ul>
        <li><b>{pane_shortcut}</b> - Switch between Source/Preview/Result panes</li>
        <li><b>Tab</b> - Navigate between controls</li>
        <li><b>Arrow Keys</b> - Navigate within images (when focused)</li>
        <li><b>Enter</b> - Activate buttons or start selection mode</li>
        <li><b>Delete</b> - Clear current selection</li>
        <li><b>{open_shortcut}</b> - Open new image</li>
        <li><b>{export_shortcut}</b> - Export result</li>
        <li><b>{copy_shortcut}</b> - Copy result to clipboard</li>
        </ul>

        <h4>Screen Reader Support</h4>
        <p>All panes and controls have descriptive labels and descriptions.
        Status messages will be announced for important actions.</p>

        <h4>High Contrast Mode</h4>
        <p>The application automatically detects and enables high contrast styling
        when system high contrast mode is enabled.</p>

        <h4>Getting Started</h4>
        <ol>
        <li>Press {open_shortcut} to open an image</li>
        <li>Press {source_shortcut} to focus the Source pane</li>
        <li>Press Enter, then use arrow keys to select signature area</li>
        <li>Press {export_shortcut} to export the result</li>
        </ol>
        """
        help_text = help_text.format(
            pane_shortcut=_shortcut("⌘+1/2/3", "Ctrl+1/2/3"),
            open_shortcut=_shortcut("⌘O", "Ctrl+O"),
            export_shortcut=_shortcut("⌘E", "Ctrl+E"),
            copy_shortcut=_shortcut("⌘C", "Ctrl+C"),
            source_shortcut=_shortcut("⌘1", "Ctrl+1"),
        )

        msg = QMessageBox(cast(QWidget, self))
        msg.setWindowTitle("Accessibility Help")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    def _announce_to_screen_reader(self, message: str) -> None:
        """Announce message to screen readers."""
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage(message, 2000)

    # Context Menu Helper Methods

    def _show_image_properties(self) -> None:
        """Show image properties dialog for the current source image."""
        if not hasattr(self, '_current_image_data') or not self._current_image_data:
            return

        # Create a simple info dialog
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(cast(QWidget, self))
        msg.setWindowTitle("Image Properties")
        msg.setIcon(QMessageBox.Icon.Information)

        # Calculate image size
        if hasattr(self, 'src_view') and self.src_view.has_image():
            image = self.src_view.get_image()
            if image:
                width, height = image.width(), image.height()
                size_mb = len(self._current_image_data) / (1024 * 1024)

                info_text = f"""<b>Image Information</b><br><br>
                <b>Dimensions:</b> {width} × {height} pixels<br>
                <b>File Size:</b> {size_mb:.2f} MB<br>
                <b>Format:</b> PNG<br>
                <b>Color Depth:</b> {image.depth()} bits"""

                msg.setText(info_text)
                msg.exec()

    def _auto_adjust_threshold(self) -> None:
        """Automatically adjust threshold based on image content."""
        if self._apply_auto_threshold():
            self.schedule_preview()

    def _invert_colors(self) -> None:
        """Invert the current color selection."""
        # Simple color inversion - could be enhanced
        if hasattr(self, '_color_hex'):
            # Convert hex to RGB, invert, convert back
            hex_color = self._color_hex.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r, g, b = 255 - r, 255 - g, 255 - b
            inverted_hex = f"#{r:02x}{g:02x}{b:02x}"

            # Apply inverted color
            if hasattr(self, '_apply_color'):
                self._apply_color(inverted_hex)

    def _auto_detect_current_region(self) -> None:
        """Auto-detect the signature region and apply it to the source selection."""
        if not self.session.session_id:
            QMessageBox.information(cast(QWidget, self), "No image uploaded", "Open an image first.")
            return

        try:
            candidates = self.local_extractor.auto_detect_signatures(
                self.session.session_id,
                max_candidates=5,
                min_confidence=0.75,
            )
            if not candidates:
                self.status_bar.showMessage("No signature region detected", 3000)
                return

            source_image = self.src_view.get_image()
            dialog = SignatureCandidateDialog(candidates, source_image, cast(QWidget, self))
            if dialog.exec() != QDialog.DialogCode.Accepted:
                self.status_bar.showMessage("Auto-detect canceled; manual selection unchanged", 3000)
                return
            selected = dialog.selected_candidate()
            if selected is None:
                self.status_bar.showMessage("No candidate selected; manual selection unchanged", 3000)
                return

            x1, y1, x2, y2 = selected.bbox
            self.src_view.set_selection_from_coords(x1, y1, x2, y2)
            self.status_bar.showMessage(
                f"Candidate confirmed · {selected.source} · score {selected.confidence:.2f}",
                3000,
            )
            self.schedule_preview()
        except Exception as exc:
            LOG.warning("Auto-detect failed: %s", exc)
            self.status_bar.showMessage("Auto-detect failed - use manual selection", 3000)

    def _capture_crop_preview(self) -> None:
        """Cache the current crop preview for overlay rendering."""
        try:
            cropped = self.src_view.crop_selection()
            if cropped and not cropped.isNull():
                self._current_crop_preview_pixmap = QPixmap.fromImage(cropped)
            else:
                self._current_crop_preview_pixmap = None
        except Exception:
            self._current_crop_preview_pixmap = None

    def _build_overlay_preview_pixmap(self, base_pixmap: QPixmap, overlay_png: bytes) -> Optional[QPixmap]:
        """Composite the extracted signature over the crop preview."""
        if base_pixmap.isNull():
            return None

        overlay = QPixmap()
        if not overlay.loadFromData(overlay_png):
            return None

        result = QPixmap(base_pixmap)
        from PySide6.QtGui import QPainter

        painter = QPainter(result)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawPixmap(
            0,
            0,
            overlay.scaled(
                result.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ),
        )
        painter.end()
        return result

    def _copy_result_to_clipboard(self) -> None:
        """Copy the result image to clipboard."""
        self.on_copy()

    # Rotation Coordinate Mapping Helper Methods

    def _restore_view_state_after_rotation(self) -> None:
        """Restore zoom and viewport state after rotation to maintain user context."""
        if not hasattr(self, 'src_view') or not self.src_view.has_image():
            return

        # Restore zoom level with bounds checking
        try:
            # Calculate reasonable zoom bounds for the new image size
            image_size = self.src_view.get_image().size() if self.src_view.get_image() else None
            if image_size:
                max_zoom = min(5.0, 2000.0 / max(image_size.width(), image_size.height()))  # Cap at 5x or based on image size
                min_zoom = 0.1  # Minimum 10% zoom

                # Apply the stored zoom with bounds checking
                target_zoom = max(min_zoom, min(max_zoom, self._pre_rotation_zoom))

                # Restore zoom
                current_zoom = self.src_view.get_zoom_percent() / 100.0
                if abs(current_zoom - target_zoom) > 0.01:  # Only change if significant difference
                    self.src_view.set_zoom(target_zoom * 100.0)

                # Show feedback about rotation preservation
                rotation_degrees = getattr(self, '_last_rotation_degrees', 0)
                self._show_feedback(f"Rotated {rotation_degrees}° - zoom and viewport preserved", "success", 2000)

        except Exception as e:
            LOG.warning(f"Could not restore view state after rotation: {e}")
            # Fallback to fit if restore fails
            self.src_view.fit(margin_percent=5.0)

    def _transform_selection_coordinates(self, x1: int, y1: int, x2: int, y2: int,
                                         from_rotation: int, to_rotation: int,
                                         image_width: int, image_height: int) -> tuple[int, int, int, int]:
        """Transform selection coordinates from one rotation to another.

        Args:
            x1, y1, x2, y2: Original selection coordinates
            from_rotation: Source rotation angle in degrees
            to_rotation: Target rotation angle in degrees
            image_width: Image width in pixels
            image_height: Image height in pixels

        Returns:
            Transformed coordinates (x1, y1, x2, y2)
        """
        if from_rotation == to_rotation:
            return x1, y1, x2, y2

        # Calculate rotation difference
        rotation_diff = (to_rotation - from_rotation) % 360

        # Handle 90-degree rotations specifically (most common case)
        if rotation_diff == 90:
            # 90° clockwise rotation: (x, y) -> (y, width-x)
            return (
                y1,
                image_width - x2,
                y2,
                image_width - x1
            )
        elif rotation_diff == 180:
            # 180° rotation: (x, y) -> (width-x, height-y)
            return (
                image_width - x2,
                image_height - y2,
                image_width - x1,
                image_height - y1
            )
        elif rotation_diff == 270:
            # 270° clockwise rotation: (x, y) -> (height-y, x)
            return (
                image_height - y2,
                x1,
                image_height - y1,
                x2
            )
        elif rotation_diff == 0:
            # No rotation needed
            return x1, y1, x2, y2
        else:
            # For non-standard angles, use trigonometric transformation
            import math

            # Center of image
            cx, cy = image_width / 2.0, image_height / 2.0

            # Convert to radians
            angle_rad = math.radians(rotation_diff)
            cos_angle = math.cos(angle_rad)
            sin_angle = math.sin(angle_rad)

            # Transform each corner
            def transform_point(px, py):
                # Translate to origin
                px, py = px - cx, py - cy

                # Rotate
                new_px = px * cos_angle - py * sin_angle
                new_py = px * sin_angle + py * cos_angle

                # Translate back and round
                return int(round(new_px + cx)), int(round(new_py + cy))

            # Transform all four corners
            corners = [
                (x1, y1), (x1, y2), (x2, y1), (x2, y2)
            ]
            transformed_corners = [transform_point(px, py) for px, py in corners]

            # Get bounding box of transformed corners
            xs = [corner[0] for corner in transformed_corners]
            ys = [corner[1] for corner in transformed_corners]

            return (
                max(0, min(image_width, min(xs))),
                max(0, min(image_height, min(ys))),
                max(0, min(image_width, max(xs))),
                max(0, min(image_height, max(ys)))
            )
    
