# SignKit Product Roadmap 2025-2026
## Feature Prioritization & Development Strategy

**Last Updated:** November 15, 2025
**Planning Horizon:** 14 months (Nov 2025 - Dec 2026)
**Review Cadence:** Monthly

---

## PRODUCT VISION

**Mission:** Empower professionals to own their signature extraction workflow with privacy-first, offline tools that save time and maintain quality.

**Vision (3 years):** The de facto standard for signature extraction and document signing for privacy-conscious professionals, with 100,000+ users and $5M ARR.

**Current Status (Nov 2025):**
- **Version:** 1.0 (92% complete)
- **Users:** 0 (pre-launch)
- **Features:** Core extraction + PDF signing ready

---

## ROADMAP PHILOSOPHY

### Guiding Principles

1. **Ship First, Perfect Later** - Launch with 80% feature completeness, iterate based on real feedback
2. **Customer-Driven** - Build what users ask for, not what seems cool
3. **Privacy Always** - Never compromise on offline-first architecture
4. **Technical Debt = Real Debt** - Allocate 20% of dev time to refactoring and technical debt
5. **Measure Everything** - No feature ships without defined success metrics

### Feature Prioritization Framework (RICE)

Each feature scored on:
- **Reach:** How many users affected (1-10 scale)
- **Impact:** Effect on conversion/retention (1-5 scale: Minimal, Low, Medium, High, Massive)
- **Confidence:** How sure are we this will work (1-100%)
- **Effort:** Engineering time in person-weeks

**RICE Score = (Reach × Impact × Confidence) / Effort**

Features with RICE > 50 = High priority
Features with RICE 20-50 = Medium priority
Features with RICE < 20 = Low priority or backlog

---

## PHASE 1: LAUNCH & STABILIZATION (Nov 2025 - Jan 2026)

**Goal:** Ship v1.0, achieve product-market fit, hit 300-500 customers

### Week 1-2: Pre-Launch Polish (Nov 15-30, 2025)

**Critical Path (Must-Have for Launch):**

- [ ] **Gumroad Integration** (Effort: 0.5 weeks)
  - Finalize product listing
  - Test purchase flow end-to-end
  - Set up license key generation
  - **RICE:** (10 × 5 × 100%) / 0.5 = **1000** (CRITICAL)

- [ ] **Cross-Platform Testing** (Effort: 1 week)
  - Test on macOS Intel + ARM64
  - Test on Windows 10/11
  - Test on Linux (Ubuntu 22.04)
  - Fix platform-specific bugs
  - **RICE:** (10 × 4 × 90%) / 1 = **36** (HIGH)

- [ ] **Demo Video Creation** (Effort: 0.25 weeks)
  - Record 45-second workflow demo
  - Add subtitles for accessibility
  - Upload to YouTube (unlisted) + embed in Gumroad
  - **RICE:** (10 × 5 × 100%) / 0.25 = **200** (CRITICAL)

- [ ] **Help Documentation** (Effort: 0.5 weeks)
  - Write 10 FAQ articles
  - Create quick start guide
  - Host on Notion or simple site
  - **RICE:** (8 × 3 × 100%) / 0.5 = **48** (HIGH)

**Nice-to-Have (Can Defer):**

- [ ] **macOS Code Signing** (Effort: 1 week)
  - Apply for Apple Developer certificate
  - Notarize app bundle
  - Prevents "untrusted developer" warning
  - **RICE:** (7 × 3 × 70%) / 1 = **14.7** (MEDIUM - defer to Month 2)

- [ ] **Windows Installer** (Effort: 1 week)
  - Create MSI installer with Inno Setup
  - Prevents "Windows SmartScreen" warning
  - **RICE:** (6 × 3 × 70%) / 1 = **12.6** (MEDIUM - defer to Month 2)

**Decision:** Launch with ZIP downloads, add installers in Month 2 based on user feedback.

---

### Month 1 (Dec 2025): Launch & Iteration

**Goals:**
- 120-200 sales
- <5% refund rate
- Net Promoter Score (NPS) > 40
- 0 critical bugs

**Feature Development (20% of time):**

- [ ] **Batch Export** (HIGH DEMAND Expected)
  - Allow users to extract multiple signatures in one session
  - Save all to library with auto-naming
  - Requested by paralegals (Persona: Sarah)
  - **Effort:** 1 week
  - **RICE Estimate:** (7 × 4 × 80%) / 1 = **22.4** (MEDIUM)
  - **Ship:** Only if 20+ users request in first 2 weeks

- [ ] **Keyboard Shortcuts** (Quick Win)
  - Cmd/Ctrl+S to save
  - Cmd/Ctrl+Z to undo
  - Arrow keys to adjust threshold
  - **Effort:** 0.5 weeks
  - **RICE:** (9 × 3 × 100%) / 0.5 = **54** (HIGH)
  - **Ship:** Week 3 of Dec

**Bug Fixing & Support (60% of time):**
- Monitor Gumroad support emails daily
- Fix critical bugs within 24 hours
- Fix minor bugs within 1 week
- Collect feature requests in Notion database

**Technical Debt (20% of time):**
- Refactor image processing pipeline (currently has duplicate code)
- Add unit tests for threshold calculation
- Document API endpoints (FastAPI auto-docs)

---

### Month 2-3 (Jan-Feb 2026): Optimize Core Experience

**Goals:**
- 400-600 total customers
- Reduce refund rate to <3%
- NPS > 50
- Establish email nurture sequence

**High-Priority Features (Based on Expected Feedback):**

- [ ] **Undo/Redo Stack** (RICE: 52)
  - Effort: 1 week
  - Impact: High (reduces user errors)
  - Requested by: Designers (Persona: Elena)

- [ ] **Preset Threshold Values** (RICE: 45)
  - Save custom threshold settings
  - Quick apply to similar scans
  - Effort: 0.5 weeks
  - Requested by: Power users processing many similar docs

- [ ] **Color Picker Presets** (RICE: 38)
  - Save brand colors for reuse
  - Quick switch between presets
  - Effort: 0.5 weeks
  - Requested by: Designers (Persona: Elena)

- [ ] **macOS Code Signing** (RICE: 30)
  - Effort: 1 week
  - Impact: Medium (reduces friction for Mac users)
  - Ship: Mid-January

- [ ] **Windows Installer** (RICE: 25)
  - Effort: 1 week
  - Impact: Medium (reduces friction for Windows users)
  - Ship: Late January

**Features to REJECT (Low RICE, Distraction):**

- ❌ **Cloud Sync** - Conflicts with privacy-first mission, defer to Pro tier
- ❌ **Mobile App** - Requires 6+ months dev, not part of MVP
- ❌ **Collaboration Features** - Not requested by target users yet

---

## PHASE 2: GROWTH & DIFFERENTIATION (Mar-Jun 2026)

**Goal:** Scale to 1,000 customers, introduce advanced features, prepare Pro tier

### Month 4-5 (Mar-Apr 2026): Power User Features

**Goals:**
- 700-1,000 total customers
- Launch Zapier integration
- Publish 20+ SEO blog posts

**Development Priorities:**

- [ ] **Zapier Integration** (RICE: 85)
  - Connect SignKit to 5,000+ apps
  - Triggers: New signature extracted, signature saved to library
  - Actions: Extract signature from Dropbox/Drive file
  - Effort: 2 weeks
  - Impact: Massive (SEO benefit + automation use cases)
  - **Ship:** Early March

- [ ] **Export Templates** (RICE: 42)
  - Pre-configured export settings (Email Signature 500×200, Business Card 300 DPI, etc.)
  - Requested by: Designers, consultants
  - Effort: 1 week
  - **Ship:** Mid-March

- [ ] **Smart Crop Suggestions** (RICE: 48)
  - AI-detected signature regions (using OpenCV contour detection)
  - Reduces manual selection time
  - Effort: 1.5 weeks
  - **Ship:** Late March if time allows

**Technical Debt:**
- Upgrade to PySide6.6 (latest Qt version)
- Refactor PDF rendering (currently uses 3 libraries, consolidate to 2)
- Add integration tests for Zapier

---

### Month 6-7 (May-Jun 2026): Enterprise-Ready Features

**Goals:**
- 1,000-1,500 total customers
- <2% monthly churn (if any recurring revenue)
- Prepare for Pro tier launch

**Development Priorities:**

- [ ] **Audit Log Export** (RICE: 55)
  - Export audit logs as CSV/JSON for compliance
  - Requested by: Banks, legal (Persona: David)
  - Effort: 1 week
  - **Ship:** Early May

- [ ] **Batch Processing (Advanced)** (RICE: 60)
  - Process folder of PDFs, extract all signatures
  - Auto-detect and name by file metadata
  - Effort: 2 weeks
  - **Ship:** Mid-May (if Month 1 batch feature was popular)

- [ ] **Team License Management** (RICE: 50)
  - Single purchase unlocks 5-10 seats
  - Admin can assign/revoke licenses
  - Effort: 1.5 weeks
  - **Ship:** Late May (prepare for enterprise sales)

**Features to Consider (Feedback-Dependent):**

- [ ] **Vector Export (SVG)** (RICE: 40)
  - Export signatures as SVG for print use
  - Highly requested by: Designers
  - Effort: 2 weeks (tricky with OpenCV)
  - **Ship:** Only if 50+ requests from paying customers

- [ ] **API Access** (RICE: 35)
  - RESTful API for programmatic signature extraction
  - Requested by: Developers, integrations
  - Effort: 1.5 weeks (FastAPI already in place)
  - **Ship:** If 20+ enterprise customers request

---

## PHASE 3: PRO TIER LAUNCH (Aug-Oct 2026)

**Goal:** Introduce recurring revenue, scale to 2,000 customers, $1,000+ MRR

### Month 8-9 (Jul-Aug 2026): Pro Tier Development

**Pro Tier Features (Choose 5-7):**

**High Confidence (Will Include):**

1. **Cloud Sync** (RICE: 70)
   - Sync signature library across devices
   - Encrypted at rest and in transit
   - Effort: 3 weeks
   - Pricing: $15/month core value driver

2. **Batch Processing (Unlimited)** (RICE: 65)
   - Lifetime tier: 10 signatures/batch
   - Pro tier: Unlimited batch size
   - Effort: 1 week (build on existing feature)

3. **Priority Support** (RICE: 60)
   - 24-hour email response (vs 48-72 for lifetime)
   - Video call support (optional)
   - Effort: 0 (process change, not dev)

4. **Browser Extension** (RICE: 55)
   - Extract signatures directly from Gmail, Google Drive
   - Chrome + Firefox
   - Effort: 3 weeks
   - High visibility feature

5. **Advanced Audit Logs** (RICE: 50)
   - Detailed compliance reports
   - Export formats: PDF, CSV, JSON
   - Effort: 1 week

**Medium Confidence (Test Demand):**

6. **Zapier Premium Triggers** (RICE: 45)
   - More advanced automation workflows
   - Effort: 1 week

7. **API Access (Full)** (RICE: 40)
   - 1,000 requests/month (vs 100 for free)
   - Effort: 0.5 weeks (rate limiting)

8. **Vector Export** (RICE: 42)
   - SVG export for print/design use
   - Effort: 2 weeks

**Development Timeline:**

- **July:** Build cloud sync infrastructure (3 weeks)
- **August Week 1-2:** Build browser extension (2 weeks)
- **August Week 3-4:** Polish, test, prepare marketing

**Launch Strategy:**

- **September 1:** Soft launch to existing customers (email announcement)
- **September 15:** Public launch (blog post, social media)
- **Goal:** 80-120 Pro subscribers by end of September (10-15% of lifetime customers)

---

### Month 10-11 (Sep-Oct 2026): Pro Tier Optimization

**Goals:**
- 100-150 Pro subscribers ($1,500-2,250 MRR)
- Pro churn rate < 5% monthly
- Lifetime sales still strong (150-200/month)

**Development Focus:**

- [ ] **Onboarding Flow Redesign** (RICE: 55)
  - In-app tutorial for new users
  - Reduces support burden
  - Effort: 1 week
  - **Ship:** Early September

- [ ] **Usage Analytics (Privacy-Respecting)** (RICE: 50)
  - Track feature adoption (anonymized, opt-in)
  - Understand which features drive retention
  - Effort: 1 week
  - **Ship:** Mid-September

- [ ] **Pro Tier Feature Iteration** (Ongoing)
  - Fix bugs in cloud sync
  - Improve browser extension performance
  - Add user-requested features

**Marketing Features (Not Dev Work):**

- Create Pro tier case studies
- Video tutorials for Pro-only features
- Email campaigns to lifetime users: "Upgrade to Pro"

---

## PHASE 4: SCALE & ENTERPRISE (Nov 2026 - Jan 2027)

**Goal:** 2,500+ total customers, $2,000+ MRR, explore enterprise

### Month 12-14 (Nov 2026 - Jan 2027): Platform Expansion

**Development Priorities:**

- [ ] **Linux Support (Official)** (RICE: 38)
  - Currently works but not officially supported
  - Package as AppImage or Snap
  - Effort: 1.5 weeks
  - **Ship:** November if developer bandwidth allows

- [ ] **Enterprise Management Portal** (RICE: 70)
  - Web-based admin panel
  - Manage 50+ licenses, usage analytics
  - Effort: 4 weeks
  - **Ship:** December-January (if 5+ enterprise deals in pipeline)

- [ ] **SSO Integration (SAML)** (RICE: 60)
  - Required for Fortune 500 sales
  - Effort: 2 weeks
  - **Ship:** Only if 3+ enterprise prospects request

**Features to Continue Iterating:**

- Improve cloud sync performance
- Add more Zapier integrations
- Expand browser extension (Safari, Edge)

**Features to Deprecate/Simplify:**

- Remove experimental features with <5% adoption
- Simplify UI based on user session recordings
- Reduce number of settings (most users don't change defaults)

---

## TECHNICAL DEBT ROADMAP

**Monthly Allocation:** 20% of dev time (1 day/week)

### Q4 2025 (Dec)
- [ ] Add unit tests for image processing functions (test coverage goal: 60%)
- [ ] Refactor coordinate mapping for rotation (currently buggy edge cases)
- [ ] Document API with OpenAPI spec (FastAPI auto-generates)

### Q1 2026 (Jan-Mar)
- [ ] Upgrade dependencies (PySide6, OpenCV, pypdfium2)
- [ ] Refactor PDF rendering pipeline (remove PyMuPDF dependency if possible)
- [ ] Add end-to-end tests (Playwright for desktop app testing)

### Q2 2026 (Apr-Jun)
- [ ] Performance optimization (reduce app launch time from 3s to <1s)
- [ ] Memory leak fixes (currently uses 150MB, should be <100MB)
- [ ] Code refactoring (reduce cyclomatic complexity in main window class)

### Q3 2026 (Jul-Sep)
- [ ] Cloud sync infrastructure (design for scale, handle 10,000+ users)
- [ ] Browser extension architecture (secure communication with desktop app)
- [ ] Security audit (hire external firm if revenue allows)

### Q4 2026 (Oct-Dec)
- [ ] Database optimization (SQLite → PostgreSQL for enterprise features)
- [ ] Logging infrastructure (structured logging with rollbar or sentry)
- [ ] Deployment automation (CI/CD for Mac, Windows, Linux builds)

---

## FEATURE REQUEST MANAGEMENT

### Collection Process

**Sources:**
1. In-app feedback form (simple text box)
2. Email: support@signkit.work
3. Twitter mentions (@SignKitApp)
4. Reddit comments
5. Product Hunt comments (first 3 months)

**Triage Process (Weekly):**

1. **Collect:** Import all feature requests to Notion database
2. **Categorize:**
   - Bug (not a feature request)
   - Enhancement (improve existing feature)
   - New Feature (net new capability)
3. **Tag by Persona:** Sarah, Marcus, Elena, David, Rachel
4. **Tag by Theme:** Performance, UI/UX, Privacy, Integrations, Enterprise
5. **Score RICE:** Estimate Reach, Impact, Confidence, Effort
6. **Assign Status:**
   - Backlog (RICE < 20)
   - Under Consideration (RICE 20-50)
   - Planned (RICE 50-100, added to roadmap)
   - In Development (actively building)
   - Shipped (released, notify requester)

### Communication

**For Planned Features:**
- Post on Product Hunt: "Feature Update: [Feature Name] is coming in [Month]"
- Tweet: "You asked, we listened. [Feature] coming soon."
- Email to requester: "Thanks for suggesting [feature]. We're building it! ETA: [date]"

**For Rejected Features:**
- Email to requester: "Thanks for suggesting [feature]. Here's why we're not building it right now: [reason]. Would [alternative] solve your use case?"

**For Shipped Features:**
- Blog post: "What's New in SignKit: [Feature Release Notes]"
- Email to all requester: "Your feature is live! [CTA to update app]"
- Social media: Screenshots/GIF demo of new feature

---

## METRICS & SUCCESS CRITERIA

### Product Health Metrics (Check Weekly)

**Engagement:**
- Daily Active Users (DAU)
- Weekly Active Users (WAU)
- DAU/WAU ratio (goal: >30% = sticky product)

**Feature Adoption:**
- % of users who use [feature] within 7 days
- Most-used features (by session time)
- Least-used features (candidates for removal)

**Quality:**
- Crash rate (goal: <0.1% of sessions)
- Bug report rate (goal: <5% of users report bugs)
- Refund rate (goal: <3%)

**Growth:**
- Week-over-week user growth
- Customer Acquisition Cost (CAC)
- Lifetime Value (LTV)
- LTV:CAC ratio (goal: >3:1)

### Feature Success Criteria

**Every feature must define:**

1. **Success Metric:** What will we measure?
2. **Target:** What's the goal? (e.g., "30% of users use batch export within 30 days")
3. **Timeline:** When will we measure? (e.g., "4 weeks after launch")
4. **Experiment:** How will we test? (e.g., "A/B test with 50% of users")

**Example: Batch Export Feature**
- Metric: % of users who export >1 signature in a session
- Target: 25% of power users (defined as 5+ signatures extracted total)
- Timeline: 30 days after launch
- Experiment: Soft launch to 50% of users, measure adoption, roll out to 100% if >20%

**If Target Missed:**
- Analyze why: Discoverability? Usability? Not valuable?
- Iterate: Redesign UI, add tutorial, or sunset feature

---

## ROADMAP REVIEW PROCESS

**Monthly Review (First Monday of Month):**

1. **Retrospective:**
   - What shipped last month?
   - What metrics improved/declined?
   - User feedback themes?

2. **Prioritization:**
   - Re-score RICE based on new data
   - Promote backlog items if priority increased
   - Deprioritize planned items if new urgency emerged

3. **Planning:**
   - Lock features for next month (max 3-4 big features)
   - Assign technical debt work (1 day/week minimum)
   - Buffer time for bugs and customer support

4. **Communication:**
   - Publish roadmap update on blog
   - Email power users: "Here's what we're building next month"
   - Tweet: "SignKit roadmap update: [link]"

**Quarterly Review (March, June, September, December):**

1. **Strategic Alignment:**
   - Are we hitting revenue targets?
   - Are we building for the right personas?
   - Is our positioning still differentiated?

2. **Roadmap Pivot:**
   - Should we shift focus? (e.g., more enterprise vs consumer)
   - Should we sunset features with low adoption?
   - Should we accelerate Pro tier vs lifetime?

3. **Technical Health:**
   - Code quality metrics (test coverage, bug density)
   - Performance benchmarks (app launch time, memory usage)
   - Security audit findings

---

## DECISION LOG

Track major product decisions here:

| Date | Decision | Rationale | Outcome (Review After 3 Months) |
|------|----------|-----------|----------------------------------|
| 2025-11-15 | Launch without macOS code signing | Speed to market > polish. Can add in Month 2. | TBD |
| 2025-11-15 | Lifetime pricing ($29-39) vs subscription | Lower barrier to entry, differentiation vs Adobe. | TBD |
| 2025-11-15 | Defer mobile app to 2027 | Focus on desktop PMF first. Mobile is 6+ month distraction. | TBD |
| 2025-11-15 | Include audit logging in MVP | Enterprise customers (banks) need this for compliance. | TBD |

---

## OPEN QUESTIONS (To Answer with Data)

1. **Should we build a freemium tier?**
   - Current plan: No free tier, only 30-day refund guarantee
   - Risk: Lower conversion vs freemium
   - Benefit: Simpler pricing, filters out tire-kickers
   - **Decision:** Launch with paid-only. Revisit in Month 6 if conversion <2%

2. **Should Pro tier be $15/mo or $20/mo?**
   - $15/mo = easier sell, lower LTV
   - $20/mo = higher LTV, but price sensitivity risk
   - **Decision:** Launch at $15/mo with annual option $129/year (save $51). Test $20/mo after 100 subscribers.

3. **Should we build mobile app (iOS/Android)?**
   - Pros: Larger addressable market, convenience
   - Cons: 6+ months dev time, different architecture, fragmented resources
   - **Decision:** Defer to 2027. Focus on desktop PMF first.

4. **Should we integrate with DocuSign/Adobe APIs?**
   - Pros: "Import signatures from DocuSign" could be killer feature
   - Cons: Dependency on third-party APIs, privacy implications
   - **Decision:** Explore in Month 6-9 if 50+ users request

5. **Should we offer lifetime grandfathering into Pro tier?**
   - Scenario: Early lifetime buyers want Pro features without paying monthly
   - Options:
     A) Lifetime users get 50% off Pro tier forever ($7.50/mo vs $15/mo)
     B) Lifetime users get Pro tier for $99/year (vs $129/year)
     C) No discount (full price for Pro tier)
   - **Decision:** TBD based on feedback when Pro tier launches

---

## APPENDIX: FEATURE BACKLOG (Not Prioritized)

Ideas collected but not yet prioritized:

- **Dark Mode** (common request, low effort)
- **Multi-language Support** (effort: high, uncertain demand)
- **Signature Animation** (export signature as animated GIF - niche use case)
- **Handwriting-to-Font** (convert signature to usable font file - complex)
- **Blockchain Verification** (cryptographic proof of signature origin - niche)
- **Signature Comparison Tool** (forensic signature matching - banks?)
- **Mobile Camera Capture** (companion app to send photos to desktop - medium effort)
- **Dropbox/Google Drive Integration** (auto-watch folder for new signatures)
- **Slack Integration** (extract signatures from Slack-shared PDFs)
- **Print-to-SignKit** (virtual printer driver - high effort, low demand)

**Decision:** Keep in backlog. Revisit if multiple users request organically.

---

## SUMMARY: NEXT 90 DAYS

**November 2025:**
- Launch SignKit v1.0
- Target: 120 sales
- Focus: Customer support, bug fixing

**December 2025:**
- Add keyboard shortcuts
- macOS code signing
- Target: 200 total customers

**January 2026:**
- Launch Zapier integration
- Windows installer
- Target: 400-500 total customers

**February 2026:**
- Power user features (undo/redo, presets)
- Prepare for Pro tier development
- Target: 600-700 total customers

---

**This roadmap is a living document. Update monthly based on user feedback, market trends, and business metrics.**

*Last Updated: November 15, 2025*
*Next Review: December 1, 2025*
