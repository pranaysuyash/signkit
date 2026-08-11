"""Template persistence for reusable PDF signature placements."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from desktop_app.workflows.models import RecipeStatus, SignatureFieldBinding


APP_DIR = os.path.join(os.path.expanduser("~"), ".signature_extractor")
TEMPLATES_FILE = os.path.join(APP_DIR, "pdf_templates.json")
TEMPLATE_STORE_VERSION = 2


def _utc_now_iso() -> str:
    """Return canonical UTC timestamp for persisted payloads."""
    return datetime.now(timezone.utc).isoformat()


def _coerce_status(value: Any) -> str:
    if isinstance(value, str) and value in {status.value for status in RecipeStatus}:
        return value
    return RecipeStatus.DRAFT.value


def _normalize_optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "y", "on"}
    return default


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_optional_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clamp_ratio(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass
class SignaturePlacementTemplate:
    """Reusable signature placement for one or many bindings."""

    template_id: str
    name: str
    signature_path: str
    page_index: int
    x_ratio: float
    y_ratio: float
    width_ratio: float
    height_ratio: float
    use_field_anchor: bool = False
    field_type: Optional[str] = None
    field_label: Optional[str] = None
    field_confidence: Optional[float] = None
    anchor_x_ratio: Optional[float] = None
    anchor_y_ratio: Optional[float] = None
    source_pdf_name: Optional[str] = None
    source_pdf_path: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    status: str = RecipeStatus.DRAFT.value
    version: int = TEMPLATE_STORE_VERSION
    recipe_id: Optional[str] = None
    migrated_from_legacy: bool = False
    field_bindings: List[SignatureFieldBinding] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.version is None:
            self.version = TEMPLATE_STORE_VERSION


def _coerce_signature_field_binding(payload: Any) -> Optional[SignatureFieldBinding]:
    if not isinstance(payload, dict):
        return None
    return SignatureFieldBinding.from_legacy_payload(payload)


def _legacy_binding_from_template_payload(
    payload: Dict[str, Any]
) -> SignatureFieldBinding:
    return SignatureFieldBinding.from_legacy_values(
        signature_path=str(payload.get("signature_path") or ""),
        page_index=_coerce_int(payload.get("page_index"), 0),
        x_ratio=_coerce_float(payload.get("x_ratio"), 0.0),
        y_ratio=_coerce_float(payload.get("y_ratio"), 0.0),
        width_ratio=_coerce_float(payload.get("width_ratio"), 0.0),
        height_ratio=_coerce_float(payload.get("height_ratio"), 0.0),
        use_field_anchor=_coerce_bool(payload.get("use_field_anchor"), False),
        field_type=_normalize_optional_text(payload.get("field_type")),
        field_label=_normalize_optional_text(payload.get("field_label")),
        field_confidence=_coerce_optional_float(payload.get("field_confidence")),
        anchor_x_ratio=_coerce_optional_float(payload.get("anchor_x_ratio")),
        anchor_y_ratio=_coerce_optional_float(payload.get("anchor_y_ratio")),
        source_pdf_name=_normalize_optional_text(payload.get("source_pdf_name")),
        source_pdf_path=_normalize_optional_text(payload.get("source_pdf_path")),
    )


def _sync_legacy_fields(template: SignaturePlacementTemplate) -> None:
    if not template.field_bindings:
        return
    primary = template.field_bindings[0]
    template.signature_path = primary.signature_asset_ref
    template.page_index = primary.page_index
    template.x_ratio = _clamp_ratio(primary.x_ratio)
    template.y_ratio = _clamp_ratio(primary.y_ratio)
    template.width_ratio = _clamp_ratio(primary.width_ratio)
    template.height_ratio = _clamp_ratio(primary.height_ratio)
    template.use_field_anchor = bool(primary.use_field_anchor)
    template.field_type = primary.field_type
    template.field_label = primary.field_label
    template.field_confidence = primary.field_confidence
    template.anchor_x_ratio = primary.anchor_x_ratio
    template.anchor_y_ratio = primary.anchor_y_ratio
    template.source_pdf_name = primary.source_pdf_name
    template.source_pdf_path = primary.source_pdf_path


def _as_template(payload: Dict[str, Any]) -> SignaturePlacementTemplate:
    """Build a strict template from possibly older payloads."""
    raw_bindings = payload.get("field_bindings")
    bindings: List[SignatureFieldBinding] = []
    if isinstance(raw_bindings, list):
        for raw in raw_bindings:
            binding = _coerce_signature_field_binding(raw)
            if binding is not None:
                bindings.append(binding)

    if not bindings:
        bindings.append(_legacy_binding_from_template_payload(payload))

    template = SignaturePlacementTemplate(
        template_id=str(payload.get("template_id") or uuid.uuid4().hex),
        name=str(payload.get("name") or "Unnamed Template"),
        signature_path="",
        page_index=0,
        x_ratio=0.0,
        y_ratio=0.0,
        width_ratio=0.0,
        height_ratio=0.0,
        use_field_anchor=False,
        field_type=None,
        field_label=None,
        field_confidence=None,
        anchor_x_ratio=None,
        anchor_y_ratio=None,
        source_pdf_name=None,
        source_pdf_path=None,
        created_at=str(payload.get("created_at") or _utc_now_iso()),
        updated_at=str(payload.get("updated_at") or _utc_now_iso()),
        status=_coerce_status(payload.get("status")),
        version=int(payload.get("version") or TEMPLATE_STORE_VERSION),
        recipe_id=_normalize_optional_text(payload.get("recipe_id")),
        migrated_from_legacy=bool(payload.get("migrated_from_legacy", False)),
        field_bindings=bindings,
    )
    _sync_legacy_fields(template)
    return template


def ensure_templates_dir() -> str:
    """Ensure template directory exists."""
    Path(APP_DIR).mkdir(parents=True, exist_ok=True)
    return APP_DIR


def _load_payload() -> Dict[str, Any]:
    """Load raw JSON payload safely."""
    ensure_templates_dir()
    if not os.path.exists(TEMPLATES_FILE):
        return {"version": TEMPLATE_STORE_VERSION, "templates": []}

    try:
        with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception:
        return {"version": TEMPLATE_STORE_VERSION, "templates": []}

    if not isinstance(payload, dict):
        return {"version": TEMPLATE_STORE_VERSION, "templates": []}

    payload.setdefault("version", TEMPLATE_STORE_VERSION)
    payload.setdefault("templates", [])
    return payload


def _write_payload(payload: Dict[str, Any]) -> None:
    """Write payload and fail softly in best-effort mode."""
    ensure_templates_dir()
    try:
        with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
    except Exception:
        return


def _safe_templates_payload() -> Dict[str, Any]:
    payload = _load_payload()
    templates = payload.get("templates")
    if not isinstance(templates, list):
        payload["templates"] = []
    return payload


def list_templates() -> List[SignaturePlacementTemplate]:
    """Return saved templates in newest-first order."""
    payload = _safe_templates_payload()
    templates = []
    for item in payload.get("templates", []):
        if not isinstance(item, dict):
            continue
        templates.append(_as_template(item))
    templates.sort(key=lambda item: item.updated_at, reverse=True)
    return templates


def get_template(template_id: str) -> Optional[SignaturePlacementTemplate]:
    """Return a template by id."""
    for template in list_templates():
        if template.template_id == template_id:
            return template
    return None


def _materialize_field_bindings(template: SignaturePlacementTemplate) -> List[SignatureFieldBinding]:
    if template.field_bindings:
        _sync_legacy_fields(template)
        return template.field_bindings
    return [
        SignatureFieldBinding.from_legacy_values(
            signature_path=template.signature_path,
            page_index=template.page_index,
            x_ratio=template.x_ratio,
            y_ratio=template.y_ratio,
            width_ratio=template.width_ratio,
            height_ratio=template.height_ratio,
            use_field_anchor=template.use_field_anchor,
            field_type=template.field_type,
            field_label=template.field_label,
            field_confidence=template.field_confidence,
            anchor_x_ratio=template.anchor_x_ratio,
            anchor_y_ratio=template.anchor_y_ratio,
            source_pdf_name=template.source_pdf_name,
            source_pdf_path=template.source_pdf_path,
        )
    ]


def save_template(template: SignaturePlacementTemplate) -> SignaturePlacementTemplate:
    """Save or update a template."""
    payload = _safe_templates_payload()
    now = _utc_now_iso()
    template.version = TEMPLATE_STORE_VERSION
    template.status = _coerce_status(template.status)

    bindings = _materialize_field_bindings(template)
    template.field_bindings = bindings
    _sync_legacy_fields(template)

    to_save = asdict(template)
    to_save["created_at"] = to_save.get("created_at") or now
    to_save["updated_at"] = now
    to_save["status"] = template.status
    to_save["version"] = TEMPLATE_STORE_VERSION
    to_save["field_bindings"] = [binding.to_payload() for binding in bindings]

    if not to_save["created_at"]:
        to_save["created_at"] = now
    if not to_save.get("template_id"):
        to_save["template_id"] = uuid.uuid4().hex
    to_save["template_id"] = str(to_save["template_id"])

    exists = False
    entries = payload["templates"]
    for index, item in enumerate(entries):
        if isinstance(item, dict) and item.get("template_id") == to_save["template_id"]:
            entries[index] = to_save
            exists = True
            break
    if not exists:
        entries.append(to_save)

    _write_payload(payload)
    return _as_template(to_save)


def create_template(
    *,
    signature_path: str,
    page_index: int,
    x_ratio: float,
    y_ratio: float,
    width_ratio: float,
    height_ratio: float,
    name: str,
    use_field_anchor: bool = False,
    field_type: Optional[str] = None,
    field_label: Optional[str] = None,
    field_confidence: Optional[float] = None,
    anchor_x_ratio: Optional[float] = None,
    anchor_y_ratio: Optional[float] = None,
    source_pdf_path: Optional[str] = None,
    source_pdf_name: Optional[str] = None,
) -> SignaturePlacementTemplate:
    """Create and persist a placement template."""
    template = SignaturePlacementTemplate(
        template_id=uuid.uuid4().hex,
        name=name.strip() or "Signature Template",
        signature_path=signature_path,
        page_index=_coerce_int(page_index, 0),
        x_ratio=_clamp_ratio(x_ratio),
        y_ratio=_clamp_ratio(y_ratio),
        width_ratio=_clamp_ratio(width_ratio),
        height_ratio=_clamp_ratio(height_ratio),
        use_field_anchor=_coerce_bool(use_field_anchor, False),
        field_type=_normalize_optional_text(field_type),
        field_label=_normalize_optional_text(field_label),
        field_confidence=_coerce_optional_float(field_confidence),
        anchor_x_ratio=_coerce_optional_float(anchor_x_ratio),
        anchor_y_ratio=_coerce_optional_float(anchor_y_ratio),
    )
    template.source_pdf_path = _normalize_optional_text(source_pdf_path)
    template.source_pdf_name = _normalize_optional_text(source_pdf_name)
    template.version = TEMPLATE_STORE_VERSION
    template.created_at = _utc_now_iso()
    template.updated_at = template.created_at
    template.field_bindings = [
        SignatureFieldBinding.from_legacy_values(
            signature_path=signature_path,
            page_index=template.page_index,
            x_ratio=template.x_ratio,
            y_ratio=template.y_ratio,
            width_ratio=template.width_ratio,
            height_ratio=template.height_ratio,
            use_field_anchor=template.use_field_anchor,
            field_type=template.field_type,
            field_label=template.field_label,
            field_confidence=template.field_confidence,
            anchor_x_ratio=template.anchor_x_ratio,
            anchor_y_ratio=template.anchor_y_ratio,
            source_pdf_name=template.source_pdf_name,
            source_pdf_path=template.source_pdf_path,
        )
    ]
    return save_template(template)


def delete_template(template_id: str) -> bool:
    """Delete a template by id."""
    payload = _safe_templates_payload()
    before = len(payload["templates"])
    payload["templates"] = [
        item for item in payload["templates"]
        if not (isinstance(item, dict) and item.get("template_id") == template_id)
    ]
    deleted = len(payload["templates"]) < before
    if deleted:
        _write_payload(payload)
    return deleted
