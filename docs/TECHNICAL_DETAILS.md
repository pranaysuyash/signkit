# Technical Details & Implementation Guide

This document contains technical implementation details that were removed from the user-facing HELP.md to keep it focused on end-user questions. This information is intended for developers, advanced users, and those troubleshooting technical issues.

## Architecture Overview

### Frontend (Desktop App)

- **Framework**: PySide6 (Qt 6.x) with Python 3.9+
- **UI Pattern**: MVC with custom widgets
- **Key Components**:
  - `main_window.py`: Main application window and event handling
  - `image_view.py`: Custom image viewer with selection and zoom
  - `api/client.py`: HTTP client for backend communication
  - `state/session.py`: Session state management

### Backend (FastAPI Server)

- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (default) or PostgreSQL
- **Image Processing**: OpenCV, PIL/Pillow, NumPy
- **Authentication**: JWT-based with configurable secrets

## Image Processing Pipeline

### 1. Image Loading & EXIF Correction

- Uses PIL/Pillow for EXIF orientation detection
- Automatically rotates images based on EXIF metadata
- Converts to QImage for Qt display

### 2. Selection & Coordinate Mapping

- Selection rectangles use image pixel coordinates (not display coordinates)
- Qt widgets use display coordinates; conversion handled in `image_view.py`
- Selection bounds: (x1, y1) to (x2, y2) where x1 < x2, y1 < y2

### 3. Threshold Processing

- **Manual Threshold**: User-adjustable slider (0-255)
- **Auto Threshold**: Otsu's method using NumPy histogram analysis
- Color customization: RGB values with #RRGGBB format
- Processing happens server-side via OpenCV

### 4. Output Generation

- PNG format with transparency preservation
- Metadata export available as JSON (selection coords, threshold, color, session info)

## Backend API Endpoints

### Authentication (`/auth`)

- `POST /auth/login`: User authentication (returns JWT token)
- Uses configurable `JWT_SECRET` environment variable

### Extraction (`/extraction`)

- `POST /extraction/upload`: Image upload (multipart/form-data)
- `POST /extraction/select_region/`: Persist a validated region selection for a session
- `POST /extraction/process_image/`: Process selection
  - Parameters: x1, y1, x2, y2, color, threshold
  - Returns: PNG bytes of extracted signature

### Health Check

- `GET /health`: Server status and version info

## Database Schema

### Core Models (SQLAlchemy)

- **User**: Authentication and user management
- **Document**: Uploaded images and metadata
- **Extraction**: Processing results and coordinates

### File Storage

- Images stored in `backend/uploads/images/`
- Stored files are intentionally not publicly mounted via `/uploads/images/` in the current architecture
- Upload reads are bounded to the configured maximum plus one byte, and validated files are atomically written with owner-readable permissions.
- Stale image and region metadata artifacts are cleaned at startup and after successful uploads; the default retention is 24 hours and is configurable with `SIGNKIT_UPLOAD_RETENTION_SECONDS`.
- This local lifecycle does not provide hosted owner authorization or idempotent cross-request retry semantics.
- SQLite database: `backend/data/app.db` (configurable)

## Coordinate Systems

### Qt/Display Coordinates

- Origin: Top-left (0,0)
- Units: Display pixels (affected by zoom)
- Used for: UI interactions, widget positioning

### Image/Pixel Coordinates

- Origin: Top-left (0,0)
- Units: Image pixels (resolution-dependent)
- Used for: Selection rectangles, backend processing

### PDF Coordinates (when applicable)

- Origin: Bottom-left (0,0)
- Units: Points (72 DPI standard)
- Conversion handled in PDF signing modules

## Error Handling & Troubleshooting

### Common Backend Errors

- **ConnectionError/Timeout**: Backend server not running on port 8001
- **413 Payload Too Large**: Image file exceeds server limits
- **415 Unsupported Media Type**: Invalid image format
- **500 Internal Server Error**: Processing failure (check server logs)

### File Upload Issues

- Ensure multipart/form-data encoding
- Validate file extensions: .png, .jpg, .jpeg
- Check file size limits in backend configuration

### Session Management

- Each upload creates a new session ID
- Sessions expire on application restart
- Session data includes: image path, selection coordinates, processing parameters

## Dependencies & Libraries

### Core Dependencies

```txt
PySide6>=6.5.0        # Qt GUI framework
requests>=2.31.0      # HTTP client
opencv-python>=4.8.0  # Image processing
Pillow>=10.0.0        # Image manipulation
numpy>=1.24.0         # Numerical computing
```

### Optional PDF Features

```txt
pypdfium2>=4.26.0     # PDF rendering
pikepdf>=8.10.0       # PDF manipulation
PyMuPDF>=1.23.0       # Alternative PDF processing
```

### Backend Dependencies

```txt
fastapi>=0.104.0      # Web framework
sqlalchemy>=2.0.0     # ORM
python-jose>=3.3.0    # JWT handling
python-multipart>=0.0.6  # File uploads
```

## Configuration

### Environment Variables

- `JWT_SECRET`: Required for authentication (generate with `python backend/generate_secret.py`)
- `DATABASE_URL`: Database connection string (SQLite default: `sqlite:///backend/data/app.db`)
- `API_BASE_URL`: Backend server URL (default: `http://127.0.0.1:8001`)

### Desktop App Configuration

- Backend URL hardcoded in `desktop_app/api/client.py`
- Default port: 8001 (update both client and server if changing)
- Session state stored in memory (persists during app runtime)

## Development & Testing

### Running the Backend

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### Database Setup

```bash
python backend/setup_db.py  # Create/reset database
python backend/verify_setup.py  # Check database state
```

### Testing Authentication

```bash
python backend/test_auth.py  # Test login flow
```

### Building & Packaging

- Use PyInstaller for desktop app distribution
- Backend can be containerized with Docker
- See `docs/BUNDLING_ANALYSIS.md` for packaging details

## Performance Considerations

### Image Processing

- Large images (>10MB) may cause memory issues
- Processing time scales with image resolution
- Threshold computation uses Otsu's algorithm (O(n) where n = pixel count)

### UI Responsiveness

- Preview updates debounced at 200ms
- Image loading happens in background threads
- Zoom and pan operations are optimized for smooth interaction

### Memory Management

- Images kept in memory during session
- Temporary files cleaned up on session end
- Large selections may impact performance

## Security Notes

- All processing happens locally (no cloud dependencies by default)
- JWT tokens have configurable expiration
- File uploads validated for type and size
- No external API calls during normal operation
- Audit logging available for PDF operations (when enabled)

## Integration Points

### PDF Signing (Optional)

- Requires additional libraries (pypdfium2, pikepdf)
- Separate audit logging system
- Coordinate conversion between Qt and PDF coordinate systems
- See `docs/PDF_FEATURE_IMPLEMENTATION.md` for details

### Library Storage

- Signatures saved as PNG with metadata
- JSON metadata includes extraction parameters
- File-based storage in user directory
- No database dependency for library features

This technical documentation preserves the implementation details that were removed from the user-facing help, ensuring developers and advanced users have access to the information they need while keeping the main help focused on end-user questions.

### Hosted extraction asset contract (2026-08-12)

Hosted extraction is authenticated through the canonical JWT dependency and owner-scoped by `Image.user_id`. Optional workspace execution linkage is accepted only when the execution belongs to the authenticated owner. Files are written privately and returned as internal paths only; export creates a receipt-backed ZIP, deletion records a soft-delete and cleanup receipt, and the audit endpoint remains available to the owner after deletion. Duplicate and concurrent retries converge through the database uniqueness constraint on owner, event type, and idempotency key. Migration `e42b7f8c91aa` must be applied before deployment.
