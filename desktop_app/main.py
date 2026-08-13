from __future__ import annotations

import sys


def _print_dependency_hint(error: ModuleNotFoundError) -> None:
    """Show a clear startup hint when a required module cannot be imported."""

    print(f"Missing dependency: {error.name}", file=sys.stderr)
    print(f"Python executable: {sys.executable}", file=sys.stderr)
    if ".venv/bin/python" in sys.executable or "./venv/bin/python" in sys.executable:
        print("Tip: activate the virtualenv before launching:", file=sys.stderr)
    else:
        print("Tip: use the project venv (./venv/bin/python) or ./.venv/bin/python for launch.", file=sys.stderr)


def _run_profile(profile_name: str) -> int:
    """Resolve the canonical profile runner lazily for testable startup wiring."""

    from desktop_app.run import _run_profile as run_profile

    return run_profile(profile_name)


def main() -> None:
    try:
        exit_code = _run_profile("standard")
    except ModuleNotFoundError as error:
        _print_dependency_hint(error)
        raise SystemExit(1)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
