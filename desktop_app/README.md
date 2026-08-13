# Desktop App - Signature Extractor

PyQt/PySide6 desktop client for signature extraction. Connects to the FastAPI backend for image processing.

## Features

- Local image upload and extraction without login; authenticated backend sync uses the JWT session and idempotent extraction requests
- Interactive region selection with rubber band
- One-click auto-detect for likely signature regions
- Real-time threshold and color controls with auto-threshold and auto-clean modes
- Overlay preview showing the extracted signature on the original crop
- Save result as PNG with transparency
- Secure vault storage with usage history
- Canonical PDF signing workflow with persistent per-page placements

## Installation

Install dependencies:

```zsh
pip install -r desktop_app/requirements.txt
```

Or install individually:

```zsh
pip install PySide6 requests python-dotenv pillow
```

## Configuration

Create a `.env` file in the project root (optional):

```env
API_BASE_URL=http://127.0.0.1:8001
```

Default: `http://127.0.0.1:8001`

## Running the App

Ensure the backend is running first:

```zsh
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001
```

Then launch the desktop app:

```zsh
python -m desktop_app.main
```

## Usage

1. Open & Upload Image
2. Select region (Selection mode) or Pan (Pan mode)
3. Optionally use Auto Detect, Auto Threshold, and Auto Clean
4. Preview to process the selection, or use overlay preview to inspect placement
5. Export, copy, save to library, or save to vault

Viewport controls
- Zoom In/Out, editable Zoom % (supports Fit), Reset Viewport, Rotate
- Clean Viewport clears all panes and the session; Clear Selection only removes the rubber‑band

## Project Structure

```text
desktop_app/
  main.py              # Entry point
  config.py            # Configuration loader
  api/
    client.py          # HTTP API client
  state/
    session.py         # Session state management
  views/
    main_window.py     # Main application window
    login_dialog.py    # Login dialog (optional, commented out)
  widgets/
    image_view.py      # Image viewer with region selection
```

## Notes

- Local desktop extraction remains usable offline. Backend extraction endpoints require authentication, owner scope, and an `Idempotency-Key`; the desktop client adds stable keys for upload, region selection, and processing when backend sync is enabled.
- Requires running FastAPI backend
- Color format must include leading # (e.g., #000000 for black)
- Selection coordinates are automatically clamped to image bounds
