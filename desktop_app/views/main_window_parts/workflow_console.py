from __future__ import annotations

from collections import Counter
import os
from typing import Dict, List, Optional

from desktop_app.workflows.workflow_utils import resolve_operator_subject
from desktop_app.workflows import authorization
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QCheckBox,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QHBoxLayout,
    QGridLayout,
    QComboBox,
    QInputDialog,
    QSizePolicy,
)

from desktop_app.workflows import store, models
from desktop_app.workflows.folder_monitor import FolderMonitor
from desktop_app.workflows.engine import WorkflowEngine
from desktop_app.workflows.operator_content import outcome_message, state_label
from desktop_app.license.restrictions import check_and_enforce_workflow_automation_license


class WorkflowConsole(QWidget):
    """Minimal operator dashboard for workflow jobs and grants."""

    def __init__(self, default_subject: str | None = None) -> None:
        super().__init__()
        self._engine = WorkflowEngine()
        self._engine.start()
        self._operator_subject = resolve_operator_subject(session_subject=default_subject)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self._summary = QLabel()
        self._summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._summary)

        self._auth_status = QLabel("")
        self._auth_status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._auth_status)

        # Use two deliberate rows instead of one overflowing toolbar. This
        # keeps every operator action reachable at ordinary laptop widths and
        # makes the order of actions readable without relying on truncation.
        controls = QGridLayout()
        controls.setHorizontalSpacing(8)
        controls.setVerticalSpacing(6)
        self.operator_subject = QLineEdit(self._operator_subject)
        self.operator_subject.setPlaceholderText("operator subject")
        self.operator_subject.setMinimumWidth(220)
        self.operator_subject.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.operator_subject.textChanged.connect(self._on_subject_changed)
        self.state_filter = QComboBox()
        self.state_filter.addItem("All", userData=None)
        self.state_filter.addItem("Queued", userData=models.WorkflowState.QUEUED.value)
        self.state_filter.addItem("Needs Review", userData=models.WorkflowState.NEEDS_REVIEW.value)
        self.state_filter.addItem("Retry", userData=models.WorkflowState.RETRY.value)
        self.state_filter.addItem("Failed", userData=models.WorkflowState.FAILED.value)
        self.state_filter.addItem("Completed", userData=models.WorkflowState.COMPLETED.value)
        self.state_filter.currentIndexChanged.connect(self.refresh)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        self.run_btn = QPushButton("Run selected")
        self.run_btn.clicked.connect(self._run_selected_job)
        self.retry_btn = QPushButton("Retry selected")
        self.retry_btn.clicked.connect(self._retry_selected_job)
        self.open_input_btn = QPushButton("Open input")
        self.open_input_btn.clicked.connect(self._open_selected_job_input)
        self.open_output_btn = QPushButton("Open output")
        self.open_output_btn.clicked.connect(self._open_selected_job_output)
        self.quarantine_btn = QPushButton("Quarantine selected")
        self.quarantine_btn.clicked.connect(self._quarantine_selected_job)
        self.cancel_btn = QPushButton("Cancel selected")
        self.cancel_btn.clicked.connect(self._cancel_selected_job)
        self.scan_btn = QPushButton("Scan folders")
        self.scan_btn.clicked.connect(self._scan_folders)
        self.run_queued_btn = QPushButton("Run queued")
        self.run_queued_btn.clicked.connect(self._run_queued_jobs)
        self.auto_run_after_scan = QCheckBox("Auto-run queued after scan")
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self._toggle_pause)

        controls.addWidget(QLabel("Filter"), 0, 0)
        controls.addWidget(self.state_filter, 0, 1)
        controls.addWidget(QLabel("Run as subject"), 0, 2)
        controls.addWidget(self.operator_subject, 0, 3)
        controls.addWidget(self.refresh_btn, 0, 4)

        controls.addWidget(self.run_btn, 1, 0)
        controls.addWidget(self.retry_btn, 1, 1)
        controls.addWidget(self.auto_run_after_scan, 1, 2, 1, 2)
        controls.addWidget(self.pause_btn, 1, 4)

        controls.addWidget(self.open_input_btn, 2, 0)
        controls.addWidget(self.open_output_btn, 2, 1)
        controls.addWidget(self.quarantine_btn, 2, 2)
        controls.addWidget(self.cancel_btn, 2, 3)
        controls.addWidget(self.scan_btn, 2, 4)
        controls.addWidget(self.run_queued_btn, 2, 5)
        controls.setColumnStretch(3, 1)
        layout.addLayout(controls)

        self.job_table = QTableWidget()
        self.job_table.setColumnCount(8)
        self.job_table.setHorizontalHeaderLabels(
            ["Job ID", "Recipe", "Input", "Output", "State", "Match", "Attempts", "Last reason"]
        )
        self.job_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.job_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.job_table.setAlternatingRowColors(True)
        self.job_table.setSortingEnabled(True)
        self.job_table.itemSelectionChanged.connect(self._update_action_states)
        layout.addWidget(self.job_table)

    def _build_summary(self, jobs: List[models.WorkflowJob], grants_count: int) -> None:
        state_counts: Dict[str, int] = Counter(job.state.value for job in jobs)
        need_review_count = state_counts.get(models.WorkflowState.NEEDS_REVIEW.value, 0)
        retry_count = state_counts.get(models.WorkflowState.RETRY.value, 0)
        completed = state_counts.get(models.WorkflowState.COMPLETED.value, 0)
        failed = state_counts.get(models.WorkflowState.FAILED.value, 0)
        queued = state_counts.get(models.WorkflowState.QUEUED.value, 0)
        cancelled = state_counts.get(models.WorkflowState.CANCELLED.value, 0)
        lock_state = "Engine paused" if self._engine.is_paused() else "Engine running"

        self._summary.setText(
            " • ".join(
                [
                    f"{lock_state}",
                    f"Active Grants: {grants_count}",
                    f"Queued: {queued}",
                    f"Needs Review: {need_review_count}",
                    f"Retry: {retry_count}",
                    f"Completed: {completed}",
                    f"Failed: {failed}",
                    f"Cancelled: {cancelled}",
                    f"Total Jobs: {len(jobs)}",
                ]
            )
        )
        self.pause_btn.setText("Resume" if self._engine.is_paused() else "Pause")

    def _load_jobs(self) -> List[models.WorkflowJob]:
        selected_state = self.state_filter.currentData()
        if selected_state:
            return store.list_jobs(state=selected_state)
        return store.list_jobs()

    def refresh(self) -> None:
        """Reload store-backed job, grant, and event state."""
        jobs = self._load_jobs()
        grants = store.list_grants(active_only=True)
        self._build_summary(jobs=jobs, grants_count=len(grants))

        self.job_table.setRowCount(len(jobs))
        for row, job in enumerate(jobs):
            self.job_table.setItem(row, 0, QTableWidgetItem(job.job_id))
            self.job_table.setItem(row, 1, QTableWidgetItem(job.recipe_id))
            self.job_table.setItem(row, 2, QTableWidgetItem(job.input_path_ref))
            self.job_table.setItem(row, 3, QTableWidgetItem(job.output_path_ref or ""))
            self.job_table.setItem(row, 4, QTableWidgetItem(state_label(job.state)))
            self.job_table.setItem(row, 5, QTableWidgetItem(job.match_class.value))
            self.job_table.setItem(row, 6, QTableWidgetItem(str(job.attempts)))
            self.job_table.setItem(row, 7, QTableWidgetItem(outcome_message(job.last_error_code, job.state)))

            for col in range(self.job_table.columnCount()):
                item = self.job_table.item(row, col)
                if item is not None:
                    item.setData(Qt.ItemDataRole.UserRole, job.job_id)

        self.job_table.resizeColumnsToContents()
        self._update_action_states()

    def _sync_subject(self, text: str) -> None:
        """Keep operator subject in sync with the editable input."""
        subject = text.strip()
        if subject:
            self._operator_subject = subject

    def _on_subject_changed(self, text: str) -> None:
        self._sync_subject(text)
        self._update_action_states()

    def _current_subject(self) -> str:
        return (self.operator_subject.text().strip() or self._operator_subject)

    def _selected_job(self) -> Optional[models.WorkflowJob]:
        """Resolve the currently selected workflow job, if any."""
        try:
            job_id = self._selected_job_id()
        except ValueError:
            return None
        return store.get_job(job_id)

    def _action_authorization(self, action: str, job: Optional[models.WorkflowJob]) -> tuple[bool, str]:
        """Return (allowed, user-facing reason) for an action on a job."""
        if job is None:
            return False, "No job selected."

        subject = self._current_subject().strip()
        if not subject:
            return False, "Operator subject is required."

        try:
            decision = authorization.require_authorization(job, subject=subject, requested_action=action)
        except ValueError as exc:
            return False, str(exc)

        if not decision.allowed:
            return False, f"{decision.code}: {decision.reason}"

        return True, ""

    def _action_allowed(self, action: str, allowed_states: Optional[set[models.WorkflowState]] = None) -> tuple[bool, str]:
        """Return action usability and blocking reason for the currently selected job."""
        selected_job = self._selected_job()
        if selected_job is None:
            return False, "No job selected."

        if self._engine.is_paused():
            return False, "Engine is paused."

        if allowed_states is not None and selected_job.state not in allowed_states:
            return False, f"Not valid in state {state_label(selected_job.state)}."

        authorized, reason = self._action_authorization(action, selected_job)
        if not authorized:
            return False, reason
        return True, ""

    def _update_action_states(self) -> None:
        selected_rows = self.job_table.selectionModel().selectedRows() if self.job_table.selectionModel() else []
        has_selection = bool(selected_rows)

        open_enabled = has_selection and not self._engine.is_paused()
        self.open_input_btn.setEnabled(open_enabled)
        self.open_output_btn.setEnabled(open_enabled)

        run_ok, run_reason = self._action_allowed(
            "run_job",
            allowed_states={models.WorkflowState.QUEUED, models.WorkflowState.FAILED, models.WorkflowState.RETRY, models.WorkflowState.NEEDS_REVIEW},
        )
        retry_ok, retry_reason = self._action_allowed("retry_job", allowed_states={models.WorkflowState.FAILED, models.WorkflowState.RETRY, models.WorkflowState.NEEDS_REVIEW})
        cancel_ok, cancel_reason = self._action_allowed("approve_job")
        quarantine_ok, quarantine_reason = self._action_allowed("approve_job")
        self.run_btn.setEnabled(has_selection and run_ok)
        self.retry_btn.setEnabled(has_selection and retry_ok)
        self.cancel_btn.setEnabled(has_selection and cancel_ok)
        self.quarantine_btn.setEnabled(has_selection and quarantine_ok)

        action_block_reasons = [reason for reason in [run_reason, retry_reason, cancel_reason, quarantine_reason] if reason and reason != "No job selected."]
        self._auth_status.setText(" | ".join(action_block_reasons) if action_block_reasons else "Ready to execute selected action.")

        self.run_queued_btn.setEnabled(not self._engine.is_paused())
        self.scan_btn.setEnabled(not self._engine.is_paused())
        self.pause_btn.setEnabled(True)

        if self._engine.is_paused():
            self._auth_status.setText("Engine is paused.")
        elif has_selection and not action_block_reasons:
            self._auth_status.setText(f"Using operator subject: {self._current_subject() or 'not-set'}.")

    def _open_path(self, raw_path: str, label: str) -> None:
        if not raw_path:
            QMessageBox.information(self, "No path", f"{label.title()} path is not available.")
            return

        if not os.path.exists(raw_path):
            QMessageBox.warning(self, "Path missing", f"{label.title()} path was not found: {raw_path}")
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(raw_path))

    def _open_selected_job_input(self) -> None:
        try:
            job_id = self._selected_job_id()
        except ValueError as exc:
            QMessageBox.information(self, "No job selected", str(exc))
            return

        job = store.get_job(job_id)
        if job is None:
            QMessageBox.warning(self, "No job", f"Could not load selected job {job_id}.")
            return
        self._open_path(job.input_path_ref, "input")

    def _open_selected_job_output(self) -> None:
        try:
            job_id = self._selected_job_id()
        except ValueError as exc:
            QMessageBox.information(self, "No job selected", str(exc))
            return

        job = store.get_job(job_id)
        if job is None:
            QMessageBox.warning(self, "No job", f"Could not load selected job {job_id}.")
            return
        if job.output_path_ref:
            self._open_path(job.output_path_ref, "output")
            return
        QMessageBox.information(self, "Output not ready", "This job has not produced an output path yet.")

    def _selected_job_id(self) -> str:
        selected_rows = self.job_table.selectionModel().selectedRows() if self.job_table.selectionModel() else []
        if not selected_rows:
            raise ValueError("No job selected.")
        row = selected_rows[0].row()
        job_id_item = self.job_table.item(row, 0)
        if job_id_item is None:
            raise ValueError("Could not resolve selected job.")
        job_id = job_id_item.data(Qt.ItemDataRole.UserRole)
        if not job_id:
            raise ValueError("Could not resolve selected job id.")
        return str(job_id)

    def _toggle_pause(self) -> None:
        if self._engine.is_paused():
            self._engine.resume()
            self.refresh()
            return
        self._engine.pause()
        self.refresh()

    def _require_workflow_automation_entitlement(self) -> bool:
        """Require the paid execution capability, without blocking operational safety controls."""

        return check_and_enforce_workflow_automation_license(parent=self)

    def _run_selected_job(self) -> None:
        """Run selected job and keep the dashboard refreshed."""
        selected_job = self._selected_job()
        if selected_job is None:
            QMessageBox.information(self, "No job selected", "No job selected.")
            return

        if selected_job.grant_id is None:
            QMessageBox.warning(self, "Run blocked", "Run blocked: the selected job has no execution grant.")
            self.refresh()
            return

        authorized, reason = self._action_allowed("run_job")
        if not authorized and reason != "No job selected.":
            QMessageBox.warning(self, "Run blocked", f"Run blocked: {reason}")
            return
        if not self._require_workflow_automation_entitlement():
            return

        try:
            updated = self._engine.run_job(
                str(selected_job.job_id),
                actor=self._current_subject(),
                action_subject=self._current_subject(),
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Run blocked", str(exc))
            self.refresh()
            return
        except RuntimeError as exc:
            QMessageBox.warning(self, "Run blocked", str(exc))
            self.refresh()
            return
        except Exception as exc:
            QMessageBox.critical(self, "Run failed", str(exc))
            self.refresh()
            return

        if updated.last_error_code:
            QMessageBox.warning(
                self,
                "Run result",
                f"Job {updated.job_id}: {state_label(updated.state)}.\n{outcome_message(updated.last_error_code, updated.state)}",
            )
        else:
            QMessageBox.information(
                self,
                "Run result",
                f"Job {updated.job_id}: {state_label(updated.state)}.",
            )
        self.refresh()

    def _retry_selected_job(self) -> None:
        selected_job = self._selected_job()
        if selected_job is None:
            QMessageBox.information(self, "No job selected", "No job selected.")
            return

        if selected_job.grant_id is None:
            QMessageBox.warning(self, "Retry blocked", "Retry blocked: the selected job has no execution grant.")
            self.refresh()
            return

        authorized, reason = self._action_allowed("retry_job")
        if not authorized and reason != "No job selected.":
            QMessageBox.warning(self, "Retry blocked", f"Retry blocked: {reason}")
            return
        if not self._require_workflow_automation_entitlement():
            return
        try:
            updated = self._engine.retry_job(
                str(selected_job.job_id),
                actor=self._current_subject(),
                action_subject=self._current_subject(),
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Retry blocked", str(exc))
            self.refresh()
            return
        except RuntimeError as exc:
            QMessageBox.warning(self, "Retry blocked", str(exc))
            self.refresh()
            return
        except Exception as exc:
            QMessageBox.critical(self, "Retry failed", str(exc))
            self.refresh()
            return

        if updated.last_error_code:
            QMessageBox.warning(
                self,
                "Retry result",
                f"Job {updated.job_id}: {state_label(updated.state)}.\n{outcome_message(updated.last_error_code, updated.state)}",
            )
        else:
            QMessageBox.information(self, "Retry result", f"Job {updated.job_id}: {state_label(updated.state)}.")
        self.refresh()

    def _quarantine_selected_job(self) -> None:
        selected_job = self._selected_job()
        if selected_job is None:
            QMessageBox.information(self, "No job selected", "No job selected.")
            return

        if selected_job.grant_id is None:
            QMessageBox.warning(self, "Quarantine blocked", "Quarantine blocked: the selected job has no execution grant.")
            self.refresh()
            return

        authorized, reason = self._action_allowed("approve_job")
        if not authorized and reason != "No job selected.":
            QMessageBox.warning(self, "Quarantine blocked", f"Quarantine blocked: {reason}")
            return

        reason, accepted = QInputDialog.getText(
            self,
            "Quarantine reason",
            "Optional reason to store with this job:",
            text="Needs manual review",
        )
        if not accepted:
            return

        try:
            updated = self._engine.quarantine_job(
                str(selected_job.job_id),
                actor=self._current_subject(),
                action_subject=self._current_subject(),
                reason=reason or "Needs manual review",
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Quarantine blocked", str(exc))
            self.refresh()
            return
        except RuntimeError as exc:
            QMessageBox.warning(self, "Quarantine blocked", str(exc))
            self.refresh()
            return
        except Exception as exc:
            QMessageBox.critical(self, "Quarantine failed", str(exc))
            self.refresh()
            return

        QMessageBox.information(self, "Quarantine complete", f"Job {updated.job_id}: {state_label(updated.state)}.")
        self.refresh()

    def _cancel_selected_job(self) -> None:
        selected_job = self._selected_job()
        if selected_job is None:
            QMessageBox.information(self, "No job selected", "No job selected.")
            return

        if selected_job.grant_id is None:
            QMessageBox.warning(self, "Cancel blocked", "Cancel blocked: the selected job has no execution grant.")
            self.refresh()
            return

        authorized, reason = self._action_allowed("approve_job")
        if not authorized and reason != "No job selected.":
            QMessageBox.warning(self, "Cancel blocked", f"Cancel blocked: {reason}")
            return

        reason, accepted = QInputDialog.getText(
            self,
            "Cancel reason",
            "Optional reason for cancellation:",
            text="Cancelled by operator",
        )
        if not accepted:
            return

        try:
            updated = self._engine.cancel_job(
                str(selected_job.job_id),
                actor=self._current_subject(),
                action_subject=self._current_subject(),
                reason=reason or "Cancelled by operator",
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Cancel blocked", str(exc))
            self.refresh()
            return
        except RuntimeError as exc:
            QMessageBox.warning(self, "Cancel blocked", str(exc))
            self.refresh()
            return
        except Exception as exc:
            QMessageBox.critical(self, "Cancel failed", str(exc))
            self.refresh()
            return

        QMessageBox.information(self, "Cancel complete", f"Job {updated.job_id}: {state_label(updated.state)}.")
        self.refresh()

    def _run_queued_jobs(self) -> None:
        """Run all queued jobs and keep the dashboard refreshed."""
        if not self._require_workflow_automation_entitlement():
            return
        try:
            summary = self._engine.run_queued_jobs(
                states=[models.WorkflowState.QUEUED],
                actor=self._current_subject(),
                action_subject=self._current_subject(),
            )
        except Exception as exc:
            QMessageBox.critical(self, "Run queued failed", str(exc))
            self.refresh()
            return

        QMessageBox.information(
            self,
            "Queued run complete",
            (
                f"Attempted: {summary['attempted']}\\n"
                f"Completed: {summary['completed']}\\n"
                f"Needs review: {summary['needs_review']}\\n"
                f"Retry: {summary['retry']}\\n"
                f"Failed: {summary['failed']}\\n"
                f"Cancelled: {summary['cancelled']}\\n"
                f"Errors: {summary['errors']}"
            ),
        )
        self.refresh()

    def _scan_folders(self) -> None:
        """Scan configured input folders and enqueue new documents."""
        if not self._require_workflow_automation_entitlement():
            return
        try:
            monitor = FolderMonitor(engine=self._engine)
            result = monitor.scan()
        except Exception as exc:
            QMessageBox.critical(self, "Scan failed", str(exc))
            self.refresh()
            return

        auto_summary: Optional[Dict[str, int]] = None
        if self.auto_run_after_scan.isChecked():
            try:
                auto_summary = self._engine.run_queued_jobs(
                    states=[models.WorkflowState.QUEUED],
                    actor=self._current_subject(),
                    action_subject=self._current_subject(),
                )
            except Exception as exc:
                QMessageBox.warning(self, "Auto run failed", str(exc))

        QMessageBox.information(
            self,
            "Folder scan complete",
            (
                f"Discovered: {result.discovered}\n"
                f"Enqueued: {result.enqueued}\n"
                f"Already queued: {result.already_scheduled}\n"
                f"Skipped: {result.skipped}"
            )
            + (
                (
                    "\n\nAuto-run after scan:\n"
                    f"Attempted: {auto_summary['attempted']}\n"
                    f"Completed: {auto_summary['completed']}\n"
                    f"Needs review: {auto_summary['needs_review']}\n"
                    f"Retry: {auto_summary['retry']}\n"
                    f"Failed: {auto_summary['failed']}\n"
                    f"Cancelled: {auto_summary['cancelled']}\n"
                    f"Errors: {auto_summary['errors']}"
                )
                if auto_summary
                else ""
            ),
        )
        self.refresh()


__all__ = ["WorkflowConsole"]
