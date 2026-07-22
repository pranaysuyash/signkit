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

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL is not set."
  echo "Example: export DATABASE_URL='postgresql+psycopg://USER:PASS@localhost:5432/signkit'"
  exit 1
fi

exec "$PYTHON_BIN" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
