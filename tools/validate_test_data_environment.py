#!/usr/bin/env python3
"""Fail fast when test-data checks are launched outside a project venv."""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path


REQUIRED_MODULES = {
    "Pillow": "PIL",
    "opencv-python": "cv2",
    "PySide6": "PySide6",
    "numpy": "numpy",
    "requests": "requests",
}

BACKEND_TEST_MODULES = {
    "alembic": "alembic",
    "fastapi": "fastapi",
    "httpx": "httpx",
    "SQLAlchemy": "sqlalchemy",
    "python-multipart": "multipart",
    "python-jose": "jose",
}


def _project_environment_roots(repo_root: Path) -> tuple[Path, ...]:
    return (repo_root / ".venv", repo_root / "venv")


def _is_project_interpreter(executable: Path, repo_root: Path) -> bool:
    """Accept venv launchers even when macOS resolves them to framework Python."""

    roots = tuple(root.resolve() for root in _project_environment_roots(repo_root))
    lexical_executable = executable.absolute()
    if any(lexical_executable.parent.parent == root for root in roots):
        return True

    active_prefix = Path(sys.prefix).resolve()
    return active_prefix in roots


def _pytest_launcher_errors(executable: Path, repo_root: Path) -> list[str]:
    """Detect a selected-environment pytest script with a stale shebang."""

    errors: list[str] = []
    selected = executable.resolve()
    roots = _project_environment_roots(repo_root)
    lexical_executable = executable.absolute()
    selected_root = next(
        (root.resolve() for root in roots if lexical_executable.parent.parent == root),
        None,
    )
    if selected_root is None:
        active_prefix = Path(sys.prefix).resolve()
        resolved_roots = {root.resolve() for root in roots}
        selected_root = active_prefix if active_prefix in resolved_roots else None
    if selected_root is None:
        return errors

    launcher = selected_root / "bin" / "pytest"
    if not launcher.is_file():
        return errors
    first_line = launcher.read_text(encoding="utf-8").splitlines()[0]
    if first_line.startswith("#!"):
        launcher_python = Path(first_line[2:].strip()).resolve()
        if launcher_python != selected:
            errors.append(
                f"pytest launcher {launcher} points to {launcher_python}, not {selected}; "
                f"run {selected} -m pytest or repair the project environment."
            )
    return errors


def validate_environment(
    executable: Path,
    repo_root: Path,
    *,
    include_backend: bool = False,
) -> list[str]:
    """Return actionable errors for the selected interpreter."""

    errors: list[str] = []
    resolved_executable = executable.resolve()
    if not _is_project_interpreter(resolved_executable, repo_root):
        expected = " or ".join(
            str(root / "bin" / "python") for root in _project_environment_roots(repo_root)
        )
        errors.append(
            "selected interpreter is outside the project environments: "
            f"{resolved_executable}. Use {expected}."
        )
    if include_backend:
        errors.extend(_pytest_launcher_errors(resolved_executable, repo_root))

    required_modules = dict(REQUIRED_MODULES)
    if include_backend:
        required_modules.update(BACKEND_TEST_MODULES)

    for distribution, module_name in required_modules.items():
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            errors.append(
                f"missing module {module_name!r} for {distribution}; "
                "install it only in the selected project environment."
            )
        except Exception as exc:  # pragma: no cover - dependency-specific import failures
            errors.append(f"module {module_name!r} failed to import: {exc}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the project interpreter and test-data dependencies."
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Interpreter to document; imports are evaluated by this process.",
    )
    parser.add_argument(
        "--backend",
        action="store_true",
        help="Also require the modules needed by backend API tests.",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    executable = Path(args.python)
    errors = validate_environment(executable, repo_root, include_backend=args.backend)
    if errors:
        print("TEST_DATA_ENVIRONMENT_ERROR:")
        for error in errors:
            print(f" - {error}")
        print(
            "Run from the repository with './.venv/bin/python' first; "
            "check './venv/bin/python' before changing dependencies."
        )
        return 2

    print(f"Test-data environment OK: {executable.resolve()}")
    required_modules = dict(REQUIRED_MODULES)
    if args.backend:
        required_modules.update(BACKEND_TEST_MODULES)
    print("Required modules: " + ", ".join(required_modules))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
