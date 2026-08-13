# Candidate picker native-GUI proof

Date: 2026-08-13  
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`  
Commit under test: `ab2ae64` plus the proof harness changes in this checkout  
Evidence tier: Tier 3 local native-GUI observation

## Command

The proof was run without `QT_QPA_PLATFORM=offscreen` in the active macOS
desktop session:

```text
TMPDIR="$PWD/.codex-test-tmp" ./.venv/bin/python \
  tools/run_candidate_picker_gui_proof.py \
  --output .codex-test-tmp/candidate-picker-native.png
```

The proof harness is reusable and exits nonzero on any failed observation. The
generated screenshot remains in the ignored local test-artifact directory.
Its SHA-256 at capture time was:

```text
dc39ec722a10cc541cb5f5230b9882d87c9764eaa4803956200250ef7f087abe
```

## Observed result

```json
{
  "native_gui": true,
  "cancel": "rejected",
  "confirm": "accepted candidate 2",
  "keyboard_focus": true,
  "preview": "rendered",
  "failure_message": "Preview unavailable"
}
```

The screenshot was visually inspected after capture. The native dialog showed
the focused candidate selector, bounded preview surface, source and bounds,
the explicit text that the ranking score is not a probability, and visible
Cancel and OK actions.

## Scope boundary

This closes the changed candidate-dialog native-GUI observation for `RECON-23`.
It does not prove the full desktop extraction workflow, screen-reader or other
assistive-technology behavior, Windows/Linux behavior, packaged-runtime
behavior, or hosted behavior. Those remain separate gates and require their
own execution evidence.
