from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from desktop_app.workflows.workflow_utils import resolve_operator_subject
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
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
    QInputDialog,
)

from desktop_app.workflows import authorization, models, store


class GrantManager(QWidget):
    """Manage execution grants for recipe-based workflow authorization."""

    def __init__(self, default_subject: str | None = None) -> None:
        super().__init__()
        self._operator_subject = resolve_operator_subject(session_subject=default_subject)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        controls = QHBoxLayout()
        self.recipe_combo = QComboBox()
        self._load_recipes()

        self.approver_subject = QLineEdit()
        self.approver_subject.setText(self._operator_subject)

        self.runner_roles = QLineEdit()
        self.runner_roles.setPlaceholderText("role1, role2")
        self.runner_roles.setText("operator")

        self.max_jobs = QLineEdit()
        self.max_jobs.setPlaceholderText("optional")
        self.max_jobs.setText("")

        self.expires_at = QLineEdit()
        self.expires_at.setPlaceholderText("optional: ISO 8601")
        self.expires_at.setText((datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "+00:00"))

        self.create_btn = QPushButton("Create Grant")
        self.create_btn.clicked.connect(self._create_grant)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)

        controls.addWidget(QLabel("Recipe"))
        controls.addWidget(self.recipe_combo)
        controls.addWidget(QLabel("Approver subject"))
        controls.addWidget(self.approver_subject)
        controls.addWidget(QLabel("Runner roles"))
        controls.addWidget(self.runner_roles)
        controls.addWidget(self.create_btn)
        controls.addWidget(self.refresh_btn)
        controls.addStretch(1)
        layout.addLayout(controls)

        form = QFormLayout()
        form.addRow("Max jobs", self.max_jobs)
        form.addRow("Expires at", self.expires_at)
        layout.addLayout(form)

        self.grant_table = QTableWidget()
        self.grant_table.setColumnCount(10)
        self.grant_table.setHorizontalHeaderLabels(
            [
                "Grant ID",
                "Recipe",
                "Approver",
                "Runner Roles",
                "Allowed Assets",
                "Version",
                "Remaining",
                "Expires",
                "Active",
                "Last update",
            ]
        )
        self.grant_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.grant_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.grant_table.setAlternatingRowColors(True)
        layout.addWidget(self.grant_table)

        actions = QHBoxLayout()
        self.revoke_btn = QPushButton("Revoke selected")
        self.revoke_btn.clicked.connect(self._revoke_selected)
        self.refresh_btn_status = QLabel("No grant selected")
        actions.addWidget(self.revoke_btn)
        actions.addStretch(1)
        actions.addWidget(self.refresh_btn_status)
        layout.addLayout(actions)

    def _load_recipes(self) -> None:
        self.recipe_combo.clear()
        for recipe in store.list_recipes():
            label = f"{recipe.name} ({recipe.recipe_id})"
            if not recipe.name:
                label = recipe.recipe_id
            self.recipe_combo.addItem(label, userData=recipe.recipe_id)
        if self.recipe_combo.count() == 0:
            self.recipe_combo.addItem("No recipes yet", userData="")

    def refresh(self) -> None:
        self._load_recipes()
        grants = store.list_grants(active_only=False)
        self.grant_table.setRowCount(len(grants))
        for row, grant in enumerate(grants):
            self.grant_table.setItem(row, 0, QTableWidgetItem(grant.grant_id))
            self.grant_table.setItem(row, 1, QTableWidgetItem(grant.recipe_id))
            self.grant_table.setItem(row, 2, QTableWidgetItem(grant.approver_subject))
            self.grant_table.setItem(row, 3, QTableWidgetItem(", ".join(grant.runner_roles)))
            self.grant_table.setItem(row, 4, QTableWidgetItem(", ".join(grant.allowed_assets) or "-"))
            self.grant_table.setItem(row, 5, QTableWidgetItem(str(grant.recipe_version)))
            self.grant_table.setItem(row, 6, QTableWidgetItem(self._remaining_jobs(grant)))
            self.grant_table.setItem(row, 7, QTableWidgetItem(grant.expires_at or "-"))
            self.grant_table.setItem(row, 8, QTableWidgetItem("yes" if grant.is_active else "no"))
            self.grant_table.setItem(row, 9, QTableWidgetItem(grant.updated_at or ""))

            for col in range(self.grant_table.columnCount()):
                item = self.grant_table.item(row, col)
                if item is not None:
                    item.setData(Qt.ItemDataRole.UserRole, grant.grant_id)

        self.grant_table.resizeColumnsToContents()
        self._update_status(len(grants))

    def _update_status(self, grant_count: int) -> None:
        self.refresh_btn_status.setText(f"Visible grants: {grant_count}")

    def _parse_selected_grant_id(self) -> str:
        selected_rows = self.grant_table.selectionModel().selectedRows() if self.grant_table.selectionModel() else []
        if not selected_rows:
            raise ValueError("No grant selected")
        item = self.grant_table.item(selected_rows[0].row(), 0)
        if item is None:
            raise ValueError("Could not resolve grant")
        grant_id = item.data(Qt.ItemDataRole.UserRole)
        if not grant_id:
            raise ValueError("Could not resolve grant id")
        return str(grant_id)

    def _create_grant(self) -> None:
        recipe_id = self.recipe_combo.currentData()
        if not recipe_id:
            QMessageBox.warning(self, "Missing recipe", "Create a recipe before creating grants.")
            return

        recipe = store.get_recipe(recipe_id)
        if recipe is None:
            QMessageBox.warning(self, "Recipe missing", "Selected recipe is no longer available.")
            return

        approver = self.approver_subject.text().strip()
        if not approver:
            QMessageBox.warning(self, "Missing approver", "Approver subject is required.")
            return

        roles = [item.strip() for item in self.runner_roles.text().split(",") if item.strip()]
        if not roles:
            roles = ["operator"]

        allowed_assets: List[str] = []
        for binding in recipe.field_bindings:
            if binding.signature_asset_ref:
                allowed_assets.append(binding.signature_asset_ref)

        max_jobs: Optional[int] = None
        max_jobs_text = self.max_jobs.text().strip()
        if max_jobs_text:
            try:
                max_jobs = int(max_jobs_text)
            except ValueError:
                QMessageBox.warning(self, "Invalid max jobs", "max_jobs must be an integer or empty.")
                return
            if max_jobs < 0:
                QMessageBox.warning(self, "Invalid max jobs", "max_jobs must be 0 or greater.")
                return

        expires = self.expires_at.text().strip() or None
        if expires is not None:
            try:
                datetime.fromisoformat(expires.replace("Z", "+00:00"))
            except ValueError:
                QMessageBox.warning(self, "Invalid expiry", "Use ISO format, for example 2026-12-31T23:59:59+00:00")
                return

        actor = approver.strip() or self._operator_subject
        try:
            authorization.create_grant(
                recipe.recipe_id,
                policy={
                    "matcher_modes": [recipe.document_matcher.get("kind", "exact")],
                    "allowed_assets": allowed_assets,
                    "runner_roles": roles,
                    "input_folder_id": recipe.input_folder.folder_id,
                    "output_folder_id": recipe.output_folder.folder_id,
                    "max_jobs": max_jobs,
                    "expires_at": expires,
                },
                runner=actor,
            )
        except Exception as exc:
            QMessageBox.warning(self, "Unable to create grant", str(exc))
            return

        QMessageBox.information(self, "Grant created", "Grant created successfully.")
        self.refresh()

    def _revoke_selected(self) -> None:
        try:
            grant_id = self._parse_selected_grant_id()
        except ValueError as exc:
            QMessageBox.information(self, "No grant selected", str(exc))
            return

        reason, accepted = QInputDialog.getText(
            self,
            "Revoke reason",
            "Why are you revoking this grant?",
            text="revoked by operator",
        )
        if not accepted:
            return

        actor = self.approver_subject.text().strip() or self._operator_subject
        store.revoke_grant(grant_id, actor=actor, reason=reason or "revoked by operator")
        QMessageBox.information(self, "Grant revoked", f"Grant {grant_id} revoked.")
        self.refresh()

    def _remaining_jobs(self, grant: models.ExecutionGrant) -> str:
        if grant.max_jobs is None:
            return "unlimited"
        consumed = authorization.count_jobs_for_grant(grant.grant_id)
        remaining = grant.max_jobs - consumed
        if remaining < 0:
            remaining = 0
        return str(remaining)


__all__ = ["GrantManager"]
