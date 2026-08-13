#!/usr/bin/env bash
set -euo pipefail

find_python() {
  if [ -x "venv/bin/python" ]; then
    echo "venv/bin/python"
    return
  fi
  if [ -x ".venv/bin/python" ]; then
    echo ".venv/bin/python"
    return
  fi
  return 1
}

PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  if ! PYTHON_BIN="$(find_python)"; then
    echo "Expected a local virtualenv at ./venv or ./.venv but none was found."
    echo "Create one with: uv venv venv && uv pip install -r requirements.venv.snapshot.txt"
    echo "If you intentionally run with a custom interpreter, set PYTHON_BIN explicitly."
    exit 1
  fi
fi

BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8001}"
exec "$PYTHON_BIN" -m uvicorn backend.app.main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" --reload
