"""Folder-based intake for controlled signing workflows.

The monitor is intentionally conservative in v1: it discovers PDF files under a
recipe's configured input folder and either enqueues them for execution (exact-mode
run) or records review-only events for unsupported files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

from desktop_app.workflows.store import list_jobs, list_recipes
from desktop_app.workflows.engine import WorkflowEngine
from desktop_app.workflows.models import RecipeStatus, WorkflowState


@dataclass(frozen=True)
class FolderMonitorResult:
    """Result of one folder scan pass."""

    discovered: int = 0
    enqueued: int = 0
    already_scheduled: int = 0
    skipped: int = 0
    errors: List[str] = field(default_factory=list)


class FolderMonitor:
    """Scan configured workflow recipes and schedule jobs from input folders."""

    def __init__(
        self,
        *,
        engine: Optional[WorkflowEngine] = None,
        max_depth: int = 1,
        allowed_exts: Optional[Iterable[str]] = None,
    ) -> None:
        self.engine = engine or WorkflowEngine()
        self.max_depth = max_depth
        self.allowed_exts = {ext.lower() for ext in (allowed_exts or (".pdf",))}

    def scan(self, *, recipe_id: Optional[str] = None, max_files: Optional[int] = None) -> FolderMonitorResult:
        self.engine.start()
        recipes = list_recipes()
        if recipe_id:
            recipes = [recipe for recipe in recipes if recipe.recipe_id == recipe_id]

        result = FolderMonitorResult()
        new_errors: List[str] = []
        discovered = 0
        enqueued = 0
        already = 0
        skipped = 0

        for recipe in recipes:
            if recipe.status != RecipeStatus.ACTIVE.value:
                continue

            folder = Path(recipe.input_folder.path or "")
            if not folder.exists() or not folder.is_dir():
                new_errors.append(f"input_folder_missing:{recipe.recipe_id}:{recipe.input_folder.path}")
                continue

            for file_path in self._iter_files(folder, recursive=recipe.input_folder.recursive):
                if file_path.suffix.lower() not in self.allowed_exts:
                    skipped += 1
                    continue

                discovered += 1
                if max_files and discovered > max_files:
                    break

                if self._already_queued(recipe.recipe_id, str(file_path)):
                    already += 1
                    continue

                try:
                    self.engine.enqueue_path(str(file_path), recipe_id=recipe.recipe_id)
                    enqueued += 1
                except Exception as exc:
                    new_errors.append(f"enqueue_failed:{recipe.recipe_id}:{file_path}:{exc}")
                    skipped += 1

        return FolderMonitorResult(
            discovered=discovered,
            enqueued=enqueued,
            already_scheduled=already,
            skipped=skipped,
            errors=new_errors,
        )

    def _iter_files(self, folder: Path, *, recursive: bool) -> Iterable[Path]:
        if not recursive:
            return [entry for entry in folder.iterdir() if entry.is_file()]
        if self.max_depth <= 1:
            return [entry for entry in folder.iterdir() if entry.is_file()]

        files: List[Path] = []
        stack = [(folder, 1)]
        while stack:
            current, depth = stack.pop()
            entries = sorted(current.iterdir(), key=lambda item: item.name)
            for entry in entries:
                if entry.is_file():
                    files.append(entry)
                elif entry.is_dir() and depth < self.max_depth:
                    stack.append((entry, depth + 1))
        return files

    def _already_queued(self, recipe_id: str, file_path: str) -> bool:
        existing = list_jobs(recipe_id=recipe_id, state=WorkflowState.QUEUED.value)
        for job in existing:
            if job.input_path_ref == file_path:
                return True
        return False
