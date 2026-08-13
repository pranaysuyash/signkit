"""Canonical workflow data models for template/recipe migration and future engine stages."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional
from uuid import uuid4


class RecipeStatus(str, Enum):
    """Lifecycle status for an executable recipe or template artifact."""

    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class FieldKind(str, Enum):
    """Kind of field binding supported by the recipe model."""

    SIGNATURE = "signature"
    INITIALS = "initials"
    DATE = "date"
    TEXT = "text"


@dataclass(frozen=True)
class SignatureFieldBinding:
    """One placement/asset binding inside a controlled workflow recipe."""

    binding_id: str
    signature_asset_ref: str
    page_index: int
    x_ratio: float
    y_ratio: float
    width_ratio: float
    height_ratio: float
    use_field_anchor: bool = False
    field_kind: str = FieldKind.SIGNATURE.value
    field_type: Optional[str] = None
    field_label: Optional[str] = None
    field_confidence: Optional[float] = None
    anchor_x_ratio: Optional[float] = None
    anchor_y_ratio: Optional[float] = None
    source_pdf_name: Optional[str] = None
    source_pdf_path: Optional[str] = None

    @staticmethod
    def from_legacy_payload(payload: Dict[str, Any]) -> "SignatureFieldBinding":
        if not isinstance(payload, dict):
            payload = {}
        return SignatureFieldBinding(
            binding_id=str(payload.get("binding_id") or uuid4().hex),
            signature_asset_ref=str(payload.get("signature_path") or payload.get("signature_asset_ref") or ""),
            page_index=int(payload.get("page_index") or 0),
            x_ratio=float(payload.get("x_ratio") or 0.0),
            y_ratio=float(payload.get("y_ratio") or 0.0),
            width_ratio=float(payload.get("width_ratio") or 0.0),
            height_ratio=float(payload.get("height_ratio") or 0.0),
            use_field_anchor=bool(payload.get("use_field_anchor") or False),
            field_kind=str(payload.get("field_kind") or payload.get("field_type") or FieldKind.SIGNATURE.value),
            field_type=(
                str(payload.get("field_type")).strip()
                if isinstance(payload.get("field_type"), str) and str(payload.get("field_type")).strip()
                else None
            ),
            field_label=(
                str(payload.get("field_label")).strip()
                if isinstance(payload.get("field_label"), str) and str(payload.get("field_label")).strip()
                else None
            ),
            field_confidence=_coerce_optional_float(payload.get("field_confidence")),
            anchor_x_ratio=_coerce_optional_float(payload.get("anchor_x_ratio")),
            anchor_y_ratio=_coerce_optional_float(payload.get("anchor_y_ratio")),
            source_pdf_name=(
                str(payload.get("source_pdf_name")).strip()
                if isinstance(payload.get("source_pdf_name"), str) and str(payload.get("source_pdf_name")).strip()
                else None
            ),
            source_pdf_path=(
                str(payload.get("source_pdf_path")).strip()
                if isinstance(payload.get("source_pdf_path"), str) and str(payload.get("source_pdf_path")).strip()
                else None
            ),
        )

    @staticmethod
    def from_legacy_values(
        *,
        signature_path: str,
        page_index: int,
        x_ratio: float,
        y_ratio: float,
        width_ratio: float,
        height_ratio: float,
        use_field_anchor: bool = False,
        field_type: Optional[str] = None,
        field_label: Optional[str] = None,
        field_confidence: Optional[float] = None,
        anchor_x_ratio: Optional[float] = None,
        anchor_y_ratio: Optional[float] = None,
        source_pdf_name: Optional[str] = None,
        source_pdf_path: Optional[str] = None,
    ) -> "SignatureFieldBinding":
        return SignatureFieldBinding(
            binding_id=uuid4().hex,
            signature_asset_ref=str(signature_path),
            page_index=int(page_index),
            x_ratio=float(x_ratio),
            y_ratio=float(y_ratio),
            width_ratio=float(width_ratio),
            height_ratio=float(height_ratio),
            use_field_anchor=bool(use_field_anchor),
            field_kind=FieldKind.SIGNATURE.value,
            field_type=_normalize_optional_text(field_type),
            field_label=_normalize_optional_text(field_label),
            field_confidence=_coerce_optional_float(field_confidence),
            anchor_x_ratio=_coerce_optional_float(anchor_x_ratio),
            anchor_y_ratio=_coerce_optional_float(anchor_y_ratio),
            source_pdf_name=_normalize_optional_text(source_pdf_name),
            source_pdf_path=_normalize_optional_text(source_pdf_path),
        )

    def to_payload(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["field_kind"] = self.field_kind
        return payload


@dataclass(frozen=True)
class ControlledSigningRecipe:
    """Versioned, deterministic recipe payload used by the workflow engine."""

    recipe_id: str
    name: str
    document_matcher: Dict[str, Any] = field(default_factory=lambda: {"kind": "exact"})
    version: int = 1
    status: str = RecipeStatus.DRAFT.value
    input_folder: "FolderConfig" = field(
        default_factory=lambda: FolderConfig(
            folder_id=uuid4().hex, path="", recursive=False, require_stable_size=True
        )
    )
    output_folder: "FolderConfig" = field(
        default_factory=lambda: FolderConfig(
            folder_id=uuid4().hex, path="", recursive=False, require_stable_size=True
        )
    )
    review_folder: Optional["FolderConfig"] = None
    authorization_policy: Dict[str, Any] = field(default_factory=lambda: {"require_active_grant": True})
    field_bindings: List[SignatureFieldBinding] = field(default_factory=list)
    created_by: str = ""
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    migration_source_legacy: bool = False
    content_hash: str = ""

    @staticmethod
    def new(
        *,
        recipe_id: Optional[str],
        name: str,
        status: str = RecipeStatus.DRAFT.value,
        document_matcher: Optional[Dict[str, Any]] = None,
        input_folder: Optional["FolderConfig"] = None,
        output_folder: Optional["FolderConfig"] = None,
        review_folder: Optional["FolderConfig"] = None,
        authorization_policy: Optional[Dict[str, Any]] = None,
        created_by: str = "",
        approved_by: Optional[str] = None,
        approved_at: Optional[str] = None,
        field_bindings: Optional[List[SignatureFieldBinding]] = None,
        migration_source_legacy: bool = False,
        content_hash: str = "",
    ) -> "ControlledSigningRecipe":
        recipe_id = recipe_id or uuid4().hex
        now = _utc_now_iso()
        return ControlledSigningRecipe(
            recipe_id=recipe_id,
            name=name.strip() or "Signature Recipe",
            status=status,
            document_matcher=_normalize_dict(document_matcher) or {"kind": "exact"},
            input_folder=input_folder
            or FolderConfig(folder_id=uuid4().hex, path="", recursive=False, require_stable_size=True),
            output_folder=output_folder
            or FolderConfig(folder_id=uuid4().hex, path="", recursive=False, require_stable_size=True),
            review_folder=review_folder,
            authorization_policy=_normalize_dict(authorization_policy) or {"require_active_grant": True},
            version=1,
            field_bindings=list(field_bindings or []),
            created_by=_normalize_optional_text(created_by) or "",
            approved_by=_normalize_optional_text(approved_by),
            approved_at=_normalize_optional_text(approved_at),
            created_at=now,
            updated_at=now,
            content_hash=content_hash.strip(),
            migration_source_legacy=migration_source_legacy,
        )

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "recipe_id": self.recipe_id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "document_matcher": self.document_matcher,
            "input_folder": self.input_folder.to_payload(),
            "output_folder": self.output_folder.to_payload(),
            "review_folder": self.review_folder.to_payload() if self.review_folder else None,
            "authorization_policy": self.authorization_policy,
            "created_by": self.created_by,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
            "migration_source_legacy": self.migration_source_legacy,
            "content_hash": self.content_hash,
            "field_bindings": [binding.to_payload() for binding in self.field_bindings],
        }
        return payload

    @staticmethod
    def from_payload(payload: Dict[str, Any]) -> "ControlledSigningRecipe":
        if not isinstance(payload, dict):
            payload = {}

        raw_bindings = payload.get("field_bindings")
        bindings: List[SignatureFieldBinding] = []
        if isinstance(raw_bindings, list):
            for raw in raw_bindings:
                if isinstance(raw, dict):
                    bindings.append(SignatureFieldBinding.from_legacy_payload(raw))

        input_folder = FolderConfig.from_payload(_coerce_mapping(payload.get("input_folder")) or {})
        output_folder = FolderConfig.from_payload(_coerce_mapping(payload.get("output_folder")) or {})
        review_folder_payload = _coerce_mapping(payload.get("review_folder"))
        review_folder = FolderConfig.from_payload(review_folder_payload) if review_folder_payload else None

        return ControlledSigningRecipe(
            recipe_id=str(payload.get("recipe_id") or uuid4().hex),
            name=str(payload.get("name") or "Signature Recipe"),
            version=int(payload.get("version") or 1),
            status=str(payload.get("status") or RecipeStatus.DRAFT.value),
            document_matcher=_normalize_dict(_coerce_mapping(payload.get("document_matcher"))) or {
                "kind": "exact"
            },
            input_folder=input_folder,
            output_folder=output_folder,
            review_folder=review_folder,
            authorization_policy=_normalize_dict(_coerce_mapping(payload.get("authorization_policy")))
            or {"require_active_grant": True},
            field_bindings=bindings,
            created_by=_normalize_optional_text(payload.get("created_by")) or "",
            approved_by=_normalize_optional_text(payload.get("approved_by")),
            approved_at=_normalize_optional_text(payload.get("approved_at")),
            created_at=str(payload.get("created_at") or _utc_now_iso()),
            updated_at=str(payload.get("updated_at") or _utc_now_iso()),
            migration_source_legacy=bool(payload.get("migration_source_legacy", False)),
            content_hash=str(payload.get("content_hash") or ""),
        )


@dataclass(frozen=True)
class FolderConfig:
    """Folder binding used by workflow execution."""

    folder_id: str
    path: str
    recursive: bool = False
    require_stable_size: bool = True

    @staticmethod
    def from_payload(payload: Dict[str, Any]) -> "FolderConfig":
        return FolderConfig(
            folder_id=_normalize_optional_text(payload.get("folder_id")) or uuid4().hex,
            path=str(payload.get("path") or ""),
            recursive=bool(payload.get("recursive", False)),
            require_stable_size=bool(payload.get("require_stable_size", True)),
        )

    def to_payload(self) -> Dict[str, Any]:
        return {
            "folder_id": self.folder_id,
            "path": self.path,
            "recursive": self.recursive,
            "require_stable_size": self.require_stable_size,
        }


class WorkflowState(str, Enum):
    """Lifecycle states for one workflow job."""

    QUEUED = "queued"
    VALIDATING = "validating"
    MATCHING = "matching"
    PROCESSING = "processing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"


class MatchClass(str, Enum):
    """Document-match class for execution routing."""

    EXACT = "exact"
    FAMILY = "family"
    REVIEW_ONLY = "review_only"


@dataclass(frozen=True)
class WorkflowJob:
    """Durable job state for one input file execution."""

    job_id: str
    input_path_ref: str
    input_fingerprint: str
    recipe_id: str
    recipe_version: int
    output_path_ref: str = ""
    receipt_reference: Optional[str] = None
    last_idempotency_key: Optional[str] = None
    state: WorkflowState = WorkflowState.QUEUED
    grant_id: Optional[str] = None
    match_class: MatchClass = MatchClass.REVIEW_ONLY
    attempts: int = 0
    max_attempts: int = 3
    last_error_code: Optional[str] = None
    last_error_message: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    @staticmethod
    def new(
        *,
        job_id: Optional[str],
        input_path_ref: str,
        input_fingerprint: str,
        recipe_id: str,
        recipe_version: int,
        state: WorkflowState = WorkflowState.QUEUED,
        grant_id: Optional[str] = None,
        match_class: MatchClass = MatchClass.REVIEW_ONLY,
        max_attempts: int = 3,
    ) -> "WorkflowJob":
        now = _utc_now_iso()
        return WorkflowJob(
            job_id=job_id or uuid4().hex,
            input_path_ref=input_path_ref,
            input_fingerprint=input_fingerprint,
            recipe_id=recipe_id,
            recipe_version=recipe_version,
            output_path_ref="",
            receipt_reference=None,
            last_idempotency_key=None,
            state=state,
            grant_id=grant_id,
            match_class=match_class,
            attempts=0,
            max_attempts=max_attempts,
            created_at=now,
            updated_at=now,
        )

    def to_payload(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "input_path_ref": self.input_path_ref,
            "input_fingerprint": self.input_fingerprint,
            "recipe_id": self.recipe_id,
            "recipe_version": self.recipe_version,
            "output_path_ref": self.output_path_ref,
            "receipt_reference": self.receipt_reference,
            "last_idempotency_key": self.last_idempotency_key,
            "state": self.state.value,
            "grant_id": self.grant_id,
            "match_class": self.match_class.value,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "last_error_code": self.last_error_code,
            "last_error_message": self.last_error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_payload(payload: Dict[str, Any]) -> "WorkflowJob":
        if not isinstance(payload, dict):
            payload = {}
        return WorkflowJob(
            job_id=str(payload.get("job_id") or uuid4().hex),
            input_path_ref=str(payload.get("input_path_ref") or ""),
            input_fingerprint=str(payload.get("input_fingerprint") or ""),
            recipe_id=str(payload.get("recipe_id") or ""),
            recipe_version=int(payload.get("recipe_version") or 1),
            output_path_ref=_normalize_optional_text(payload.get("output_path_ref")) or "",
            receipt_reference=_normalize_optional_text(payload.get("receipt_reference")),
            last_idempotency_key=_normalize_optional_text(payload.get("last_idempotency_key")),
            state=WorkflowState(str(payload.get("state") or WorkflowState.QUEUED.value)),
            grant_id=_normalize_optional_text(payload.get("grant_id")),
            match_class=MatchClass(str(payload.get("match_class") or MatchClass.REVIEW_ONLY.value)),
            attempts=int(payload.get("attempts") or 0),
            max_attempts=int(payload.get("max_attempts") or 3),
            last_error_code=_normalize_optional_text(payload.get("last_error_code")),
            last_error_message=_normalize_optional_text(payload.get("last_error_message")),
            created_at=str(payload.get("created_at") or _utc_now_iso()),
            updated_at=str(payload.get("updated_at") or _utc_now_iso()),
        )


@dataclass(frozen=True)
class WorkflowJobEvent:
    """One state transition event for workflow job observability."""

    event_id: str
    job_id: str
    state_from: Optional[str]
    state_to: str
    actor: str
    code: str
    message: Optional[str]
    occurred_at: str = ""

    @staticmethod
    def from_payload(payload: Dict[str, Any]) -> "WorkflowJobEvent":
        if not isinstance(payload, dict):
            payload = {}
        return WorkflowJobEvent(
            event_id=str(payload.get("event_id") or uuid4().hex),
            job_id=str(payload.get("job_id") or ""),
            state_from=_normalize_optional_text(payload.get("state_from")),
            state_to=str(payload.get("state_to") or ""),
            actor=str(payload.get("actor") or ""),
            code=str(payload.get("code") or ""),
            message=_normalize_optional_text(payload.get("message")),
            occurred_at=str(payload.get("occurred_at") or _utc_now_iso()),
        )

    def to_payload(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "job_id": self.job_id,
            "state_from": self.state_from,
            "state_to": self.state_to,
            "actor": self.actor,
            "code": self.code,
            "message": self.message,
            "occurred_at": self.occurred_at,
        }


@dataclass(frozen=True)
class ExecutionGrant:
    """Durable grant entry controlling who may execute a recipe."""

    grant_id: str
    recipe_id: str
    recipe_version: int
    approver_subject: str
    runner_roles: List[str]
    allowed_assets: List[str]
    input_folder_id: str
    output_folder_id: str
    matcher_modes: List[str]
    max_jobs: Optional[int]
    expires_at: Optional[str]
    is_active: bool
    revoked_at: Optional[str] = None
    revoked_reason: Optional[str] = None
    revoked_by: Optional[str] = None
    created_by: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    @staticmethod
    def new(
        *,
        grant_id: Optional[str],
        recipe_id: str,
        recipe_version: int,
        approver_subject: str,
        runner_roles: Optional[List[str]] = None,
        allowed_assets: Optional[List[str]] = None,
        input_folder_id: str = "",
        output_folder_id: str = "",
        matcher_modes: Optional[List[str]] = None,
        max_jobs: Optional[int] = None,
        expires_at: Optional[str] = None,
        is_active: bool = True,
        created_by: Optional[str] = None,
    ) -> "ExecutionGrant":
        now = _utc_now_iso()
        return ExecutionGrant(
            grant_id=grant_id or uuid4().hex,
            recipe_id=recipe_id,
            recipe_version=recipe_version,
            approver_subject=approver_subject,
            runner_roles=[value for value in (runner_roles or []) if isinstance(value, str) and value],
            allowed_assets=[value for value in (allowed_assets or []) if isinstance(value, str) and value],
            input_folder_id=input_folder_id,
            output_folder_id=output_folder_id,
            matcher_modes=[value for value in (matcher_modes or []) if isinstance(value, str) and value],
            max_jobs=max_jobs if isinstance(max_jobs, int) else None,
            expires_at=expires_at,
            is_active=bool(is_active),
            created_by=created_by,
            created_at=now,
            updated_at=now,
        )

    def to_payload(self) -> Dict[str, Any]:
        return {
            "grant_id": self.grant_id,
            "recipe_id": self.recipe_id,
            "recipe_version": self.recipe_version,
            "approver_subject": self.approver_subject,
            "runner_roles": self.runner_roles,
            "allowed_assets": self.allowed_assets,
            "input_folder_id": self.input_folder_id,
            "output_folder_id": self.output_folder_id,
            "matcher_modes": self.matcher_modes,
            "max_jobs": self.max_jobs,
            "expires_at": self.expires_at,
            "is_active": self.is_active,
            "revoked_at": self.revoked_at,
            "revoked_reason": self.revoked_reason,
            "revoked_by": self.revoked_by,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_payload(payload: Dict[str, Any]) -> "ExecutionGrant":
        if not isinstance(payload, dict):
            payload = {}
        return ExecutionGrant(
            grant_id=str(payload.get("grant_id") or uuid4().hex),
            recipe_id=str(payload.get("recipe_id") or ""),
            recipe_version=int(payload.get("recipe_version") or 1),
            approver_subject=str(payload.get("approver_subject") or ""),
            runner_roles=[item for item in (payload.get("runner_roles") or []) if isinstance(item, str)],
            allowed_assets=[item for item in (payload.get("allowed_assets") or []) if isinstance(item, str)],
            input_folder_id=str(payload.get("input_folder_id") or ""),
            output_folder_id=str(payload.get("output_folder_id") or ""),
            matcher_modes=[item for item in (payload.get("matcher_modes") or []) if isinstance(item, str)],
            max_jobs=int(payload.get("max_jobs")) if isinstance(payload.get("max_jobs"), int) else None,
            expires_at=_normalize_optional_text(payload.get("expires_at")),
            is_active=bool(payload.get("is_active", True)),
            revoked_at=_normalize_optional_text(payload.get("revoked_at")),
            revoked_reason=_normalize_optional_text(payload.get("revoked_reason")),
            revoked_by=_normalize_optional_text(payload.get("revoked_by")),
            created_by=_normalize_optional_text(payload.get("created_by")),
            created_at=str(payload.get("created_at") or _utc_now_iso()),
            updated_at=str(payload.get("updated_at") or _utc_now_iso()),
        )


def _coerce_optional_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _coerce_mapping(value: Any) -> Optional[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return value
    return None


def _normalize_dict(value: Any) -> Dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    normalized: Dict[str, Any] = {}
    for key, item in value.items():
        if isinstance(key, str) and key:
            normalized[key.strip()] = item
    return normalized


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
