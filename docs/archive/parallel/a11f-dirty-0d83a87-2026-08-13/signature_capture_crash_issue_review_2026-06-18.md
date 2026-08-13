# Signature Capture Crash Issue Review

Date: 2026-06-18

## Reported symptom

Clicking `Capture Signature` surfaced an error and the app appeared to close automatically.

## Root cause

The webcam preview timer slot in `desktop_app/views/main_window_parts/extraction.py` assumed every camera frame would be a 3-channel BGR image. If the camera returned an unexpected frame shape or a conversion failed inside `_update_frame()`, the exception could escape the Qt timer callback and tear down the UI event loop.

## Fix applied

- Normalized camera frames before rendering them into the preview.
- Added exception handling around the live preview update path.
- Kept the dialog open on preview failure and surfaced the problem in the dialog instead of letting the app crash.
- Added regression tests for grayscale frames and unsupported frame shapes.

## Verification

- Static inspection of the capture dialog path.
- Added unit coverage in `desktop_app/tests/test_capture_dialog.py`.

## Follow-up

- If a specific camera model still produces odd frames, collect the exact frame shape and OpenCV error text so the preview normalizer can be expanded further.
