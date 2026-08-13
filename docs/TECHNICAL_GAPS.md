# Technical Gaps & Action Plan (Updated Oct 27, 2025)

This reflects the current codebase on the `feature/desktop-pyqt-base` branch after a full walkthrough of the desktop app and backend.

---

## Critical Launch Gaps

### 1. Ports & Configuration
- `desktop_app/README.md` previously referenced port **8000** while the app and backend default to **8001**.
- No checked-in `.env.example` describing required variables (`API_BASE_URL`, `JWT_SECRET`, `DATABASE_URL`). *(Superseded 2026-08-12; addendum below.)*
**Action:** Review stale references by location and keep active and archived materials explicitly separated before launch claims. (Estimate: 30–45 min)

### 2. Packaging & Distribution
- No PyInstaller/Nuitka build scripts; no unsigned DMG/EXE/AppImage artifacts.
- No instructions for macOS Gatekeeper bypass while unsigned.
**Action:** Produce PyInstaller specs for macOS/Windows/Linux, generate unsigned installers with a short “How to open” note, plan for signing/notarization post-launch. (Estimate: 1–2 days initial pass)

### 3. Checkout Flow & Refund Surfacing
- In-app “Buy License…” opens env-configured URL and “Enter License…” stores the key, but there is no actual Gumroad product yet.
- 30-day refund promise is not surfaced inside the app (Help/About).
**Action:** Create Gumroad product, verify license email, add refund link in Help/About, test end-to-end purchase → key entry → export. (Estimate: 1 day including content)

### 4. Backend Cleanup & Upload Safety
- `backend/app/main.py` and `backend/app/routers/extraction.py` contain large commented legacy blocks and inconsistent upload paths (relative vs absolute).
- Upload endpoint saves files as `.png` unconditionally without validating extension/content-type.
**Action:** Strip commented sections, standardize upload directory handling, validate MIME types/size, return concise error JSON. (Estimate: 2–3 hours)

### 5. QA Runbook
- No recorded smoke test results for clean macOS/Windows/Linux VMs covering EXIF photos, large scans, tiny selections, invalid formats, and offline backend.
**Action:** Execute and document pass/fail for the scenarios above before accepting payments. (Estimate: 0.5 day)

---

## High-Priority Polish (Pre-Launch)

1. **Shortcuts Completion & Documentation**  
   Ctrl/Cmd+O/E/C and rotation exist, but Delete (clear) and Esc (cancel) are missing; no shortcuts cheat sheet under Help. Add keys and document them. (1–2 hrs)

2. **Drag-and-Drop + Recent Files**  
   Allow dropping images onto the window and expose a “Recent files” list (last five paths). Improves onboarding speed. (2–3 hrs)

3. **Error & Offline Messaging**  
   Wrap API calls with friendly toasts for backend offline, 404/415, disk full, oversized images; avoid raw exception dialogs. (1–2 hrs)

4. **Help Menu & Diagnostics**  
   Add Help menu linking to Quick Start, Export Options, Shortcuts, Troubleshooting, Privacy, Terms/EULA. Include “Report Issue / Send Diagnostics” that opens logs folder and copies template text. (2–3 hrs)

5. **Evaluation Mode Strategy**  
   Currently soft (no gate). Decide whether to enforce export/save lock until license or keep soft gate with clear CTA copy. Update messaging accordingly. (Workshop + 1 hr code if gating)

---

## Medium-Term (Post-Launch) Enhancements

1. **Advanced Processing Controls** – Otsu/Adaptive thresholds, simple erode/dilate, optional edge smoothing. (4–6 hrs)
2. **Presets** – Save/load color + threshold combinations for recurring use. (3–4 hrs)
3. **Analytics (Opt-In)** – “Help improve the app” toggle; minimal events (start, preview, export, buy). Default off, document privacy stance. (2–3 hrs + infra)
4. **Legal Surfaces** – Finalize Privacy Policy, Terms, 3rd-party notices; link from `Help > About`. (0.5–1 day with counsel template)
5. **Testing Infrastructure** – Add integration tests (upload → process) and keep regression harnesses; consider pytest + httpx. (4–6 hrs setup)
6. **Crash Reporting** – Opt-in Sentry (or similar) for unhandled exceptions. (2–3 hrs)
7. **Auto-Detection Research** – Contour-based prototype & evaluation per AUTO_DETECTION_ML.md. (multi-week research)

---

## Recently Completed (Reference)

- Rotate CW/CCW with session reset (desktop_app/views/main_window.py:on_rotate)
- Local library save/list/delete with timestamped names (desktop_app/library/storage.py)
- JSON metadata export alongside PNG
- Clipboard copy with transparency preserved
- Auto-preview on selection/threshold change; preview toggles remove manual button

---

## Open Decisions

1. **License enforcement:** Hard gate before launch or ship soft gate + monitoring?  
2. **Price ladder:** $19 early adopters vs flat $29.  
3. **Telemetry:** Ship opt-in analytics at launch or defer?  
4. **macOS signing:** Ship unsigned with instructions or wait for Developer ID notarization?

Answering these will determine which high-priority tasks stay in the launch gate.


## Addendum (2026-08-12)

- `desktop_app/README.md` now references port **8001** consistently for local runs.
- `.env.example` exists at repository root and includes API, auth, DB, and updates settings.
- `scripts/run-backend-dev.sh` is now aligned with the same port policy and uses `BACKEND_PORT` (default `8001`).
- Remaining `8000` references are concentrated in historical/archived launch artifacts, not active runtime instructions.
- Next decision: whether to normalize archived references or explicitly treat them as historical only.
