#!/bin/bash

# Deploy only after the canonical public-surface gate passes.
# This script never stages, commits, resets, or rewrites repository state.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ "${DEPLOY_CONFIRM:-}" != "signkit-landing" ]]; then
  echo "Refusing deployment. Set DEPLOY_CONFIRM=signkit-landing after reviewing the release record." >&2
  exit 2
fi

command -v wrangler >/dev/null 2>&1 || {
  echo "Wrangler is required for Cloudflare Pages deployment." >&2
  exit 2
}

cd "$PROJECT_ROOT"
PROJECT_PYTHON="$PROJECT_ROOT/.venv/bin/python"
if [[ ! -x "$PROJECT_PYTHON" ]]; then
  echo "Canonical project interpreter is required at $PROJECT_PYTHON" >&2
  exit 2
fi

"$PROJECT_PYTHON" tools/audit_public_surface.py --strict
"$PROJECT_PYTHON" -m pytest tests/test_launch_claim_registry.py tests/test_public_surface_audit.py -q
"$PROJECT_PYTHON" -m py_compile serve.py tools/audit_public_surface.py tools/test_deployed_surface.py
node --check web/live/js/checkout.js

echo "Deploying canonical SignKit surface to Cloudflare Pages project signkit-landing."
wrangler pages deploy "$PROJECT_ROOT" --project-name signkit-landing --branch "${DEPLOY_BRANCH:-landing-page}"

"$PROJECT_PYTHON" tools/test_deployed_surface.py --base-url "${DEPLOY_BASE_URL:-https://signkit.work}"
