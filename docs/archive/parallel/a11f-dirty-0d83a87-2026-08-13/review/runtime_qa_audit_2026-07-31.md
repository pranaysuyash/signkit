# SignKit Premium Runtime QA Audit

Date: 2026-07-31
Project: /Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app
Build tested: current working-tree source, PyInstaller arm64 bundle at dist/SignKitPremium.app
Host: Apple Silicon macOS 15.7.7
Evidence ceiling: Tier 4 runtime/manual observation. The requested Computer Use plugin was not exposed as a callable tool in this session, so macOS accessibility UI automation and screenshots were used as fallback. This is not Computer Use plugin evidence.

## Executive result

The newest current-source premium bundle launches and renders the main window, backend status, extraction tab, PDF tab, premium workflow tabs, and Vault. Release readiness is not established. Runtime testing found:

1. Loading the sample signature opens a blocking QGraphicsScene object is not callable error dialog.
2. Auto-detection selects only a narrow first stroke of the sample signature, producing an incomplete export.
3. Opening a PDF reports success but leaves the visible PDF viewer in No PDF loaded state with navigation disabled.

Automated verification also found:

- The license storage path fails because _normalize_tier() returns None for a supplied tier.
- One MainWindow test hangs because it exercises the standard locked-window path while asserting an old URL-opening behavior instead of the current premium-gated behavior.

## Build and launch evidence

The documented builder was attempted first:

    ./build-tools/build_macos.sh premium

It failed because it selected the legacy venv and its Python 3.11 pip installation is broken:

    ModuleNotFoundError: No module named 'pip._internal.operations.build'

The same script incorrectly probes import pillow and import opencv_python, so it reports those packages missing even when the healthy .venv has Pillow and OpenCV installed.

The lower-level builder was then invoked with the healthy .venv and PATH corrected so its internal bare python command resolved to that environment:

    PATH="$PWD/.venv/bin:$PATH" ./.venv/bin/python build-tools/build.py --build-platform darwin --profile mac-premium --spec build-tools/SignatureExtractor_macOS_Premium.spec

Result: build succeeded and produced dist/SignKitPremium.app, an arm64 Mach-O executable with SignKit Premium display name and version 1.0.0. codesign --verify --deep --strict completed successfully.

PyInstaller emitted warnings for missing hidden import desktop_app.views.main_window_parts.library and optional imports mx.DateTime, pysqlite2, and MySQLdb.

The bundle launched with:

    open -na "$PWD/dist/SignKitPremium.app" --args --profile mac-premium

The app process stayed alive, the window rendered, and backend status transitioned from checking to online.

## Runtime findings

### R1. Sample load opens a blocking graphics-scene error

Severity: P1, core extraction workflow blocker.
Evidence: Tier 4 runtime plus Tier 1 source confirmation.

Reproduction:

1. Launch dist/SignKitPremium.app.
2. Select Signature Extraction.
3. Click Try with sample signature.
4. Observe: 'PySide6.QtWidgets.QGraphicsScene' object is not callable.

The source image and selection remain visible behind the dialog, so the failure occurs after image loading begins. Screenshot: assets/runtime-qa-2026-07-31/02-sample-load-error.png.

Likely root cause confirmed by source:

- desktop_app/widgets/image_view.py:20 stores a QGraphicsScene instance as self.scene, shadowing QGraphicsView.scene().
- desktop_app/views/main_window_parts/extraction.py:1911, 3094, and 3337 call self.res_view.scene().clear().

Closure path: choose one canonical scene API, rename the ImageView attribute or update callers, add a real GUI regression test for first load plus reset/rotation/library-load paths, rebuild, and repeat manual testing.

### R2. Auto-detection produces an incomplete sample extraction

Severity: P1, extraction correctness and customer trust risk.
Evidence: Tier 4 runtime plus exported-artifact inspection.

After dismissing R1 and clicking Auto Detect, the green selection covers only the first narrow vertical stroke of the sample signature. The UI reports 78x197 at (54,70) for an 800x400 source. The exported artifact is valid RGBA PNG, 78 x 197, alpha range (0,255), content bounds (10,10,78,187), but it does not represent the visible full sample signature. Screenshot: assets/runtime-qa-2026-07-31/03-auto-detect.png.

This is proven for the built-in sample path. It does not prove every user image fails, but it does prove the first-run demonstration can lead to an incomplete export.

Closure path: define a golden expected bounding box for the sample, assert detector overlap with that region, and add a manual acceptance check with a real signature image.

### R3. PDF open confirmation is disconnected from the visible PDF viewer

Severity: P1, PDF signing workflow blocker.
Evidence: Tier 4 runtime plus Tier 1 source confirmation.

Reproduction:

1. Select PDF Signing.
2. Click Open PDF....
3. Choose assets/demo_document.pdf.
4. Observe PDF opened: demo_document.pdf.
5. Dismiss the dialog.

The tab remains blank, displays No PDF loaded, and navigation is disabled. Screenshot: assets/runtime-qa-2026-07-31/04-pdf-open-success-blank.png.

Source trace:

- desktop_app/views/main_window_parts/pdf.py:360-373 wires visible controls to _on_pdf_tab_open, _on_pdf_tab_close, and _on_pdf_tab_save.
- desktop_app/views/main_window.py:300-303 forwards _on_pdf_tab_open to on_pdf_open.
- desktop_app/views/main_window_parts/pdf.py:631-667 records session state and shows a success dialog but never sets _current_pdf_path or loads the canonical PDFViewer.
- desktop_app/pdf/viewer.py:1346-1357 correctly shows No PDF loaded when its renderer is missing.

Closure path: make the visible PDF tab use one canonical open handler that loads PDFViewer, sets _current_pdf_path, restores placements, updates controls, and only then reports success. Migrate callers, remove the duplicate editable path, and add an end-to-end open assertion for a non-null renderer and Page 1 of ... label.

### R4. PDF sidebar content is clipped

Severity: P2, usability.
Evidence: Tier 4 screenshot.

At the premium default window size, long PDF helper text and some control labels are clipped in the left panel. Screenshot: assets/runtime-qa-2026-07-31/04-pdf-open-success-blank.png.

Closure path: test the PDF tab at minimum and default sizes, allow helper labels to wrap or widen the panel, and add a visual size regression check.

### R5. Premium workflow surfaces only have empty-state proof

Severity: P2, incomplete acceptance coverage.
Evidence: Tier 4 runtime.

Workflow Dashboard, Workflow Grants, Recipe Builder, and Vault loaded without visible errors. Dashboard reported zero jobs and grants, Grants reported zero visible grants, Recipe Builder reported ready for a new recipe, and Vault showed its empty state. Screenshot: assets/runtime-qa-2026-07-31/05-vault.png.

Not proven: recipe and grant creation, folder scanning, authorized execution, retry/quarantine/cancel, PDF placement and save, or populated Vault copy/delete behavior.

Closure path: complete one fixture-backed workflow from recipe creation through authorized execution, then verify output, audit state, retry behavior, and operator-visible errors.

## Automated verification

Passing checks:

- ./.venv/bin/pytest -q tests/test_entrypoints.py tests/test_build_profile.py tests/test_launch_profile.py tests/test_main_window_contract.py: 17 passed in 0.84s.
- ./.venv/bin/pytest -q desktop_app/tests/test_pdf_features.py desktop_app/tests/test_pdf_render_cache.py desktop_app/tests/test_pdf_field_detection.py: 35 passed in 1.36s.
- ./.venv/bin/pytest -q desktop_app/tests/test_workflow_screen_smoke.py: 11 passed in 0.48s.

A1, stale or hanging workflow review test:

    gtimeout 12s ./.venv/bin/pytest -q desktop_app/tests/test_main_window_logic.py -k workflow_review_action --maxfail=1

Result: exit 124 timeout.

The test at desktop_app/tests/test_main_window_logic.py:272-283 constructs a standard locked MainWindow, triggers workflow review, and expects a URL. The current implementation at desktop_app/views/main_window.py:668-693 shows a premium-required dialog and routes to the license purchase flow. Decide which contract is canonical, then update implementation and test together. Do not mask the modal with a timeout.

A2, license tier persistence failure:

    gtimeout 90s ./.venv/bin/pytest -q --ignore=desktop_app/tests/test_main_window_logic.py

Result: 78 passed, 1 failed in 4.59s.

Failure: tests/test_license_storage_operations.py::test_workflow_automation_gated_by_license_tier, AttributeError: NoneType has no attribute value.

Source evidence:

- desktop_app/license/storage.py:75-80 starts _normalize_tier() but does not contain the conversion and ValueError fallback.
- desktop_app/license/storage.py:102-105 contains that code after return normalized inside _normalize_add_ons(), so it is unreachable from _normalize_tier().
- desktop_app/license/storage.py:232-240 dereferences license_tier.value.

Impact: supplied tiers such as team or starter can fail before license state is persisted, affecting workflow entitlement. The premium profile bypasses normal gating, so premium runtime testing does not cover it.

Closure path: restore complete tier normalization control flow, add explicit team, starter, business, invalid, and missing-tier tests, then repeat the license and premium-gating suite.

A3, isolated MainWindow suite hang:

    gtimeout 12s ./.venv/bin/pytest -q desktop_app/tests/test_main_window_logic.py

Result: exit 124. The workflow smoke file completed normally; the hang is isolated to the workflow review test described in A1.

## Artifacts and scope

Created for this audit:

- docs/review/runtime_qa_audit_2026-07-31.md
- docs/review/assets/runtime-qa-2026-07-31/
- /private/tmp/signkit-runtime-sample.png
- dist/SignKitPremium.app and its PyInstaller support directory

No application source files were edited for this audit. Existing dirty working-tree changes from parallel work were preserved untouched. The report and screenshot artifacts remain uncommitted.

## Acceptance status

User-facing behavior proven: the current premium bundle launches, reaches online backend status, loads the sample source image, presents export options, writes an RGBA PNG, and renders premium empty-state workflow surfaces.

Business/team value: the audit prevents a false release claim for extraction and PDF signing and preserves reproducible evidence for prioritization.

Internal/operational value: build-environment failures, bundle warnings, source-level root causes, test hangs, and license persistence failure are recorded with commands and closure paths.

Not release-ready: R1, R2, R3, and A2 remain open.

Three review passes completed:

- Pass 1 correctness: reproduced launch, sample load, auto-detect, export, PDF open, and premium tabs.
- Pass 2 architecture: traced the graphics-scene collision, legacy/canonical PDF split, and misplaced license normalization.
- Pass 3 supervision readiness: recorded commands, evidence tiers, screenshots, remaining uncertainty, and closure criteria.

## Anything else?

Yes. The package scripts are part of the release surface. The documented builder depends on a broken legacy environment and invalid import probes, while the lower-level builder hardcodes a bare python subprocess. Packaging is not reproducible from the documented one-command path until those environment assumptions are corrected and a clean-build smoke test is added.

## Addendum: blocker remediation and current-build retest (2026-07-31)

This addendum records the remediation pass. The original findings above remain historical evidence of the failures reproduced before the fixes.

### Fixes applied

- `desktop_app/widgets/image_view.py`: renamed the private scene storage from `self.scene` to `self._scene`, preserving the inherited callable `QGraphicsView.scene()` used by result-pane cleanup.
- `desktop_app/resources/sample_signature.py`: the first-run sample now returns a temporary copy of the checked-in `512px-Mohammad_Rafiquzzaman_signature.jpg`. The supplied `/Users/pranay/Documents/512px-Mohammad_Rafiquzzaman_signature_test.jpg` is byte-identical to that canonical repository asset.
- `desktop_app/processing/extractor.py`: auto-detection now derives a bounded global threshold from Otsu, computes the complete ink envelope for disconnected cursive strokes, and retains adaptive contour detection as a fallback.
- `desktop_app/views/main_window_parts/pdf.py`: opening a PDF now loads `PDFViewer` before mutating session state, tracks the active path, restores persisted placements, updates action state, and closes the viewer and session together.
- `desktop_app/pdf/viewer.py`: persisted placements recreate their signature pixmap from `sig_path` before rendering.
- `desktop_app/license/storage.py`: moved tier normalization back into `_normalize_tier`; `team`, `starter`, `business`, invalid, and missing values now resolve safely.
- `desktop_app/views/main_window.py`: workflow review only refreshes a real premium console; a placeholder or unavailable console falls back to the attributed content-free URL. The locked path remains an explicit upgrade flow.
- `build-tools/build_macos.sh`, `build-tools/build.py`, and macOS/Linux/Windows/Intel spec files: the builder prefers `.venv`, uses the executing interpreter for PyInstaller, maps distribution names to import names correctly, avoids cleaning protected virtual-environment caches, embeds the canonical sample, and removes the stale hidden import for a non-existent module.

### Automated verification after fixes

- `./.venv/bin/pytest -q`: **79 passed in 5.75s**.
- Targeted remediation and adjacent PDF/workflow suite: **87 passed, 3 skipped in 3.77s**. Skips are the existing event-loop-dependent rotation and library callback tests.
- `./.venv/bin/python -m compileall -q desktop_app build-tools/build.py`: passed.
- `bash -n build-tools/build_macos.sh`: passed during review of the executable build path.
- `./build-tools/build_macos.sh premium`: passed using `.venv/bin/python`, producing `dist/SignKitPremium.app` at approximately 326 MB.
- Bundle asset check: `Contents/Resources/desktop_app/resources/512px-Mohammad_Rafiquzzaman_signature.jpg` present.
- `codesign --verify --deep --strict --verbose=2 dist/SignKitPremium.app`: passed with a valid bundle and satisfied designated requirement.

The current build still reports only optional PyInstaller compatibility warnings for `mx.DateTime`, `pysqlite2`, and `MySQLdb`. No missing app-owned module warning remains for `desktop_app.views.main_window_parts.library`.

### Manual runtime evidence, Tier 4

The rebuilt arm64 premium app was launched from `dist/SignKitPremium.app` after the source fixes.

- Built-in “Try with sample signature” loaded the supplied real image, displayed `512 × 184`, and produced a full selection of `(14,15)–(507,175)`. No `QGraphicsScene object is not callable` dialog appeared.
- “Auto Detect” retained the full mark rather than the previous `78 × 197` first-stroke crop. Evidence: `assets/runtime-qa-2026-07-31/06-fixed-sample-real-image.png` and `07-fixed-auto-detect-full.png`.
- Opening `assets/demo_document.pdf` displayed the rendered document with `Page 1 of 6`; the viewer no longer remained at `No PDF loaded`. Evidence: `assets/runtime-qa-2026-07-31/08-fixed-pdf-loaded.png`.
- Premium Workflow Dashboard loaded and reported an empty, ready queue without an exception. Evidence: `assets/runtime-qa-2026-07-31/09-fixed-workflow-dashboard.png`.

### Remaining observations and hardening path

- The supplied sample proves the corrected envelope behavior for this real input, but auto-detection is still heuristic and has not been benchmarked against a labeled multi-image corpus. Hardening path: add a small versioned golden set with expected regions and score intersection-over-union before release.
- At the tested 1440 × 948 window size, the PDF sidebar and Workflow Dashboard toolbar visibly clip some long control labels. Core controls remained reachable, so this is a P2 visual usability finding, not a blocker. Hardening path: add responsive sidebar width constraints or horizontal scrolling and a manual visual check at the supported minimum window size.
- The manual pass did not execute a populated workflow from recipe creation through authorized run, retry, quarantine, and output audit. Those were already documented as unproven in the original report and remain follow-up acceptance work.

### Updated acceptance status

R1 graphics-scene crash: **closed and runtime-retested**.

R2 incomplete built-in sample detection: **closed for the supplied canonical sample and runtime-retested**; broader corpus validation remains open.

R3 blank PDF viewer after open: **closed and runtime-retested**.

A1 workflow-review test hang: **closed**, with locked and fallback URL contracts covered by tests.

A2 license-tier persistence failure: **closed**, with the full test suite passing.

The app is buildable and manually usable for the remediated flows. It is not a claim of full production readiness for populated workflow operations or generalized auto-detection until the remaining hardening checks above are completed.

Repository hygiene note: `git diff --check` still reports trailing whitespace in the pre-existing dirty `build-tools/build_all_platforms.sh` changes at lines 237, 243, and 252. That file was not edited in this remediation pass so parallel work remains untouched; it should be cleaned in the owning build-script review.

## Addendum: release-gate hardening pass (2026-07-31)

This pass closed the remaining implementation gaps identified above and retested the affected code paths before rebuilding.

### Additional fixes applied

- `desktop_app/views/main_window_parts/pdf.py`: widened the PDF controls surface to 360 px and placed the complete control stack inside a vertical `QScrollArea`, preventing long actions and lower controls from being clipped at the supported desktop window size.
- `desktop_app/views/main_window_parts/workflow_console.py`: changed the single overflowing toolbar into a two-row grid so filtering, authorization subject, execution, retry, folder, quarantine, cancellation, scan, queue, and pause controls remain reachable without truncation.
- `desktop_app/workflows/engine.py`: direct filesystem signature assets are now preserved. Cleanup only removes temporary files materialized from vault references. This fixes a data-loss risk that mocked signing tests did not expose.
- `desktop_app/tests/fixtures/auto_detect_golden.json` and `desktop_app/tests/test_extractor.py`: added a versioned exact bounding-box golden for the supplied 512 x 184 signature image.
- `desktop_app/tests/test_workflow_engine.py`: added a real-PDF integration test covering recipe persistence, grant authorization, actual PDF output creation, source signature preservation, and `EVT_SIGNING_DONE` audit evidence.

### Verification after this pass

- `./.venv/bin/pytest -q desktop_app/tests/test_extractor.py desktop_app/tests/test_workflow_engine.py desktop_app/tests/test_workflow_screen_smoke.py`: **31 passed in 2.14s**.
- The targeted workflow test now exercises the real signer and confirms the direct sample asset still exists after completion.
- The golden detector test matches `(14, 15, 507, 175)` exactly for `512px-Mohammad_Rafiquzzaman_signature.jpg`.

The updated app must still be rebuilt and manually retested after these UI and engine changes. The native `@Computer` tool is not callable in this session, so the manual retest will use the documented macOS accessibility fallback and will be labeled as such. No claim is made that the unavailable native tool was used.

### Revised acceptance status

- R4 sidebar and toolbar clipping: **implementation closed; rebuilt-bundle visual retest pending**.
- R5 populated workflow coverage: **source and integration evidence closed for recipe, authorized run, real output, source preservation, and audit event; rebuilt UI walkthrough pending**.
- Generalized auto-detection beyond the supplied canonical sample: **open hardening item**. Closure requires a labeled multi-image corpus and IoU threshold evidence.
- Native `@Computer` verification: **blocked by tool availability**, with macOS accessibility fallback available and required for this session.

## Addendum: final rebuilt-bundle acceptance pass (2026-07-31)

The final premium bundle was rebuilt after the last PDF label changes and tested as a single clean runtime instance.

- Targeted UI and PDF suite: **32 passed in 1.95s**.
- Full suite: **79 passed in 5.31s**.
- `./.venv/bin/python -m compileall -q desktop_app build-tools/build.py`: passed.
- `bash -n build-tools/build_macos.sh`: passed.
- `codesign --verify --deep --strict dist/SignKitPremium.app`: passed.
- `./build-tools/build_macos.sh premium`: passed with `.venv/bin/python`; final arm64 bundle size approximately 326 MB.
- Clean launch: the final bundle opened successfully.
- Workflow Dashboard: subject field and all action rows remained fully visible at the 1440 x 948 window size. Evidence: `assets/runtime-qa-2026-07-31/40-final-workflow-layout.png`.
- PDF sidebar: lower template and bulk actions were fully readable after scrolling to the bottom. Evidence: `assets/runtime-qa-2026-07-31/39-final-launch-visible.png`.
- The previous clean-instance manual pass also verified the real sample image, full `(14,15)–(507,175)` selection, and PDF `Page 1 of 6` rendering. Evidence: `assets/runtime-qa-2026-07-31/32-clean-auto-detect-later.png` and `assets/runtime-qa-2026-07-31/35-clean-pdf-loaded-no-dialog.png`.
- In the final clean launch, the status bar showed `Backend: checking...` and then `Backend: Offline`. Local extraction and PDF rendering remained usable, but online backend availability was not re-proven in that final instance. Closure requires starting the supported backend and capturing a fresh `Backend: Online` runtime check.
- Native `@Computer` remained unavailable as a callable tool. These are Tier 4 macOS accessibility observations and screenshots, not native Computer Use evidence.
- `git diff --check` still reports three trailing-whitespace lines in the existing dirty `build-tools/build_all_platforms.sh` changes at lines 237, 243, and 252. This was preserved as parallel work and not changed here.

### Final call

The current build is ready for internal QA and controlled demo use for the tested local extraction and PDF flows. It is not yet a production-readiness claim for generalized auto-detection across an unlabeled corpus or for a fully populated operator workflow walkthrough in the frozen UI. Those are explicit hardening items, not hidden blockers in the tested flows.

## Addendum: backend-online blocker closure (2026-07-31)

The final runtime check exposed one additional app-side blocker: the backend health timer called `self.extraction_view.backend_status_label`, but `MainWindow` owns the status label directly as `self.backend_status_label`. The resulting `AttributeError` was swallowed by the health-check exception handler, leaving a healthy backend displayed as `Backend: checking…`.

- `desktop_app/views/main_window.py`: corrected all three health-state updates to use the canonical top-level `self.backend_status_label`.
- `desktop_app/tests/test_main_window_logic.py`: added a regression test proving a healthy backend updates the visible status label to `Backend: Online`.
- Targeted regression suite: **20 passed, 3 skipped**.
- Rebuilt with `./build-tools/build_macos.sh premium`: **passed**, arm64 `dist/SignKitPremium.app`, approximately 326 MB.
- Fresh health contract: `curl -sS -i http://127.0.0.1:8001/health` returned HTTP 200 and `{"status":"healthy","uploads_dir_exists":true}`.
- Fresh rebuilt-bundle runtime: status bar visibly showed `Backend: Online`. Evidence: `assets/runtime-qa-2026-07-31/44-rebuilt-backend-online-visible.png`.
- Fresh rebuilt-bundle sample flow: the supplied signature loaded with `Img: 512x184`, `Sel: (14,15)–(507,175)`, and `Backend: Online`. Evidence: `assets/runtime-qa-2026-07-31/46-rebuilt-sample-loaded-online.png`.
- Fresh rebuilt-bundle PDF flow: the PDF menu action opened `demo_document.pdf`; the runtime remained online and the status bar reported `Opened PDF: demo_document.pdf`. Evidence: `assets/runtime-qa-2026-07-31/54-pdf-tab-online.png`.

This closes the previously observed backend-online blocker for the rebuilt app. Native `@Computer` verification remains unavailable because no callable Computer Use tool was exposed in this session. The manual evidence above is Tier 4 macOS accessibility and screenshot evidence, not native Computer Use evidence. Generalized auto-detection and populated frozen-UI workflow walkthrough remain hardening items as stated above.

## Addendum: native Computer Use verification (2026-07-31)

The native Computer Use runtime became callable through the installed `computer-use` plugin wrapper and was used against the running rebuilt app `work.signkit.premium.app`. This supersedes the earlier accessibility-only limitation for this pass.

- Semantic navigation to **Signature Extraction** exposed the real sample image, `Img: 512×184`, selection `(14,15)→(507,175)`, quality score `80/100`, and `Backend: Online`. Evidence: `assets/runtime-qa-2026-07-31/55-computer-use-signature-extraction.jpeg`.
- Semantic click on **Auto Detect** completed without a dialog or exception and preserved the expected selection `(14,15)→(507,175)`. Evidence: `assets/runtime-qa-2026-07-31/58-computer-use-auto-detect.jpeg`.
- Semantic navigation to **PDF Signing** exposed the rendered PDF with `Page 1 of 6`, `Close PDF`, `Save Signed PDF...`, field actions, signature library controls, template actions, and Quick Start. Evidence: `assets/runtime-qa-2026-07-31/56-computer-use-pdf-signing.jpeg`.
- Semantic navigation to **Workflow Dashboard** exposed the ready engine summary, operator subject field, filter, run/retry/quarantine/cancel controls, folder scan, queue, pause, and `Workflow Dashboard loaded`, with `Backend: Online`. Evidence: `assets/runtime-qa-2026-07-31/57-computer-use-workflow-dashboard.jpeg`.

This is Tier 4 native Computer Use evidence for the rebuilt bundle. The populated workflow execution path remains intentionally unexecuted in the UI because no recipe or grant was pre-existing and creating persistent test workflow records would alter the user's local app state. The real recipe, grant, signing, source-preservation, and audit path remains covered by the integration test described above.
