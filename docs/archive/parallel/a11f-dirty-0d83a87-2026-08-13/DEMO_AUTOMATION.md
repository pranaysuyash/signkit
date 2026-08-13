# Automated Demo Video Generation (macOS, Windows, Linux)

This guide shows how to automatically record repeatable demo videos of the desktop app by driving UI flows and capturing the screen. It includes:

- A cross‑platform recorder wrapper around `ffmpeg` (`tools/record.py`)
- A Qt/QTest‑based demo runner (`tools/demo_runner.py`) that executes flows from YAML
- An example flow (`flows/sample_place_sign_export.yaml`)

You can parameterize flows and regenerate videos on demand for different use cases.

## Overview

1) UI automation: Drive your PySide6 app using Qt’s own test helpers (`QTest`) by targeting widgets via `objectName`.
2) Recording: Start and stop an `ffmpeg` screen capture around each flow. Optionally crop to your window.
3) Data‑driven flows: Describe user steps in YAML so you can reuse the same runner to produce different videos.

## Prerequisites

- Python 3.9+
- PySide6 (for in‑process UI driving)
- PyYAML (for flows): `pip install pyyaml`
- ffmpeg on your OS

### Install ffmpeg

- macOS (Homebrew): `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y ffmpeg`
- Windows: Install the official build and add `ffmpeg.exe` to your PATH: https://www.gyan.dev/ffmpeg/builds/

## Flow definition (YAML)

Example at `flows/sample_place_sign_export.yaml`. Steps have this shape:

- `wait`: milliseconds to wait
- `click`: click a widget by `objectName` with optional button
- `type`: send keystrokes to focused widget
- `invoke`: call a named slot/method on the main window (escape complex UI)

You must set stable `objectName`s on widgets you want to target (buttons, inputs, menus). See “Object naming tips” below.

## Recording matrix by OS

- macOS: `ffmpeg -f avfoundation -framerate 30 -i "<screen_index>:" out.mp4`
  - Discover devices: `ffmpeg -f avfoundation -list_devices true -i ""`
  - Crop: add `-filter:v "crop=w:h:x:y"`

- Linux (X11): `ffmpeg -f x11grab -framerate 30 -i :0.0 out.mp4`
  - Specific region: `-video_size 1280x720 -i :0.0+X,Y`
  - Headless CI: run under `Xvfb` and point to that display

- Windows: `ffmpeg -f gdigrab -framerate 30 -i desktop out.mp4`
  - Region: `-offset_x X -offset_y Y -video_size 1280x720`

The provided `tools/record.py` selects the right flags automatically. You can pass a region to crop to your window later.

## Quick start (macOS example)

1) Install prerequisites (PySide6, PyYAML, ffmpeg).
2) Ensure key widgets in `MainWindow` have meaningful `objectName`s (e.g., `openFileButton`, `exportButton`).
3) Edit `flows/sample_place_sign_export.yaml` to match your app.
4) Run the demo runner (this will start ffmpeg, play the flow, and stop recording):

```
python tools/demo_runner.py \
  --flow flows/sample_place_sign_export.yaml \
  --output demos/sample_place_sign_export.mp4
```

## Object naming tips

- In your PySide6 code, set `widget.setObjectName("descriptiveName")` for elements you’ll click.
- Use unique names per view. For list items you dynamically create, trigger actions by invoking slots (`invoke`) instead of blind clicks.
- The runner resolves `window.findChild(QWidget, objectName)`; you can change the type to a concrete widget where appropriate.

## Flow step reference

- `wait: <ms>` – pause for animations or I/O
- `click: <objectName>` – left click; alternative: `click: {target: <objectName>, button: right}`
- `type: "string to type"` – sends key clicks to focused widget
- `invoke: {method: on_export_json, args: []}` – call `getattr(main_window, method)(*args)`

## Advanced usage

- Cropping to window: Extend `tools/record.py` to query window geometry and pass `region=(x,y,w,h)` to `start_recording()`.
- Subtitles: Emit an SRT while running steps, then burn in with `ffmpeg -vf subtitles=subs.srt`.
- Voiceover: Generate TTS audio, then `ffmpeg -i video.mp4 -i voice.wav -shortest -map 0:v -map 1:a out.mp4`.
- CI: On Linux with Xvfb, spawn a virtual display, run the app and the runner, and upload the produced MP4 as an artifact.

## Troubleshooting

- No video/black screen: Verify the input format per OS (avfoundation/x11grab/gdigrab) and the device/display index.
- Cursor not visible: Use OBS if you need cursor highlighting. ffmpeg’s capture is raw.
- Widgets not found: Ensure `objectName`s are set and unique; consider using `invoke` to call slots directly.

## Files added by this guide

- `tools/record.py` – cross‑platform ffmpeg wrapper
- `tools/demo_runner.py` – UI driver using QtTest + YAML flows
- `flows/sample_place_sign_export.yaml` – example flow

