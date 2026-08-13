# Comprehensive Pre-Launch & Roadmap Review Prompt for LLM

## Context for LLM Review

You are a senior product manager with 15+ years of experience shipping successful B2C software products. You have deep expertise in:

- Mac app distribution and monetization
- Developer tools and productivity software
- Product-led growth strategies
- Launch execution and go-to-market
- Pricing psychology and positioning
- User onboarding and retention
- Roadmap prioritization

You are conducting a comprehensive pre-launch review of **Signature Extractor**, a native Mac app that extracts clean signatures from scanned documents. The product is planning to launch on Black Friday 2025 (November 29) at a promotional price of $19 (regular $29).

---

## Full Prompt to Give LLM

```
I need you to conduct an exhaustive, critical pre-launch review of my Mac app product and help me plan a roadmap. Act as an experienced product manager who has successfully launched 10+ software products. Be brutally honest - I want to identify gaps before launch, not after.

# PRODUCT OVERVIEW

**Name:** Signature Extractor
**Platform:** macOS (native app, PySide6/Qt6)
**Target Architectures:** Apple Silicon (ARM64) + Intel (x86_64)
**Price:** $29 one-time purchase (Black Friday launch: $19)
**Launch Date:** November 25-29, 2025 (Black Friday window)
**Distribution:** Gumroad (DMG download)

**Core Value Proposition:**
Extract professional-quality signatures from scanned documents with transparent backgrounds in seconds. Completely offline, privacy-first.

**Target Audience:**
- Real estate agents (contracts, forms)
- Small business owners (invoices, agreements)
- Freelancers/consultants (proposals, SOWs)
- Remote workers (digital paperwork)
- Anyone who needs to reuse their signature digitally

**Key Differentiators:**
1. Native Mac app (not web-based)
2. Completely offline (no cloud uploads)
3. One-click extraction with smart threshold
4. Professional PNG output with transparency
5. Built-in signature library and rotation tools
6. One-time payment (no subscription)

---

# YOUR MISSION

Review this product across 15 dimensions and provide:
1. **Critical assessment** (1-5 score, where 3+ is acceptable)
2. **Specific gaps or risks** that could sink the launch
3. **Actionable recommendations** (what to fix NOW vs post-launch)
4. **Roadmap priorities** for v1.1, v1.5, v2.0
5. **Launch readiness verdict** (GO / NO-GO / GO with risks)

---

# SECTION 1: FIRST-TIME USER EXPERIENCE (FTUE)

## Current Implementation

**Onboarding Dialog:**
- Welcome message with app overview
- Quick start guide (3 steps: Open → Select → Extract)
- License section with test license (pranay@example.com)
- "Enter License" button (green, primary CTA)
- "Buy License" button (opens Gumroad)
- Backend status indicator (auto-check)
- "Get Started" button to dismiss

**Main UI First Launch:**
- Empty state with helpful text: "Drag & drop an image or use File → Open"
- Menu bar with File, Edit, Help
- Toolbar visible but grayed out (no image loaded)

**First Extraction Flow:**
1. User drags image or clicks File → Open
2. Image loads in canvas with zoom controls
3. User drags rectangle around signature
4. "Extract Signature" button becomes active
5. Processing overlay with spinner
6. Extracted signature appears in right panel
7. Success message with export options

## Questions for Review

1. **Friction Analysis:**
   - Is the onboarding dialog too long/short?
   - Does the test license section confuse users? (Should it be hidden in production?)
   - Is the empty state compelling enough to drive action?
   - What % of users will complete first extraction? (Target: 70%+)

2. **Clarity:**
   - Is it immediately obvious what this app does?
   - Do users understand the selection → extraction → export flow?
   - Are the keyboard shortcuts discoverable?
   - Is the license model clear? (One-time $29, all v1.x updates)

3. **Delight Moments:**
   - Where can we add micro-interactions or animations?
   - What makes the first extraction feel magical?
   - How do we celebrate user's first successful export?

4. **Failure Recovery:**
   - What if their first image fails to extract?
   - What if backend doesn't start? (Already graceful, but is messaging clear?)
   - What if they draw selection incorrectly?

5. **Recommendations:**
   - What would you change about FTUE?
   - What should we A/B test?
   - What metrics should we track?

---

# SECTION 2: CORE FEATURES (MUST WORK FLAWLESSLY)

## Implemented Features

**1. Image Upload & Display:**
- Drag & drop from Finder
- File → Open dialog
- Supports: JPG, JPEG, PNG
- Security: Magic number validation, file size limits (50MB), dimension checks
- Image viewer: Zoom (scroll), pan (drag), fit-to-window

**2. Signature Selection:**
- Rectangle selection tool (click & drag)
- Visual feedback (red selection box)
- Adjustable handles (resize after drawing)
- Clear selection button
- Keyboard shortcut: Cmd+Shift+S to start selection

**3. Extraction Processing:**
- Multiple extraction modes:
  - Basic: Simple threshold extraction
  - Advanced: Smart threshold + rotation + cleanup
- Adjustable parameters:
  - Color (RGB sliders)
  - Threshold (1-255)
- Real-time preview (optional)
- Processing time: < 2 seconds for typical image

**4. Post-Extraction Tools:**
- Rotation: 0-360° with live preview
- Cleanup: Remove noise/artifacts
- Crop: Auto-crop to signature bounds
- Undo/Redo: Full history

**5. Signature Library:**
- Save extracted signatures with names
- Grid view with thumbnails
- Quick re-export from library
- Edit/delete saved signatures
- Persistent storage (SQLite)

**6. Export Options:**
- Format: PNG (with transparency)
- Resolution: Configurable DPI
- Destination: User-selected folder
- Auto-naming: SignatureExtract_YYYYMMDD_HHMMSS.png

**7. License System:**
- Email-based activation
- Online validation (with offline grace period)
- Test license: pranay@example.com (full access)
- Production: Gumroad license key delivery
- Restrictions: Export, library save require license

## Questions for Review

1. **Feature Completeness:**
   - Is anything critical missing for v1.0?
   - Are there half-baked features that should be removed?
   - What features are confusing or rarely used?

2. **Quality Bar:**
   - Do all features work reliably across different image types?
   - Are there edge cases that crash or fail?
   - Is the extraction quality "good enough" for professional use?

3. **Performance:**
   - Is < 2 seconds acceptable for extraction?
   - Does the app feel snappy on both Apple Silicon and Intel?
   - Are there memory leaks or performance degradation over time?

4. **Feature Priorities:**
   - Rank current features by importance (critical / nice-to-have / remove)
   - What would you cut to ship faster?
   - What would you delay to post-launch?

5. **Recommendations:**
   - What features need polish before launch?
   - What features should be highlighted in marketing?
   - What features are table stakes vs differentiators?

---

# SECTION 3: USER INTERFACE & DESIGN

## Current Design

**Visual Style:**
- Native Qt6 widgets with macOS styling
- Light mode only (no dark mode yet)
- Flat, minimal design
- Standard Mac menu bar
- Toolbar with icon buttons

**Layout:**
- Left panel: Image canvas (main area, ~70% width)
- Right panel: Extracted signature preview + controls (~30% width)
- Bottom status bar: Processing status, coordinates, zoom level

**Colors:**
- Primary: Red (#FF0000) for selection box
- Success: Green for buttons/status
- Neutral: Gray for disabled states
- Background: White/light gray

**Typography:**
- System font (SF Pro on macOS)
- Standard sizes: 12pt body, 14pt headings

**Iconography:**
- Mix of Qt built-in icons + custom SVGs
- Some placeholder icons (needs design pass)

## Questions for Review

1. **First Impressions:**
   - Does the app look professional?
   - Does it feel like a $29 product?
   - How does it compare to Mac App Store apps?

2. **Usability:**
   - Is the information hierarchy clear?
   - Are CTAs obvious and compelling?
   - Can users complete tasks without hunting for controls?

3. **Visual Consistency:**
   - Are colors used consistently?
   - Do button styles match across the app?
   - Are spacing and padding consistent?

4. **Accessibility:**
   - Are text sizes readable?
   - Is color contrast sufficient?
   - Are keyboard shortcuts complete?

5. **Dark Mode:**
   - Should dark mode be in v1.0? (Currently not implemented)
   - Would lack of dark mode prevent purchase?

6. **Recommendations:**
   - What's the biggest UI/UX weakness?
   - What would a professional designer fix first?
   - What quick wins could improve perceived quality?

---

# SECTION 4: USER FLOWS (CRITICAL PATHS)

## Key User Journeys

**Flow 1: First-Time User → First Extraction (10 minutes)**
1. Download DMG from Gumroad (post-purchase)
2. Open DMG, drag app to Applications
3. Launch app, macOS security prompt (Right-click → Open)
4. Onboarding dialog appears
5. Read quick start, see test license
6. Click "Get Started"
7. Main window loads (empty state)
8. Drag image from Finder onto app
9. Image loads and displays
10. Draw rectangle around signature
11. Click "Extract Signature"
12. Processing (2 seconds)
13. Signature appears in right panel
14. Click "Export" → choose location → save
15. Success! (File exported to ~/Desktop)

**Flow 2: Repeat User → Quick Extraction (30 seconds)**
1. Launch app (no onboarding)
2. Cmd+O to open file dialog
3. Select image
4. Cmd+Shift+S to start selection
5. Draw selection box
6. Return key to extract
7. Cmd+E to export (remembers last location)
8. Done

**Flow 3: Library Management (5 minutes)**
1. Extract signature
2. Click "Save to Library"
3. Enter name (e.g., "Personal", "Business")
4. Signature saved
5. Later: Click "Library" tab
6. Grid of saved signatures appears
7. Click signature to reload
8. Quick re-export without re-extracting

**Flow 4: License Activation (2 minutes)**
1. User purchases on Gumroad ($29)
2. Receives email with license key
3. In app: Help → Enter License Key
4. Paste email (pranay@example.com for test)
5. Click "Activate"
6. Online validation (2 seconds)
7. Success message
8. All features unlocked

**Flow 5: Troubleshooting Extraction (5 minutes)**
1. Extract signature, but quality is poor
2. Click "Advanced Options"
3. Adjust threshold slider (trial and error)
4. Click "Re-extract" to preview
5. Adjust color if needed (RGB sliders)
6. Satisfied with result
7. Click "Extract Signature"
8. Export

## Questions for Review

1. **Friction Points:**
   - Where do users get stuck or confused?
   - Which steps take longer than expected?
   - What causes users to abandon the flow?

2. **Error Handling:**
   - What happens if extraction fails?
   - How do users recover from mistakes?
   - Are error messages helpful or cryptic?

3. **Efficiency:**
   - Can power users complete tasks faster?
   - Are keyboard shortcuts sufficient?
   - Are there unnecessary clicks?

4. **Discoverability:**
   - Do users find advanced features?
   - Is the library feature obvious?
   - How do users learn about keyboard shortcuts?

5. **Recommendations:**
   - Which flow is most fragile?
   - What should be automated?
   - What inline help or tooltips are needed?

---

# SECTION 5: ADVANCED FEATURES (DIFFERENTIATION)

## Current Advanced Features

**1. Batch Processing:**
- ❌ Not implemented (v1.0)
- 📋 Roadmap for v1.1

**2. PDF Support:**
- ❌ Not implemented (v1.0)
- 📋 Roadmap for v1.1

**3. Auto-Detection (AI/ML):**
- ❌ Not implemented
- 📋 Research item for v2.0

**4. Cloud Sync:**
- ❌ Not implemented (offline-only)
- 📋 Maybe v2.0 (conflicts with privacy-first positioning)

**5. Preset Styles:**
- ❌ Not implemented
- 📋 Save extraction settings as presets (v1.1?)

**6. Integration (Dropbox, Drive, etc.):**
- ❌ Not implemented
- 📋 Low priority

## Questions for Review

1. **MVP vs Bloat:**
   - Is v1.0 too minimal or appropriately focused?
   - Are we shipping too early or too late?
   - What would make this a "must-have" vs "nice-to-have"?

2. **Competitive Analysis:**
   - What do competitors have that we don't?
   - What gaps leave us vulnerable?
   - What features would make us un-competitive?

3. **User Expectations:**
   - Do users expect batch processing in v1.0?
   - Is lack of PDF support a deal-breaker?
   - Would users pay $29 for current feature set?

4. **Technical Feasibility:**
   - Which roadmap items are easy wins?
   - Which require significant R&D?
   - What's the LOE for each feature?

5. **Recommendations:**
   - What should be in v1.0 that isn't?
   - What should be cut from roadmap?
   - What's the killer feature for v2.0?

---

# SECTION 6: PERFORMANCE & RELIABILITY

## Current Status

**App Launch Time:**
- Cold start: ~3-4 seconds (backend auto-start)
- Warm start: ~1-2 seconds

**Backend:**
- FastAPI server on localhost:8001
- Auto-starts with app (subprocess)
- Graceful fallback if offline
- SQLite database (local storage)

**Image Processing:**
- Upload: < 1 second (local file copy)
- Extraction: 1-3 seconds (depends on image size)
- Export: < 1 second

**Memory Usage:**
- Idle: ~150MB
- Processing large image: ~300MB
- Backend: ~100MB

**Stability:**
- Crash rate: Unknown (no telemetry yet)
- Known bugs: None blocking (as of Nov 13, 2025)

**Edge Cases:**
- Large images (>50MB): Rejected by security validator
- Unsupported formats: TIFF, BMP (not yet supported)
- Malformed files: Caught by magic number check

## Questions for Review

1. **Performance Benchmarks:**
   - Is 3-4 second cold start acceptable?
   - Is 1-3 second extraction fast enough?
   - What's the target for "feels instant"?

2. **Reliability:**
   - What's the acceptable crash rate? (Target: < 1% sessions)
   - How do we test stability across macOS versions?
   - What error handling is missing?

3. **Scalability:**
   - Can the app handle 100+ images in library?
   - Does performance degrade over time?
   - Are there memory leaks?

4. **Compatibility:**
   - What macOS versions are supported? (Currently: 10.15+)
   - Does it work on both Apple Silicon and Intel?
   - What about Rosetta 2 translation?

5. **Recommendations:**
   - What's the biggest performance bottleneck?
   - Should we add telemetry/crash reporting? (Privacy concerns)
   - What stress testing is needed before launch?

---

# SECTION 7: HELP & DOCUMENTATION

## Current Documentation

**In-App:**
- Onboarding dialog with quick start
- Help menu with links:
  - User Guide (opens docs/USER_GUIDE.md in browser)
  - Keyboard Shortcuts (shows modal)
  - Enter License Key (opens dialog)
  - Check for Updates (manual check)
  - About (version info)

**External:**
- docs/USER_GUIDE.md (~200 lines)
  - Quick Start
  - Opening Images
  - Extracting Signatures
  - Using Library
  - Keyboard Shortcuts
  - Troubleshooting
  - System Requirements
  - Privacy & Security
  - License Info

- README.md (GitHub, not for end users)

**Support:**
- No in-app support chat
- No FAQ page (yet)
- Contact: Email only (pranay@example.com - placeholder)

**Video Tutorials:**
- ❌ None yet
- 📋 30-second demo video planned for launch

## Questions for Review

1. **Self-Service:**
   - Can users solve common problems without contacting support?
   - Are error messages helpful enough?
   - Is the user guide comprehensive?

2. **Discoverability:**
   - Do users know the Help menu exists?
   - Are keyboard shortcuts easy to find?
   - Should there be in-app tooltips?

3. **Support Readiness:**
   - What are the top 10 likely support questions?
   - Do we have canned responses ready?
   - What's the expected support load? (Target: < 5% of users)

4. **Video Content:**
   - Is a 30-second demo enough?
   - Should there be a full tutorial (2-3 minutes)?
   - What should be shown in videos?

5. **Recommendations:**
   - What documentation is missing?
   - Should there be in-app contextual help?
   - What's the support channel strategy?

---

# SECTION 8: BUSINESS MODEL & PRICING

## Current Model

**Pricing:**
- Regular: $29 one-time payment
- Black Friday Launch: $19 (save $10)
- Deal Duration: Nov 25 - Dec 2, 2025 (8 days)

**License Structure:**
- Email-based activation
- Single-user license (1 Mac)
- All v1.x updates included forever (1.0 → 1.99)
- v2.0 = separate product ($39 regular or $19 upgrade)

**Payment Processing:**
- Gumroad (10% fee + Stripe fees)
- Automated license delivery via email
- No trial period (screenshots + demo video pre-purchase)

**Revenue Model:**
- One-time sales only
- No subscription
- No freemium tier
- No in-app purchases

**Target Market Size:**
- Mac users: ~100M worldwide
- Addressable: ~5% (need signature extraction) = 5M
- Realistic TAM: 1% = 50k potential customers

**Financial Goals:**
- Year 1: 500 customers = $14,500 revenue
- Break-even: ~50 sales (covers dev time at minimum wage)
- Success: 1,000+ customers = $29,000+ revenue

## Questions for Review

1. **Price Sensitivity:**
   - Is $29 the right price point?
   - Should it be higher ($39-49) or lower ($19-24)?
   - How does $19 launch discount affect perceived value?

2. **Competitive Pricing:**
   - What do competitors charge?
   - Are we priced premium, mid-tier, or budget?
   - Does one-time payment vs subscription matter?

3. **Discount Strategy:**
   - Is $10 off enough for Black Friday?
   - Should discount be steeper (50% = $14.50)?
   - Will $19 cannibalize $29 sales post-launch?

4. **Licensing Model:**
   - Is single-user enough, or should we offer multi-user/team?
   - Should there be a "lifetime all versions" tier?
   - Is email-based activation friction or necessary protection?

5. **Monetization Opportunities:**
   - Should there be a free trial (7-14 days)?
   - Should there be a "lite" version (limited exports)?
   - Could this be a subscription ($4.99/month)?

6. **Market Size:**
   - Is TAM too small to be viable?
   - Are we targeting the right audience?
   - How do we expand beyond initial niche?

7. **Recommendations:**
   - What's the optimal pricing strategy?
   - Should we A/B test prices?
   - What payment options are critical? (PayPal, Apple Pay?)

---

# SECTION 9: DISTRIBUTION & INSTALLATION

## Current Plan

**Distribution Channel:**
- Primary: Gumroad (direct sales)
- Future: Mac App Store? (Not for v1.0)

**Packaging:**
- Format: DMG (disk image)
- Architectures: 2 separate DMGs
  - SignatureExtractor_ARM64.dmg (Apple Silicon)
  - SignatureExtractor_Intel.dmg (Intel)
- Size: ~145MB compressed (DMG), ~323MB uncompressed (app bundle)

**Installation:**
1. User downloads DMG from Gumroad
2. Opens DMG (mounts as virtual disk)
3. Drags app to Applications folder
4. Ejects DMG
5. Launches app from Applications
6. macOS security: "App from unidentified developer"
7. User must Right-click → Open (first time only)

**Code Signing:**
- ❌ Not currently signed with Apple Developer cert
- ⚠️ Users see security warning
- 📋 Planned: Sign with Developer ID before launch

**Notarization:**
- ❌ Not notarized
- ⚠️ macOS 10.15+ shows scary warning
- 📋 Must notarize before launch (critical)

**Auto-Updates:**
- ❌ Not implemented (v1.0)
- Manual: Users check Help → Check for Updates
- 📋 Future: Sparkle framework for auto-updates (v1.1+)

## Questions for Review

1. **Installation Friction:**
   - Is DMG install too complicated?
   - Should we provide a .pkg installer instead?
   - Will users understand the security warning?

2. **Code Signing:**
   - Is unsigned app a deal-breaker?
   - What % of users will abandon at security warning?
   - Should signing be done before launch? (YES!)

3. **Notarization:**
   - Is notarization mandatory for v1.0? (YES!)
   - What's the process and timeline? (1-2 days)
   - What's the cost? ($99/year Apple Developer Program)

4. **Distribution Strategy:**
   - Should we launch on Mac App Store too?
   - Gumroad pros/cons vs other platforms?
   - Should there be a direct website store?

5. **Updates:**
   - How do users learn about updates?
   - Is manual update check acceptable for v1.0?
   - What's the priority for auto-updates?

6. **Architecture Confusion:**
   - Will users know which DMG to download?
   - Should we auto-detect and serve correct DMG?
   - Should there be a "universal binary" (fatter file)?

7. **Recommendations:**
   - What's blocking launch re: distribution?
   - What's the minimum viable install experience?
   - What can wait until post-launch?

---

# SECTION 10: MARKETING & POSITIONING

## Current Positioning

**Tagline:** "Professional Signature Extraction for Mac"

**Value Props:**
1. Extract clean signatures from scanned documents
2. Perfect transparency in seconds
3. Completely offline - your signatures never leave your Mac
4. One-click extraction with smart threshold
5. Built-in library and rotation tools

**Target Personas:**

**Persona 1: Real Estate Agent Rachel**
- Age: 35-50
- Pain: Constantly needs to sign contracts, often from phone photos
- Use Case: Extract signature from license scan, reuse on PDFs
- Budget: Will pay $29 if it saves 10 minutes/week

**Persona 2: Freelance Consultant Frank**
- Age: 28-45
- Pain: Clients need wet signatures on proposals
- Use Case: Scan handwritten signature, digitize for proposals
- Budget: Expects free or cheap tool

**Persona 3: Small Business Owner Sam**
- Age: 40-60
- Pain: Invoices, contracts need signatures, no time for DocuSign
- Use Case: Quick signature extraction for ad-hoc documents
- Budget: $29 is impulse buy if it "just works"

**Competitive Positioning:**

| Product | Price | Online/Offline | Platform | Differentiator |
|---------|-------|----------------|----------|----------------|
| **Signature Extractor** | $29 | Offline | Mac only | Privacy, native, one-time |
| Adobe Acrobat DC | $19.99/mo | Online | Cross-platform | Industry standard, features |
| Preview (Mac) | Free | Offline | Mac only | Built-in, basic tools |
| Docusign | $10-45/mo | Online | Cross-platform | E-signature workflow |
| SignNow | $8-30/mo | Online | Cross-platform | Cheaper than Docusign |

**Why We Win:**
- One-time payment (vs subscription fatigue)
- Privacy-first (offline processing)
- Native Mac experience (fast, reliable)
- Specialized tool (does one thing well)

**Why We Lose:**
- Not cross-platform (Windows, web)
- No collaboration features
- No full PDF editing
- Unknown brand

## Questions for Review

1. **Positioning Clarity:**
   - Is "Professional Signature Extraction" clear enough?
   - Does target audience immediately understand value?
   - Is "offline/privacy" a strong enough differentiator?

2. **Messaging:**
   - What's the most compelling benefit?
   - Should we lead with speed, quality, or privacy?
   - Do we emphasize "Mac-native" or downplay platform limitation?

3. **Persona Fit:**
   - Are these the right target personas?
   - Which persona is most likely to buy?
   - Should we focus on one persona for launch?

4. **Competitive Threats:**
   - What if Adobe bundles this feature?
   - What if Preview (free) adds signature extraction?
   - How do we compete with "good enough" free tools?

5. **Brand Perception:**
   - Does "Signature Extractor" feel premium?
   - Should the app have a more creative name?
   - What imagery/colors convey trustworthiness?

6. **Launch Messaging:**
   - What headline converts best for Black Friday?
     - A) "Save $10: Professional Signature Extraction"
     - B) "Launch Special: Extract Signatures in Seconds"
     - C) "Black Friday: The Best Signature Tool for Mac"

7. **Recommendations:**
   - What's the biggest positioning weakness?
   - What messaging tests should we run?
   - What's the ideal elevator pitch (10 words)?

---

# SECTION 11: LAUNCH PLAN (BLACK FRIDAY)

## Current Strategy

**Launch Date:** November 25-29, 2025
**Deal:** $19 (save $10 off $29)
**Duration:** Nov 25 (Mon) - Dec 2 (Mon) - 8 days

**Primary Channels:**
1. **Product Hunt** (Tuesday Nov 26)
   - 30-second demo video
   - Compelling description
   - Active engagement in comments
   - Goal: Top 10 product of the day

2. **Reddit** (Nov 25-29)
   - r/macapps (Show & Tell)
   - r/productivity (tool discussion)
   - r/MacOS (apps & tools)
   - Authentic posts, not spammy

3. **Twitter/X** (ongoing)
   - Thread with demo GIF
   - Engage with Mac community
   - Black Friday hashtags

4. **Black Friday Deal Sites**
   - AppSumo, StackSocial, RetailMeNot
   - Submit by Nov 20 deadline

**Marketing Assets:**
- ✅ 30-second demo video (planned)
- ✅ Landing page on Gumroad
- ✅ Screenshots (5 key shots)
- ✅ User guide (docs/)
- ❌ Press kit (not yet)
- ❌ Testimonials (need beta users)

**Success Metrics:**
- Minimum: 50 sales @ $19 = $950
- Good: 150 sales @ $19 = $2,850
- Excellent: 300+ sales @ $19 = $5,700+

**Backup Plans:**
- If Product Hunt flops: Double down on Reddit
- If Black Friday noise too loud: Extend to Dec 15
- If no sales: Emergency price drop to $14.99

## Questions for Review

1. **Timing:**
   - Is 15 days enough to prepare?
   - Should we launch before BF (Nov 20) to build momentum?
   - Should we skip BF and launch in January?

2. **Channel Strategy:**
   - Are Product Hunt, Reddit, Twitter enough?
   - Should we invest in paid ads ($100-500)?
   - What channels are we missing?

3. **Pricing:**
   - Is $19 the right Black Friday price?
   - Should we go deeper (50% off = $14.50)?
   - Will $10 discount move the needle?

4. **Assets:**
   - Is a 30-second video sufficient?
   - Do we need customer testimonials for launch?
   - Should there be a landing page (vs direct to Gumroad)?

5. **Risk Management:**
   - What if we get 0 sales on launch day?
   - What if Product Hunt bans the post?
   - What if Gumroad goes down?

6. **Post-Launch:**
   - What's the plan for Dec 3-31?
   - Should there be a "Holiday Special" at $24?
   - When do we raise to full $29?

7. **Recommendations:**
   - What's the biggest launch risk?
   - What quick wins could boost launch success?
   - Should we delay launch to February?

---

# SECTION 12: COMPETITIVE ANALYSIS

## Key Competitors

**1. Adobe Acrobat DC**
- Price: $19.99/month subscription
- Features: Full PDF editing, e-signatures, cloud sync
- Strengths: Industry standard, trusted brand, feature-rich
- Weaknesses: Expensive over time, subscription, bloated

**2. macOS Preview (Free)**
- Price: Free (built-in)
- Features: Basic PDF editing, signature from trackpad/camera
- Strengths: Free, built-in, "good enough" for many
- Weaknesses: Limited tools, no batch, manual process

**3. DocuSign / SignNow**
- Price: $10-45/month subscription
- Features: E-signature workflows, team collaboration, compliance
- Strengths: Full e-signature solution, integrations
- Weaknesses: Overkill for personal use, expensive, online-only

**4. PDF Expert (Readdle)**
- Price: $89.99 one-time or $9.99/month
- Features: PDF editing, annotations, form filling, signatures
- Strengths: Native Mac/iOS, one-time option, polished UI
- Weaknesses: Expensive, signature extraction not core feature

**5. Online Tools (Smallpdf, ILovePDF, etc.)**
- Price: Free (limited) or $9/month
- Features: Web-based PDF tools including signature extraction
- Strengths: No download, cross-platform, cheap
- Weaknesses: Privacy concerns, upload required, internet-dependent

## Questions for Review

1. **Competitive Threats:**
   - Which competitor is most dangerous?
   - What would make Preview "good enough" to kill us?
   - Could Adobe add this feature and destroy our market?

2. **Differentiation:**
   - Is "offline/privacy" enough differentiation?
   - Is "one-time payment" compelling vs subscription?
   - Are we differentiated or just a niche tool?

3. **Feature Gaps:**
   - What do competitors have that we critically lack?
   - What features keep users on Adobe/Preview?
   - Should we add PDF editing to compete?

4. **Pricing Comparison:**
   - Is $29 competitive with $20/month (Acrobat)?
   - Does one-time payment justify higher upfront cost?
   - Are we priced too high or too low vs competitors?

5. **Market Position:**
   - Are we a "substitute" or "complement" to competitors?
   - Do users need Signature Extractor + Adobe, or either/or?
   - Should we position as "Adobe alternative" or "specialist tool"?

6. **Moats:**
   - What prevents competitors from copying us?
   - What would make us defensible long-term?
   - Is this a sustainable business or a feature?

7. **Recommendations:**
   - Who should we explicitly compare against in marketing?
   - What competitive FUD should we address preemptively?
   - Should we offer head-to-head comparison page?

---

# SECTION 13: LEGAL & COMPLIANCE

## Current Status

**Terms of Service:**
- ❌ Not yet written
- 📋 Needed before launch

**Privacy Policy:**
- ❌ Not yet written
- 📋 Needed before launch (even for offline app)

**GDPR Compliance:**
- Email collection for license (Gumroad handles)
- No user tracking/analytics in app (privacy-first)
- No cookies (offline app)

**CCPA Compliance:**
- Same as GDPR (minimal data collection)

**License Agreement:**
- ✅ Single-user license model documented
- ❌ No formal EULA text yet

**Intellectual Property:**
- App name: "Signature Extractor" (generic, not trademarked)
- Logo/icon: Custom (no infringement)
- Code: Original (PySide6, OpenCV - open source libs used)

**Export Restrictions:**
- No encryption beyond standard HTTPS
- No export controls apply

**Liability:**
- What if extracted signature used for fraud?
- Disclaimer needed: "Not for legal authentication"

## Questions for Review

1. **Legal Blockers:**
   - Can we launch without Terms of Service?
   - Can we launch without Privacy Policy?
   - What's legally required vs best practice?

2. **Liability Risks:**
   - What if someone uses extracted signature maliciously?
   - What if app corrupts user's files?
   - What disclaimers are needed?

3. **Data Privacy:**
   - Even offline app needs Privacy Policy?
   - What about license validation (sends email to server)?
   - Should we add telemetry? (Privacy concerns)

4. **Intellectual Property:**
   - Should we trademark "Signature Extractor"?
   - Are there existing trademarks we're infringing?
   - Should we copyright the icon/logo?

5. **Compliance:**
   - What about GDPR "right to be forgotten"?
   - What about refund policy on Gumroad?
   - What about accessibility laws (ADA)?

6. **Recommendations:**
   - What legal docs are mandatory before launch?
   - Should we hire a lawyer or use templates?
   - What's the biggest legal risk?

---

# SECTION 14: ANALYTICS & METRICS

## Current Tracking

**In-App Analytics:**
- ❌ None implemented (privacy-first positioning)
- No crash reporting
- No usage telemetry
- No feature usage tracking

**External Analytics:**
- Gumroad sales data (purchases, refunds)
- Product Hunt votes/comments (manual)
- Reddit post engagement (manual)
- Twitter impressions (native analytics)

**Success Metrics (Defined):**
- Launch week sales (target: 50-150)
- Year 1 customers (target: 500)
- Product Hunt rank (target: Top 10)
- Customer satisfaction (target: 4.5+ stars)

**User Behavior (Unknown):**
- % who complete onboarding
- % who complete first extraction
- % who purchase vs test with test license
- % who use library feature
- % who use rotation feature
- Average session length
- Crash rate

## Questions for Review

1. **Analytics Strategy:**
   - Should we add opt-in telemetry for product improvement?
   - Can we balance privacy-first + data-driven decisions?
   - What's the minimum data needed to improve product?

2. **Key Metrics:**
   - What are the 5 most important metrics to track?
   - How do we measure product success beyond revenue?
   - What metrics predict churn or satisfaction?

3. **Privacy Trade-offs:**
   - Does "no analytics" hurt product development?
   - Would users accept opt-in telemetry?
   - Should we use privacy-preserving analytics (differential privacy)?

4. **User Feedback:**
   - How do we collect qualitative feedback?
   - Should there be in-app NPS or feedback form?
   - What's the plan for user interviews?

5. **Experimentation:**
   - How do we A/B test without analytics?
   - Should we have separate builds for testing?
   - What's the strategy for feature validation?

6. **Recommendations:**
   - What's the minimum viable analytics setup?
   - Should we add crash reporting at least? (Privacy-safe)
   - What tools respect privacy? (PostHog, Plausible, etc.)

---

# SECTION 15: ROADMAP (v1.1, v1.5, v2.0)

## Current Roadmap Ideas

**v1.1 (1-2 months post-launch):**
- [ ] Batch processing (extract from multiple images)
- [ ] PDF support (extract from PDF pages)
- [ ] Preset styles (save extraction settings)
- [ ] Dark mode
- [ ] Auto-updates (Sparkle framework)

**v1.5 (3-6 months):**
- [ ] Advanced cleanup tools (noise reduction, sharpening)
- [ ] Signature comparison (find duplicates)
- [ ] Export to multiple formats (SVG, JPEG)
- [ ] Keyboard shortcut customization
- [ ] Improved library (search, tags, sorting)

**v2.0 (12-18 months):**
- [ ] Auto-detection (AI/ML finds signatures automatically)
- [ ] Form filling (place signature in PDF forms)
- [ ] Multi-user licenses (team/business pricing)
- [ ] Cloud sync (optional, for library)
- [ ] Windows/Linux ports (cross-platform)

**Unscheduled Ideas:**
- Handwriting extraction (expand beyond signatures)
- Logo extraction (similar use case)
- Integration with DocuSign, Adobe Sign (export to services)
- Mobile app (iOS companion for capture)

## Questions for Review

1. **Prioritization:**
   - What features should be in v1.1?
   - What can wait until v1.5 or v2.0?
   - What features would drive most sales?

2. **Customer Demand:**
   - What are users asking for most?
   - What features increase retention?
   - What features are "nice to have" vs "must have"?

3. **Technical Feasibility:**
   - What's easy to build vs hard?
   - What requires R&D vs implementation?
   - What's the LOE for each feature?

4. **Strategic Fit:**
   - What features align with "offline/privacy" positioning?
   - What features conflict with positioning?
   - Should we expand scope or stay focused?

5. **v2.0 Pricing:**
   - Should v2.0 be a separate product?
   - Should there be an upgrade discount for v1 users?
   - What justifies v2 pricing vs free update?

6. **Platform Expansion:**
   - Should we build for Windows?
   - Should there be a web version?
   - Would cross-platform dilute Mac-native positioning?

7. **Recommendations:**
   - What's the killer feature for v1.1?
   - What features should be cut from roadmap?
   - What's the vision for v2.0?

---

# SECTION 16: LAUNCH READINESS (GO/NO-GO DECISION)

## Final Questions

1. **Product Quality:**
   - Is the product stable enough for launch?
   - Are there known critical bugs?
   - Would you personally pay $29 for this?

2. **Market Timing:**
   - Is Black Friday the right time?
   - Is 15 days enough preparation?
   - Should we delay to January?

3. **Distribution Readiness:**
   - Is lack of code signing/notarization blocking?
   - Is DMG the right format?
   - Is installation friction acceptable?

4. **Marketing Readiness:**
   - Do we have enough marketing assets?
   - Is the messaging compelling?
   - Are launch channels sufficient?

5. **Support Readiness:**
   - Can we handle 50-500 customers?
   - Are docs good enough for self-service?
   - What's the support plan?

6. **Business Readiness:**
   - Is pricing tested and validated?
   - Is Gumroad setup complete?
   - Are legal docs ready?

7. **Personal Readiness:**
   - Are you emotionally ready to launch?
   - Do you have time for launch week intensity?
   - What's your backup plan if it fails?

## Scoring (1-5 Scale)

For each of the 15 sections above, provide:
- **Score:** 1 (poor) to 5 (excellent)
- **Confidence:** Low / Medium / High
- **Top 3 Risks:** What could go wrong?
- **Top 3 Fixes:** What to improve before launch?

## Final Recommendation

**Option 1: GO (Launch Nov 25-29)**
- Pros: [Your analysis]
- Cons: [Your analysis]
- Conditions: [What must be fixed]

**Option 2: NO-GO (Delay to January)**
- Pros: [Your analysis]
- Cons: [Your analysis]
- Conditions: [What to complete before next attempt]

**Option 3: SOFT LAUNCH (Beta Launch, Not Public)**
- Pros: [Your analysis]
- Cons: [Your analysis]
- Conditions: [How to execute]

---

# YOUR DELIVERABLES

Please provide:

## 1. EXECUTIVE SUMMARY (200-300 words)
- Overall assessment of product
- Top 3 strengths
- Top 3 critical gaps
- Launch recommendation (GO / NO-GO / SOFT LAUNCH)

## 2. SECTION-BY-SECTION REVIEW
For each of 15 sections:
- Score (1-5)
- Confidence level
- Key findings (3-5 bullet points)
- Top 3 risks
- Top 3 actionable fixes

## 3. LAUNCH READINESS SCORECARD
- Total score (out of 75)
- Pass/fail on critical dimensions
- Must-fix items for launch
- Nice-to-have improvements

## 4. PRIORITIZED ROADMAP
- v1.0 launch: What must be done NOW
- v1.1 (1-2 months): Top 5 features
- v1.5 (3-6 months): Top 5 features
- v2.0 (12+ months): Vision + pricing

## 5. CRITICAL PATH TO LAUNCH
- Day-by-day plan (Nov 13-25)
- Must-complete tasks
- Parallel tracks
- Decision points
- Go/no-go gates

## 6. POST-LAUNCH PLAN (First 30 Days)
- Week 1: Launch execution
- Week 2-4: Monitoring and iteration
- Success metrics
- Failure mitigation

## 7. PRICING & POSITIONING RECOMMENDATION
- Optimal pricing strategy
- Launch discount recommendation
- Messaging framework
- Competitive positioning

## 8. RISK REGISTER
- Top 10 risks to launch
- Probability (1-5)
- Impact (1-5)
- Mitigation strategy

## 9. BLACK FRIDAY STRATEGY REVIEW
- Evaluate existing BLACK_FRIDAY_STRATEGY.md
- Additions/modifications recommended
- Channel priority ranking
- Expected ROI per channel

## 10. LONG-TERM STRATEGIC QUESTIONS
- Is this a feature or a product?
- Is $29 one-time sustainable?
- Should this be subscription?
- Should this be cross-platform?
- What's the 3-year vision?
- Exit strategy (acquire, scale, maintain)?

---

# CONTEXT TO ANALYZE

Please review these documents from the project:

## Core Documents:
1. `.github/copilot-instructions.md` - Repository overview
2. `docs/PRODUCT_REVIEW_CHECKLIST.md` - Product review framework
3. `docs/BLACK_FRIDAY_STRATEGY.md` - Launch strategy
4. `docs/VERSIONING_AND_UPDATES.md` - Versioning model
5. `docs/USER_GUIDE.md` - End-user documentation
6. `TESTING_GUIDE.md` - Testing checklist
7. `DISTRIBUTION_STRATEGY.md` - Distribution plan

## Code to Review (Key Files):
1. `desktop_app/main.py` - App entry point
2. `desktop_app/views/main_window.py` - Main UI
3. `desktop_app/views/onboarding_dialog.py` - FTUE
4. `desktop_app/processing/extractor.py` - Core extraction logic
5. `desktop_app/widgets/image_view.py` - Image display + drag-drop
6. `backend/app/main.py` - Backend API
7. `build-tools/SignatureExtractor_macOS.spec` - Build config

---

# FINAL INSTRUCTIONS

Be **brutally honest**. I want to know what will cause the launch to fail. I want to identify blind spots, not get validation.

Focus on:
- **What's missing** (gaps that will hurt us)
- **What's confusing** (users will struggle)
- **What's risky** (could blow up launch)
- **What's wrong** (bad decisions made)

Don't sugarcoat. If something is bad, say it's bad. If pricing is wrong, say so. If we should delay launch, say so.

Your goal: Help me launch successfully or convince me to delay if not ready.

**Word count target:** 5,000-10,000 words (be thorough)
**Tone:** Senior PM giving tough love to junior founder
**Format:** Markdown with clear headings and bullet points
```

---

## How to Use This Prompt

### Option 1: Claude/ChatGPT (Full Context)

1. Copy entire prompt above
2. Paste into Claude (Opus/Sonnet) or GPT-4
3. Attach all documents listed in "Context to Analyze" section
4. Wait for comprehensive review (may take 2-3 minutes to generate)

### Option 2: Iterative Review (Sections 1-5, then 6-10, etc.)

If hitting token limits, break into chunks:

- **Chunk 1:** FTUE, Core Features, UI/UX (Sections 1-3)
- **Chunk 2:** User Flows, Advanced Features, Performance (Sections 4-6)
- **Chunk 3:** Help, Business Model, Distribution (Sections 7-9)
- **Chunk 4:** Marketing, Launch Plan, Competitive Analysis (Sections 10-12)
- **Chunk 5:** Legal, Analytics, Roadmap, Launch Decision (Sections 13-16)

### Option 3: Focused Review (Pick 3-5 Critical Sections)

If time-constrained, prioritize:

1. **Section 1 (FTUE)** - First impressions matter
2. **Section 8 (Business Model)** - Pricing must be right
3. **Section 11 (Launch Plan)** - Execution is everything
4. **Section 16 (Launch Readiness)** - GO/NO-GO decision
5. **Section 15 (Roadmap)** - Strategic direction

---

## Expected Output

You will receive a 5,000-10,000 word comprehensive review covering:

- **Honest assessment** of product readiness (not just praise)
- **Specific actionable feedback** (not generic advice)
- **Launch recommendation** with reasoning (GO / NO-GO / SOFT LAUNCH)
- **Critical path** to successful launch
- **Risk mitigation** strategies
- **Roadmap prioritization** based on user value

---

## Timeline

**When to run this review:**

- **Now (Nov 13):** Initial review to identify gaps
- **Nov 18:** Mid-prep review after assets created
- **Nov 23:** Final review before launch (go/no-go gate)
- **Dec 10:** Post-launch review (what worked/failed)

---

## Pro Tips

1. **Be ready for harsh feedback** - This prompt is designed to surface problems
2. **Don't argue with output** - If multiple areas score low, that's data
3. **Focus on critical fixes** - You can't fix everything in 15 days
4. **Use scores to prioritize** - Fix all 1-2 scores, most 3 scores, some 4 scores
5. **Re-run after fixes** - See if score improves before launch
6. **Share with trusted advisor** - Get human feedback too

---

## Customization

To adapt this prompt for your needs:

- **Add more sections** (e.g., Accessibility, Internationalization)
- **Remove irrelevant sections** (e.g., if not doing Black Friday)
- **Adjust scoring criteria** (e.g., 1-10 scale instead of 1-5)
- **Add specific concerns** (e.g., "I'm worried about X, analyze deeply")
- **Request specific format** (e.g., "Output as Notion-ready markdown")

---

## Success Criteria

You'll know this review worked if:

- ✅ You discover 3-5 critical issues you didn't know about
- ✅ You get a clear launch recommendation with reasoning
- ✅ You have a prioritized action plan for next 15 days
- ✅ You understand your biggest risks and how to mitigate
- ✅ You feel confident (or appropriately cautious) about launch

---

## Post-Review Actions

After receiving the LLM review:

1. **Triage issues by severity:**

   - **P0 (Launch blocker):** Must fix or delay
   - **P1 (Critical):** Fix before launch if possible
   - **P2 (Important):** Fix in v1.1
   - **P3 (Nice-to-have):** Backlog

2. **Update todo list:**

   - Break P0/P1 issues into tasks
   - Assign deadlines
   - Track daily progress

3. **Re-assess launch date:**

   - If P0 issues take >15 days, delay to January
   - If P1 issues take >7 days, soft launch (beta)
   - If P2/P3 only, full launch

4. **Share with stakeholders:**

   - Send review to co-founders, advisors, beta users
   - Get second opinions on critical recommendations
   - Build consensus on launch decision

5. **Schedule follow-up review:**
   - Nov 23 (2 days before launch)
   - Re-run prompt with updated context
   - Confirm GO/NO-GO decision

---

## Emergency: Launch Failure Mode

If LLM review scores < 50/75 total:

- **STOP:** Do not launch on Black Friday
- **PIVOT:** Delay to January or Q1 2026
- **FOCUS:** Fix top 5 P0/P1 issues
- **TEST:** Run beta with 10-20 users
- **ITERATE:** Improve based on beta feedback
- **RE-LAUNCH:** When score > 55/75

Don't launch a bad product to hit an arbitrary date. Better to delay and launch strong.

---

Good luck! 🚀
