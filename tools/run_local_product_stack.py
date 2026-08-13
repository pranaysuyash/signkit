#!/usr/bin/env python3
"""Run the canonical local landing and companion as one recoverable stack.

The launcher owns process lifecycle only. It reuses ``serve.py`` for the
canonical root and the existing FastAPI application for ``/workspace-app``;
it does not introduce a proxy, duplicate route, or second workspace service.
The default database is an isolated rebuildable SQLite file so a product
preview cannot silently mutate the developer's normal local database.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
LANDING_HOST = "127.0.0.1"
LANDING_PORT = 8080
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8001
DEFAULT_SECRET = "signkit-local-product-stack-secret-that-is-at-least-32-bytes"


def _python_bin() -> str:
    for relative in (".venv/bin/python", "venv/bin/python"):
        candidate = ROOT / relative
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return sys.executable


def _url_is_ready(url: str) -> bool:
    try:
        with urlopen(url, timeout=0.75) as response:
            return response.status == 200
    except (OSError, URLError):
        return False


def _wait_for(url: str, process: subprocess.Popen[str], label: str, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"{label} exited before becoming ready (code {process.returncode})")
        if _url_is_ready(url):
            return
        time.sleep(0.1)
    raise RuntimeError(
        f"{label} did not become ready at {url}; check whether its port is already in use "
        "and inspect the process output"
    )


def _stop(processes: list[subprocess.Popen[str]]) -> None:
    for process in reversed(processes):
        if process.poll() is None:
            process.terminate()
    deadline = time.monotonic() + 5
    for process in reversed(processes):
        if process.poll() is None:
            remaining = max(0.1, deadline - time.monotonic())
            try:
                process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def _database_url(args: argparse.Namespace) -> str:
    if args.database_url:
        return args.database_url
    runtime_dir = ROOT / ".codex-test-tmp"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{(runtime_dir / 'local-product-stack.db').resolve().as_posix()}"


def _data_dir(args: argparse.Namespace) -> Path:
    if args.data_dir:
        data_dir = Path(args.data_dir).expanduser().resolve()
    else:
        data_dir = (ROOT / ".codex-test-tmp" / "local-product-stack-data").resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database-url",
        help="override the isolated SQLite default; use only with an intentional local database",
    )
    parser.add_argument(
        "--data-dir",
        help="override the isolated filesystem data root; use only with an intentional local directory",
    )
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument(
        "--once",
        action="store_true",
        help="start both services, print their URLs, then shut them down after readiness checks",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    python_bin = _python_bin()
    environment = os.environ.copy()
    environment.setdefault("JWT_SECRET", DEFAULT_SECRET)
    # Do not inherit an ambient database URL into a product preview. An
    # alternate database must be explicit on the command line.
    environment["DATABASE_URL"] = _database_url(args)
    # Keep uploads and logs isolated as well. An alternate data root must be
    # explicit on the command line, just like an alternate database.
    environment["SIGNKIT_DATA_DIR"] = str(_data_dir(args))
    environment["SIGNKIT_LANDING_HOST"] = LANDING_HOST
    environment["SIGNKIT_LANDING_PORT"] = str(LANDING_PORT)

    processes: list[subprocess.Popen[str]] = []
    try:
        backend = subprocess.Popen(
            [
                python_bin,
                "-m",
                "uvicorn",
                "backend.app.main:app",
                "--host",
                BACKEND_HOST,
                "--port",
                str(BACKEND_PORT),
            ],
            cwd=ROOT,
            env=environment,
        )
        processes.append(backend)
        _wait_for(f"http://{BACKEND_HOST}:{BACKEND_PORT}/health", backend, "local companion", args.timeout)

        landing = subprocess.Popen(
            [python_bin, "serve.py"],
            cwd=ROOT,
            env=environment,
        )
        processes.append(landing)
        _wait_for(f"http://{LANDING_HOST}:{LANDING_PORT}/", landing, "canonical landing", args.timeout)

        print(f"Landing: http://{LANDING_HOST}:{LANDING_PORT}/")
        print(f"Workspace: http://{BACKEND_HOST}:{BACKEND_PORT}/workspace-app/")
        print(f"Database: {environment['DATABASE_URL']}")
        if args.once:
            return 0

        print("Local product stack is running. Press Ctrl-C to stop both services.")
        while True:
            if backend.poll() is not None:
                raise RuntimeError(f"local companion exited (code {backend.returncode})")
            if landing.poll() is not None:
                raise RuntimeError(f"canonical landing exited (code {landing.returncode})")
            time.sleep(0.5)
    except KeyboardInterrupt:
        return 130
    except (OSError, RuntimeError) as exc:
        print(f"local product stack failed: {exc}", file=sys.stderr)
        return 1
    finally:
        _stop(processes)


if __name__ == "__main__":
    raise SystemExit(main())
