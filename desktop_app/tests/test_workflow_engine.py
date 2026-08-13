from pathlib import Path
import shutil
from typing import List
import pytest

from desktop_app.workflows import authorization, matcher, models, store
from desktop_app.workflows.engine import WorkflowEngine


def _configure_store_path(monkeypatch, path: Path) -> None:
    monkeypatch.setattr(store, "APP_DIR", path)
    monkeypatch.setattr(store, "WORKFLOW_STORE_FILE", path / "workflow_store.json")


def _fresh_binding(signature_path: str) -> models.SignatureFieldBinding:
    return models.SignatureFieldBinding.from_legacy_values(
        signature_path=signature_path,
        page_index=0,
        x_ratio=0.1,
        y_ratio=0.2,
        width_ratio=0.25,
        height_ratio=0.06,
        field_label="Signer A",
    )


def _create_recipe(tmp_path: Path) -> models.ControlledSigningRecipe:
    signature_path = tmp_path / "sig.png"
    signature_path.write_bytes(b"signature")

    return models.ControlledSigningRecipe.new(
        recipe_id="recipe-1",
        name="Legal Packet",
        status=models.RecipeStatus.ACTIVE.value,
        field_bindings=[_fresh_binding(str(signature_path))],
        input_folder=models.FolderConfig(
            folder_id="in-1",
            path=str(tmp_path / "in"),
            recursive=False,
            require_stable_size=True,
        ),
        output_folder=models.FolderConfig(
            folder_id="out-1",
            path=str(tmp_path / "out"),
            recursive=False,
            require_stable_size=True,
        ),
        review_folder=models.FolderConfig(
            folder_id="review-1",
            path=str(tmp_path / "review"),
            recursive=False,
            require_stable_size=True,
        ),
    )


def test_workflow_engine_completes_when_match_is_exact(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    recipe = store.save_recipe(_create_recipe(tmp_path))

    signature_grant = authorization.create_grant(
        recipe.recipe_id,
        policy={"matcher_modes": ["exact"], "allowed_assets": []},
        runner="operator@example.com",
    )
    store.save_grant(signature_grant)

    input_pdf = tmp_path / "in" / "packet.pdf"
    input_pdf.parent.mkdir(parents=True, exist_ok=True)
    input_pdf.write_bytes(b"%PDF-1.4\n%mock\n")

    engine = WorkflowEngine(output_namer="{name}_{job_id}_signed.pdf")
    engine.start()
    job = engine.enqueue_path(str(input_pdf), recipe_id=recipe.recipe_id)

    def fake_evaluate_match(*args, **kwargs) -> matcher.MatchResult:
        return matcher.MatchResult(models.MatchClass.EXACT.value, 1.0, {"kind": "exact"})

    def fake_page_geometry(_path: str) -> List[tuple[float, float]]:
        return [(612.0, 792.0)]

    def fake_sign_pdf(_input_path: str, output_path: str, _signatures: List[dict]) -> bool:
        Path(output_path).write_bytes(b"%PDF-1.4\n%signed\n")
        return True

    monkeypatch.setattr("desktop_app.workflows.engine.matcher.evaluate_match", fake_evaluate_match)
    monkeypatch.setattr("desktop_app.workflows.engine._page_geometry_map", fake_page_geometry)
    monkeypatch.setattr("desktop_app.workflows.engine.sign_pdf", fake_sign_pdf)

    result = engine.run_job(job.job_id, actor="operator", action_subject="operator@example.com")

    assert result.state == models.WorkflowState.COMPLETED
    assert result.last_error_code is None
    assert result.grant_id == signature_grant.grant_id

    expected_output = recipe.output_folder.path.rstrip("/") + "/" + f"{recipe.name.replace(' ', '_')}_{job.job_id}_signed.pdf"
    assert Path(expected_output).exists()
    assert result.output_path_ref == expected_output

    events = store.list_events(job.job_id)
    codes = [event.code for event in events]
    assert "EVT_SIGNING_DONE" in codes


def test_workflow_engine_real_pdf_signing_preserves_direct_signature_asset(monkeypatch, tmp_path: Path) -> None:
    """Exercise the actual PDF signer and prove source assets are not cleaned up."""
    _configure_store_path(monkeypatch, tmp_path)

    project_root = Path(__file__).resolve().parents[2]
    signature_path = project_root / "desktop_app/resources/signature_template_synthetic_512.jpg"
    input_pdf = tmp_path / "in" / "packet.pdf"
    input_pdf.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(project_root / "desktop_app/tests/fixtures/sample.pdf", input_pdf)

    recipe = store.save_recipe(
        models.ControlledSigningRecipe.new(
            recipe_id="real-pdf-recipe",
            name="Real PDF Packet",
            status=models.RecipeStatus.ACTIVE.value,
            field_bindings=[
                models.SignatureFieldBinding.from_legacy_values(
                    signature_path=str(signature_path),
                    page_index=0,
                    x_ratio=0.1,
                    y_ratio=0.2,
                    width_ratio=0.25,
                    height_ratio=0.06,
                )
            ],
            input_folder=models.FolderConfig(folder_id="in", path=str(input_pdf.parent), recursive=False),
            output_folder=models.FolderConfig(folder_id="out", path=str(tmp_path / "out"), recursive=False),
            review_folder=models.FolderConfig(folder_id="review", path=str(tmp_path / "review"), recursive=False),
        )
    )
    grant = authorization.create_grant(
        recipe.recipe_id,
        policy={"matcher_modes": ["exact"], "allowed_assets": [str(signature_path)]},
        runner="operator@example.com",
    )
    store.save_grant(grant)

    engine = WorkflowEngine()
    engine.start()
    job = engine.enqueue_path(str(input_pdf), recipe_id=recipe.recipe_id)
    result = engine.run_job(job.job_id, actor="operator", action_subject="operator@example.com")

    assert result.state == models.WorkflowState.COMPLETED
    assert result.output_path_ref and Path(result.output_path_ref).exists()
    assert signature_path.exists()
    event_codes = [event.code for event in store.list_events(job.job_id)]
    assert "EVT_SIGNING_DONE" in event_codes


def test_workflow_engine_routes_review_class_to_review(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    recipe = store.save_recipe(_create_recipe(tmp_path))
    authorization.create_grant(
        recipe.recipe_id,
        policy={"matcher_modes": ["review_only"], "allowed_assets": []},
        runner="operator@example.com",
    )

    input_pdf = tmp_path / "in" / "packet.pdf"
    input_pdf.parent.mkdir(parents=True, exist_ok=True)
    input_pdf.write_bytes(b"%PDF-1.4\n%mock\n")

    engine = WorkflowEngine()
    engine.start()
    job = engine.enqueue_path(str(input_pdf), recipe_id=recipe.recipe_id)

    monkeypatch.setattr(
        "desktop_app.workflows.engine.matcher.evaluate_match",
        lambda *_args, **_kwargs: matcher.MatchResult(models.MatchClass.REVIEW_ONLY.value, 0.0, {"reason": "ambiguous"}),
    )

    result = engine.run_job(job.job_id, actor="operator", action_subject="operator@example.com")

    assert result.state == models.WorkflowState.NEEDS_REVIEW
    assert result.last_error_code == "ERR_MATCH_NONE"


def test_workflow_engine_routes_malformed_input_to_bounded_review_state(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    recipe = store.save_recipe(_create_recipe(tmp_path))
    grant = authorization.create_grant(
        recipe.recipe_id,
        policy={"matcher_modes": ["exact"], "allowed_assets": []},
        runner="operator@example.com",
    )
    store.save_grant(grant)

    input_file = tmp_path / "in" / "notes.txt"
    input_file.parent.mkdir(parents=True, exist_ok=True)
    input_file.write_text("not a PDF", encoding="utf-8")

    engine = WorkflowEngine()
    engine.start()
    job = engine.enqueue_path(str(input_file), recipe_id=recipe.recipe_id)
    result = engine.run_job(job.job_id, actor="operator", action_subject="operator@example.com")

    assert result.state == models.WorkflowState.NEEDS_REVIEW
    assert result.last_error_code == "ERR_INPUT_INVALID"
    assert result.attempts == 0
    assert result.last_error_message == "input_requires_review"


def test_workflow_engine_rejects_run_without_valid_grant(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    recipe = store.save_recipe(_create_recipe(tmp_path))

    input_pdf = tmp_path / "in" / "packet.pdf"
    input_pdf.parent.mkdir(parents=True, exist_ok=True)
    input_pdf.write_bytes(b"%PDF-1.4\n%mock\n")

    engine = WorkflowEngine()
    engine.start()
    job = engine.enqueue_path(str(input_pdf), recipe_id=recipe.recipe_id)

    result = engine.run_job(job.job_id, actor="operator", action_subject="operator@example.com")

    assert result.state == models.WorkflowState.FAILED
    assert result.last_error_code == "ERR_AUTH_MISSING"


def test_workflow_engine_rejects_execution_for_disallowed_matcher_mode(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    recipe = store.save_recipe(_create_recipe(tmp_path))
    authorization.create_grant(
        recipe.recipe_id,
        policy={"matcher_modes": ["family"], "allowed_assets": []},
        runner="operator@example.com",
    )

    input_pdf = tmp_path / "in" / "packet.pdf"
    input_pdf.parent.mkdir(parents=True, exist_ok=True)
    input_pdf.write_bytes(b"%PDF-1.4\n%mock\n")

    engine = WorkflowEngine()
    engine.start()
    job = engine.enqueue_path(str(input_pdf), recipe_id=recipe.recipe_id)

    monkeypatch.setattr(
        "desktop_app.workflows.engine.matcher.evaluate_match",
        lambda *_args, **_kwargs: matcher.MatchResult(models.MatchClass.EXACT.value, 1.0, {"kind": "exact"}),
    )

    result = engine.run_job(job.job_id, actor="operator", action_subject="operator@example.com")

    assert result.state == models.WorkflowState.FAILED
    assert result.last_error_code == authorization.REASONS["matcher_mode_mismatch"]


def test_workflow_engine_rejects_execution_for_disallowed_signature_asset(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    recipe = store.save_recipe(_create_recipe(tmp_path))
    authorization.create_grant(
        recipe.recipe_id,
        policy={"matcher_modes": ["exact"], "allowed_assets": ["sig-allowed" ]},
        runner="operator@example.com",
    )

    input_pdf = tmp_path / "in" / "packet.pdf"
    input_pdf.parent.mkdir(parents=True, exist_ok=True)
    input_pdf.write_bytes(b"%PDF-1.4\n%mock\n")

    engine = WorkflowEngine()
    engine.start()
    job = engine.enqueue_path(str(input_pdf), recipe_id=recipe.recipe_id)

    monkeypatch.setattr(
        "desktop_app.workflows.engine.matcher.evaluate_match",
        lambda *_args, **_kwargs: matcher.MatchResult(models.MatchClass.EXACT.value, 1.0, {"kind": "exact"}),
    )

    result = engine.run_job(job.job_id, actor="operator", action_subject="operator@example.com")

    assert result.state == models.WorkflowState.FAILED
    assert result.last_error_code == authorization.REASONS["asset_not_allowed"]


def test_workflow_engine_rejects_execution_when_folder_scope_is_restricted(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    recipe = store.save_recipe(
        models.ControlledSigningRecipe.new(
            recipe_id="recipe-1",
            name="Legal Packet",
            status=models.RecipeStatus.ACTIVE.value,
            field_bindings=[_fresh_binding(str(tmp_path / "sig.png"))],
            input_folder=models.FolderConfig(
                folder_id="in-folder", path=str(tmp_path / "in"), recursive=False, require_stable_size=True
            ),
            output_folder=models.FolderConfig(
                folder_id="out-folder", path=str(tmp_path / "out"), recursive=False, require_stable_size=True
            ),
            review_folder=models.FolderConfig(
                folder_id="review-folder", path=str(tmp_path / "review"), recursive=False, require_stable_size=True
            ),
        )
    )
    tmp_path.joinpath("sig.png").write_bytes(b"signature")

    authorization.create_grant(
        recipe.recipe_id,
        policy={
            "matcher_modes": ["exact"],
            "allowed_assets": [str(tmp_path / "sig.png")],
            "input_folder_id": "different-in-folder",
        },
        runner="operator@example.com",
    )

    input_pdf = tmp_path / "in" / "packet.pdf"
    input_pdf.parent.mkdir(parents=True, exist_ok=True)
    input_pdf.write_bytes(b"%PDF-1.4\n%mock\n")

    engine = WorkflowEngine()
    engine.start()
    job = engine.enqueue_path(str(input_pdf), recipe_id=recipe.recipe_id)

    monkeypatch.setattr(
        "desktop_app.workflows.engine.matcher.evaluate_match",
        lambda *_args, **_kwargs: matcher.MatchResult(models.MatchClass.EXACT.value, 1.0, {"kind": "exact"}),
    )

    result = engine.run_job(job.job_id, actor="operator", action_subject="operator@example.com")

    assert result.state == models.WorkflowState.FAILED
    assert result.last_error_code == authorization.REASONS["folder_scope_mismatch"]
    expected_output = recipe.output_folder.path.rstrip("/") + "/" + f"{recipe.name.replace(' ', '_')}_{job.job_id}_signed.pdf"
    assert result.output_path_ref == expected_output


def test_workflow_engine_pause_blocks_execution(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    recipe = store.save_recipe(_create_recipe(tmp_path))
    authorization.create_grant(
        recipe.recipe_id,
        policy={"matcher_modes": ["exact"], "allowed_assets": []},
        runner="operator@example.com",
    )

    input_pdf = tmp_path / "in" / "packet.pdf"
    input_pdf.parent.mkdir(parents=True, exist_ok=True)
    input_pdf.write_bytes(b"%PDF-1.4\n%mock\n")

    engine = WorkflowEngine()
    engine.start()
    job = engine.enqueue_path(str(input_pdf), recipe_id=recipe.recipe_id)
    engine.pause()

    with pytest.raises(RuntimeError):
        _ = engine.run_job(job.job_id, actor="operator", action_subject="operator@example.com")


def test_workflow_engine_retry_and_cancel_paths(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    recipe = store.save_recipe(_create_recipe(tmp_path))
    grant = authorization.create_grant(
        recipe.recipe_id,
        policy={"matcher_modes": ["exact"], "allowed_assets": []},
        runner="operator@example.com",
    )
    store.save_grant(grant)

    job = store.save_job(
        models.WorkflowJob.new(
            job_id="job-manual",
            input_path_ref=str(tmp_path / "in" / "doc.pdf"),
            input_fingerprint="fp",
            recipe_id=recipe.recipe_id,
            recipe_version=recipe.version,
            state=models.WorkflowState.FAILED,
            grant_id=grant.grant_id,
        )
    )

    engine = WorkflowEngine()
    engine.start()
    engine._require_running()

    # Retry path should fail on non-PDF input unless evaluator is mocked to exact.
    monkeypatch.setattr(
        "desktop_app.workflows.engine.matcher.evaluate_match",
        lambda *_args, **_kwargs: matcher.MatchResult(models.MatchClass.EXACT.value, 1.0, {"reason": "manual"}),
    )
    monkeypatch.setattr("desktop_app.workflows.engine._page_geometry_map", lambda _path: [(612.0, 792.0)])
    monkeypatch.setattr(
        "desktop_app.workflows.engine.sign_pdf",
        lambda _in, output_path, _signatures: Path(output_path).write_bytes(b"%PDF-1.4\nok\n") or True,
    )

    output_dir = tmp_path / "out"
    output_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / "in" / "doc.pdf").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "in" / "doc.pdf").write_bytes(b"%PDF-1.4\n\n")

    retry_result = engine.retry_job("job-manual", actor="operator", action_subject="operator@example.com")
    assert retry_result.state == models.WorkflowState.COMPLETED

    # Quarantine action should move job into review for later handling.
    wait_job = store.save_job(
        models.WorkflowJob.new(
            job_id="job-review",
            input_path_ref=str(tmp_path / "in" / "doc2.pdf"),
            input_fingerprint="fp",
            recipe_id=recipe.recipe_id,
            recipe_version=recipe.version,
            state=models.WorkflowState.RETRY,
            grant_id=grant.grant_id,
        )
    )
    (tmp_path / "in" / "doc2.pdf").write_bytes(b"%PDF-1.4\n\n")
    wait_job = engine.quarantine_job(wait_job.job_id, actor="operator", action_subject="operator@example.com")
    assert wait_job.state == models.WorkflowState.NEEDS_REVIEW
    assert wait_job.last_error_code == "ERR_JOB_QUARANTINED"

    # Cancel should immediately hard-stop a queued job.
    pending = store.save_job(
        models.WorkflowJob.new(
            job_id="job-pending",
            input_path_ref=str(tmp_path / "in" / "doc3.pdf"),
            input_fingerprint="fp",
            recipe_id=recipe.recipe_id,
            recipe_version=recipe.version,
            state=models.WorkflowState.QUEUED,
            grant_id=grant.grant_id,
        )
    )
    cancelled = engine.cancel_job(pending.job_id, actor="operator", action_subject="operator@example.com")
    assert cancelled.state == models.WorkflowState.CANCELLED
    assert cancelled.last_error_code == "ERR_JOB_CANCELLED"


def test_authorization_rejects_expired_grant(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    recipe = store.save_recipe(_create_recipe(tmp_path))
    expired = authorization.create_grant(
        recipe.recipe_id,
        policy={"expires_at": "2000-01-01T00:00:00+00:00", "allowed_assets": []},
        runner="approver@example.com",
    )

    job = models.WorkflowJob.new(
        job_id="job-expired",
        input_path_ref=str(tmp_path / "in" / "doc.pdf"),
        input_fingerprint="fp",
        recipe_id=recipe.recipe_id,
        recipe_version=recipe.version,
        grant_id=expired.grant_id,
    )
    store.save_job(job)

    decision = authorization.require_authorization(
        job,
        subject="approver@example.com",
        requested_action="run_job",
    )

    assert not decision.allowed
    assert decision.code == authorization.REASONS["expired"]


def test_matcher_non_pdf_file_drives_review(monkeypatch, tmp_path: Path) -> None:
    recipe = models.ControlledSigningRecipe.new(recipe_id="r", name="R", status=models.RecipeStatus.ACTIVE.value)
    source = tmp_path / "notes.txt"
    source.write_text("just text")

    result = matcher.evaluate_match(recipe, str(source))

    assert result.match_class == models.MatchClass.REVIEW_ONLY.value
    assert result.evidence["error"] == "input_not_pdf"


def test_matcher_rejects_without_pdf_driver(monkeypatch, tmp_path: Path) -> None:
    recipe = models.ControlledSigningRecipe.new(recipe_id="r", name="R", status=models.RecipeStatus.ACTIVE.value)
    source = tmp_path / "broken.pdf"
    source.write_bytes(b"%PDF-1.4\n")

    monkeypatch.setattr("desktop_app.workflows.matcher._get_pikepdf", lambda: (__import__("types").SimpleNamespace()))

    result = matcher.evaluate_match(recipe, str(source))

    assert result.match_class == models.MatchClass.REVIEW_ONLY.value
    assert result.evidence["error"].startswith("pdf_open_failed")
