# Launch TODOs and Roadmap (condensed)

This mirrors the working list we’ve been tracking in chat. Status will be kept up to date here.

Canonical backlog governance is now in:
`docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`

Update rule: any item with explicit acceptance or an unresolved risk stays explicitly in-progress/pending in
`Docs/LAUNCH_TOP_10_STATUS.md` and is reflected as "in-progress" or "pending" in this list.

Legend: [x] done • [~] in progress • [ ] pending

Full backlog (34 items): see TODO_FULL.md

## Top 10 launch gate

- [x] Auto-preview on selection/threshold changes (remove manual Preview)
- [x] Export/Save enablement tied to preview existence
- [x] Rotate CW/CCW with re-upload as new session
- [x] “My Signatures” local library (save/list/delete)
- [x] Library double-click opens into Source pane (re-uploads to backend)
- [x] Fit-to-view improved for transparent images
- [x] Left sidebar fixed width (avoid taking half the window)
- [x] Clearer icons + tooltips; de-dupe emoji vs system icons
- [~] Color swatch reflects current color consistently
- [x] Keyboard shortcuts for common actions (Cmd on macOS / Ctrl on others)

## Desktop UX polish

- [x] Lighter native look on macOS (minimal custom styles)
- [ ] Ensure right pane dominance and splitter behavior across window sizes
- [x] Clipboard: Copy result PNG with transparency
- [ ] Quick export presets (PNG w/transparent, JPG white bg)
- [x] JSON metadata export (bounds, threshold, color)
- [ ] Better status messages + unobtrusive errors

## Library behavior

- [x] Save extracted PNG with timestamped filename
- [x] Delete via context menu
- [x] Limit list to 50 recent
- [x] Show human-friendly names and times
- [x] Persist to ~/.signature_extractor/signatures
- [x] Opening loads into Source and resets preview

## Color/selection

- [~] Color picker swatch updates immediately and stays in sync
- [ ] Optional eyedropper/average color from selection (future)
- [ ] Threshold ramp preview (future)

## Backend

- [ ] Clean up commented/duplicate code
- [x] Confirm port 8001 across docs, tests, and desktop client
- [ ] Smoke tests: /health, upload, process round-trip
- [x] Canonical root test collection covers `tests/`, `backend/tests/`, and `desktop_app/tests`; optional PDF and Qt event-loop skips remain explicit
- [x] Remove hardcoded backend database credential defaults, fail closed for incomplete production configuration, and protect local PII paths with owner-only permissions

## Packaging and distribution

- [ ] PyInstaller spec for macOS bundle
- [ ] Unsigned DMG for early adopters; add Gatekeeper bypass notes
- [ ] Code signing + notarization (post-early access)
- [x] Manual update check in-app (“Check for Updates…”) using static updates.json

## Commerce (Gumroad first)

- [ ] Create Gumroad account + product (Standard license)
- [ ] Set GUMROAD_PRODUCT_URL in .env and wire Buy action (Buy menu opens env URL; fallback present)
- [ ] Product page copy (benefits, usage GIF, FAQ)
- [ ] Deliverable bundles: macOS app (unsigned initially)
- [ ] Plan later migration path (DoDoPayments)

## Docs and comms

- [ ] Update README with desktop-only instructions
- [ ] Add quickstart with screenshots
- [ ] Record short demo video (open → select → preview → export → library)
- [x] Local canonical product surface per `docs/LANDING_PAGE_PLAN.md` and the document-registration-studio direction; hosted publication remains a separate release gate
- [ ] Publish `updates.json` and stable downloads; add legal links (Privacy, Terms/EULA, Refund)

## Licensing & Evaluation

- [x] Local paid-feature gating uses one signed receipt boundary; legacy keys fail closed and the historical test key is explicit test mode. See `docs/decisions/ADR-0151-signed-local-entitlement-activation.md`.
- [ ] Provider adapter and controlled activation: configure product ID, verify receipt delivery, and exercise replay, timeout, refund, dispute, chargeback, offline grace, and support recovery (`L0-02`, `QA-15`)
- [x] Native-GUI proof archived for cancel/confirm, keyboard focus, preview rendering, and failure messaging; rerun after candidate-dialog or desktop-runtime changes (`RECON-23`)
- [~] Synthetic auto-detection baseline recorded; permissioned held-out evaluation, provenance, recall@k/IoU, failure classes, and an accuracy-bar decision remain open (`RECON-24`)
- [ ] Export gating: show Upgrade dialog if unlicensed (soft gate first)
- [ ] Status bar note when unlicensed: “Evaluation mode — Export locked”
- [ ] Optional watermark overlay in evaluation mode (off by default)

## Local product reconciliation addendum (2026-08-13)

The local product is now being advanced against the long-term document
registration-studio direction. The canonical task record is
`docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`; these entries keep the
condensed TODO list honest while the larger reconciliation remains active.

- [x] `RECON-13` Promote the selected registration-studio direction to the local canonical root.
- [x] `RECON-14` Add reusable real-browser proof for the root, workspace handoff, keyboard/pointer states, responsive widths, and reduced motion.
- [x] `RECON-16` Add one-command local stack startup with isolated data defaults and clean process shutdown.
- [x] `RECON-17` Add disposable local source-to-ready proof covering extraction, cleanup, vault, placement/export, forced failure, retry, passports, and artifact receipt, then join it to the browser proof through the local bridge.
- [x] `RECON-18` Implement one canonical metadata-only local companion bridge from the desktop workflow store to the browser workspace. See `docs/decisions/ADR-0147-local-desktop-passport-bridge-boundary.md`.
- [x] `RECON-19` Harden local bridge retry with store locking, durable idempotency receipts, deterministic default keys, and concurrent replay tests. See `docs/decisions/ADR-0147-local-desktop-passport-bridge-boundary.md`.
- [x] `RECON-20` Prove the local macOS ARM64 packaged runtime, prevent `.env` bundling, and package the canonical browser workspace. See `docs/review/local_packaging_runtime_proof_2026-08-13.md`.

The local closure claim is intentionally narrower than a hosted or packaged
release claim. Hosted deployment, provider activation, signed artifacts,
cross-platform installation, and external user research remain separate
backlog gates.

The local packaged-runtime claim is also deliberately narrow: QA-20 is closed
for macOS ARM64 only. Intel, Windows, Linux, notarization, clean installation,
rollback, hosted deployment, and provider activation remain open.

---

Notes

- Pending items marked [~] have code in place; needs verification or minor follow-ups.
- If you want these grouped differently or tracked per-milestone, say the word and I’ll split into M1/M2 with dates.
