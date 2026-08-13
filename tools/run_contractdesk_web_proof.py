"""Start and probe the canonical local ContractDesk web proof surface.

The command deliberately uses one deterministic port instead of silently
selecting an available port. This makes browser evidence reproducible and
prevents accidentally probing an unrelated local service.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8871
WORKSPACE_PATH = "/workspace-app/index.html"
FIXTURE_PATH = "/workspace-app/proof-fixtures.json"


def _read_url(url: str, timeout: float = 2.0) -> tuple[int, bytes]:
    with urlopen(url, timeout=timeout) as response:
        return int(response.status), response.read()


def _wait_for_server(base_url: str, process: subprocess.Popen[str] | None, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    last_error = "server did not respond"
    while time.monotonic() < deadline:
        if process is not None and process.poll() is not None:
            output = process.communicate()[1].strip()
            detail = f"\n{output}" if output else ""
            raise RuntimeError(f"backend exited before becoming healthy (code {process.returncode}){detail}")
        try:
            status, _ = _read_url(f"{base_url}/health")
            if status == 200:
                return
            last_error = f"health returned HTTP {status}"
        except (OSError, URLError) as exc:
            last_error = str(exc)
        time.sleep(0.1)
    raise RuntimeError(f"timed out waiting for {base_url}/health: {last_error}")


def probe_surface(base_url: str) -> dict[str, object]:
    """Probe public, metadata-only endpoints needed before browser evidence."""

    checks: dict[str, object] = {}
    health_status, health_body = _read_url(f"{base_url}/health")
    health = json.loads(health_body)
    checks["health"] = {"status": health_status, "application": health.get("status")}

    page_status, page_body = _read_url(f"{base_url}{WORKSPACE_PATH}")
    page_text = page_body.decode("utf-8")
    if page_status != 200 or "SignKit Workspace" not in page_text:
        raise RuntimeError("workspace mount did not return the SignKit Workspace page")
    checks["workspace_mount"] = {"status": page_status, "title_present": True}

    fixture_status, fixture_body = _read_url(f"{base_url}{FIXTURE_PATH}")
    fixture = json.loads(fixture_body)
    scenario_id = fixture.get("scenario_id")
    if fixture_status != 200 or not scenario_id:
        raise RuntimeError("proof fixture did not return a scenario_id")
    checks["proof_fixture"] = {"status": fixture_status, "scenario_id": scenario_id}

    for asset in ("app.js", "styles.css"):
        asset_status, _ = _read_url(f"{base_url}/workspace-app/{asset}")
        if asset_status != 200:
            raise RuntimeError(f"workspace asset returned HTTP {asset_status}: {asset}")
    checks["workspace_assets"] = {"status": 200, "assets": ["app.js", "styles.css"]}

    return {
        "status": "pass",
        "base_url": base_url,
        "workspace_url": f"{base_url}{WORKSPACE_PATH}",
        "fixture_url": f"{base_url}{FIXTURE_PATH}",
        "checks": checks,
    }


def _start_backend(host: str, port: int) -> subprocess.Popen[str]:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.app.main:app",
        "--host",
        host,
        "--port",
        str(port),
        "--log-level",
        "warning",
    ]
    return subprocess.Popen(
        command,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument(
        "--check-existing",
        action="store_true",
        help="Probe an already-running backend instead of starting one.",
    )
    parser.add_argument(
        "--keep-running",
        action="store_true",
        help="Keep the started backend alive after the probe for browser evidence.",
    )
    args = parser.parse_args(argv)
    base_url = f"http://{args.host}:{args.port}"
    process: subprocess.Popen[str] | None = None
    try:
        if not args.check_existing:
            process = _start_backend(args.host, args.port)
        _wait_for_server(base_url, process, args.timeout)
        result = probe_surface(base_url)
        print(json.dumps(result, indent=2, sort_keys=True))
        if args.keep_running and process is not None:
            print("Backend is running. Press Ctrl-C to stop it.")
            process.wait()
        return 0
    except KeyboardInterrupt:
        return 130
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"contractdesk web proof failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if process is not None and process.poll() is None and not args.keep_running:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    raise SystemExit(main())

