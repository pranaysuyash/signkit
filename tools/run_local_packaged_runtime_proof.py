#!/usr/bin/env python3
"""Exercise the current macOS packaged runtime on isolated local state."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen


DEFAULT_APP = Path("dist/SignKit.app")
BACKEND_PORT = 8001


def _port_open() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(0.2)
        return client.connect_ex(("127.0.0.1", BACKEND_PORT)) == 0


def _wait_for_health(timeout_seconds: float) -> int:
    deadline = time.monotonic() + timeout_seconds
    last_error = "not attempted"
    while time.monotonic() < deadline:
        try:
            with urlopen("http://127.0.0.1:8001/health", timeout=1) as response:
                return response.status
        except Exception as error:  # pragma: no cover - timing varies by machine
            last_error = str(error)
            time.sleep(0.2)
    raise RuntimeError(f"packaged backend did not become healthy: {last_error}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_proof(app_path: Path, data_dir: Path, timeout_seconds: float) -> dict[str, object]:
    if os.uname().sysname != "Darwin":
        raise RuntimeError("packaged runtime proof requires macOS")
    app_path = app_path.resolve()
    executable = app_path / "Contents" / "MacOS" / "SignKit"
    workspace_asset = app_path / "Contents" / "Resources" / "web" / "cloud_workspace" / "index.html"
    if not app_path.is_dir() or not executable.is_file():
        raise FileNotFoundError(f"packaged app or executable is missing: {app_path}")
    if _port_open():
        raise RuntimeError("port 8001 is already occupied before packaged launch")
    if any(path.name == ".env" or path.name.startswith(".env.") for path in app_path.rglob("*")):
        raise RuntimeError("packaged app contains a .env file")
    if not workspace_asset.is_file():
        raise RuntimeError("packaged app is missing web/cloud_workspace/index.html")

    codesign = subprocess.run(
        ["codesign", "--verify", "--deep", "--strict", str(app_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if codesign.returncode != 0:
        raise RuntimeError(f"codesign verification failed: {codesign.stderr.strip()}")

    data_dir.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update(
        {
            "QT_QPA_PLATFORM": "offscreen",
            "SIGNKIT_DATA_DIR": str(data_dir),
            "SIGNKIT_PROFILE": "standard",
        }
    )
    process = subprocess.Popen(
        [str(executable)],
        cwd=app_path.parents[1],
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    health_status: int | None = None
    try:
        health_status = _wait_for_health(timeout_seconds)
        if health_status != 200:
            raise RuntimeError(f"packaged health returned {health_status}")
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        deadline = time.monotonic() + 3
        while _port_open() and time.monotonic() < deadline:
            time.sleep(0.1)
    if _port_open():
        raise RuntimeError("port 8001 remained open after packaged shutdown")

    return {
        "status": "passed",
        "app": str(app_path),
        "executable_sha256": _sha256(executable),
        "health_status": health_status,
        "codesign": "verified",
        "workspace_asset": str(workspace_asset.relative_to(app_path)),
        "isolated_data_dir": str(data_dir),
        "data_files": sorted(str(path.relative_to(data_dir)) for path in data_dir.rglob("*") if path.is_file()),
        "port_8001_after_shutdown": "closed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, default=DEFAULT_APP)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()
    try:
        if args.data_dir:
            result = run_proof(args.app, args.data_dir, args.timeout)
        else:
            with tempfile.TemporaryDirectory(prefix="signkit-packaged-proof-") as temp_dir:
                result = run_proof(args.app, Path(temp_dir), args.timeout)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as error:
        print(json.dumps({"status": "failed", "error": str(error)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
