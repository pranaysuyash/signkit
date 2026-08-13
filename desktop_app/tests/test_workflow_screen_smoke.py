from __future__ import annotations

from pathlib import Path

import pytest
from unittest.mock import patch


PySide6 = pytest.importorskip("PySide6")


def _configure_store_path(monkeypatch, path: Path) -> None:
    from desktop_app.workflows import store

    monkeypatch.setattr(store, "APP_DIR", path)
    monkeypatch.setattr(store, "WORKFLOW_STORE_FILE", path / "workflow_store.json")


def _seed_template_store(monkeypatch, path: Path) -> None:
    from desktop_app.pdf import template_store

    monkeypatch.setattr(template_store, "APP_DIR", path)
    monkeypatch.setattr(template_store, "TEMPLATES_FILE", path / "pdf_templates.json")
    template_store.save_template(
        template_store.SignaturePlacementTemplate(
            template_id="template-1",
            name="Signer One Template",
            signature_path="sig-asset-1",
            page_index=0,
            x_ratio=0.1,
            y_ratio=0.2,
            width_ratio=0.3,
            height_ratio=0.07,
            field_type="signature",
            field_label="Signer One",
        )
    )


def _seed_recipe_and_job(
    *,
    monkeypatch_obj,
    tmp_path: Path,
    subject: str,
) -> tuple[models.ControlledSigningRecipe, models.ExecutionGrant, models.WorkflowJob]:
    """Create an active recipe, a grant, and a queued job in the local store."""
    from dataclasses import replace
    from desktop_app.workflows import authorization, models, store

    _configure_store_path(monkeypatch_obj, tmp_path)

    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()

    signature_path = tmp_path / "sig.png"
    signature_path.write_bytes(b"sig")

    recipe = store.save_recipe(
        models.ControlledSigningRecipe.new(
            recipe_id="recipe-auth",
            name="Auth Recipe",
            status=models.RecipeStatus.ACTIVE.value,
            field_bindings=[
                models.SignatureFieldBinding.from_legacy_values(
                    signature_path=str(signature_path),
                    page_index=0,
                    x_ratio=0.1,
                    y_ratio=0.2,
                    width_ratio=0.25,
                    height_ratio=0.06,
                    field_label="Signer",
                )
            ],
            input_folder=models.FolderConfig(folder_id="in", path=str(in_dir), recursive=False),
            output_folder=models.FolderConfig(folder_id="out", path=str(out_dir), recursive=False),
        )
    )

    grant = authorization.create_grant(
        recipe.recipe_id,
        policy={"matcher_modes": ["exact"], "allowed_assets": [str(signature_path)]},
        runner=subject,
    )
    store.save_grant(grant)

    input_pdf = in_dir / "document.pdf"
    input_pdf.write_bytes(b"%PDF-1.4\n")

    job = store.save_job(
        models.WorkflowJob.new(
            job_id="job-auth",
            input_path_ref=str(input_pdf),
            input_fingerprint="fp1",
            recipe_id=recipe.recipe_id,
            recipe_version=recipe.version,
            grant_id=grant.grant_id,
            state=models.WorkflowState.QUEUED,
        )
    )
    return recipe, grant, replace(job, output_path_ref=job.output_path_ref)


def test_workflow_console_refresh_smoke(qapp, monkeypatch, tmp_path: Path) -> None:
    """Dashboard should initialize and refresh with a clean store."""
    from desktop_app.views.main_window_parts.workflow_console import WorkflowConsole
    from desktop_app.workflows import store

    _configure_store_path(monkeypatch, tmp_path)
    store.clear_store()

    console = WorkflowConsole()
    console.refresh()

    assert "Queued" in console._summary.text() and "Active Grants" in console._summary.text()
    assert console.job_table.rowCount() == 0
    assert console.job_table.columnCount() == 8
    assert console.recover_stale_btn.text() == "Recover stale"


def test_workflow_console_authorization_blocks_actions_for_mismatched_subject(qapp, monkeypatch, tmp_path: Path) -> None:
    """Unauthorized subjects should see disabled run/retry/cancel actions and auth status detail."""
    from desktop_app.workflows import store
    from desktop_app.views.main_window_parts.workflow_console import WorkflowConsole

    _configure_store_path(monkeypatch, tmp_path)
    store.clear_store()
    _, _, job = _seed_recipe_and_job(monkeypatch_obj=monkeypatch, tmp_path=tmp_path, subject="approved@team.io")

    console = WorkflowConsole(default_subject="other@team.io")
    console.refresh()
    console.job_table.selectRow(0)

    assert not console.run_btn.isEnabled()
    assert not console.retry_btn.isEnabled()
    assert not console.cancel_btn.isEnabled()
    assert not console.quarantine_btn.isEnabled()
    assert "Subject is not authorized for this grant" in console._auth_status.text()

    console.operator_subject.setText("approved@team.io")
    assert console.run_btn.isEnabled()

    authorized, reason = console._action_allowed("run_job")
    assert authorized
    assert reason == ""

    # Ensure helper path uses resolved job subject.
    assert console._current_subject() == "approved@team.io"
    assert console._selected_job() == store.get_job(job.job_id)


def test_workflow_console_run_job_blocks_unauthorized_subject(qapp, monkeypatch, tmp_path: Path) -> None:
    """Blocked actions should not call engine handlers until authorization passes."""
    from dataclasses import replace

    from desktop_app.views.main_window_parts.workflow_console import WorkflowConsole
    from desktop_app.workflows import models, store

    _configure_store_path(monkeypatch, tmp_path)
    store.clear_store()
    _, _, job = _seed_recipe_and_job(monkeypatch_obj=monkeypatch, tmp_path=tmp_path, subject="approved@team.io")

    warnings: list[str] = []

    def _capture_warning(*args, **kwargs):
        if args:
            message = args[2] if len(args) > 2 else ""
        else:
            message = kwargs.get("text", "")
        warnings.append(str(message))

    monkeypatch.setattr("desktop_app.views.main_window_parts.workflow_console.QMessageBox.warning", _capture_warning)
    monkeypatch.setattr(
        "desktop_app.views.main_window_parts.workflow_console.QMessageBox.information",
        lambda *args, **kwargs: None,
    )
    called = {"run": 0}
    monkeypatch.setattr(
        "desktop_app.views.main_window_parts.workflow_console.WorkflowEngine.run_job",
        lambda *args, **kwargs: called.__setitem__("run", called["run"] + 1) or replace(store.get_job(job.job_id), state=models.WorkflowState.FAILED),
    )

    console = WorkflowConsole(default_subject="other@team.io")
    console.refresh()
    console.job_table.selectRow(0)
    console._run_selected_job()

    assert called["run"] == 0
    assert warnings and "Run blocked" in warnings[0]
    assert any("ERR_AUTH_SUBJECT_MISMATCH" in message for message in warnings)


def test_workflow_console_run_job_calls_engine_for_authorized_subject(qapp, monkeypatch, tmp_path: Path) -> None:
    """Authorized subject should invoke engine.run_job when action is accepted."""
    from dataclasses import replace

    from desktop_app.views.main_window_parts.workflow_console import WorkflowConsole
    from desktop_app.workflows import models, store

    _configure_store_path(monkeypatch, tmp_path)
    store.clear_store()
    _, _, job = _seed_recipe_and_job(monkeypatch_obj=monkeypatch, tmp_path=tmp_path, subject="approved@team.io")

    monkeypatch.setattr(
        "desktop_app.views.main_window_parts.workflow_console.QMessageBox.information",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "desktop_app.views.main_window_parts.workflow_console.QMessageBox.warning",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "desktop_app.views.main_window_parts.workflow_console.check_and_enforce_workflow_automation_license",
        lambda parent: True,
    )

    calls: list[tuple[str, str, str]] = []
    updated = replace(store.get_job(job.job_id), state=models.WorkflowState.COMPLETED, last_error_code=None)
    monkeypatch.setattr(
        "desktop_app.views.main_window_parts.workflow_console.WorkflowEngine.run_job",
        lambda _self, job_id, *, actor, action_subject: (
            calls.append((job_id, actor, action_subject)),
            updated,
        )[-1],
    )

    console = WorkflowConsole(default_subject="approved@team.io")
    console.refresh()
    console.job_table.selectRow(0)
    console._run_selected_job()

    assert calls == [(job.job_id, "approved@team.io", "approved@team.io")]

def test_workflow_console_open_actions_handle_missing_paths(qapp, monkeypatch, tmp_path: Path) -> None:
    """Open-input / open-output actions should surface missing-path guidance instead of crashing."""
    from desktop_app.views.main_window_parts.workflow_console import WorkflowConsole
    from desktop_app.workflows import models, store

    _configure_store_path(monkeypatch, tmp_path)
    store.clear_store()

    in_dir = tmp_path / "in"
    in_dir.mkdir()
    output_dir = tmp_path / "out"
    output_dir.mkdir()

    recipe = store.save_recipe(
        models.ControlledSigningRecipe.new(
            recipe_id="r-1",
            name="Action Recipe",
            status=models.RecipeStatus.ACTIVE.value,
            input_folder=models.FolderConfig(folder_id="in", path=str(in_dir), recursive=False),
            output_folder=models.FolderConfig(folder_id="out", path=str(output_dir), recursive=False),
            field_bindings=[
                models.SignatureFieldBinding.from_legacy_values(
                    signature_path="sig-asset-1",
                    page_index=0,
                    x_ratio=0.1,
                    y_ratio=0.2,
                    width_ratio=0.25,
                    height_ratio=0.06,
                    field_label="Signer",
                )
            ],
        )
    )

    job = store.save_job(
        models.WorkflowJob.new(
            job_id="job-1",
            input_path_ref=str(in_dir / "missing.pdf"),
            input_fingerprint="x",
            recipe_id=recipe.recipe_id,
            recipe_version=recipe.version,
        )
    )

    console = WorkflowConsole()
    console.refresh()

    # Select the single row.
    console.job_table.selectRow(0)

    messages: list[str] = []

    def _append_message(*args, **kwargs):
        if len(args) > 2:
            messages.append(str(args[2]))
            return None
        if "text" in kwargs:
            messages.append(str(kwargs["text"]))

    monkeypatch.setattr("desktop_app.views.main_window_parts.workflow_console.QMessageBox.information", _append_message)
    monkeypatch.setattr("desktop_app.views.main_window_parts.workflow_console.QMessageBox.warning", _append_message)
    monkeypatch.setattr("desktop_app.views.main_window_parts.workflow_console.QDesktopServices.openUrl", lambda _url: True)

    console._open_selected_job_input()
    console._open_selected_job_output()

    assert any("not found" in str(msg) for msg in messages) or any("not available" in str(msg) for msg in messages)


def test_workflow_console_open_actions_open_real_files(qapp, monkeypatch, tmp_path: Path) -> None:
    """When a job has real file paths, open actions should call desktop open only after resolution."""
    from desktop_app.views.main_window_parts.workflow_console import WorkflowConsole
    from desktop_app.workflows import models, store

    _configure_store_path(monkeypatch, tmp_path)
    store.clear_store()

    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()
    input_pdf = in_dir / "doc.pdf"
    output_pdf = out_dir / "doc_signed.pdf"
    input_pdf.write_bytes(b"%PDF-1.4\n")
    output_pdf.write_bytes(b"%PDF-1.4\n")

    recipe = store.save_recipe(
        models.ControlledSigningRecipe.new(
            recipe_id="r-2",
            name="Action Recipe",
            status=models.RecipeStatus.ACTIVE.value,
            input_folder=models.FolderConfig(folder_id="in", path=str(in_dir), recursive=False),
            output_folder=models.FolderConfig(folder_id="out", path=str(out_dir), recursive=False),
            field_bindings=[
                models.SignatureFieldBinding.from_legacy_values(
                    signature_path="sig-asset-1",
                    page_index=0,
                    x_ratio=0.1,
                    y_ratio=0.2,
                    width_ratio=0.25,
                    height_ratio=0.06,
                    field_label="Signer",
                )
            ],
        )
    )

    saved_job = store.save_job(
        models.WorkflowJob.new(
            job_id="job-2",
            input_path_ref=str(input_pdf),
            input_fingerprint="x",
            recipe_id=recipe.recipe_id,
            recipe_version=recipe.version,
            state=models.WorkflowState.COMPLETED,
        )
    )
    from dataclasses import replace

    store.save_job(replace(saved_job, output_path_ref=str(output_pdf)))

    console = WorkflowConsole()
    console.refresh()
    console.job_table.selectRow(0)

    opened_urls: list[str] = []

    def _fake_open_url(url) -> bool:
        opened_urls.append(str(url.toString()))
        return True

    monkeypatch.setattr("desktop_app.views.main_window_parts.workflow_console.QMessageBox.warning", lambda *_, **__: None)
    monkeypatch.setattr("desktop_app.views.main_window_parts.workflow_console.QMessageBox.information", lambda *_, **__: None)
    monkeypatch.setattr("desktop_app.views.main_window_parts.workflow_console.QDesktopServices.openUrl", _fake_open_url)

    console._open_selected_job_input()
    console._open_selected_job_output()

    assert len(opened_urls) == 2


def test_recipe_builder_save_recipe_smoke(qapp, monkeypatch, tmp_path: Path) -> None:
    """Recipe builder should persist a drafted recipe with valid required fields."""
    from desktop_app.views.main_window_parts.recipe_builder import RecipeBuilder
    from desktop_app.workflows import store
    from desktop_app.workflows import models

    _configure_store_path(monkeypatch, tmp_path)
    store.clear_store()

    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()

    builder = RecipeBuilder()
    builder.name_input.setText("WIP Legal Packet")
    builder.input_folder.setText(str(in_dir))
    builder.output_folder.setText(str(out_dir))
    builder.matcher_mode.setCurrentText("exact")

    row = 0
    builder.fields.item(row, 0).setText("Approver")
    builder.fields.item(row, 1).setText("sig-asset-1")
    builder.fields.item(row, 2).setText("0")
    builder.fields.item(row, 3).setText("0.1")
    builder.fields.item(row, 4).setText("0.2")
    builder.fields.item(row, 5).setText("0.25")
    builder.fields.item(row, 6).setText("0.06")

    # Block modal dialogs in headless CI.
    with patch("desktop_app.views.main_window_parts.recipe_builder.QMessageBox.information"), patch(
        "desktop_app.views.main_window_parts.recipe_builder.QMessageBox.warning"
    ):
        builder._save_recipe()

    recipes = store.list_recipes()
    assert len(recipes) == 1
    assert recipes[0].name == "WIP Legal Packet"
    assert recipes[0].status == models.RecipeStatus.DRAFT.value
    assert len(recipes[0].field_bindings) == 1
    assert recipes[0].field_bindings[0].field_label == "role:Approver"


def test_recipe_builder_save_and_activate_recipe_smoke(qapp, monkeypatch, tmp_path: Path) -> None:
    """Save & Activate path should persist recipe as active."""
    from desktop_app.views.main_window_parts.recipe_builder import RecipeBuilder
    from desktop_app.workflows import store
    from desktop_app.workflows import models

    _configure_store_path(monkeypatch, tmp_path)
    store.clear_store()

    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()

    builder = RecipeBuilder()
    builder.name_input.setText("Auto Activated Packet")
    builder.input_folder.setText(str(in_dir))
    builder.output_folder.setText(str(out_dir))
    builder.matcher_mode.setCurrentText("exact")

    row = 0
    builder.fields.item(row, 0).setText("Approver")
    builder.fields.item(row, 1).setText("sig-asset-1")
    builder.fields.item(row, 2).setText("0")
    builder.fields.item(row, 3).setText("0.1")
    builder.fields.item(row, 4).setText("0.2")
    builder.fields.item(row, 5).setText("0.25")
    builder.fields.item(row, 6).setText("0.06")

    with patch("desktop_app.views.main_window_parts.recipe_builder.QMessageBox.information"), patch(
        "desktop_app.views.main_window_parts.recipe_builder.QMessageBox.warning"
    ):
        builder._save_and_activate_recipe()

    recipes = store.list_recipes()
    assert len(recipes) == 1
    assert recipes[0].name == "Auto Activated Packet"
    assert recipes[0].status == models.RecipeStatus.ACTIVE.value


def test_recipe_builder_import_template_into_recipe(qapp, monkeypatch, tmp_path: Path) -> None:
    """Importing from template should populate fields and then save as a recipe."""
    from desktop_app.views.main_window_parts.recipe_builder import RecipeBuilder
    from desktop_app.workflows import store
    from desktop_app.workflows import models

    _configure_store_path(monkeypatch, tmp_path)
    _seed_template_store(monkeypatch, tmp_path)
    store.clear_store()

    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()

    builder = RecipeBuilder()
    builder.name_input.setText("Template Import Packet")
    builder.input_folder.setText(str(in_dir))
    builder.output_folder.setText(str(out_dir))
    builder.matcher_mode.setCurrentText("exact")

    index = next((i for i in range(builder.import_template_combo.count()) if builder.import_template_combo.itemData(i) == "template-1"), -1)
    assert index > 0
    builder.import_template_combo.setCurrentIndex(index)

    with patch("desktop_app.views.main_window_parts.recipe_builder.QMessageBox.information"), patch(
        "desktop_app.views.main_window_parts.recipe_builder.QMessageBox.warning"
    ):
        builder._import_from_template()

    assert builder.fields.rowCount() >= 2
    assert builder.fields.item(builder.fields.rowCount() - 1, 1).text() == "sig-asset-1"
    assert builder.fields.item(builder.fields.rowCount() - 1, 0).text() == "Signer One"

    with patch("desktop_app.views.main_window_parts.recipe_builder.QMessageBox.information"), patch(
        "desktop_app.views.main_window_parts.recipe_builder.QMessageBox.warning"
    ):
        builder._save_recipe()

    recipes = store.list_recipes()
    assert len(recipes) == 1
    assert recipes[0].name == "Template Import Packet"
    assert recipes[0].status == models.RecipeStatus.DRAFT.value
    assert recipes[0].field_bindings[0].signature_asset_ref == "sig-asset-1"


def test_recipe_builder_load_edit_preserves_created_time(qapp, monkeypatch, tmp_path: Path) -> None:
    """Loading an existing recipe and saving should keep created_at intact."""
    from desktop_app.views.main_window_parts.recipe_builder import RecipeBuilder
    from desktop_app.workflows import store
    from desktop_app.workflows import models

    _configure_store_path(monkeypatch, tmp_path)
    store.clear_store()

    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()

    initial = store.save_recipe(
        models.ControlledSigningRecipe.new(
            recipe_id="r-edit",
            name="Editable",
            status=models.RecipeStatus.DRAFT.value,
            field_bindings=[
                models.SignatureFieldBinding.from_legacy_values(
                    signature_path="sig-asset-1",
                    page_index=0,
                    x_ratio=0.1,
                    y_ratio=0.2,
                    width_ratio=0.25,
                    height_ratio=0.06,
                    field_label="Signer",
                )
            ],
            input_folder=models.FolderConfig(folder_id="input", path=str(in_dir), recursive=True, require_stable_size=True),
            output_folder=models.FolderConfig(folder_id="output", path=str(out_dir), recursive=False, require_stable_size=True),
        )
    )

    builder = RecipeBuilder()
    index = builder.recipe_combo.findData("r-edit")
    assert index >= 0
    builder.recipe_combo.setCurrentIndex(index)

    assert builder.name_input.text() == "Editable"
    builder.name_input.setText("Editable V2")

    with patch("desktop_app.views.main_window_parts.recipe_builder.QMessageBox.information"), patch(
        "desktop_app.views.main_window_parts.recipe_builder.QMessageBox.warning"
    ):
        builder._save_recipe()

    latest = store.get_recipe("r-edit")
    assert latest is not None
    assert latest.name == "Editable V2"
    assert latest.created_at == initial.created_at


def test_recipe_builder_open_folder_warns_for_missing_path(qapp, monkeypatch, tmp_path: Path) -> None:
    """Open-folder action should warn when path does not exist."""
    from desktop_app.views.main_window_parts.recipe_builder import RecipeBuilder
    from desktop_app.workflows import store

    _configure_store_path(monkeypatch, tmp_path)
    store.clear_store()

    builder = RecipeBuilder()
    builder.input_folder.setText(str(tmp_path / "missing"))

    warnings: list[str] = []
    monkeypatch.setattr(
        "desktop_app.views.main_window_parts.recipe_builder.QMessageBox.warning",
        lambda *args, **kwargs: warnings.append(kwargs.get("text") or (args[2] if len(args) > 2 else "")),
    )

    builder._open_selected_folder(builder.input_folder)

    assert warnings and "not found" in str(warnings[0]).lower()
