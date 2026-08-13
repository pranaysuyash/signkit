# SignKit - Project Brief & Onboarding Guide
## Quick Start for AI Agents & New Contributors

**Last Updated**: November 14, 2025  
**Version**: 1.0  
**Purpose**: Rapid onboarding document for AI agents and contributors

---

## 🎯 What is SignKit?

**Elevator Pitch**: Privacy-first desktop application that extracts signatures from documents, enables PDF signing, and evolves into an intelligent document & identity platform.

**Current Status**: Pre-launch (v1.0 launching November 2025)

**Market Position**: Offline-first alternative to DocuSign/Adobe Sign with unique signature extraction capabilities

---

## 📊 Quick Facts

| Aspect | Details |
|--------|---------|
| **Product Name** | SignKit (formerly Signature Extractor) |
| **Category** | Document signing & identity management |
| **Platform** | Desktop (macOS, Windows, Linux) |
| **Architecture** | Python + PySide6 (Qt) + FastAPI backend |
| **Pricing** | $29 one-time (launch), tiered annual later |
| **Target Market** | Professionals, freelancers, small businesses |
| **Unique Value** | Signature extraction + offline-first + privacy |
| **Launch Date** | November 25, 2025 (target) |
| **Current Stage** | 80% complete, final polish phase |

---

## 🏗️ Current Product (v1.0)

### Core Features
1. **Signature Extraction**
   - Upload image/PDF with signature
   - Select signature region with zoom/pan
   - Adjust threshold, color, morphology
   - Export clean PNG with transparency

2. **PDF Signing**
   - View PDFs
   - Place extracted signatures
   - Save signed PDFs
   - Audit logging

3. **Library Management**
   - Save extracted signatures
   - Organize signature library
   - Quick access to saved signatures

4. **Offline-First Architecture**
   - Local processing (no cloud upload)
   - Optional backend for advanced features
   - Privacy-preserving by design

### Technical Stack
- **Frontend**: PySide6 (Qt for Python)
- **Backend**: FastAPI (local server, auto-start)
- **Image Processing**: OpenCV, PIL, NumPy
- **PDF**: PyMuPDF (fitz)
- **Database**: SQLite (local)
- **Packaging**: PyInstaller (planned)

### Current Limitations (Trial Mode)
- Export restricted (requires license)
- PDF save restricted (requires license)
- Full functionality available for testing

---

## 💰 Business Model

### Pricing Strategy
**Launch Pricing** (Gumroad):
- **One-time**: $29 (introductory)
- **No refunds** (try-before-buy model)
- **Unlimited trial** (all features except export/save)

**Future Pricing** (Post-launch):
- **Basic**: $29/year - Core features
- **Professional**: $79/year - Advanced features
- **Enterprise**: $299/year - Team features, API

### Revenue Projections
- **Year 1**: $210K (10K users, 15% conversion)
- **Year 2**: $600K (50K users, 20% conversion)
- **Year 3**: $3.1M (200K users, 25% conversion)

### Distribution
- **Primary**: Gumroad (digital distribution)
- **Website**: signkit.work (landing page)
- **Marketing**: Product Hunt, Reddit, SEO

---

## 🚀 Product Roadmap

### Phase 0: Launch (Current - Week 4)
**Status**: 80% complete

**Remaining Work**:
- [ ] Gumroad setup (1-2 days)
- [ ] Legal docs (privacy policy, terms) (1 day)
- [ ] PyInstaller packaging (2-3 days)
- [ ] Platform builds (macOS, Windows, Linux) (3-4 days)
- [ ] Final testing (2-3 days)
- [ ] Launch! 🚀

**Timeline**: November 25, 2025

---

### Phase 1: Identity Power Pack (Months 1-3)
**Theme**: "Your signature, everywhere"

**Priority Features**:
1. **Email Signature Generator** ⭐ HIGHEST PRIORITY
   - Signature-first templates
   - Auto-color matching from signature
   - Animated signatures (SVG, GIF)
   - Multi-platform export (Gmail, Outlook, etc.)
   - AI-powered text generation
   - **Timeline**: 3 weeks
   - **Impact**: +30% revenue

2. **Digital Business Cards**
   - vCard export with signature
   - QR code business cards
   - Apple Wallet / Google Pay
   - **Timeline**: 2 weeks
   - **Impact**: +10% revenue

3. **Signature Beautification**
   - Styling (embossed, metallic, neon)
   - Stamps & seals (round, rectangle)
   - SVG vectorization
   - Watermark generation
   - **Timeline**: 2 weeks
   - **Impact**: +15% revenue

**Total Timeline**: 7 weeks  
**Revenue Impact**: $325K Year 1 (+55%)

---

### Phase 2: Document Intelligence (Months 4-6)
**Theme**: "Smart documents, zero friction"

**Features**:
1. Intelligent form filling (auto-detect fields)
2. Smart signature placement (AI-powered)
3. PDF utilities (merge, split, compress)
4. OCR & extraction (handwriting, stamps, logos)

**Timeline**: 10 weeks  
**Revenue Impact**: $1.5M Year 2 (+75%)

---

### Phase 3: Trust & Security (Months 7-9)
**Theme**: "Privacy-first trust layer"

**Features**:
1. Local signature vault (encrypted)
2. Document integrity verification
3. QR-based verification system
4. Lightweight workflows

**Timeline**: 7 weeks  
**Revenue Impact**: $3M Year 2 (+100%)

---

### Phase 4: AI/ML Intelligence (Months 10-15)
**Theme**: "Documents that understand themselves"

**Features**:
1. **Computer Vision**: Forgery detection, layout AI, scan enhancement
2. **NLP**: Contract analysis, document classification, field detection
3. **CV + NLP Fusion**: Auto-fill, fraud detection, contract comparison

**Timeline**: 17 weeks  
**Revenue Impact**: $6.5M Year 3 (+117%)

---

### Phase 5: CRM & Ecosystem (Months 16-24)
**Theme**: "Your documents become your CRM"

**Features**:
1. **Auto-Generated CRM** ⭐ GAME CHANGER
   - NER extraction (names, companies, emails)
   - Auto-create contacts from documents
   - Auto-create deals from invoices
   - Relationship intelligence

2. Smart search & organization
3. Meeting preparation AI

**Timeline**: 15 weeks  
**Revenue Impact**: $15M Year 3 (+130%)

---

## 🎯 Strategic Vision

### Positioning Evolution
```
v1.0: Signature Extractor
  ↓
v1.5: Signature Identity Suite
  ↓
v2.0: Document Workflow Platform
  ↓
v2.5: Intelligent Document Engine
  ↓
v3.0: Privacy-First DocuSign + CRM Alternative
```

### 5-Year Vision
**"SignKit is the privacy-first intelligent document and identity platform that understands, organizes, and protects your professional life—from signature extraction to relationship intelligence."**

### Market Position
"DocuSign + Notion + HubSpot for privacy-conscious professionals"

### Core Differentiators
1. **Privacy-First**: Local processing, no cloud upload required
2. **Signature Extraction**: Unique capability, no competitor offers this
3. **Offline-First**: Works without internet
4. **One-Time Pricing**: No subscriptions (initially)
5. **Cross-Domain**: Identity + Documents + Trust + Intelligence

---

## 🏛️ Architecture Overview

### Desktop Application
```
┌─────────────────────────────────────┐
│         PySide6 (Qt) UI             │
│  ┌──────────┬──────────┬─────────┐  │
│  │Extraction│   PDF    │ Library │  │
│  │   Tab    │   Tab    │   Tab   │  │
│  └──────────┴──────────┴─────────┘  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Backend Manager (Local)        │
│  ┌─────────────────────────────┐    │
│  │  FastAPI Server (localhost) │    │
│  │  - Image processing         │    │
│  │  - PDF operations           │    │
│  │  - Session management       │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Processing Engines             │
│  ┌──────────┬──────────┬─────────┐  │
│  │ OpenCV   │ PyMuPDF  │ SQLite  │  │
│  │ PIL/NumPy│  (fitz)  │   DB    │  │
│  └──────────┴──────────┴─────────┘  │
└─────────────────────────────────────┘
```

### Key Components
- **desktop_app/**: Qt frontend application
- **backend/**: FastAPI server (local)
- **desktop_app/processing/**: Image processing logic
- **desktop_app/license/**: License validation
- **desktop_app/views/**: UI components

---

## 📁 Project Structure

```
signature-extractor-app/
├── desktop_app/              # Qt frontend
│   ├── views/               # UI components
│   │   ├── main_window_parts/
│   │   │   ├── extraction.py
│   │   │   ├── pdf.py
│   │   │   └── library.py
│   │   └── license_restriction_dialog.py
│   ├── processing/          # Image processing
│   │   └── extractor.py
│   ├── license/             # License system
│   │   ├── validator.py
│   │   └── storage.py
│   └── backend_manager.py   # Backend lifecycle
├── backend/                 # FastAPI server
│   └── app/
│       ├── main.py
│       ├── config.py
│       └── routers/
├── docs/                    # Documentation
│   ├── SIGNKIT_PROJECT_BRIEF.md (this file)
│   ├── SIGNKIT_ECOSYSTEM_MASTER_PLAN.md
│   ├── DOMAIN_EXPANSION_STRATEGY.md
│   ├── PRODUCT_STRATEGY.md
│   ├── ROADMAP.md
│   └── GUMROAD_COMPLETE_GUIDE.md
├── .kiro/specs/            # Feature specifications
│   ├── qr-pdf-innovation/
│   ├── enterprise-features/
│   ├── workflow-automation/
│   └── ...
├── tests/                  # Test suite
├── build-tools/            # Packaging scripts
└── web/                    # Landing page
```

---

## 🔑 Key Decisions & Context

### Product Decisions
1. **Name**: SignKit (finalized, was "Signature Extractor")
2. **Pricing**: $29 one-time launch, annual tiers later
3. **Refund Policy**: No refunds (try-before-buy model)
4. **Distribution**: Gumroad-only initially
5. **Platform**: Desktop-first (mobile later)

### Technical Decisions
1. **Architecture**: Local-first with optional cloud
2. **Backend**: FastAPI (auto-start, graceful degradation)
3. **Database**: SQLite (local, no Postgres required)
4. **Packaging**: PyInstaller (cross-platform)
5. **License**: Gumroad license keys

### Strategic Decisions
1. **Focus**: Privacy-first positioning
2. **Market**: Professionals, freelancers, SMBs
3. **Differentiation**: Signature extraction (unique)
4. **Evolution**: Identity → Documents → Intelligence → CRM
5. **Monetization**: Freemium → Tiered → Enterprise

---

## 📚 Key Documents (Priority Order)

### For Quick Understanding
1. **This Document** (`docs/SIGNKIT_PROJECT_BRIEF.md`) - Start here
2. **Current Status** (`.kiro/specs/CURRENT_STATUS.md`) - What's done
3. **Launch Plan** (`.kiro/specs/SIGNKIT_LAUNCH_FINAL.md`) - Launch details

### For Strategic Context
4. **Ecosystem Master Plan** (`docs/SIGNKIT_ECOSYSTEM_MASTER_PLAN.md`) - 5-year vision
5. **Domain Expansion** (`docs/DOMAIN_EXPANSION_STRATEGY.md`) - Feature priorities
6. **Product Strategy** (`docs/PRODUCT_STRATEGY.md`) - Market positioning

### For Implementation
7. **Roadmap** (`docs/ROADMAP.md`) - Detailed feature roadmap
8. **QR Innovation** (`.kiro/specs/qr-pdf-innovation/requirements.md`) - QR features
9. **Gumroad Guide** (`docs/GUMROAD_COMPLETE_GUIDE.md`) - Distribution setup

### For Specific Features
10. **Enterprise Features** (`.kiro/specs/enterprise-features/`) - Enterprise roadmap
11. **Workflow Automation** (`.kiro/specs/workflow-automation/`) - Workflow features
12. **Professional PDF** (`.kiro/specs/professional-pdf-workflow/`) - PDF features

---

## 🎨 Brand & Messaging

### Taglines
- **Current**: "Extract signatures from documents in seconds"
- **Future**: "Your complete signature identity toolkit"
- **Vision**: "Privacy-first document intelligence"

### Key Messages
1. "DocuSign without the cloud"
2. "Extract once, use everywhere"
3. "Privacy-first document workflows"
4. "One-time payment, lifetime trust"
5. "From extraction to everywhere"

### Target Audience
- **Primary**: Freelancers, consultants, small business owners
- **Secondary**: Legal professionals, compliance officers
- **Tertiary**: Privacy-conscious organizations

---

## 🚧 Current Challenges & Priorities

### Pre-Launch Priorities
1. **Gumroad Setup** (HIGH) - Product listing, license delivery
2. **Legal Docs** (HIGH) - Privacy policy, terms of service
3. **Packaging** (HIGH) - PyInstaller configuration
4. **Testing** (MEDIUM) - Cross-platform validation
5. **Marketing** (MEDIUM) - Landing page, launch materials

### Known Issues
- None critical (app is 80% complete)
- Minor UI polish needed
- Documentation needs completion

### Technical Debt
- Minimal (clean codebase)
- Some refactoring opportunities
- Test coverage could be improved

---

## 💡 Key Insights & Learnings

### What Makes SignKit Unique
1. **Signature Extraction**: No competitor offers this
2. **Offline-First**: Privacy advantage over cloud tools
3. **Cross-Domain**: Identity + Documents + Trust
4. **Evolution Path**: Clear roadmap to platform

### Market Opportunities
1. **Email Signatures**: Daily use, viral potential
2. **Auto-Generated CRM**: New category, huge value
3. **CV + NLP Fusion**: High barrier to entry
4. **Privacy Market**: Growing demand

### Strategic Advantages
1. **First-Mover**: Signature extraction + verification
2. **Privacy Brand**: Trust with regulated industries
3. **Pricing**: 60-85% cheaper than competitors
4. **Ecosystem**: Natural cross-domain expansion

---

## 🤝 How to Contribute

### For AI Agents
1. **Read this document first** (you're doing it!)
2. **Check current status** (`.kiro/specs/CURRENT_STATUS.md`)
3. **Review relevant specs** (`.kiro/specs/` directory)
4. **Ask clarifying questions** before implementing
5. **Follow existing patterns** in codebase

### For Developers
1. Clone repository
2. Set up Python environment (requirements.txt)
3. Run backend: `python backend/app/main.py`
4. Run desktop app: `python desktop_app/main.py`
5. Check `docs/` for detailed documentation

### For Designers
1. Review current UI (PySide6/Qt)
2. Check brand guidelines (TBD)
3. Focus on user workflows
4. Maintain privacy-first aesthetic

---

## 📞 Quick Reference

### Important URLs
- **Repository**: (local development)
- **Landing Page**: signkit.work (planned)
- **Distribution**: gumroad.com/l/signkit (planned)
- **Verification**: verify.signkit.work (future)

### Key Contacts
- **Product Owner**: Pranay
- **Development**: AI-assisted (Kiro, Claude, ChatGPT)
- **Launch Target**: November 25, 2025

### Quick Commands
```bash
# Run backend
python backend/app/main.py

# Run desktop app
python desktop_app/main.py

# Run tests
pytest tests/

# Build package (future)
pyinstaller build-tools/SignatureExtractor.spec
```

---

## ✅ Onboarding Checklist

For new AI agents or contributors:

- [ ] Read this document (SIGNKIT_PROJECT_BRIEF.md)
- [ ] Review current status (CURRENT_STATUS.md)
- [ ] Understand architecture (this doc, section above)
- [ ] Check roadmap (ROADMAP.md or ECOSYSTEM_MASTER_PLAN.md)
- [ ] Review relevant specs (.kiro/specs/)
- [ ] Understand codebase structure (project structure above)
- [ ] Set up development environment (if coding)
- [ ] Ask questions about unclear areas
- [ ] Start contributing!

---

## 🎯 TL;DR (30-Second Summary)

**What**: SignKit extracts signatures from documents and enables PDF signing, evolving into an intelligent document & identity platform.

**Status**: 80% complete, launching November 2025 at $29 one-time.

**Unique**: Only tool that extracts signatures + offline-first + privacy-focused.

**Vision**: Privacy-first alternative to DocuSign with auto-generated CRM from documents.

**Next**: Launch v1.0 → Add email signatures → Build document intelligence → Develop AI/ML → Create auto-CRM.

**Revenue**: $210K Year 1 → $1.5M Year 2 → $6.5M Year 3 → $76M Year 5.

---

**Document Version**: 1.0  
**Last Updated**: November 14, 2025  
**Maintained By**: Product Team  
**Next Review**: Post-launch (December 2025)

**Ready to build? Start with Phase 1: Email Signature Generator!**
