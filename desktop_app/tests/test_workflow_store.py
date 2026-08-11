"""Tests for controlled workflow persistence and authorization guard behavior."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from desktop_app.workflows import models
from desktop_app.workflows import store


def _configure_store_path(monkeypatch, path: Path) -> None:
    monkeypatch.setattr(store, "APP_DIR", path)
    monkeypatch.setattr(store, "WORKFLOW_STORE_FILE", path / "workflow_store.json")


def _fresh_binding() -> models.SignatureFieldBinding:
    return models.SignatureFieldBinding.from_legacy_values(
        signature_path="/tmp/signature.png",
        page_index=0,
        x_ratio=0.1,
        y_ratio=0.2,
        width_ratio=0.25,
        height_ratio=0.06,
        field_label="Signer A",
    )


def test_workflow_store_roundtrip_and_state_filters(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)

    first = models.ControlledSigningRecipe.new(
        recipe_id="r-1",
        name="Exact Contract",
        status=models.RecipeStatus.ACTIVE.value,
        field_bindings=[_fresh_binding()],
        document_matcher={"kind": "exact", "filename_prefix": "INV"},
    )
    second = models.ControlledSigningRecipe.new(
        recipe_id="r-2",
        name="Family Contract",
        status=models.RecipeStatus.DRAFT.value,
        field_bindings=[_fresh_binding()],
        document_matcher={"kind": "family", "signature": "INV"},
    )

    saved_first = store.save_recipe(first)
    saved_second = store.save_recipe(second)

    all_recipes = store.list_recipes()
    assert len(all_recipes) == 2
    assert all_recipes[0].recipe_id in {saved_first.recipe_id, saved_second.recipe_id}
    assert store.get_recipe(saved_first.recipe_id) == saved_first

    active_only = store.list_recipes(status=models.RecipeStatus.ACTIVE.value)
    assert len(active_only) == 1
    assert active_only[0].recipe_id == saved_first.recipe_id

    # order remains deterministic and newest-updated first for the same store roundtrip
    assert all_recipes[0].updated_at >= all_recipes[1].updated_at


def test_workflow_store_grant_validation_and_revoke(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)

    recipe = store.save_recipe(
        models.ControlledSigningRecipe.new(
            recipe_id="r-guard",
            name="Guard Recipe",
            status=models.RecipeStatus.APPROVED.value,
            field_bindings=[_fresh_binding()],
        )
    )

    active_grant = models.ExecutionGrant.new(
        grant_id="g-active",
        recipe_id=recipe.recipe_id,
        recipe_version=recipe.version,
        approver_subject="ops@company",
        runner_roles=["operator"],
        allowed_assets=["sig-asset-1"],
        input_folder_id="input-a",
        output_folder_id="output-a",
        matcher_modes=["exact"],
        max_jobs=3,
        is_active=True,
    )
    store.save_grant(active_grant)

    valid = store.is_grant_valid(active_grant)
    assert valid is True

    inactive = store.revoke_grant("g-active", reason="policy update", actor="admin")
    assert inactive is not None
    assert inactive.is_active is False
    assert inactive.revoked_reason == "policy update"

    assert store.is_grant_valid(inactive) is False


def test_workflow_store_jobs_events_lifecycle(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)

    recipe = store.save_recipe(
        models.ControlledSigningRecipe.new(
            recipe_id="r-job",
            name="Job Recipe",
            field_bindings=[_fresh_binding()],
            status=models.RecipeStatus.ACTIVE.value,
        )
    )

    job = models.WorkflowJob.new(
        job_id="job-1",
        input_path_ref="/tmp/doc-1.pdf",
        input_fingerprint="fp-1",
        recipe_id=recipe.recipe_id,
        recipe_version=recipe.version,
        state=models.WorkflowState.QUEUED,
        grant_id="g-1",
        match_class=models.MatchClass.EXACT,
    )

    store.save_job(job)

    queued = store.list_jobs(state=models.WorkflowState.QUEUED.value)
    assert len(queued) == 1
    assert queued[0].job_id == "job-1"

    store.append_job_event(
        event_id=None,
        job_id="job-1",
        state_from=None,
        state_to=models.WorkflowState.VERIFYING,
        actor="runner",
        code="EVT_JOB_VERIFY_START",
        message="verifying file",
    )

    events = store.list_events(job_id="job-1")
    assert len(events) == 1
    assert events[0].state_to == models.WorkflowState.VERIFYING.value


def test_workflow_store_delete_recipe_cascades_children(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)

    recipe = store.save_recipe(
        models.ControlledSigningRecipe.new(
            recipe_id="r-cascade",
            name="Cascade Recipe",
            field_bindings=[_fresh_binding()],
            status=models.RecipeStatus.ACTIVE.value,
        )
    )

    grant = models.ExecutionGrant.new(
        grant_id="g-cascade",
        recipe_id=recipe.recipe_id,
        recipe_version=recipe.version,
        approver_subject="approver",
        input_folder_id="in",
        output_folder_id="out",
    )
    store.save_grant(grant)

    job = models.WorkflowJob.new(
        job_id="job-cascade",
        input_path_ref="/tmp/doc-2.pdf",
        input_fingerprint="fp-2",
        recipe_id=recipe.recipe_id,
        recipe_version=recipe.version,
        match_class=models.MatchClass.EXACT,
    )
    job = store.save_job(job)

    store.append_job_event(
        event_id=None,
        job_id=job.job_id,
        state_from=None,
        state_to=models.WorkflowState.VALIDATING,
        actor="runner",
        code="EVT_JOB_STARTED",
        message="start",
    )

    assert store.get_grant("g-cascade") is not None
    assert store.get_job("job-cascade") is not None
    assert len(store.list_events(job_id="job-cascade")) == 1

    removed = store.delete_recipe(recipe.recipe_id)
    assert removed is True
    assert store.get_recipe(recipe.recipe_id) is None
    assert store.get_grant("g-cascade") is None
    assert store.get_job("job-cascade") is None
    assert len(store.list_events(job_id="job-cascade")) == 0


def test_workflow_store_handles_invalid_payload(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    store.WORKFLOW_STORE_FILE.write_text("{not-json}")

    assert store.list_recipes() == []
    assert store.list_grants() == []
    assert store.list_jobs() == []
    assert store.list_events() == []


def test_workflow_store_grant_expiry_guard(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)

    past = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    near_future = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    expired = models.ExecutionGrant.new(
        grant_id="g-expired",
        recipe_id="recipe-x",
        recipe_version=1,
        approver_subject="approver",
        expires_at=past,
    )
    valid = models.ExecutionGrant.new(
        grant_id="g-valid",
        recipe_id="recipe-x",
        recipe_version=1,
        approver_subject="approver",
        expires_at=near_future,
    )

    assert store.is_grant_valid(expired) is False
    assert store.is_grant_valid(valid) is True


def test_workflow_store_append_event_requires_job(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)

    with pytest.raises(ValueError):
        store.append_job_event(
            event_id=None,
            job_id="",
            state_from=None,
            state_to=models.WorkflowState.QUEUED,
            actor="runner",
            code="EVT_FAIL",
            message="missing job",
        )
