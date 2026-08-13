"""Executable checks for the shared root environment contract."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("JWT_SECRET", "configuration-contract-secret-that-is-at-least-32-bytes")

from backend.app.config import Settings


ROOT = Path(__file__).resolve().parents[1]


def _example_values() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key] = value
    return values


def test_env_example_declares_safe_local_defaults_and_required_contract() -> None:
    values = _example_values()

    assert values["API_BASE_URL"] == "http://127.0.0.1:8001"
    assert values["DATABASE_URL"] == "sqlite:///./signature_extractor.db"
    assert values["BACKEND_HOST"] == "127.0.0.1"
    assert values["BACKEND_PORT"] == "8001"
    assert values["JWT_SECRET"].startswith("your_")
    example_text = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "Configuration status legend" in example_text
    assert "HOSTED ONLY" in example_text


def test_backend_settings_honor_explicit_database_url_and_shared_root_env_path() -> None:
    settings = Settings(
        JWT_SECRET="x" * 64,
        DATABASE_URL="sqlite:///./contract.sqlite",
    )

    assert settings.resolved_database_url == "sqlite:///./contract.sqlite"
    assert Path(str(settings.model_config["env_file"])).resolve() == (ROOT / ".env").resolve()


def test_backend_launcher_uses_configurable_host_and_port_without_rejecting_local_defaults() -> None:
    script = (ROOT / "scripts" / "run-backend-dev.sh").read_text(encoding="utf-8")

    assert 'BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"' in script
    assert 'BACKEND_PORT="${BACKEND_PORT:-8001}"' in script
    assert 'if [ -z "${DATABASE_URL:-}" ]' not in script
