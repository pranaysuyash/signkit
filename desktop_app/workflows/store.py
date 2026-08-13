"""Persistent store for controlled workflow entities.

This module is the local persistence foundation for the folder-driven signing
automation workstream. It stores recipes, grants, jobs, and job events in one
durable JSON document under the same app storage root used by other desktop stores.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from typing import Any, Dict, List, Optional

from desktop_app.workflows.models import (
    ControlledSigningRecipe,
    ExecutionGrant,
    FolderConfig,
    WorkflowJob,
    WorkflowJobEvent,
    WorkflowState,
    RecipeStatus,
)


_configured_data_dir = os.environ.get("SIGNKIT_DATA_DIR")
if _configured_data_dir:
    APP_DIR = Path(_configured_data_dir).expanduser().resolve() / "workflow"
else:
    APP_DIR = Path.home() / ".signature_extractor"

_configured_store_file = os.environ.get("SIGNKIT_WORKFLOW_STORE_FILE")
WORKFLOW_STORE_FILE = (
    Path(_configured_store_file).expanduser().resolve()
    if _configured_store_file
    else APP_DIR / "workflow_store.json"
)
WORKFLOW_STORE_VERSION = 1

_store_process_lock = threading.RLock()
_store_lock_state = threading.local()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_list(value: Any) -> List[Dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _coerce_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _coerce_str(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _coerce_state(value: Any) -> str:
    if isinstance(value, WorkflowState):
        return value.value
    return _coerce_str(value)


def _ensure_dir() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def workflow_store_lock():
    """Serialize workflow mutations across threads and companion processes."""

    depth = getattr(_store_lock_state, "depth", 0)
    if depth:
        _store_lock_state.depth = depth + 1
        try:
            yield
        finally:
            _store_lock_state.depth = depth
        return

    _store_process_lock.acquire()
    handle = None
    try:
        _ensure_dir()
        lock_path = WORKFLOW_STORE_FILE.with_suffix(WORKFLOW_STORE_FILE.suffix + ".lock")
        handle = lock_path.open("a+", encoding="utf-8")
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            handle.write("0")
            handle.flush()
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        _store_lock_state.depth = 1
        _store_lock_state.handle = handle
        yield
    finally:
        try:
            if handle is not None:
                if os.name == "nt":
                    import msvcrt

                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                handle.close()
        finally:
            _store_lock_state.depth = 0
            _store_lock_state.handle = None
            _store_process_lock.release()


def _load_payload() -> Dict[str, Any]:
    _ensure_dir()
    if not WORKFLOW_STORE_FILE.exists():
        return {
            "version": WORKFLOW_STORE_VERSION,
            "recipes": [],
            "grants": [],
            "jobs": [],
            "events": [],
            "retry_receipts": [],
        }
    try:
        with WORKFLOW_STORE_FILE.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return {
            "version": WORKFLOW_STORE_VERSION,
            "recipes": [],
            "grants": [],
            "jobs": [],
            "events": [],
            "retry_receipts": [],
        }
    if not isinstance(payload, dict):
        return {
            "version": WORKFLOW_STORE_VERSION,
            "recipes": [],
            "grants": [],
            "jobs": [],
            "events": [],
            "retry_receipts": [],
        }

    payload.setdefault("version", WORKFLOW_STORE_VERSION)
    payload.setdefault("recipes", [])
    payload.setdefault("grants", [])
    payload.setdefault("jobs", [])
    payload.setdefault("events", [])
    payload.setdefault("retry_receipts", [])
    return payload


def _write_payload(payload: Dict[str, Any]) -> None:
    _ensure_dir()
    tmp_path = WORKFLOW_STORE_FILE.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
    os.replace(tmp_path, WORKFLOW_STORE_FILE)


def _safe_payload() -> Dict[str, Any]:
    payload = _load_payload()
    payload["recipes"] = _coerce_list(payload.get("recipes"))
    payload["grants"] = _coerce_list(payload.get("grants"))
    payload["jobs"] = _coerce_list(payload.get("jobs"))
    payload["events"] = _coerce_list(payload.get("events"))
    payload["retry_receipts"] = _coerce_list(payload.get("retry_receipts"))
    return payload


def _serialize_recipe(recipe: ControlledSigningRecipe) -> Dict[str, Any]:
    payload = recipe.to_payload()
    payload["updated_at"] = _utc_now_iso()
    payload["content_hash"] = _compute_recipe_hash(payload)
    return payload


def _compute_recipe_hash(payload: Dict[str, Any]) -> str:
    """Stable hash for recipe content to support idempotent migration and updates."""
    canonical = {
        "name": _coerce_str(payload.get("name")),
        "document_matcher": _coerce_dict(payload.get("document_matcher")),
        "input_folder": _coerce_dict(payload.get("input_folder")),
        "output_folder": _coerce_dict(payload.get("output_folder")),
        "review_folder": _coerce_dict(payload.get("review_folder")),
        "authorization_policy": _coerce_dict(payload.get("authorization_policy")),
        "field_bindings": _coerce_list(payload.get("field_bindings")),
        "status": _coerce_str(payload.get("status")),
        "version": payload.get("version"),
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _find_index(items: List[Dict[str, Any]], item_id: str, id_field: str) -> int:
    for index, item in enumerate(items):
        if item.get(id_field) == item_id:
            return index
    return -1


def _upsert(items: List[Dict[str, Any]], payload: Dict[str, Any], key_field: str) -> None:
    index = _find_index(items, _coerce_str(payload.get(key_field)), key_field)
    if index >= 0:
        items[index] = payload
    else:
        items.append(payload)


def list_recipes(*, status: Optional[str] = None) -> List[ControlledSigningRecipe]:
    """Return stored recipes sorted by most recently updated first."""
    payload = _safe_payload()
    raw_items = payload["recipes"]
    recipes = []
    for item in raw_items:
        recipe = ControlledSigningRecipe.from_payload(item)
        if status and recipe.status != status:
            continue
        recipes.append(recipe)
    recipes.sort(key=lambda item: item.updated_at, reverse=True)
    return recipes


def get_recipe(recipe_id: str) -> Optional[ControlledSigningRecipe]:
    if not recipe_id:
        return None
    payload = _safe_payload()
    for raw in payload["recipes"]:
        if raw.get("recipe_id") == recipe_id:
            return ControlledSigningRecipe.from_payload(raw)
    return None


def save_recipe(recipe: ControlledSigningRecipe) -> ControlledSigningRecipe:
    """Create/update a recipe and persist store state."""
    payload = _safe_payload()
    saved = recipe
    now = _utc_now_iso()

    if not recipe.created_at:
        saved = replace(recipe, created_at=now)
    if not saved.updated_at:
        saved = replace(saved, updated_at=now)

    saved_dict = _serialize_recipe(saved)
    _upsert(payload["recipes"], saved_dict, "recipe_id")

    _write_payload(payload)
    return ControlledSigningRecipe.from_payload(saved_dict)


def delete_recipe(recipe_id: str) -> bool:
    payload = _safe_payload()
    before = len(payload["recipes"])
    payload["recipes"] = [item for item in payload["recipes"] if item.get("recipe_id") != recipe_id]
    if len(payload["recipes"]) == before:
        return False

    # Cascade recipe-linked grants/jobs/events.
    recipe_jobs = _jobs_for_recipe(payload["jobs"], recipe_id)
    job_ids = {job_id for job_id in recipe_jobs}
    payload["grants"] = [item for item in payload["grants"] if item.get("recipe_id") != recipe_id]
    payload["jobs"] = [item for item in payload["jobs"] if item.get("recipe_id") != recipe_id]
    payload["events"] = [item for item in payload["events"] if item.get("job_id") not in job_ids]

    _write_payload(payload)
    return True


def _jobs_for_recipe(jobs_payload: List[Dict[str, Any]], recipe_id: str) -> List[str]:
    return [item.get("job_id") for item in jobs_payload if item.get("recipe_id") == recipe_id and item.get("job_id")]


def list_grants(
    *,
    recipe_id: Optional[str] = None,
    active_only: bool = False,
    now_ts: Optional[str] = None,
) -> List[ExecutionGrant]:
    payload = _safe_payload()
    result: List[ExecutionGrant] = []
    for raw in payload["grants"]:
        grant = ExecutionGrant.from_payload(raw)
        if recipe_id and grant.recipe_id != recipe_id:
            continue
        if active_only and not grant.is_active:
            continue
        if now_ts and not is_grant_valid(grant, now_ts=now_ts):
            continue
        result.append(grant)
    result.sort(key=lambda item: item.updated_at, reverse=True)
    return result


def get_grant(grant_id: str) -> Optional[ExecutionGrant]:
    if not grant_id:
        return None
    payload = _safe_payload()
    for raw in payload["grants"]:
        if raw.get("grant_id") == grant_id:
            return ExecutionGrant.from_payload(raw)
    return None


def save_grant(grant: ExecutionGrant) -> ExecutionGrant:
    payload = _safe_payload()
    now = _utc_now_iso()

    saved = grant
    if not grant.created_at:
        saved = replace(grant, created_at=now)
    if not saved.updated_at:
        saved = replace(saved, updated_at=now)

    saved_dict = saved.to_payload()
    saved_dict["updated_at"] = now
    _upsert(payload["grants"], saved_dict, "grant_id")
    _write_payload(payload)
    return ExecutionGrant.from_payload(saved_dict)


def revoke_grant(grant_id: str, *, reason: str, actor: Optional[str] = None) -> Optional[ExecutionGrant]:
    current = get_grant(grant_id)
    if current is None:
        return None
    payload = _safe_payload()
    revoked = replace(
        current,
        is_active=False,
        revoked_at=_utc_now_iso(),
        revoked_reason=reason.strip() if reason else "revoked",
        revoked_by=actor,
    )
    _upsert(payload["grants"], revoked.to_payload(), "grant_id")
    _write_payload(payload)
    return revoked


def is_grant_valid(grant: ExecutionGrant, now_ts: Optional[str] = None) -> bool:
    if not grant.is_active:
        return False
    if grant.revoked_at:
        return False
    if grant.expires_at is None:
        return True
    try:
        expiry = datetime.fromisoformat(grant.expires_at.replace("Z", "+00:00"))
    except Exception:
        return False
    now = datetime.fromisoformat((now_ts or _utc_now_iso()).replace("Z", "+00:00"))
    return now <= expiry


def list_jobs(
    recipe_id: Optional[str] = None,
    state: Optional[str] = None,
    grant_id: Optional[str] = None,
) -> List[WorkflowJob]:
    payload = _safe_payload()
    result: List[WorkflowJob] = []
    normalized_state = _coerce_state(state) if state else None
    for raw in payload["jobs"]:
        job = WorkflowJob.from_payload(raw)
        if recipe_id and job.recipe_id != recipe_id:
            continue
        if grant_id and job.grant_id != grant_id:
            continue
        if normalized_state and job.state.value != normalized_state:
            continue
        result.append(job)
    result.sort(key=lambda item: item.created_at, reverse=True)
    return result


def get_job(job_id: str) -> Optional[WorkflowJob]:
    if not job_id:
        return None
    payload = _safe_payload()
    for raw in payload["jobs"]:
        if raw.get("job_id") == job_id:
            return WorkflowJob.from_payload(raw)
    return None


def get_retry_receipt(job_id: str, idempotency_key: str) -> Optional[Dict[str, Any]]:
    """Return the durable result for one local retry request, if recorded."""

    if not job_id or not idempotency_key:
        return None
    payload = _safe_payload()
    for receipt in payload["retry_receipts"]:
        if (
            receipt.get("job_id") == job_id
            and receipt.get("idempotency_key") == idempotency_key
            and isinstance(receipt.get("job"), dict)
        ):
            return dict(receipt)
    return None


def save_retry_receipt(job: WorkflowJob, idempotency_key: str) -> Dict[str, Any]:
    """Persist one retry result so a repeated request cannot execute twice."""

    if not job.job_id:
        raise ValueError("job_id is required")
    if not idempotency_key:
        raise ValueError("idempotency_key is required")
    with workflow_store_lock():
        payload = _safe_payload()
        receipt = {
            "job_id": job.job_id,
            "idempotency_key": idempotency_key,
            "job": job.to_payload(),
            "recorded_at": _utc_now_iso(),
        }
        existing = next(
            (
                item
                for item in payload["retry_receipts"]
                if item.get("job_id") == job.job_id
                and item.get("idempotency_key") == idempotency_key
            ),
            None,
        )
        if existing is None:
            payload["retry_receipts"].append(receipt)
        else:
            existing.update(receipt)
        _write_payload(payload)
        return dict(receipt)


def save_job(job: WorkflowJob) -> WorkflowJob:
    payload = _safe_payload()
    now = _utc_now_iso()
    saved = job
    if not job.created_at:
        saved = replace(job, created_at=now)
    saved = replace(saved, updated_at=now)
    saved_dict = saved.to_payload()
    _upsert(payload["jobs"], saved_dict, "job_id")
    _write_payload(payload)
    return WorkflowJob.from_payload(saved_dict)


def append_job_event(
    *,
    event_id: Optional[str],
    job_id: str,
    state_from: Optional[str],
    state_to: Optional[Any],
    actor: str,
    code: str,
    message: Optional[str] = None,
) -> WorkflowJobEvent:
    payload = _safe_payload()
    if not job_id:
        raise ValueError("job_id is required")
    if get_job(job_id) is None:
        raise ValueError("job_id does not exist")
    event = WorkflowJobEvent(
        event_id=_coerce_str(event_id) or uuid4().hex,
        job_id=job_id,
        state_from=_coerce_str(state_from) or None,
        state_to=_coerce_state(state_to),
        actor=actor or "system",
        code=_coerce_str(code),
        message=(message.strip() if isinstance(message, str) else None),
        occurred_at=_utc_now_iso(),
    )
    payload["events"].append(event.to_payload())
    _write_payload(payload)
    return event


def list_events(job_id: Optional[str] = None) -> List[WorkflowJobEvent]:
    payload = _safe_payload()
    result: List[WorkflowJobEvent] = []
    for raw in payload["events"]:
        event = WorkflowJobEvent.from_payload(raw)
        if job_id and event.job_id != job_id:
            continue
        result.append(event)
    result.sort(key=lambda item: item.occurred_at)
    return result


def migrate_legacy_templates() -> int:
    """
    One-shot migration from older template store into recipes.

    Returns number of recipes imported.
    """
    from desktop_app.pdf import template_store

    store = _safe_payload()
    if store["recipes"]:
        return 0

    templates = template_store.list_templates()
    imported = 0
    for template in templates:
        if not template.field_bindings:
            continue
        recipe = ControlledSigningRecipe.new(
            recipe_id=template.template_id,
            name=template.name,
            field_bindings=template.field_bindings,
            status=template.status if template.status in {s.value for s in RecipeStatus} else RecipeStatus.DRAFT.value,
            input_folder=FolderConfig(
                folder_id=template.template_id + "-in",
                path="",
                recursive=False,
                require_stable_size=True,
            ),
            output_folder=FolderConfig(
                folder_id=template.template_id + "-out",
                path="",
                recursive=False,
                require_stable_size=True,
            ),
            migration_source_legacy=True,
            content_hash=str(template.version) if hasattr(template, "version") else "",
            document_matcher={"kind": "exact"},
        )
        recipe = replace(
            recipe,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )
        save_recipe(recipe)
        imported += 1
    return imported


def clear_store() -> None:
    """Test helper to reset the store file."""
    payload = {
        "version": WORKFLOW_STORE_VERSION,
        "recipes": [],
        "grants": [],
        "jobs": [],
        "events": [],
        "retry_receipts": [],
    }
    with workflow_store_lock():
        _write_payload(payload)
