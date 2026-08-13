from __future__ import annotations

import os
from datetime import datetime
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, cast

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QIcon, QKeySequence, QPalette, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QDoubleSpinBox,
    QSpinBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from desktop_app.resources.icons import get_icon, set_button_icon


def _rgba(color: QColor) -> str:
    """Return a Qt stylesheet-friendly RGBA string for the given QColor."""
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"


def _create_button(
    text: str = "",
    parent: QWidget = None,
    *,
    use_modern_mac: bool = False,  # Changed default to False for consistency
    primary: bool = False,
    color: str = 'blue',
    compact: bool = True  # Default to compact for sidebar buttons
) -> QPushButton:
    """Create a button, using ModernMacButton on macOS if available and requested.

    Args:
        text: Button text
        parent: Parent widget
        use_modern_mac: Force modern button (default: auto-detect macOS)
        primary: True for primary action buttons (colored)
        color: One of 'blue', 'purple', 'pink', 'red', 'orange', 'yellow', 'green', 'teal'
        compact: True for smaller buttons (sidebar/toolbar), False for larger (dialogs)
    """
    if use_modern_mac:
        try:
            from desktop_app.widgets.modern_mac_button import ModernMacButton
            btn = ModernMacButton(
                text, parent,
                primary=primary,
                color=color,
                glass=True,
                compact=compact
            )
            return btn
        except (NameError, TypeError):
            # Fallback if ModernMacButton not available or doesn't support compact
            pass

    # Default to standard QPushButton - let theme system handle styling
    return QPushButton(text, parent)


from desktop_app.library import storage as lib
from desktop_app.views.bulk_sign_dialog import BulkSignDialog
from desktop_app.pdf.stack_profile import stack_install_hint, signing_backend_report

try:
    from desktop_app.pdf.viewer import PDFViewer
    from desktop_app.pdf.signer import read_signature_manifest
    from desktop_app.pdf.form_fields import PdfFormFieldEditor
    from desktop_app.pdf.annotations import PdfAnnotationEditor
    from desktop_app.pdf.document_session_store import load_document_session, save_document_session
    from desktop_app.pdf.db_audit import DatabaseAuditLogger as AuditLogger, get_audit_logs_for_pdf
    from desktop_app.pdf.template_store import (
        SignaturePlacementTemplate,
        create_template,
        delete_template,
        list_templates,
        get_template,
        save_template,
    )

    PDF_AVAILABLE = True
except ImportError as exc:  # pragma: no cover - optional dependency
    PDF_AVAILABLE = False
    PDF_IMPORT_ERROR = exc
else:
    PDF_IMPORT_ERROR = None


class PdfTabMixin:
    """PDF signing tab, audit logging, and signature placement helpers."""

    def _make_section_label(self, text: str, color_hex: Optional[str], *, top_margin: int = 12) -> QLabel:
        label = QLabel(text.upper())
        margin = max(top_margin, 0)
        if color_hex is None:
            # Use bright white for maximum contrast
            color_hex = "#FFFFFF"
        label.setStyleSheet(
            "font-size: 10px; font-weight: 700; letter-spacing: 1.2px;"
            f"margin-top: {margin}px; margin-bottom: 4px; color: {color_hex};"
        )
        return label

    def _setup_pdf_ui(self) -> None:
        install_hint = stack_install_hint()
        if not PDF_AVAILABLE:
            self._pdf_placeholder_tab = QWidget()
            placeholder = self._pdf_placeholder_tab
            layout = QVBoxLayout(placeholder)
            layout.addStretch()

            # Title
            title = QLabel("📄 PDF Signing Unavailable")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("font-size: 18px; font-weight: 600; color: #999; margin-bottom: 16px;")
            layout.addWidget(title)

            # Description
            description = QLabel(
                "PDF signing features require additional dependencies.\n\n"
                "To enable PDF signing, install the required libraries:"
            )
            description.setAlignment(Qt.AlignmentFlag.AlignCenter)
            description.setStyleSheet("font-size: 13px; color: #888; margin-bottom: 12px;")
            description.setWordWrap(True)
            layout.addWidget(description)

            # Installation command
            install_cmd = QLabel(
                "<code style='background-color: rgba(100, 100, 100, 0.2); "
                "padding: 8px 16px; border-radius: 6px; font-family: monospace;'>"
                f"{install_hint}"
                "</code>"
            )
            install_cmd.setAlignment(Qt.AlignmentFlag.AlignCenter)
            install_cmd.setTextFormat(Qt.TextFormat.RichText)
            install_cmd.setStyleSheet("font-size: 12px; margin: 12px 0;")
            layout.addWidget(install_cmd)

            # Error details if available
            if PDF_IMPORT_ERROR:
                error_label = QLabel(f"<small>Import error: {str(PDF_IMPORT_ERROR)}</small>")
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_label.setStyleSheet("font-size: 11px; color: #666; margin-top: 16px;")
                error_label.setWordWrap(True)
                layout.addWidget(error_label)

            # Help button
            help_btn = _create_button("Installation Help", self)
            help_icon = get_icon("help")
            if not help_icon.isNull():
                help_btn.setIcon(help_icon)
            help_btn.clicked.connect(lambda: self._open_document("docs/PDF_SETUP.md"))
            help_btn.setStyleSheet(
                "QPushButton { padding: 8px 16px; font-size: 13px; margin-top: 16px; }"
            )
            help_layout = QHBoxLayout()
            help_layout.addStretch()
            help_layout.addWidget(help_btn)
            help_layout.addStretch()
            layout.addLayout(help_layout)

            layout.addStretch()
            self._pdf_tab_index = self.tab_widget.addTab(placeholder, "📄 PDF Signing")

            # Add tooltip to tab explaining why it's disabled
            self.tab_widget.setTabToolTip(
                self._pdf_tab_index,
                f"PDF signing backend status: {signing_backend_report()}"
            )
            return

        pdf_tab = QWidget()
        pdf_layout = QHBoxLayout(pdf_tab)

        # Keep the control surface wide enough for action labels and provide a
        # vertical overflow path. The old fixed 300 px panel clipped long
        # actions such as "Apply Signature to Multiple Pages..." on normal
        # laptop-sized windows.
        pdf_left_panel = QWidget()
        pdf_left_panel.setObjectName("pdfControlsPanel")
        pdf_left_panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        pdf_left_panel.setFixedWidth(360)

        pdf_panel_layout = QVBoxLayout(pdf_left_panel)
        pdf_panel_layout.setContentsMargins(0, 0, 0, 0)

        pdf_scroll = QScrollArea(pdf_left_panel)
        pdf_scroll.setObjectName("pdfControlsScroll")
        pdf_scroll.setWidgetResizable(True)
        pdf_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        pdf_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        pdf_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        pdf_controls_host = QWidget()
        pdf_controls_host.setObjectName("pdfControlsContent")
        pdf_controls = QVBoxLayout(pdf_controls_host)
        pdf_controls.setContentsMargins(16, 18, 16, 18)
        pdf_controls.setSpacing(10)
        pdf_scroll.setWidget(pdf_controls_host)
        pdf_panel_layout.addWidget(pdf_scroll)

        # >>> ADD: match Extraction tab panel styling on macOS for 1:1 visual parity
        if sys.platform == "darwin":
            from PySide6.QtGui import QPalette, QColor

            pdf_left_panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

            # Pull the same palette logic Extraction tab uses
            palette = self.palette()
            group = palette.currentColorGroup()
            text_color = palette.color(group, QPalette.ColorRole.WindowText)
            base_color = palette.color(group, QPalette.ColorRole.Window)
            is_dark_mode = base_color.lightness() < 120

            border_color = palette.color(group, QPalette.ColorRole.Mid)

            if is_dark_mode:
                panel_color = QColor(28, 28, 32, 248)
            else:
                panel_color = QColor(251, 251, 253, 250)

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

            disabled_text = QColor(text_color)
            disabled_text.setAlpha(120 if is_dark_mode else 180)
            disabled_text_str = _rgba(disabled_text)

            field_bg = QColor(panel_color)
            field_bg = field_bg.lighter(118)
            field_bg.setAlpha(185)
            field_bg_str = _rgba(field_bg)

            subtle_line = QColor(border_color)
            subtle_line.setAlpha(70)
            subtle_line_str = _rgba(subtle_line)

            pdf_left_panel.setStyleSheet(
                "QWidget#pdfControlsPanel {"
                f"  background-color: {_rgba(panel_color)};"
                f"  border-right: 1px solid {subtle_line_str};"
                f"  color: {text_color.name()};"
                "  font-size: 12px;"
                "}"
                "#pdfControlsPanel QLabel,"
                "#pdfControlsPanel QStatusBar,"
                "#pdfControlsPanel QToolButton {"
                "  background-color: transparent;"
                "  border: none;"
                f"  color: {text_color.name()};"
                "}"
                "#pdfControlsPanel QLineEdit,"
                "#pdfControlsPanel QSpinBox,"
                "#pdfControlsPanel QDoubleSpinBox,"
                "#pdfControlsPanel QTextEdit,"
                "#pdfControlsPanel QComboBox {"
                f"  background-color: {field_bg_str};"
                f"  border: 1px solid {subtle_line_str};"
                "  border-radius: 8px;"
                "  padding: 6px 8px;"
                f"  color: {text_color.name()};"
                "}"
                "#pdfControlsPanel QLineEdit:focus,"
                "#pdfControlsPanel QSpinBox:focus,"
                "#pdfControlsPanel QDoubleSpinBox:focus,"
                "#pdfControlsPanel QTextEdit:focus,"
                "#pdfControlsPanel QComboBox:focus {"
                f"  border: 2px solid {'#007AFF' if is_dark_mode else '#0051D5'};"
                "  outline: none;"
                "}"
                "#pdfControlsPanel QComboBox::drop-down {"
                "  width: 22px;"
                "}"
                "#pdfControlsPanel QListWidget {"
                f"  background-color: {field_bg_str};"
                f"  border: 1px solid {subtle_line_str};"
                "  border-radius: 16px;"
                "  padding: 6px;"
                "}"
                "#pdfControlsPanel QListWidget:focus {"
                f"  border: 2px solid {'#007AFF' if is_dark_mode else '#0051D5'};"
                "}"
                "#pdfControlsPanel QListWidget::item:selected {"
                f"  background-color: {button_hover_str};"
                f"  color: {text_color.name()};"
                "  border-radius: 16px;"
                "}"
                "#pdfControlsPanel QSlider::groove:horizontal {"
                "  background: rgba(100, 100, 100, 180);"
                "  height: 6px;"
                "  border-radius: 3px;"
                "  margin: 0;"
                "}"
                "#pdfControlsPanel QSlider::handle:horizontal {"
                "  background: rgba(255, 255, 255, 230);"
                "  border: 1px solid rgba(180, 180, 180, 200);"
                "  width: 16px; height: 16px; margin: -6px 0; border-radius: 8px;"
                "}"
                f"QWidget#pdfControlsPanel QPushButton:not([objectName='ModernMacButton']) {{ padding: 7px 14px; border-radius: 8px; border: 1px solid {button_border_str};"
                f"  background-color: {button_bg_str}; color: {text_color.name()}; font-weight: 500; }}"
                f"QWidget#pdfControlsPanel QPushButton:not([objectName='ModernMacButton']):hover {{ background-color: {button_hover_str}; }}"
                f"QWidget#pdfControlsPanel QPushButton:not([objectName='ModernMacButton']):focus {{ border: 2px solid {'#007AFF' if is_dark_mode else '#0051D5'}; outline: none; }}"
                f"QWidget#pdfControlsPanel QPushButton:disabled {{ color: {disabled_text_str}; background-color: {disabled_bg_str}; border-color: {subtle_line_str}; }}"
                f"QWidget#pdfControlsPanel QCheckBox {{ color: {text_color.name()}; spacing: 6px; }}"
            )

        self._init_pdf_controls(pdf_controls)

        self.pdf_viewer = PDFViewer()
        self.pdf_viewer.signature_placed.connect(self._on_pdf_signature_placed)
        self.pdf_viewer.signature_selected.connect(self._on_pdf_signature_overlay_selected)
        self.pdf_viewer.page_changed.connect(self._on_pdf_page_changed)

        pdf_layout.addWidget(pdf_left_panel)
        pdf_layout.addWidget(self.pdf_viewer, 1)

        self._pdf_tab_index = self.tab_widget.addTab(pdf_tab, "📄 PDF Signing")
        self._init_pdf_features()
        self._setup_pdf_menu()

    def _init_pdf_controls(self, pdf_controls: QVBoxLayout) -> None:
        if not PDF_AVAILABLE:
            return

        # Cast self to QWidget for type checking (self will be a QMainWindow at runtime)
        parent_widget = cast(QWidget, self)

        # Compute section label colors for both macOS and non-macOS
        palette = self.palette()
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

        pdf_controls.addWidget(self._make_section_label("PDF Document", section_color_hex, top_margin=0))

        open_pdf_btn = _create_button("Open PDF...", parent_widget)
        set_button_icon(open_pdf_btn, "open", "Open PDF...", use_emoji=False)
        open_pdf_btn.clicked.connect(self._on_pdf_tab_open)
        self._pdf_open_btn = open_pdf_btn
        pdf_controls.addWidget(open_pdf_btn)

        close_pdf_btn = _create_button("Close PDF", parent_widget)
        set_button_icon(close_pdf_btn, "close", "Close PDF", use_emoji=False)
        close_pdf_btn.clicked.connect(self._on_pdf_tab_close)
        self._pdf_close_btn = close_pdf_btn
        pdf_controls.addWidget(close_pdf_btn)

        save_pdf_btn = _create_button("Save Signed PDF...", parent_widget)
        set_button_icon(save_pdf_btn, "save", "Save Signed PDF...", use_emoji=False)
        save_pdf_btn.clicked.connect(self._on_pdf_tab_save)
        self._pdf_save_btn = save_pdf_btn
        pdf_controls.addWidget(save_pdf_btn)

        detect_fields_btn = _create_button("Find Fields", parent_widget)
        set_button_icon(detect_fields_btn, "search", "Find signature fields", use_emoji=False)
        detect_fields_btn.setToolTip("Detect likely signature fields on the current PDF page")
        detect_fields_btn.clicked.connect(self._on_pdf_find_fields)
        pdf_controls.addWidget(detect_fields_btn)

        place_field_btn = _create_button("Auto Place on Field", parent_widget)
        set_button_icon(place_field_btn, "sparkle", "Auto place signature on detected field", use_emoji=False)
        place_field_btn.setToolTip("Snap the selected signature into the best detected field on the current page")
        place_field_btn.clicked.connect(self._on_pdf_place_on_field)
        pdf_controls.addWidget(place_field_btn)

        pdf_controls.addWidget(self._make_section_label("Detected Signature Fields", section_color_hex))
        self.pdf_detected_field_list = QListWidget()
        self.pdf_detected_field_list.setMaximumHeight(140)
        self.pdf_detected_field_list.itemSelectionChanged.connect(self._on_detected_field_selection_changed)
        pdf_controls.addWidget(self.pdf_detected_field_list)

        detected_field_btns = QHBoxLayout()
        use_best_field_btn = _create_button("Use Best", parent_widget)
        use_best_field_btn.setToolTip("Clear field selection and use the best detected match")
        use_best_field_btn.clicked.connect(self._on_use_best_detected_field)
        detected_field_btns.addWidget(use_best_field_btn)

        use_selected_field_btn = _create_button("Use Selected", parent_widget)
        use_selected_field_btn.setToolTip("Use the selected detected field for placement")
        use_selected_field_btn.clicked.connect(self._on_pdf_place_on_field)
        detected_field_btns.addWidget(use_selected_field_btn)
        pdf_controls.addLayout(detected_field_btns)

        pdf_controls.addWidget(self._make_section_label("Native Form Fields", section_color_hex))
        self.pdf_form_field_list = QListWidget()
        self.pdf_form_field_list.setMaximumHeight(140)
        self.pdf_form_field_list.itemSelectionChanged.connect(self._on_form_field_selection_changed)
        pdf_controls.addWidget(self.pdf_form_field_list)

        self.pdf_form_value_edit = QLineEdit()
        self.pdf_form_value_edit.setPlaceholderText("Text value or checkbox state (on/off)")
        pdf_controls.addWidget(self.pdf_form_value_edit)

        form_btns = QHBoxLayout()
        detect_form_btn = _create_button("Detect Forms", parent_widget)
        detect_form_btn.clicked.connect(self._on_pdf_detect_form_fields)
        form_btns.addWidget(detect_form_btn)

        apply_form_btn = _create_button("Apply Field", parent_widget)
        apply_form_btn.clicked.connect(self._on_pdf_fill_selected_form_field)
        form_btns.addWidget(apply_form_btn)
        pdf_controls.addLayout(form_btns)

        signature_form_btn = _create_button("Sign Widget", parent_widget)
        signature_form_btn.clicked.connect(self._on_pdf_fill_signature_widget)
        pdf_controls.addWidget(signature_form_btn)

        pdf_controls.addSpacing(20)

        pdf_controls.addWidget(self._make_section_label("Signature Library", section_color_hex))
        pdf_controls.addWidget(QLabel("Click a signature, then click on PDF to place:"))

        # Subtle note about where to manage signatures
        note_lbl = QLabel(
            "<i>Signatures are managed in the <b>Signature Extraction</b> tab (add/remove).</i>"
        )
        note_lbl.setWordWrap(True)
        note_lbl.setStyleSheet("font-size: 11px; color: rgba(128,128,128,0.9);")
        pdf_controls.addWidget(note_lbl)

        self.pdf_sig_list = QListWidget()
        if sys.platform == "darwin":
            self.pdf_sig_list.setSpacing(3)
            self.pdf_sig_list.setWordWrap(False)
            self.pdf_sig_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.pdf_sig_list.setMaximumHeight(300)
        self.pdf_sig_list.itemClicked.connect(self._on_pdf_signature_selected)
        pdf_controls.addWidget(self.pdf_sig_list)

        lib_buttons = QHBoxLayout()
        
        load_sig_btn = _create_button("Load...", parent_widget)
        set_button_icon(load_sig_btn, "open", "Load signature from file", use_emoji=False)
        load_sig_btn.setToolTip(
            "Load signature image from file ("
            + ("⌘⇧L" if sys.platform == "darwin" else "Ctrl+Shift+L")
            + ")"
        )
        load_sig_btn.clicked.connect(self._on_load_signature_clicked)
        lib_buttons.addWidget(load_sig_btn)
        
        refresh_sig_btn = _create_button("Refresh", parent_widget)
        set_button_icon(refresh_sig_btn, "refresh", "Refresh", use_emoji=False)
        refresh_sig_btn.clicked.connect(self._refresh_pdf_signature_library)
        lib_buttons.addWidget(refresh_sig_btn)

        paste_sig_btn = _create_button("Paste", parent_widget)
        set_button_icon(paste_sig_btn, "paste", "Paste", use_emoji=False)
        paste_sig_btn.setToolTip("Paste signature from clipboard (Ctrl/Cmd+V)")
        paste_sig_btn.clicked.connect(self._on_pdf_paste_signature)
        lib_buttons.addWidget(paste_sig_btn)
        pdf_controls.addLayout(lib_buttons)

        pdf_controls.addWidget(self._make_section_label("Signature Appearance", section_color_hex))

        signature_style_grid = QGridLayout()
        signature_style_grid.setContentsMargins(0, 0, 0, 0)
        signature_style_grid.setHorizontalSpacing(8)
        signature_style_grid.setVerticalSpacing(6)

        self.pdf_signature_rotation_input = QSpinBox()
        self.pdf_signature_rotation_input.setRange(0, 359)
        self.pdf_signature_rotation_input.setSuffix("°")
        self.pdf_signature_rotation_input.setValue(0)
        self.pdf_signature_rotation_input.valueChanged.connect(self._on_pdf_signature_style_changed)

        self.pdf_signature_brightness_input = QDoubleSpinBox()
        self.pdf_signature_brightness_input.setRange(0.0, 3.0)
        self.pdf_signature_brightness_input.setDecimals(2)
        self.pdf_signature_brightness_input.setSingleStep(0.05)
        self.pdf_signature_brightness_input.setValue(1.0)
        self.pdf_signature_brightness_input.valueChanged.connect(self._on_pdf_signature_style_changed)

        self.pdf_signature_contrast_input = QDoubleSpinBox()
        self.pdf_signature_contrast_input.setRange(0.0, 3.0)
        self.pdf_signature_contrast_input.setDecimals(2)
        self.pdf_signature_contrast_input.setSingleStep(0.05)
        self.pdf_signature_contrast_input.setValue(1.0)
        self.pdf_signature_contrast_input.valueChanged.connect(self._on_pdf_signature_style_changed)

        self.pdf_signature_saturation_input = QDoubleSpinBox()
        self.pdf_signature_saturation_input.setRange(0.0, 3.0)
        self.pdf_signature_saturation_input.setDecimals(2)
        self.pdf_signature_saturation_input.setSingleStep(0.05)
        self.pdf_signature_saturation_input.setValue(1.0)
        self.pdf_signature_saturation_input.valueChanged.connect(self._on_pdf_signature_style_changed)

        signature_style_grid.addWidget(QLabel("Rotation"), 0, 0)
        signature_style_grid.addWidget(self.pdf_signature_rotation_input, 0, 1)
        signature_style_grid.addWidget(QLabel("Brightness"), 1, 0)
        signature_style_grid.addWidget(self.pdf_signature_brightness_input, 1, 1)
        signature_style_grid.addWidget(QLabel("Contrast"), 2, 0)
        signature_style_grid.addWidget(self.pdf_signature_contrast_input, 2, 1)
        signature_style_grid.addWidget(QLabel("Saturation"), 3, 0)
        signature_style_grid.addWidget(self.pdf_signature_saturation_input, 3, 1)

        reset_style_btn = _create_button("Reset Style", parent_widget)
        reset_style_btn.setToolTip("Reset signature style to default")
        reset_style_btn.clicked.connect(self._on_pdf_signature_style_reset)

        style_row = QHBoxLayout()
        style_row.addLayout(signature_style_grid)
        style_row.addWidget(reset_style_btn)
        pdf_controls.addLayout(style_row)

        pdf_controls.addWidget(self._make_section_label("Signature Templates", section_color_hex))
        pdf_controls.addWidget(QLabel("Save templates from placed signatures to reuse later:"))

        template_header = QHBoxLayout()
        template_name_label = QLabel("Name")
        template_header.addWidget(template_name_label)
        template_header.addStretch()
        self.pdf_template_name_input = QLineEdit()
        self.pdf_template_name_input.setPlaceholderText("Template name")
        self.pdf_template_name_input.setMaximumWidth(160)
        template_header.addWidget(self.pdf_template_name_input, 1)
        pdf_controls.addLayout(template_header)

        self.pdf_template_list = QListWidget()
        self.pdf_template_list.setMaximumHeight(200)
        self.pdf_template_list.itemSelectionChanged.connect(self._on_pdf_template_selection_changed)
        pdf_controls.addWidget(self.pdf_template_list)

        template_btns = QHBoxLayout()
        save_template_btn = _create_button("Save Template", parent_widget)
        set_button_icon(save_template_btn, "save", "Save Template", use_emoji=False)
        save_template_btn.setToolTip("Create a reusable placement template from a placed signature")
        save_template_btn.clicked.connect(self._on_pdf_template_save)
        template_btns.addWidget(save_template_btn)

        apply_template_btn = _create_button("Apply Template", parent_widget)
        set_button_icon(apply_template_btn, "sparkle", "Apply Template", use_emoji=False)
        apply_template_btn.setToolTip("Apply the selected template to this page")
        apply_template_btn.clicked.connect(self._on_pdf_template_apply)
        template_btns.addWidget(apply_template_btn)
        pdf_controls.addLayout(template_btns)

        template_batch_btns = QHBoxLayout()
        apply_template_pages_btn = _create_button("Apply to Pages...", parent_widget)
        set_button_icon(apply_template_pages_btn, "bulk", "Apply to Pages...", use_emoji=False)
        apply_template_pages_btn.setToolTip("Apply the selected template to multiple pages")
        apply_template_pages_btn.clicked.connect(self._on_pdf_template_apply_to_pages)
        template_batch_btns.addWidget(apply_template_pages_btn)

        delete_template_btn = _create_button("Delete Template", parent_widget)
        set_button_icon(delete_template_btn, "close", "Delete Template", use_emoji=False)
        delete_template_btn.clicked.connect(self._on_pdf_template_delete)
        template_batch_btns.addWidget(delete_template_btn)
        pdf_controls.addLayout(template_batch_btns)

        bulk_sign_btn = _create_button("Apply to Multiple Pages...", parent_widget)
        set_button_icon(bulk_sign_btn, "bulk", "Apply to Multiple Pages...", use_emoji=False)
        bulk_sign_btn.setToolTip("Apply signature to multiple pages at once")
        bulk_sign_btn.clicked.connect(self._on_bulk_sign_clicked)
        pdf_controls.addWidget(bulk_sign_btn)

        pdf_controls.addSpacing(20)

        # Instructions panel - let theme system handle styling
        instructions = QLabel(
            "✨ <b>Quick Start</b><br><br>"
            "1️⃣ Click <b>Open PDF</b><br>"
            "2️⃣ Select a signature from library or paste<br>"
            "3️⃣ Click on PDF to place signature<br>"
            "4️⃣ Navigate pages and add more if needed<br>"
            "5️⃣ <b>Save Signed PDF</b> when complete<br><br>"
            "💡 Tip: Use "
            + ("⌘⇧V" if sys.platform == "darwin" else "Ctrl+Shift+V")
            + " to paste from clipboard"
        )
        instructions.setObjectName("instructionsPanel")  # Let theme system style it
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        instructions.setTextFormat(Qt.TextFormat.RichText)
        pdf_controls.addWidget(instructions)

        pdf_controls.addSpacing(10)

        self.pdf_coord_tooltips_cb = QCheckBox("Show coordinate tooltips")
        self.pdf_coord_tooltips_cb.setToolTip("Display PDF page coordinates while hovering/moving/resizing signatures")
        self.pdf_coord_tooltips_cb.setChecked(False)
        self.pdf_coord_tooltips_cb.stateChanged.connect(self._on_pdf_coord_tooltips_toggled)
        pdf_controls.addWidget(self.pdf_coord_tooltips_cb)

        pdf_controls.addStretch()

    def _init_pdf_features(self):
        """Initialize PDF-specific state. Called from __init__ if PDF_AVAILABLE."""
        self.audit_logger: Optional[AuditLogger] = None
        self._pending_sig_path: Optional[str] = None
        self._current_pdf_path: Optional[str] = None
        self._form_field_editor = PdfFormFieldEditor() if PDF_AVAILABLE else None
        self._form_fields_cache = []
        self._current_pdf_template_id: Optional[str] = None
        self._last_pdf_placement = None
        self._selected_pdf_signature_index: int = -1
        self._selected_pdf_signature_style: Dict[str, float] = {
            "rotation_deg": 0.0,
            "brightness": 1.0,
            "contrast": 1.0,
            "saturation": 1.0,
        }
        self._is_syncing_signature_style_controls = False
        # Bulk placement state
        self._bulk_pages: list = []
        self._bulk_sig_path: str = ""
        self._bulk_pixmap: Optional[QPixmap] = None
        self._bulk_use_same_pos: bool = False
        self._bulk_signature_geometry: Optional[dict] = None
        self._bulk_signature_style: Dict[str, float] = {
            "rotation_deg": 0.0,
            "brightness": 1.0,
            "contrast": 1.0,
            "saturation": 1.0,
        }
        self._update_pdf_control_states()
    
    def _setup_pdf_menu(self):
        """Add PDF menu to menu bar. Called from __init__ if PDF_AVAILABLE."""
        pdf_menu = QMenu("&PDF", self)
        self.menuBar().addMenu(pdf_menu)
        
        open_pdf_act = QAction("&Open PDF...", self)
        open_pdf_act.setShortcut(QKeySequence("Meta+Shift+O"))
        open_pdf_act.setStatusTip("Open a PDF file for signing")
        open_pdf_act.triggered.connect(self.on_pdf_open)
        pdf_menu.addAction(open_pdf_act)
        
        close_pdf_act = QAction("&Close PDF", self)
        close_pdf_act.setStatusTip("Close the current PDF")
        close_pdf_act.triggered.connect(self.on_pdf_close)
        pdf_menu.addAction(close_pdf_act)
        
        pdf_menu.addSeparator()
        
        load_sig_act = QAction("&Load Signature...", self)
        load_sig_act.setShortcut(QKeySequence("Meta+Shift+L"))
        load_sig_act.setStatusTip("Load signature image from file")
        load_sig_act.triggered.connect(self._on_load_signature_clicked)
        pdf_menu.addAction(load_sig_act)
        
        paste_sig_act = QAction("&Paste Signature from Clipboard", self)
        paste_sig_act.setShortcut(QKeySequence.StandardKey.Paste)
        paste_sig_act.setStatusTip("Paste signature from clipboard for placement")
        paste_sig_act.triggered.connect(self._on_pdf_paste_signature)
        pdf_menu.addAction(paste_sig_act)
        
        pdf_menu.addSeparator()
        
        save_pdf_act = QAction("&Save Signed PDF...", self)
        save_pdf_act.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_pdf_act.setStatusTip("Save the signed PDF")
        save_pdf_act.triggered.connect(self.on_pdf_save)
        pdf_menu.addAction(save_pdf_act)

        find_fields_act = QAction("&Find Signature Fields", self)
        find_fields_act.setStatusTip("Detect likely signature fields on the current page")
        find_fields_act.triggered.connect(self._on_pdf_find_fields)
        pdf_menu.addAction(find_fields_act)

        place_field_act = QAction("&Auto Place on Field", self)
        place_field_act.setStatusTip("Place the selected signature into the best detected field")
        place_field_act.triggered.connect(self._on_pdf_place_on_field)
        pdf_menu.addAction(place_field_act)

        highlight_field_act = QAction("Add &Highlight to Selected Field", self)
        highlight_field_act.setStatusTip("Write a review highlight on the currently selected detected field")
        highlight_field_act.triggered.connect(self._on_pdf_add_highlight_to_selected_field)
        pdf_menu.addAction(highlight_field_act)

        comment_field_act = QAction("Add &Comment to Selected Field", self)
        comment_field_act.setStatusTip("Attach a note annotation to the currently selected detected field")
        comment_field_act.triggered.connect(self._on_pdf_add_comment_to_selected_field)
        pdf_menu.addAction(comment_field_act)

        pdf_menu.addSeparator()
        
        view_logs_act = QAction("View &Audit Logs", self)
        view_logs_act.setStatusTip("View audit logs for current PDF")
        view_logs_act.triggered.connect(self.on_pdf_view_audit_logs)
        pdf_menu.addAction(view_logs_act)
    
    def on_pdf_open(self):
        """Open a PDF file for signing."""
        if not PDF_AVAILABLE:
            hint = stack_install_hint()
            QMessageBox.warning(self, "Feature Unavailable",
                              "PDF features are currently unavailable in this environment.\n"
                              f"Install with: {hint}")
            return
        
        path = self._native_open_file("Open PDF", "PDF Files (*.pdf)")
        if not path:
            return

        # Load the visible viewer before mutating session state. This keeps a
        # failed open from leaving the app claiming that a blank document is
        # active.
        self._clear_pdf_pending_signature_state()
        if not hasattr(self, "pdf_viewer") or not self.pdf_viewer.open_pdf(path):
            self.statusBar().showMessage(f"Unable to open PDF: {Path(path).name}", 4000)
            return

        self._current_pdf_path = path
        self._reset_pdf_signature_selection_state(reset_controls=True)
        self.session.init_pdf_state()
        if self.session.pdf_state:
            self.session.pdf_state.current_pdf_path = path

        QMessageBox.information(
            self, "PDF Opened",
            f"PDF opened: {Path(path).name}\n\n"
            "You can now:\n"
            "• Browse pages with persistent signature placements\n"
            "• Detect likely signature fields\n"
            "• Place signatures from the library or clipboard\n"
            "• Track audit logs"
        )
        
        # Initialize audit logger
        self.audit_logger = AuditLogger(path, self.session.user_email)
        self.audit_logger.log_open()
        self._restore_persisted_pdf_placements(path)
        
        self.statusBar().showMessage(f"Opened PDF: {Path(path).name}")
        self._update_pdf_control_states()
        if hasattr(self, "_refresh_toolbar_action_states"):
            self._refresh_toolbar_action_states()

    def _restore_persisted_pdf_placements(self, path: str) -> None:
        """Restore placements saved for the exact current PDF file."""
        if not self.pdf_viewer:
            return
        placements = load_document_session(path)
        if not placements:
            placements = read_signature_manifest(path)
        if placements:
            self.pdf_viewer.restore_signature_placements(placements)
            if self.session.pdf_state:
                self.session.pdf_state.placed_signatures = list(placements)

    def _update_pdf_control_states(self) -> None:
        """Keep document actions aligned with the visible viewer state."""
        has_pdf = bool(self._current_pdf_path and self.pdf_viewer and self.pdf_viewer.renderer)
        if hasattr(self, "_pdf_close_btn"):
            self._pdf_close_btn.setEnabled(has_pdf)
        if hasattr(self, "_pdf_save_btn"):
            self._pdf_save_btn.setEnabled(has_pdf)

    @staticmethod
    def _coerce_pdf_signature_style(signature_style: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Normalize signature style values from control input and persisted data."""
        style = signature_style or {}
        def _coerce(value: Any, default: float) -> float:
            try:
                return float(value)
            except (TypeError, ValueError):
                return float(default)

        return {
            "rotation_deg": _coerce(style.get("rotation_deg", 0.0), 0.0) % 360.0,
            "brightness": _coerce(style.get("brightness", 1.0), 1.0),
            "contrast": _coerce(style.get("contrast", 1.0), 1.0),
            "saturation": _coerce(style.get("saturation", 1.0), 1.0),
        }

    def _signature_style_from_controls(self) -> Dict[str, float]:
        return self._coerce_pdf_signature_style(
            {
                "rotation_deg": self.pdf_signature_rotation_input.value(),
                "brightness": self.pdf_signature_brightness_input.value(),
                "contrast": self.pdf_signature_contrast_input.value(),
                "saturation": self.pdf_signature_saturation_input.value(),
            }
        )

    def _set_signature_style_controls(self, signature_style: Dict[str, float]) -> None:
        style = self._coerce_pdf_signature_style(signature_style)
        self._is_syncing_signature_style_controls = True
        try:
            self.pdf_signature_rotation_input.setValue(int(round(style["rotation_deg"])))
            self.pdf_signature_brightness_input.setValue(style["brightness"])
            self.pdf_signature_contrast_input.setValue(style["contrast"])
            self.pdf_signature_saturation_input.setValue(style["saturation"])
        finally:
            self._is_syncing_signature_style_controls = False

        self._selected_pdf_signature_style = style

    def _on_pdf_signature_style_changed(self, *_args) -> None:
        if self._is_syncing_signature_style_controls:
            return

        style = self._signature_style_from_controls()
        self._selected_pdf_signature_style = style

        if not self.pdf_viewer:
            return

        if self._selected_pdf_signature_index >= 0:
            self.pdf_viewer.page_view.update_signature_style(self._selected_pdf_signature_index, style)
            if self._current_pdf_path:
                save_document_session(self._current_pdf_path, self.pdf_viewer.get_placed_signatures())
            return

        if self._pending_sig_path:
            self.pdf_viewer.set_signature_style_for_placement(style)

    def _on_pdf_signature_style_reset(self) -> None:
        self._set_signature_style_controls(self._coerce_pdf_signature_style({}))
        self._on_pdf_signature_style_changed()

    def _clear_pdf_pending_signature_state(self) -> None:
        self._pending_sig_path = None
        if self.pdf_viewer:
            clear_pending = getattr(self.pdf_viewer, "clear_signature_placement", None)
            if callable(clear_pending):
                clear_pending()

    def _reset_pdf_signature_selection_state(self, *, reset_controls: bool = False) -> None:
        self._selected_pdf_signature_index = -1
        self._selected_pdf_signature_style = self._signature_style_from_controls()
        if reset_controls:
            self._set_signature_style_controls(self._coerce_pdf_signature_style({}))
            self._selected_pdf_signature_style = self._signature_style_from_controls()
        if self.pdf_viewer and self._pending_sig_path:
            self.pdf_viewer.set_signature_style_for_placement(self._selected_pdf_signature_style)

    def _on_pdf_page_changed(self, _page: int) -> None:
        """Clear overlay edit selection when the page changes."""
        self._reset_pdf_signature_selection_state(reset_controls=False)

    def _on_pdf_signature_overlay_selected(self, index: int) -> None:
        if index < 0:
            self._selected_pdf_signature_index = -1
            # Keep current controls as pending style for the next placement.
            self._selected_pdf_signature_style = self._signature_style_from_controls()
            return

        self._selected_pdf_signature_index = index
        style = self.pdf_viewer.page_view.get_signature_style(index)
        self._selected_pdf_signature_style = style
        self._set_signature_style_controls(style)
        if self._current_pdf_path and self.pdf_viewer:
            save_document_session(self._current_pdf_path, self.pdf_viewer.get_placed_signatures())
    
    def on_pdf_close(self):
        """Close the current PDF."""
        if hasattr(self, "pdf_viewer"):
            self.pdf_viewer.close_pdf()
        self._current_pdf_path = None
        self._current_pdf_template_id = None
        self._clear_pdf_pending_signature_state()
        self._clear_bulk_signature_state()
        self._reset_pdf_signature_selection_state(reset_controls=True)
        if self.session.pdf_state:
            self.session.clear_pdf_state()
            self.audit_logger = None
            self.statusBar().showMessage("PDF closed")
        else:
            self.statusBar().showMessage("No PDF open")
        self._update_pdf_control_states()
        if hasattr(self, "_refresh_toolbar_action_states"):
            self._refresh_toolbar_action_states()
    
    def on_pdf_save(self):
        """Save the signed PDF."""
        # Check license before allowing PDF save operations
        from desktop_app.license.restrictions import check_and_enforce_pdf_operations_license
        if not check_and_enforce_pdf_operations_license(self):
            self.statusBar().showMessage("PDF operations require a license", 2000)
            return
        
        if not self.session.pdf_state or not self.session.pdf_state.current_pdf_path:
            QMessageBox.warning(self, "No PDF", "No PDF is currently open")
            return
        
        placed_sigs = []
        if hasattr(self, "pdf_viewer") and self.pdf_viewer:
            placed_sigs = self.pdf_viewer.get_placed_signatures()
        elif self.session.pdf_state:
            placed_sigs = list(self.session.pdf_state.placed_signatures)

        if self.session.pdf_state is not None:
            self.session.pdf_state.placed_signatures = list(placed_sigs)
        if not placed_sigs:
            reply = QMessageBox.question(
                self, "No Signatures",
                "No signatures have been placed. Save anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Ask for output path
        original_name = Path(self.session.pdf_state.current_pdf_path).name
        default_name = f"{Path(original_name).stem}_signed.pdf"
        
        output_path = self._native_save_file("Save Signed PDF", default_name, "PDF Files (*.pdf)")
        if not output_path:
            return
        
        signing_choices = [
            "Visual placement (not cryptographic)",
            "Certificate-backed PAdES",
        ]
        signing_choice, choice_ok = QInputDialog.getItem(
            self,
            "Choose PDF signing semantics",
            "Select how this PDF should be exported:",
            signing_choices,
            0,
            False,
        )
        if not choice_ok:
            return

        signing_mode = "certificate" if signing_choice == signing_choices[1] else "visual"
        certificate_path: str | None = None
        certificate_passphrase: str | None = None
        if signing_mode == "certificate":
            certificate_path = self._native_open_file(
                "Select signing certificate",
                "PKCS#12 Certificates (*.p12 *.pfx)",
            )
            if not certificate_path:
                return
            certificate_passphrase, passphrase_ok = QInputDialog.getText(
                self,
                "Certificate passphrase",
                "Enter the PKCS#12 passphrase:",
                QLineEdit.EchoMode.Password,
            )
            if not passphrase_ok:
                return

        # Export through the canonical explicit signing seam.
        try:
            from desktop_app.workflows.engine import export_pdf_artifact

            export_result = export_pdf_artifact(
                self.session.pdf_state.current_pdf_path,
                output_path,
                signing_mode=signing_mode,
                signatures=placed_sigs if signing_mode == "visual" else None,
                pfx_path=certificate_path,
                passphrase=certificate_passphrase,
            )
            success = bool(export_result) if signing_mode == "visual" else True
            
            if success:
                # Log save operation
                if self.audit_logger:
                    self.audit_logger.log_save(output_path, len(placed_sigs))
                if self._current_pdf_path:
                    save_document_session(self._current_pdf_path, placed_sigs)
                save_document_session(output_path, placed_sigs)

                if signing_mode == "certificate":
                    receipt_path = getattr(export_result, "receipt_path", None)
                    receipt_line = f"\\nReceipt: {receipt_path}" if receipt_path else ""
                    message = (
                        f"Certificate-backed PDF saved to:\\n{output_path}\\n\\n"
                        f"Cryptographic verification passed.{receipt_line}"
                    )
                else:
                    message = (
                        f"Visual-placement PDF saved to:\\n{output_path}\\n\\n"
                        f"Signatures placed: {len(placed_sigs)}\\n"
                        "This export is not a cryptographic signature."
                    )
                QMessageBox.information(self, "Success", message)
                self.statusBar().showMessage(f"💾 Saved: {Path(output_path).name}")
            else:
                QMessageBox.warning(self, "Error", "Failed to save signed PDF")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving PDF:\n{e}")
            if self.audit_logger:
                self.audit_logger.log_error("save_failed", str(e))
        finally:
            if hasattr(self, "_refresh_toolbar_action_states"):
                self._refresh_toolbar_action_states()

    def _on_pdf_coord_tooltips_toggled(self, state: int) -> None:
        """Toggle coordinate tooltips in the PDF viewer."""
        if self.pdf_viewer:
            self.pdf_viewer.enable_coordinate_tooltips(bool(state))

    def _selected_pdf_field_for_annotation(self) -> Optional[dict]:
        """Return currently selected detected field metadata or None."""
        if not self.pdf_viewer or not self._current_pdf_path:
            QMessageBox.information(
                self,
                "No PDF Open",
                "Please open a PDF document first.",
            )
            return None

        candidate = self.pdf_viewer.get_selected_field_candidate()
        if not candidate:
            QMessageBox.information(
                self,
                "No Field Selected",
                "Select a detected field in the signature field list first.",
            )
            return None
        return candidate

    def _annotation_output_path(self) -> str:
        """Return an output path for annotation changes."""
        return self._current_edit_output_path()

    def _on_pdf_add_highlight_to_selected_field(self) -> None:
        """Add a highlight annotation to the selected detected field."""
        candidate = self._selected_pdf_field_for_annotation()
        if not candidate:
            return
        if not self._current_pdf_path:
            return
        try:
            editor = PdfAnnotationEditor(self._current_pdf_path)
            output_path = self._annotation_output_path()
            editor.add_highlight(
                output_path,
                page_index=int(candidate.get("page_index", 0)),
                x=float(candidate.get("x", 0.0)),
                y=float(candidate.get("y", 0.0)),
                width=float(candidate.get("width", 0.0)),
                height=float(candidate.get("height", 0.0)),
                contents=str(candidate.get("field_type", "field")),
            )
            self._reload_edited_pdf(output_path)
            self.statusBar().showMessage("✅ Highlight added to selected field")
        except Exception as exc:
            QMessageBox.critical(self, "Add Highlight Failed", f"Unable to add highlight:\n{exc}")

    def _on_pdf_add_comment_to_selected_field(self) -> None:
        """Add a comment annotation to the selected detected field."""
        candidate = self._selected_pdf_field_for_annotation()
        if not candidate:
            return
        if not self._current_pdf_path:
            return

        comment, ok = QInputDialog.getMultiLineText(
            self,
            "Add Comment",
            "Comment text:",
            "Please review this field.",
        )
        if not ok or not comment.strip():
            return

        try:
            editor = PdfAnnotationEditor(self._current_pdf_path)
            output_path = self._annotation_output_path()
            editor.add_note(
                output_path,
                page_index=int(candidate.get("page_index", 0)),
                x=float(candidate.get("x", 0.0)),
                y=float(candidate.get("y", 0.0)),
                contents=comment,
            )
            self._reload_edited_pdf(output_path)
            self.statusBar().showMessage("✅ Comment added to selected field")
        except Exception as exc:
            QMessageBox.critical(self, "Add Comment Failed", f"Unable to add comment:\n{exc}")

    def on_pdf_view_audit_logs(self) -> None:
        """Show audit logs for the currently open PDF."""
        if not self._current_pdf_path:
            QMessageBox.information(self, "No PDF", "Open a PDF document first to view audit logs.")
            return

        if not self.audit_logger:
            QMessageBox.information(
                self,
                "No Audit Data",
                "No audit session is active for the current PDF.",
            )
            return

        logs = get_audit_logs_for_pdf(self._current_pdf_path)
        if not logs:
            QMessageBox.information(self, "Audit Logs", "No audit events found for this PDF.")
            return

        lines = ["PDF Audit Log"]
        for entry in logs[:200]:
            detail = entry.details or ""
            lines.append(f"{entry.timestamp} | {entry.operation} | {detail}")

        QMessageBox.information(
            self,
            "Audit Logs",
            "\n".join(lines),
        )


    def _on_pdf_find_fields(self):
        """Detect likely signature fields in the current PDF page.

        find_signature_fields() runs asynchronously (see desktop_app/pdf/viewer.py);
        it returns immediately, so the field-count status message and sidebar
        refresh happen in the on_complete callback rather than right after
        the call.
        """
        if not self.pdf_viewer or not self.pdf_viewer.renderer:
            QMessageBox.information(self, "No PDF Open", "Please open a PDF document first.")
            return

        current_page = self.pdf_viewer.current_page

        def _on_done(field_candidates):
            self._refresh_detected_field_list()
            if field_candidates:
                self.statusBar().showMessage(
                    f"Detected {len(field_candidates)} field candidate(s) on page {current_page + 1}",
                    3000,
                )

        self.pdf_viewer.find_signature_fields(on_complete=_on_done)

    def _on_pdf_place_on_field(self):
        """Snap the selected signature into the best detected field on the current page.

        place_signature_on_detected_field() may complete synchronously
        (field candidates already cached) or asynchronously (detection has
        to run first); on_complete covers both cases with one code path.
        """
        if not self.pdf_viewer or not self.pdf_viewer.renderer:
            QMessageBox.information(self, "No PDF Open", "Please open a PDF document first.")
            return

        current_page = self.pdf_viewer.current_page

        def _on_done(placed: bool) -> None:
            if placed:
                self.statusBar().showMessage(
                    f"Placed signature on detected field on page {current_page + 1}",
                    3000,
                )

        self.pdf_viewer.place_signature_on_detected_field(on_complete=_on_done)

    def _refresh_detected_field_list(self):
        """Populate the sidebar with detected signature fields."""
        if not hasattr(self, "pdf_detected_field_list"):
            return
        self.pdf_detected_field_list.clear()
        if not self.pdf_viewer or not self.pdf_viewer.page_view.field_candidates:
            item = QListWidgetItem("No detected signature fields")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(Qt.GlobalColor.gray)
            self.pdf_detected_field_list.addItem(item)
            return

        for index, candidate in enumerate(self.pdf_viewer.page_view.field_candidates):
            label = candidate.get("label") or candidate.get("field_type", "field").replace("_", " ")
            confidence = int(float(candidate.get("confidence", 0.0)) * 100)
            item = QListWidgetItem(
                f"{label}  •  p{self.pdf_viewer.current_page + 1}  •  {confidence}%"
            )
            item.setData(Qt.ItemDataRole.UserRole, index)
            item.setToolTip(
                f"{candidate.get('field_type', 'field')} @ "
                f"{candidate.get('x', 0)}, {candidate.get('y', 0)}"
            )
            self.pdf_detected_field_list.addItem(item)

    def _on_detected_field_selection_changed(self):
        """Update the viewer with the selected detected field."""
        if not self.pdf_viewer:
            return
        selected = self.pdf_detected_field_list.selectedItems()
        if not selected:
            self.pdf_viewer.set_selected_field_candidate_index(None)
            return
        self.pdf_viewer.set_selected_field_candidate_index(int(selected[0].data(Qt.ItemDataRole.UserRole)))

    def _on_use_best_detected_field(self):
        """Clear detected field selection and use the best match."""
        if self.pdf_viewer:
            self.pdf_viewer.set_selected_field_candidate_index(None)
            if hasattr(self, "pdf_detected_field_list"):
                self.pdf_detected_field_list.clearSelection()

    def _on_pdf_detect_form_fields(self):
        """Inspect native form widgets in the current PDF."""
        if not self._form_field_editor or not self._current_pdf_path:
            QMessageBox.information(self, "No PDF Open", "Please open a PDF document first.")
            return

        self._refresh_pdf_form_field_list()
        if hasattr(self, "pdf_form_field_list"):
            self.statusBar().showMessage(
                f"Detected {self.pdf_form_field_list.count()} native form field(s)",
                3000,
            )

    def _refresh_pdf_form_field_list(self):
        """Populate the sidebar with native PDF form fields."""
        if not hasattr(self, "pdf_form_field_list"):
            return

        self.pdf_form_field_list.clear()
        if not self._form_field_editor or not self._current_pdf_path:
            return

        try:
            fields = self._form_field_editor.detect_pdf(self._current_pdf_path)
        except Exception as exc:
            QMessageBox.warning(self, "Form Detection Failed", f"Unable to inspect native form fields:\n{exc}")
            return

        self._form_fields_cache = fields
        if not fields:
            item = QListWidgetItem("No native form fields detected")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(Qt.GlobalColor.gray)
            self.pdf_form_field_list.addItem(item)
            return

        for index, field in enumerate(fields):
            item = QListWidgetItem(
                f"{field.field_name}  •  {field.field_type}  •  p{field.page_index + 1}"
            )
            item.setData(Qt.ItemDataRole.UserRole, index)
            tooltip_bits = [field.tooltip or field.value or field.field_name]
            if field.choices:
                tooltip_bits.append("Choices: " + ", ".join(field.choices))
            if field.on_state:
                tooltip_bits.append(f"On state: {field.on_state}")
            item.setToolTip(" | ".join(bit for bit in tooltip_bits if bit))
            self.pdf_form_field_list.addItem(item)

    def _on_form_field_selection_changed(self):
        """Load the selected form field value into the editor."""
        if not hasattr(self, "_form_fields_cache") or not self.pdf_form_field_list.selectedItems():
            return
        index = int(self.pdf_form_field_list.selectedItems()[0].data(Qt.ItemDataRole.UserRole))
        if 0 <= index < len(self._form_fields_cache):
            field = self._form_fields_cache[index]
            self.pdf_form_value_edit.setText(field.value if field.value != "Off" else "")

    def _on_pdf_fill_selected_form_field(self):
        """Fill the selected native form field with the entered value."""
        if not self._form_field_editor or not self._current_pdf_path:
            QMessageBox.information(self, "No PDF Open", "Please open a PDF document first.")
            return
        selected = self.pdf_form_field_list.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Field Selected", "Select a form field first.")
            return

        index = int(selected[0].data(Qt.ItemDataRole.UserRole))
        if not hasattr(self, "_form_fields_cache") or not (0 <= index < len(self._form_fields_cache)):
            return

        field = self._form_fields_cache[index]
        value = self.pdf_form_value_edit.text().strip()
        if not value and "check" in field.field_type.lower():
            value = "on"
        if not value and "text" in field.field_type.lower():
            QMessageBox.information(self, "Missing Value", "Enter a value for the text field.")
            return

        output_path = self._current_edit_output_path()
        try:
            changed = self._form_field_editor.fill_field(
                self._current_pdf_path,
                output_path,
                field.field_name,
                value=value,
            )
            if not changed:
                QMessageBox.warning(self, "No Change", "The selected field could not be updated.")
                return
            self._reload_edited_pdf(output_path)
            self._refresh_pdf_form_field_list()
            self.statusBar().showMessage(f"Filled form field: {field.field_name}", 3000)
        except Exception as exc:
            QMessageBox.critical(self, "Form Fill Failed", f"Unable to fill the field:\n{exc}")

    def _on_pdf_fill_signature_widget(self):
        """Insert the selected signature into a native signature field if present."""
        if not self._form_field_editor or not self._current_pdf_path:
            QMessageBox.information(self, "No PDF Open", "Please open a PDF document first.")
            return
        if not self._pending_sig_path or not Path(self._pending_sig_path).exists():
            QMessageBox.information(self, "No Signature Selected", "Select a signature image first.")
            return

        selected = self.pdf_form_field_list.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Field Selected", "Select a form field first.")
            return

        index = int(selected[0].data(Qt.ItemDataRole.UserRole))
        if not hasattr(self, "_form_fields_cache") or not (0 <= index < len(self._form_fields_cache)):
            return

        field = self._form_fields_cache[index]
        output_path = self._current_edit_output_path()
        try:
            changed = self._form_field_editor.fill_field(
                self._current_pdf_path,
                output_path,
                field.field_name,
                signature_image_path=self._pending_sig_path,
            )
            if not changed:
                QMessageBox.warning(self, "No Change", "The selected field could not be signed.")
                return
            self._reload_edited_pdf(output_path)
            self._refresh_pdf_form_field_list()
            self.statusBar().showMessage(f"Signed native widget: {field.field_name}", 3000)
        except Exception as exc:
            QMessageBox.critical(self, "Widget Signing Failed", f"Unable to sign the widget:\n{exc}")

    def _current_edit_output_path(self) -> str:
        """Return the current editable output path for native PDF changes."""
        if not self._current_pdf_path:
            raise ValueError("No active PDF")
        path = Path(self._current_pdf_path)
        return str(path.with_name(f"{path.stem}_edited{path.suffix}"))

    def _reload_edited_pdf(self, output_path: str):
        """Reload the viewer after a native PDF edit save."""
        if self.pdf_viewer:
            self.pdf_viewer.open_pdf(output_path)
        self._current_pdf_path = output_path
        self._clear_pdf_pending_signature_state()
        self._reset_pdf_signature_selection_state(reset_controls=True)
        self._form_fields_cache = []
        if self.session.pdf_state:
            self.session.pdf_state.current_pdf_path = output_path
    
    def _on_pdf_signature_selected(self, item):
        """Handle signature selection from library."""
        sig_path = item.data(Qt.ItemDataRole.UserRole)
        if not sig_path or not Path(sig_path).exists():
            return
        
        # Check if PDF is open
        if not self.pdf_viewer or not self.pdf_viewer.renderer:
            QMessageBox.information(
                self, "No PDF Open",
                "Please open a PDF document first before selecting a signature."
            )
            return
        
        # Load signature image
        pixmap = QPixmap(sig_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Error", "Failed to load signature image")
            return
        
        # Store path for later use when saving
        self._pending_sig_path = sig_path
        self._selected_pdf_signature_index = -1

        # Set signature for placement in viewer (with path)
        self.pdf_viewer.set_signature_for_placement(pixmap, sig_path)
        self.pdf_viewer.set_signature_style_for_placement(self._signature_style_from_controls())
        
        self.statusBar().showMessage(f"✏️ Click on PDF to place signature: {Path(sig_path).name}")

    def _refresh_pdf_template_list(self):
        """Refresh template list in the PDF controls panel."""
        self.pdf_template_list.clear()
        templates = list_templates()

        if not templates:
            item = QListWidgetItem("📝 No signature templates yet")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(Qt.GlobalColor.gray)
            self.pdf_template_list.addItem(item)
            return

        for template in templates:
            anchor_note = ""
            if template.use_field_anchor:
                anchor_note = " • anchored"
            item = QListWidgetItem(
                f"{template.name}  •  p{template.page_index + 1}{anchor_note}"
            )
            item.setData(Qt.ItemDataRole.UserRole, template.template_id)
            item.setToolTip(
                f"Signature: {template.signature_path}\n"
                f"Source PDF: {template.source_pdf_name or 'Current document'}\n"
                f"Relative box: x={template.x_ratio:.3f}, y={template.y_ratio:.3f}, "
                f"w={template.width_ratio:.3f}, h={template.height_ratio:.3f}"
            )
            self.pdf_template_list.addItem(item)

        if self._current_pdf_template_id:
            for index in range(self.pdf_template_list.count()):
                item = self.pdf_template_list.item(index)
                if item.data(Qt.ItemDataRole.UserRole) == self._current_pdf_template_id:
                    self.pdf_template_list.setCurrentItem(item)
                    break

    def _on_pdf_template_selection_changed(self):
        """Load selected template into template controls."""
        selected = self.pdf_template_list.selectedItems()
        if not selected:
            return

        template_id = selected[0].data(Qt.ItemDataRole.UserRole)
        if not template_id:
            return

        template = get_template(template_id)
        if not template:
            return

        self._current_pdf_template_id = template_id
        if hasattr(self, "pdf_template_name_input"):
            self.pdf_template_name_input.setText(template.name)

    def _resolve_signature_placement_rect(
        self,
        template: SignaturePlacementTemplate,
        sig_pixmap: QPixmap,
        *,
        skip_detection: bool = False,
    ) -> Optional[tuple]:
        """Resolve template placement rectangle for the active page.

        `skip_detection` is set by the multi-page bulk-apply loop
        (`_on_pdf_template_apply_to_pages`), which batch-detects fields for
        every target page up front (see `_run_field_detection_batch`) instead
        of detecting once per page inside this per-page call. When set,
        this trusts whatever `pdf_viewer.page_view.field_candidates` already
        holds for the current page (populated by `goto_page()` ->
        `_load_page_field_candidates()` reading the pre-computed batch
        result) rather than re-running detection.
        """
        if not self.pdf_viewer:
            return None

        if not self.pdf_viewer.page_view.pixmap:
            return None

        if template.use_field_anchor and template.anchor_x_ratio is not None and template.anchor_y_ratio is not None:
            if not skip_detection:
                self.pdf_viewer._detect_signature_fields_silent()
            rect = self.pdf_viewer.build_field_anchor_signature_rect_from_ratio(
                template.anchor_x_ratio,
                template.anchor_y_ratio,
                sig_pixmap=sig_pixmap,
            )
            if rect is not None:
                return rect

        return self.pdf_viewer.build_scaled_signature_rect(
            template.x_ratio,
            template.y_ratio,
            template.width_ratio,
            template.height_ratio,
        )

    def _run_after_bulk_field_detection(
        self,
        pages: List[int],
        needs_detection: bool,
        then_fn: Callable[[], None],
    ) -> None:
        """Run `then_fn()` immediately, or after a single batched background
        field-detection pass over `pages` when `needs_detection` is True.

        Shared by `_on_pdf_template_apply_to_pages` and the bulk branch of
        `_on_pdf_signature_placed` — both previously called
        `_detect_signature_fields_silent()` once per page inside a
        synchronous loop for "adaptive" (field-anchored) bulk placement,
        which for N pages meant N sequential blocking pdfium-render +
        OpenCV calls on the UI thread. See
        docs/analysis/2026-07-01_performance_optimization_audit.md.
        """
        if not needs_detection or not self.pdf_viewer:
            then_fn()
            return

        self.statusBar().showMessage(f"Detecting fields on {len(pages)} page(s)...", 0)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        def _on_ready(_all_candidates: Dict[int, list]) -> None:
            QApplication.restoreOverrideCursor()
            then_fn()

        self.pdf_viewer.detect_fields_for_pages(pages, on_complete=_on_ready)

    def _apply_template_to_target_page(
        self,
        page_num: int,
        template: SignaturePlacementTemplate,
        run_id: Optional[str],
        *,
        skip_detection: bool = False,
    ) -> bool:
        """Apply one template on one page.

        `skip_detection` is forwarded to `_resolve_signature_placement_rect`
        — set by the multi-page bulk-apply loop once it has already
        batch-detected fields for all target pages.
        """
        if not self.pdf_viewer or not self.pdf_viewer.renderer:
            return False

        if page_num < 0 or page_num >= self.pdf_viewer.renderer.page_count():
            return False

        if not Path(template.signature_path).exists():
            return False

        self.pdf_viewer.goto_page(page_num)

        if self.pdf_viewer.page_view.signatures is None:
            self.pdf_viewer.page_view.signatures = []

        signature_pixmap = QPixmap(template.signature_path)
        if signature_pixmap.isNull():
            return False

        rect = self._resolve_signature_placement_rect(
            template, signature_pixmap, skip_detection=skip_detection
        )
        if rect is None:
            return False

        x, y, width, height = rect
        self.pdf_viewer.page_view.add_signature_overlay(
            x,
            y,
            width,
            height,
            signature_pixmap,
            template.signature_path,
        )

        if self.audit_logger:
            details = (
                f"Template '{template.name}' applied on page {page_num + 1}"
            )
            self.audit_logger.log_place_signature(
                page_num,
                template.signature_path,
                x,
                y,
                width,
                height,
                run_id=run_id,
                details=details,
            )
        return True

    def _on_pdf_template_apply(self):
        """Apply the selected template on the current page."""
        if not self._current_pdf_path:
            QMessageBox.information(self, "No PDF", "Please open a PDF document first.")
            return
        if not hasattr(self, "pdf_template_list"):
            return

        template_id = self._current_pdf_template_id
        if not template_id:
            selected = self.pdf_template_list.selectedItems()
            if selected:
                template_id = selected[0].data(Qt.ItemDataRole.UserRole)

        if not template_id:
            QMessageBox.information(self, "No Template", "Please select a template first.")
            return

        template = get_template(template_id)
        if not template:
            QMessageBox.warning(self, "Template Missing", "Template not found.")
            return

        current_page = self.pdf_viewer.current_page if self.pdf_viewer else 0
        if self._apply_template_to_target_page(current_page, template, run_id=None):
            self.statusBar().showMessage(f"✅ Template '{template.name}' applied")
        else:
            QMessageBox.warning(self, "Template Apply Failed", "Template could not be applied on this page.")

    def _on_pdf_template_apply_to_pages(self):
        """Apply selected template to multiple pages."""
        if not self._current_pdf_path or not self.pdf_viewer or not self.pdf_viewer.renderer:
            QMessageBox.information(self, "No PDF", "Please open a PDF document first.")
            return

        if not hasattr(self, "pdf_template_list"):
            return

        template_id = self._current_pdf_template_id
        selected = self.pdf_template_list.selectedItems()
        if selected:
            template_id = selected[0].data(Qt.ItemDataRole.UserRole)
        if not template_id:
            QMessageBox.information(self, "No Template", "Please select a template first.")
            return

        template = get_template(template_id)
        if not template:
            QMessageBox.warning(self, "Template Missing", "Template not found.")
            return

        dialog = BulkSignDialog(
            self.pdf_viewer.renderer.page_count(),
            self.pdf_viewer.current_page,
            self
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        target_pages = dialog.get_selected_pages()
        target_pages = sorted(set(target_pages))
        if not target_pages:
            return

        reply = QMessageBox.question(
            self,
            "Apply Template",
            f"Apply template '{template.name}' to {len(target_pages)} page(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        run_id = None
        if self.audit_logger:
            run_id = self.audit_logger.start_run(
                "template_apply",
                details=f"Applying template '{template.name}'",
                page_count=len(target_pages),
            )

        def _run_placement_loop() -> None:
            placed_count = 0
            for page_num in target_pages:
                if self._apply_template_to_target_page(
                    page_num, template, run_id=run_id, skip_detection=needs_detection
                ):
                    placed_count += 1

            if self.audit_logger and run_id:
                self.audit_logger.finish_run(
                    run_id,
                    success=(placed_count == len(target_pages)),
                    signature_count=placed_count,
                    details=f"Template applied on {placed_count}/{len(target_pages)} page(s)",
                )

            if placed_count:
                skipped = len(target_pages) - placed_count
                if skipped:
                    self.statusBar().showMessage(
                        f"✅ Template '{template.name}' placed on {placed_count} page(s), {skipped} skipped."
                    )
                else:
                    self.statusBar().showMessage(
                        f"✅ Template '{template.name}' placed on {placed_count} page(s)"
                    )
            else:
                QMessageBox.warning(self, "Template Apply Failed", "Template could not be applied to any page.")

        needs_detection = bool(
            template.use_field_anchor
            and template.anchor_x_ratio is not None
            and template.anchor_y_ratio is not None
        )
        self._run_after_bulk_field_detection(target_pages, needs_detection, _run_placement_loop)

    def _on_pdf_template_save(self):
        """Save the currently placed signature as a reusable template."""
        if not self._current_pdf_path:
            QMessageBox.information(self, "No PDF", "Please open a PDF document first.")
            return

        if not self._last_pdf_placement:
            QMessageBox.information(
                self,
                "No Placement",
                "Place a signature on the page first, then save it as a template.",
            )
            return

        sig_path = self._last_pdf_placement.get("sig_path")
        if not sig_path or not Path(sig_path).exists():
            QMessageBox.warning(self, "Missing Signature", "No saved signature image found for this placement.")
            return

        placement_width = int(self._last_pdf_placement.get("width") or 0)
        if placement_width <= 0:
            QMessageBox.warning(self, "Invalid Placement", "Placement geometry is not available.")
            return

        template_name = getattr(self, "pdf_template_name_input", None)
        if template_name is None or not template_name.text().strip():
            template_name = Path(sig_path).stem
        else:
            template_name = template_name.text().strip()

        template = create_template(
            signature_path=sig_path,
            page_index=int(self._last_pdf_placement.get("page") or 0),
            x_ratio=float(self._last_pdf_placement.get("x_ratio") or 0.0),
            y_ratio=float(self._last_pdf_placement.get("y_ratio") or 0.0),
            width_ratio=float(self._last_pdf_placement.get("width_ratio") or 0.0),
            height_ratio=float(self._last_pdf_placement.get("height_ratio") or 0.0),
            name=str(template_name),
            use_field_anchor=bool(self._last_pdf_placement.get("use_field_anchor")),
            field_type=self._last_pdf_placement.get("field_type"),
            field_label=self._last_pdf_placement.get("field_label"),
            field_confidence=self._last_pdf_placement.get("field_confidence"),
            anchor_x_ratio=self._last_pdf_placement.get("anchor_x_ratio"),
            anchor_y_ratio=self._last_pdf_placement.get("anchor_y_ratio"),
            source_pdf_path=self._current_pdf_path,
            source_pdf_name=Path(self._current_pdf_path).name,
        )

        self._current_pdf_template_id = template.template_id
        self._refresh_pdf_template_list()
        self.statusBar().showMessage(f"💾 Template saved: {template.name}")

    def _on_pdf_template_delete(self):
        """Delete selected template."""
        if not hasattr(self, "pdf_template_list"):
            return

        selected = self.pdf_template_list.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Template", "Please select a template to delete.")
            return

        template_id = selected[0].data(Qt.ItemDataRole.UserRole)
        if not template_id:
            return

        template = get_template(template_id)
        if not template:
            QMessageBox.warning(self, "Template Missing", "Template not found.")
            return

        reply = QMessageBox.question(
            self,
            "Delete Template",
            f"Delete template '{template.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if delete_template(template_id):
            if self._current_pdf_template_id == template_id:
                self._current_pdf_template_id = None
            self._refresh_pdf_template_list()
            self.statusBar().showMessage(f"🗑️ Deleted template: {template.name}")
        else:
            QMessageBox.warning(self, "Delete Failed", "Template could not be deleted.")
    
    def _on_pdf_signature_placed(self, page, x, y, width, height, style=None):
        """Handle signature placement on PDF."""
        signature_style = self._coerce_pdf_signature_style(
            style if isinstance(style, dict) else self._signature_style_from_controls()
        )
        self._selected_pdf_signature_style = signature_style
        self._set_signature_style_controls(signature_style)

        # Check if this is bulk placement
        if self._bulk_pages and self._bulk_pixmap:
            source_page = self.pdf_viewer.current_page
            self._bulk_signature_geometry = self._build_bulk_signature_geometry(x, y, width, height)
            if not self._bulk_signature_geometry:
                self.statusBar().showMessage(
                    "⚠️ Bulk placement skipped: unable to compute placement geometry."
                )
                self._clear_bulk_signature_state()
                self.pdf_viewer.goto_page(source_page)
                return

            target_pages = [p for p in self._bulk_pages if p != source_page]
            if self.audit_logger:
                run_id = self.audit_logger.start_run(
                    "bulk_signature_placement",
                    details=f"Bulk placement on {len(set(self._bulk_pages))} page(s) from page {source_page + 1}",
                    page_count=len(set(target_pages)),
                )
            else:
                run_id = None

            use_same_pos = self._bulk_use_same_pos

            def _run_bulk_placement_loop() -> None:
                placed_count = 0
                for target_page in target_pages:
                    self.pdf_viewer.goto_page(target_page)
                    rect = self._compute_bulk_signature_rect_for_target(
                        use_same_pos=use_same_pos, skip_detection=not use_same_pos
                    )

                    if not rect:
                        continue

                    tx, ty, tw, th = rect
                    self.pdf_viewer.page_view.add_signature_overlay(
                        tx,
                        ty,
                        tw,
                        th,
                        self._bulk_pixmap,
                        self._bulk_sig_path,
                        self._bulk_signature_style,
                    )
                    placed_count += 1

                    if self.audit_logger:
                        self.audit_logger.log_place_signature(
                            target_page,
                            self._bulk_sig_path,
                            tx,
                            ty,
                            tw,
                            th,
                            run_id=run_id,
                        )

                self._finish_bulk_placement_run(run_id, placed_count, len(target_pages))
                if self._current_pdf_path and self.pdf_viewer:
                    save_document_session(self._current_pdf_path, self.pdf_viewer.get_placed_signatures())
                self._clear_bulk_signature_state()
                self._clear_pdf_pending_signature_state()

                self.pdf_viewer.goto_page(source_page)
                if placed_count == len(target_pages):
                    self.statusBar().showMessage(f"✅ Signature placed on {placed_count + 1} page(s)")
                else:
                    skipped = len(target_pages) - placed_count
                    self.statusBar().showMessage(
                        f"✅ Signature placed on {placed_count + 1} page(s), {skipped} page(s) skipped."
                    )

            # "Adaptive" mode (not use_same_pos) is the field-anchored case
            # that needs detection; "same position" mode never detects.
            self._run_after_bulk_field_detection(target_pages, not use_same_pos, _run_bulk_placement_loop)
            return

        # Single placement
        selected_field_index = None
        field_metadata = {}
        if self.pdf_viewer and self.pdf_viewer.page_view.selected_field_candidate_index is not None:
            selected_field_index = self.pdf_viewer.page_view.selected_field_candidate_index
            try:
                field_metadata = self.pdf_viewer.page_view.field_candidates[selected_field_index]
            except Exception:
                field_metadata = {}

        page_width = 1
        page_height = 1
        if self.pdf_viewer and self.pdf_viewer.page_view.pixmap:
            page_width = max(1, self.pdf_viewer.page_view.pixmap.width())
            page_height = max(1, self.pdf_viewer.page_view.pixmap.height())

        self._last_pdf_placement = {
            "page": page,
            "sig_path": self._pending_sig_path,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "x_ratio": x / page_width,
            "y_ratio": y / page_height,
            "width_ratio": width / page_width,
            "height_ratio": height / page_height,
            "rotation_deg": signature_style["rotation_deg"],
            "brightness": signature_style["brightness"],
            "contrast": signature_style["contrast"],
            "saturation": signature_style["saturation"],
            "use_field_anchor": selected_field_index is not None,
            "field_type": field_metadata.get("field_type"),
            "field_label": field_metadata.get("label") or field_metadata.get("field_type"),
            "field_confidence": field_metadata.get("confidence"),
            "anchor_x_ratio": (x + width / 2) / page_width,
            "anchor_y_ratio": (y + height / 2) / page_height,
        }

        if self.audit_logger and self._pending_sig_path:
            self.audit_logger.log_place_signature(
                page, self._pending_sig_path, x, y, width, height
            )

        if self.pdf_viewer and self.pdf_viewer.page_view.signatures:
            self._selected_pdf_signature_index = len(self.pdf_viewer.page_view.signatures) - 1
            self._selected_pdf_signature_style = signature_style

        if self._current_pdf_path and self.pdf_viewer:
            save_document_session(self._current_pdf_path, self.pdf_viewer.get_placed_signatures())

        self._clear_pdf_pending_signature_state()
        self.statusBar().showMessage(f"✅ Signature placed on page {page + 1}")

    def _build_bulk_signature_geometry(self, x: int, y: int, width: int, height: int) -> Optional[dict]:
        """Capture placement geometry as page-relative ratios."""
        if not self.pdf_viewer or not self.pdf_viewer.page_view.pixmap:
            return None

        page_width = self.pdf_viewer.page_view.pixmap.width()
        page_height = self.pdf_viewer.page_view.pixmap.height()
        if page_width <= 0 or page_height <= 0:
            return None

        return {
            "source_page": self.pdf_viewer.current_page,
            "x_ratio": x / page_width,
            "y_ratio": y / page_height,
            "width_ratio": width / page_width,
            "height_ratio": height / page_height,
            "anchor_x_ratio": (x + width / 2) / page_width,
            "anchor_y_ratio": (y + height / 2) / page_height,
        }

    def _compute_bulk_signature_rect_for_target(
        self, use_same_pos: bool, *, skip_detection: bool = False
    ) -> Optional[tuple]:
        """Compute signature placement rectangle for the active target page.

        `skip_detection` is set by the bulk-placement loop in
        `_on_pdf_signature_placed` once it has already batch-detected fields
        for every target page (see `_run_after_bulk_field_detection`),
        instead of this method re-detecting once per page.
        """
        if not self.pdf_viewer or not self._bulk_signature_geometry:
            return None

        geometry = self._bulk_signature_geometry
        if use_same_pos:
            return self.pdf_viewer.build_scaled_signature_rect(
                geometry["x_ratio"],
                geometry["y_ratio"],
                geometry["width_ratio"],
                geometry["height_ratio"],
            )

        # Adaptive mode: auto-snapping to nearest detected field near anchor.
        if not skip_detection:
            self.pdf_viewer._detect_signature_fields_silent()
        rect = self.pdf_viewer.build_field_anchor_signature_rect_from_ratio(
            geometry["anchor_x_ratio"],
            geometry["anchor_y_ratio"],
            self._bulk_pixmap,
        )
        if rect is not None:
            return rect

        # Fallback to scaled placement when no usable field is found.
        return self.pdf_viewer.build_scaled_signature_rect(
            geometry["x_ratio"],
            geometry["y_ratio"],
            geometry["width_ratio"],
            geometry["height_ratio"],
        )

    def _finish_bulk_placement_run(
        self,
        run_id: Optional[str],
        placed_count: int,
        total_count: int,
    ) -> None:
        """Finish the active bulk run with a final summary."""
        if not self.audit_logger or not run_id:
            return

        self.audit_logger.finish_run(
            run_id,
            success=(placed_count == total_count),
            signature_count=placed_count,
            details=f"Bulk placement completed on {placed_count}/{total_count} target page(s)",
        )

    def _clear_bulk_signature_state(self) -> None:
        """Reset bulk placement state."""
        self._bulk_pages = []
        self._bulk_sig_path = ""
        self._bulk_pixmap = None
        self._bulk_use_same_pos = False
        self._bulk_signature_geometry = None
        self._bulk_signature_style = self._coerce_pdf_signature_style({})
    
    def _on_pdf_paste_signature(self):
        """Paste signature from clipboard for placement."""
        import tempfile
        import uuid
        
        # Check license before allowing PDF paste operations
        from desktop_app.license.restrictions import check_and_enforce_pdf_operations_license
        if not check_and_enforce_pdf_operations_license(self):
            self.statusBar().showMessage("PDF operations require a license", 2000)
            return
        
        # Check if PDF is open
        if not self.pdf_viewer or not self.pdf_viewer.renderer:
            QMessageBox.information(
                self, "No PDF Open",
                "Please open a PDF document first before pasting a signature."
            )
            return
        
        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()
        
        if pixmap.isNull():
            QMessageBox.information(
                self, "No Image in Clipboard",
                "No image found in clipboard.\n\n"
                "Copy a signature from the Extraction tab first."
            )
            return
        
        # Save clipboard image to temp location for tracking
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"clipboard_sig_{uuid.uuid4().hex[:8]}.png")
        
        # Save pixmap to temp file
        if not pixmap.save(temp_path, "PNG"):
            QMessageBox.warning(self, "Error", "Failed to process clipboard image")
            return
        
        self._pending_sig_path = temp_path
        self._selected_pdf_signature_index = -1
        
        # Set signature for placement in viewer (with path)
        self.pdf_viewer.set_signature_for_placement(pixmap, temp_path)
        self.pdf_viewer.set_signature_style_for_placement(self._signature_style_from_controls())
        
        self.statusBar().showMessage("📋 Click on PDF to place clipboard signature")
    
    def _refresh_pdf_signature_library(self):
        """Refresh the signature library list in PDF tab with coordinate tooltips."""
        self.pdf_sig_list.clear()
        
        # Get signatures from library with metadata
        items = lib.list_items()
        
        if not items:
            item = QListWidgetItem("📝 No signatures saved yet")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(Qt.GlobalColor.gray)
            self.pdf_sig_list.addItem(item)
            
            item2 = QListWidgetItem("💡 Extract & save signatures")
            item2.setFlags(Qt.ItemFlag.NoItemFlags)
            item2.setForeground(Qt.GlobalColor.gray)
            self.pdf_sig_list.addItem(item2)
            
            item3 = QListWidgetItem("   in the Extraction tab first")
            item3.setFlags(Qt.ItemFlag.NoItemFlags)
            item3.setForeground(Qt.GlobalColor.gray)
            self.pdf_sig_list.addItem(item3)
            return
        
        for lib_item in items:
            if not Path(lib_item.path).exists():
                continue
            
            # Create list item with preview
            item = QListWidgetItem(Path(lib_item.path).name)
            
            # Load and scale thumbnail
            pixmap = QPixmap(lib_item.path)
            if not pixmap.isNull():
                thumbnail = pixmap.scaled(
                    80, 40,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                from PySide6.QtGui import QIcon
                item.setIcon(QIcon(thumbnail))
            
            item.setData(Qt.ItemDataRole.UserRole, lib_item.path)
            item.setToolTip(lib_item.tooltip_text)  # Show coordinates in tooltip
            self.pdf_sig_list.addItem(item)
    
    def _load_signature_file(
        self,
        source_path: str,
        handle_duplicate: str = "ask"
    ) -> tuple[bool, str, Optional[str]]:
        """Load a single signature file into the library.
        
        Args:
            source_path: Path to source image file
            handle_duplicate: How to handle duplicates - "ask", "replace", "copy", "skip"
        
        Returns:
            Tuple of (success: bool, message: str, loaded_path: Optional[str])
        """
        try:
            filename = os.path.basename(source_path)
            
            # Check for duplicate
            existing_path = self._check_duplicate_signature(filename)
            
            if existing_path and handle_duplicate == "ask":
                action, _ = self._show_duplicate_dialog(filename, apply_to_all=False)
                handle_duplicate = action
            
            if handle_duplicate == "cancel":
                return False, "Cancelled", None
            
            if handle_duplicate == "skip":
                return False, f"Skipped: {filename}", None
            
            # Determine custom filename for "copy" action
            custom_filename = None
            if existing_path and handle_duplicate == "copy":
                # Generate unique filename with timestamp
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                custom_filename = f"{name}_{timestamp}{ext}"
            elif existing_path and handle_duplicate == "replace":
                # Use original filename to replace
                custom_filename = filename
            
            # Load the signature
            loaded_path = lib.save_image_to_library(
                source_path,
                metadata=None,
                custom_filename=custom_filename
            )
            
            return True, f"Loaded: {os.path.basename(loaded_path)}", loaded_path
            
        except ValueError as e:
            return False, f"Invalid image: {filename} - {str(e)}", None
        except IOError as e:
            return False, f"Failed to load: {filename} - {str(e)}", None
        except Exception as e:
            return False, f"Error: {filename} - {str(e)}", None
    
    def _on_load_signature_clicked(self):
        """Handle Load Signature button click - open file dialog and load signatures."""
        from PySide6.QtWidgets import QFileDialog
        
        # Open file dialog with multi-select
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Load Signature Image(s)")
        file_dialog.setNameFilter("Image Files (*.png *.jpg *.jpeg)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)  # Multi-select
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        
        if not file_dialog.exec():
            return
        
        selected_files = file_dialog.selectedFiles()
        if not selected_files:
            return
        
        # Process files
        loaded_count = 0
        failed_count = 0
        first_loaded_path = None
        duplicate_action = "ask"
        apply_to_all = False
        failed_messages = []
        
        for i, file_path in enumerate(selected_files):
            # Update status for batch operations
            if len(selected_files) > 1:
                self.statusBar().showMessage(
                    f"Loading signatures... ({i + 1}/{len(selected_files)})"
                )
                QApplication.processEvents()
            
            # Handle duplicate action
            if apply_to_all and duplicate_action != "ask":
                handle_dup = duplicate_action
            else:
                handle_dup = "ask"
            
            # Check for duplicate and show dialog if needed
            if handle_dup == "ask":
                filename = os.path.basename(file_path)
                existing = self._check_duplicate_signature(filename)
                if existing:
                    action, apply_checked = self._show_duplicate_dialog(
                        filename,
                        apply_to_all=(len(selected_files) > 1 and i < len(selected_files) - 1)
                    )
                    
                    if action == "cancel":
                        self.statusBar().showMessage("Loading cancelled")
                        return
                    
                    handle_dup = action
                    if apply_checked:
                        duplicate_action = action
                        apply_to_all = True
            
            # Load the file
            success, message, loaded_path = self._load_signature_file(file_path, handle_dup)
            
            if success:
                loaded_count += 1
                if first_loaded_path is None:
                    first_loaded_path = loaded_path
            else:
                failed_count += 1
                if message and not message.startswith("Skipped"):
                    failed_messages.append(message)
        
        # Refresh library
        self._refresh_pdf_signature_library()
        
        # Select first loaded signature
        if first_loaded_path:
            for i in range(self.pdf_sig_list.count()):
                item = self.pdf_sig_list.item(i)
                item_path = item.data(Qt.ItemDataRole.UserRole)
                if item_path == first_loaded_path:
                    self.pdf_sig_list.setCurrentItem(item)
                    self._on_pdf_signature_selected(item)
                    break
        
        # Display summary message
        if loaded_count > 0 and failed_count == 0:
            self.statusBar().showMessage(f"Loaded {loaded_count} signature(s)")
        elif loaded_count > 0 and failed_count > 0:
            msg = f"Loaded {loaded_count}, failed {failed_count}"
            if failed_messages:
                msg += f"\nErrors:\n" + "\n".join(failed_messages[:3])
                if len(failed_messages) > 3:
                    msg += f"\n... and {len(failed_messages) - 3} more"
            QMessageBox.warning(self, "Partial Success", msg)
            self.statusBar().showMessage(f"Loaded {loaded_count} signature(s)")
        elif failed_count > 0:
            msg = f"Failed to load {failed_count} file(s)"
            if failed_messages:
                msg += f"\n\n" + "\n".join(failed_messages[:5])
            QMessageBox.critical(self, "Load Failed", msg)
            self.statusBar().showMessage("Failed to load signatures")
        else:
            self.statusBar().showMessage("No signatures loaded")
    
    def _check_duplicate_signature(self, filename: str) -> Optional[str]:
        """Check if a signature with the same filename exists in library.
        
        Args:
            filename: Filename to check (without path)
        
        Returns:
            Path to existing file if duplicate found, None otherwise
        """
        library_path = os.path.join(lib.library_dir(), filename)
        if os.path.exists(library_path):
            return library_path
        return None
    
    def _show_duplicate_dialog(self, filename: str, apply_to_all: bool = False) -> tuple[str, bool]:
        """Show dialog for handling duplicate signature files.
        
        Args:
            filename: Name of the duplicate file
            apply_to_all: Whether to show "Apply to all" checkbox
        
        Returns:
            Tuple of (action, apply_to_all_checked) where action is:
            - "replace": Overwrite existing file
            - "copy": Create new copy with unique name
            - "skip": Don't load this file
            - "cancel": Cancel entire operation
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Duplicate Signature")
        dialog.setModal(True)
        dialog.resize(450, 200)
        
        layout = QVBoxLayout(dialog)
        
        # Message
        message = QLabel(
            f"A signature named <b>{filename}</b> already exists in your library.\n\n"
            "What would you like to do?"
        )
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Apply to all checkbox (if batch operation)
        apply_to_all_cb = None
        if apply_to_all:
            apply_to_all_cb = QCheckBox("Apply this choice to all remaining duplicates")
            layout.addWidget(apply_to_all_cb)
        
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        replace_btn = QPushButton("Replace")
        replace_btn.setToolTip("Overwrite the existing signature")
        replace_btn.clicked.connect(lambda: dialog.done(1))
        button_layout.addWidget(replace_btn)
        
        copy_btn = QPushButton("Create Copy")
        copy_btn.setToolTip("Save as a new file with a unique name")
        copy_btn.clicked.connect(lambda: dialog.done(2))
        copy_btn.setDefault(True)
        button_layout.addWidget(copy_btn)
        
        skip_btn = QPushButton("Skip")
        skip_btn.setToolTip("Don't load this file")
        skip_btn.clicked.connect(lambda: dialog.done(3))
        button_layout.addWidget(skip_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setToolTip("Cancel loading all files")
        cancel_btn.clicked.connect(lambda: dialog.done(0))
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        result = dialog.exec()
        apply_checked = apply_to_all_cb.isChecked() if apply_to_all_cb else False
        
        action_map = {
            0: "cancel",
            1: "replace",
            2: "copy",
            3: "skip"
        }
        
        return action_map.get(result, "cancel"), apply_checked
    
    def _on_bulk_sign_clicked(self):
        """Handle bulk signature placement across multiple pages."""
        if not self.pdf_viewer or not self.pdf_viewer.renderer:
            QMessageBox.information(
                self, "No PDF Open",
                "Please open a PDF document first."
            )
            return
        
        # Get selected signature from library
        selected_items = self.pdf_sig_list.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self, "No Signature Selected",
                "Please select a signature from the library first."
            )
            return
        
        sig_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
        if not sig_path or not Path(sig_path).exists():
            QMessageBox.warning(self, "Error", "Signature file not found")
            return
        
        # Load signature
        pixmap = QPixmap(sig_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Error", "Failed to load signature image")
            return
        
        # Show bulk placement dialog
        dialog = BulkSignDialog(
            self.pdf_viewer.renderer.page_count(),
            self.pdf_viewer.current_page,
            self
        )
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        selected_pages = dialog.get_selected_pages()
        use_same_pos = dialog.use_same_position()
        
        if not selected_pages:
            return
        
        # Ask user to click where to place signature
        reply = QMessageBox.information(
            self, "Place Signature",
            f"Click on the PDF to choose where to place the signature.\n\n"
            f"It will be applied to {len(selected_pages)} page(s): {', '.join(str(p+1) for p in selected_pages[:5])}"
            f"{'...' if len(selected_pages) > 5 else ''}",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        
        if reply != QMessageBox.StandardButton.Ok:
            return
        
        # Store bulk placement info and set signature for placement
        self._bulk_pages = selected_pages
        self._bulk_sig_path = sig_path
        self._bulk_pixmap = pixmap
        self._bulk_use_same_pos = use_same_pos
        self._bulk_signature_style = self._signature_style_from_controls()
        
        self.pdf_viewer.set_signature_for_placement(pixmap, sig_path)
        self.pdf_viewer.set_signature_style_for_placement(self._bulk_signature_style)
        self.statusBar().showMessage(
            f"📄 Click to place signature on {len(selected_pages)} page(s)"
        )
