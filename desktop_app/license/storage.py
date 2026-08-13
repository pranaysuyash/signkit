import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Iterable, Optional, Tuple

from desktop_app.license.entitlements import EntitlementReceipt
from desktop_app.license.verification import load_public_keys


APP_DIR_NAME = ".signature_extractor"
LICENSE_FILE = "license.json"

# Compatibility label only. It is accepted solely when explicit test mode is
# enabled in a development/test process; it is never production entitlement
# evidence.
TEST_LICENSE_EMAIL = "pranay@example.com"
TEST_LICENSE_MODE_ENV = "SIGNKIT_LICENSE_TEST_MODE"


class LicenseTier(Enum):
    """License pricing/entitlement tiers."""

    TRIAL = "trial"
    STARTER = "starter"
    TEAM = "team"
    BUSINESS = "business"


class LicenseFeature(Enum):
    """Feature-gating keys used by the licensing model."""

    EXPORT = "export"
    PDF_OPERATIONS = "pdf_operations"
    WORKFLOW_AUTOMATION = "workflow_automation"


class LicenseAddon(Enum):
    """Independently purchasable capability grants layered on a base license."""

    WORKFLOW_AUTOMATION = "workflow_automation"


_TIER_ORDER = {
    LicenseTier.TRIAL: 0,
    LicenseTier.STARTER: 1,
    LicenseTier.TEAM: 2,
    LicenseTier.BUSINESS: 3,
}


_TIER_FEATURES = {
    LicenseTier.TRIAL: {
        # intentionally empty: trial mode allows no locked paid features
    },
    LicenseTier.STARTER: {
        LicenseFeature.EXPORT,
        LicenseFeature.PDF_OPERATIONS,
    },
    LicenseTier.TEAM: {
        LicenseFeature.EXPORT,
        LicenseFeature.PDF_OPERATIONS,
        LicenseFeature.WORKFLOW_AUTOMATION,
    },
    LicenseTier.BUSINESS: {
        LicenseFeature.EXPORT,
        LicenseFeature.PDF_OPERATIONS,
        LicenseFeature.WORKFLOW_AUTOMATION,
    },
}


_ADDON_FEATURES = {
    LicenseAddon.WORKFLOW_AUTOMATION: {
        LicenseFeature.WORKFLOW_AUTOMATION,
    },
}


def _normalize_tier(tier_value: Optional[str]) -> LicenseTier:
    """Normalize an arbitrary tier value to a safe tier."""

    if not tier_value:
        return LicenseTier.TRIAL

    try:
        return LicenseTier(str(tier_value).strip().lower())
    except ValueError:
        return LicenseTier.TRIAL


def _normalize_add_ons(add_on_values: Optional[Iterable[LicenseAddon | str]]) -> set[LicenseAddon]:
    """Normalize persisted or issuer-provided add-on identifiers safely."""

    if not add_on_values:
        return set()

    values: Iterable[LicenseAddon | str]
    if isinstance(add_on_values, (str, LicenseAddon)):
        values = [add_on_values]
    else:
        values = add_on_values

    normalized: set[LicenseAddon] = set()
    for value in values:
        candidate = value.value if isinstance(value, LicenseAddon) else str(value)
        try:
            normalized.add(LicenseAddon(candidate.strip().lower()))
        except ValueError:
            continue
    return normalized


def _test_mode_enabled() -> bool:
    """Require an explicit opt-in before accepting the development test key."""

    if getattr(sys, "frozen", False):
        return False
    return os.getenv(TEST_LICENSE_MODE_ENV, "").strip().lower() in {"1", "true", "yes"}


OperationType = LicenseFeature


def _config_dir() -> str:
    """Return the per-user config directory (e.g., ~/.signature_extractor)."""
    home = os.path.expanduser("~")
    path = os.path.join(home, APP_DIR_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def _license_path() -> str:
    return os.path.join(_config_dir(), LICENSE_FILE)


@dataclass
class LicenseInfo:
    key: str
    email: Optional[str] = None
    is_test_license: bool = False
    tier: LicenseTier = LicenseTier.TRIAL
    add_ons: set[LicenseAddon] = field(default_factory=set)
    validated_at: Optional[datetime] = None
    entitlement: Optional[EntitlementReceipt] = None

    @property
    def features(self) -> set[LicenseFeature]:
        """Return enabled feature set for this license."""

        features = set(_TIER_FEATURES.get(self.tier, _TIER_FEATURES[LicenseTier.TRIAL]))
        for add_on in self.add_ons:
            features.update(_ADDON_FEATURES.get(add_on, set()))
        return features

    def is_valid(self) -> bool:
        """Check whether trusted entitlement evidence currently grants access."""

        if not self.key:
            return False
        if self.entitlement is not None:
            public_keys = load_public_keys()
            public_key = public_keys.get(self.entitlement.key_id or "")
            return self.entitlement.is_usable(public_key=public_key)
        return self.is_test_license and _test_mode_enabled()

    def has_feature(self, feature: LicenseFeature) -> bool:
        """Return whether the feature is enabled under this license tier."""

        return feature in self.features

    def has_add_on(self, add_on: LicenseAddon) -> bool:
        """Return whether the license contains a named modular capability grant."""

        return add_on in self.add_ons


def load_license() -> Optional[LicenseInfo]:
    """Load license info from disk, if present."""
    path = _license_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        key = data.get("key", "").strip()
        email = data.get("email")
        is_test_license = bool(data.get("is_test_license", False))
        entitlement_data = data.get("entitlement")
        entitlement = None
        if entitlement_data is not None:
            entitlement = EntitlementReceipt.from_dict(entitlement_data)
        validated_at_str = data.get("validated_at")
        validated_at = None
        if validated_at_str:
            try:
                validated_at = datetime.fromisoformat(validated_at_str)
            except ValueError:
                pass
        
        if key:
            is_test_license = is_test_license and _test_mode_enabled()
            if entitlement is not None:
                persisted_tier = _normalize_tier(entitlement.plan_id)
                persisted_add_ons = _normalize_add_ons(entitlement.add_ons)
            else:
                persisted_tier = LicenseTier.BUSINESS if is_test_license else LicenseTier.TRIAL
                persisted_add_ons = set()

            return LicenseInfo(
                key=key, 
                email=email, 
                is_test_license=is_test_license,
                tier=persisted_tier,
                add_ons=persisted_add_ons,
                validated_at=validated_at,
                entitlement=entitlement,
            )
    except Exception:
        # Ignore malformed file
        return None
    return None


def save_license(
    key: str,
    email: Optional[str] = None,
    tier: Optional[str] = None,
    add_ons: Optional[Iterable[LicenseAddon | str]] = None,
    entitlement: Optional[EntitlementReceipt] = None,
) -> None:
    """Persist raw activation input or a normalized entitlement receipt.

    A key-only record is retained for support/migration visibility but cannot
    grant paid access. Production activation must use ``activate_receipt``.
    """

    key = key.strip()
    is_test_license = _test_mode_enabled() and (
        key == TEST_LICENSE_EMAIL or email == TEST_LICENSE_EMAIL
    )
    if entitlement is not None:
        license_tier = _normalize_tier(entitlement.plan_id)
        normalized_add_ons = _normalize_add_ons(entitlement.add_ons)
    elif is_test_license:
        license_tier = LicenseTier.BUSINESS
        normalized_add_ons = _normalize_add_ons(add_ons)
    else:
        license_tier = LicenseTier.TRIAL
        normalized_add_ons = set()
    
    data = {
        "key": key,
        "is_test_license": is_test_license,
        "tier": license_tier.value,
        "add_ons": sorted(add_on.value for add_on in normalized_add_ons),
        "validated_at": datetime.now().isoformat()
    }
    if email:
        data["email"] = email.strip()
    if entitlement is not None:
        data["entitlement"] = entitlement.to_dict()
    
    path = _license_path()
    directory = os.path.dirname(path) or "."
    fd, temporary_path = tempfile.mkstemp(prefix=".license-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        try:
            os.chmod(temporary_path, 0o600)
        except OSError:
            pass
        os.replace(temporary_path, path)
    finally:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass


def is_licensed() -> bool:
    """Return whether a signed receipt or explicit development test grant is active."""

    info = load_license()
    return bool(info and info.is_valid())


class LicenseValidator:
    """Feature validation over the one canonical local entitlement boundary."""
    
    @staticmethod
    def is_test_license(license_key: str) -> bool:
        """Check the test key only in explicit development/test mode."""
        return _test_mode_enabled() and license_key.strip() == TEST_LICENSE_EMAIL
    
    @staticmethod
    def validate_license_key(key: str) -> bool:
        """Validate only the explicit development key; receipts use activation."""
        return LicenseValidator.is_test_license(key)
    
    @staticmethod
    def is_operation_allowed(operation_type: OperationType) -> Tuple[bool, str]:
        """
        Check if operation is allowed under current license.
        
        Args:
            operation_type: The type of operation to check
            
        Returns:
            (allowed: bool, reason: str)
        """
        license_info = load_license()
        
        if not license_info:
            return False, "No license found. Application is in trial mode."
        
        if not license_info.is_valid():
            return False, "Invalid license. Please check your license key."

        feature = LicenseFeature(operation_type.value)
        if license_info.has_feature(feature):
            return True, "License valid"
        return False, f"License tier '{license_info.tier.value}' does not include '{operation_type.value}'."
    
    @staticmethod
    def get_license_status() -> Tuple[bool, str, bool]:
        """
        Get comprehensive license status.
        
        Returns:
            (is_licensed: bool, status_message: str, is_test: bool)
        """
        license_info = load_license()
        
        if not license_info:
            return False, "Trial Mode - No License", False
        
        if license_info.is_test_license and license_info.is_valid():
            return True, f"Test License Active ({license_info.key})", True

        if license_info.is_valid():
            email_part = f" ({license_info.email})" if license_info.email else ""
            return True, f"Licensed {license_info.tier.value}{email_part}", False

        if license_info.entitlement is not None:
            return False, "Activation is not verified on this device", False
        return False, "License is unverified; activate with a signed receipt", False

    @staticmethod
    def has_feature(feature: LicenseFeature) -> bool:
        """Check whether current stored license enables a feature."""
        license_info = load_license()
        return bool(license_info and license_info.is_valid() and license_info.has_feature(feature))

    @staticmethod
    def has_add_on(add_on: LicenseAddon) -> bool:
        """Check whether the current license contains a named add-on grant."""

        license_info = load_license()
        return bool(license_info and license_info.is_valid() and license_info.has_add_on(add_on))

    @staticmethod
    def can_use_workflow_automation() -> bool:
        """Dedicated helper for gating workflow automation features."""
        return LicenseValidator.has_feature(LicenseFeature.WORKFLOW_AUTOMATION)

# Export the new classes and enums for easy importing
__all__ = [
    'LicenseInfo',
    'LicenseValidator', 
    'OperationType',
    'EntitlementReceipt',
    'TEST_LICENSE_EMAIL',
    'load_license',
    'save_license',
    'is_licensed',
    'LicenseTier',
    'LicenseFeature',
    'LicenseAddon',
]
