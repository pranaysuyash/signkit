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

if ! "$PYTHON_BIN" - <<'PY'
import importlib

for module in ("requests", "PySide6"):
    importlib.import_module(module)
PY
then
  echo "Required Python dependencies are missing from $PYTHON_BIN"
  echo "Reinstall desktop dependencies in the selected virtualenv."
  exit 1
fi

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-}"
if [ -z "${DATABASE_URL:-}" ]; then
  export DATABASE_URL="sqlite:///./signature_extractor.db"
fi

if [ -z "${JWT_SECRET:-}" ]; then
  if command -v openssl >/dev/null 2>&1; then
    export JWT_SECRET="$(openssl rand -hex 32)"
  else
    export JWT_SECRET="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
  fi
fi

exec "$PYTHON_BIN" -m desktop_app.main
