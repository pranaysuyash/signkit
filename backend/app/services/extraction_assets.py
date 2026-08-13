"""Canonical owner-scoped extraction asset and receipt operations."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.extraction_audit import ExtractionAuditEvent
from backend.app.models.image import Image
from backend.app.models.user import User
from backend.app.models.workspace import WorkspaceExecution


class ExtractionAssetError(ValueError):
    """Raised for invalid asset ownership, lifecycle, or retry state."""


class IdempotencyConflict(ExtractionAssetError):
    """Raised when one idempotency key is reused for a different request."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def retention_deadline(seconds: int) -> datetime:
    return utc_now() + timedelta(seconds=max(60, seconds))


def request_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def validate_idempotency_key(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized or len(normalized) > 80:
        raise ExtractionAssetError("Idempotency-Key must be 1-80 characters")
    return normalized


def find_replay(
    db: Session,
    owner: User,
    event_type: str,
    idem_key: str | None,
    expected_hash: str,
) -> ExtractionAuditEvent | None:
    if idem_key is None:
        return None
    event = (
        db.query(ExtractionAuditEvent)
        .filter(
            ExtractionAuditEvent.owner_user_id == owner.id,
            ExtractionAuditEvent.event_type == event_type,
            ExtractionAuditEvent.idem_key == idem_key,
        )
        .first()
    )
    if event is not None and event.request_hash != expected_hash:
        raise IdempotencyConflict("Idempotency-Key was already used for a different request")
    return event


def resolve_replay_after_race(
    db: Session,
    owner: User,
    event_type: str,
    idem_key: str,
    expected_hash: str,
) -> ExtractionAuditEvent:
    db.rollback()
    event = find_replay(db, owner, event_type, idem_key, expected_hash)
    if event is None:
        raise ExtractionAssetError("Idempotent operation could not be recovered")
    return event


def owned_asset(
    db: Session,
    owner: User,
    asset_id: str,
    *,
    include_deleted: bool = False,
) -> Image:
    try:
        normalized_id = uuid.UUID(asset_id)
    except (TypeError, ValueError) as exc:
        raise ExtractionAssetError("Invalid extraction asset id") from exc

    query = db.query(Image).filter(Image.id == normalized_id, Image.user_id == owner.id)
    if not include_deleted:
        query = query.filter(Image.deleted_at.is_(None))
    asset = query.first()
    if asset is None:
        raise FileNotFoundError("Extraction asset not found")
    return asset


def owned_workspace_execution(
    db: Session,
    owner: User,
    workspace_execution_id: str | None,
) -> uuid.UUID | None:
    if not workspace_execution_id:
        return None
    try:
        normalized_id = uuid.UUID(workspace_execution_id)
    except (TypeError, ValueError) as exc:
        raise ExtractionAssetError("Invalid workspace execution id") from exc
    execution = (
        db.query(WorkspaceExecution)
        .filter(
            WorkspaceExecution.id == normalized_id,
            WorkspaceExecution.owner_user_id == owner.id,
        )
        .first()
    )
    if execution is None:
        raise FileNotFoundError("Workspace execution not found")
    return normalized_id


def new_audit_event(
    *,
    owner: User,
    asset_id: uuid.UUID | None,
    event_type: str,
    idem_key: str | None,
    request_hash_value: str,
    response: dict[str, Any] | None = None,
    artifact_path: Path | None = None,
    status_code: int = 200,
) -> ExtractionAuditEvent:
    return ExtractionAuditEvent(
        id=uuid.uuid4(),
        asset_id=asset_id,
        owner_user_id=owner.id,
        event_type=event_type,
        idem_key=idem_key,
        request_hash=request_hash_value,
        status_code=status_code,
        response_json=json.dumps(response, sort_keys=True, default=str) if response is not None else None,
        artifact_path=str(artifact_path) if artifact_path is not None else None,
        # Avoid second-resolution server timestamps so receipt order remains
        # meaningful on SQLite and other databases used by local deployments.
        created_at=utc_now(),
    )


def response_from_event(event: ExtractionAuditEvent) -> dict[str, Any]:
    if not event.response_json:
        return {}
    return json.loads(event.response_json)


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=str(path.parent),
            prefix=".artifact-",
            suffix=".part",
            delete=False,
        ) as temporary_file:
            temporary_path = temporary_file.name
            temporary_file.write(data)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, path)
        os.chmod(path, 0o600)
    finally:
        if temporary_path:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass


def safe_unlink(path: Path | None) -> bool:
    if path is None or not path.exists():
        return True
    try:
        path.unlink()
        return True
    except OSError:
        return False


def audit_events_for_asset(db: Session, owner: User, asset_id: uuid.UUID) -> list[ExtractionAuditEvent]:
    return (
        db.query(ExtractionAuditEvent)
        .filter(
            ExtractionAuditEvent.owner_user_id == owner.id,
            ExtractionAuditEvent.asset_id == asset_id,
        )
        .order_by(ExtractionAuditEvent.created_at.asc(), ExtractionAuditEvent.id.asc())
        .all()
    )


def commit_with_idempotency_recovery(
    db: Session,
    owner: User,
    event: ExtractionAuditEvent,
) -> ExtractionAuditEvent:
    try:
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    except IntegrityError:
        if event.idem_key is None:
            db.rollback()
            raise
        return resolve_replay_after_race(
            db,
            owner,
            event.event_type,
            event.idem_key,
            event.request_hash,
        )
