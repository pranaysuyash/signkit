"""Workflow execution engine for authorized folder-based signing runs."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Union
from uuid import uuid4

from desktop_app.workflows import authorization
from desktop_app.workflows import matcher
from desktop_app.workflows import models, store


FAILURE_CODES = {
    "auth_missing": "ERR_AUTH_MISSING",
    "auth_expired": "ERR_AUTH_EXPIRED",
    "auth_revoked": "ERR_AUTH_REVOKED",
    "invalid": "ERR_WORKFLOW_INVALID",
    "invalid_state": "ERR_WORKFLOW_STATE",
    "paused": "ERR_WORKFLOW_PAUSED",
    "match_none": "ERR_MATCH_NONE",
    "match_ambiguous": "ERR_MATCH_AMBIGUOUS",
    "quarantined": "ERR_JOB_QUARANTINED",
    "cancelled": "ERR_JOB_CANCELLED",
    "retry_forbidden": "ERR_RETRY_FORBIDDEN",
    "signing_failed": "ERR_SIGNING_FAILED",
    "verify_mismatch": "ERR_VERIFY_MISMATCH",
    "output_exists": "ERR_OUTPUT_EXISTS",
    "io_unstable": "ERR_IO_UNSTABLE",
    "output_io": "ERR_OUTPUT_IO",
}


def sign_pdf(input_pdf_path: str, output_pdf_path: str, signatures: List[Dict[str, object]]) -> bool:
    """Proxy through to the desktop PDF signer when optional backend dependencies are available."""
    try:
        from importlib import import_module

        signer_module = import_module("desktop_app.pdf.signer")
        return bool(signer_module.sign_pdf(input_pdf_path, output_pdf_path, signatures))
    except Exception as exc:  # pragma: no cover - environment-specific integration edge
        raise RuntimeError(f"signer_unavailable:{exc}") from exc


def sign_pdf_with_certificate(input_pdf_path: str, output_pdf_path: str, pfx_path: str | None = None, **kwargs):
    """Route explicit certificate-backed signing through the canonical PDF module."""
    try:
        from importlib import import_module

        signer_module = import_module("desktop_app.pdf.signer")
        return signer_module.sign_pdf_with_certificate(
            input_pdf_path,
            output_pdf_path,
            pfx_path,
            **kwargs,
        )
    except Exception as exc:  # pragma: no cover - environment-specific integration edge
        raise RuntimeError(f"digital_signer_unavailable:{exc}") from exc


class _MissingVaultFallback:
    def retrieve_signature(self, signature_ref: str) -> bytes:
        raise RuntimeError(
            f"vault_factory_unavailable: cannot resolve signature asset '{signature_ref}' because vault backend is unavailable"
        )


def _load_vault_factory():
    try:
        from importlib import import_module

        return import_module("desktop_app.processing.vault").NotaryVault
    except Exception:
        return _MissingVaultFallback


class WorkflowEngine:
    """Execution engine for running persisted workflow jobs."""

    def __init__(
        self,
        *,
        actor: str = "system",
        active_only: bool = True,
        output_namer: str = "{name}_{job_id}_signed.pdf",
        allowed_match_classes: Optional[Sequence[str]] = None,
        vault_factory: Optional[object] = None,
        audit_actor: str = "workflow-engine",
    ) -> None:
        self.actor = actor
        self.active_only = active_only
        self.output_namer = output_namer
        self.allowed_match_classes = set(
            allowed_match_classes or [models.MatchClass.EXACT.value, models.MatchClass.REVIEW_ONLY.value]
        )
        self._vault_factory = _load_vault_factory() if vault_factory is None else vault_factory
        self._running = False
        self._paused = False
        self._audit_actor = audit_actor

    def start(self) -> None:
        """Start engine lifecycle hooks."""
        self._running = True

    def stop(self) -> None:
        """Stop engine lifecycle hooks."""
        self._running = False

    def pause(self) -> None:
        """Pause execution for explicit operator stop/maintenance mode."""
        self._paused = True

    def resume(self) -> None:
        """Resume execution after a pause."""
        self._paused = False

    def is_paused(self) -> bool:
        """Return whether this engine instance is paused."""
        return self._paused

    def retry_job(
        self,
        job_id: str,
        *,
        actor: str = "system",
        action_subject: str = "system",
        idempotency_key: Optional[str] = None,
    ) -> models.WorkflowJob:
        """Retry a job that is eligible for retry/review."""
        with store.workflow_store_lock():
            return self._retry_job_locked(
                job_id,
                actor=actor,
                action_subject=action_subject,
                idempotency_key=idempotency_key,
            )

    def _retry_job_locked(
        self,
        job_id: str,
        *,
        actor: str = "system",
        action_subject: str = "system",
        idempotency_key: Optional[str] = None,
    ) -> models.WorkflowJob:
        """Retry a job while the caller owns the workflow store lock."""
        self._require_running()
        self._require_not_paused()
        job = store.get_job(job_id)
        if job is None:
            raise ValueError(f"job_not_found:{job_id}")

        if job.state not in {models.WorkflowState.FAILED, models.WorkflowState.RETRY, models.WorkflowState.NEEDS_REVIEW}:
            return self._transition_job(
                job,
                to_state=job.state,
                actor=actor,
                code=FAILURE_CODES["invalid_state"],
                message="retry_not_allowed",
            )

        decision = authorization.require_authorization(
            job,
            subject=action_subject,
            requested_action="retry_job",
        )
        if not decision.allowed:
            return self._transition_job(
                job,
                models.WorkflowState.FAILED,
                actor=actor,
                code=_reason_code(decision.code),
                message=f"retry_denied:{decision.reason}",
            )
        if idempotency_key:
            job = store.save_job(replace(job, last_idempotency_key=idempotency_key))
        return self.run_job(job.job_id, actor=actor, action_subject=action_subject)

    def cancel_job(
        self,
        job_id: str,
        *,
        actor: str = "system",
        action_subject: str = "system",
        reason: str = "cancelled_by_operator",
    ) -> models.WorkflowJob:
        """Cancel job execution and prevent further auto-retry."""
        self._require_running()
        self._require_not_paused()
        job = store.get_job(job_id)
        if job is None:
            raise ValueError(f"job_not_found:{job_id}")

        decision = authorization.require_authorization(
            job,
            subject=action_subject,
            requested_action="approve_job",
        )
        if not decision.allowed:
            return self._transition_job(
                job,
                models.WorkflowState.FAILED,
                actor=actor,
                code=_reason_code(decision.code),
                message=f"cancel_denied:{decision.reason}",
            )

        message = reason.strip() or "cancelled_by_operator"
        return self._transition_job(
            job,
            models.WorkflowState.CANCELLED,
            actor=actor,
            code=FAILURE_CODES["cancelled"],
            message=message,
        )

    def quarantine_job(
        self,
        job_id: str,
        *,
        actor: str = "system",
        action_subject: str = "system",
        reason: str = "quarantined_by_operator",
    ) -> models.WorkflowJob:
        """Mark a job as pending review and remove from auto-retry progression."""
        self._require_running()
        self._require_not_paused()
        job = store.get_job(job_id)
        if job is None:
            raise ValueError(f"job_not_found:{job_id}")

        decision = authorization.require_authorization(
            job,
            subject=action_subject,
            requested_action="approve_job",
        )
        if not decision.allowed:
            return self._transition_job(
                job,
                models.WorkflowState.FAILED,
                actor=actor,
                code=_reason_code(decision.code),
                message=f"quarantine_denied:{decision.reason}",
            )

        message = reason.strip() or "quarantined_by_operator"
        return self._transition_job(
            job,
            models.WorkflowState.NEEDS_REVIEW,
            actor=actor,
            code=FAILURE_CODES["quarantined"],
            message=message,
        )

    def enqueue_path(self, pdf_path: str, recipe_id: Optional[str] = None) -> models.WorkflowJob:
        """Create a queued workflow job for an incoming document."""
        self._require_running()
        pdf = Path(pdf_path)
        if not pdf.exists():
            raise ValueError(f"input_not_found:{pdf_path}")

        recipe = _pick_recipe(recipe_id, active_only=self.active_only)
        if recipe is None:
            raise ValueError("recipe_not_found")

        grant_id = _pick_default_grant(recipe.recipe_id)

        job = models.WorkflowJob.new(
            job_id=None,
            input_path_ref=str(pdf),
            input_fingerprint=_compute_fingerprint(pdf),
            recipe_id=recipe.recipe_id,
            recipe_version=recipe.version,
            grant_id=grant_id,
        )
        job = replace(job, match_class=models.MatchClass.REVIEW_ONLY)
        saved = store.save_job(job)
        store.append_job_event(
            event_id=None,
            job_id=saved.job_id,
            state_from=None,
            state_to=job.state,
            actor=self.actor,
            code="EVT_JOB_CREATED",
            message=f"enqueued={pdf_path}",
        )
        return saved

    def run_job(self, job_id: str, *, actor: str = "system", action_subject: str = "system") -> models.WorkflowJob:
        """Execute one queued workflow job end-to-end."""
        with store.workflow_store_lock():
            return self._run_job_locked(job_id, actor=actor, action_subject=action_subject)

    def _run_job_locked(self, job_id: str, *, actor: str = "system", action_subject: str = "system") -> models.WorkflowJob:
        """Execute one queued workflow job while the caller owns the store lock."""
        self._require_running()
        self._require_not_paused()
        job = store.get_job(job_id)
        if job is None:
            raise ValueError(f"job_not_found:{job_id}")

        recipe = store.get_recipe(job.recipe_id)
        if recipe is None:
            return self._transition_job(
                job,
                models.WorkflowState.FAILED,
                actor=actor,
                code=FAILURE_CODES["invalid"],
                message="recipe_not_found",
            )

        decision = authorization.require_authorization(
            job,
            subject=action_subject,
            requested_action="run_job",
        )
        if not decision.allowed:
            reason = decision.code
            code = reason if reason in FAILURE_CODES.values() else FAILURE_CODES["auth_missing"]
            return self._transition_job(
                job,
                models.WorkflowState.FAILED,
                actor=actor,
                code=code,
                message=decision.reason,
            )
        store.save_job(replace(job, grant_id=decision.grant.grant_id if decision.grant else job.grant_id))

        job = self.transition(job.job_id, models.WorkflowState.VALIDATING, actor=actor, code="EVT_JOB_VALIDATING")
        if not job.input_path_ref:
            return self._fail_job(job, actor=actor, code=FAILURE_CODES["invalid"], message="missing_input_path")

        if not os.path.exists(job.input_path_ref):
            return self._fail_job(job, actor=actor, code=FAILURE_CODES["invalid"], message="input_missing")

        try:
            match = matcher.evaluate_match(recipe, job.input_path_ref)
        except Exception as exc:
            return self._fail_job(
                job, actor=actor, code=FAILURE_CODES["match_ambiguous"], message=f"matcher_failed:{exc}"
            )

        if match.match_class == models.MatchClass.REVIEW_ONLY.value:
            job = self._update_job_match_class(job, models.MatchClass.REVIEW_ONLY, match)
            return self._transition_job(
                job,
                models.WorkflowState.NEEDS_REVIEW,
                actor=self._audit_actor,
                code=FAILURE_CODES["match_none"],
                message=f"match_failed:{match.evidence}",
            )

        if match.match_class == models.MatchClass.FAMILY.value and models.MatchClass.FAMILY.value not in self.allowed_match_classes:
            job = self._update_job_match_class(job, models.MatchClass.FAMILY, match)
            return self._transition_job(
                job,
                models.WorkflowState.NEEDS_REVIEW,
                actor=self._audit_actor,
                code=FAILURE_CODES["match_ambiguous"],
                message=f"match_disallowed:{match.evidence}",
            )

        job = self._update_job_match_class(job, models.MatchClass(match.match_class), match)
        job = self.transition(
            job.job_id, models.WorkflowState.MATCHING, actor=self._audit_actor, code="EVT_MATCH_DONE", message=f"{match.evidence}"
        )

        try:
            output_path = self._compute_output_path(recipe, job)
        except Exception as exc:
            return self._fail_job(job, actor=actor, code=FAILURE_CODES["output_io"], message=f"output_path:{exc}")

        # Persist intended output path early so operators can inspect planned outputs
        # even if execution fails before signing completes.
        job = store.save_job(replace(job, output_path_ref=output_path))

        scope_decision = authorization.validate_execution_scope(
            grant=decision.grant,
            recipe=recipe,
            match_class=match.match_class,
            input_path=job.input_path_ref,
            signature_asset_refs=[binding.signature_asset_ref for binding in recipe.field_bindings],
            output_path=output_path,
        )
        if not scope_decision.allowed:
            reason = scope_decision.code
            code = reason if reason in FAILURE_CODES.values() else _reason_code(reason)
            return self._transition_job(
                job,
                models.WorkflowState.FAILED,
                actor=actor,
                code=code,
                message=scope_decision.reason,
            )

        try:
            return self._sign_job(job=job, recipe=recipe, output_path=output_path, match=match, actor=actor)
        except FileExistsError as exc:
            return self._fail_job(job, actor=actor, code=FAILURE_CODES["output_exists"], message=str(exc))
        except Exception as exc:
            return self._fail_job(job, actor=actor, code=FAILURE_CODES["signing_failed"], message=f"signing_error:{exc}")

    def run_queued_jobs(
        self,
        *,
        states: Optional[Iterable[models.WorkflowState]] = None,
        actor: str = "system",
        action_subject: str = "system",
    ) -> Dict[str, int]:
        """Run all jobs matching the requested state set."""
        self._require_running()
        self._require_not_paused()

        normalized_states = [state for state in (states or [models.WorkflowState.QUEUED]) if isinstance(state, models.WorkflowState)]
        state_values = {state.value for state in normalized_states}
        candidates = [job for job in store.list_jobs() if job.state.value in state_values]
        summary: Dict[str, int] = {
            "attempted": len(candidates),
            "completed": 0,
            "needs_review": 0,
            "retry": 0,
            "failed": 0,
            "cancelled": 0,
            "errors": 0,
        }

        for job in candidates:
            try:
                updated = self.run_job(job.job_id, actor=actor, action_subject=action_subject)
            except Exception:
                summary["errors"] += 1
                continue

            if updated.state == models.WorkflowState.COMPLETED:
                summary["completed"] += 1
            elif updated.state == models.WorkflowState.NEEDS_REVIEW:
                summary["needs_review"] += 1
            elif updated.state == models.WorkflowState.RETRY:
                summary["retry"] += 1
            elif updated.state == models.WorkflowState.FAILED:
                summary["failed"] += 1
            elif updated.state == models.WorkflowState.CANCELLED:
                summary["cancelled"] += 1

        return summary

    def transition(
        self,
        job_id: str,
        to_state: models.WorkflowState,
        actor: str,
        code: str,
        message: Optional[str] = None,
    ) -> models.WorkflowJob:
        """Transition a persisted job to a new state."""
        job = store.get_job(job_id)
        if job is None:
            raise ValueError(f"job_not_found:{job_id}")
        return self._transition_job(job, to_state=to_state, actor=actor, code=code, message=message)

    def _sign_job(
        self,
        *,
        job: models.WorkflowJob,
        recipe: models.ControlledSigningRecipe,
        output_path: str,
        match: matcher.MatchResult,
        actor: str,
    ) -> models.WorkflowJob:
        if not recipe.field_bindings:
            return self._fail_job(job, actor=actor, code=FAILURE_CODES["signing_failed"], message="no_bindings")

        job = self.transition(job.job_id, models.WorkflowState.PROCESSING, actor=actor, code="EVT_SIGNING_START")

        with tempfile.TemporaryDirectory(prefix="signkit-workflow-") as staging_dir:
            temporary_input = os.path.join(staging_dir, Path(job.input_path_ref).name)
            shutil.copy2(job.input_path_ref, temporary_input)
            signatures: List[Dict[str, object]] = []
            used_paths: List[str] = []
            try:
                page_box = _page_geometry_map(temporary_input)
                for binding in recipe.field_bindings:
                    sig_abs_path = _resolve_signature_path(binding.signature_asset_ref, self._vault_factory())
                    signatures.append(
                        _signature_payload_from_ratio(
                            binding=binding,
                            page_boxes=page_box,
                            sig_abs_path=Path(sig_abs_path),
                        )
                    )
                    # Direct filesystem assets belong to the operator and
                    # must survive the run. Only remove temporary files
                    # materialized from the vault during cleanup.
                    if not os.path.exists(binding.signature_asset_ref) or os.path.abspath(
                        sig_abs_path
                    ) != os.path.abspath(binding.signature_asset_ref):
                        used_paths.append(sig_abs_path)

                job = self.transition(job.job_id, models.WorkflowState.VERIFYING, actor=actor, code="EVT_SIGNING_PREP")

                signed_ok = sign_pdf(
                    temporary_input,
                    output_path,
                    signatures,
                )
            except Exception as exc:
                return self._fail_job(job, actor=actor, code=FAILURE_CODES["signing_failed"], message=str(exc))
            finally:
                for path in used_paths:
                    try:
                        if os.path.exists(path):
                            os.remove(path)
                    except Exception:
                        pass

        if not signed_ok:
            return self._fail_job(job, actor=actor, code=FAILURE_CODES["signing_failed"], message="sign_pdf_false")

        if not os.path.exists(output_path):
            return self._fail_job(job, actor=actor, code=FAILURE_CODES["verify_mismatch"], message="output_missing")

        if os.path.abspath(output_path) == os.path.abspath(job.input_path_ref):
            return self._fail_job(job, actor=actor, code=FAILURE_CODES["verify_mismatch"], message="in_place_output")

        if os.path.getsize(output_path) <= 0:
            return self._fail_job(job, actor=actor, code=FAILURE_CODES["verify_mismatch"], message="empty_output")

        output_hash = _compute_hash(output_path)
        input_hash = _compute_hash(job.input_path_ref)
        if output_hash == input_hash:
            return self._fail_job(
                job,
                actor=actor,
                code=FAILURE_CODES["verify_mismatch"],
                message="output_hash_unchanged",
            )

        job = self.transition(
            job.job_id,
            models.WorkflowState.COMPLETED,
            actor=actor,
            code="EVT_SIGNING_DONE",
            message=f"match={match.match_class};confidence={match.confidence:.3f};output={output_path}",
        )
        return replace(job, last_error_code=None, last_error_message=None, updated_at=job.updated_at)

    def _update_job_match_class(
        self,
        job: models.WorkflowJob,
        match_class: models.MatchClass,
        match: matcher.MatchResult,
    ) -> models.WorkflowJob:
        updated = replace(
            job,
            match_class=match_class,
            last_error_code=None,
            last_error_message=f"match={match.match_class};confidence={match.confidence:.2f}",
            attempts=job.attempts,
        )
        return store.save_job(updated)

    def _compute_output_path(self, recipe: models.ControlledSigningRecipe, job: models.WorkflowJob) -> str:
        output_dir = Path(recipe.output_folder.path or Path(job.input_path_ref).parent)
        output_dir.mkdir(parents=True, exist_ok=True)

        stem = Path(job.input_path_ref).stem
        name = self.output_namer.format(
            name=recipe.name.replace(" ", "_"),
            job_id=job.job_id,
            input_path=job.input_path_ref,
            recipe_id=recipe.recipe_id,
        )
        candidate = output_dir / name
        if candidate.exists():
            raise FileExistsError(str(candidate))
        return str(candidate)

    def _transition_job(
        self,
        job: models.WorkflowJob,
        to_state: models.WorkflowState,
        *,
        actor: str,
        code: str,
        message: Optional[str] = None,
    ) -> models.WorkflowJob:
        updated = replace(
            job,
            state=to_state,
            last_error_code=None if to_state == models.WorkflowState.COMPLETED else code,
            last_error_message=message,
        )
        if to_state in {
            models.WorkflowState.RETRY,
            models.WorkflowState.FAILED,
            models.WorkflowState.CANCELLED,
        }:
            updated = replace(
                updated,
                attempts=job.attempts + 1,
                last_error_code=code,
                last_error_message=message,
            )
        if to_state == models.WorkflowState.NEEDS_REVIEW:
            recipe = store.get_recipe(job.recipe_id)
            if recipe and recipe.review_folder:
                _copy_review_candidate(
                    folder=recipe.review_folder,
                    input_path=job.input_path_ref,
                    job_id=job.job_id,
                )
        saved = store.save_job(updated)
        state_from = job.state.value
        store.append_job_event(
            event_id=None,
            job_id=job.job_id,
            state_from=state_from,
            state_to=to_state,
            actor=actor,
            code=code,
            message=message,
        )
        return saved

    def _fail_job(self, job: models.WorkflowJob, *, actor: str, code: str, message: str) -> models.WorkflowJob:
        should_retry = job.attempts + 1 < job.max_attempts
        final_state = models.WorkflowState.RETRY if should_retry else models.WorkflowState.FAILED
        return self._transition_job(
            job,
            to_state=final_state,
            actor=actor,
            code=code,
            message=message,
        )

    def _require_running(self) -> None:
        if not self._running:
            self.start()

    def _require_not_paused(self) -> None:
        if self._paused:
            raise RuntimeError("engine_paused")


def _reason_code(code: str) -> str:
    """Normalize authorization result codes into a workflow-compatible code."""
    if code.startswith("ERR_"):
        return code
    return FAILURE_CODES["invalid"]


def _pick_recipe(recipe_id: Optional[str], *, active_only: bool) -> Optional[models.ControlledSigningRecipe]:
    if recipe_id:
        candidate = store.get_recipe(recipe_id)
        if candidate is None:
            return None
        if active_only and candidate.status != models.RecipeStatus.ACTIVE.value:
            return None
        return candidate

    for candidate in store.list_recipes():
        if active_only and candidate.status != models.RecipeStatus.ACTIVE.value:
            continue
        return candidate
    return None


def _pick_default_grant(recipe_id: str) -> Optional[str]:
    grants = store.list_grants(recipe_id=recipe_id, active_only=True)
    if not grants:
        return None
    grants.sort(key=lambda item: item.updated_at, reverse=True)
    return grants[0].grant_id


def _page_geometry_map(pdf_path: str) -> List[tuple[float, float]]:
    pikepdf = _get_pikepdf()
    doc = pikepdf.open(pdf_path)
    try:
        geometry = []
        for page in doc.pages:
            box = list(page.MediaBox)
            width = float(box[2]) - float(box[0])
            height = float(box[3]) - float(box[1])
            geometry.append((width, height))
        return geometry
    finally:
        doc.close()


def _get_pikepdf():
    """Load pikepdf only when matching/signing introspection runs."""
    try:
        import pikepdf  # type: ignore[import-not-found]

        return pikepdf
    except ModuleNotFoundError as exc:
        raise RuntimeError("pikepdf is required for workflow execution and matching") from exc


def _signature_payload_from_ratio(
    *,
    binding: models.SignatureFieldBinding,
    page_boxes: List[tuple[float, float]],
    sig_abs_path: Path,
) -> Dict[str, object]:
    page_index = binding.page_index
    if page_index < 0 or page_index >= len(page_boxes):
        raise ValueError(f"invalid_page_index:{page_index}")
    width, height = page_boxes[page_index]
    return {
        "page": page_index,
        "sig_path": str(sig_abs_path),
        "x": float(binding.x_ratio) * width,
        "y": float(binding.y_ratio) * height,
        "width": float(binding.width_ratio) * width,
        "height": float(binding.height_ratio) * height,
    }


def _resolve_signature_path(signature_ref: str, vault: Union[object, _MissingVaultFallback]) -> str:
    signature_ref = signature_ref.strip()
    if not signature_ref:
        raise ValueError("empty_signature_ref")

    if os.path.exists(signature_ref):
        return signature_ref

    try:
        png_bytes = vault.retrieve_signature(signature_ref)
    except Exception as exc:
        raise ValueError(f"signature_ref_unresolved:{signature_ref}:{exc}") from exc

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    with open(temp_file.name, "wb") as handle:
        handle.write(png_bytes)
    return temp_file.name


def _compute_fingerprint(path: Path) -> str:
    return _compute_hash(path)


def _compute_hash(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def _copy_review_candidate(
    *,
    folder: models.FolderConfig,
    input_path: str,
    job_id: str,
) -> Optional[str]:
    review_dir = Path(folder.path or "").expanduser()
    if not str(review_dir):
        return None

    review_dir.mkdir(parents=True, exist_ok=True)
    source = Path(input_path)
    if not source.exists():
        return None

    target = review_dir / f"{source.stem}_{job_id}_{uuid4().hex[:8]}{source.suffix}"
    shutil.copy2(source, target)
    return str(target)
def export_pdf_artifact(
    input_pdf_path: str,
    output_pdf_path: str,
    *,
    signing_mode: str,
    signatures: list[dict[str, object]] | None = None,
    pfx_path: str | None = None,
    **certificate_options: object,
) -> object:
    """Export through one explicit seam while preserving signing semantics."""

    if signing_mode == "visual":
        if signatures is None:
            raise ValueError("visual signing requires signatures")
        if pfx_path is not None or certificate_options:
            raise ValueError("visual signing does not accept certificate options")
        return sign_pdf(input_pdf_path, output_pdf_path, signatures)

    if signing_mode == "certificate":
        if pfx_path is None and "credential_provider" not in certificate_options:
            raise ValueError("certificate signing requires pfx_path")
        if signatures is not None:
            raise ValueError("certificate signing does not accept visual signatures")
        return sign_pdf_with_certificate(
            input_pdf_path,
            output_pdf_path,
            pfx_path,
            **certificate_options,
        )

    raise ValueError(f"unsupported signing_mode: {signing_mode}")
