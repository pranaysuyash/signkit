# Signature Extractor App

**Desktop-first signature extraction tool** with precision control for extracting signatures from documents.

✨ **Features**:

- 🎯 Precision selection with zoom/pan controls
- 🎨 Color customization & threshold adjustment
- 🔄 EXIF auto-rotation for mobile photos
- 💾 Export as transparent PNG with metadata
- � **PDF signing** with extracted signatures and audit logging
- �🔒 Privacy-focused: all processing happens locally by default
- 🖥️ Desktop app (PyQt/PySide6) with FastAPI backend

## Architecture

- **Frontend**: PySide6 desktop application (macOS, Windows, Linux)
- **Backend**: FastAPI REST API (Python 3.9+)
- **Database**: SQLite for local dev, PostgreSQL for production/backend scaling
- **Processing**: OpenCV, NumPy, PIL for image manipulation

## Documentation

- **[Use Cases](docs/USE_CASES.md)** — 20+ real-world applications (legal, healthcare, design, e-signing)
- **[PDF Quick Start](docs/PDF_QUICK_START.md)** — PDF signing workflow and audit logging
- **[PDF Stack Setup](docs/PDF_SETUP.md)** — runtime library policy, role mapping, and install matrix
- **[PDF Library Exploration](docs/analysis/PDF_LIBRARY_EXPLORATION_2026-06-17.md)** — broader OSS candidate survey and rationale
- **[PDF Platform Convergence](docs/analysis/PDF_PLATFORM_CONVERGENCE_2026-06-17.md)** — long-term architecture for editing, annotations, signing, and export
- **[Long-Term PDF Workspace Architecture](docs/analysis/LONG_TERM_PDF_WORKSPACE_ARCHITECTURE_2026-06-18.md)** — preserved first-principles memo for the durable PDF workspace direction
- **[PDF Implementation](docs/PDF_FEATURE_IMPLEMENTATION.md)** — Technical details for developers
- **[Pricing Strategy](docs/PRICING.md)** — Freemium model with Pro/Team/Enterprise tiers
- **[Product Roadmap](docs/ROADMAP.md)** — 8-phase development plan (auto-recognition, integrations, deployment)
- **[Recent Updates](docs/RECENT_UPDATES.md)** — Latest UX fixes and improvements
- **[UI Changes Guide](docs/UI_CHANGES.md)** — Visual before/after walkthrough
- **[Desktop UI Spec](docs/desktop-frontend/pyqt-spec.md)** — Controls (Zoom %, Fit, Reset/Clean, Rotate) and status bar fields
- **[Coordinate Mapping](docs/COORDINATE_MAPPING.md)** — Rotation-aware scene→image mapping details
- **[Shortcuts](docs/SHORTCUTS.md)** — Keyboard shortcuts for common actions

For archived session notes moved from the repo root, see `docs/ROOT_DOCS_INDEX.md`.
- **[Help & Troubleshooting](docs/HELP.md)** — Quick fixes and FAQs

## Quick Start

### 1. Configuration Setup

**Quick Setup (Recommended)**:

```zsh
# Copy example configuration
cp .env.example .env

# Generate secure JWT secret
openssl rand -hex 32

# Edit .env and replace JWT_SECRET with the generated value
```

**Manual Setup**:

Create `.env` at repo root with these required settings:

```env
# REQUIRED: Generate with: openssl rand -hex 32
JWT_SECRET=your_secure_32_byte_hex_key_here

# REQUIRED: API endpoint for desktop app
API_BASE_URL=http://127.0.0.1:8001

# Database:
# - Local dev fallback: sqlite:///./signature_extractor.db
# - Production / multi-user: postgresql://username:password@localhost:5432/signature_extractor
DATABASE_URL=sqlite:///./signature_extractor.db
```

See `.env.example` for complete configuration options and examples.

### 2. Backend Setup

Run backend:

```zsh
# Install backend dependencies
pip install -r backend/requirements.txt

# Start server
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001
```

Health check: <http://127.0.0.1:8001/health>

### 3. Desktop App

Install dependencies:

```zsh
pip install PySide6 requests python-dotenv pillow opencv-python numpy

# Optional: PDF feature stack (OSS-first default)
python -m pip install pypdfium2 pikepdf
```

Use the stack matrix in **[PDF_SETUP](docs/PDF_SETUP.md)** if you only need part of the PDF workflow:

```zsh
# Preview only
python -m pip install pypdfium2

# Signing only
python -m pip install pikepdf

# Full stack for current PDF feature set
python -m pip install pypdfium2 pikepdf
# Advanced/optional PyMuPDF path (if explicitly enabled)
python -m pip install -r desktop_app/requirements-pymupdf-optional.txt
# Optional annotation and OCR helpers (if needed)
python -m pip install -r desktop_app/requirements-pdf-optional.txt
```

Run app:

```zsh
python -m desktop_app.main
```

Local one-command launcher:

```zsh
./scripts/run-desktop-dev.sh
```

**PDF Features** (optional):

- If PDF feature stack is installed (or optional PyMuPDF is enabled), the PDF menu appears with signing capabilities
- Without them, signature extraction still works normally
- See **[PDF Quick Start](docs/PDF_QUICK_START.md)** for detailed PDF workflow

## Recent Updates (Oct 2025)

✅ **NEW: PDF Signing** (Oct 31, 2025):

- 📝 Place extracted signatures into PDF documents
- 🔍 Interactive PDF viewer with zoom and navigation
- 💾 Save signed PDFs with embedded signatures
- 📊 Comprehensive audit logging for compliance (JSONL format)
- ⚡ Powered by pypdfium2 (Chrome's PDFium), pikepdf, and optional PyMuPDF

✅ **Fixed & Enhanced UX**:

- Selection vs pan conflict (added mode toggle)
- EXIF orientation handling (auto-rotate mobile photos)
- Result visibility (white background for transparency)
- Progressive disclosure (hide panes until selection made)
- Rotation-aware selection mapping that persists through zoom/pan/fit/resize/rotation
- New View controls: Zoom In/Out, editable Zoom % combo (with Fit), Reset Viewport, Rotate
- Clean Viewport action to clear all panes and session; Clear Selection kept separate
- Status bar shows Viewport, Image, Visible bounds, Zoom, Rotation, Selection

✅ **Documentation**:

- Comprehensive use cases (20+ scenarios)
- Pricing strategy (4 tiers, revenue projections)
- Product roadmap (auto-recognition, integrations, deployment)

✅ **Cleanup**:

- Removed React frontend (simplified to desktop-only)
- SQLite fallback for local testing, PostgreSQL for production/backend scaling
- Updated all docs and specs

## Use Cases

### Core Applications

1. **Contract Management & E-Signing** — Extract signatures for DocuSign/Adobe Sign
2. **Document Digitization** — Archive paper documents with signature preservation
3. **Identity Verification (KYC)** — Banks, fintech signature consistency checks
4. **Graphic Design & Branding** — Personal signature for emails, business cards
5. **Medical Forms** — Patient consent form signatures for EMR integration

### Advanced Use Cases

- Legal document comparison & forensic analysis
- Real estate transaction processing
- API integration for SaaS platforms
- Browser extension for quick extraction
- Notarization & apostille services
- Insurance claims processing

See **[full use case guide](docs/USE_CASES.md)** for 20+ detailed scenarios.

## Pricing

- 🪪 **Lifetime Desktop**: **$39** (launch price **$29**) one-time, no subscriptions
- 💼 **Pro Workspace**: **$15/mo or $129/yr** (future)
  - batch workflows, sync, shared libraries, audit exports
- 🏢 **Team / Enterprise**: custom pricing (future)

See **[pricing strategy doc](docs/PRICING.md)** for complete tier details and launch plan.

## Development

### Project Structure

```
signature-extractor-app/
├── backend/                 # FastAPI server
│   ├── app/
│   │   ├── routers/        # Auth & extraction endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── crud/           # Database operations
│   │   └── utils/          # Auth, dependencies
│   ├── uploads/            # Image storage
│   └── setup_db.py         # DB initialization
├── desktop_app/            # PySide6 desktop UI
│   ├── views/              # Main window, widgets
│   ├── api/                # Backend client
│   ├── state/              # Session management
│   └── config.py           # App configuration
├── docs/                   # Documentation
│   ├── USE_CASES.md        # Real-world applications
│   ├── PRICING.md          # Business model
│   ├── ROADMAP.md          # Product development plan
│   └── RECENT_UPDATES.md   # Changelog
└── README.md               # This file
```

### Next Steps (Roadmap Phase 2)

1. **Icons & Visual Polish** — QIcon for buttons, app icon, color theme
2. **Rotate Buttons** — 90° CW/CCW with re-upload
3. **Export Metadata** — JSON output with bbox, timestamp, settings
4. **Auto-Detection** — OCR (Tesseract) and signature recognition (contours/ML)
5. **Browser Extension** — Chrome/Firefox for quick extraction
6. **Packaging** — PyInstaller/Nuitka for distributable binaries

See **[full roadmap](docs/ROADMAP.md)** for 8-phase development plan.

## Contributing

Contributions welcome! Focus areas:

- Desktop UX improvements (icons, themes, shortcuts)
- Image processing enhancements (morphology, edge detection)
- Integration plugins (DocuSign, Zapier, etc.)
- Documentation and tutorials

## License

[Add license here — suggest MIT or Apache 2.0 for open-source]

## Support

- **Issues**: [GitHub Issues](https://github.com/pranaysuyash/signkit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pranaysuyash/signkit/discussions)
- **Email**: [Add support email]

---

**Built with** ❤️ for professionals who need precision and privacy in signature extraction.
