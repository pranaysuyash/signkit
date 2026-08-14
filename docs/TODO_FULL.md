# Full Launch Roadmap

This document preserves the comprehensive roadmap we've been tracking. It is
grouped by area and uses statuses: [x] locally evidenced, [~] in progress,
[ ] pending, and [s] skip/later. Current priority, ownership, evidence, and
release status are canonical in
`docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md` and `docs/QA_RESULTS.md`.

**Progress: 19 done / 7 in-progress / 12 pending / 3 skip-for-now**

Legend:

- Top 10 Launch = must-have for initial release
- Next Phase = implement after launch if needed
- [s] = skip for first release (defer to v2 or optional)

## Top 10 launch gate (10)

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

## Desktop UX polish (7)

- [x] Lighter native look on macOS (minimal custom styles)
- [ ] Ensure right pane dominance and splitter behavior across window sizes
- [x] Clipboard: Copy result PNG with transparency
- [ ] Quick export presets (PNG transparent, JPG white background)
- [x] JSON metadata export (bounds, threshold, color)
- [ ] Better status messages + unobtrusive errors
- [ ] Animate result pane refresh (short fade) when preview regenerates
- [ ] Replace modal notifications with inline banner component in sidebar
- [ ] Collapsible control groups or first-run guided tour overlay
- [x] Drag-and-drop to open image into Source
- [x] Add subtle drop shadow/vignette behind preview/result stack for depth
- [x] Replace emoji-style mode toggle with icon + label toggle button
- [x] Provide mini colour history swatches beneath colour picker
- [x] Add quick colour preset buttons (brand blue, black, etc.) near colour picker

## Library behavior (5)

- [x] Save extracted PNG with timestamped filename
- [x] Delete via context menu
- [x] Limit list to 50 recent
- [x] Show human-friendly names and times
- [x] Opening loads into Source and resets preview

## Color and selection (3)

- [ ] Eyedropper / average color from selection
- [ ] Threshold ramp preview (quick compare)
- [ ] Live selection size while dragging; nudge selection with arrow keys

## Backend (3)

- [ ] Clean up commented/duplicate code
- [x] Confirm port 8001 across docs, tests, and desktop client
- [x] Local smoke tests: /health, authenticated upload, process/export/deletion round-trip (`QA-53`); hosted smoke remains a separate gate

## Packaging and distribution (3)

- [x] PyInstaller spec for the current macOS arm64 bundle (`QA-55`)
- [~] Local macOS arm64 DMG proof exists (`QA-55`); Gatekeeper guidance, signing, notarization, and other-platform bundles remain open
- [ ] Code signing + notarization (post-early access)

## Commerce (2)

- [ ] Create Gumroad product and set GUMROAD_PRODUCT_URL in .env; wire Buy action
- [ ] Product page copy (benefits, usage GIF, FAQ, support/contact)

## Licensing, updates, and evaluation (10)

- [x] Local evaluation and entitlement boundary uses signed receipts and an Upgrade path; the older soft-only framing is superseded (`L1-01`, `QA-23`)
- [ ] Optional watermark toggle for evaluation exports (off by default)
- [ ] Local license storage UX polish (Enter/Change license; no hard gate)
- [x] Export gating blocks paid actions when unlicensed and exposes the Upgrade path (`L1-01`, `QA-23`)
- [x] Status bar message when unlicensed explains the evaluation-mode export lock (`L1-01`, `QA-23`)
- [x] Add “Check for Updates…” in Help; fetch `UPDATES_URL` JSON and compare version
- [ ] Background weekly update check; store cache in `~/.signature_extractor/update_cache.json`
- [ ] Align provider selection (Gumroad vs Paddle/Lemon) across docs and code
- [ ] License verification stub: optional online check if `LICENSE_VERIFY_URL` set; cache `last_validation_at`
- [ ] Add About/License dialog with refund link and key management

## Docs and comms (2)

- [ ] Update README with desktop-only instructions and quickstart screenshots
- [x] Keep optional landing analytics fail-silent when `gtag` is absent while preserving configured event forwarding (`QA-62`); provider activation, consent, hosted parity, and production observability remain separate

## Local RAG & Summaries (12)

- [ ] Support text‑based PDFs only (detect and show unsupported notice for scans)
- [ ] Add pdf text extraction fallback via pdfminer.six (keep pypdfium2 first)
- [ ] Chunking + normalization pipeline with page mapping
- [ ] BM25 retriever baseline (Whoosh) with MMR
- [ ] Optional embeddings via llama.cpp + FAISS as an enhancement
- [ ] TL;DR summarization with 1–2B instruct model (optional download)
- [ ] Q&A with retrieval (k=8–12) + MMR; include page citations
- [ ] UI: “Understand” sidebar with Summary + Q&A tabs
- [ ] Model download manager (integrity check, resume)
- [ ] Key terms extraction into structured JSON (phase 2)
- [ ] Red flag detection (rules + LLM judge) (phase 2)
- [ ] LRU cache pruning and cancelable jobs (phase 2); optional larger models (phase 3)

## Add‑On Packaging (Document Understanding)

- [ ] Add feature flag `document_understanding_local` in license payload
- [ ] Checkout + unlock flow for add‑on (lifetime); included in Pro
- [ ] UI gating: Upgrade dialog when accessing Understand pane without add‑on

## Landing page (8)

- [x] Implement the local canonical landing sections per the document-registration-studio direction (`QA-51`, `QA-58`); hosted publication remains separate
- [ ] Add comparison table from `docs/PRICING.md`
- [x] Wire the local canonical CTA to state-aware checkout with bounded UTM params (`QA-27`, `QA-51`); provider activation and hosted parity remain separate
- [ ] Publish `updates.json` at stable URL and link on page footer
- [x] Add local legal footer links for Privacy, Terms, EULA, and support; legal approval and hosted serving remain separate (`L1-02`, `QA-27`)
- [ ] Produce 45s hero demo and 15s PDF placement GIF
- [ ] Press kit: icon, logo, 3–5 screenshots with captions
- [ ] A/B test CTA copy and pricing badge (optional)

---

## Status synchronization addendum (2026-08-14)

This full roadmap is a preserved planning inventory, not a second task
authority. The Product Owner backlog owns current status. Local closures in
this file are linked to QA evidence, while hosted deployment, provider
activation, signing, notarization, cross-platform packaging, rollback,
permissioned real-corpus evaluation, and user research remain open.

The optional landing-analytics boundary is locally closed by QA-62: missing
`gtag` is silent, the canonical asset is explicitly versioned for cache
invalidation, and configured forwarding remains tested. This does not claim
provider activation, consent compliance, hosted parity, event delivery, or
production observability.

Notes

- This file is a preserved full roadmap inventory. For the condensed tracker,
  see `docs/TODO.md`; for current status, use the Product Owner backlog and QA
  matrix.
