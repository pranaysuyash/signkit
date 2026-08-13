# App Open Items (Launch-Focused)

Use this list to track app-side tasks only (no web or backend infra beyond what’s surfaced in-app). Keep this aligned with LAUNCH_TOP_10_STATUS.md.

Canonical backlog reference:
`docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`

Execution rule:
- In-app item status here must match this list and `Docs/LAUNCH_TOP_10_STATUS.md`.
- Every unresolved behavior mismatch (including licensing) gets an explicit status transition entry in the PO backlog.

## In‑App UX/Features

- [x] Rotate 90° CW/CCW with re‑upload and selection reset (main_window.py:on_rotate)
- [x] Clipboard Copy of PNG with alpha (Copy button + Ctrl/Cmd+C)
- [x] Keyboard Shortcuts — Open/Export/Copy/Zoom/Rotate implemented; Delete (clear) + Esc (cancel) and documentation updates now complete
- [x] Library MVP — auto-save, list, double-click open, context delete (library/storage.py + main_window)
- [x] Export Metadata JSON saved alongside PNG (Export JSON button)
- [x] Drag‑and‑drop to open image (implemented in widgets/image_view.py with fileDropped signal)
- [ ] Recent files (last 5)
- [ ] Improve error toasts: backend offline, 404/415, 500, disk full, large image guidance (friendly, actionable messages)
- [ ] Optional advanced processing: Otsu/Adaptive thresholds, erode/dilate, edge smoothing (post-launch)

## Local RAG & Summaries (In-App)

- [ ] Right sidebar: “Understand” with tabs (Summary, Q&A)
- [ ] First-run model download flow (small pack; show size and path)
- [ ] Indexing progress + cancel; per-PDF cache
- [ ] Explain selection (context menu) → short paraphrase
- [ ] Citations by page in answers

## Licensing/Checkout (In‑App Surfaces)

- [x] Wire Buy link (env‑configurable) and “Enter License” dialog to store key locally
- [x] Evaluation mode hard-gate strategy is active for export/copy/save-to-library in unlicensed mode
- [x] Surface 30-day refund link in Help/About
- [x] Export/copy/save gating aligned in `on_export`, `_copy_result_to_clipboard`, `on_save_to_library`
- [x] Status bar now emits “Evaluation mode — <Action> is locked” for gated export/copy/save actions
- [x] Add “Check for Updates…” menu; implement static `updates.json` check
- [ ] Optional watermark overlay on preview in evaluation mode

## Platform Polish

- [x] Consistent icons (system icons via resources/icons; emoji only as fallback)
- [~] Tooltips present; still add Keyboard shortcuts cheat sheet under Help
- [x] Native feel: macOS uses default style; platform shortcuts use Cmd vs Ctrl

## Help & Docs (Accessed from App)

- [x] Help menu links: Quick Start, Export Options, Shortcuts, Troubleshooting, Privacy, Terms/EULA
- [x] “Report issue / Send diagnostics” opens logs folder + prefilled email template

## Packaging/Release Touchpoints

- [x] PyInstaller builds for macOS (ARM64 + Intel via GitHub Actions)
- [x] GitHub Actions CI/CD configured (.github/workflows/build-macos.yml)
- [x] DMG creation automated in build pipeline
- [x] "How to open on macOS" instructions included in GitHub Release notes
- [ ] Versioned artifact names and checksums; CHANGELOG entry per release
- [ ] Windows/Linux builds (post-launch)

## Config & Consistency

- [x] Unify ports to 8001 across desktop docs and in-app references (including local backend runner script)
- [x] Add .env.example (API_BASE_URL, JWT_SECRET, DATABASE_URL for SQLite)

## Analytics (Opt‑In)

- [ ] Settings toggle “Help improve the app” (default off)
- [ ] If enabled, minimal events: start, selection, preview rendered, export success, Buy clicked

## Legal/Policy Surfaces

- [x] Link Privacy Policy, Terms/EULA from Help
- [x] Third‑party notices from About

## QA Matrix

- [ ] Clean VM tests: macOS/Win/Linux — open → select → preview → rotate → export; EXIF photos; large scans; tiny selections; invalid file types; offline backend
- [ ] Performance: preview latency target; memory sanity on >20MP

## Samples/Assets

- [ ] Bundle or link 6–10 sample documents; confirm licensing
- [ ] Two short GIFs for Quick Start (select/preview, export)

Notes

- When an item moves to “done”, update LAUNCH_TOP_10_STATUS.md with acceptance evidence (e.g., screenshot path, test note).
