from __future__ import annotations

import pytest
import requests

from desktop_app.api.client import ApiClient
from desktop_app.api.contracts import LoginResponse, ProcessResponse, UploadResponse
from desktop_app.api.errors import (
    ApiContractError,
    ApiValidationError,
    AuthenticationFailed,
    ExtractionSessionMissing,
)
from desktop_app.state.session import SessionState


class _FakeResponse:
    def __init__(self, *, status_code=200, payload=None, content=b"", headers=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.content = content
        self.headers = headers or {"Content-Type": "application/json"}
        self.text = text

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error", response=self)


def test_api_client_rejects_invalid_base_url():
    with pytest.raises(ValueError, match="Invalid API base URL"):
        ApiClient("ftp://example.com", SessionState())


def test_api_client_updates_base_url_through_boundary():
    client = ApiClient("http://127.0.0.1:8001", SessionState())

    client.update_base_url("http://127.0.0.1:8002")

    assert client.base_url == "http://127.0.0.1:8002"


def test_login_returns_payload_without_mutating_session(monkeypatch):
    session = SessionState()
    client = ApiClient("http://127.0.0.1:8001", session)

    captured = {}

    def fake_post(url, data=None, headers=None, timeout=None):
        captured["url"] = url
        captured["data"] = data
        captured["headers"] = headers
        return _FakeResponse(payload={"access_token": "token-123", "user": "pranay@example.com"})

    monkeypatch.setattr(requests, "post", fake_post)

    payload = client.login("pranay@example.com", "secret")

    assert isinstance(payload, LoginResponse)
    assert payload.access_token == "token-123"
    assert payload.payload["access_token"] == "token-123"
    assert session.access_token is None
    assert session.user_email is None
    assert captured["url"].endswith("/auth/login")
    assert captured["data"] == {"username": "pranay@example.com", "password": "secret"}
    assert captured["headers"]["Accept"] == "application/json"


def test_login_maps_auth_failure(monkeypatch):
    client = ApiClient("http://127.0.0.1:8001", SessionState())

    def fake_post(*args, **kwargs):
        return _FakeResponse(status_code=401, payload={"detail": "Invalid credentials"})

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(AuthenticationFailed, match="Invalid credentials"):
        client.login("pranay@example.com", "wrong")


def test_upload_image_requires_real_file(tmp_path):
    client = ApiClient("http://127.0.0.1:8001", SessionState())
    missing = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError):
        client.upload_image(str(missing))


def test_upload_image_requires_contract_id(tmp_path, monkeypatch):
    client = ApiClient("http://127.0.0.1:8001", SessionState())
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"fake image bytes")

    def fake_post(url, files=None, headers=None, timeout=None):
        return _FakeResponse(payload={"filename": "sample.png"})

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(ApiContractError, match="missing id"):
        client.upload_image(str(image_path))


def test_upload_image_returns_typed_response(tmp_path, monkeypatch):
    client = ApiClient("http://127.0.0.1:8001", SessionState())
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"fake image bytes")
    captured = {}

    def fake_post(url, files=None, headers=None, timeout=None):
        captured["headers"] = headers
        return _FakeResponse(payload={"id": "session-123", "filename": "sample.png", "file_path": None})

    monkeypatch.setattr(requests, "post", fake_post)

    result = client.upload_image(str(image_path))

    assert isinstance(result, UploadResponse)
    assert result.session_id == "session-123"
    assert result.filename == "sample.png"
    assert result.file_path is None
    assert captured["headers"]["Idempotency-Key"].startswith("upload-")


def test_upload_image_blocks_remote_document_egress_by_default(tmp_path, monkeypatch):
    client = ApiClient("https://api.example.com", SessionState())
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"fake image bytes")
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: pytest.fail("remote upload must be blocked"))

    with pytest.raises(ApiValidationError, match="Remote document upload is disabled"):
        client.upload_image(str(image_path))


def test_upload_image_allows_explicit_connected_mode(tmp_path, monkeypatch):
    client = ApiClient(
        "https://api.example.com",
        SessionState(),
        allow_remote_document_upload=True,
    )
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"fake image bytes")
    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: _FakeResponse(payload={"id": "session-remote", "filename": "sample.png"}),
    )

    result = client.upload_image(str(image_path))

    assert result.session_id == "session-remote"


def test_process_image_validates_selection_before_network():
    client = ApiClient("http://127.0.0.1:8001", SessionState())

    with pytest.raises(ApiValidationError, match="session_id is required"):
        client.process_image(session_id=" ", x1=0, y1=0, x2=10, y2=10, color="#000000", threshold=128)

    with pytest.raises(ApiValidationError, match="x2 must be > x1"):
        client.process_image(session_id="session-1", x1=10, y1=0, x2=5, y2=10, color="#000000", threshold=128)

    with pytest.raises(ApiValidationError, match="threshold must be between 0 and 255"):
        client.process_image(session_id="session-1", x1=0, y1=0, x2=10, y2=10, color="#000000", threshold=999)

    with pytest.raises(ApiValidationError, match="color must be a #RRGGBB hex value"):
        client.process_image(session_id="session-1", x1=0, y1=0, x2=10, y2=10, color="blue", threshold=128)


def test_process_image_maps_missing_session(monkeypatch):
    client = ApiClient("http://127.0.0.1:8001", SessionState())

    def fake_post(url, data=None, headers=None, timeout=None):
        return _FakeResponse(status_code=404, payload={"detail": "Image file not found."})

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(ExtractionSessionMissing, match="Image file not found"):
        client.process_image(session_id="session-1", x1=0, y1=0, x2=10, y2=10, color="#000000", threshold=128)


def test_process_image_returns_typed_response(monkeypatch):
    client = ApiClient("http://127.0.0.1:8001", SessionState())
    captured = {}

    def fake_post(url, data=None, headers=None, timeout=None):
        captured["headers"] = headers
        return _FakeResponse(
            payload=None,
            content=b"png-bytes",
            headers={"Content-Type": "image/png"},
        )

    monkeypatch.setattr(requests, "post", fake_post)

    result = client.process_image(session_id="session-1", x1=0, y1=0, x2=10, y2=10, color="#000000", threshold=128)

    assert isinstance(result, ProcessResponse)
    assert result.png_bytes == b"png-bytes"
    assert result.content_type == "image/png"
    assert captured["headers"]["Idempotency-Key"].startswith("process-")


def test_select_region_validates_input():
    client = ApiClient("http://127.0.0.1:8001", SessionState())

    with pytest.raises(ApiValidationError, match="session_id is required"):
        client.select_region(session_id=" ", x1=0, y1=0, x2=10, y2=10, color="#000000", threshold=128)

    with pytest.raises(ApiValidationError, match="x2 must be > x1"):
        client.select_region(session_id="session-1", x1=10, y1=0, x2=5, y2=10, color="#000000", threshold=128)


def test_select_region_maps_missing_session(monkeypatch):
    client = ApiClient("http://127.0.0.1:8001", SessionState())

    def fake_post(url, data=None, headers=None, timeout=None):
        return _FakeResponse(status_code=404, payload={"detail": "Session not found"})

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(ExtractionSessionMissing, match="Session not found"):
        client.select_region(session_id="session-1", x1=0, y1=0, x2=10, y2=10, color="#000000", threshold=128)


def test_select_region_returns_typed_response(monkeypatch):
    client = ApiClient("http://127.0.0.1:8001", SessionState())
    captured = {}

    def fake_post(url, data=None, headers=None, timeout=None):
        captured["headers"] = headers
        return _FakeResponse(
            payload={
                "message": "Region selected",
                "session_id": "session-123",
                "selection": {"x1": 1, "y1": 2, "x2": 3, "y2": 4},
                "image": {"width": 20, "height": 10},
                "file_path": None,
            }
        )

    monkeypatch.setattr(requests, "post", fake_post)

    result = client.select_region(session_id="session-1", x1=0, y1=0, x2=10, y2=10, color="#000000", threshold=128)

    assert result.session_id == "session-123"
    assert result.selection == {"x1": 1, "y1": 2, "x2": 3, "y2": 4}
    assert result.image == {"width": 20, "height": 10}
    assert result.payload["session_id"] == "session-123"
    assert captured["headers"]["Idempotency-Key"].startswith("select-")


def test_health_check_recovers_after_transient_failure(monkeypatch):
    client = ApiClient("http://127.0.0.1:8001", SessionState())
    calls = {"count": 0}

    def fake_get(url, headers=None, timeout=None):
        calls["count"] += 1
        if calls["count"] == 1:
            raise requests.ConnectionError("boom")
        return _FakeResponse(payload={"status": "healthy", "version": "1.0"})

    monkeypatch.setattr(requests, "get", fake_get)

    ok1, payload1 = client.health_check(timeout=0.1)
    ok2, payload2 = client.health_check(timeout=0.1)

    assert not ok1
    assert "error" in payload1
    assert ok2
    assert payload2["status"] == "healthy"
    assert not client.is_offline()
    assert calls["count"] == 2


def test_health_check_honors_manual_offline_mode(monkeypatch):
    client = ApiClient("http://127.0.0.1:8001", SessionState())
    client.set_offline_mode(True)

    called = {"count": 0}

    def fake_get(*args, **kwargs):
        called["count"] += 1
        return _FakeResponse(payload={"status": "healthy"})

    monkeypatch.setattr(requests, "get", fake_get)

    ok, payload = client.health_check(timeout=0.1)

    assert not ok
    assert payload["error"] == "Client in offline mode"
    assert called["count"] == 0
