"""
License restriction helpers for UI components.
This module provides functions that check licenses and show restriction dialogs.
"""

from typing import Optional
from PySide6.QtWidgets import QWidget

from .storage import OperationType, LicenseValidator
# Import will be done at runtime to avoid circular imports
# from ..views.license_restriction_dialog import show_restriction_dialog


def check_and_enforce_export_license(parent: Optional[QWidget] = None) -> bool:
    """
    Check license before export operations and show restriction dialog if needed.
    
    Args:
        parent: Parent widget for the restriction dialog
        
    Returns:
        True if operation should proceed, False if blocked
    """
    allowed, reason = LicenseValidator.is_operation_allowed(OperationType.EXPORT)
    
    if allowed:
        return True
    
    # Import at runtime to avoid circular imports
    from desktop_app.views.license_restriction_dialog import show_restriction_dialog
    
    # Show restriction dialog and return whether license was activated
    return show_restriction_dialog(
        OperationType.EXPORT,
        parent=parent,
        default_plan_id=_resolve_plan_from_parent(parent),
    )


def check_and_enforce_pdf_operations_license(parent: Optional[QWidget] = None) -> bool:
    """
    Check license before PDF paste/save operations and show restriction dialog if needed.
    
    Args:
        parent: Parent widget for the restriction dialog
        
    Returns:
        True if operation should proceed, False if blocked
    """
    allowed, reason = LicenseValidator.is_operation_allowed(OperationType.PDF_OPERATIONS)
    
    if allowed:
        return True
    
    # Import at runtime to avoid circular imports
    from desktop_app.views.license_restriction_dialog import show_restriction_dialog
    
    # Show restriction dialog and return whether license was activated
    return show_restriction_dialog(
        OperationType.PDF_OPERATIONS,
        parent=parent,
        default_plan_id=_resolve_plan_from_parent(parent),
    )


def check_and_enforce_workflow_automation_license(parent: Optional[QWidget] = None) -> bool:
    """Gate automated packet execution while preserving read-only and safety actions."""

    allowed, _ = LicenseValidator.is_operation_allowed(OperationType.WORKFLOW_AUTOMATION)
    if allowed:
        return True

    from desktop_app.views.license_restriction_dialog import show_restriction_dialog

    return show_restriction_dialog(
        OperationType.WORKFLOW_AUTOMATION,
        parent=parent,
        default_plan_id="workflow_automation",
        use_parent_default_plan=False,
    )


def _resolve_plan_from_parent(parent: Optional[QWidget]) -> str | None:
    """Best-effort extraction of default purchase plan from a parent window."""

    if parent is not None and hasattr(parent, "get_default_purchase_plan_id"):
        getter = getattr(parent, "get_default_purchase_plan_id")
        if callable(getter):
            try:
                return getter()
            except Exception:
                return None
    return None


def is_export_allowed() -> bool:
    """
    Quick check if export operations are allowed (without showing dialogs).
    
    Returns:
        True if export is allowed, False if blocked
    """
    allowed, _ = LicenseValidator.is_operation_allowed(OperationType.EXPORT)
    return allowed


def is_pdf_operations_allowed() -> bool:
    """
    Quick check if PDF operations are allowed (without showing dialogs).
    
    Returns:
        True if PDF operations are allowed, False if blocked
    """
    allowed, _ = LicenseValidator.is_operation_allowed(OperationType.PDF_OPERATIONS)
    return allowed


def is_workflow_automation_allowed() -> bool:
    """Return whether local packet automation is enabled without opening UI."""

    allowed, _ = LicenseValidator.is_operation_allowed(OperationType.WORKFLOW_AUTOMATION)
    return allowed


def get_restriction_reason(operation_type: OperationType) -> str:
    """
    Get the reason why an operation is restricted.
    
    Args:
        operation_type: The type of operation to check
        
    Returns:
        Human-readable reason for restriction, or empty string if allowed
    """
    allowed, reason = LicenseValidator.is_operation_allowed(operation_type)
    return "" if allowed else reason
