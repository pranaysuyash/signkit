import os
import logging
from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Sequence

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover

    def load_dotenv(*_args, **_kwargs) -> None:  # type: ignore[override]
        """Graceful fallback when python-dotenv is unavailable."""
        return None

LOG = logging.getLogger(__name__)

# Single source of truth for the app version, used in the Help dialog and in
# forensic watermark metadata. Still a placeholder (no packaging/release
# process sets this yet) -- but a single placeholder that can't silently
# drift out of sync with itself, rather than the same literal duplicated
# independently in two files.
APP_VERSION = "1.0.0"

# External product destinations are deliberately content-free URLs. SignKit
# never appends document names, processing results, or local workflow metadata.
WORKFLOW_REVIEW_URL = (
    "https://pranaysuyash.com/contact"
    "?source=signkit&entry=desktop-app&intent=document-workflow"
)

DODO_CHECKOUT_BASE_URL = "https://checkout.dodopayments.com/buy/"
GUMROAD_FALLBACK_URL = "https://pranaysuyash.gumroad.com/l/signkit-v1"


@dataclass(frozen=True)
class PricingPlan:
    """Configuration contract for a purchasable SignKit plan."""

    plan_id: str
    name: str
    subtitle: str
    headline: str
    features: Sequence[str]
    user_profile: str
    monthly_price_note: str
    annual_price_note: str = ""
    recommended: bool = False
    use_cases: Sequence[str] = ()
    persona_summary: str = ""

    @property
    def badge(self) -> str:
        return "Most teams choose" if self.recommended else "Balanced"


@dataclass(frozen=True)
class PricingAddon:
    """A modular commercial offer that augments, rather than replaces, a base plan."""

    addon_id: str
    name: str
    headline: str
    features: Sequence[str]
    user_profile: str
    price_note: str


_PLANS = [
    PricingPlan(
        plan_id="starter",
        name="Starter",
        subtitle="Independent operators",
        headline="Manual workflow control with reusable signature placements",
        features=(
            "Template-based signature placement",
            "Unlimited local extraction",
            "Export signed PDFs with local audit trail",
            "Single-user execution with manual run",
        ),
        user_profile="Freelancers and solo operators",
        use_cases=(
            "Solo practitioners",
            "HR onboarding packets",
            "Simple recurring contract signing",
        ),
        persona_summary="Good for one-to-three operators who need repeatable local signing.",
        monthly_price_note="Starter $19/mo",
    ),
    PricingPlan(
        plan_id="team",
        name="Team",
        subtitle="Legal and operations teams",
        headline="Folder automation for recurring packets, with review queue + retry controls",
        features=(
            "Everything in Starter",
            "Multi-user grants and role-scoped execution",
            "Recurring folder workflow (input/output/review folders)",
            "Review lane + retry + quarantine",
        ),
        user_profile="Ops teams and legal/admin users",
        use_cases=(
            "Legal + finance teams",
            "Distributed teams with role-based access",
            "Teams enforcing signature quality reviews",
        ),
        persona_summary="Best fit for recurring packet ops with explicit approver and operator roles.",
        monthly_price_note="Team $59/mo",
        annual_price_note="Annual billed plans",
        recommended=True,
    ),
    PricingPlan(
        plan_id="business",
        name="Business",
        subtitle="High-volume teams and ops-heavy orgs",
        headline="Governance, incident trails, and high-volume signing",
        features=(
            "Everything in Team",
            "High-volume queue throughput",
            "Receipt pack export + execution lineage",
            "Policy templates, expiry controls, and incident trail",
        ),
        user_profile="Operations leaders and legal offices",
        use_cases=(
            "Operations and compliance teams",
            "Global legal/HR teams with policy constraints",
            "High-volume automated packet processing",
        ),
        persona_summary="Built for teams that need strict auditability and policy controls at scale.",
        monthly_price_note="Business $159/mo",
    ),
]


_ADDONS = [
    PricingAddon(
        addon_id="workflow_automation",
        name="Automated Packet Ops",
        headline="Run approved local signing recipes from monitored folders with operator review controls.",
        features=(
            "Folder scan and queueing for recurring packets",
            "Run selected or queued authorized jobs",
            "Retry-based execution with the existing review and quarantine controls",
        ),
        user_profile="Legal, HR, and operations teams with recurring local document packets",
        price_note="Commercial pilot add-on. Configure a dedicated checkout product before offering publicly.",
    ),
]


def get_pricing_plans() -> list[PricingPlan]:
    """Return the current public pricing plan matrix."""

    return list(_PLANS)


def get_pricing_plan(plan_id: str | None = None) -> PricingPlan:
    """Resolve one pricing plan by id and fall back to recommended."""

    normalized = (plan_id or "").strip().lower()
    for plan in _PLANS:
        if plan.plan_id == normalized:
            return plan
    for plan in _PLANS:
        if plan.recommended:
            return plan
    return _PLANS[0]


def get_pricing_addons() -> list[PricingAddon]:
    """Return independently purchasable capability modules."""

    return list(_ADDONS)


def get_pricing_addon(addon_id: str | None) -> PricingAddon | None:
    """Resolve an add-on by id without silently treating it as a base plan."""

    normalized = (addon_id or "").strip().lower()
    for addon in _ADDONS:
        if addon.addon_id == normalized:
            return addon
    return None


def get_pricing_offer_id(offer_id: str | None = None) -> str:
    """Resolve a known base plan or add-on to a checkout-safe offer id."""

    addon = get_pricing_addon(offer_id)
    if addon is not None:
        return addon.addon_id
    return get_pricing_plan(offer_id).plan_id


def _checkout_product_id_env_name(plan_id: str | None) -> str:
    if not plan_id:
        return "DODO_PRODUCT_ID"
    normalized = plan_id.strip().upper()
    return f"DODO_PRODUCT_ID_{normalized}"


def _checkout_fallback_env_name(plan_id: str | None) -> str:
    if not plan_id:
        return "GUMROAD_PRODUCT_URL"
    normalized = plan_id.strip().upper()
    return f"GUMROAD_PRODUCT_URL_{normalized}"


def _is_valid_dodo_product_id(product_id: str) -> bool:
    product_id = product_id.strip()
    return product_id.startswith("pdt_") and product_id[4:].isalnum()


def _checkout_url_for_env(plan_id: str | None) -> str:
    product_env_name = _checkout_product_id_env_name(plan_id)
    product_id = os.getenv(product_env_name, "").strip()
    if _is_valid_dodo_product_id(product_id):
        return f"{DODO_CHECKOUT_BASE_URL}{product_id}"

    fallback_env_name = _checkout_fallback_env_name(plan_id)
    explicit_fallback = os.getenv(fallback_env_name, "").strip()
    return explicit_fallback or os.getenv("GUMROAD_PRODUCT_URL", GUMROAD_FALLBACK_URL)


def get_purchase_url(plan_id: str | None = None) -> str:
    """Return checkout URL for the provided plan or the active default plan."""

    if plan_id is None:
        explicit = os.getenv("SIGNKIT_DEFAULT_PLAN", "").strip()
        if explicit:
            return _checkout_url_for_env(explicit)
        return _checkout_url_for_env(None)

    normalized = plan_id.strip().lower()
    if normalized == "default":
        return get_purchase_url()
    return _checkout_url_for_env(normalized)


@dataclass
class AppConfig:
    api_base_url: str
    allow_remote_document_upload: bool = False
    debug: bool = False
    log_level: str = "INFO"
    enable_analytics: bool = False
    updates_url: str = "https://cdn.signkit.work/updates.json"


def load_config() -> AppConfig:
    """Load and validate application configuration."""
    # Load .env from repo root if present
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(dotenv_path=env_path)
    
    # Load configuration values
    api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
    allow_remote_document_upload = os.getenv("ALLOW_REMOTE_DOCUMENT_UPLOAD", "false").lower() in ("true", "1", "yes")
    debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    enable_analytics = os.getenv("ENABLE_ANALYTICS", "false").lower() in ("true", "1", "yes")
    updates_url = os.getenv("UPDATES_URL", "https://cdn.signkit.work/updates.json")
    
    # Validate configuration
    _validate_config(api_base_url, log_level, updates_url)
    
    config = AppConfig(
        api_base_url=api_base_url,
        allow_remote_document_upload=allow_remote_document_upload,
        debug=debug,
        log_level=log_level,
        enable_analytics=enable_analytics,
        updates_url=updates_url
    )
    
    LOG.info(f"Configuration loaded: API={api_base_url}, Debug={debug}")
    return config


def _validate_config(api_base_url: str, log_level: str, updates_url: str) -> None:
    """Validate configuration values and provide helpful error messages."""
    errors = []
    
    # Validate API base URL
    try:
        parsed = urlparse(api_base_url)
        if not parsed.scheme or not parsed.netloc:
            errors.append(f"Invalid API_BASE_URL format: {api_base_url}")
        elif parsed.scheme not in ("http", "https"):
            errors.append(f"API_BASE_URL must use http or https, got: {parsed.scheme}")
    except Exception:
        errors.append(f"Invalid API_BASE_URL: {api_base_url}")
    
    # Validate log level
    valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if log_level not in valid_log_levels:
        errors.append(f"Invalid LOG_LEVEL: {log_level}. Must be one of: {', '.join(valid_log_levels)}")
    
    # Validate updates URL
    try:
        parsed = urlparse(updates_url)
        if not parsed.scheme or not parsed.netloc:
            errors.append(f"Invalid UPDATES_URL format: {updates_url}")
    except Exception:
        errors.append(f"Invalid UPDATES_URL: {updates_url}")
    
    if errors:
        error_msg = "Desktop app configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
        error_msg += "\n\nPlease check your .env file. See .env.example for valid configuration examples."
        LOG.error(error_msg)
        raise ValueError(error_msg)
