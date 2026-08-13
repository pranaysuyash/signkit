"""Authorization and grant-lifecycle helpers for controlled signing workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional

from desktop_app.workflows import models, store

AuthCode = str


REASONS = {
    "ok": "grant_ok",
    "missing_subject": "ERR_AUTH_MISSING_SUBJECT",
    "missing_grant": "ERR_AUTH_MISSING",
    "revoked": "ERR_AUTH_REVOKED",
    "expired": "ERR_AUTH_EXPIRED",
    "inactive": "ERR_AUTH_INACTIVE",
    "recipe_mismatch": "ERR_AUTH_RECIPE_MISMATCH",
    "version_mismatch": "ERR_AUTH_VERSION_MISMATCH",
    "quota_exceeded": "ERR_AUTH_QUOTA_EXCEEDED",
    "subject_mismatch": "ERR_AUTH_SUBJECT_MISMATCH",
    "matcher_mode_mismatch": "ERR_AUTH_MATCHER_MODE_MISMATCH",
    "asset_not_allowed": "ERR_AUTH_ASSET_NOT_ALLOWED",
    "folder_scope_mismatch": "ERR_AUTH_FOLDER_MISMATCH",
}


@dataclass(frozen=True)
class GrantDecision:
    """Authorization result for a workflow job."""

    allowed: bool
    code: str
    reason: str
    grant: Optional[models.ExecutionGrant] = None


def is_grant_valid(
    grant: models.ExecutionGrant,
    *,
    now_ts: Optional[str] = None,
) -> bool:
    """Validate a grant's lifecycle and expiry using persisted policy."""
    return store.is_grant_valid(grant, now_ts=now_ts)


def create_grant(
    recipe_id: str,
    policy: Dict[str, object],
    runner: str,
) -> models.ExecutionGrant:
    """Create and persist a new execution grant for a recipe.

    Args:
        recipe_id: Target recipe id.
        policy: Policy and constraint fields.
        runner: Subject requesting/owning the grant.
    """
    recipe = store.get_recipe(recipe_id)
    if recipe is None:
        raise ValueError(f"Unknown recipe_id={recipe_id}")

    matcher_modes = _normalize_list(policy.get("matcher_modes"), default=["exact"])
    allowed_assets = _normalize_list(policy.get("allowed_assets"), default=[])
    runner_roles = _normalize_list(policy.get("runner_roles"), default=["operator"])

    input_folder_id = _normalize_optional_text(policy.get("input_folder_id"))
    output_folder_id = _normalize_optional_text(policy.get("output_folder_id"))

    if not input_folder_id:
        input_folder_id = recipe.input_folder.folder_id
    if not output_folder_id:
        output_folder_id = recipe.output_folder.folder_id

    grant = models.ExecutionGrant.new(
        grant_id=None,
        recipe_id=recipe.recipe_id,
        recipe_version=recipe.version,
        approver_subject=runner,
        runner_roles=runner_roles,
        allowed_assets=allowed_assets,
        input_folder_id=input_folder_id,
        output_folder_id=output_folder_id,
        matcher_modes=matcher_modes,
        max_jobs=int(policy["max_jobs"]) if isinstance(policy.get("max_jobs"), int) else None,
        expires_at=_normalize_optional_text(policy.get("expires_at")),
        is_active=bool(policy.get("is_active", True)),
        created_by=runner,
    )
    return store.save_grant(grant)


def revoke_grant(grant_id: str, *, actor: str, reason: str) -> Optional[models.ExecutionGrant]:
    """Revoke a grant and persist the updated authorization state."""
    return store.revoke_grant(grant_id, actor=actor, reason=reason)


def require_authorization(
    job: models.WorkflowJob,
    *,
    subject: str,
    requested_action: str,
) -> GrantDecision:
    """Require authorization for a given requested action against a job.

    Subject is treated as principal identifier (e.g., email or OS subject string).
    """
    if not subject:
        return GrantDecision(False, REASONS["missing_subject"], "Subject is required")

    # Explicitly non-persistent actions can still run with broad role checks disabled.
    if requested_action not in {"inspect_job", "run_job", "retry_job", "approve_job"}:
        return GrantDecision(False, "ERR_AUTH_UNKNOWN_ACTION", f"Unknown action: {requested_action}")

    if not job.grant_id:
        return GrantDecision(False, REASONS["missing_grant"], "No grant attached to job")

    grant = store.get_grant(job.grant_id)
    if grant is None:
        return GrantDecision(False, REASONS["missing_grant"], "Grant not found")

    if not is_grant_valid(grant):
        if grant.revoked_at:
            return GrantDecision(False, REASONS["revoked"], "Grant is revoked")
        if not grant.is_active:
            return GrantDecision(False, REASONS["inactive"], "Grant is inactive")
        return GrantDecision(False, REASONS["expired"], "Grant expired")

    if grant.recipe_id != job.recipe_id:
        return GrantDecision(False, REASONS["recipe_mismatch"], "Grant does not match recipe")

    if grant.recipe_version != job.recipe_version:
        return GrantDecision(False, REASONS["version_mismatch"], "Grant does not match recipe version")

    if not _subject_is_authorized(grant, subject):
        return GrantDecision(False, REASONS["subject_mismatch"], "Subject is not authorized for this grant")

    executed = count_jobs_for_grant(grant.grant_id)
    if requested_action != "inspect_job" and grant.max_jobs is not None and executed >= grant.max_jobs:
        return GrantDecision(False, REASONS["quota_exceeded"], "Grant job quota is exhausted")

    return GrantDecision(True, REASONS["ok"], "Grant is valid", grant=grant)


def validate_execution_scope(
    *,
    grant: models.ExecutionGrant,
    recipe: models.ControlledSigningRecipe,
    match_class: str,
    input_path: str,
    signature_asset_refs: Iterable[str],
    output_path: Optional[str] = None,
) -> GrantDecision:
    """Validate match-mode, asset, and folder constraints for one execution attempt."""

    normalized_match_class = str(match_class)
    if grant.matcher_modes:
        normalized_allowed = [str(value).strip().lower() for value in grant.matcher_modes]
        if normalized_match_class not in normalized_allowed:
            return GrantDecision(
                False,
                REASONS["matcher_mode_mismatch"],
                f"Matcher mode '{normalized_match_class}' not allowed for this grant",
                grant=grant,
            )

    allowed_assets = [str(item).strip() for item in grant.allowed_assets if isinstance(item, str)]
    if allowed_assets:
        for asset_ref in signature_asset_refs:
            if str(asset_ref).strip() not in allowed_assets:
                return GrantDecision(
                    False,
                    REASONS["asset_not_allowed"],
                    f"Signature asset '{asset_ref}' not allowed by this grant",
                    grant=grant,
                )

    if grant.input_folder_id and str(grant.input_folder_id) != str(recipe.input_folder.folder_id):
        return GrantDecision(False, REASONS["folder_scope_mismatch"], "Grant input folder scope does not match recipe", grant=grant)

    if grant.output_folder_id and str(grant.output_folder_id) != str(recipe.output_folder.folder_id):
        return GrantDecision(False, REASONS["folder_scope_mismatch"], "Grant output folder scope does not match recipe", grant=grant)

    if not _is_path_within_folder(input_path, recipe.input_folder.path):
        return GrantDecision(False, REASONS["folder_scope_mismatch"], "Input path is outside granted input folder", grant=grant)

    if output_path and not _is_path_within_folder(output_path, recipe.output_folder.path):
        return GrantDecision(False, REASONS["folder_scope_mismatch"], "Output path is outside granted output folder", grant=grant)

    return GrantDecision(True, REASONS["ok"], "Execution scope is allowed", grant=grant)


def _is_path_within_folder(path: str, folder: str) -> bool:
    folder_path = Path(folder).resolve() if folder else Path()
    if not folder:
        return False
    target_path = Path(path).resolve()
    try:
        target_path.relative_to(folder_path)
        return True
    except ValueError:
        return False


def count_jobs_for_grant(grant_id: str) -> int:
    """Count jobs already associated with this grant."""
    if not grant_id:
        return 0
    jobs = store.list_jobs(grant_id=grant_id)
    # Count started jobs; exclude jobs that never ran.
    return len(
        [
            job
            for job in jobs
            if job.state
            in {
                models.WorkflowState.VALIDATING,
                models.WorkflowState.MATCHING,
                models.WorkflowState.PROCESSING,
                models.WorkflowState.VERIFYING,
                models.WorkflowState.COMPLETED,
                models.WorkflowState.RETRY,
                models.WorkflowState.FAILED,
                models.WorkflowState.NEEDS_REVIEW,
            }
        ]
    )


def _normalize_optional_text(value: object) -> Optional[str]:
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _normalize_list(value: object, *, default: list[str] | None = None) -> list[str]:
    if not isinstance(value, list):
        return list(default or [])
    return [item for item in value if isinstance(item, str) and item.strip()]


def _subject_is_authorized(grant: models.ExecutionGrant, subject: str) -> bool:
    if grant.approver_subject == subject:
        return True
    return subject in grant.runner_roles
