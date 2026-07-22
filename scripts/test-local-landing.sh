#!/usr/bin/env bash
set -euo pipefail

# Local smoke test for landing pages without Cloudflare "pretty URL" routing.
# Validates that all expected files exist and can be served by a static server.

PORT="${PORT:-8099}"

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
check_200 "/root.html"
check_200 "/buy.html"
check_200 "/purchase.html"
check_200 "/gum.html"
check_200 "/test-variants.html"
check_200 "/robots.txt"
check_200 "/sitemap.xml"
check_200 "/web/live/js/checkout-config.js"
check_200 "/web/live/js/checkout.js"

INDEX_HTML="$(curl -sS "${BASE}/index.html")"
if [[ "${INDEX_HTML}" != *"One file is a tool problem. Hundreds are a workflow problem."* ]]; then
  echo "FAIL: canonical landing is missing the recurring-workflow decision point" >&2
  exit 1
fi
if [[ "${INDEX_HTML}" != *"source=signkit&amp;entry=landing&amp;intent=document-workflow"* ]]; then
  echo "FAIL: recurring-workflow CTA is missing source attribution" >&2
  exit 1
fi
if [[ "${INDEX_HTML}" != *"SignKit does not send"* ]]; then
  echo "FAIL: recurring-workflow CTA is missing its privacy boundary" >&2
  exit 1
fi
echo "OK recurring-workflow CTA, attribution, and privacy boundary"

if [[ "${INDEX_HTML}" != *'data-checkout-provider="dodo"'* ]]; then
  echo "FAIL: canonical landing has no Dodo primary checkout actions" >&2
  exit 1
fi
if [[ "${INDEX_HTML}" != *'data-checkout-provider="gumroad"'* ]]; then
  echo "FAIL: canonical landing has no explicit Gumroad fallback" >&2
  exit 1
fi
if [[ "${INDEX_HTML}" != *'Dodo Payments provides the receipt, download, and licence key'* ]]; then
  echo "FAIL: checkout fulfilment responsibility is not explained" >&2
  exit 1
fi
echo "OK Dodo primary, Gumroad fallback, and fulfilment copy"

echo "Local landing smoke test passed (${BASE})"
