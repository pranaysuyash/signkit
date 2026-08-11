#!/usr/bin/env bash
set -euo pipefail

# Local smoke test for the canonical landing page. The Python server does not
# implement Cloudflare redirects, so the manifest is asserted directly and the
# runtime provider contract is exercised by the dependency-free pytest harness.

PORT="${PORT:-8099}"

if [[ -x "./.venv/bin/pytest" ]]; then
  PYTEST=(./.venv/bin/pytest)
else
  PYTEST=(python3 -m pytest)
fi

"${PYTEST[@]}" -q tests/test_landing_surface_contract.py

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]]; then
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

python3 -m http.server "${PORT}" >/dev/null 2>&1 &
SERVER_PID="$!"

BASE="http://127.0.0.1:${PORT}"

wait_ready() {
  for _ in $(seq 1 30); do
    if curl -s -o /dev/null "${BASE}/"; then
      return 0
    fi
    sleep 0.1
  done
  return 1
}

wait_ready

check_200() {
  local path="$1"
  local code
  code="$(curl -sS -o /dev/null -L -w "%{http_code}" "${BASE}${path}")"
  if [[ "$code" != "200" ]]; then
    echo "FAIL: ${BASE}${path} expected 200, got $code" >&2
    exit 1
  fi
  echo "OK 200 ${path}"
}

check_200 "/index.html"
check_200 "/robots.txt"
check_200 "/sitemap.xml"
check_200 "/web/live/js/checkout-config.js"
check_200 "/web/live/js/checkout.js"

INDEX_HTML="$(curl -sS "${BASE}/index.html")"

if [[ "${INDEX_HTML}" != *'data-checkout-provider="dodo"'* ]]; then
  echo "FAIL: canonical landing has no Dodo primary checkout actions" >&2
  exit 1
fi
if [[ "${INDEX_HTML}" != *'data-checkout-provider="gumroad"'* ]]; then
  echo "FAIL: canonical landing has no explicit Gumroad fallback" >&2
  exit 1
fi
if [[ "${INDEX_HTML}" != *'web/live/js/checkout-config.js'* ]] || [[ "${INDEX_HTML}" != *'web/live/js/checkout.js'* ]]; then
  echo "FAIL: canonical landing does not load the canonical checkout contract" >&2
  exit 1
fi
echo "OK canonical checkout configuration and provider markers"

for variant in root buy purchase gum test-variants; do
  for route in "/${variant}" "/${variant}/" "/${variant}.html"; do
    if ! awk -v route="${route}" '$1 == route && $2 == "/" && $3 == "301" { found = 1 } END { exit !found }' _redirects; then
      echo "FAIL: ${route} is not permanently redirected to / in _redirects" >&2
      exit 1
    fi
  done
done
for route in \
  /web/live/ /web/live/index.html \
  /web/new_landing_page/ /web/new_landing_page/index.html \
  /web/cloud_workspace/ /web/cloud_workspace/index.html; do
  if ! awk -v route="${route}" '$1 == route && $2 == "/" && $3 == "301" { found = 1 } END { exit !found }' _redirects; then
    echo "FAIL: ${route} is not permanently redirected to / in _redirects" >&2
    exit 1
  fi
done
for route in \
  /deploy_dist/index.html /docs/GUMROAD_EMAIL_TEMPLATES.html \
  /web/archives/main_pre_merge_20251121_184736/claude_landing_page/index.html \
  /web/backups/landing-page-sync-20251123/index.html \
  /web/concepts/2026-07-31-b2c-redesign/index.html; do
  if ! awk -v route="${route}" '$1 == route || ($1 ~ /\*/ && index(route, substr($1, 1, index($1, "*") - 1)) == 1) { found = 1 } END { exit !found }' _redirects; then
    echo "FAIL: ${route} is not covered by the retained HTML redirect policy" >&2
    exit 1
  fi
done
echo "OK canonical route manifest redirects every legacy variant to /"

echo "Local landing smoke test passed (${BASE})"
