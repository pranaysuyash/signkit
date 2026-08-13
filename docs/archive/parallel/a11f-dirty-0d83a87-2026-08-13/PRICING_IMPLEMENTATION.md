# Pricing Implementation Plan — Signature Extractor (No Trial)

This complements docs/PRICING.md by describing how to implement licensing, payments, and upgrade flows with no free trial.

## Offers (from PRICING.md)
- Lifetime Desktop: $39 list price (launch promo $29) with PDF workflow included
- Pro Workspace (future): $15/month or $129/year
- Team/Enterprise: Deferred

## Payment & Licensing Options
- Paddle or Lemon Squeezy: VAT/compliance, license keys, refunds (recommended to ship fast)
- Stripe + self-rolled licensing: Webhooks + license store; more control, more work

Recommendation: Start with Paddle/Lemon Squeezy for checkout + license issuance. Add Stripe later if needed.

## License Model
- Lifetime: Per-user license key; no expiry
- Pro: Subscription tied to email; license checks on renewal (when launched)
- Offline-friendly: Write license file to user config dir; validate offline, refresh in background when online

## Update Entitlement & Delivery
- Lifetime license covers all updates to the offline desktop app (image + PDF workflows) as long as the desktop SKU exists; new features ship as minor releases (e.g., v1.1, v1.2).
- Major architectural shifts (e.g., cloud workspace) are reserved for Pro/Team. Lifetime users retain read-only access to any cloud-dependent UI with a “Pro feature” badge.
- Distribution: ship signed installers (DMG/EXE/AppImage). App exposes `Help → Check for Updates…` that hits a static `updates.json` served from the website/CDN.
- Background update check runs weekly when network is available; stores the latest version metadata in `~/.signature_extractor/update_cache.json`.
- When a newer build is detected, surface a non-blocking banner (“Update available — Download v1.2”) linking to the installer. Never auto-download without consent.
- Maintain previous installers for rollback; license file and local library persist across upgrades.

## License Validation & Caching
- Activation: user pastes license key → app exchanges with payment provider API → receives signed payload (`license_type`, `expires_at`, `features`) → stored as `license.json`.
- Offline behavior: once activated, license remains valid indefinitely; app only requires revalidation when online and `last_validation_at` is older than 30 days.
- Grace period: if remote validation fails, keep app unlocked for 14 days while showing “Unable to validate license” toast; revert to evaluation mode afterwards.
- Security: store hashed machine identifier + signature to prevent casual sharing; allow manual “Deactivate this device” via support if machine limit exceeded.

## Evaluation Mode (No Trial)
- Pre-purchase behavior: Unlimited preview (selection, threshold/color, PDF placement) but export/save disabled
- Optional: Watermark overlay in preview to signal evaluation mode
- Entry points: “Buy Lifetime ($39)” headline with “$29 launch pricing” badge in export dialog and status bar

## Upgrade Flows
- In-app “Buy” dialog: Price, benefits, 30‑day refund note, license key field
- Redemption: Paste license key → stored locally → unlocks export immediately
- Sync: On app start (if online), validate license; continue offline if cached

## Add-on & Pro Upsell Touchpoints (Future)
- Feature gating: mark Pro-only UI with lock icon + tooltip; clicking opens upgrade dialog pre-filled with user email.
- In-app purchase flow delegates to hosted checkout; on success, webhook updates license record → app polls via `/licenses/{key}` endpoint → switches to `pro` tier without restart.
- Offer limited-time add-ons (e.g., font packs) via the same dialog with “Apply coupon” support; unlocks by toggling feature flags in the license payload.
- Keep offline-first experience: add-ons that require downloads (e.g., templates) cache locally and respect company firewall environments.

## Refunds & Transitions
- 30‑day money‑back on Lifetime; provider webhook revokes license
- Pro cancellation (future): Downgrade to Lifetime if present; otherwise lock exports

## Price Localization & Coupons
- Use payment provider geo‑pricing
- Launch coupon (e.g., LAUNCH20) valid for first 14 days

## Data Model (Local)
- `~/.signature_extractor/config.json`
  - `license_key`, `license_type` (lifetime/pro)
  - `license_issued_at`, `last_validation_at`
  - `first_run_at`, `install_id`

## UI Touchpoints
- Export dialog: “Export is locked — Buy Lifetime to unlock (30‑day refund)”
- Status bar: “Evaluation mode — Export locked” with “Buy” button
- About/License dialog: Enter key, manage license, refund link

## Metrics
- Website → purchase rate
- First run → purchase rate
- Refund rate (Lifetime)
- (Future) Churn for Pro

## Roadmap Hooks
- “Manage License” menu entry
- Background validator (weekly) with back‑off and privacy‑respectful logs
- Graceful error states and clear messaging if license invalid
