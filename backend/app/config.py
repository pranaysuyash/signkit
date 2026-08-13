from __future__ import annotations

import logging
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        # The repository root .env is the shared configuration surface for the
        # desktop app, backend launcher, and local migration commands.
        env_file=str((Path(__file__).resolve().parents[2] / ".env")),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Database settings
    DATABASE_HOSTNAME: str = "localhost"
    DATABASE_PORT: str = "5432"
    DATABASE_PASSWORD: str = "pranay"
    DATABASE_NAME: str = "signature_extractor"
    DATABASE_USERNAME: str = "pranay"
    DATABASE_URL: str | None = None

    # JWT settings
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Optional third-party integrations
    RAZORPAY_KEY_ID: str | None = None
    RAZORPAY_KEY_SECRET: str | None = None

    @property
    def resolved_database_url(self) -> str:
        """Construct a SQLAlchemy-compatible database URL."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOSTNAME}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_configuration()
        logger.info("Settings initialized successfully")
        logger.debug("Database URL: %s", self.resolved_database_url)
        logger.debug("JWT Algorithm: %s", self.JWT_ALGORITHM)
        logger.debug(
            "JWT Expiry: %s minutes", self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    def _validate_configuration(self) -> None:
        """Validate configuration and provide helpful error messages."""
        errors = []
        
        # Validate JWT_SECRET
        if not self.JWT_SECRET or self.JWT_SECRET == "your_super_secret_jwt_key_here_replace_with_random_32_byte_hex":
            errors.append(
                "JWT_SECRET is missing or using example value. "
                "Generate a secure key with: openssl rand -hex 32"
            )
        elif len(self.JWT_SECRET) < 32:
            errors.append(
                "JWT_SECRET is too short. Use at least 32 characters for security. "
                "Generate with: openssl rand -hex 32"
            )
        
        # Validate database configuration
        if not self.DATABASE_NAME:
            errors.append("DATABASE_NAME is required")
        
        if not self.DATABASE_USERNAME:
            errors.append("DATABASE_USERNAME is required")
        
        if not self.DATABASE_PASSWORD or self.DATABASE_PASSWORD == "your_db_password":
            errors.append(
                "DATABASE_PASSWORD is missing or using example value. "
                "Set a secure database password."
            )
        
        # Validate port
        try:
            port = int(self.DATABASE_PORT)
            if port < 1 or port > 65535:
                errors.append(f"DATABASE_PORT must be between 1-65535, got {port}")
        except ValueError:
            errors.append(f"DATABASE_PORT must be a number, got '{self.DATABASE_PORT}'")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            error_msg += "\n\nPlease check your .env file or environment variables."
            error_msg += "\nSee .env.example for configuration examples."
            logger.error(error_msg)
            raise ValueError(error_msg)


try:
    settings = Settings()
except ValidationError as exc:
    logger.error("Settings validation error: %s", exc)
    raise
except Exception as exc:
    logger.error("Unexpected error loading settings: %s", exc)
    raise
