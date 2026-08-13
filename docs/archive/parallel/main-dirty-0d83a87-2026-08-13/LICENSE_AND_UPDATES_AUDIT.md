# Licensing & Updates — Code Audit

Date: 2025-10-31

This document cross-checks our current codebase against the pricing/licensing model and highlights concrete implementation gaps with suggested next steps.

## What Exists (Code)
- Local license storage
  - File: `desktop_app/license/storage.py:1`
  - Behavior: Saves `license.json` under `~/.signature_extractor/`; `is_licensed()` returns true for any key length ≥ 6.
- Simple license UI
  - File: `desktop_app/views/license_dialog.py:1`
  - File: `desktop_app/views/main_window.py:360` (License menu wiring)
  - Behavior: “Enter License…” opens dialog; “Buy License…” opens Gumroad URL via `GUMROAD_PRODUCT_URL` env var.

## What’s Missing vs. Docs
- Export gating (Evaluation mode)
  - Expectation: Export/Save disabled until licensed; clear CTA text.
  - Code: `on_export()` (desktop_app/views/main_window.py:760) has no gating.
- Update checks
  - Expectation: Manual “Check for Updates…” and weekly background check against `updates.json`.
  - Code: no update checker, no menu entry.
- License validation/caching
  - Expectation: Signed payload, periodic revalidation (when online), 14-day grace.
  - Code: purely local key presence; no online validation; no grace policy.
- Provider alignment
  - Expectation: Paddle/LemonSqueezy or Stripe
  - Code: Opens Gumroad product URL. Docs and code diverge.
- In-app upgrade surfaces
  - Expectation: Inline CTA in export dialog/status bar; “Manage License” entry.
  - Code: Only top-level License menu; export dialog has no CTA.
- Refund and legal links
  - Expectation: Refund link in About/License dialog; policies in Help.
  - Code: Not present in dialogs/menus.
- Watermark in evaluation mode (optional)
  - Expectation: Watermark overlay on preview.
  - Code: No watermark overlay.

## Recommended Changes (Surgical)
- Export gating (soft-to-hard toggle)
  - Add `self._licensed` check in `on_export()` and `on_save_to_library()` to show an upgrade dialog (soft gate now, hard gate once confident).
  - Files: `desktop_app/views/main_window.py:760`, `desktop_app/views/export_dialog.py`.
- Inline CTA surfaces
  - Export Dialog: add footer text “Export locked — Buy Lifetime” with a button that opens `on_buy_license()`.
  - Status bar: show “Evaluation mode — Export locked” when not licensed.
  - Files: `desktop_app/views/export_dialog.py`, `desktop_app/views/main_window.py`.
- Update checker (manual first)
  - Add Help menu item “Check for Updates…”; fetch static `updates.json`, compare `app_version`.
  - Files: `desktop_app/views/main_window.py`, new `desktop_app/update/checker.py`.
- Online validation (stub)
  - Add optional background task that pings a `LICENSE_VERIFY_URL` if set; cache `last_validation_at`.
  - Files: `desktop_app/license/storage.py` (extend schema), new `desktop_app/license/verify.py`.
- Provider unification
  - Decide on provider (Gumroad vs Paddle/Lemon). If Gumroad for launch, align docs; otherwise update `on_buy_license()` to open Paddle/Lemon checkout.
  - File: `desktop_app/views/main_window.py:1113`.
- Legal/refund links
  - Add “About/License” dialog with refund link and key management.
  - Files: new `desktop_app/views/about_dialog.py`, menu wiring in `main_window.py`.
- Watermark (optional)
  - Render a small “Evaluation mode” text overlay in preview if not licensed.
  - File: `desktop_app/widgets/image_view.py` (overlay paint).

## Config & Env
- `GUMROAD_PRODUCT_URL` or `CHECKOUT_URL` (if switching provider)
- `UPDATES_URL` (e.g., https://yourdomain.com/updates.json)
- `LICENSE_VERIFY_URL` (optional; for periodic checks when online)

## Definition of Done (Phase 1)
- Export shows friendly lock dialog when unlicensed; “Buy Lifetime” opens checkout.
- Help menu contains “Check for Updates…” which fetches `updates.json` and shows status.
- License dialog stores key and updates status bar; About dialog links refund/terms.
- Docs updated to match chosen provider and UX.

