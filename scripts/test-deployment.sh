#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-https://signkit.work}"
BASE_URL="${BASE_URL%/}"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

check_200() {
  local path="$1"
  local url="${BASE_URL}${path}"
  local code
  code="$(curl -sS -o /dev/null -L -w "%{http_code}" "$url")"
  if [[ "$code" != "200" ]]; then
    fail "$url expected 200, got $code"
  fi
  echo "OK 200 $url"
}

check_redirect_to_root() {
  local path="$1"
  local url="${BASE_URL}${path}"
  local response
  local code
  local redirect
  response="$(curl -sS -o /dev/null -w '%{http_code} %{redirect_url}' "$url")"
  code="${response%% *}"
  redirect="${response#* }"
  if [[ "$code" != "301" ]]; then
    fail "$url expected 301 to /, got $code"
  fi
  if [[ "$redirect" != "/" ]] && [[ "$redirect" != "${BASE_URL}/" ]]; then
    fail "$url expected redirect destination /, got ${redirect:-<empty>}"
  fi
  echo "OK 301 $url -> /"
}

content_type() {
  local path="$1"
  curl -sS -I -L "${BASE_URL}${path}" | awk -F': ' 'tolower($1)=="content-type"{print tolower($2)}' | tr -d '\r' | head -n 1
}

check_robots() {
  local ct
  ct="$(content_type "/robots.txt")"
  if [[ "$ct" != text/plain* ]]; then
    fail "${BASE_URL}/robots.txt expected text/plain, got ${ct:-<empty>}"
  fi
  echo "OK content-type robots.txt $ct"
}

check_sitemap() {
  local ct
  ct="$(content_type "/sitemap.xml")"
  if [[ "$ct" != *xml* ]]; then
    fail "${BASE_URL}/sitemap.xml expected *xml*, got ${ct:-<empty>}"
  fi
  if ! curl -sS -L "${BASE_URL}/sitemap.xml" | head -n 2 | grep -q '^<?xml'; then
    fail "${BASE_URL}/sitemap.xml does not look like XML"
  fi
  echo "OK sitemap.xml content-type $ct"
}

check_200 "/"
check_200 "/index.html"
for variant in root buy purchase gum test-variants; do
  check_redirect_to_root "/${variant}"
  check_redirect_to_root "/${variant}/"
  check_redirect_to_root "/${variant}.html"
done
for route in \
  /web/live/ /web/live/index.html \
  /web/new_landing_page/ /web/new_landing_page/index.html \
  /web/cloud_workspace/ /web/cloud_workspace/index.html; do
  check_redirect_to_root "${route}"
done
for route in \
  /deploy_dist/index.html /docs/GUMROAD_EMAIL_TEMPLATES.html \
  /web/archives/main_pre_merge_20251121_184736/claude_landing_page/index.html \
  /web/backups/landing-page-sync-20251123/index.html \
  /web/concepts/2026-07-31-b2c-redesign/index.html; do
  check_redirect_to_root "${route}"
done
check_robots
check_sitemap

echo "All checks passed for ${BASE_URL}"
