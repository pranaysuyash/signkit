"""Security hardening tests for backend config and on-disk PII paths.

Covers:
- W2 / ISSUE-009: no hardcoded DB credentials; production fails closed.
- W4 / ISSUE-010: config reload / test seam.
- W3 / ISSUE-012: owner-only permissions on user-data dirs and sidecars.
"""
from __future__ import annotations

import os
import stat

import pytest

from backend.app.config import Settings, get_settings, reload_settings
from backend.app.paths import get_user_data_dir
from backend.app.services.extraction import persist_selection_metadata


def _require_posix() -> None:
    if os.name != "posix":
        pytest.skip("Permission hardening is only enforced on POSIX systems.")


def test_no_hardcoded_database_credentials() -> None:
    """The default DB password/username must not be a real value (ISSUE-009)."""
    assert Settings.model_fields["DATABASE_PASSWORD"].default is None
    assert Settings.model_fields["DATABASE_USERNAME"].default is None


def test_local_dev_allows_missing_credentials(monkeypatch) -> None:
    """Local dev with no DATABASE_URL and no creds must still construct."""
    monkeypatch.setenv("JWT_SECRET", "x" * 64)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./dev.sqlite")
    monkeypatch.delenv("DATABASE_USERNAME", raising=False)
    monkeypatch.delenv("DATABASE_PASSWORD", raising=False)
    settings = Settings(ENVIRONMENT="development", DATABASE_URL=None)
    assert settings.DATABASE_USERNAME is None
    assert settings.DATABASE_PASSWORD is None


def test_production_fails_closed_without_credentials(monkeypatch) -> None:
    """Production with no DATABASE_URL and no creds must raise (ISSUE-009)."""
    monkeypatch.setenv("JWT_SECRET", "x" * 64)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_USERNAME", raising=False)
    monkeypatch.delenv("DATABASE_PASSWORD", raising=False)
    with pytest.raises(ValueError, match="DATABASE_USERNAME and DATABASE_PASSWORD"):
        Settings(ENVIRONMENT="production", DATABASE_URL=None)


def test_full_database_url_requires_no_separate_credentials(monkeypatch) -> None:
    """A complete Postgres DATABASE_URL must not require bare creds (prod)."""
    monkeypatch.setenv("JWT_SECRET", "x" * 64)
    settings = Settings(
        ENVIRONMENT="production",
        DATABASE_URL="postgresql://app_user:app_pass@db:5432/sig",
    )
    assert settings.resolved_database_url.startswith("postgresql://")


def test_reload_settings_seam_picks_up_env(monkeypatch) -> None:
    """reload_settings() must reflect post-import env changes (ISSUE-010)."""
    from backend.app import config

    original = config.settings
    try:
        monkeypatch.setenv("JWT_SECRET", "x" * 64)
        monkeypatch.setenv("DATABASE_URL", "sqlite:///./reload.sqlite")
        monkeypatch.setenv("DATABASE_USERNAME", "reloaded-user")
        reload_settings()
        assert get_settings().DATABASE_USERNAME == "reloaded-user"
    finally:
        config.settings = original


def test_user_data_dir_is_owner_only(monkeypatch, tmp_path) -> None:
    """Per-user data dir is created with owner-only perms (ISSUE-012)."""
    _require_posix()
    monkeypatch.setenv("SIGNKIT_DATA_DIR", str(tmp_path))
    data_dir = get_user_data_dir()
    mode = stat.S_IMODE(data_dir.stat().st_mode)
    assert mode == 0o700


def test_persist_selection_metadata_is_owner_only(monkeypatch, tmp_path) -> None:
    """Selection sidecar dir + file are owner-only (ISSUE-012)."""
    _require_posix()
    metadata_dir = tmp_path / "regions"
    path = persist_selection_metadata(
        metadata_dir, "asset-1", {"x1": 0, "y1": 0, "x2": 10, "y2": 10}
    )
    dir_mode = stat.S_IMODE(metadata_dir.stat().st_mode)
    file_mode = stat.S_IMODE(path.stat().st_mode)
    assert dir_mode == 0o700
    assert file_mode == 0o600
