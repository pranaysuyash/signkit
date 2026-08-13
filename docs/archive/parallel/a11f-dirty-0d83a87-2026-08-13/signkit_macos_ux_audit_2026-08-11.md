# SignKit macOS UX Audit

**Date:** 2026-08-11
**Scope:** SignKit desktop app (`desktop_app/`), macOS-oriented UX behaviors and conventions
**Owner:** Pranay (triage + execution)
**Context source:** macOS app design guidance + runtime UI code inspection in this repo

## Summary
This pass identified UX issues that reduce macOS consistency, discoverability, and error-prevention under normal use flows. The issues are prioritized for follow-up fixes.

## Findings

- **High – Global command model is split between standard and custom patterns**
  - **Files:** `desktop_app/views/main_window.py`, `desktop_app/views/main_window_parts/pdf.py`, `desktop_app/views/main_window_parts/toolbar.py`
  - **Observed:** File-level actions and a dedicated PDF menu overlap for similar operations, while the toolbar uses minimal icon-only actions.
  - **User impact:** Inconsistent discoverability and higher interaction cost for common actions (open/save/signature actions are split across menu surfaces and toolbar patterns).
  - **Risk:** Users will develop brittle workflows and miss actions, increasing support load and mistakes during time-sensitive signing sessions.
  - **Recommended remediation:** Consolidate command surfacing policy to one primary model. Keep semantic action grouping on the app menu and keep toolbar limited to a small, stable set with labels or consistent icon semantics.

- **High – Broad custom styling overrides undermine native macOS behavior**
  - **Files:** `desktop_app/views/main_window_parts/theme.py`, `desktop_app/resources/styles.qss`, `desktop_app/views/main_window_parts/extraction.py`
  - **Observed:** App-wide/custom panel overrides are extensive and can override expected native control rhythm.
  - **User impact:** Perceived inconsistency in focus state, spacing, hover/active feedback, and input affordances across dialogs.
  - **Risk:** Reduced accessibility and platform trust, especially for macOS users expecting native controls and predictable behavior.
  - **Recommended remediation:** Audit and reduce non-functional custom QSS overrides. Retain only visual treatment needed for parity and rely on default/native widget behavior for interaction states.

- **High – No clearly defined global cancel/abort key pattern in extraction flow**
  - **File:** `desktop_app/views/main_window_parts/extraction.py`
  - **Observed:** Keyboard mapping includes extensive custom shortcuts, but a global Escape-based cancel path is not clearly exposed as a first-class command in the same control flow section.
  - **User impact:** Power users cannot safely escape modal-like/interactive states quickly; incomplete gestures can feel sticky.
  - **Risk:** Friction and accidental actions after failed/unfinished steps.
  - **Recommended remediation:** Add explicit `Esc` behavior for mode-exit/cancel/clear interaction where appropriate (view state, pending edit state, popovers), with predictable behavior across image/PDF modes.

- **Medium – Discoverability gap in rotate flow and operation state cues**
  - **File:** `desktop_app/views/main_window_parts/pdf.py`
  - **Observed:** Rotation and edit operations have multiple entry points; some use shortcut-driven paths that are not visually mirrored in the same toolbar/menu context.
  - **User impact:** Users may repeat or undo unexpectedly, especially when signatures are moved and then transformed.
  - **Risk:** Signature misplacement and repeat edit loops before save/export.
  - **Recommended remediation:** Add clear operation grouping (transform set), explicit reset/undo for each irreversible stage, and visible control state hints.

- **Medium – Toolbar action discoverability tradeoff (icon-only in macOS context)**
  - **File:** `desktop_app/views/main_window_parts/toolbar.py`
  - **Observed:** Toolbar actions are currently compact/icon-only in key places.
  - **User impact:** New users need trial-and-error; repeated use slows down because action intent is not obvious.
  - **Risk:** Increased mistakes and slower onboarding.
  - **Recommended remediation:** Enable explicit text/combined labels where practical, keep icon density low, and prioritize clear first-use affordances on macOS.

- **Medium – Accessibility depth is partial across custom controls**
  - **Files:** `desktop_app/views/main_window_parts/extraction.py`, `desktop_app/views/main_window_parts/pdf.py`, `desktop_app/views/vault_tab.py`
  - **Observed:** Accessibility names and focus policies exist in parts, but custom composite controls and dynamic panels are likely inconsistent in screen-reader flow.
  - **User impact:** Keyboard-only and assistive users face uneven discoverability and task completion reliability.
  - **Risk:** Incomplete accessibility parity vs mainstream macOS behavior expectations.
  - **Recommended remediation:** Audit full tab order and AT labels for every composite widget container and interactive custom control; publish a minimum pass matrix (keyboard, VoiceOver, dynamic mode changes).

- **Medium – Help and troubleshooting are menu-centric, not contextual**
  - **Files:** `desktop_app/views/main_window.py`, `docs/TECHNICAL_GAPS.md`
  - **Observed:** Help/troubleshooting exists, but most guidance is not attached to the failing state.
  - **User impact:** Users do not always know what failed or what next step to recover with.
  - **Risk:** Extra support cycles from non-obvious errors.
  - **Recommended remediation:** Add contextual recovery hints near failure states and a one-click diagnostic route in the active workspace.

- **Low – Keyboard and menu expectation audit needed for Mac standard parity**
  - **Files:** `desktop_app/views/main_window_parts/extraction.py`, `desktop_app/views/main_window.py`
  - **Observed:** Shortcut strategy is strong in parts but should be checked against macOS conventions (especially consistency around cancel, redo/undo, and rotate gestures in every mode).
  - **User impact:** Frequent confusion for muscle-memory usage across app sessions.
  - **Risk:** Reduced long-session usability.
  - **Recommended remediation:** Add a canonical shortcut map and lint check for duplicate/conflicting command keys in active actions.

## Suggested execution plan (smallest durable next pass)

1. Define single command surface policy (Menu vs Toolbar vs Context) and apply once.
2. Introduce explicit Escape/Cancel behavior for extraction and PDF transform states.
3. Reduce/trim custom visual overrides that alter native behavior semantics.
4. Standardize rotation/transform control flow with visible state, reset, and undo points.
5. Ship contextual status/help hints after actionable failures.
6. Run a focused macOS usability pass with keyboard + VoiceOver + drag/transform scenarios.

## Acceptance criteria draft

- At least 80% of primary actions are discoverable through one primary path.
- Escape cancels interactive state predictably in image and PDF sign flows.
- No duplicated action command paths create conflicting names or hidden duplicates.
- Assistive keyboard traversal completes all high-value actions without hidden dead-ends.
- No regression in existing menu accelerators during the audit scope.


## Implementation updates (2026-08-11)

- Added centralized source-selection validation in extraction flow (`desktop_app/views/main_window_parts/extraction.py`):
  - Added `_get_source_selection(require_selection: bool = True)` and switched preview/result/export/metadata paths to this helper.
  - Replaced direct `selected_rect_image_coords()` reads with guarded access to avoid zero-area propagation.
  - Added Escape handler `_handle_escape_cancel()` and bound `Esc` in `_setup_keyboard_navigation`.
  - Added tests for empty-selection guard and preview scheduling guard in `desktop_app/tests/test_main_window_logic.py`.

- Updated macOS toolbar action discoverability (`desktop_app/views/main_window_parts/toolbar.py`):
  - Toolbar style changed to `ToolButtonTextUnderIcon` to avoid icon-only ambiguity.

- Stabilized PDF placement state handling (`desktop_app/views/main_window_parts/pdf.py`, `desktop_app/pdf/viewer.py`):
  - Added `PDFViewer.clear_signature_placement()` as a single source of truth for clearing pending signature preview/state.
  - PDF open/close/reload/signature placement now clear pending placement state via shared helper.
  - Added `_clear_pdf_pending_signature_state()` in the PDF mixin to clear both internal `_pending_sig_path` and viewer pending placement UI state.
  - Added test for restored-signature mutability in `desktop_app/tests/test_pdf_improvements.py`.

### Notes

- These updates are intended to prevent stale placement metadata from surviving document transitions and to make restore/drag paths deterministic.

### Additional findings from this pass (2026-08-11, continued)

- **Medium – PDF signature context actions were incomplete**
  - **Files:** `desktop_app/pdf/viewer.py`, `desktop_app/views/main_window_parts/pdf.py`, `desktop_app/tests/test_pdf_improvements.py`
  - **Observed:** The signature right-click menu exposed only deletion, while users could still rotate and edit appearance only from sidebar controls.
  - **Executed remediation:** Added transform and appearance actions directly in the right-click menu:
    - Rotate +90°
    - Rotate -90°
    - Brightness ±0.1
    - Contrast ±0.1
    - Saturation ±0.1
    - Reset appearance
  - **Risk guard:** Selection handling now also persists style changes to the per-document session immediately to keep edits recoverable when reopening.

- **Low – Reopen/restore behavior still depends on persisted session state**
  - **Files:** `desktop_app/pdf/document_session_store.py`, `desktop_app/pdf/viewer.py`, `desktop_app/tests/test_document_session_store.py`, `desktop_app/tests/test_pdf_improvements.py`
  - **Observed:** Signature re-detect for a PDF opened outside of this app’s session-store flow is not guaranteed; restore requires app-persisted session metadata.
  - **Mitigation in this pass:** Improved session scoring and fallback matching (path + filename + metadata) so persisted placements restore more reliably across file moves/renames.
  - **Residual gap:** For true in-document detection, we still need a persistent on-PDF manifest or signed-output sidecar strategy.

### Execution notes

- This environment has `PySide6` available for these tests, so GUI-adjacent unit tests executed successfully.
- Targeted session/behavior test runs in this pass:
  - `uv run pytest desktop_app/tests/test_coordinate_mapping.py desktop_app/tests/test_document_session_store.py`
  - `uv run pytest desktop_app/tests/test_pdf_improvements.py`
- Remaining GUI validation with hands-on flow is still recommended on a local macOS desktop to confirm discoverability and touch interactions.
