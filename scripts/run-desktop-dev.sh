#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
  else
    echo "Expected root .venv virtualenv, but .venv/bin/python was not found."
    echo "Create one with: uv venv .venv && uv pip install -r requirements.txt"
    PYTHON_BIN="python3"
  fi
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
