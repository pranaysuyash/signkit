# Signature Extractor — Product Roadmap

## Addendum (2026-07-16)

This roadmap contains useful historical feature detail but is not the current ordering
authority for legal-signature or vertical expansion. The next product programme begins
with defensible local completion (integrity, consent/intent, evidence package,
verification, certificate support), then canonical vertical configurations, then
optional connected/regulated trust. Use
`docs/research/2026-07-16_signkit_market_legal_vertical_research.md` and
`docs/analysis/2026-07-16_local_first_trust_architecture_decision.md`. No item there is
runtime-complete merely because it is documented.

## Overview

Desktop-first signature extraction tool with server/cloud expansion path. Core value: extract signatures from documents instantly with fine control, export for e-signing workflows or direct integration.

---

## Phase 1: Desktop UX Polish ✅ (mostly complete)

### Completed

- [x] Zoom/pan controls (+, -, Fit, 100%, Ctrl+wheel)
- [x] Selection dimensions display (W×H, position)
- [x] Crop preview pane (shows raw selection)
- [x] Live result preview (debounced threshold/color changes)
- [x] Clear selection button
- [x] White background for result view (transparency visible)
- [x] SQLite backend option (no Postgres required for local use)
- [x] Hide preview/result panes until selection made (maximize source view initially)

### In Progress

- [x] **Selection vs Pan mode toggle** — "Mode: Select" / "Mode: Pan" button to avoid conflict when zoomed ✅ **COMPLETED**
- [x] **EXIF orientation handling** — Auto-rotate images based on metadata so source view matches camera orientation ✅ **COMPLETED**
- [ ] **Icons and visual polish** — Use QIcon for buttons; app icon; subtle color theme

### Recently Completed (Oct 2025)

- [x] **Status bar with session ID** — Permanent display in footer with tooltips
- [x] **Professional export dialog** — Format options (PNG-24/PNG-8/JPEG), background choices, trim to content, quality control
- [x] **Save to Library quick-save** — Auto-generated timestamp filenames with PNG default

---

## Phase 2: Image Manipulation & Export

### Rotate

- **Implementation**: Rotate 90° CW/CCW buttons
- **Approach**: Client rotates image in-memory (PIL), re-uploads as new session_id, updates source view
- **Why**: Keeps server and client state aligned; no coordinate mapping complexity
- **UI**: Add `Rotate ↶` and `Rotate ↷` buttons near zoom controls

### Export Formats & Metadata

- **PNG**: Transparent background (current)
- **JPEG**: Opaque white background option
- **SVG**: Experimental vectorization via potrace or similar
- **Metadata JSON**:
  ```json
  {
    "original_filename": "contract.jpg",
    "selection_bbox": { "x1": 120, "y1": 450, "x2": 680, "y2": 820 },
    "output_size": { "width": 560, "height": 370 },
    "dpi": 300,
    "color": "#0000ff",
    "threshold": 200,
    "timestamp": "2025-10-26T14:32:00Z"
  }
  ```
- **Clipboard Copy**: One-click copy PNG to clipboard for quick paste into other tools

### Presets

- Save/load threshold + color + morphology combos
- Use cases: "Dark Blue Ink", "Light Gray Signature", "Black on White"
- Store in JSON in user's home dir or app data folder

---

## Phase 3: Advanced Processing Options

### Thresholding Enhancements

- **Otsu's Method**: Automatic threshold calculation
- **Adaptive Thresholding**: Local threshold per region (better for uneven lighting)
- **UI**: Dropdown: "Manual | Otsu | Adaptive"

### Morphology Operations

- **Erode/Dilate**: Clean up noise, fill gaps
- **UI**: Toggle switches + strength sliders (radius 1-5px)

### Edge Smoothing

- **Gaussian Blur**: Pre- or post-mask to soften jagged edges
- **Anti-aliasing**: Optional upscale → process → downscale for smoother output

### Background Modes

- **Current**: Color fill + alpha
- **Pure Alpha**: White → transparent (no color replacement)
- **Grayscale**: Keep original ink tone, remove background

---

## Phase 4: Auto-Recognition (AI/ML)

### Text Mode (OCR)

- **Library**: Tesseract (via pytesseract)
- **Use Case**: Extract typed signatures, names, email addresses from documents
- **UI**: "Mode: Manual | Text | Signature" toggle
- **Workflow**: Run OCR on full image or selected region → highlight detected text → user picks which to extract

### Signature Detection (Computer Vision)

- **Approach 1 — Contour-based**:
  - Find connected components
  - Filter by aspect ratio, solidity, area
  - Auto-suggest regions likely to be signatures
- **Approach 2 — ML-based** (future):
  - Train lightweight CNN on signature vs non-signature patches
  - YOLOv8-nano or MobileNet for real-time detection
  - Pre-trained model available as optional download (10-50MB)
- **UI**:
  - "Auto-Detect Signatures" button
  - Highlights candidate regions with confidence scores
  - User clicks to accept or manually adjust

### Implementation Notes

- Make recognition optional (plugin/module architecture)
- Keep core extraction fast; recognition runs on demand
- Provide feedback progress bar for longer operations

---

## Phase 5: Integration & Extensibility

### DocuSign & E-Sign Platforms

- **Export Package**: PNG + metadata JSON + placement coordinates
- **Placement Strategies**:
  - **Absolute Position**: Use JSON (pageNumber, x, y, width, height) to create DocuSign "signHere" tab
  - **Anchor Text**: Place relative to anchor string (e.g., "Signature: \_\_\_")
- **Helper Script** (`integrations/docusign_upload.py`):
  - Create envelope with document
  - Add recipient and placement tab
  - Upload PNG as custom stamp (optional) or use platform's signature field
- **REST API Mode**: Expose backend endpoint `/export/docusign` that:
  - Accepts session_id, recipient info, placement config
  - Returns DocuSign envelope URL for signing

### Browser Extension (Chrome/Firefox/Edge)

- **Use Case**: Right-click on image in browser → "Extract Signature" → opens mini UI in sidebar
- **Tech Stack**: WebExtension API + local backend connection (WebSocket or HTTP to localhost:8001)
- **Flow**:
  1. User right-clicks image
  2. Extension sends image to local backend (or cloud if deployed)
  3. Shows selection UI in sidebar
  4. Processed result copied to clipboard or downloaded
- **Privacy**: All processing local by default; cloud opt-in

### REST API & Webhook

- **Endpoints**:
  - `POST /extraction/upload` (existing)
  - `POST /extraction/process_image/` (existing)
  - `POST /export/metadata` — Returns JSON metadata
  - `POST /export/clipboard` — Prepares PNG for clipboard (desktop-only feature via local endpoint)
  - `POST /webhook/docusign` — Trigger envelope creation from external app
- **Authentication**: JWT tokens for cloud mode; optional for local desktop use
- **Rate Limiting**: Token bucket (10 req/min for free tier, unlimited for paid)

### Third-Party Integrations

- **Zapier/Make.com**: Trigger on file upload → extract → send to e-sign platform
- **Slack/Teams Bot**: Upload doc in chat → bot replies with extracted signatures
- **Google Drive/Dropbox**: Batch process folders via OAuth integration

---

## Phase 6: Deployment & Distribution

### Desktop App Packaging

- **Tool**: PyInstaller or Nuitka
- **Platforms**: macOS (universal binary), Windows (x64), Linux (AppImage)
- **Installer**:
  - macOS: DMG with drag-to-Applications
  - Windows: NSIS or Inno Setup installer
  - Linux: AppImage (portable) + optional .deb/.rpm
- **Size Target**: <100MB (include Python runtime + Qt + deps)
- **Auto-Update**: Use Sparkle (macOS) or built-in updater checking GitHub releases

### Server/Cloud Deployment

- **Container**: Docker image (FastAPI + SQLite or Postgres)
- **Hosting Options**:
  1. **Fly.io**: $0-5/mo for low traffic; auto-scale
  2. **Railway**: Similar pricing; simpler setup
  3. **DigitalOcean App Platform**: $5/mo droplet
  4. **AWS/GCP/Azure**: For enterprise; use ECS/Cloud Run/App Service
- **CI/CD**: GitHub Actions
  - Build Docker image on push to `main`
  - Run tests (pytest for backend)
  - Deploy to staging then production
  - Auto-generate release notes
- **Monitoring**: Sentry for error tracking, Plausible/PostHog for usage analytics (privacy-friendly)

### Data & Privacy

- **Local-First**: Desktop app processes everything locally (no data sent to cloud by default)
- **Cloud Opt-In**: User can enable cloud sync/backup (encrypted at rest)
- **GDPR Compliance**: No PII stored; images auto-deleted after 24h on cloud unless user saves
- **Terms of Service**: Clear language about data handling, no training on user data

---

## Phase 7: Marketing & Go-To-Market

### Landing Page (One-Pager)

- **Hero Section**:
  - Headline: "Extract Signatures from Documents in Seconds"
  - Subheadline: "Desktop app with precision control. Export to DocuSign, HelloSign, or anywhere."
  - CTA: "Download for macOS" | "Download for Windows" | "Try Web Demo"
  - Hero Image: Animated GIF or video (15s) showing: upload → select → extract → save
- **Features Section** (3 columns):
  - **Fast & Local**: Process images on your machine. No upload delays.
  - **Precision Control**: Zoom, adjust threshold, pick color. Perfect extraction every time.
  - **Easy Export**: PNG, JSON metadata, one-click copy. Integrates with e-sign platforms.
- **Use Cases** (4 cards):
  - Real Estate Agents: Extract client signatures from contracts
  - HR Teams: Process signed offer letters
  - Legal Professionals: Archive signature images from agreements
  - Small Business: Quick signature extraction for invoices
- **Pricing**:
  - **Free**: Desktop app, unlimited local use
  - **Pro** ($9/mo or $79/yr): Cloud sync, browser extension, priority support
  - **Enterprise** (Custom): Self-hosted, SSO, API access, SLA
- **Social Proof**: Testimonials (get 3-5 early users to provide quotes)
- **FAQ**: 5-7 common questions (privacy, formats, integrations)
- **Footer**: Links to docs, GitHub, support email, Twitter/X

### SEO & Content

- **Target Keywords**:
  - "signature extraction software"
  - "extract signature from PDF"
  - "signature extractor tool"
  - "digital signature cropping"
  - "DocuSign signature upload"
- **Blog Posts** (publish 1/week for 8 weeks):
  1. "How to Extract Signatures from PDFs for DocuSign"
  2. "Best Practices for Signature Image Quality"
  3. "Automating Document Workflows with Signature Extraction"
  4. "Privacy-First Signature Extraction: Why Local Processing Matters"
  5. "Integrating Signature Extraction with Zapier"
  6. "Batch Processing Signatures: A Guide for HR Teams"
  7. "Open Source Signature Extraction: Building with FastAPI and Qt"
  8. "Signature Detection with Computer Vision: Behind the Scenes"

### Launch Strategy

- **Week 1-2**: Soft launch
  - Post to Hacker News (Show HN: Signature extraction tool)
  - Share on Reddit (r/productivity, r/python, r/dataisbeautiful)
  - Tweet with demo video
  - Submit to Product Hunt (plan for Thursday launch)
- **Week 3-4**: Outreach
  - Email 20 real estate agents / HR professionals for feedback
  - Offer Pro plan free for 6 months in exchange for testimonial
  - Reach out to YouTubers in productivity/tech space
- **Month 2**: Iterate
  - Fix top 3 user complaints
  - Add most-requested feature (likely auto-detection or batch mode)
  - Publish case study with early customer
- **Month 3+**: Scale
  - Paid ads (Google/Facebook) if CAC < LTV
  - Partner with e-sign platforms (affiliate or integration listing)
  - Launch browser extension
  - Apply to Y Combinator / other accelerators if seeking funding

### Messaging & Positioning

- **Tagline**: "Precision signature extraction. Local-first. Export anywhere."
- **Elevator Pitch**:
  > "Signature Extractor is a desktop app that helps professionals extract signatures from documents with precision control. Unlike generic cropping tools, we offer zoom, threshold adjustment, and one-click export to e-sign platforms. Perfect for real estate agents, HR teams, and anyone processing signed documents."
- **Differentiation**:
  - **vs. Adobe Acrobat**: Faster, cheaper, focused on one task
  - **vs. Generic Image Editors**: Specialized for signatures; auto-detection coming
  - **vs. Online Tools**: Privacy-first (local processing); no file size limits
- **Brand Voice**: Professional but friendly; helpful not salesy; privacy-conscious

---

## Phase 8: Advanced Features (Future)

### Batch Mode

- **UI**:
  - "Open Folder" button
  - List view of all images
  - Apply same settings to all
  - Progress bar with cancel option
- **Workflow**:
  1. Select folder with 10-100 documents
  2. App auto-detects signature regions (if auto-detect enabled)
  3. User reviews and adjusts
  4. Export all to named files (e.g., `signature_001.png`, `signature_002.png`)

### History & Organization

- **History Pane**: List of all processed images with thumbnails, timestamps
- **Search**: Filter by date, filename, color used
- **Tags**: User-defined tags (e.g., "Client A", "Q3 Contracts")
- **Export History**: CSV or JSON with metadata for all processed files

### API Client Libraries

- **Python**: `pip install signature-extractor-client`
- **JavaScript/Node**: `npm install signature-extractor-client`
- **Example**:

  ```python
  from signature_extractor import Client

  client = Client(api_key="sk_...")
  result = client.extract(
      image_path="contract.jpg",
      bbox=(100, 200, 500, 400),
      color="#0000ff",
      threshold=180
  )
  result.save("signature.png")
  result.export_metadata("metadata.json")
  ```

### White-Label / Self-Hosted

- **Target**: Enterprises, agencies
- **Features**:
  - Custom branding (logo, colors)
  - Docker Compose stack (backend + frontend + DB)
  - Admin dashboard (user management, usage stats)
  - API quotas and billing integration (Stripe)
- **Pricing**: One-time $499 or $49/mo per instance

---

## Success Metrics

### Desktop App

- **Downloads**: 1,000 in first 3 months
- **Active Users** (DAU/MAU): 20% DAU/MAU (engaged user base)
- **Retention**: 40% week-1 retention
- **NPS**: >50 (measure after 2 weeks of use)

### Cloud/API

- **API Calls**: 10,000/month by month 6
- **Paid Conversions**: 5% of active desktop users upgrade to Pro
- **MRR**: $1,000 by month 6, $5,000 by month 12

### Marketing

- **Landing Page**: 1,000 unique visitors/month by month 3
- **Conversion Rate**: 5% (visitors → downloads)
- **Blog Traffic**: 500 organic visitors/month by month 6
- **Social**: 500 Twitter followers, 100 GitHub stars by month 3

---

## Technology Stack Summary

### Desktop

- **Frontend**: PySide6 (Qt)
- **Backend (Local)**: FastAPI + SQLite
- **Image Processing**: OpenCV, Pillow, NumPy
- **OCR**: Tesseract (optional module)
- **Packaging**: PyInstaller / Nuitka

### Server/Cloud

- **Backend**: FastAPI + Postgres (or SQLite for simple deployment)
- **Container**: Docker
- **Hosting**: Fly.io / Railway / DigitalOcean
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry, Plausible

### Browser Extension

- **Tech**: WebExtension API (Chrome/Firefox/Edge)
- **Communication**: WebSocket or HTTP to localhost:8001 (desktop mode) or cloud API

### Integrations

- **E-Sign**: DocuSign REST API, HelloSign API
- **Automation**: Zapier, Make.com
- **Storage**: Google Drive API, Dropbox API
- **Messaging**: Slack API, Microsoft Teams API

---

## Risk Mitigation

### Technical Risks

- **Image Quality**: Some signatures too faint or blurry
  - _Mitigation_: Add pre-processing options (brightness, contrast, sharpen)
- **EXIF Orientation**: Not all images have correct EXIF tags
  - _Mitigation_: Manual rotate buttons as fallback
- **Performance**: Large images (>10MB) slow to process
  - _Mitigation_: Auto-downscale to 4K max; show progress spinner

### Business Risks

- **Low Adoption**: Users don't see value vs. free tools
  - _Mitigation_: Focus on speed + precision + privacy differentiation; offer free tier forever
- **Competition**: Adobe/Canva add similar feature
  - _Mitigation_: Go niche (signature extraction only); build integrations they won't; stay fast and focused
- **Pricing**: Hard to monetize desktop app
  - _Mitigation_: Freemium model; charge for cloud sync, browser extension, enterprise features

### Legal Risks

- **Copyright**: Users extract signatures from copyrighted documents
  - _Mitigation_: Terms of Service state tool is for personal/authorized use only
- **Privacy**: Images contain sensitive info
  - _Mitigation_: Local-first by default; clear privacy policy; no data retention on cloud

---

## Next Immediate Actions (This Sprint)

1. **Fix selection vs pan conflict** ✅ **COMPLETED** (Mode toggle button added)
2. **EXIF orientation handling** ✅ **COMPLETED** (Auto-rotate on load)
3. **Hide preview/result until selection** ✅ **COMPLETED** (Panes now hidden initially)
4. **White background for result view** ✅ **COMPLETED** (Improved visibility)
5. **Status bar with session ID** ✅ **COMPLETED** (Footer display with tooltips)
6. **Professional export dialog** ✅ **COMPLETED** (Format/background/trim options)
7. **Add app icon** → Use `QApplication.setWindowIcon()` with a custom icon
8. **Add button icons** → Use `QPushButton.setIcon()` with QIcon from resources
9. **Test rotate buttons** → Implement `Rotate CW/CCW` with PIL rotate + re-upload
10. **Export metadata dialog** → Add "Export Metadata" button that saves JSON
11. **Document REST API** → Create `docs/API.md` with endpoint specs for extension developers
12. **Create landing page mockup** → Sketch in Figma or use HTML template

---

**Status**: Living document. Updated as features ship and priorities shift.
**Owner**: Pranay
**Last Updated**: 2025-10-26
