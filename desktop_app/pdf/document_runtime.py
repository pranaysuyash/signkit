"""Disposable worker-process boundary for untrusted PDFium work."""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
from typing import Any


class DocumentRuntimeError(RuntimeError):
    """Raised when a document worker cannot return a valid result."""


@dataclass(frozen=True)
class IsolatedDocumentRuntime:
    """Run one PDF operation in a disposable child process.

    The parent process owns no PDFium objects for these operations. A worker
    timeout or native crash becomes a structured Python error instead of
    terminating the desktop process.
    """

    timeout_seconds: float = 30.0
    python_executable: str | None = None

    @property
    def _project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    def _run(self, request: dict[str, Any]) -> dict[str, Any]:
        executable = self.python_executable or sys.executable
        environment = os.environ.copy()
        project_root = str(self._project_root)
        existing_pythonpath = environment.get("PYTHONPATH")
        environment["PYTHONPATH"] = (
            f"{project_root}{os.pathsep}{existing_pythonpath}"
            if existing_pythonpath
            else project_root
        )
        try:
            completed = subprocess.run(
                [executable, "-m", "desktop_app.pdf.document_worker"],
                input=json.dumps(request),
                text=True,
                capture_output=True,
                cwd=project_root,
                env=environment,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise DocumentRuntimeError("document_worker_timeout") from exc
        except OSError as exc:
            raise DocumentRuntimeError("document_worker_unavailable") from exc

        if completed.returncode != 0:
            raise DocumentRuntimeError(
                f"document_worker_exit:{completed.returncode}"
            )
        try:
            response = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise DocumentRuntimeError("document_worker_invalid_response") from exc
        if not isinstance(response, dict) or response.get("ok") is not True:
            reason = response.get("error", "unknown") if isinstance(response, dict) else "unknown"
            raise DocumentRuntimeError(f"document_worker_failed:{reason}")
        return response

    def detect_page(self, pdf_path: str, page_index: int) -> list[dict[str, Any]]:
        response = self._run(
            {"operation": "detect_page", "pdf_path": str(pdf_path), "page_index": page_index}
        )
        candidates = response.get("candidates")
        if not isinstance(candidates, list):
            raise DocumentRuntimeError("document_worker_invalid_candidates")
        return [candidate for candidate in candidates if isinstance(candidate, dict)]

    def render_page(self, pdf_path: str, page_index: int, scale: float = 1.0) -> bytes:
        response = self._run(
            {
                "operation": "render_page",
                "pdf_path": str(pdf_path),
                "page_index": page_index,
                "scale": scale,
            }
        )
        encoded = response.get("png_base64")
        if not isinstance(encoded, str):
            raise DocumentRuntimeError("document_worker_invalid_render")
        try:
            return base64.b64decode(encoded, validate=True)
        except ValueError as exc:
            raise DocumentRuntimeError("document_worker_invalid_render") from exc
