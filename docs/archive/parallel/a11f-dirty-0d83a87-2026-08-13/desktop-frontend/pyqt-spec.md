# Desktop Frontend (PyQt/PySide6) Specification

**Status**: ✅ **IMPLEMENTED** (Oct 2025)

This document describes the desktop GUI application built with PySide6 (Qt for Python). The React frontend has been completely removed. The backend FastAPI service remains unchanged.

## Overview

- **FastAPI backend** runs on port **8001** (standardized from initial 8000)
- **Client-server mode**: Desktop app talks to running FastAPI over HTTP at `http://127.0.0.1:8001`
- **Current status**: Fully functional with all core features implemented
- **React frontend**: Completely removed (Oct 2025) - this is now a desktop-only application

## User Workflows (Implemented)

### 1) Login (✅ Implemented)

- Login dialog on startup with email/password inputs
- Call `POST /auth/login` with OAuth2PasswordRequestForm
- JWT stored in `SessionState` (in-memory)
- Token attached as Bearer to subsequent API calls

### 2) Upload Image (✅ Implemented)

- File picker dialog (PNG/JPG/JPEG)
- **EXIF auto-rotation**: Automatically corrects image orientation based on EXIF data
- Call `POST /extraction/upload` as multipart/form-data with `file` field
- Response: `{ id (UUID), filename, file_path }` where `file_path` is intentionally server-private (`null` in current contract); the authenticated client sends a stable `Idempotency-Key`
- Session ID saved in `SessionState` and **displayed in status bar footer** with tooltip

### 3) Select Region (✅ Implemented)

- **QGraphicsView** with zoom/pan/selection modes
- **Mode toggle**: "Selection Mode" button switches between selection and pan/zoom
- **QRubberBand**: Draw rectangle selection (x1, y1, x2, y2)
- **Zoom**: Mouse wheel to zoom in/out
- **Pan**: Click-and-drag in pan mode
- Controls shown: Threshold slider (0-255), Color picker (hex)
- Rotation-aware selection: selection coordinates are mapped from the scene using all 4 corners, so coordinates remain correct after rotating the view or fitting/resizing.

### Viewport Controls (✅ Implemented)

- Zoom buttons: Zoom In / Zoom Out
- Zoom percent: editable combo supporting manual values (e.g., 125%) and a Fit option
- Fit: scale image to active pane while preserving aspect ratio
- Reset Viewport: reset zoom, pan, and rotation to defaults for the active pane
- Rotate: per-pane rotation buttons (↺/↻). Source rotation triggers a re-upload with the rotated image; preview/result rotations are view-only.

### Session/Desktop Actions (✅ Implemented)

- Clean Viewport: clears source/preview/result panes, removes the current session id, and disables dependent actions until a new upload
- Clear Selection: removes current rubber-band selection and hides preview/result panes

### Status Bar (✅ Implemented)

- Viewport WxH, Image WxH, Visible bounds (x1,y1→x2,y2 [WxH]), Zoom %, Rotation °, Selection (x1,y1→x2,y2 [WxH])
- Session id preview with tooltip showing the full id

### 4) Preview Extraction (✅ Implemented)

- Click "Preview" button after making selection
- Call `POST /extraction/process_image/` with params: session_id, x1, y1, x2, y2, color, threshold
- Receives PNG stream (image/png)
- Displays in right panel with **white background** for visibility
- **Status bar feedback**: "Processing..." → "Preview ready!" messages

### 5) Export/Save Result (✅ Implemented)

Three save options:

**a) Export (Professional Dialog)**:
- Opens `ExportDialog` with advanced options:
  - **Format**: PNG-24 (default), PNG-8 (smaller), JPEG (no transparency)
  - **Background**: Transparent, White, Black, or Custom color
  - **Trim to content**: Removes transparent borders with configurable padding (0-100px)
  - **JPEG quality**: Slider (1-100%) for compression control
- Uses PIL for image processing (alpha compositing, format conversion, trimming)
- Save location via QFileDialog

**b) Save to Library** (Quick Save):
- Auto-generated filename: `signature_YYYYMMDD_HHMMSS.png`
- Saves to `~/.signature_extractor/signatures/` (prepared, needs persistence logic)
- Status bar feedback: "Saved to library!"

**c) Copy to Clipboard** (Future):
- Not yet implemented

## API Contracts (Backend on Port 8001)

All API calls go to `http://127.0.0.1:8001`

**POST /auth/login**
- Content-Type: `application/x-www-form-urlencoded`
- Body: `username`, `password`
- Response: `{ access_token, token_type }`

**POST /extraction/upload**
- Content-Type: `multipart/form-data` (field `file`)
- Response: `{ id (UUID), filename, file_path }` where `file_path` is internal metadata (`null` in current contract)

**POST /extraction/process_image/**
- Params/Form fields: `session_id` (UUID), `x1`, `y1`, `x2`, `y2`, `color` ("#RRGGBB"), `threshold` (0-255)
- Response: `image/png` stream

**GET /health**
- Response: `{ status: "ok" }` (used for smoke tests)

**Notes**:
- Color string **must start with `#`** - backend parses hex at indexes 1, 3, 5
- Coordinates clamped to actual image size (backend + frontend validation)
- Backend keeps uploaded files in user-writable upload storage, but does not mount them publicly.

## Project Layout (Current Implementation)

```text
desktop_app/
  main.py                   # ✅ Entry point (QApplication + main window)
  api/
    client.py               # ✅ HTTP wrapper (requests) with JWT, upload, process_image
    __init__.py
  views/
    login_dialog.py         # ✅ QDialog for login (email/password)
    main_window.py          # ✅ QMainWindow with controls + image views + status bar
    export_dialog.py        # ✅ Professional export dialog (formats, backgrounds, trim)
    __init__.py
  widgets/
    image_view.py           # ✅ QGraphicsView with zoom/pan/selection, QRubberBand
    __init__.py
  state/
    session.py              # ✅ Holds access_token, session_id, last_upload_response
    __init__.py
  resources/                # 🔄 Planned: icons, stylesheets (currently using emoji)
```

**Dependencies** (see repo root for virtual env):
- PySide6 (Qt6 for Python)
- requests (HTTP client)
- python-dotenv (environment variables)
- Pillow/PIL (image processing for export)
- opencv-python (backend image processing)
- numpy (backend array operations)

## Key Components (Implementation Details)

### api/client.py (✅ Complete)
- **ApiClient class**:
  - `login(email, password)` → stores JWT token
  - `upload_image(file_path)` → returns `{id, filename, file_path}` (`file_path` remains private and is `null`)
  - `process_image(session_id, x1, y1, x2, y2, color, threshold)` → returns PNG bytes
- **Authorization**: Adds `Authorization: Bearer {token}` header when token present
- **Base URL**: `http://127.0.0.1:8001` (configurable via environment)

### widgets/image_view.py (✅ Complete)
- **ImageView (QGraphicsView)**:
  - Displays QPixmap from local file or uploaded image
  - **Zoom**: Mouse wheel zoom in/out, reset zoom button
  - **Pan**: Click-and-drag in pan mode (when selection disabled)
  - **Selection**: QRubberBand rectangle with mode toggle
  - **EXIF handling**: Auto-rotates images based on EXIF orientation tag
- **Signals**: Emits `selectionChanged(x1, y1, x2, y2)` when user completes selection

### views/main_window.py (✅ Complete)
- **QMainWindow** with:
  - **Menu bar**: File (Open, Exit), Help (About)
  - **Left panel**: Controls (Open File, Mode Toggle, Threshold, Color, Preview, Export, Save to Library)
  - **Right panel**: Two ImageView widgets (Original + Result) in splitter
  - **Status bar**: Session ID (permanent, truncated with tooltip) + transient status messages
- **Progressive UI**: Controls enable/disable based on state (no upload → no preview, etc.)
- **Button tooltips**: Clear explanations for each action
- **Status feedback**: Replaces popup messages with status bar messages

### views/export_dialog.py (✅ Complete)
- **ExportDialog (QDialog)**:
  - **Format selector**: PNG-24 (default), PNG-8 (smaller), JPEG (no transparency)
  - **Background options**: Radio buttons (Transparent, White, Black, Custom)
  - **Custom color picker**: QColorDialog for custom background
  - **Trim to content**: Checkbox with padding spinbox (0-100px)
  - **JPEG quality**: Slider (1-100%) for compression
- **Export logic**: PIL-based processing (alpha_composite, quantize, convert)
- **File dialog**: QFileDialog for save location

### state/session.py (✅ Complete)
- **SessionState class** (singleton pattern):
  - `access_token` - JWT from login
  - `session_id` - UUID from upload
  - `last_upload_response` - Full upload response
  - `original_file_path` - Local file path
  - Methods: `set_token()`, `clear_token()`, `set_session()`

## Configuration

- **API base URL**: Hardcoded to `http://127.0.0.1:8001` in `api/client.py`
  - Future: Move to environment variable or config file
  - `.env` (root): `JWT_SECRET`, `DATABASE_URL`, etc. (backend only)
- **Backend config**: `backend/app/config.py` uses `pydantic_settings`
- **Local library path**: `~/.signature_extractor/signatures/` (prepared, needs implementation)

## Error Handling (✅ Implemented)

**HTTP status mapping**:
- **401**: Clear token and show Login dialog
- **403**: "Permission denied" message
- **404**: "File not found" for session/image
- **413/415**: "File too large/unsupported type"
- **422**: Show validation errors from backend
- **500**: Generic server error with details

**User feedback**:
- **Status bar messages**: Transient messages for operations (upload, process, export)
- **QMessageBox**: For errors, warnings, and confirmations
- **Try-catch blocks**: All API calls wrapped with exception handling

## Logging & Diagnostics

**Current**: Console logging (stdout/stderr)

**Future**:
- Rotating file handler in `desktop_app/logs/app.log`
- Help > Diagnostics menu to open logs
- Test `/health` endpoint from Help menu

## Build & Run (macOS zsh)

### Development Setup

```zsh
# Create venv and install deps
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install PySide6 requests python-dotenv pillow opencv-python numpy

# Install backend deps (if not already done)
pip install sqlalchemy psycopg2-binary python-multipart 'python-jose[cryptography]' 'passlib[bcrypt]' pydantic-settings
```

### Run Backend (Terminal 1)

```zsh
source .venv/bin/activate
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001
```

### Run Desktop App (Terminal 2)

```zsh
source .venv/bin/activate
python -m desktop_app.main
```

### Packaging (Future)

```zsh
pip install pyinstaller
pyinstaller --noconfirm --windowed --name "Signature Extractor" desktop_app/main.py
# Or use PyInstaller with spec file for better control
```

## Completed Features (Oct 2025)

### Core Functionality ✅
- [x] Login dialog with JWT authentication
- [x] File upload with EXIF auto-rotation
- [x] Image display with zoom/pan/selection modes
- [x] Selection mode toggle (vs pan mode)
- [x] Threshold slider (0-255)
- [x] Color picker (hex)
- [x] Preview extraction
- [x] Professional export dialog (PNG-24/PNG-8/JPEG, backgrounds, trim, quality)
- [x] Save to library (auto-generated filenames)
- [x] Status bar with session ID and transient messages
- [x] Progressive UI (enable/disable controls based on state)
- [x] Button tooltips
- [x] White background for result visibility

### React Frontend
- [x] **Completely removed** (Oct 2025) - Desktop-only application

## Pending Features

### High Priority 🔴
- [ ] **Keyboard shortcuts** (Ctrl+O, Ctrl+S, Delete, Ctrl+Z)
- [ ] **Proper QIcon icons** (replace emoji)
- [ ] **Local library infrastructure** (persistence, sidebar list, double-click load)
- [ ] **Dark theme toggle**

### Medium Priority 🟡
- [ ] **Rotate with re-upload** (CW/CCW buttons)
- [ ] **Export metadata JSON** (bbox, timestamp, settings)
- [ ] **Copy to clipboard** (result image)
- [ ] **Batch processing** (multiple files)
- [ ] **Presets** (save/load threshold+color combos)

### Low Priority 🟢
- [ ] **Auto-detection** (OCR + signature detection)
- [ ] **In-app backend launcher** (bundled mode)
- [ ] **Help > Diagnostics** menu (logs, health check)
- [ ] **File logging** (rotating handler)
- [ ] **Application icon** (dock/taskbar)
- [ ] **Installer** (DMG for macOS, MSI for Windows)

## Technical Debt
- [ ] Move API base URL to config file/environment variable
- [ ] Add comprehensive error handling for network failures
- [ ] Implement retry logic for API calls
- [ ] Add loading spinners for long operations
- [ ] Unit tests for image processing logic
- [ ] Integration tests for API client
- [ ] UI tests for critical workflows
- Help menu (✅ Implemented)
  - Help & Troubleshooting (opens docs/HELP.md)
  - Keyboard Shortcuts (opens docs/SHORTCUTS.md)
  - Backend health check (opens http://127.0.0.1:8001/health)

### Hosted extraction contract addendum (2026-08-12)

Backend extraction calls require a JWT owner session. Upload, region selection, and process calls use stable idempotency keys; export, delete, and audit receipts are owner-scoped operations. Local/offline extraction remains separate from hosted API authorization. Production readiness still requires applying the ownership/audit migration and completing the `L0-09` hosted smoke gate.
