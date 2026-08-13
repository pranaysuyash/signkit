from PySide6.QtCore import Qt
import json

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
import sys
from typing import Optional

from desktop_app.license.activation import ActivationError, activate_receipt
from desktop_app.license.entitlements import EntitlementReceipt
from desktop_app.widgets.modern_mac_button import ModernMacButton


def _create_button(
    text: str = "",
    parent: Optional[QDialog] = None,
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


class LicenseDialog(QDialog):
    """Install a provider-issued signed entitlement receipt."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter License")
        self.setModal(True)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Paste your signed activation receipt (JSON):"))
        self.key_edit = QLineEdit(self)
        self.key_edit.setPlaceholderText("Paste the receipt supplied after purchase")
        layout.addWidget(self.key_edit)

        btn_row = QHBoxLayout()
        self.cancel_btn = _create_button("Cancel", self)
        self.ok_btn = _create_button("Activate", self, primary=True)
        self.ok_btn.setDefault(True)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.ok_btn)
        layout.addLayout(btn_row)

        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self._on_activate)

        self.resize(420, 160)

    def _on_activate(self):
        raw_receipt = (self.key_edit.text() or "").strip()
        if not raw_receipt:
            self.key_edit.setFocus()
            return
        try:
            payload = json.loads(raw_receipt)
            receipt = EntitlementReceipt.from_dict(payload)
            activate_receipt(receipt)
        except (json.JSONDecodeError, ValueError, TypeError, ActivationError) as error:
            QMessageBox.warning(
                self,
                "Activation not verified",
                f"SignKit could not verify this activation receipt. {error}",
            )
            self.key_edit.setFocus()
            return
        self.accept()
