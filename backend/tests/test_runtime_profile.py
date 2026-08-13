from __future__ import annotations

import os
import subprocess
import sys


def _route_paths(profile: str, tmp_path) -> set[str]:
    env = os.environ.copy()
    env.update(
        {
            "SIGNKIT_RUNTIME_PROFILE": profile,
            "DATABASE_URL": f"sqlite:///{tmp_path / f'{profile}.sqlite'}",
            "JWT_SECRET": "runtime-profile-test-secret-at-least-32-bytes",
        }
    )
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from backend.app.main import app; print('\\n'.join(getattr(route, 'path', '') for route in app.routes))",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return set(result.stdout.splitlines())


def test_hosted_runtime_does_not_register_local_document_route(tmp_path):
    paths = _route_paths("hosted", tmp_path)

    assert "/workspace/executions/{execution_id}/document-inspections" not in paths


def test_local_companion_runtime_registers_local_document_route(tmp_path):
    paths = _route_paths("local_companion", tmp_path)

    assert "/workspace/executions/{execution_id}/document-inspections" in paths
