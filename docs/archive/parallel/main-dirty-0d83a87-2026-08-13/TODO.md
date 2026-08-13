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
- [~] Confirm port 8001 across docs, tests, and desktop client
- [ ] Smoke tests: /health, upload, process round-trip

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
- [ ] Simple landing page per `docs/LANDING_PAGE_PLAN.md` (hero, features, comparison, pricing, FAQ)
- [ ] Publish `updates.json` and stable downloads; add legal links (Privacy, Terms/EULA, Refund)

## Licensing & Evaluation

- [ ] Export gating: show Upgrade dialog if unlicensed (soft gate first)
- [ ] Status bar note when unlicensed: “Evaluation mode — Export locked”
- [ ] Optional watermark overlay in evaluation mode (off by default)

---

Notes

- Pending items marked [~] have code in place; needs verification or minor follow-ups.
- If you want these grouped differently or tracked per-milestone, say the word and I’ll split into M1/M2 with dates.
