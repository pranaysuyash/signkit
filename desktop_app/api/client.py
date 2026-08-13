from __future__ import annotations

import mimetypes
import hashlib
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse
from uuid import uuid4

import requests

from desktop_app.api.contracts import LoginResponse, ProcessResponse, RegionSelectionResponse, UploadResponse
from desktop_app.api.errors import (
    ApiContractError,
    ApiValidationError,
    AuthenticationFailed,
    BackendUnavailable,
    ExtractionSessionMissing,
    ProcessingFailed,
    UploadFailed,
)
from desktop_app.state.session import SessionState


class ApiClient:
    MAX_UPLOAD_BYTES = 50 * 1024 * 1024
    _HEALTHY_STATUSES = {"ok", "healthy", "up"}

    def __init__(self, base_url: str, session: SessionState) -> None:
        self._base_url = self._validate_base_url(base_url)
        self.session = session
        self._manual_offline_mode = False
        self._backend_reachable = True
        self._last_health_error: Optional[str] = None

    @property
    def base_url(self) -> str:
        return self._base_url

    def update_base_url(self, base_url: str) -> None:
        """Update the backend base URL through a validated boundary."""
        self._base_url = self._validate_base_url(base_url)

    @staticmethod
    def _validate_base_url(base_url: str) -> str:
        parsed = urlparse(base_url.rstrip("/"))
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Invalid API base URL scheme")
        if not parsed.netloc:
            raise ValueError("Invalid API base URL host")
        return base_url.rstrip("/")

    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Accept": "application/json",
            "X-Request-ID": uuid4().hex,
        }
        token = getattr(self.session, "access_token", None)
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if extra:
            headers.update(extra)
        return headers

    def login(self, username: str, password: str) -> LoginResponse:
        url = f"{self.base_url}/auth/login"
        data = {"username": username, "password": password}
        try:
            resp = requests.post(url, data=data, headers=self._headers(), timeout=30)
        except requests.Timeout as exc:
            raise BackendUnavailable("Backend timed out during login") from exc
        except requests.RequestException as exc:
            raise BackendUnavailable("Backend is unreachable during login") from exc

        if resp.status_code in {401, 403}:
            raise AuthenticationFailed("Invalid credentials")
        if resp.status_code >= 400:
            detail = self._response_detail(resp) or f"Login failed with status {resp.status_code}"
            if resp.status_code in {400, 422}:
                raise ApiValidationError(detail)
            if resp.status_code >= 500:
                raise BackendUnavailable(detail)
            raise ApiContractError(detail)

        payload = self._json_payload(resp, "login")
        token = payload.get("access_token")
        if not token:
            raise ApiContractError("Login response missing access_token")
        return LoginResponse(access_token=str(token), payload=payload)

    def upload_image(self, filepath: str) -> UploadResponse:
        url = f"{self.base_url}/extraction/upload"
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(filepath)
        if not path.is_file():
            raise FileNotFoundError(filepath)
        if not os.access(path, os.R_OK):
            raise ApiValidationError(f"Upload file is not readable: {filepath}")
        size = path.stat().st_size
        if size <= 0:
            raise ApiValidationError("Upload file is empty")
        if size > self.MAX_UPLOAD_BYTES:
            raise ApiValidationError("Upload file exceeds 50MB limit")

        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        upload_idempotency_key = f"upload-{hashlib.sha256(path.read_bytes()).hexdigest()}"
        with path.open("rb") as f:
            files = {"file": (path.name, f, mime_type)}
            try:
                resp = requests.post(
                    url,
                    files=files,
                    headers=self._headers({"Idempotency-Key": upload_idempotency_key}),
                    timeout=120,
                )
            except requests.Timeout as exc:
                raise BackendUnavailable("Backend timed out during upload") from exc
            except requests.RequestException as exc:
                raise BackendUnavailable("Backend is unreachable during upload") from exc

        if resp.status_code == 413:
            raise ApiValidationError("Upload file exceeds server limits")
        if resp.status_code >= 400:
            detail = self._response_detail(resp) or f"Upload failed with status {resp.status_code}"
            if resp.status_code in {400, 422}:
                raise ApiValidationError(detail)
            if resp.status_code >= 500:
                raise UploadFailed(detail)
            raise ApiContractError(detail)

        payload = self._json_payload(resp, "upload")
        session_id = payload.get("id")
        if not session_id:
            raise ApiContractError("Upload response missing id")
        return UploadResponse(
            session_id=str(session_id),
            filename=str(payload.get("filename")) if payload.get("filename") else None,
            file_path=str(payload.get("file_path")) if payload.get("file_path") else None,
            payload=payload,
        )

    def select_region(
        self,
        *,
        session_id: str,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        threshold: int,
    ) -> RegionSelectionResponse:
        session_id = self._validate_session_id(session_id)
        self._validate_selection(x1=x1, y1=y1, x2=x2, y2=y2)
        self._validate_threshold(threshold)
        self._validate_color(color)

        url = f"{self.base_url}/extraction/select_region/"
        data = {
            "session_id": session_id,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "color": color,
            "threshold": threshold,
        }
        selection_idempotency_key = "select-" + hashlib.sha256(
            json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        try:
            resp = requests.post(
                url,
                data=data,
                headers=self._headers({"Idempotency-Key": selection_idempotency_key}),
                timeout=30,
            )
        except requests.Timeout as exc:
            raise BackendUnavailable("Backend timed out while selecting region") from exc
        except requests.RequestException as exc:
            raise BackendUnavailable("Backend is unreachable while selecting region") from exc

        if resp.status_code == 404:
            raise ExtractionSessionMissing("Session not found for select region")
        if resp.status_code in {400, 422}:
            detail = self._response_detail(resp) or "Invalid region selection"
            raise ApiValidationError(detail)
        if resp.status_code in {401, 403}:
            raise AuthenticationFailed("Authentication is required to select region")
        if resp.status_code >= 400:
            detail = self._response_detail(resp) or f"Select region failed with status {resp.status_code}"
            if resp.status_code >= 500:
                raise ApiContractError(detail)
            raise ApiContractError(detail)

        payload = self._json_payload(resp, "select region")
        payload_session_id = payload.get("session_id")
        if not payload_session_id:
            raise ApiContractError("Select region response missing session_id")
        return RegionSelectionResponse(
            session_id=str(payload_session_id),
            message=str(payload.get("message")) if payload.get("message") else None,
            selection=payload.get("selection") if isinstance(payload.get("selection"), dict) else None,
            image=payload.get("image") if isinstance(payload.get("image"), dict) else None,
            file_path=str(payload.get("file_path")) if payload.get("file_path") else None,
            payload=payload,
        )

    def process_image(self, *, session_id: str, x1: int, y1: int, x2: int, y2: int, color: str, threshold: int) -> ProcessResponse:
        session_id = self._validate_session_id(session_id)
        self._validate_selection(x1=x1, y1=y1, x2=x2, y2=y2)
        self._validate_threshold(threshold)
        self._validate_color(color)

        url = f"{self.base_url}/extraction/process_image/"
        data = {
            "session_id": session_id,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "color": color,
            "threshold": threshold,
        }
        process_idempotency_key = "process-" + hashlib.sha256(
            json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        try:
            resp = requests.post(
                url,
                data=data,
                headers=self._headers({"Idempotency-Key": process_idempotency_key}),
                timeout=120,
            )
        except requests.Timeout as exc:
            raise BackendUnavailable("Backend timed out during processing") from exc
        except requests.RequestException as exc:
            raise BackendUnavailable("Backend is unreachable during processing") from exc

        if resp.status_code == 404:
            raise ExtractionSessionMissing("Image file not found on server for session_id")
        if resp.status_code in {400, 422}:
            detail = self._response_detail(resp) or "Invalid crop selection"
            raise ApiValidationError(detail)
        if resp.status_code in {401, 403}:
            raise AuthenticationFailed("Authentication is required to process the image")
        if resp.status_code >= 400:
            detail = self._response_detail(resp) or f"Processing failed with status {resp.status_code}"
            if resp.status_code >= 500:
                raise ProcessingFailed(detail)
            raise ApiContractError(detail)

        if "image/png" not in resp.headers.get("Content-Type", "image/png"):
            raise ProcessingFailed("Processing response did not return PNG data")
        return ProcessResponse(
            png_bytes=resp.content,
            content_type=resp.headers.get("Content-Type", "image/png"),
        )

    def set_offline_mode(self, offline: bool) -> None:
        """Set manual offline mode for graceful degradation."""
        self._manual_offline_mode = offline
    
    def is_offline(self) -> bool:
        """Return whether the client is currently offline."""
        return self._manual_offline_mode or not self._backend_reachable

    def _validate_session_id(self, session_id: str) -> str:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ApiValidationError("session_id is required")
        return session_id.strip()

    def _validate_selection(self, *, x1: int, y1: int, x2: int, y2: int) -> None:
        for name, value in {"x1": x1, "y1": y1, "x2": x2, "y2": y2}.items():
            if not isinstance(value, int):
                raise ApiValidationError(f"{name} must be an integer")
            if value < 0:
                raise ApiValidationError(f"{name} must be non-negative")
        if x2 <= x1:
            raise ApiValidationError("x2 must be > x1")
        if y2 <= y1:
            raise ApiValidationError("y2 must be > y1")

    def _validate_threshold(self, threshold: int) -> None:
        if not isinstance(threshold, int):
            raise ApiValidationError("threshold must be an integer")
        if not 0 <= threshold <= 255:
            raise ApiValidationError("threshold must be between 0 and 255")

    def _validate_color(self, color: str) -> None:
        if not isinstance(color, str) or not color.startswith("#") or len(color) != 7:
            raise ApiValidationError("color must be a #RRGGBB hex value")
        try:
            int(color[1:], 16)
        except ValueError as exc:
            raise ApiValidationError("color must be a #RRGGBB hex value") from exc

    def _json_payload(self, response: requests.Response, context: str) -> Dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise ApiContractError(f"{context} response was not valid JSON") from exc
        if not isinstance(payload, dict):
            raise ApiContractError(f"{context} response must be a JSON object")
        return payload

    def _response_detail(self, response: requests.Response) -> Optional[str]:
        try:
            payload = response.json()
        except ValueError:
            return response.text.strip() or None
        if isinstance(payload, dict):
            detail = payload.get("detail") or payload.get("error")
            if detail:
                return str(detail)
        return response.text.strip() or None

    def health_check(self, timeout: float = 3.0) -> Tuple[bool, Dict[str, Any]]:
        """Ping backend /health. Returns (ok, payload_or_error).

        - ok=True and payload dict when reachable and healthy
        - ok=False and payload containing {"error": str} when unreachable or unhealthy
        """
        if self._manual_offline_mode:
            self._backend_reachable = False
            self._last_health_error = "Client in offline mode"
            return False, {"error": self._last_health_error}

        url = f"{self.base_url}/health"
        try:
            resp = requests.get(url, headers={"Accept": "application/json"}, timeout=timeout)
            if resp.status_code >= 400:
                payload = self._json_payload(resp, "health")
                self._backend_reachable = False
                self._last_health_error = self._response_detail(resp) or payload.get("detail") or payload.get("error") or f"Health check failed with status {resp.status_code}"
                return False, payload
            payload = self._json_payload(resp, "health")
            status = str(payload.get("status", "")).lower()
            ok = not status or status in self._HEALTHY_STATUSES
            self._backend_reachable = ok
            self._last_health_error = None if ok else payload.get("detail") or payload.get("error") or "Backend is unhealthy"
            return ok, payload
        except requests.Timeout as exc:
            self._backend_reachable = False
            self._last_health_error = "Backend timed out"
            return False, {"error": self._last_health_error}
        except requests.RequestException as exc:
            self._backend_reachable = False
            self._last_health_error = str(exc)
            return False, {"error": self._last_health_error}
        except ApiContractError as exc:
            self._backend_reachable = False
            self._last_health_error = str(exc)
            return False, {"error": self._last_health_error}
