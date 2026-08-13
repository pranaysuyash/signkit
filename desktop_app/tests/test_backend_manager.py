"""Tests for backend auto-start environment preparation."""

from __future__ import annotations

import os
from unittest.mock import patch

from desktop_app.backend_manager import BackendManager


def test_local_sqlite_fallback_uses_overridden_data_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("SIGNKIT_DATA_DIR", str(tmp_path))
    manager = BackendManager(auto_start=True)

    sqlite_url = manager._local_sqlite_url()

    assert sqlite_url == f"sqlite:///{tmp_path / 'signature_extractor.db'}"


def test_prepare_backend_env_injects_local_sqlite_and_secret(monkeypatch, tmp_path):
    monkeypatch.setenv("SIGNKIT_DATA_DIR", str(tmp_path))
    manager = BackendManager(auto_start=True)

    prepared = manager._prepare_backend_env({})

    assert prepared["DATABASE_URL"] == f"sqlite:///{tmp_path / 'signature_extractor.db'}"
    assert len(prepared["JWT_SECRET"]) == 64
    assert prepared["SIGNKIT_RUNTIME_PROFILE"] == "local_companion"
    assert prepared["SIGNKIT_HEALTH_TOKEN"] == manager._health_token


def test_prepare_backend_env_preserves_explicit_database_url(monkeypatch, tmp_path):
    monkeypatch.setenv("SIGNKIT_DATA_DIR", str(tmp_path))
    manager = BackendManager(auto_start=True)

    prepared = manager._prepare_backend_env(
        {
            "DATABASE_URL": "postgresql://pranay:pranay@127.0.0.1:5432/signature_extractor",
            "JWT_SECRET": "x" * 64,
        }
    )

    assert prepared["DATABASE_URL"] == "postgresql://pranay:pranay@127.0.0.1:5432/signature_extractor"
    assert prepared["JWT_SECRET"] == "x" * 64


def test_inprocess_backend_env_applies_database_and_jwt_contract(monkeypatch, tmp_path):
    """Frozen startup must pass generated local settings before backend import."""

    with patch.dict(os.environ, {"SIGNKIT_DATA_DIR": str(tmp_path)}, clear=True):
        manager = BackendManager(auto_start=True)
        prepared = manager._prepare_backend_env(dict(os.environ))

        manager._apply_inprocess_backend_env(prepared)

        assert os.environ["DATABASE_URL"] == f"sqlite:///{tmp_path / 'signature_extractor.db'}"
        assert os.environ["JWT_SECRET"] == prepared["JWT_SECRET"]
        assert os.environ["SIGNKIT_RUNTIME_PROFILE"] == "local_companion"
        assert os.environ["SIGNKIT_HEALTH_TOKEN"] == manager._health_token


def test_health_check_rejects_generic_healthy_impostor(monkeypatch):
    manager = BackendManager(auto_start=False)

    class ImpostorResponse:
        status_code = 200

        @staticmethod
        def json():
            return {"status": "healthy"}

    monkeypatch.setattr("requests.get", lambda *args, **kwargs: ImpostorResponse())

    assert manager.is_available() is False
