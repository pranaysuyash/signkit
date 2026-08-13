# Launch Top 10 - Status Report

This document maps your "Launch Top 10" list to what's been implemented, what needs to be done, and what should be skipped for the first release.

Canonical task tracker: `docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`

**Summary: 5 done / 2 in-progress / 4 pending (must-do) / 0 skip**

- **Canonical backlog:** `docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`
- **Current PO contract:** any item with unresolved acceptance remains `in-progress` or `pending` until evidence is attached in that backlog.

---

## 1. Evaluation Gate [x] COMPLETE (linked to L1-01, L0-02)

**Your requirement:** Export/save disabled until license present; clear CTA in export dialog/status bar; unlock immediately after key entry; license cached offline.

**Current state:**

- [x] License menu with Buy link (uses GUMROAD_PRODUCT_URL env)
- [x] Local license entry/storage (desktop_app/license/)
- [x] Soft non-blocking mode foundation is in place
- [x] Export hard-gated through license enforcement helper
- [x] Save to Library and Copy behavior now enforced through the same gate path as Export
- [x] Clear CTA banner/reminder (status bar unlock CTA now present)

**Decision:** **POLICY APPLIED (hard gate across Export / Copy / Save-to-Library)**

`on_export`, `on_copy`, `on_save_to_library`, and toolbar copy now all enforce the same
license gate and use the same lock messaging.

**Action needed:** decide and document consistent policy in product + release notes.

**Code files:** `desktop_app/views/main_window_parts/extraction.py`, `desktop_app/license/storage.py`

---

## 2. Checkout + License [~] IN PROGRESS (MUST DO)

> Current truth (2026-08-13): the local app now accepts only a provider-issued
> signed activation receipt for paid access. The earlier “stores a key locally”
> wording below is historical and is superseded by
> `docs/decisions/ADR-0151-signed-local-entitlement-activation.md`. Provider
> configuration, controlled purchase, refund/revocation delivery, and support
> recovery remain open.

**Tracked requirement:** Provider-backed checkout and receipt delivery, with a
local-first signed activation boundary and a documented refund path.

**Current state:**

- [x] In-app "Enter License" UI accepts signed receipt JSON and stores normalized evidence locally
- [x] Buy menu opens GUMROAD_PRODUCT_URL from env
- [ ] Gumroad account created
- [ ] Product created on Gumroad
- [ ] License key email flow configured
- [x] 30-day refund link documented

**Decision:** **BLOCKED pending the commercial/provider decision and fulfilment evidence**

- The local entitlement boundary is ready for a provider adapter, but provider
  fulfilment and purchase evidence are not present yet.
- **Action needed:**
  1. Select one provider and product/version mapping
  2. Configure the provider adapter without embedding provider secrets
  3. Exercise signed receipt delivery, duplicate/retry, refund, dispute,
     chargeback, offline grace, and support recovery
  4. Update checkout and legal claims only after that evidence exists

**Code files:** `desktop_app/views/main_window.py` (on_buy_license), `.env`

---

## 3. Desktop Packaging [ ] PENDING (MUST DO)

**Your requirement:** PyInstaller builds for macOS/Windows/Linux; basic signing where feasible; smoke-test open → select → preview → export on clean VMs.

**Current state:**

- [x] Code is packagable (no web dependencies)
- [ ] PyInstaller spec created
- [ ] macOS build tested
- [ ] Windows build tested
- [ ] Linux build tested
- [ ] Smoke tests run on clean VMs
- [ ] Basic signing (macOS unsigned initially OK)

**Decision:** **DO NOW**

- Critical for distribution
- **Action needed:**
  1. Create PyInstaller spec file
  2. Build macOS .app bundle first
  3. Test on clean macOS VM
  4. Document Gatekeeper bypass for unsigned app
  5. Create Windows/Linux builds (can be post-macOS)

**Files to create:** `signature_extractor.spec`, build scripts, distribution docs

---

## 4. Rotate 90° CW/CCW [x] DONE ✓

**Your requirement:** Rotate locally (PIL), re-upload as new session, reset selection; visible status messages. Acceptance: orientation correct; no coordinate bugs.

**Current state:**

- [x] Rotate CW/CCW buttons in UI
- [x] PIL-based rotation with expand=True
- [x] Re-upload to backend for new session
- [x] Selection reset after rotation
- [x] Status messages ("Uploading rotated image...", "Rotated and uploaded")
- [x] Keyboard shortcuts (Cmd/Ctrl+] and Cmd/Ctrl+[)

**Decision:** ✓ **COMPLETE - NO ACTION NEEDED**

**Code files:** `desktop_app/views/main_window.py` (on_rotate)

---

## 5. Clipboard Copy [x] DONE ✓

**Your requirement:** Copy current PNG result (with alpha) to clipboard; confirm toast; works cross-platform.

**Current state:**

- [x] Copy to Clipboard button
- [x] Copies PNG with alpha channel preserved
- [x] Status bar confirmation ("Copied to clipboard")
- [x] Cross-platform via QApplication.clipboard
- [x] Keyboard shortcut (Cmd/Ctrl+C)

**Decision:** ✓ **COMPLETE - NO ACTION NEEDED**

**Code files:** `desktop_app/views/main_window.py` (on_copy)

---

## 6. Keyboard Shortcuts [x] COMPLETE

**Your requirement:** Ctrl/Cmd+O (open), Ctrl/Cmd+S (export), Delete (clear), Esc (cancel). Acceptance: documented and functional on macOS/Win/Linux.

**Current state:**

- [x] Cmd/Ctrl+O (open)
- [x] Cmd/Ctrl+E (export) - using E instead of S
- [x] Cmd/Ctrl+C (copy)
- [x] Cmd/Ctrl+0 (100%), Cmd/Ctrl+1 (fit)
- [x] Standard zoom in/out shortcuts
- [x] Cmd/Ctrl+] and [ (rotate)
- [x] Delete (clear) - implemented (Delete + Ctrl/Cmd+D)
- [x] Esc (cancel) - implemented
- [x] Documented in user-facing docs

**Decision:** ✓ **COMPLETE - NO ADDITIONS NEEDED**

- Core shortcuts work
- **Decision logged:** Clear + Esc shortcuts are now implemented and documented in Help.

**Code files:** `desktop_app/views/main_window.py` (**init** shortcuts section)

---

## 7. Backend Cleanup [ ] PENDING (MUST DO)

**Your requirement:** Remove commented/duplicated blocks; single CORS/StaticFiles mount; uploads path consistent; 4xx/5xx errors human-readable.

**Current state:**

- [~] Some commented code remains
- [~] CORS/StaticFiles need review
- [~] Uploads path needs verification
- [ ] Error messages not audited for user-friendliness
- [~] Port 8001 mostly consistent but needs verification

**Decision:** **DO NOW**

- Critical for professional release
- **Action needed:**
  1. Audit backend/app/\*.py for commented/duplicate code
  2. Verify single CORS config
  3. Verify uploads path consistency
  4. Review all error responses for clarity
  5. Confirm port 8001 everywhere (docs, tests, client)

**Code files:** `backend/app/main.py`, `backend/app/routers/*.py`, `backend/app/config.py`

---

## 8. Landing + Checkout Page [ ] PENDING (MUST DO)

**Your requirement:** Use COPY_DECK; annotated screenshots/GIF; pricing $29 (or ladder test); Buy button → checkout → post-purchase email with key.

**Current state:**

- [ ] Landing page created
- [ ] COPY_DECK used for messaging
- [ ] Screenshots/GIF created
- [ ] Pricing decided
- [ ] Checkout flow tested end-to-end

**Decision:** **DO NOW**

- Critical for launch
- **Action needed:**
  1. Find/reference COPY_DECK (or create messaging)
  2. Take annotated screenshots of workflow
  3. Create demo GIF (open → select → preview → export)
  4. Create simple static landing page
  5. Link to Gumroad checkout
  6. Test full purchase flow

**Files to create:** Landing page HTML/markdown, assets (screenshots, GIF)

---

## 9. Docs & Config [~] IN PROGRESS

**Your requirement:** .env.example (JWT_SECRET, DATABASE_URL sqlite); Quick Start; Export Options; Pricing; known issues; all ports unified to 8001.

**Current state:**

- [x] .env concept exists
- [~] JWT_SECRET documented (in config.py comments)
- [~] DATABASE_URL sqlite pattern present
- [~] Basic README exists
- [x] .env.example file
- [ ] Quick Start section
- [ ] Export Options docs
- [ ] Pricing page/FAQ
- [ ] Known issues list
- [~] Port 8001 mostly used (needs verification)

**Decision:** **DO NOW**

- **Action needed:**
  1. Expand Quick Start, Troubleshooting, and known-issues docs
  2. Add Quick Start to README
  3. Document Export Options (dialog features)
  4. Create Pricing/FAQ doc
  5. List known issues/limitations
  6. Verify port 8001 everywhere

**Files:** `.env.example`, `README.md`, `docs/PRICING.md`, `docs/FAQ.md`, `docs/KNOWN_ISSUES.md`

---

## 10. QA Matrix [ ] PENDING (MUST DO)

**Your requirement:** Cases: large images, EXIF rotations, tiny selections, bad inputs (415/404), offline mode; pass list with evidence before go-live.

**Current state:**

- [ ] Large images test (>10MB, >4000px)
- [ ] EXIF rotations test (all orientations)
- [ ] Tiny selections test (<10px)
- [ ] Bad inputs test (415/404/422)
- [ ] Offline mode test (no backend)
- [ ] Pass list documented

**Decision:** **DO NOW - BEFORE LAUNCH**

- No formal QA has been run
- **Action needed:**
  1. Create test case checklist
  2. Run each case systematically
  3. Document results (pass/fail with evidence)
  4. Fix any critical bugs found
  5. Accept known limitations for v1

**Files to create:** `docs/QA_CHECKLIST.md`, `docs/QA_RESULTS.md`

---

## Summary by Priority

### DONE (4 items) ✓

1. Rotate 90° CW/CCW
2. Clipboard Copy
3. Keyboard Shortcuts
4. Evaluation Gate (hard/locked behavior + status CTA)

### IN PROGRESS (2 items) 🟡

1. Checkout + License - payment + hosted product + purchase plumbing
2. Docs & Config - partially done

### MUST DO NOW (4 items) 🔴

1. Checkout + License (Gumroad setup)
2. Desktop Packaging (PyInstaller)
3. Backend Cleanup
4. Landing + Checkout Page
5. QA Matrix

### SKIP FOR v1 (from "Next Phase") ⚪

- Advanced Processing (Otsu/Adaptive)
- Auto-Detection
- Browser Extension
- Auto-updater
- Telemetry
- Integrations
- A/B Experiments

---

## Recommended Action Plan

### Week 1: Critical Path

1. **Decision:** Hard vs soft evaluation gate (1 hour)
2. **Gumroad setup:** Account + product + test checkout (4 hours)
3. **Backend cleanup:** Remove cruft, verify consistency (4 hours)
4. **PyInstaller:** macOS build + test (8 hours)

### Week 2: Polish & Launch

1. **Landing page:** Simple static with GIF (4 hours)
2. **Docs:** .env.example, Quick Start, FAQ (4 hours)
3. **QA Matrix:** Run all tests, document (8 hours)
4. **Final fixes:** Address QA findings (8 hours)

### Week 3: Post-Launch

1. Monitor early adopter feedback
2. Fix critical bugs
3. Plan v2 features based on usage

---

## Notes

- **Database:** Currently optional; JWT_SECRET is required for backend auth (not strictly needed if you remove auth routes)
- **Port 8001:** Desktop client expects this; backend usually runs on 8001
- **Unsigned builds:** Acceptable for early adopters with clear Gatekeeper bypass instructions
- **Hard gate vs soft gate:** Your spec says hard (disable export); we built soft (optional license). Decide which to ship.
