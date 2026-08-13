# Full Launch Roadmap

This document mirrors the full backlog we've been tracking. It's grouped by area and uses statuses: [x] done • [~] in progress • [ ] pending • [s] skip/later.

**Progress: 18 done / 7 in-progress / 12 pending / 3 skip-for-now**

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
- [~] Confirm port 8001 across docs, tests, and desktop client
- [ ] Smoke tests: /health, upload, process round-trip

## Packaging and distribution (3)

- [ ] PyInstaller spec for macOS bundle
- [ ] Unsigned DMG for early adopters; add Gatekeeper bypass notes
- [ ] Code signing + notarization (post-early access)

## Commerce (2)

- [ ] Create Gumroad product and set GUMROAD_PRODUCT_URL in .env; wire Buy action
- [ ] Product page copy (benefits, usage GIF, FAQ, support/contact)

## Licensing, updates, and evaluation (10)

- [~] HIGH: Evaluation Mode Gate (Soft) — non-blocking banner + periodic reminder; no feature gating
- [ ] Optional watermark toggle for evaluation exports (off by default)
- [ ] Local license storage UX polish (Enter/Change license; no hard gate)
- [ ] Export gating: Block Export/Save when unlicensed; show friendly Upgrade dialog with CTA
- [ ] Add status bar message when unlicensed: “Evaluation mode — Export locked”
- [x] Add “Check for Updates…” in Help; fetch `UPDATES_URL` JSON and compare version
- [ ] Background weekly update check; store cache in `~/.signature_extractor/update_cache.json`
- [ ] Align provider selection (Gumroad vs Paddle/Lemon) across docs and code
- [ ] License verification stub: optional online check if `LICENSE_VERIFY_URL` set; cache `last_validation_at`
- [ ] Add About/License dialog with refund link and key management

## Docs and comms (1)

- [ ] Update README with desktop-only instructions and quickstart screenshots

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

- [ ] Implement landing sections per `docs/LANDING_PAGE_PLAN.md`
- [ ] Add comparison table from `docs/PRICING.md`
- [ ] Wire primary CTA to checkout with UTM params
- [ ] Publish `updates.json` at stable URL and link on page footer
- [ ] Add legal footer links (Privacy, Terms/EULA, Refunds, Notices)
- [ ] Produce 45s hero demo and 15s PDF placement GIF
- [ ] Press kit: icon, logo, 3–5 screenshots with captions
- [ ] A/B test CTA copy and pricing badge (optional)

---

Notes

- This file is the authoritative full list. For a condensed “Top 10” tracker, see docs/TODO.md.
