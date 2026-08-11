"""Utility helpers for workflow operators and durable identifiers."""

from __future__ import annotations

import getpass
import hashlib
import os
from pathlib import Path
from typing import Optional


def _coerce_subject(value: Optional[object]) -> str | None:
    """Return a non-empty string subject from an optional value, else ``None``."""

    if not isinstance(value, str):
        return None

    candidate = value.strip()
    if not candidate:
        return None
    return candidate


def resolve_operator_subject(*, session_subject: Optional[str] = None) -> str:
    """Return a stable operator subject for authorization and audit rows.

    Resolution order:
    1. Explicit session subject (typically ``SessionState.user_email``).
    2. Environment overrides.
    3. OS login name.
    4. A fixed local fallback.
    """

    coerced_session_subject = _coerce_subject(session_subject)
    if coerced_session_subject:
        return coerced_session_subject

    for env_key in (
        "SIGNKIT_OPERATOR_SUBJECT",
        "WORKFLOW_OPERATOR_SUBJECT",
        "LOGNAME",
        "USER",
        "USERNAME",
    ):
        candidate = _coerce_subject(os.environ.get(env_key, ""))
        if candidate:
            return candidate

    try:
        return getpass.getuser()
    except Exception:
        return "desktop-operator"


def folder_id_from_path(path: str, *, namespace: str) -> str:
    """Build a deterministic folder identifier for a configured path and namespace."""

    normalized = str(Path(path).expanduser().resolve())
    digest = hashlib.sha1(f"{namespace}:{normalized}".encode("utf-8")).hexdigest()[:12]
    return f"{namespace}-{digest}"
