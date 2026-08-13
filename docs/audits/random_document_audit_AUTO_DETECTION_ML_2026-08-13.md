# Random Document Audit Report

**Audit date:** 2026-08-13
**Chosen document:** `docs/AUTO_DETECTION_ML.md`
**Selection method:** Real RNG (`random.SystemRandom`) over 1799 candidate documents (index 314).
**Governing doctrine:** `motto_v5.md` (master/main agent first, parallel subagents, evidence tiers, git/local-work safety, "Anything else?" prompt, durable documentation).
**Main agent:** Forge. Verification performed by 5 scoped parallel subagents (codebase verifier, test/runtime verifier, security/privacy reviewer, product/UX reviewer, skeptic/rebuttal) + direct main-agent verification of high-value claims.

---

## 1. Document Inventory

Candidate documents were collected across the repo (markdown + selected `.txt`), excluding generated artifacts (`dist`, `build`, `node_modules`, `__pycache__`, `.venv`, `.git`, `deploy_dist`, etc.).

| Top-level location | Candidate docs | Notes |
|---|---|---|
| `docs/` | 1627 | Design, analysis, audits, marketing, data manifests, archive/parallel |
| `.kiro/` | 85 | Spec/steering artifacts |
| `marketing/` | 36 | Product/marketing copy |
| `web/` | 29 | Web surface docs |
| `scripts/` | 4 | Tooling scripts/docs |
| `legal/` | 4 | Legal/marketing-claims docs |
| `experiments/` | 2 | Research notes |
| `assets/` | 2 | Resource docs |
| root | 9 | `PRODUCT.md`, `DESIGN.md`, `motto_v5.md`, `robots.txt`, `requirements*.txt`, `tools/`, `desktop_app/`, `.github/`, `.agent/` |
| **TOTAL** | **1799** | Random pick over all of these |

Representative notable docs (not exhaustive): `PRODUCT.md`, `DESIGN.md`, `docs/FULL_PRODUCT_AUDIT_MARCH_2026.md`, `docs/PRE_LAUNCH_AUDIT.md`, `docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`, `docs/test_data_audit_addendum_2026-08-13.md`, `docs/analysis/2026-08-02_app_feature_and_build_readiness.md` (already analyzed the exact `extractor.py` + golden-fixture surface — see Step 13).

---

## 2. Random Selection

- **Chosen document:** `docs/AUTO_DETECTION_ML.md`
- **Selection method:** Genuine pseudo-random pick using `random.SystemRandom().randrange(1799)` → index 314, over the full filtered candidate list (saved to `/tmp/audit_candidate_docs.json`). Not convenience-selected.
- **Why it matters:** It is a forward-looking strategy doc for the product's core capability (automatic signature detection). It mixes shipped reality, aspirational ML plans, privacy claims, and a build timeline — exactly the kind of doc that drifts from code and misleads future work.

---

## 3. Chosen Document Deep Analysis

`docs/AUTO_DETECTION_ML.md` (493 lines) describes: current manual-selection approach; goal of automatic detection; Approach 1 (traditional CV: contour detection, OCR + negative space); Approach 2 (ML: YOLO/Faster R-CNN, segmentation); Approach 3 (foundation/cloud: ViT/DINO, Google Document AI); a "Recommended Approach (Solo Dev)" with Phases 1–4; model hosting options; training infrastructure; a "Realistic Timeline" with several `[x]` done items; recommended tech stack; and a closing "Next Steps" that offers to implement Phase 1.

### Doc Item Table (extract)

| ID | Type | Short quote / evidence | Location | Interpretation | Conf. |
|---|---|---|---|---|---|
| D1 | Stale/Current-State Claim | "Current Approach (Manual Selection) / Users manually draw rectangle" | L5 | States app is manual-only today | Med |
| D2 | Explicit Task | "Add 'Auto-Detect' button to UI" | L310 | Phase 1 action | High |
| D3 | Explicit Task | "Use contour-based detection (OpenCV only, no new deps)" | L311 | Phase 1 action | High |
| D4 | Implicit Task | "Show all candidates, let user pick correct one" | L312-313 | UX design requirement | High |
| D5 | Intended-State Claim | "Good enough for 60-70% of simple documents" | L313 | Accuracy claim, unmeasured | Low |
| D6 | Current-State Claim | "OpenCV (already have)" | L459 | Dependency claim | High |
| D7 | Intended-State Claim | Phase 2: "log anonymized data" of user selections | L328-339 | Training-data collection plan | Med |
| D8 | Privacy Claim | Phase 2: "Ask permission, anonymize, or store locally only" | L339 | Privacy guardrail claim | Med |
| D9 | Deployment Mode Claim | Cloud APIs "Conflicts with 'privacy-first' positioning" | L298 | Privacy positioning claim | Med |
| D10 | Contradiction | Timeline marks `[x]` "Implement contour detection / Add Auto-Detect button / Ship to early users" | L427-430 | Claims Phase 1 done | High |
| D11 | Contradiction | "Want me to implement Phase 1 (contour detection) now?" | L483 | Implies Phase 1 NOT done | High |
| D12 | Intended-State Claim | YOLOv8 training, `~/.signature_extractor/models/`, 50MB model download | L180-199, L350, L378 | ML plan (future) | Med |
| D13 | Implicit Task | "Falls back to traditional CV if model not installed" | L350 | Fallback requirement | Med |
| D14 | Stale/Current-State Claim | Approach 1.1 snippet returns only largest candidate via `max(...)` | L76-78 | Matches snippet, conflicts with D4 prose | High |
| D15 | Performance Claim | YOLO "50-100ms on GPU, 500ms on CPU" | L152 | Unverifiable (no model) | Low |

---

## 4. Extracted Task Candidates

| Task ID | Source Doc Items | Task | Explicit/Implicit | Why | Expected area | Priority guess |
|---|---|---|---|---|---|---|
| T1 | D2, D3, D10 | Implement contour auto-detect + Auto-Detect button | Explicit | Doc timeline says done | desktop_app | P? verify |
| T2 | D4, D14 | Surface multiple candidates, let user pick | Implicit | Doc design vs code | desktop_app UI | P? verify |
| T3 | D5 | Validate 60-70% accuracy claim | Implicit | Claim unmeasured | tests/data | P? verify |
| T4 | D6 | Confirm OpenCV dependency present | Explicit | Claim to verify | deps | P? verify |
| T5 | D7, D8 | Build Phase 2 anonymized selection logging | Implicit | Plan, unimplemented | backend | P? verify |
| T6 | D9 | Enforce privacy-first (no cloud egress) | Implicit | Positioning vs code | backend/desktop | P? verify |
| T7 | D12, D13 | Train/load YOLO model + fallback | Implicit | ML plan | ML pipeline | P? verify |
| T8 | D10, D11 | Reconcile doc self-contradiction (done vs "implement now") | Explicit | Contradiction | docs | P1 |
| T9 | D1 | Correct "manual only" stale claim | Implicit | Stale | docs | P2 |
| T10 | D14 vs D4 | Align snippet (largest-only) with multi-candidate design | Implicit | Contradiction | docs | P2 |

---

## 5. Static Codebase Reality Check

Verification of each task candidate (main agent + subagents; reconciled and directly verified for high-value items).

| Task | Codebase Status | Evidence | What exists today | Gap | Work needed |
|---|---|---|---|---|---|
| T1 | Already Done | `desktop_app/processing/extractor.py:510` (`auto_detect_signature`), `desktop_app/views/main_window_parts/extraction.py:941` (`ElidingButton("Auto Detect")`, objName `autoDetectSelectionButton`), wired `:1387`, `:4261`, `:2070` | Contour/threshold/color auto-detect + button shipped | None for Phase 1 core | Docs only |
| T2 | Partial / Dead-end | `extractor.py:470` `auto_detect_signatures` returns `SignatureCandidate` list (tested), but UI only calls singular `auto_detect_signature` and auto-applies one box (`extraction.py:4261-4279`) | Multi-candidate API exists, never surfaced | No candidate-picker UI | Build UI + wire API |
| T3 | Unknown / Unverified | `extractor.py:526-538` comment: params "selected on the external corpus development split only; ... not tuned against a labeled signature dataset"; no labeled dataset in repo | Accuracy unmeasured | No eval harness | Build eval (recall@k/IoU) |
| T4 | Already Done | `desktop_app/requirements.txt:29` `opencv-python==4.12.0.88`; also in `requirements.venv.snapshot.txt:29`; used in `extractor.py:70`, `backend/app/services/extraction.py:10`, etc. | OpenCV real dep | None | Docs only |
| T5 | Missing | No `anonym`/`feedback`/`correction`/`opt-in` code; selection persisted per-owner (`backend/app/routers/extraction.py:257,277`) | Phase 2 unimplemented | Full dataset-collection pipeline absent | Future (needs decision) |
| T6 | Already Done (consistent) | No cloud egress of user data; only `cdn.signkit.work/updates.json` (version check, no user data) `main_window.py:921`; localhost health probe `backend_manager.py:347` | Privacy-first holds in code | None | Docs only |
| T7 | Missing | No `ultralytics`/`torch`/`onnxruntime`/`google.cloud.documentai` imports or deps; no `.pt`/`.onnx` weights; no `~/.signature_extractor/models/`; only `tools/import_ultralytics_signature_corpus.py` (corpus conversion, no model) | ML plan is future-only | Full ML pipeline | Future (decision needed) |
| T8 | Contradictory Evidence | Code proves Phase 1 shipped (T1). Doc L483 still asks to implement it | Doc stale/self-contradictory | Doc must be reconciled | Update doc |
| T9 | Stale Doc | D1 "Current Approach (Manual Selection)" contradicted by shipped auto-detect | Doc stale re: Phase 1 | Doc update | Update doc |
| T10 | Stale Doc | Approach 1.1 snippet (naive `findContours` + largest) superseded by `extractor.py:510-630` (blue-ink color path → Otsu envelope → adaptive+contour fallback) | Doc snippet outdated | Doc update | Update doc |

---

## 6. Dynamic Verification and Test Baseline

- **Environment:** Project `.venv` (Python 3.13.12) has `cv2 4.12.0`, `pytest 8.4.2`, `numpy 2.2.6`. Runnable.
- **Default suite baseline:** `.venv/bin/python -m pytest -q` → **181 passed in 7.06s** (clean). All green = pre-existing pass; no new code changed, so no regressions attributable.
- **Targeted auto-detect tests (run directly, outside default collection):** `desktop_app/tests/test_extractor.py` + `test_signature_edge_cases.py` → **21 passed in 0.31s**. They pass when invoked but are **not collected by default** (see ISSUE-007).
- **Test sensitivity (per motto §0.5.1):** Existing auto-detect tests are **S1** (pass). No S2/S3 mutation proof was performed in this audit; "auto-detect works" is therefore S1 evidence, not enforcement-proven. The green suite is not, by itself, proof the behavior is enforced.
- **Full-suite gap:** Default `pytest` collects only `tests/` (181). `desktop_app/tests/` and `backend/tests/` are excluded.

---

## 7. Critical Implementation and Test Traps Checked

- **4A Env-var/config loading:** `backend/app/config.py:106-107` builds `settings = Settings()` at import time (pydantic `BaseSettings` reads `.env`/env then freezes). Tests that set `os.environ` post-import cannot change `DATABASE_URL`/secrets; they work around it by setting env before import (`tests/test_auth_hardening.py:11-14`). **ModuleCacheIssue candidate** — fragile but works by design.
- **4B Test isolation/state leakage:** `tests/conftest.py` provides function-scoped `qapp` (offscreen `QApplication`) and an autouse `_disable_onboarding` fixture — clean. No shared mutable module state found in the auto-detect path.
- **4C Full suite not optional:** Default suite green (181), but it omits 21+ auto-detect tests in `desktop_app/tests/`. A regression there would be invisible to `pytest` from root.
- **4D Proof-of-concept:** No probes made (audit-only). No durable changes. See Step 11.

---

## 8. Data, Privacy, and PII Boundary Checks

The doc (Phase 2) proposes logging user signature selections to build a training set, with a privacy claim ("ask permission, anonymize, store locally"). Verification:

- **Write paths for user data:** Uploads → `backend/app/paths.py:31` `USER_DATA_DIR/uploads/images` (macOS `~/Library/Application Support/SignKit/uploads/images`); sidecar `uploads/images/regions/{asset.id}.json` with bbox + image characteristics (`extraction.py:59,277`); DB column `selection_json` (`extraction.py:257`). All created at import with default umask, **no `chmod` hardening** (`extraction.py:58,60`) → potentially world-readable on multi-user systems.
- **Fixture vs production boundary:** Selection metadata is bound to the **authenticated owner's document**, not anonymized into a shared corpus. **No fixture/synthetic marker gating.** Phase 2's "anonymize" has **zero enforcing code** → DataBoundaryRisk.
- **PII propagation:** Local SQLite `signature_extractor.db` (repo root, 139 KB, **untracked** — not a committed secret) stores uploaded signatures + selection metadata **unencrypted**. `.env` is **not tracked** (good).
- **Deployment modes:** No dogfood/beta/production privacy-mode gating exists for any data collection. Doc's "privacy-first" is consistent with *current* code (no cloud egress) but there is no mechanism to safely enable Phase 2 collection later.
- **Heuristic limits (§5D):** N/A to a detector that uses no PII regex; accuracy heuristics are unvalidated (T3).
- **Kill switch / rollback (§5J):** No enforcement mechanism exists for Phase 2, so no kill switch is needed *yet*; but any future collection must ship with one (see ISSUE-012).

---

## 9. Deduped Issue / Task Register

### ISSUE-001: AUTO_DETECTION_ML.md is self-contradictory about Phase 1 ship state
- **Category:** docs / contradiction
- **Origin:** Explicit + Contradiction. Source: `docs/AUTO_DETECTION_ML.md:427-430` vs `:483`. Related: D10, D11.
- **Codebase Evidence:** `extractor.py:510`, `extraction.py:941,1387,4261` prove contour auto-detect + button shipped.
- **Static:** Confirmed done in code.
- **Dynamic:** Default suite 181 passed; auto-detect tests 21 passed (direct).
- **Current behavior:** Doc says done AND asks to implement — ambiguous to readers.
- **Expected / decision:** Reconcile doc: mark Phase 1 done, remove "implement now" CTA.
- **Gap:** Misleads future agents into re-proposing done work (violates motto re-proposal rule).
- **Impact:** Wasted work, wrong prioritization.
- **Risk:** Medium (decision-quality).
- **Confidence:** High.
- **Acceptance:** [ ] Doc states Phase 1 shipped with file:line proof. [ ] Closing CTA removed/reframed as "enhancements."
- **Test plan:** Manual doc review + link to tests.
- **Rollback:** N/A (docs).

### ISSUE-002: "Current Approach (Manual Selection)" claim is stale
- **Category:** docs / stale
- **Origin:** Implicit. Source: `docs/AUTO_DETECTION_ML.md:5`. Related: D1.
- **Evidence:** `extraction.py:941` Auto-Detect button + `extractor.py:510` auto path.
- **Current:** App is manual + auto today.
- **Expected:** Doc reflects both modes.
- **Confidence:** High. **Acceptance:** [ ] Doc updated. **Tests:** manual.

### ISSUE-003: Approach 1.1 code snippet superseded by evolved implementation
- **Category:** docs / stale
- **Origin:** Implicit. Source: `docs/AUTO_DETECTION_ML.md:45-79`.
- **Evidence:** `extractor.py:510-630` (blue-ink color detection → Otsu envelope → adaptive+contour fallback). Doc snippet is naive contour-only.
- **Current:** Implementation more sophisticated than doc.
- **Expected:** Doc snippet aligned or replaced with a pointer to `extractor.py`.
- **Confidence:** High. **Acceptance:** [ ] Snippet updated or linked. **Tests:** manual.

### ISSUE-004: Doc's "show all candidates, let user pick" UX not implemented
- **Category:** product-decision / UX
- **Origin:** Implicit + Contradiction. Source: `docs/AUTO_DETECTION_ML.md:312-313` vs `:76-78`.
- **Evidence:** `extractor.py:470` `auto_detect_signatures` returns ranked `SignatureCandidate` list; UI only calls singular `auto_detect_signature` and auto-applies (`extraction.py:4261-4279`). No candidate-picker UI.
- **Current:** Single auto-applied bbox.
- **Expected:** Either implement candidate picker (per doc design) or update doc to state single-best is intentional.
- **Confidence:** High. **Acceptance:** [ ] Decision recorded; doc or UI reconciled. **Tests:** UI test for picker if built.

### ISSUE-005: Multi-candidate API is dead code in product (no UI consumer)
- **Category:** refactor / UX
- **Origin:** Implicit. Source: extracted from `extractor.py:470`.
- **Evidence:** `auto_detect_signatures` defined and unit-tested (`test_color_signature_candidate.py`) but no UI caller; singular path used everywhere.
- **Current:** API unused by product surface.
- **Expected:** Surface it (ISSUE-004) or document as internal/test-only.
- **Confidence:** High. **Acceptance:** [ ] Either wired to UI or marked internal. **Tests:** existing unit tests.

### ISSUE-006: Detection accuracy claim ("60-70%") is unverified
- **Category:** tests / product-decision
- **Origin:** Implicit. Source: `docs/AUTO_DETECTION_ML.md:313`.
- **Evidence:** `extractor.py:526-538` — params "selected on the external corpus development split only; ... not tuned against a labeled signature dataset." No labeled dataset or eval harness in repo.
- **Current:** No measured accuracy.
- **Expected:** Either produce an eval (recall@k / IoU on a labeled set) or soften the claim to "heuristic, unvalidated."
- **Confidence:** High (that it's unverified). **Acceptance:** [ ] Eval harness or doc caveat. **Tests:** new eval test.

### ISSUE-007: Default `pytest` excludes `desktop_app/tests/` and `backend/` (coverage gap)
- **Category:** tests / tooling
- **Origin:** Implicit (trap 4C). Source: `pytest.ini:2` `testpaths = tests`.
- **Evidence:** Default collection = 181 (root `tests/` only). `desktop_app/tests/test_extractor.py` + `test_signature_edge_cases.py` = 21 auto-detect tests pass when invoked directly but are **not** collected by default `pytest`. `backend/tests/` likewise excluded.
- **Current:** 21 passing auto-detect tests silently skipped by CI/default runs.
- **Expected:** Default `pytest` discovers all suites (extend `testpaths` or add a root `conftest`/tox config).
- **Impact:** Regressions in auto-detect could pass unnoticed.
- **Risk:** Medium (coverage).
- **Confidence:** High (dynamic proof).
- **Acceptance:** [ ] `pytest` from root collects desktop_app + backend tests. [ ] Green.
- **Test plan:** Run `pytest` (root) + `pytest desktop_app/tests backend/tests`; both green.
- **Rollback:** Config only; revert `pytest.ini` if needed.

### ISSUE-008: No positive accuracy regression test (golden fixture is a no-detection placeholder)
- **Category:** tests
- **Origin:** Implicit. Source: `desktop_app/tests/fixtures/auto_detect_golden.json:4` `expected_bbox:[0,0,0,0]`, `tolerance_px:0`.
- **Evidence:** Consuming test (`test_extractor.py:72-85`) uses `max(expected, fallback_width)` softening — a smoke test, not a precise bbox assertion. `docs/test_data_manifest.md:26` wrongly calls it a "versioned exact bounding-box golden" — contradicted.
- **Current:** Only negative/soft tests; no IoU/recall check.
- **Expected:** Add a precise positive accuracy test on a labeled signature image (and fix the manifest's false description).
- **Confidence:** High. **Acceptance:** [ ] Positive bbox test with tolerance; manifest corrected. **Tests:** new.

### ISSUE-009: Hardcoded default DB credentials in backend config
- **Category:** security
- **Origin:** Implicit (trap 4A/§8). Source: `backend/app/config.py:27,29`.
- **Evidence:** `DATABASE_PASSWORD="pranay"`, `DATABASE_USERNAME="pranay"`. Validation only rejects the literal `"your_db_password"`, so `"pranay"` passes.
- **Current:** Weak default ships; relevant when Postgres path used (SQLite fallback is local default via `backend_manager.py:128-161`).
- **Expected:** Remove hardcoded creds; require from env/secret; fail closed if missing in production mode.
- **Confidence:** High. **Acceptance:** [ ] No default creds; test fails on missingsecret in prod. **Tests:** config test.
- **Rollback:** env-var based; revert config if needed.

### ISSUE-010: Import-time `Settings()` singleton (ModuleCacheIssue)
- **Category:** architecture / test-isolation
- **Origin:** Implicit. Source: `backend/app/config.py:106-107`.
- **Evidence:** `settings = Settings()` at import; post-import `os.environ` changes ignored. Tests work around by setting env before import.
- **Current:** Works, fragile.
- **Expected:** Document the constraint; provide a reset/test seam, or read env at call time for the few values tests mutate.
- **Confidence:** Medium. **Acceptance:** [ ] Constraint documented; test seam if needed.

### ISSUE-011: Phase 2 selection-logging plan has no enforcing code (DataBoundaryRisk)
- **Category:** privacy / data-boundary
- **Origin:** Implicit. Source: `docs/AUTO_DETECTION_ML.md:328-339` (D7, D8).
- **Evidence:** No opt-in/consent/anonymization; selection persisted per-owner (`extraction.py:257,277`). No shared corpus writer.
- **Current:** Phase 2 unimplemented; privacy claim aspirational.
- **Expected (future):** If built, must include explicit consent, anonymization, fixture/synthetic markers, and a kill switch. Not worth building now.
- **Confidence:** High. **Acceptance:** N/A until decision. **Recommendation:** Defer; document guardrails required before any build.

### ISSUE-012: Upload/sidecar files created without permission hardening (potential world-readable PII)
- **Category:** privacy / security
- **Origin:** Implicit. Source: `backend/app/routers/extraction.py:58,60`; `paths.py:31`.
- **Evidence:** Dirs created with default umask, no `chmod`; SQLite `signature_extractor.db` unencrypted at repo root (untracked).
- **Current:** Local PII on disk, no hardening.
- **Expected:** Restrict permissions (0700 per-user dirs); document retention/delete.
- **Confidence:** Medium. **Acceptance:** [ ] Dir perms set; test asserts. **Tests:** new.

### ISSUE-013: ML/cloud plan (Approaches 2 & 3) is future-only; doc presents it as imminent
- **Category:** docs / product-decision
- **Origin:** Implicit. Source: `docs/AUTO_DETECTION_ML.md:137-301, 343-363`.
- **Evidence:** No `ultralytics`/`torch`/`onnxruntime`/`google.cloud.documentai` in deps or source; no weights; only corpus-conversion tool `tools/import_ultralytics_signature_corpus.py`.
- **Current:** Accurate as "future plan," but framed without priority/decision gates.
- **Expected:** Reframe as explicit future/decision-needed; add go/no-go criteria (dataset size, accuracy bar, privacy review).
- **Confidence:** High. **Acceptance:** [ ] Doc reframed; decision gates added.

### ISSUE-014: No privacy/deployment mode gating for future data collection
- **Category:** operational-safety / privacy
- **Origin:** Implicit. Source: doc "privacy-first" positioning (D9) + absence of mode system.
- **Evidence:** No dogfood/beta/production mode mechanism in repo for data collection.
- **Current:** Fine today (no collection); risky if Phase 2 built without gates.
- **Expected:** Define mode gates before any collection (see ISSUE-011).
- **Confidence:** Medium. **Acceptance:** N/A until decision.

### ISSUE-015: Dependency declaration split (no canonical root requirements)
- **Category:** tooling / docs
- **Origin:** Implicit. Source: `desktop_app/requirements.txt:29` + `requirements.venv.snapshot.txt:29` (opencv present in both).
- **Evidence:** No root `requirements.txt`; backend vs desktop deps split. OpenCV IS correctly declared (correcting a subagent's erroneous "not in snapshot" claim — direct verification confirmed line 29).
- **Current:** Reproducible via snapshot, but no single source of truth.
- **Expected:** Document the split; consider a canonical pinned requirements per component.
- **Confidence:** High. **Acceptance:** [ ] Doc note or single manifest.

---

## 10. Prioritization

Scoring: Severity (5=breach/unusable … 1=polish), Blast (5=most users … 1=rare), Effort (5=large … 1=trivial), Confidence (5=proven … 1=speculative).

| ID | Title | Sev | Blast | Effort | Conf | Priority | Why |
|---|---|---|---|---|---|---|---|
| ISSUE-001 | Doc self-contradiction on Phase 1 | 2 | 3 | 1 | 5 | **P1** | Misleads planning; cheap to fix; high confidence |
| ISSUE-007 | `pytest` excludes desktop_app/backend tests | 3 | 4 | 1 | 5 | **P1** | 21 auto-detect tests silently skipped; CI blind spot |
| ISSUE-002 | Stale "manual only" claim | 2 | 2 | 1 | 5 | P2 | Doc accuracy |
| ISSUE-003 | Outdated Approach 1.1 snippet | 2 | 2 | 1 | 5 | P2 | Doc accuracy |
| ISSUE-004 | Candidate-picker UX not built | 3 | 3 | 3 | 5 | P2 | Real product gap vs doc design |
| ISSUE-005 | Multi-candidate API dead in UI | 2 | 2 | 2 | 5 | P2 | Refactor/clarify |
| ISSUE-006 | "60-70%" accuracy unverified | 3 | 3 | 3 | 5 | P2 | Decision needs data |
| ISSUE-008 | No positive accuracy test | 3 | 3 | 2 | 5 | P2 | Test gap |
| ISSUE-009 | Hardcoded DB creds | 4 | 3 | 2 | 5 | **P1** | Security default; fix before any prod Postgres |
| ISSUE-010 | Import-time Settings singleton | 2 | 2 | 2 | 3 | P3 | Fragile; document |
| ISSUE-011 | Phase 2 logging unimplemented/unguarded | 3 | 2 | 4 | 5 | P3* | Defer; guardrails required if built |
| ISSUE-012 | Unhardened upload/sidecar perms | 3 | 2 | 2 | 3 | P3 | Local PII exposure |
| ISSUE-013 | ML/cloud plan framed as imminent | 2 | 2 | 1 | 5 | P2 | Doc reframe |
| ISSUE-014 | No mode gating for future collection | 2 | 1 | 3 | 3 | P3 | Future-facing |
| ISSUE-015 | Split dependency declaration | 1 | 2 | 1 | 5 | P3 | Hygiene |

### Priority Queues

**P0:** None (no active breach/unusable workflow found).

**P1:**
- ISSUE-001 (reconcile doc self-contradiction)
- ISSUE-007 (fix test discovery to include `desktop_app/tests` + `backend/`)
- ISSUE-009 (remove hardcoded DB credentials)

**P2:**
- ISSUE-002, ISSUE-003 (stale doc claims)
- ISSUE-004, ISSUE-005 (candidate-picker UX gap)
- ISSUE-006, ISSUE-008 (accuracy validation gap)
- ISSUE-013 (reframe ML plan)

**P3 / later:**
- ISSUE-010 (config singleton), ISSUE-012 (file perms), ISSUE-014 (mode gating), ISSUE-015 (dep hygiene)

**Quick Wins:**
- ISSUE-001, ISSUE-002, ISSUE-003, ISSUE-015 (all doc-only, low effort, high clarity).
- ISSUE-007 config fix (one-line `testpaths` change + verification).

**Risky Changes:**
- ISSUE-009 (config default change — must not break local SQLite fallback / CI).
- ISSUE-004 (new UI surface — design decision needed).

**Needs Discussion Before Work:**
- ISSUE-004 / ISSUE-005: build candidate picker, or declare single-best intentional?
- ISSUE-006 / ISSUE-008: what accuracy bar justifies "auto-detect" as default vs manual-only?
- ISSUE-011 / ISSUE-013 / ISSUE-014: is ML training / cloud a direction at all? What are go/no-go gates?

**Not Worth Doing (yet):**
- Building Phase 2 data collection (ISSUE-011) or any ML training pipeline (ISSUE-013) now — no dataset, no validated need, no privacy guardrails. Document the gates; do not start.

---

## 11. Proof-of-Concept Validation

**No proof-of-concept probe was needed.** This was an audit-only engagement; no working files were modified. Static evidence (file:line) plus existing dynamic evidence (default suite 181 passed; direct run of 21 excluded auto-detect tests passed) were sufficient to reach conclusions. No probe cleanup required.

---

## 12. Assumptions Challenged by Implementation

| Assumption | Why it seemed true | What disproved it | Evidence | How recommendation changed |
|---|---|---|---|---|
| Subagent claim: "opencv not in requirements snapshot" | Skeptic subagent reported snapshot lacked opencv | Direct read of `requirements.venv.snapshot.txt:29` shows `opencv-python==4.12.0.88` | `requirements.venv.snapshot.txt:29` | Corrected ISSUE-015; doc "already have" claim confirmed accurate |
| "Tests passing = auto-detect covered" | 181 tests green | Default `pytest` only collects root `tests/`; 21 auto-detect tests live in uncollected `desktop_app/tests/` | `pytest.ini:2`; direct run 21 passed | Added ISSUE-007 (real coverage gap) |
| "Doc is a pure future plan" | ML sections look aspirational | Phase 1 (contour + button) is actually shipped; doc contradicts itself | `extractor.py:510`, `extraction.py:941` | Reframed: stale re traditional CV, accurate re ML |
| "Auto-detect returns candidates for user pick" (per doc prose) | Doc L312-313 | UI auto-applies single bbox; candidate API unused in UI | `extraction.py:4261-4279`, `extractor.py:470` | ISSUE-004/005 (UX dead-end) |

---

## 13. Parallel Agent / Multi-Model Findings

Five scoped subagents were dispatched (codebase verifier, test/runtime verifier, security/privacy reviewer, product/UX reviewer, skeptic/rebuttal). Findings were reconciled into the single register above. Key reconciliations:

- **Subagent agreement (high confidence):** Phase 1 auto-detect + button shipped; ML (YOLO/ultralytics/torch/documentai) not implemented; no cloud egress of user data; OpenCV is a real dependency.
- **Subagent disagreement resolved:** The skeptic claimed opencv was absent from dependency snapshots. Direct main-agent verification (`requirements.venv.snapshot.txt:29`) disproved that — the dependency IS declared. Treated as a verification error, not evidence.
- **Prior related work found:** `docs/analysis/2026-08-02_app_feature_and_build_readiness.md` already analyzed the `extractor.py` + golden-fixture surface, and `docs/test_data_manifest.md` references the golden fixture — yet `AUTO_DETECTION_ML.md` was never reconciled with that analysis. This explains the staleness: the planning doc drifted while implementation advanced.
- **No external model / second-opinion review was required** to reach these conclusions; they are repo-evidence based.

---

## 14. Discussion Pack

### My Recommendation
I recommend working on, in order:
1. **ISSUE-001** — Reconcile `AUTO_DETECTION_ML.md` (remove the "implement Phase 1 now" contradiction; mark Phase 1 shipped).
2. **ISSUE-007** — Fix `pytest.ini` test discovery so `desktop_app/tests/` and `backend/` are collected by default.
3. **ISSUE-009** — Remove hardcoded `pranay` DB credentials from `backend/app/config.py`.

### Why These Matter Now
- The doc actively misleads future agents into re-proposing shipped work (a violation of the re-proposal rule in `motto_v5.md`).
- 21 auto-detect tests pass but are invisible to the default suite — a silent CI blind spot on the product's core feature.
- Hardcoded credentials are a shipped security default that must not reach any production Postgres.

### What Breaks If Ignored
- Repeated wasted planning on "Phase 1."
- Undetected regressions in signature auto-detection.
- Credential exposure if the app is ever pointed at a real database.

### What I Would Not Work On Yet
- Phase 2 data collection (ISSUE-011), ML training (ISSUE-013), cloud APIs — no dataset, no validated need, no privacy guardrails. Document gates; defer.

### What Is Ambiguous
- Whether single-best auto-apply (current) is the intended UX, or the doc's candidate-picker is still desired (ISSUE-004/005).
- What accuracy bar makes auto-detect safe as a default (ISSUE-006/008).

### Questions For You
1. Should auto-detect stay single-best auto-apply, or should we build the candidate-picker the doc describes?
2. Is ML-based detection (YOLO/segmentation) a direction you still want, and what dataset/accuracy bar would trigger it?
3. For any future Phase 2 data collection, do you want consent + anonymization + a kill switch baked in from day one?

### Needs Runtime Verification
- Full `pytest` including `desktop_app/tests` and `backend/` after ISSUE-007 fix (command provided in ISSUE-007).
- Mutation/sensitivity (S2/S3) proof that auto-detect behavior is enforced — not performed here.

### Needs Online Research
- None for the core findings. (External framework behavior not required; repo evidence sufficient.)

### Needs ChatGPT / External Review
- Only if you want a second opinion on the Phase 2 privacy-design decision (see below).

---

## 15. Online Research
None required. All findings are repo-evidence based (static file:line + dynamic test runs).

---

## 16. ChatGPT / External Review Escalation Writeup

*Included because the Phase 2 data-collection privacy design is a genuine second-opinion-worthy decision.*

# Review Request: Phase 2 Training-Data Collection Privacy Design

## Context
Auditing `docs/AUTO_DETECTION_ML.md`. Phase 2 proposes logging anonymized user signature selections (doc type, bbox, image characteristics) to build a training set, claiming "ask permission, anonymize, store locally only."

## What Was Checked
- `backend/app/routers/extraction.py:257,277` — selection persisted per authenticated owner.
- `backend/app/paths.py:31` — upload/sidecar storage; no permission hardening.
- Repo-wide search — no opt-in/consent/anonymization/fixture-marker code.

## What The Document Claims
1. Log user selections to build a dataset.
2. Ask permission, anonymize, store locally.
3. Privacy-first positioning; cloud APIs conflict with it.

## What The Codebase Shows
1. No collection code exists (Phase 2 unimplemented).
2. Selection metadata is stored bound to the owner's document, not anonymized.
3. No privacy/deployment mode gating exists.

## Runtime / Test Evidence
- Default suite 181 passed; no collection path exercised (none exists).

## Current Uncertainty
> Should Phase 2, when built, collect selections with explicit opt-in consent + anonymization + fixture markers + a runtime kill switch, or is local-only storage without consent acceptable for a "privacy-first" product?

## Options
### Option A: Consent + anonymization + kill switch
Pros: aligns with stated privacy-first positioning; safe by default.
Cons: more engineering; friction for users.
Where it breaks: none for privacy; only UX friction.

### Option B: Local-only, no consent
Pros: simplest; "store locally only."
Cons: contradicts "ask permission"; weak if logs ever leave device; regulatory risk.
Where it breaks: privacy positioning, possible compliance.

## Current Recommendation
Option A — bake consent + anonymization + kill switch in before any collection (ISSUE-011/014). Do not build Phase 2 yet.

## Files To Review
- `backend/app/routers/extraction.py` (selection persistence)
- `backend/app/paths.py` (storage roots)
- `docs/AUTO_DETECTION_ML.md` (Phase 2 section)

## Specific Questions
1. Is explicit opt-in required, or is local-only sufficient given the privacy-first claim?
2. What anonymization is adequate for bbox + image-characteristic metadata?

---

## 17. Recommended Next Work Unit

### Unit-1: Reconcile AUTO_DETECTION_ML.md with shipped reality (docs-only, safe, reversible)

**Goal:** Eliminate the self-contradiction and stale claims so future agents stop re-proposing Phase 1.

**Issues covered:** ISSUE-001, ISSUE-002, ISSUE-003, ISSUE-013 (doc reframe).

**Scope:**
- In: `docs/AUTO_DETECTION_ML.md` edits (mark Phase 1 shipped with `extractor.py:510` + `extraction.py:941` proof; remove/reframe L483 "implement now" CTA; correct L5 "manual only"; replace or annotate the L45-79 snippet; reframe Approaches 2–3 as explicit future/decision-needed with go/no-go gates).
- Out: Any code changes, ML work, test changes (those are separate units).

**Likely files touched:** `docs/AUTO_DETECTION_ML.md` only.

**Acceptance criteria:**
- [ ] Doc states Phase 1 (contour + Auto-Detect button) is shipped, with file:line citations.
- [ ] Closing "implement Phase 1 now?" CTA removed or reframed as enhancement backlog.
- [ ] L5 "Current Approach (Manual Selection)" corrected to reflect manual + auto.
- [ ] Approach 1.1 snippet annotated as superseded by `extractor.py:510-630`, or replaced.
- [ ] Approaches 2–3 labeled future/decision-needed with explicit gates.

**Tests to run:**
- Baseline: `.venv/bin/python -m pytest -q` (181 passed expected, unchanged).
- Targeted: none (docs-only).
- Full suite: unchanged.

**Manual verification:** Open doc; confirm no remaining "implement now" / "manual only" contradictions.

**Docs to update:** the chosen doc itself (this unit).

**Operational safety / rollback:** Docs only. If unwanted, revert the single file. No build/test impact.

**Risks:** Minimal (documentation). Main risk is under-stating remaining gaps — keep ISSUE-004/006/007/009 visible in the doc's "Open questions" section.

**Rollback plan:** Revert `docs/AUTO_DETECTION_ML.md` to prior content (no git mutation without approval; provide diff on request).

> Companion quick win (recommend in same session, separate unit): **ISSUE-007** — change `pytest.ini` `testpaths = tests` to include `desktop_app/tests` and `backend/tests` (or add a root `conftest`/tox) and confirm `pytest` from root still passes.

---

## 18. Appendix: Searches Performed

- `Glob **/auto_detect.py`; `Grep auto_detect` (repo + `*.py/*.ui`)
- `Grep import cv2|from cv2` (desktop_app, backend)
- `Grep Auto-Detect|auto detect|auto_detect` (source)
- `Grep ultralytics|import torch|torchvision|onnxruntime|pytesseract|google-cloud-documentai|documentai|roboflow|yolov` (deps + source)
- `Grep signature_extractor/models|load_model|.pt|roboflow|yolov8|download|models/` (source)
- `Grep findContours|YOLO|segmentation|inference|predict|detect_signature|unet|rcnn|mask` (backend + source)
- `Grep requests.|urllib|httpx|socket|analytics|telemetry|track|/api|boto3|google.cloud|aws|azure` (telemetry/egress)
- `Grep os.getenv|os.environ|load_dotenv|lru_cache|settings` (config caching)
- `Grep anonym|feedback|correction|selection|opt-in|consent|dataset` (Phase 2)
- `Grep open(|write|save|.pt|torch|model|tempfile` (persistence)
- `git log --oneline --all -30`; `--grep=detect -i`; `--grep=signature -i`; `git log -S auto_detect_signature`
- `find` for `*.pt *.onnx *.pth *.h5` + `datasets/ annotations/ labels/` (excl. venv)
- `Read pytest.ini`, `conftest.py`, `backend/app/config.py`, `backend/app/paths.py`, `backend/app/routers/extraction.py`, `desktop_app/processing/extractor.py:470-630`, `desktop_app/views/main_window_parts/extraction.py:4255-4290`, `desktop_app/requirements.txt`, `requirements.venv.snapshot.txt`, `desktop_app/tests/fixtures/auto_detect_golden.json`, `tests/test_color_signature_candidate.py`, `tests/test_integration_workflows.py`
- Dynamic: `.venv/bin/python -m pytest -q` (181 passed); `.venv/bin/python -m pytest desktop_app/tests/test_extractor.py desktop_app/tests/test_signature_edge_cases.py` (21 passed); collection checks.

---

### Anything else? (motto §0.1.1)
- The repo already has a mature audit trail (`FULL_PRODUCT_AUDIT_MARCH_2026.md`, `PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`, `test_data_audit_addendum_2026-08-13.md`, `docs/analysis/2026-08-02_app_feature_and_build_readiness.md`). This random-doc audit corroborates those and adds the specific "doc drifted from shipped Phase 1" finding. Consider linking this audit from `PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md` so the stale-doc item is tracked.
- Secondary finding worth a separate look (out of blast radius of this doc): `signature_extractor.db` exists at repo root unencrypted (untracked) — if it ever gets committed or shared, it is local PII-in-repo. Flagged in ISSUE-012; not fixed here.
- No durable implementation was performed. All recommendations are gated on your approval.

## 19. Follow-up verification (2026-08-13)

The audit's ISSUE-009, ISSUE-010, and ISSUE-012 findings were independently
rechecked against the live checkout and promoted into the current execution
backlog. The recovered parallel implementation now removes hardcoded database
credential defaults, fails closed for incomplete production configuration,
provides a narrow settings reload seam, and applies owner-only POSIX modes to
local user-data/upload/selection-sidecar paths. The implementation and focused
tests are recorded in ADR-0150 and `backend/tests/test_config_and_path_security.py`.

The audit remains historical evidence for the original findings. Its older
"not fixed here" and "no durable implementation" statements are superseded by
this addendum; the hosted database, migration, deployment, and multi-user OS
proof gates remain open.
