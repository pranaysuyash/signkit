from __future__ import annotations

from desktop_app.run import _run_profile


def main() -> None:
    exit_code = _run_profile("standard")
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
