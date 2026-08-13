import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Iterable, Optional, Tuple

from desktop_app.license.entitlements import EntitlementReceipt


APP_DIR_NAME = ".signature_extractor"
LICENSE_FILE = "license.json"

# Test license configuration
TEST_LICENSE_EMAIL = "pranay@example.com"


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


def _plan_from_key(key: str) -> LicenseTier:
    """Infer a legacy tier from key shape."""

    if not key:
        return LicenseTier.TRIAL

    normalized = key.strip().lower()
    if normalized in {"starter", "team", "business"}:
        return LicenseTier(normalized)

    for tier in (LicenseTier.BUSINESS, LicenseTier.TEAM, LicenseTier.STARTER):
        prefix = f"{tier.value}:"
        if normalized.startswith(prefix):
            return tier

    if LicenseValidator.is_test_license(key):
        return LicenseTier.BUSINESS

    # Existing behavior: valid legacy keys were treated as licensed, so keep that path
    return LicenseTier.TEAM if len(key) >= 6 else LicenseTier.TRIAL


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
        """Check if license is currently valid."""
        if not self.key:
            return False
        if self.entitlement is not None:
            return self.entitlement.is_usable()
        if self.is_test_license:
            return True
        # Keep legacy behavior: minimum key length grants a working license
        return len(self.key) >= 6

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
        is_test_license = data.get("is_test_license", False)
        tier_value = data.get("tier")
        add_on_values = data.get("add_ons")
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
            # Check if this is the test license
            if key == TEST_LICENSE_EMAIL or email == TEST_LICENSE_EMAIL:
                is_test_license = True
            
            return LicenseInfo(
                key=key, 
                email=email, 
                is_test_license=is_test_license,
                tier=_normalize_tier(tier_value) if tier_value else _plan_from_key(key),
                add_ons=_normalize_add_ons(add_on_values),
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
    """Persist license info to disk."""
    key = key.strip()
    is_test_license = key == TEST_LICENSE_EMAIL or email == TEST_LICENSE_EMAIL
    license_tier = LicenseTier.BUSINESS if is_test_license else _normalize_tier(tier)
    if license_tier == LicenseTier.TRIAL:
        license_tier = _plan_from_key(key)
    normalized_add_ons = _normalize_add_ons(add_ons)
    
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
    
    with open(_license_path(), "w", encoding="utf-8") as f:
        json.dump(data, f)


def is_licensed() -> bool:
    """Very lightweight local check for MVP: consider any non-empty key as licensed.

    Later, integrate an online verification or signature check if desired.
    """
    info = load_license()
    return bool(info and info.is_valid())


class LicenseValidator:
    """Enhanced license validation with test license support."""
    
    @staticmethod
    def is_test_license(license_key: str) -> bool:
        """Check if license key is the test license."""
        return license_key.strip() == TEST_LICENSE_EMAIL
    
    @staticmethod
    def validate_license_key(key: str) -> bool:
        """Validate license key including test license."""
        key = key.strip()
        if not key:
            return False
        
        # Test license is always valid
        if LicenseValidator.is_test_license(key):
            return True
        
        # Regular license validation (minimum length requirement)
        return len(key) >= 6
    
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
        
        if license_info.is_test_license:
            return True, f"Test License Active ({license_info.key})", True
        
        if license_info.is_valid():
            email_part = f" ({license_info.email})" if license_info.email else ""
            return True, f"Licensed {license_info.tier.value}{email_part}", False
        
        return False, "Invalid License", False

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
