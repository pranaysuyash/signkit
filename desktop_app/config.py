import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv
from urllib.parse import urlparse

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


def get_purchase_url() -> str:
    """Return Dodo checkout when configured, otherwise the explicit fallback."""
    product_id = os.getenv("DODO_PRODUCT_ID", "").strip()
    if product_id.startswith("pdt_") and product_id[4:].isalnum():
        return f"{DODO_CHECKOUT_BASE_URL}{product_id}"
    return os.getenv("GUMROAD_PRODUCT_URL", GUMROAD_FALLBACK_URL)


@dataclass
class AppConfig:
    api_base_url: str
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
    debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    enable_analytics = os.getenv("ENABLE_ANALYTICS", "false").lower() in ("true", "1", "yes")
    updates_url = os.getenv("UPDATES_URL", "https://cdn.signkit.work/updates.json")
    
    # Validate configuration
    _validate_config(api_base_url, log_level, updates_url)
    
    config = AppConfig(
        api_base_url=api_base_url,
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
