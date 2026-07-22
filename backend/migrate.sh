#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ALEMBIC_BIN="${PROJECT_ROOT}/.venv/bin/alembic"

if [[ ! -x "$ALEMBIC_BIN" ]]; then
    ALEMBIC_BIN="$(command -v alembic || true)"
fi

if [[ -z "$ALEMBIC_BIN" ]]; then
    echo "alembic not found. Install dependencies in the root .venv and retry."
    exit 1
fi

PYTHONPATH="${PYTHONPATH:-$PROJECT_ROOT:$SCRIPT_DIR}"
export PYTHONPATH

cd "$SCRIPT_DIR"
exec "$ALEMBIC_BIN" -c "$SCRIPT_DIR/alembic.ini" "$@"
