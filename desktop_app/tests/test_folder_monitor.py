from pathlib import Path

from desktop_app.workflows import models, store
from desktop_app.workflows.folder_monitor import FolderMonitor
from desktop_app.workflows.engine import WorkflowEngine


def _configure_store_path(monkeypatch, path: Path) -> None:
    monkeypatch.setattr(store, "APP_DIR", path)
    monkeypatch.setattr(store, "WORKFLOW_STORE_FILE", path / "workflow_store.json")


def _create_active_recipe(tmp_path: Path) -> models.ControlledSigningRecipe:
    return models.ControlledSigningRecipe.new(
        recipe_id="r-1",
        name="R",
        status=models.RecipeStatus.ACTIVE.value,
        input_folder=models.FolderConfig(folder_id="in", path=str(tmp_path / "in"), recursive=False, require_stable_size=True),
        output_folder=models.FolderConfig(folder_id="out", path=str(tmp_path / "out"), recursive=False, require_stable_size=True),
        field_bindings=[],
    )


def test_folder_monitor_discovers_only_new_pdfs(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    recipe = _create_active_recipe(tmp_path)
    store.save_recipe(recipe)

    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()

    (in_dir / "one.pdf").write_bytes(b"%PDF-1.4\n%\n")
    (in_dir / "two.txt").write_text("ignore")

    monitor = FolderMonitor(engine=WorkflowEngine())
    result = monitor.scan(recipe_id="r-1")

    assert result.discovered == 1
    assert result.enqueued == 1
    assert result.skipped == 1  # non-pdf
    assert store.list_jobs().pop().input_path_ref.endswith("one.pdf")


def test_folder_monitor_skips_already_queued(monkeypatch, tmp_path: Path) -> None:
    _configure_store_path(monkeypatch, tmp_path)
    recipe = _create_active_recipe(tmp_path)
    recipe = store.save_recipe(recipe)

    in_dir = tmp_path / "in"
    in_dir.mkdir()
    pdf = in_dir / "one.pdf"
    pdf.write_bytes(b"%PDF-1.4\n%\n")

    existing = models.WorkflowJob.new(
        job_id="j-1",
        input_path_ref=str(pdf),
        input_fingerprint="fp",
        recipe_id=recipe.recipe_id,
        recipe_version=recipe.version,
        state=models.WorkflowState.QUEUED,
    )
    store.save_job(existing)

    monitor = FolderMonitor(engine=WorkflowEngine())
    result = monitor.scan(recipe_id="r-1")

    assert result.enqueued == 0
    assert result.already_scheduled == 1


def test_verify_output_rejects_invalid_outputs(tmp_path: Path) -> None:
    from desktop_app.workflows.verifier import verify_output

    source = tmp_path / "in.pdf"
    output = tmp_path / "out.pdf"
    source.write_bytes(b"%PDF-1.4\nA")
    output.write_bytes(b"")

    result = verify_output(str(source), str(output))
    assert not result.ok
    assert result.reason == "output_empty"

    output.write_bytes(b"%PDF-1.4\nA")
    result = verify_output(str(source), str(output))
    assert not result.ok
    assert result.reason == "unchanged_digest"
