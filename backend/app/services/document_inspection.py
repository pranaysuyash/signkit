"""Local-only document inspection with durable replay receipts."""

from __future__ import annotations

import hashlib
from io import BytesIO
import json
from pathlib import Path
import tempfile

import pikepdf
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import ValidationError

from desktop_app.pdf.document_runtime import DocumentRuntimeError, IsolatedDocumentRuntime

from backend.app.models.user import User
from backend.app.models.workspace import WorkspaceExecution, WorkspaceExecutionEvent
from backend.app.schemas.workspace import DocumentInspectionCandidate


EVENT_TYPE = "document_inspection"
FAILURE_EVENT_TYPE = "document_inspection_failed"
MAX_DOCUMENT_BYTES = 25 * 1024 * 1024


class DocumentInspectionError(ValueError):
    """Raised when a local inspection cannot be safely performed."""


class DocumentInspectionConflict(DocumentInspectionError):
    """Raised when an idempotency key is reused for different document bytes."""


class DocumentInspectionTopologyError(DocumentInspectionError):
    """Raised when a document operation targets a non-local execution."""


def _receipt_payload(
    event: WorkspaceExecutionEvent,
    input_sha256: str,
    pages_processed: int,
    *,
    replayed: bool,
) -> dict[str, object]:
    if not event.result_json:
        raise DocumentInspectionError("Document inspection receipt has no stored result")
    try:
        result = json.loads(event.result_json)
    except json.JSONDecodeError as exc:
        raise DocumentInspectionError("Document inspection receipt is invalid") from exc
    if not isinstance(result, dict):
        raise DocumentInspectionError("Document inspection receipt is invalid")
    result["receipt_id"] = str(event.id)
    result["replayed"] = replayed
    return result


def _request_hash(input_sha256: str, page_index: int) -> str:
    return hashlib.sha256(f"{input_sha256}:{page_index}".encode("ascii")).hexdigest()


def record_inspection_failure(
    db: Session,
    execution: WorkspaceExecution,
    actor: User,
    *,
    idem_key: str | None,
    page_index: int,
    document_bytes: bytes,
    failure_code: str,
    retryable: bool,
    operator_action: str,
) -> None:
    """Append one sanitized, replay-safe failure receipt to the event ledger."""

    input_sha256 = hashlib.sha256(document_bytes).hexdigest() if document_bytes else None
    request_hash = _request_hash(input_sha256, page_index) if input_sha256 else None
    query = db.query(WorkspaceExecutionEvent).filter(
        WorkspaceExecutionEvent.execution_id == execution.id,
        WorkspaceExecutionEvent.actor_user_id == actor.id,
        WorkspaceExecutionEvent.event_type == FAILURE_EVENT_TYPE,
    )
    if idem_key:
        existing = query.filter(WorkspaceExecutionEvent.idem_key == idem_key).first()
    elif request_hash:
        existing = query.filter(WorkspaceExecutionEvent.request_hash == request_hash).first()
    else:
        existing = None
    if existing is not None:
        return

    sequence = (
        db.query(func.coalesce(func.max(WorkspaceExecutionEvent.sequence), 0))
        .filter(WorkspaceExecutionEvent.execution_id == execution.id)
        .scalar()
    )
    result_payload: dict[str, object] = {
        "schema_version": "1",
        "execution_id": str(execution.id),
        "event_type": FAILURE_EVENT_TYPE,
        "outcome": "failed",
        "failure_code": failure_code,
        "retryable": retryable,
        "operator_action": operator_action,
        "page_index": page_index,
    }
    if input_sha256:
        result_payload["input_sha256"] = input_sha256
    event = WorkspaceExecutionEvent(
        execution_id=execution.id,
        sequence=int(sequence) + 1,
        actor_user_id=actor.id,
        event_type=FAILURE_EVENT_TYPE,
        status_from=execution.status,
        status_to=execution.status,
        idem_key=idem_key,
        request_hash=request_hash,
        result_json=json.dumps(result_payload, sort_keys=True),
        summary=f"Local document inspection failed; code={failure_code}; retryable={str(retryable).lower()}",
    )
    db.add(event)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


def _legacy_receipt_matches(event: WorkspaceExecutionEvent, input_sha256: str) -> bool:
    return event.summary == f"Local document inspection completed; input_sha256={input_sha256}"


def _receipt_payload_legacy(
    event: WorkspaceExecutionEvent,
    input_sha256: str,
    pages_processed: int,
    *,
    replayed: bool,
) -> dict[str, object]:
    return {
        "execution_id": event.execution_id,
        "event_type": EVENT_TYPE,
        "runtime_mode": "isolated",
        "retained": False,
        "input_sha256": input_sha256,
        "receipt_id": event.id,
        "page_index": 0,
        "pages_processed": pages_processed,
        "candidates": [],
        "replayed": replayed,
    }


def inspect_local_document(
    db: Session,
    execution: WorkspaceExecution,
    actor: User,
    *,
    filename: str,
    document_bytes: bytes,
    page_index: int,
    idem_key: str | None,
) -> dict[str, object]:
    if execution.topology != "local":
        raise DocumentInspectionTopologyError(
            "Document inspection is available only for local topology executions."
        )
    if not idem_key or len(idem_key) < 6 or len(idem_key) > 80:
        raise DocumentInspectionError("Idempotency-Key is required and must be 6-80 characters")
    if Path(filename).suffix.lower() != ".pdf":
        raise DocumentInspectionError("Only PDF documents are accepted for local inspection")
    if not document_bytes or len(document_bytes) > MAX_DOCUMENT_BYTES:
        raise DocumentInspectionError("PDF payload is empty or exceeds the 25 MB limit")
    if not document_bytes.startswith(b"%PDF-"):
        raise DocumentInspectionError("Invalid PDF payload")

    input_sha256 = hashlib.sha256(document_bytes).hexdigest()
    request_hash = _request_hash(input_sha256, page_index)
    replay = (
        db.query(WorkspaceExecutionEvent)
        .filter(
            WorkspaceExecutionEvent.execution_id == execution.id,
            WorkspaceExecutionEvent.actor_user_id == actor.id,
            WorkspaceExecutionEvent.event_type == EVENT_TYPE,
            WorkspaceExecutionEvent.idem_key == idem_key,
        )
        .first()
    )
    if replay is not None:
        if replay.request_hash and replay.request_hash != request_hash:
            raise DocumentInspectionConflict(
                "Idempotency-Key was already used for different document bytes"
            )
        if replay.request_hash is None and not _legacy_receipt_matches(replay, input_sha256):
            raise DocumentInspectionConflict(
                "Idempotency-Key was already used for different document bytes"
            )
        return _receipt_payload(replay, input_sha256, 1, replayed=True)

    try:
        with pikepdf.Pdf.open(BytesIO(document_bytes)) as pdf:
            page_count = len(pdf.pages)
    except Exception as exc:
        raise DocumentInspectionError("Invalid or unreadable PDF payload") from exc

    if page_index < 0 or page_index >= page_count:
        raise DocumentInspectionError(f"page_index must be between 0 and {page_count - 1}")

    with tempfile.TemporaryDirectory(prefix="signkit-local-pdf-") as directory:
        pdf_path = Path(directory) / "input.pdf"
        pdf_path.write_bytes(document_bytes)
        try:
            candidates = IsolatedDocumentRuntime(timeout_seconds=30).detect_page(
                str(pdf_path), page_index
            )
        except DocumentRuntimeError as exc:
            raise DocumentInspectionError("Local PDF worker could not inspect the document") from exc

    if len(candidates) > 12 or any(not isinstance(candidate, dict) for candidate in candidates):
        raise DocumentInspectionError("Worker returned an invalid candidate result")
    try:
        normalized_candidates = [
            DocumentInspectionCandidate.model_validate(candidate).model_dump(mode="json")
            for candidate in candidates
        ]
    except ValidationError as exc:
        raise DocumentInspectionError("Worker returned an invalid candidate result") from exc
    result_payload = {
        "execution_id": str(execution.id),
        "event_type": EVENT_TYPE,
        "runtime_mode": "isolated",
        "retained": False,
        "input_sha256": input_sha256,
        "page_index": page_index,
        "pages_processed": 1,
        "candidates": normalized_candidates,
    }

    sequence = (
        db.query(func.coalesce(func.max(WorkspaceExecutionEvent.sequence), 0))
        .filter(WorkspaceExecutionEvent.execution_id == execution.id)
        .scalar()
    )
    event = WorkspaceExecutionEvent(
        execution_id=execution.id,
        sequence=int(sequence) + 1,
        actor_user_id=actor.id,
        event_type=EVENT_TYPE,
        status_from=execution.status,
        status_to=execution.status,
        idem_key=idem_key,
        request_hash=request_hash,
        result_json=json.dumps(result_payload, sort_keys=True),
        summary=(
            f"Local document inspection completed; input_sha256={input_sha256}; "
            f"page={page_index}; candidates={len(normalized_candidates)}; worker=isolated; retained=false"
        ),
    )
    db.add(event)
    try:
        db.commit()
        db.refresh(event)
    except IntegrityError:
        db.rollback()
        replay = (
            db.query(WorkspaceExecutionEvent)
            .filter(
                WorkspaceExecutionEvent.execution_id == execution.id,
                WorkspaceExecutionEvent.actor_user_id == actor.id,
                WorkspaceExecutionEvent.event_type == EVENT_TYPE,
                WorkspaceExecutionEvent.idem_key == idem_key,
            )
            .first()
        )
        if replay is None or (
            replay.request_hash and replay.request_hash != request_hash
        ) or (replay.request_hash is None and not _legacy_receipt_matches(replay, input_sha256)):
            raise DocumentInspectionConflict("Document inspection retry could not be reconciled")
        return _receipt_payload(replay, input_sha256, 1, replayed=True)
    return _receipt_payload(event, input_sha256, 1, replayed=False)
