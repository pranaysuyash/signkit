# SignKit macOS App Review - 2026-06-26

This note captures the macOS design review pass requested for `signature-extractor-app`.

## What Was Reviewed

- App shell and workflow surfaces in `desktop_app/views/main_window.py`
- Toolbar and shortcut behavior in `desktop_app/views/main_window_parts/toolbar.py`
- Menu ordering and native roles in `desktop_app/views/main_window.py` and `desktop_app/views/main_window_parts/pdf.py`
- App preferences surface in `desktop_app/views/preferences_dialog.py`
- Visual state from fresh screenshots in `screenshots_final/`

## Changes Made

- Added a native `SignKit` app menu with `About`, `Preferences`, and `Quit`.
- Added a lightweight preferences dialog for onboarding visibility.
- Moved the standard menu set into macOS order: `File`, `Edit`, `View`, `Window`, `Help`, then app-specific menus.
- Normalized core shortcuts toward macOS conventions.
- Simplified the main toolbar to icon-only actions and removed extra clutter.
- Fixed window-state persistence to use the same `QSettings` namespace for save and restore.

## Visual Validation

Fresh screenshots were captured successfully with:

- `scripts/final_screenshot_capture.py`

Representative outputs reviewed:

- `screenshots_final/00_01_empty_20260626_214502.png`
- `screenshots_final/14_15_pdf_empty_20260626_214529.png`
- `screenshots_final/18_19_final_20260626_214535.png`

The app now reads more like a native Mac utility than before:

- cleaner top chrome
- simpler toolbar
- better command structure
- less menu noise in the primary workflow

## Verification

- `./.venv/bin/pytest desktop_app/tests/test_main_window_logic.py -q`
- `./.venv/bin/python -m py_compile desktop_app/views/main_window.py desktop_app/views/preferences_dialog.py desktop_app/views/main_window_parts/toolbar.py desktop_app/views/main_window_parts/pdf.py desktop_app/views/main_window_parts/extraction.py`
- `QT_QPA_PLATFORM=offscreen .venv/bin/python` menu inspection confirmed menu order:
  - `SignKit`
  - `File`
  - `Edit`
  - `View`
  - `Window`
  - `Help`
  - `License`
  - `Tools`
  - `PDF`

## Remaining Mac Polish Gaps

- The app still uses a custom dark/glass visual language in content areas, which is acceptable for a pro tool but not fully system-default.
- The status bar remains information-dense; it could be simplified further if we want an even more native Mac feel.
- Some PDF and extraction controls are still bespoke because the workflow is inherently custom and pro-tool oriented.

## Conclusion

The app is now closer to macOS conventions in structure and command model, and the changes are verified against the live Qt runtime and fresh screenshots.
