"""
License restriction dialog shown when operations are blocked due to licensing.
"""

import sys
import webbrowser
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QStyle
)

from desktop_app.license.storage import OperationType
from desktop_app.config import get_purchase_url
from desktop_app.views.license_dialog import LicenseDialog
from desktop_app.widgets.modern_mac_button import ModernMacButton


# Restriction messages
RESTRICTION_MESSAGES = {
    OperationType.EXPORT: {
        "title": "Export Requires License",
        "message": "Export functionality requires a license. You can still preview and process signatures in trial mode.",
        "details": "Export your processed signatures to PNG, JPG, or other formats."
    },
    OperationType.PDF_OPERATIONS: {
        "title": "PDF Operations Require License", 
        "message": "PDF signing and saving requires a license. You can still view PDFs and preview signature placement in trial mode.",
        "details": "Paste signatures to PDFs and save signed documents."
    }
}


def _create_button(
    text: str = "",
    parent: Optional[QDialog] = None,
    *,
    use_modern_mac: Optional[bool] = None,
    primary: bool = False,
    color: str = 'blue',
    compact: bool = False
) -> QPushButton:
    """Create a button, using ModernMacButton on macOS if available and requested."""
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
            # Fallback if ModernMacButton not available
            pass

    # Default to standard QPushButton
    return QPushButton(text, parent)


class LicenseRestrictionDialog(QDialog):
    """Dialog shown when operations are restricted due to licensing."""
    
    def __init__(self, operation_type: OperationType, parent=None):
        """
        Args:
            operation_type: The type of operation that was restricted
            parent: Parent widget
        """
        super().__init__(parent)
        self.operation_type = operation_type
        self.license_activated = False
        
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Setup dialog UI with clear messaging and action buttons."""
        # Get messages for this operation type
        messages = RESTRICTION_MESSAGES.get(
            self.operation_type, 
            RESTRICTION_MESSAGES[OperationType.EXPORT]
        )
        
        self.setWindowTitle(messages["title"])
        self.setModal(True)
        self.resize(480, 280)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Icon and title
        title_layout = QHBoxLayout()
        title_layout.setSpacing(12)
        
        # Use a warning icon (you could add an actual icon here)
        # Use standard warning icon
        icon_label = QLabel()
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        icon_label.setPixmap(icon.pixmap(48, 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(icon_label)
        
        title_text = QVBoxLayout()
        title_label = QLabel(messages["title"])
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        title_text.addWidget(title_label)
        
        subtitle_label = QLabel("Trial Mode Active")
        subtitle_label.setStyleSheet("font-size: 12px; color: #666; margin-top: 2px;")
        title_text.addWidget(subtitle_label)
        
        title_layout.addLayout(title_text)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Main message
        message_label = QLabel(messages["message"])
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 14px; color: #444; line-height: 1.4;")
        layout.addWidget(message_label)
        
        # Feature details
        details_label = QLabel(f"This feature allows you to: {messages['details']}")
        details_label.setWordWrap(True)
        details_label.setStyleSheet("font-size: 12px; color: #666; margin-top: 8px;")
        layout.addWidget(details_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #ddd;")
        layout.addWidget(separator)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Cancel button
        self.cancel_btn = _create_button("Continue in Trial Mode", self)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        
        # Buy license button
        self.buy_btn = _create_button("Buy License", self, color='green')
        self.buy_btn.clicked.connect(self.on_buy_license)
        button_layout.addWidget(self.buy_btn)
        
        # Enter license button (primary action)
        self.enter_license_btn = _create_button("Enter License Key", self, primary=True)
        self.enter_license_btn.setDefault(True)
        self.enter_license_btn.clicked.connect(self.on_enter_license)
        button_layout.addWidget(self.enter_license_btn)
        
        layout.addLayout(button_layout)
        
        # Focus on the primary action
        self.enter_license_btn.setFocus()
    
    def on_enter_license(self) -> None:
        """Open license entry dialog."""
        license_dialog = LicenseDialog(self)
        if license_dialog.exec():
            # License was successfully entered
            self.license_activated = True
            self.accept()
    
    def on_buy_license(self) -> None:
        """Open purchase URL in browser."""
        try:
            webbrowser.open(get_purchase_url())
        except Exception:
            # If browser opening fails, just continue
            pass
        
        # Keep dialog open so user can enter license after purchase
        # Don't close the dialog automatically
    
    def was_license_activated(self) -> bool:
        """
        Check if a license was successfully activated during this dialog session.
        
        Returns:
            True if license was activated, False otherwise
        """
        return self.license_activated


def show_restriction_dialog(operation_type: OperationType, parent=None) -> bool:
    """
    Show restriction dialog for the given operation type.
    
    Args:
        operation_type: The type of operation that was restricted
        parent: Parent widget
        
    Returns:
        True if user activated a license and operation should be retried,
        False if operation should remain blocked
    """
    dialog = LicenseRestrictionDialog(operation_type, parent)
    result = dialog.exec()
    
    # Return True only if dialog was accepted AND license was activated
    return result == QDialog.DialogCode.Accepted and dialog.was_license_activated()
