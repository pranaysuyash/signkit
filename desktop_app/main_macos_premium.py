from __future__ import annotations

import sys

from desktop_app.run import _run_profile


def main() -> None:
    if sys.platform != "darwin":
        print("❌ SignKit Premium app must be launched on macOS.")
        print("Use the standard entrypoint on non-mac platforms.")
        raise SystemExit(1)

    exit_code = _run_profile("mac-premium")
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
