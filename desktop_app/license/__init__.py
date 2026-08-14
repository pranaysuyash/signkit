"""License management package for signature extractor application.

Notes:
    GUI-restricted helpers (in :mod:`restrictions`) are imported lazily so that
    headless or non-UI environments can still use core license APIs. This is
    especially important for bootstrap/runtime tests that don't load PySide.
"""

from __future__ import annotations

from .storage import (
    LicenseInfo,
    LicenseAddon,
    LicenseValidator,
    OperationType,
    TEST_LICENSE_EMAIL,
    is_licensed,
    load_license,
    save_license,
)
from .activation import ActivationError, ActivationResult, activate_receipt, reconcile_receipt

from .validator import (
    check_export_license,
    check_pdf_operations_license,
    get_license_status_info,
    get_operation_restriction_info,
)


def _import_restrictions():
    """Import GUI restriction helpers lazily and return a module tuple."""

    try:
        from .restrictions import (
            check_and_enforce_export_license,
            check_and_enforce_pdf_operations_license,
            check_and_enforce_workflow_automation_license,
            get_restriction_reason,
            is_export_allowed,
            is_pdf_operations_allowed,
            is_workflow_automation_allowed,
        )

        return (
            check_and_enforce_export_license,
            check_and_enforce_pdf_operations_license,
            check_and_enforce_workflow_automation_license,
            is_export_allowed,
            is_pdf_operations_allowed,
            is_workflow_automation_allowed,
            get_restriction_reason,
        )
    except Exception:
        # Fall back to headless-safe no-op behavior when GUI toolkits are unavailable.
        def _check_and_enforce_export_license(*_args, **_kwargs) -> bool:
            return LicenseValidator.is_operation_allowed(OperationType.EXPORT)[0]

        def _check_and_enforce_pdf_operations_license(*_args, **_kwargs) -> bool:
            return LicenseValidator.is_operation_allowed(OperationType.PDF_OPERATIONS)[0]

        def _check_and_enforce_workflow_automation_license(*_args, **_kwargs) -> bool:
            return LicenseValidator.is_operation_allowed(OperationType.WORKFLOW_AUTOMATION)[0]

        def _quick_operation_allowed(_operation: OperationType) -> bool:
            return LicenseValidator.is_operation_allowed(_operation)[0]

        def _restriction_reason(operation: OperationType) -> str:
            allowed, reason = LicenseValidator.is_operation_allowed(operation)
            return "" if allowed else reason

        return (
            _check_and_enforce_export_license,
            _check_and_enforce_pdf_operations_license,
            _check_and_enforce_workflow_automation_license,
            _quick_operation_allowed,
            _quick_operation_allowed,
            _quick_operation_allowed,
            _restriction_reason,
        )


check_and_enforce_export_license, check_and_enforce_pdf_operations_license, check_and_enforce_workflow_automation_license, is_export_allowed, is_pdf_operations_allowed, is_workflow_automation_allowed, get_restriction_reason = (
    _import_restrictions()
)

__all__ = [
    # Core license storage
    'LicenseInfo',
    'LicenseAddon',
    'LicenseValidator',
    'OperationType',
    'TEST_LICENSE_EMAIL',
    'load_license',
    'save_license',
    'is_licensed',
    'ActivationError',
    'ActivationResult',
    'activate_receipt',
    'reconcile_receipt',
    
    # Validation helpers
    'check_export_license',
    'check_pdf_operations_license',
    'get_operation_restriction_info',
    'get_license_status_info',
    
    # Restriction enforcement
    'check_and_enforce_export_license',
    'check_and_enforce_pdf_operations_license',
    'check_and_enforce_workflow_automation_license',
    'is_export_allowed',
    'is_pdf_operations_allowed',
    'is_workflow_automation_allowed',
    'get_restriction_reason'
]
