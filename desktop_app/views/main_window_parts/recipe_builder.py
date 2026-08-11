"""Operator recipe builder for recurring PDF signing workflows."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import List, Optional
import os

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from desktop_app.pdf import template_store
from desktop_app.workflows import models, store
from desktop_app.workflows.workflow_utils import folder_id_from_path


class RecipeBuilder(QWidget):
    """A lightweight recipe creation screen for v1 controlled workflows."""

    def __init__(self) -> None:
        super().__init__()
        self._editing_recipe_id: Optional[str] = None
        self._editing_created_at: Optional[str] = None
        self._populating_combo = False
        self._setup_ui()
        self.refresh()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        selector_row = QHBoxLayout()
        self.recipe_combo = QComboBox()
        self.recipe_combo.currentIndexChanged.connect(self._on_recipe_selection_change)
        self.new_recipe_btn = QPushButton("New Recipe")
        self.new_recipe_btn.clicked.connect(self._start_new_recipe)
        selector_row.addWidget(QLabel("Existing Recipes"))
        selector_row.addWidget(self.recipe_combo)
        selector_row.addWidget(self.new_recipe_btn)
        selector_row.addStretch(1)
        layout.addLayout(selector_row)

        self.name_input = QLineEdit()
        self.matcher_mode = QComboBox()
        self.matcher_mode.addItems(["exact", "family", "review_only"])
        self.input_folder = QLineEdit()
        self.output_folder = QLineEdit()
        self.review_folder = QLineEdit()
        self.status_label = QLabel("No recipe loaded.")
        self.recipe_table_status = QLabel("")
        self.recipe_table_status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.input_folder.setPlaceholderText("Unsigned docs folder (watched source)")
        self.output_folder.setPlaceholderText("Signed docs folder (destination output)")
        self.review_folder.setPlaceholderText("Optional review queue folder")
        self.folder_guidance = QLabel(
            "Define: unsigned docs folder -> processing -> signed docs folder. "
            "Optional review folder receives items flagged for manual review."
        )
        self.folder_guidance.setStyleSheet("color: #5f6368; font-size: 11px;")
        self.folder_guidance.setWordWrap(True)
        layout.addWidget(self.folder_guidance)

        form = QFormLayout()
        form.addRow("Recipe Name", self.name_input)
        form.addRow("Matcher Mode", self.matcher_mode)
        layout.addLayout(form)

        for key, input_box in (
            ("Unsigned Docs Folder", self.input_folder),
            ("Signed Docs Output Folder", self.output_folder),
            ("Review Folder (optional)", self.review_folder),
        ):
            browse_layout = QHBoxLayout()
            browse_btn = QPushButton("Browse")
            browse_btn.clicked.connect(lambda _checked=False, target=input_box: self._pick_folder(target))
            browse_layout.addWidget(input_box)
            browse_layout.addWidget(browse_btn)
            layout.addWidget(QLabel(key))
            layout.addLayout(browse_layout)

            open_btn = QPushButton("Open folder")
            open_btn.clicked.connect(lambda _checked=False, target=input_box: self._open_selected_folder(target))
            browse_layout.addWidget(open_btn)

        self.fields = QTableWidget()
        self.fields.setColumnCount(7)
        self.fields.setHorizontalHeaderLabels(["Role", "Vault Asset ID", "Page", "X Ratio", "Y Ratio", "W Ratio", "H Ratio"])
        self.fields.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.fields.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.EditKeyPressed)
        self.matcher_mode.setToolTip("Choose how incoming documents are matched to the active recipe")
        self.fields.setToolTip("Role-based signature space mapping. Keep role names consistent across templates and recipes.")
        layout.addWidget(self.fields)

        row_controls = QHBoxLayout()
        add_binding = QPushButton("Add Field")
        add_binding.clicked.connect(self._add_field_row)
        remove_binding = QPushButton("Remove Field")
        remove_binding.clicked.connect(self._remove_selected_field)
        self.import_template_combo = QComboBox()
        self.import_template_combo.setMinimumWidth(260)
        self.import_template_btn = QPushButton("Import from Template")
        self.import_template_btn.clicked.connect(self._import_from_template)
        row_controls.addWidget(add_binding)
        row_controls.addWidget(remove_binding)
        row_controls.addSpacing(20)
        row_controls.addWidget(QLabel("Template"))
        row_controls.addWidget(self.import_template_combo)
        row_controls.addWidget(self.import_template_btn)
        row_controls.addStretch(1)
        layout.addLayout(row_controls)

        action_row = QHBoxLayout()
        self.dry_run_btn = QPushButton("Dry Run")
        self.save_btn = QPushButton("Save Draft Recipe")
        self.save_and_activate_btn = QPushButton("Save & Activate Recipe")
        self.dry_run_btn.clicked.connect(self._run_dry_run)
        self.save_btn.clicked.connect(self._save_recipe)
        self.save_and_activate_btn.clicked.connect(self._save_and_activate_recipe)
        action_row.addWidget(self.dry_run_btn)
        action_row.addWidget(self.save_btn)
        action_row.addWidget(self.save_and_activate_btn)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        self.dry_run_result = QLabel("Dry-run output: not run yet.")
        self.dry_run_result.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.dry_run_result)
        layout.addWidget(self.recipe_table_status)
        layout.addWidget(self.status_label)

        for _ in range(2):
            self._add_field_row()

    def _safe_combo_data(self, combo: QComboBox) -> str:
        current_data = combo.currentData()
        return "" if current_data is None else str(current_data)

    def _pick_folder(self, target: QLineEdit) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select folder")
        if directory:
            target.setText(directory)

    def refresh(self) -> None:
        """Reload store-backed recipes and templates."""
        selected_recipe_id = self._safe_combo_data(self.recipe_combo) if hasattr(self, "recipe_combo") else ""
        selected_template_id = self._safe_combo_data(self.import_template_combo) if hasattr(self, "import_template_combo") else ""

        self._load_recipes()
        self._load_templates()

        if selected_recipe_id:
            index = self.recipe_combo.findData(selected_recipe_id)
            if index >= 0:
                self.recipe_combo.setCurrentIndex(index)
            elif self.recipe_combo.count() > 0:
                self.recipe_combo.setCurrentIndex(0)
        if selected_template_id:
            index = self.import_template_combo.findData(selected_template_id)
            if index >= 0:
                self.import_template_combo.setCurrentIndex(index)

        if self._editing_recipe_id:
            self._load_selected_recipe()
        elif self.recipe_combo.currentIndex() == 0 and self.recipe_combo.count() > 1:
            # Keep an existing selected recipe by default.
            first_recipe = self.recipe_combo.itemData(1)
            if first_recipe:
                self._load_selected_recipe_by_id(str(first_recipe))
        else:
            self._start_new_recipe()

    def _load_recipes(self) -> None:
        self._populating_combo = True
        self.recipe_combo.clear()
        self.recipe_combo.addItem("No selection", userData="")
        recipes = store.list_recipes()
        for recipe in recipes:
            label = f"{recipe.name} ({recipe.status})"
            if not recipe.name:
                label = recipe.recipe_id
            self.recipe_combo.addItem(label, userData=recipe.recipe_id)
        if self.recipe_combo.count() == 0:
            self.recipe_combo.addItem("No recipes found", userData="")
        self._populating_combo = False

    def _load_templates(self) -> None:
        self.import_template_combo.clear()
        self.import_template_combo.addItem("Select template", userData="")
        for template in template_store.list_templates():
            self.import_template_combo.addItem(f"{template.name} ({template.template_id[:8]})", userData=template.template_id)
        self.import_template_btn.setEnabled(self.import_template_combo.count() > 1)

    def _on_recipe_selection_change(self) -> None:
        if self._populating_combo:
            return
        selected_id = self._safe_combo_data(self.recipe_combo)
        if not selected_id:
            self._start_new_recipe()
            return
        if selected_id == (self._editing_recipe_id or ""):
            return
        self._load_selected_recipe_by_id(selected_id)

    def _start_new_recipe(self) -> None:
        self._editing_recipe_id = None
        self._editing_created_at = None
        self._clear_fields()
        self._add_field_row()
        self.name_input.clear()
        self.matcher_mode.setCurrentText("exact")
        self.input_folder.clear()
        self.output_folder.clear()
        self.review_folder.clear()
        self.recipe_table_status.setText("Draft mode")
        self.status_label.setText("Ready for new recipe.")

    def _load_selected_recipe_by_id(self, recipe_id: str) -> None:
        recipe = store.get_recipe(recipe_id)
        if recipe is None:
            self.status_label.setText("Selected recipe no longer exists.")
            return

        self._editing_recipe_id = recipe.recipe_id
        self._editing_created_at = recipe.created_at
        self.name_input.setText(recipe.name)
        self.matcher_mode.setCurrentText((recipe.document_matcher or {}).get("kind", "exact"))
        self.input_folder.setText(recipe.input_folder.path)
        self.output_folder.setText(recipe.output_folder.path)
        self.review_folder.setText(recipe.review_folder.path if recipe.review_folder else "")
        self._set_bindings(recipe.field_bindings)
        self.recipe_table_status.setText(f"Loaded: {recipe.name} ({recipe.recipe_id})")
        self.status_label.setText("Recipe loaded for edit.")
        if self.fields.rowCount() == 0:
            self._add_field_row()

    def _load_selected_recipe(self) -> None:
        if self._editing_recipe_id:
            self._load_selected_recipe_by_id(self._editing_recipe_id)

    def _clear_fields(self) -> None:
        self.fields.setRowCount(0)

    def _set_bindings(self, bindings: List[models.SignatureFieldBinding]) -> None:
        self._clear_fields()
        for binding in bindings:
            self._append_binding_row(
                role=(binding.field_label or "").replace("role:", ""),
                signature_asset_ref=binding.signature_asset_ref,
                page_index=binding.page_index,
                x_ratio=binding.x_ratio,
                y_ratio=binding.y_ratio,
                width_ratio=binding.width_ratio,
                height_ratio=binding.height_ratio,
            )
        if self.fields.rowCount() == 0:
            self._add_field_row()

    def _append_binding_row(
        self,
        *,
        role: str,
        signature_asset_ref: str,
        page_index: int,
        x_ratio: float,
        y_ratio: float,
        width_ratio: float,
        height_ratio: float,
    ) -> None:
        row = self.fields.rowCount()
        self.fields.insertRow(row)
        values = [
            role,
            signature_asset_ref,
            str(page_index),
            str(x_ratio),
            str(y_ratio),
            str(width_ratio),
            str(height_ratio),
        ]
        for col, value in enumerate(values):
            self.fields.setItem(row, col, QTableWidgetItem(value))

    def _add_field_row(self) -> None:
        row = self.fields.rowCount()
        self.fields.insertRow(row)
        defaults = ["", "", "0", "0.1", "0.2", "0.25", "0.06"]
        for col, value in enumerate(defaults):
            self.fields.setItem(row, col, QTableWidgetItem(value))

    def _remove_selected_field(self) -> None:
        selected = self.fields.selectionModel().selectedRows()
        if not selected:
            return
        for idx in sorted((index.row() for index in selected), reverse=True):
            self.fields.removeRow(idx)
        if self.fields.rowCount() == 0:
            self._add_field_row()

    def _import_from_template(self) -> None:
        template_id = self._safe_combo_data(self.import_template_combo)
        if not template_id:
            QMessageBox.information(self, "Template required", "Choose a template before importing.")
            return

        template = template_store.get_template(template_id)
        if template is None:
            QMessageBox.warning(self, "Template missing", "Selected template no longer exists.")
            return

        if not template.field_bindings:
            QMessageBox.information(self, "Template empty", "Selected template has no saved bindings.")
            return

        for binding in template.field_bindings:
            self._append_binding_row(
                role=(binding.field_label or "Signer"),
                signature_asset_ref=binding.signature_asset_ref,
                page_index=binding.page_index,
                x_ratio=binding.x_ratio,
                y_ratio=binding.y_ratio,
                width_ratio=binding.width_ratio,
                height_ratio=binding.height_ratio,
            )
        self.status_label.setText(
            f"Imported {len(template.field_bindings)} placement(s) from template {template.name}."
        )

    def _open_selected_folder(self, target: QLineEdit) -> None:
        folder = target.text().strip()
        if not folder:
            QMessageBox.warning(self, "Folder required", "Set a folder path before opening it.")
            return

        if not os.path.isdir(folder):
            QMessageBox.warning(self, "Invalid folder", f"Folder not found: {folder}")
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _collect_bindings(self) -> List[models.SignatureFieldBinding]:
        rows = self.fields.rowCount()
        bindings: List[models.SignatureFieldBinding] = []
        for row in range(rows):
            role = (self.fields.item(row, 0).text() if self.fields.item(row, 0) else "").strip()
            asset = (self.fields.item(row, 1).text() if self.fields.item(row, 1) else "").strip()
            if not role and not asset:
                continue
            if not role or not asset:
                raise ValueError(f"Field row {row + 1}: role and vault asset ID are required.")

            page_text = (self.fields.item(row, 2).text() if self.fields.item(row, 2) else "0") or "0"
            x_text = (self.fields.item(row, 3).text() if self.fields.item(row, 3) else "0.1") or "0.1"
            y_text = (self.fields.item(row, 4).text() if self.fields.item(row, 4) else "0.2") or "0.2"
            w_text = (self.fields.item(row, 5).text() if self.fields.item(row, 5) else "0.25") or "0.25"
            h_text = (self.fields.item(row, 6).text() if self.fields.item(row, 6) else "0.06") or "0.06"

            page = int(page_text)
            x_ratio = float(x_text)
            y_ratio = float(y_text)
            w_ratio = float(w_text)
            h_ratio = float(h_text)
            if not (0.0 <= x_ratio <= 1.0 and 0.0 <= y_ratio <= 1.0 and 0.0 <= w_ratio <= 1.0 and 0.0 <= h_ratio <= 1.0):
                raise ValueError(f"Field row {row + 1}: coordinates must be ratios 0.0 to 1.0.")

            bindings.append(
                models.SignatureFieldBinding.from_legacy_values(
                    signature_path=asset,
                    page_index=page,
                    x_ratio=x_ratio,
                    y_ratio=y_ratio,
                    width_ratio=w_ratio,
                    height_ratio=h_ratio,
                    field_label=f"role:{role}",
                    field_type="signature",
                )
            )
        if not bindings:
            raise ValueError("At least one field binding is required.")
        return bindings

    def _validate_folder_pair(self, input_path: str, output_path: str) -> None:
        in_dir = Path(input_path.strip())
        out_dir = Path(output_path.strip())
        if not in_dir.exists() or not in_dir.is_dir():
            raise ValueError("Unsigned docs folder must exist.")
        if not out_dir.exists() or not out_dir.is_dir():
            raise ValueError("Signed output folder must exist.")
        if in_dir == out_dir:
            raise ValueError("Unsigned and signed folders must be different.")
        if in_dir.is_relative_to(out_dir) or out_dir.is_relative_to(in_dir):
            raise ValueError("Unsigned and signed folders cannot be nested.")

    def _validate_review_folder(self, review_path: str, input_path: str, output_path: str) -> None:
        if not review_path:
            return

        rev_dir = Path(review_path)
        if not rev_dir.exists() or not rev_dir.is_dir():
            raise ValueError("Review folder must exist.")

        in_dir = Path(input_path)
        out_dir = Path(output_path)
        if rev_dir == in_dir or rev_dir == out_dir:
            raise ValueError("Review folder should be separate from unsigned/signed folders.")
        if rev_dir.is_relative_to(in_dir) or in_dir.is_relative_to(rev_dir) or rev_dir.is_relative_to(out_dir) or out_dir.is_relative_to(rev_dir):
            raise ValueError("Review folder should not be nested inside source or output folders.")

    def _run_dry_run(self) -> None:
        try:
            in_path = self.input_folder.text().strip()
            out_path = self.output_folder.text().strip()
            review_path = self.review_folder.text().strip()
            self._validate_folder_pair(in_path, out_path)
            self._validate_review_folder(review_path, in_path, out_path)
            _ = self._collect_bindings()
            self.dry_run_result.setText(
                f"Dry run OK: matcher={self.matcher_mode.currentText()}, input={in_path}, output={out_path}"
            )
            self.dry_run_result.setStyleSheet("color: #4caf50;")
        except Exception as exc:
            self.dry_run_result.setText(f"Dry run blocked: {exc}")
            self.dry_run_result.setStyleSheet("color: #d32f2f;")

    def _build_recipe(self, *, status: models.RecipeStatus = models.RecipeStatus.DRAFT) -> models.ControlledSigningRecipe:
        recipe_name = self.name_input.text().strip()
        if not recipe_name:
            raise ValueError("Recipe name is required.")

        in_path = self.input_folder.text().strip()
        out_path = self.output_folder.text().strip()
        review_path = self.review_folder.text().strip()
        self._validate_folder_pair(in_path, out_path)
        self._validate_review_folder(review_path, in_path, out_path)

        bindings = self._collect_bindings()
        matcher_kind = self.matcher_mode.currentText().strip().lower()
        if matcher_kind not in {"exact", "family", "review_only"}:
            raise ValueError("Unsupported matcher mode.")

        review_folder: Optional[models.FolderConfig] = None
        if review_path:
            rev_dir = Path(review_path)
            review_folder = models.FolderConfig(
                folder_id=folder_id_from_path(str(rev_dir), namespace="review"),
                path=str(rev_dir),
                recursive=True,
                require_stable_size=True,
            )

        return models.ControlledSigningRecipe.new(
            recipe_id=self._editing_recipe_id,
            name=recipe_name,
            status=status.value,
            document_matcher={"kind": matcher_kind},
            input_folder=models.FolderConfig(
                folder_id=folder_id_from_path(str(in_path), namespace="input"),
                path=in_path,
                recursive=True,
                require_stable_size=True,
            ),
            output_folder=models.FolderConfig(
                folder_id=folder_id_from_path(str(out_path), namespace="output"),
                path=out_path,
                recursive=False,
                require_stable_size=True,
            ),
            review_folder=review_folder,
            field_bindings=bindings,
        )

    def _build_recipe_for_persistence(
        self, *, status: models.RecipeStatus
    ) -> models.ControlledSigningRecipe:
        recipe = self._build_recipe(status=status)
        if self._editing_created_at:
            recipe = replace(recipe, created_at=self._editing_created_at)
        return recipe

    def _save_recipe(self) -> None:
        try:
            recipe = self._build_recipe_for_persistence(status=models.RecipeStatus.DRAFT)
            saved = store.save_recipe(recipe)
            self.status_label.setText(f"Saved draft recipe: {saved.recipe_id}")
            self.status_label.setStyleSheet("color: #2e7d32;")
            self._editing_recipe_id = saved.recipe_id
            self._editing_created_at = saved.created_at
            self.refresh()
            QMessageBox.information(self, "Recipe saved", f"Recipe '{saved.name}' was saved as draft.")
        except Exception as exc:
            self.status_label.setText(f"Save blocked: {exc}")
            self.status_label.setStyleSheet("color: #c62828;")
            QMessageBox.warning(self, "Unable to save", str(exc))

    def _save_and_activate_recipe(self) -> None:
        try:
            recipe = self._build_recipe_for_persistence(status=models.RecipeStatus.ACTIVE)
            saved = store.save_recipe(recipe)
            self.status_label.setText(f"Saved active recipe: {saved.recipe_id}")
            self.status_label.setStyleSheet("color: #2e7d32;")
            self._editing_recipe_id = saved.recipe_id
            self._editing_created_at = saved.created_at
            self.refresh()
            QMessageBox.information(self, "Recipe activated", f"Recipe '{saved.name}' was saved as active.")
        except Exception as exc:
            self.status_label.setText(f"Activate blocked: {exc}")
            self.status_label.setStyleSheet("color: #c62828;")
            QMessageBox.warning(self, "Unable to save", str(exc))


__all__ = ["RecipeBuilder"]
