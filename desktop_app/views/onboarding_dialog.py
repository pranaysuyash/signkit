"""First-run onboarding dialog to guide new users through initial setup."""

from __future__ import annotations

import sys
from typing import Optional, cast

from desktop_app.config import PricingPlan, get_pricing_plan, get_pricing_plans, get_purchase_url
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPalette
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QWidget,
    QFrame,
)

from desktop_app.resources.icons import get_icon
from desktop_app.widgets.modern_mac_button import ModernMacButton


def _create_button(
    text: str = "",
    parent: Optional[QWidget] = None,
    *,
    use_modern_mac: Optional[bool] = None,
    primary: bool = False,
    color: str = 'blue',
    compact: bool = False  # Dialog buttons are typically not compact
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
    if use_modern_mac is None:
        use_modern_mac = sys.platform == "darwin"

    if use_modern_mac:
        try:
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

    # Default to standard QPushButton
    return QPushButton(text, parent)


class OnboardingDialog(QDialog):
    """Welcome dialog shown on first app launch with quick start guide."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        default_plan_id: str | None = None,
        show_strategic_upgrade: bool = True,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Welcome to SignKit")
        self.setModal(True)
        self.setMinimumWidth(560)
        self.setMaximumWidth(700)
        self._default_plan_id = get_pricing_plan(default_plan_id).plan_id
        self._show_strategic_upgrade = show_strategic_upgrade

        # Apply theme-aware styling
        self._apply_theme()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        header = QLabel("Welcome to SignKit")
        header.setStyleSheet("font-size: 24px; font-weight: 600;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Subtitle
        subtitle = QLabel(
            "Handle sensitive signed documents locally"
            + (" and run recurring packet workflows from folders." if not self._show_strategic_upgrade else ".")
        )
        subtitle.setStyleSheet("font-size: 14px; color: gray;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Why SignKit section
        why_label = QLabel("<b>Why SignKit?</b>")
        why_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(why_label)

        features = [
            ("info", "Privacy First", "Core extraction and PDF work run locally by default. Checkout, updates, and support use network services only when you choose them."),
            ("ok", "Reusable Signature Library", "Extract once, save reusable signatures, and place them across future PDFs."),
            ("apply", "Local PDF Workflow", "Clean signatures, keep a vault history, and finish sensitive documents locally by default."),
        ]

        for emoji, title, description in features:
            feat_widget = self._create_step_widget(emoji, title, description)
            layout.addWidget(feat_widget)

        # Separator
        separator_why = QFrame()
        separator_why.setFrameShape(QFrame.Shape.HLine)
        separator_why.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator_why)

        # Quick start guide
        guide_label = QLabel("<b>Quick Start Guide:</b>")
        guide_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(guide_label)

        steps = (
            [
            ("1.", "Open a signed document", "Click 'Open & Upload Image' to load a scan, form, contract, or other document containing the signature you need"),
            ("2.", "Select signature", "Draw a rectangle around your signature in the source view"),
            ("3.", "Adjust settings", "Fine-tune the threshold and color removal to isolate your signature"),
            ("4.", "Run", "Use the manual flow first: place and verify output before automating."),
            ]
            if self._show_strategic_upgrade
            else [
                ("1.", "Open a template and sample packet", "Open a signed doc, define reusable roles, then save a placement recipe."),
                ("2.", "Map signature spaces", "Assign each role to a vault asset with position and page placement."),
                ("3.", "Define folders", "Set unsigned input, signed output, and optional review queue folders."),
                ("4.", "Authorize runners", "Create a grant so approved operators can execute recurring recipes."),
            ]
        )

        for emoji, title, description in steps:
            step_widget = self._create_step_widget(emoji, title, description)
            layout.addWidget(step_widget)

        # Backend health check section
        health_section = QHBoxLayout()
        health_section.setSpacing(12)

        self.health_status_label = QLabel("Checking backend...")
        self.health_status_label.setStyleSheet("font-size: 13px; color: gray;")
        health_section.addWidget(self.health_status_label)

        health_section.addStretch()

        self.check_health_btn = _create_button("Check Connection", self)
        self.check_health_btn.clicked.connect(self._check_backend_health)
        health_section.addWidget(self.check_health_btn)

        layout.addLayout(health_section)

        # License section
        license_section = QVBoxLayout()
        license_section.setSpacing(8)

        license_label = QLabel("<b>License & Activation:</b>")
        license_label.setStyleSheet("font-size: 14px;")
        license_section.addWidget(license_label)

        usage_copy = (
            "Build trusted repeatable flows around folders + templates. "
            "Define signature spaces once, then process packets from input folders to signed outputs."
        )
        license_info = QLabel(usage_copy)
        license_info.setStyleSheet("font-size: 12px; color: gray; margin-left: 16px;")
        license_info.setWordWrap(True)
        license_info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        license_section.addWidget(license_info)

        self._add_plan_persona_cards(license_section)

        if self._show_strategic_upgrade:
            self._add_plan_tiles(license_section)
        else:
            premium_mode_badge = QLabel(
                "Premium profile active — your app already includes recurring workflow access."
            )
            premium_mode_badge.setStyleSheet("font-size: 12px; color: #5f6368; margin-left: 16px;")
            premium_mode_badge.setWordWrap(True)
            license_section.addWidget(premium_mode_badge)

            _plan_cta_layout = QHBoxLayout()
            _plan_cta_layout.setContentsMargins(16, 4, 0, 0)
            buy_license_btn = _create_button(
                "Open Billing Portal",
                self,
            )
            buy_license_btn.clicked.connect(self._open_purchase_page)
            _plan_cta_layout.addWidget(buy_license_btn)
            _plan_cta_layout.addStretch()
            license_section.addLayout(_plan_cta_layout)

        # License actions (shared across both modes)
        license_btn_layout = QHBoxLayout()
        license_btn_layout.setContentsMargins(16, 4, 0, 0)

        enter_license_btn = _create_button("Enter License", self, primary=True, color='green')
        enter_license_btn.clicked.connect(self._open_license_dialog)
        license_btn_layout.addWidget(enter_license_btn)

        license_btn_layout.addStretch()
        license_section.addLayout(license_btn_layout)

        layout.addLayout(license_section)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)

        # Help links section
        links_section = QHBoxLayout()
        links_section.setSpacing(16)

        help_btn = _create_button("Help & Troubleshooting", self)
        help_btn.clicked.connect(lambda: self._open_document("docs/HELP.md"))
        links_section.addWidget(help_btn)

        shortcuts_btn = _create_button("Keyboard Shortcuts", self)
        shortcuts_btn.clicked.connect(lambda: self._open_document("docs/SHORTCUTS.md"))
        links_section.addWidget(shortcuts_btn)

        layout.addLayout(links_section)

        # Bottom section
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)

        self.dont_show_cb = QCheckBox("Don't show this again")
        bottom_layout.addWidget(self.dont_show_cb)

        bottom_layout.addStretch()

        get_started_btn = _create_button("Get Started", self, primary=True)
        get_started_btn.setDefault(True)
        get_started_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(get_started_btn)

        layout.addLayout(bottom_layout)

        # Store backend check function reference
        self._backend_check_fn = None

    def _add_plan_tiles(self, parent_layout: QVBoxLayout) -> None:
        plans = get_pricing_plans()
        plan_rows = QHBoxLayout()
        for index, plan in enumerate(plans):
            if index > 0:
                spacer = QWidget()
                spacer.setFixedWidth(8)
                plan_rows.addWidget(spacer)
            plan_tile = self._build_plan_tile(plan)
            plan_rows.addWidget(plan_tile)
        parent_layout.addLayout(plan_rows)

    def _add_plan_persona_cards(self, parent_layout: QVBoxLayout) -> None:
        use_case_title = QLabel("<b>Who this is for</b>")
        use_case_title.setStyleSheet("font-size: 14px; margin-top: 12px;")
        parent_layout.addWidget(use_case_title)

        use_case_cards = QHBoxLayout()
        for i, plan in enumerate(get_pricing_plans()[:3]):
            if i > 0:
                spacer = QWidget()
                spacer.setFixedWidth(8)
                use_case_cards.addWidget(spacer)
            plan_summary = plan.use_cases[0] if plan.use_cases else plan.persona_summary or plan.user_profile
            use_case_cards.addWidget(self._build_use_case_tile(plan.name, plan.subtitle, plan_summary))
        parent_layout.addLayout(use_case_cards)

    def _build_use_case_tile(self, title: str, role: str, detail: str) -> QWidget:
        tile = QWidget()
        layout = QVBoxLayout(tile)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 8, 12, 8)

        heading = QLabel(f"<b>{title}</b>")
        heading.setStyleSheet("font-size: 12px;")
        heading.setWordWrap(True)
        layout.addWidget(heading)

        role_label = QLabel(role)
        role_label.setStyleSheet("font-size: 10px; font-weight: 600; color: #5f6368;")
        role_label.setWordWrap(True)
        layout.addWidget(role_label)

        body = QLabel(detail)
        body.setStyleSheet("font-size: 10px; color: #444;")
        body.setWordWrap(True)
        layout.addWidget(body)
        return tile

    def _build_plan_tile(self, plan: PricingPlan) -> QWidget:
        tile = QWidget()
        layout = QVBoxLayout(tile)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 10, 12, 10)

        header = QLabel(
            f"<b>{plan.name}</b> · {plan.user_profile}"  # concise persona anchor
        )
        header.setWordWrap(True)
        header.setStyleSheet("font-size: 13px; color: #1e1e1e;")
        layout.addWidget(header)

        badge_text = plan.badge if plan.recommended else "Balanced"
        badge = QLabel(badge_text)
        badge.setStyleSheet("font-size: 10px; color: #5f6368;")
        layout.addWidget(badge)

        subtitle = QLabel(plan.headline)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("font-size: 12px; margin-bottom: 4px;")
        layout.addWidget(subtitle)

        persona = QLabel(f"Who it is for: {plan.user_profile}")
        persona.setStyleSheet("font-size: 10px; color: #5f6368; margin-bottom: 6px;")
        persona.setWordWrap(True)
        layout.addWidget(persona)

        price = QLabel(plan.annual_price_note or plan.monthly_price_note)
        price.setStyleSheet("font-size: 11px; color: #666;")
        layout.addWidget(price)

        feature_intro = QLabel("Features")
        feature_intro.setStyleSheet("font-size: 10px; font-weight: 600; margin-top: 4px;")
        layout.addWidget(feature_intro)
        for feature in plan.features:
            row = QLabel(f"• {feature}")
            row.setStyleSheet("font-size: 10px; margin-left: 8px; color: #444;")
            row.setWordWrap(True)
            layout.addWidget(row)

        if plan.use_cases:
            summary = QLabel("Workflow examples:")
            summary.setStyleSheet("font-size: 10px; font-weight: 600; margin-top: 4px;")
            layout.addWidget(summary)
            for case_line in plan.use_cases:
                case_row = QLabel(f"• {case_line}")
                case_row.setStyleSheet("font-size: 10px; margin-left: 8px; color: #444;")
                case_row.setWordWrap(True)
                layout.addWidget(case_row)

        action_layout = QHBoxLayout()
        action_layout.addStretch()
        cta = "Choose Plan"
        if plan.plan_id == self._default_plan_id:
            cta = "Buy Recommended"
        button = _create_button(cta, tile, primary=plan.plan_id == self._default_plan_id, color='blue')
        button.clicked.connect(lambda checked=False, plan_id=plan.plan_id: self._open_purchase_page(plan_id))
        action_layout.addWidget(button)
        layout.addLayout(action_layout)
        return tile

    def _create_step_widget(self, icon_type: str, title: str, description: str) -> QWidget:
        """Create a styled step widget for the quick start guide.
        
        Args:
            icon_type: Icon identifier (e.g., 'info', 'ok', 'apply') or step number (e.g., '1.')
            title: Step title
            description: Step description
        """
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(12)

        # Icon or step number
        icon_label = QLabel()
        icon_label.setFixedWidth(40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Check if it's a step number (contains a digit) or an icon type
        if any(char.isdigit() for char in icon_type):
            # It's a step number - display as text
            icon_label.setText(icon_type)
            icon_label.setStyleSheet("font-size: 20px; font-weight: 600;")
        else:
            # It's an icon type - use QIcon
            icon = get_icon(icon_type)
            if not icon.isNull():
                pixmap = icon.pixmap(24, 24)
                icon_label.setPixmap(pixmap)
            else:
                # Fallback to text if icon not available
                icon_label.setText(icon_type)
                icon_label.setStyleSheet("font-size: 20px;")
        
        container_layout.addWidget(icon_label)

        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_label = QLabel(f"<b>{title}</b>")
        title_label.setStyleSheet("font-size: 13px;")
        text_layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 12px; color: gray;")
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)

        container_layout.addLayout(text_layout)

        return container

    def _apply_theme(self) -> None:
        """Apply theme-aware styling for light/dark mode."""
        if sys.platform != "darwin":
            return

        palette = self.palette()
        base_color = palette.color(QPalette.ColorGroup.Normal, QPalette.ColorRole.Window)
        is_dark_mode = base_color.lightness() < 120

        if is_dark_mode:
            self.setStyleSheet(
                "QDialog { background-color: rgba(28, 28, 32, 255); }"
                "QLabel { color: rgba(255, 255, 255, 220); }"
                "QPushButton { "
                "  background-color: rgba(60, 60, 67, 200); "
                "  color: white; "
                "  border: 1px solid rgba(255, 255, 255, 30); "
                "  border-radius: 6px; "
                "  padding: 6px 12px; "
                "}"
                "QPushButton:hover { background-color: rgba(80, 80, 90, 220); }"
            )
        else:
            self.setStyleSheet(
                "QDialog { background-color: rgba(251, 251, 253, 255); }"
                "QLabel { color: rgba(0, 0, 0, 220); }"
                "QPushButton { "
                "  background-color: rgba(235, 235, 240, 200); "
                "  color: black; "
                "  border: 1px solid rgba(0, 0, 0, 30); "
                "  border-radius: 6px; "
                "  padding: 6px 12px; "
                "}"
                "QPushButton:hover { background-color: rgba(220, 220, 225, 220); }"
            )

    def set_backend_check_function(self, check_fn) -> None:
        """Set the function to call for backend health checking."""
        self._backend_check_fn = check_fn

    def _check_backend_health(self) -> None:
        """Trigger backend health check if function is set."""
        if self._backend_check_fn:
            self.health_status_label.setText("Checking...")
            self._backend_check_fn(self._on_health_check_result)

    def _on_health_check_result(self, online: bool, message: str) -> None:
        """Handle backend health check result."""
        if online:
            self.health_status_label.setText("Backend is online and ready")
            self.health_status_label.setStyleSheet("font-size: 13px; color: #2e7d32;")
        else:
            self.health_status_label.setText(f"Backend offline: {message}")
            self.health_status_label.setStyleSheet("font-size: 13px; color: #c62828;")

    def _open_license_dialog(self) -> None:
        """Open the license entry dialog in parent window."""
        parent_window = self.parent()
        if parent_window and hasattr(parent_window, "on_enter_license"):
            parent_window.on_enter_license()
        else:
            from desktop_app.views.license_dialog import LicenseDialog
            dialog = LicenseDialog(self)
            if dialog.exec():
                self.health_status_label.setText("License activated successfully")
                self.health_status_label.setStyleSheet("font-size: 13px; color: #2e7d32;")

    def _open_purchase_page(self, plan_id: str | None = None) -> None:
        """Open a plan-specific checkout page in the browser."""
        target_plan = self._default_plan_id if plan_id is None else plan_id
        QDesktopServices.openUrl(QUrl(get_purchase_url(target_plan)))

    def _open_document(self, doc_path: str) -> None:
        """Open documentation file (delegates to parent window if available)."""
        parent_window = self.parent()
        if parent_window and hasattr(parent_window, "_open_document"):
            parent_window._open_document(doc_path)
        else:
            # Fallback: try to open relative path
            from pathlib import Path
            path = Path(__file__).parents[2] / doc_path
            if path.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def should_show_again(self) -> bool:
        """Return whether the dialog should be shown again on next launch."""
        return not self.dont_show_cb.isChecked()


__all__ = ["OnboardingDialog"]
