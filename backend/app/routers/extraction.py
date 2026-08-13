"""Authenticated, owner-scoped extraction asset routes."""

from __future__ import annotations

import io
import hashlib
import json
import logging
import uuid
import zipfile
from pathlib import Path

import cv2
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.extraction_audit import ExtractionAuditEvent
from backend.app.models.image import Image
from backend.app.models.user import User
from backend.app.paths import UPLOADS_DIR
from backend.app.schemas.extraction import ExtractionAuditEventResponse
from backend.app.security import UploadSecurity
from backend.app.services.extraction import (
    build_selection_metadata,
    persist_selection_metadata,
    render_signature_png,
    resolve_upload_path,
)
from backend.app.services.extraction_assets import (
    ExtractionAssetError,
    IdempotencyConflict,
    atomic_write,
    audit_events_for_asset,
    commit_with_idempotency_recovery,
    find_replay,
    new_audit_event,
    owned_asset,
    owned_workspace_execution,
    request_hash,
    response_from_event,
    retention_deadline,
    safe_unlink,
    utc_now,
    validate_idempotency_key,
)
from backend.app.services.upload_lifecycle import cleanup_expired_uploads, upload_retention_seconds
from backend.app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Extraction"])

os_uploads_dir = Path(str(UPLOADS_DIR))
os_uploads_dir.mkdir(parents=True, exist_ok=True)
REGION_METADATA_DIR = os_uploads_dir / "regions"
REGION_METADATA_DIR.mkdir(parents=True, exist_ok=True)


class RegionSelectionRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="Asset ID returned by upload")
    x1: int = Field(..., ge=0)
    y1: int = Field(..., ge=0)
    x2: int = Field(..., ge=0)
    y2: int = Field(..., ge=0)
    color: str = Field(..., min_length=7, max_length=7)
    threshold: int = Field(..., ge=0, le=255)


def _asset_response(asset: Image) -> dict[str, object]:
    return {
        "id": str(asset.id),
        "filename": asset.filename,
        "file_path": None,
        "content_type": asset.content_type,
        "workspace_execution_id": (
            str(asset.workspace_execution_id) if asset.workspace_execution_id else None
        ),
        "created_at": asset.created_at,
        "retention_expires_at": asset.retention_expires_at,
        "deleted_at": asset.deleted_at,
    }


def _asset_or_404(db: Session, current_user: User, asset_id: str, *, include_deleted: bool = False) -> Image:
    try:
        return owned_asset(db, current_user, asset_id, include_deleted=include_deleted)
    except (ExtractionAssetError, FileNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extraction asset not found") from exc


def _replay_payload(event: ExtractionAuditEvent) -> dict[str, object]:
    payload = response_from_event(event)
    payload["receipt_id"] = str(event.id)
    payload["replayed"] = True
    return payload


def _http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, IdempotencyConflict):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, FileNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, ExtractionAssetError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Extraction operation failed")


@router.get("/assets")
def list_assets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List active assets owned by the authenticated principal."""
    assets = (
        db.query(Image)
        .filter(Image.user_id == current_user.id, Image.deleted_at.is_(None))
        .order_by(Image.created_at.desc())
        .all()
    )
    return {"assets": [_asset_response(asset) for asset in assets]}


@router.post("/upload")
def upload_image_endpoint(
    file: UploadFile = File(...),
    workspace_execution_id: str | None = Form(default=None),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    temporary_asset_path: Path | None = None
    try:
        if not file:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")
        filename = (file.filename or "").strip()
        extension = Path(filename).suffix.lower()
        if file.content_type and file.content_type.lower() not in {"image/png", "image/jpeg"}:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported image media type",
            )
        data = file.file.read(UploadSecurity.MAX_FILE_SIZE + 1)
        UploadSecurity.validate_image_bytes(filename, data)
        idempotency_key = validate_idempotency_key(idempotency_key)

        content_sha256 = hashlib.sha256(data).hexdigest()
        fingerprint = request_hash(
            {
                "filename": filename,
                "content_sha256": content_sha256,
                "workspace_execution_id": workspace_execution_id,
            }
        )
        replay = find_replay(db, current_user, "upload", idempotency_key, fingerprint)
        if replay is not None:
            return _replay_payload(replay)

        workspace_id = owned_workspace_execution(db, current_user, workspace_execution_id)
        asset_id = uuid.uuid4()
        saved_filename = f"{asset_id}{extension}"
        temporary_asset_path = os_uploads_dir / saved_filename
        atomic_write(temporary_asset_path, data)

        asset = Image(
            id=asset_id,
            user_id=current_user.id,
            filename=saved_filename,
            file_path=str(temporary_asset_path),
            content_type=file.content_type or "application/octet-stream",
            workspace_execution_id=workspace_id,
            content_sha256=content_sha256,
            retention_expires_at=retention_deadline(upload_retention_seconds()),
        )
        db.add(asset)
        db.flush()
        response = _asset_response(asset)
        event = new_audit_event(
            owner=current_user,
            asset_id=asset.id,
            event_type="upload",
            idem_key=idempotency_key,
            request_hash_value=fingerprint,
            response=response,
        )
        committed_event = commit_with_idempotency_recovery(db, current_user, event)
        if committed_event.id != event.id:
            safe_unlink(temporary_asset_path)
            return _replay_payload(committed_event)

        cleanup_expired_uploads(os_uploads_dir, REGION_METADATA_DIR)
        response["receipt_id"] = str(committed_event.id)
        response["replayed"] = False
        logger.info("Extraction asset uploaded for authenticated owner")
        return response
    except HTTPException:
        if temporary_asset_path is not None:
            safe_unlink(temporary_asset_path)
        raise
    except FileNotFoundError as exc:
        if temporary_asset_path is not None:
            safe_unlink(temporary_asset_path)
        raise _http_error(exc) from exc
    except (ValueError, ExtractionAssetError) as exc:
        if temporary_asset_path is not None:
            safe_unlink(temporary_asset_path)
        raise _http_error(exc) from exc
    except IntegrityError as exc:
        if temporary_asset_path is not None:
            safe_unlink(temporary_asset_path)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Upload retry could not be reconciled") from exc
    except Exception as exc:
        if temporary_asset_path is not None:
            safe_unlink(temporary_asset_path)
        db.rollback()
        logger.exception("Error uploading image: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload image") from exc


@router.post("/select_region/")
def select_region(
    payload: RegionSelectionRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        idempotency_key = validate_idempotency_key(idempotency_key)
        fingerprint = request_hash(payload.model_dump())
        replay = find_replay(db, current_user, "select_region", idempotency_key, fingerprint)
        if replay is not None:
            return _replay_payload(replay)

        asset = _asset_or_404(db, current_user, payload.session_id)
        file_path = resolve_upload_path(str(asset.id), os_uploads_dir)
        image = cv2.imread(str(file_path))
        if image is None:
            raise ValueError("Failed to read image file")

        height, width = image.shape[:2]
        metadata = build_selection_metadata(
            str(asset.id),
            width=width,
            height=height,
            x1=payload.x1,
            y1=payload.y1,
            x2=payload.x2,
            y2=payload.y2,
            threshold=payload.threshold,
            color=payload.color,
        )
        asset.selection_json = json.dumps(metadata, sort_keys=True)
        response = {
            "message": "Region selected",
            "session_id": str(asset.id),
            "selection": metadata["selection"],
            "image": metadata["image_bounds"],
            "file_path": None,
        }
        event = new_audit_event(
            owner=current_user,
            asset_id=asset.id,
            event_type="select_region",
            idem_key=idempotency_key,
            request_hash_value=fingerprint,
            response=response,
        )
        committed_event = commit_with_idempotency_recovery(db, current_user, event)
        if committed_event.id != event.id:
            return _replay_payload(committed_event)
        try:
            persist_selection_metadata(REGION_METADATA_DIR, str(asset.id), metadata)
        except OSError:
            logger.exception("Selection sidecar persistence failed; database receipt remains canonical")
        response["receipt_id"] = str(committed_event.id)
        response["replayed"] = False
        return response
    except HTTPException:
        raise
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extraction asset not found") from exc
    except (ValueError, ExtractionAssetError) as exc:
        raise _http_error(exc) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Selection retry could not be reconciled") from exc
    except Exception as exc:
        db.rollback()
        logger.exception("Error in select_region: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to select region") from exc


@router.post("/process_image/")
def process_image_endpoint(
    session_id: str = Form(...),
    x1: int = Form(...),
    y1: int = Form(...),
    x2: int = Form(...),
    y2: int = Form(...),
    color: str = Form(...),
    threshold: int = Form(...),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    output_path: Path | None = None
    try:
        idempotency_key = validate_idempotency_key(idempotency_key)
        request_payload = {
            "session_id": session_id,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "color": color,
            "threshold": threshold,
        }
        fingerprint = request_hash(request_payload)
        replay = find_replay(db, current_user, "process_image", idempotency_key, fingerprint)
        if replay is not None and replay.artifact_path and Path(replay.artifact_path).exists():
            return FileResponse(
                replay.artifact_path,
                media_type="image/png",
                headers={"X-Extraction-Receipt": str(replay.id), "X-Extraction-Replayed": "true"},
            )

        asset = _asset_or_404(db, current_user, session_id)
        file_path = resolve_upload_path(str(asset.id), os_uploads_dir)
        final_image_io = render_signature_png(
            file_path,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            color=color,
            threshold=threshold,
        )
        if replay is not None and replay.artifact_path:
            output_path = Path(replay.artifact_path)
        else:
            output_path = os_uploads_dir / f"processed-{asset.id}-{uuid.uuid4()}.png"
        atomic_write(output_path, final_image_io.getvalue())
        if replay is not None:
            return FileResponse(
                str(output_path),
                media_type="image/png",
                headers={"X-Extraction-Receipt": str(replay.id), "X-Extraction-Replayed": "true"},
            )
        event = new_audit_event(
            owner=current_user,
            asset_id=asset.id,
            event_type="process_image",
            idem_key=idempotency_key,
            request_hash_value=fingerprint,
            response={"asset_id": str(asset.id), "media_type": "image/png"},
            artifact_path=output_path,
        )
        committed_event = commit_with_idempotency_recovery(db, current_user, event)
        if committed_event.id != event.id:
            safe_unlink(output_path)
            if committed_event.artifact_path and Path(committed_event.artifact_path).exists():
                return FileResponse(
                    committed_event.artifact_path,
                    media_type="image/png",
                    headers={"X-Extraction-Receipt": str(committed_event.id), "X-Extraction-Replayed": "true"},
                )
        return FileResponse(
            str(output_path),
            media_type="image/png",
            headers={"X-Extraction-Receipt": str(committed_event.id), "X-Extraction-Replayed": "false"},
        )
    except HTTPException:
        if output_path is not None:
            safe_unlink(output_path)
        raise
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extraction asset not found") from exc
    except (ValueError, ExtractionAssetError) as exc:
        raise _http_error(exc) from exc
    except IntegrityError as exc:
        if output_path is not None:
            safe_unlink(output_path)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Processing retry could not be reconciled") from exc
    except Exception as exc:
        if output_path is not None:
            safe_unlink(output_path)
        db.rollback()
        logger.exception("Error processing image: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process image") from exc


def _export_bytes(asset: Image, events: list[ExtractionAuditEvent]) -> bytes:
    source_path = Path(asset.file_path)
    if not source_path.exists():
        raise FileNotFoundError("Extraction asset file not found")
    manifest = {
        "asset": _asset_response(asset),
        "selection": json.loads(asset.selection_json) if asset.selection_json else None,
        "events": [
            {
                "id": str(event.id),
                "event_type": event.event_type,
                "status_code": event.status_code,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            }
            for event in events
        ],
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(source_path, arcname=Path(asset.filename).name)
        archive.writestr("manifest.json", json.dumps(manifest, indent=2, default=str))
    return buffer.getvalue()


@router.post("/assets/{asset_id}/export")
def export_asset(
    asset_id: str,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        idempotency_key = validate_idempotency_key(idempotency_key)
        fingerprint = request_hash({"asset_id": asset_id, "format": "zip"})
        replay = find_replay(db, current_user, "export", idempotency_key, fingerprint)
        if replay is not None and replay.artifact_path and Path(replay.artifact_path).exists():
            return FileResponse(
                replay.artifact_path,
                media_type="application/zip",
                filename=f"signkit-export-{asset_id}.zip",
                headers={"X-Extraction-Receipt": str(replay.id), "X-Extraction-Replayed": "true"},
            )

        asset = _asset_or_404(db, current_user, asset_id)
        events = audit_events_for_asset(db, current_user, asset.id)
        export_path = Path(str(UPLOADS_DIR)) / f"export-{asset.id}-{uuid.uuid4()}.zip"
        if replay is not None and replay.artifact_path:
            export_path = Path(replay.artifact_path)
        atomic_write(export_path, _export_bytes(asset, events))
        if replay is not None:
            return FileResponse(
                str(export_path),
                media_type="application/zip",
                filename=f"signkit-export-{asset_id}.zip",
                headers={"X-Extraction-Receipt": str(replay.id), "X-Extraction-Replayed": "true"},
            )
        event = new_audit_event(
            owner=current_user,
            asset_id=asset.id,
            event_type="export",
            idem_key=idempotency_key,
            request_hash_value=fingerprint,
            response={"asset_id": str(asset.id), "format": "zip"},
            artifact_path=export_path,
        )
        committed_event = commit_with_idempotency_recovery(db, current_user, event)
        if committed_event.id != event.id:
            safe_unlink(export_path)
            export_path = Path(committed_event.artifact_path or export_path)
        return FileResponse(
            str(export_path),
            media_type="application/zip",
            filename=f"signkit-export-{asset_id}.zip",
            headers={"X-Extraction-Receipt": str(committed_event.id), "X-Extraction-Replayed": "false"},
        )
    except HTTPException:
        raise
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extraction asset not found") from exc
    except (ValueError, ExtractionAssetError) as exc:
        raise _http_error(exc) from exc
    except Exception as exc:
        db.rollback()
        logger.exception("Error exporting asset: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to export asset") from exc


@router.delete("/assets/{asset_id}")
def delete_asset(
    asset_id: str,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        idempotency_key = validate_idempotency_key(idempotency_key)
        fingerprint = request_hash({"asset_id": asset_id, "operation": "delete"})
        replay = find_replay(db, current_user, "delete", idempotency_key, fingerprint)
        if replay is not None:
            return _replay_payload(replay)

        asset = _asset_or_404(db, current_user, asset_id)
        events = audit_events_for_asset(db, current_user, asset.id)
        paths = {Path(asset.file_path), REGION_METADATA_DIR / f"{asset.id}.json"}
        paths.update(Path(event.artifact_path) for event in events if event.artifact_path)
        cleanup_status = "complete" if all(safe_unlink(path) for path in paths) else "pending"
        asset.deleted_at = utc_now()
        asset.deleted_by_user_id = current_user.id
        asset.selection_json = None
        asset.file_path = ""
        response = {
            "asset_id": str(asset.id),
            "deleted": True,
            "cleanup_status": cleanup_status,
        }
        event = new_audit_event(
            owner=current_user,
            asset_id=asset.id,
            event_type="delete",
            idem_key=idempotency_key,
            request_hash_value=fingerprint,
            response=response,
        )
        committed_event = commit_with_idempotency_recovery(db, current_user, event)
        if committed_event.id != event.id:
            return _replay_payload(committed_event)
        response["receipt_id"] = str(committed_event.id)
        response["replayed"] = False
        return response
    except HTTPException:
        raise
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extraction asset not found") from exc
    except (ValueError, ExtractionAssetError) as exc:
        raise _http_error(exc) from exc
    except Exception as exc:
        db.rollback()
        logger.exception("Error deleting asset: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete asset") from exc


@router.get("/assets/{asset_id}/audit", response_model=list[ExtractionAuditEventResponse])
def get_asset_audit(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    asset = _asset_or_404(db, current_user, asset_id, include_deleted=True)
    return audit_events_for_asset(db, current_user, asset.id)
