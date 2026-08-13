# App Non‑Code Readiness Checklist

This document tracks every non‑coding deliverable to launch and support the desktop app professionally. Use it as the companion to LAUNCH_CHECKLIST, PRICING_IMPLEMENTATION, and MARKETING_PLAN.

## Product Decisions
- Pricing ladder and promise
  - Decision: Lifetime price ($29 recommended for launch tests; consider $19 early‑adopters or $39 A/B).
  - Refund: 30‑day money‑back guarantee; link surfaced in app and emails.
  - Evaluation mode: Preview unlimited; Export/Save locked until purchase. No free trial counters.
  - Acceptance: Pricing stated consistently across app, landing, emails; refund language present; Export gate text is clear.

## Legal & Policy
- Documents
  - Privacy Policy (local‑only by default; optional telemetry opt‑in).
  - Terms of Use + EULA (license scope, no reverse engineering, one‑user license, refund policy).
  - Third‑party notices (Qt/PySide6, OpenCV, Pillow, requests, jose, passlib, etc.).
- Compliance basics
  - Cookie/analytics notice (if landing uses analytics).
  - Data handling statement for cloud/Pro (future placeholder).
- Acceptance: Docs linked in footer (landing) and Help menu (app); attributions included with installer/bundle.

## UX Copy & In‑App Messaging
- Core texts (reference COPY_DECK)
  - CTAs: Buy Lifetime, Export locked notice, success toasts, error messages.
  - Tooltips: Zoom/Rotate/Export, Mode toggle, threshold.
  - Status bar: Uploading… / Processing… / Exported.
- Error catalog (friendly, actionable)
  - Backend offline; 404 image; 415 unsupported type; 500 processing failed; permission denied; disk full; large image guidance.
- Acceptance: All dialogs and toasts use consistent tone; no placeholder strings; spell‑check pass.

## Support Operations
- Contact & help
  - Support inbox (support@), autoresponder with receipt ETA and diagnostics steps.
  - Minimal Help Center: FAQ, How to open on macOS (unsigned), Troubleshooting.
- Diagnostics
  - “Report Issue / Send Diagnostics” menu opens logs folder and prepopulates email template.
- Acceptance: One‑click path from app to support with context instructions.

## Checkout & Licenses (No Trial)
- Provider setup
  - Product with OS variants; license key issuance; refund workflow; coupon codes; affiliate terms.
- Communications
  - Post‑purchase email: download links, license key, how‑to, refund note.
  - In‑app Buy link (env‑configurable URL).
- Acceptance: End‑to‑end test purchase → email receipt → license entry → Export unlocked.

## Landing & Assets
- Landing page content
  - Hero headline/subhead, annotated screenshots/GIFs, Buy button, guarantee, FAQs, legal links.
  - “How to open on macOS” for unsigned early builds.
- Press kit
  - App icon, logo, 3–5 screenshots with captions, one‑pager PDF.
- Acceptance: Page deployed under domain; links verified; assets crisp and legible.

## Analytics (Opt‑In)
- Metrics
  - Website: purchase clicks, attribution via UTM.
  - App (optional, opt‑in): first run, selection, preview rendered, export success, Buy click.
- Controls
  - Settings toggle “Help improve the app” with privacy summary.
- Acceptance: Opt‑in default off; events documented; data minimal and anonymous.

## Documentation Set
- Quick Start (desktop_app/README) with 2 GIFs.
- Export Options (formats/background/trim; already in docs).
- Keyboard Shortcuts cheat sheet (once added).
- Troubleshooting (errors + fixes; macOS Gatekeeper steps).
- Changelog policy and versioning.
- Acceptance: Open from Help menu; URLs stable; consistent ports (8001).

## QA & Test Plan
- OS matrix: macOS (Intel/Apple Silicon), Windows 10/11, Ubuntu LTS.
- Scenarios: Phone EXIF, large scans (A4 600dpi), tiny selections, invalid file types, offline backend.
- Performance: target <800ms preview on 8MP; memory stable on 50MP.
- Accessibility: keyboard navigation, high‑contrast readability, minimum 12–13px labels.
- Acceptance: Runbook with pass/fail notes; top issues triaged.

## Release & Distribution
- Build artifacts: naming, version semantics, checksums.
- Signing strategy: macOS notarization (post‑MVP), Windows signing; interim instructions for unsigned builds.
- Release notes: CHANGELOG sections; GitHub Releases entry per tag.
- Acceptance: Reproducible build steps; tag→artifacts pipeline works locally.

## Data & Storage
- Library path conventions
  - macOS: ~/Library/Application Support/Signature Extractor/signatures
  - Windows: %AppData%\Signature Extractor\signatures
  - Linux: ~/.signature_extractor/signatures
- Config file contents: license key, install id, last validation, preferences.
- Backup guidance: simple instructions in docs.
- Acceptance: Paths documented; app points to same defaults.

## Security & Updates
- Dependency audit: pip‑audit run; versions pinned; quarterly review.
- Vulnerability handling: email contact + patch window commitment.
- Update policy: how users get new builds; auto‑update feasibility note.
- Acceptance: Notices added; audit report filed in repo (or internal doc).

## Samples & Tutorials
- Sample files: 6–10 safe‑to‑share images with varied backgrounds/orientation.
- Tutorial checklist: 60‑second flow; 3 short GIFs.
- Acceptance: Bundled or downloadable; license clarified.

## Localization & Future Readiness
- Externalize user‑visible strings where easy; avoid hard‑coding.
- Date/time numbers in ISO formats in metadata JSON.
- Acceptance: Strings map exists; no blockers to add locales later.

## Open Decisions (to confirm before code)
- Price ladder: $19 early adopters (first 100) vs $29 flat.
- Checkout provider: Gumroad vs LemonSqueezy (default: Gumroad for speed).
- Telemetry stance: Opt‑in now vs later; event list minimal.
- macOS signing at launch: unsigned with instructions vs wait for notarization.

---

Owner fields and due dates can be added inline once assignments are made. Use this as the non‑code gate for go/no‑go.

