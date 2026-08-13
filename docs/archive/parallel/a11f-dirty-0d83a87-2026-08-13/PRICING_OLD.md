# Signature Extractor — Pricing Strategy

## Pricing Philosophy

1. **Desktop-first**: Free forever for core local extraction
2. **Pay for convenience**: Cloud sync, API access, integrations
3. **Fair & transparent**: No per-signature fees, no hidden charges
4. **Volume discounts**: Enterprise plans scale with team size

---

## Pricing Tiers

### 🪪 **Lifetime Desktop (One-Time)**

**Price**: $49 one-time (B2C)

**Includes**:

- Full desktop app (macOS, Windows, Linux)
- Unlimited local extractions forever
- 12 months of updates included (bug fixes + minor features)

**Limits**:

- No cloud features (sync, API, webhooks)
- No browser extension
- No team workspace
- After 12 months, optional update plan: $15/year (keeps lifetime license active with updates)

**Best For**: Individuals who prefer one-time purchase and local-only privacy

---

### 🆓 **Free (Desktop Only)**

**Price**: $0

**Includes**:

- Full desktop app (macOS, Windows, Linux)
- Unlimited signature extractions (local processing)
- Basic controls (threshold, color, zoom, pan)
- Export PNG with transparency
- SQLite database (local storage)
- EXIF orientation handling
- Community support (GitHub Discussions)

**Limits**:

- No cloud sync/backup
- No API access
- No browser extension
- No batch processing (manual one-by-one)

**Best For**: Individuals, freelancers, hobbyists, students

---

### 💼 **Pro (Desktop + Cloud)**

**Price**: $12/month or $120/year (save 17%)

**Everything in Free, plus**:

- **Cloud sync**: Backup sessions and extracted signatures
- **Browser extension**: Chrome, Firefox, Edge — extract from any webpage
- **Batch processing**: Drag-and-drop multiple files
- **Advanced controls**:
  - Otsu/adaptive thresholding
  - Morphology operations (erode, dilate)
  - Edge smoothing
- **Export formats**: PNG, JPEG, SVG, metadata JSON
- **Presets**: Save/load favorite threshold+color combos
- **Priority support**: Email response within 24 hours
- **Usage limits**: 500 cloud extractions/month

**Best For**: Professionals (real estate, legal, design), small businesses

---

### 🏢 **Team (Multi-User)**

**Price**: $30/month per user (min 3 users) or $300/year per user

**Everything in Pro, plus**:

- **Team workspace**: Shared library of extracted signatures
- **Role-based access**: Admin, Editor, Viewer roles
- **Audit logs**: Who extracted what, when (compliance-friendly)
- **API access**: 10,000 requests/month
- **Webhooks**: Trigger external workflows
- **SSO (Single Sign-On)**: Google Workspace, Microsoft 365, Okta
- **Custom branding**: White-label option (logo, colors)
- **Priority support**: Email/chat response within 4 hours
- **Dedicated account manager**: For teams 10+ users
- **Usage limits**: 5,000 cloud extractions/month per user

**Best For**: Law firms, healthcare providers, real estate agencies, design studios

---

### 🚀 **Enterprise (Custom)**

**Price**: Custom (starts at $500/month)

**Everything in Team, plus**:

- **Unlimited users**
- **On-premise deployment**: Deploy backend on your own infrastructure (Docker, Kubernetes)
- **Custom integrations**: DocuSign, Salesforce, custom CRM/ERP
- **Advanced AI features**:
  - OCR (text extraction)
  - Auto signature detection (ML-based)
  - Forgery detection (experimental)
- **SLA**: 99.9% uptime guarantee
- **Dedicated support**: Slack channel, phone, video calls
- **Custom feature development**: Negotiate feature prioritization
- **Volume licensing**: Special pricing for 100+ users
- **HIPAA/SOC 2 compliance**: Signed BAA, security audits
- **Usage limits**: Unlimited cloud extractions

**Best For**: Hospitals, banks, insurance companies, government agencies, SaaS platforms

---

## Add-Ons (All Tiers)

### 🤖 **OCR & Auto-Detection**

**Price**: +$5/month (Pro), included in Team/Enterprise

- Tesseract OCR for text extraction
- Contour-based signature auto-detection
- ML model (optional 40MB download)

### 📦 **Extra Cloud Storage**

**Price**: $0.10/GB/month (beyond 5GB included in Pro/Team)

- Store original images and extracted signatures
- Encrypted at rest (AES-256)

### 🔌 **API Overage**

**Price**: $0.001 per request (beyond tier limit)

- Applies to Team and Enterprise tiers
- Billed monthly based on actual usage

### 🎓 **Education Discount**

**Price**: 50% off Pro/Team tiers

- Verify with .edu email or student ID
- Annual verification required

### 💚 **Non-Profit Discount**

**Price**: 40% off Team tier, free Pro tier (1 user)

- Verify with 501(c)(3) status or equivalent

---

## Competitive Analysis

| Feature | Signature Extractor | Adobe Acrobat Pro | DocuSign | Smallpdf |
|---------|-------------------|------------------|----------|----------|
| **Pricing** | $49 lifetime / $12/mo | $19.99/mo | $10-40/mo | $9/mo |
| **Trial** | 14 days, 50 extractions | 7 days | 30 days | Limited features |
| **Desktop App** | ✅ Native | ❌ Web only | ❌ Web only | ❌ Web only |
| **Lifetime Option** | ✅ $49 | ❌ | ❌ | ❌ |
| **Local Processing** | ✅ Privacy-first | ⚠️ Cloud | ⚠️ Cloud | ⚠️ Cloud |
| **Precision Control** | ✅ Zoom, threshold | ⚠️ Basic | ❌ | ❌ |
| **Auto-Detection** | 🔄 Coming soon | ✅ | ✅ | ⚠️ Basic |
| **API Access** | Pro tier | Enterprise | ✅ Included | ❌ |

**Competitive Advantages**:
1. **Only lifetime option** in the market
2. **Desktop-first** for speed and privacy
3. **Precision control** vs generic crop tools
4. **Clear pricing** - No hidden fees or confusing tiers

**Positioning**: Signature Extractor complements e-sign platforms (extract → upload to DocuSign), rather than competing directly. Focus on **precision control** and **privacy**.

---

## Revenue Projections (Year 1)

### Conservative Scenario

- 500 Free users (no revenue)
- 50 Pro users × $12 = $600/mo
- 2 Team accounts (5 users each) × $150 = $300/mo
- **Monthly Revenue**: $900
- **Annual Revenue**: ~$10,800

### Moderate Scenario

- 2,000 Free users
- 200 Pro users × $12 = $2,400/mo
- 10 Team accounts (avg 5 users) × $150 = $1,500/mo
- 1 Enterprise account = $500/mo
- **Monthly Revenue**: $4,400
- **Annual Revenue**: ~$52,800

### Optimistic Scenario

- 5,000 Free users
- 500 Pro users × $12 = $6,000/mo
- 30 Team accounts (avg 6 users) × $180 = $5,400/mo
- 3 Enterprise accounts (avg) = $1,800/mo
- **Monthly Revenue**: $13,200
- **Annual Revenue**: ~$158,400

---

## Pricing Psychology

### Why $12/month for Pro?

- **Below competition**: DocuSign ($25), Adobe Sign ($30) → Signature Extractor feels like a steal
- **Impulse-friendly**: Under $15 triggers "low-friction" purchase decision
- **Annual incentive**: $120/year = $10/mo → 17% discount encourages commitment

### Why $30/user for Team?

- **Volume discount**: 3+ users = $90/mo total (cheaper than 3 Pro users at $36/mo if they didn't have team features)
- **B2B expectation**: Teams expect to pay $20-50/user/mo for SaaS tools
- **Margin for sales**: Room for 20-30% discounts for larger teams

### Why Custom for Enterprise?

- **Value-based pricing**: Large orgs have bigger budgets and need custom features
- **Negotiation leverage**: "Starts at $500" anchors the conversation high
- **Relationship-building**: Custom contracts allow for long-term partnerships and upsells

---

## Payment & Billing

- **Stripe**: Credit card, Apple Pay, Google Pay
- **Invoicing**: Net-30 for Enterprise (ACH, wire transfer)
- **Currency**: USD primary; EUR, GBP for international users (Stripe auto-converts)
- **Refund Policy**: 30-day money-back guarantee (no questions asked)
- **Cancellation**: Anytime; keep access until end of billing period

---

## Free Trial Strategy

### Pro Tier: 14-Day Free Trial

- No credit card required
- Full access to all Pro features
- Email reminders at Day 7, Day 13, Day 14
- Post-trial: Convert to Free tier (no data loss) or upgrade to Pro

### Team/Enterprise: Custom Demo

- Schedule 30-min call with sales
- Live demo with sample documents
- 30-day pilot program for larger teams (negotiable)

---

## Growth Tactics

1. **Freemium Conversion**: Add subtle "Upgrade to Pro" prompts in desktop app (e.g., after 10 extractions: "🎉 You've extracted 10 signatures! Upgrade to Pro for batch processing")
2. **Referral Program**: Give 1 month free Pro for every friend who signs up (both referrer and referee)
3. **Content Marketing**: Blog posts on "How to extract signatures from contracts", "Best practices for e-signing workflows" → SEO traffic
4. **YouTube Tutorials**: Screen recordings showing extraction process → embed on landing page
5. **Product Hunt Launch**: Target tech-savvy early adopters → drive initial signups
6. **Integration Partnerships**: Co-marketing with DocuSign, Zapier, Notion → cross-promotion
7. **LinkedIn Ads**: Target legal, real estate, design job titles → $500/mo ad spend
8. **Affiliate Program**: 20% commission for bloggers/YouTubers who promote Signature Extractor

---

## Pricing Evolution (Future)

### Year 2-3: Introduce New Tiers

- **Starter ($5/mo)**: Between Free and Pro — cloud sync only, no browser extension (capture users who don't want full Pro)
- **Premium ($25/mo)**: Above Pro — includes OCR, auto-detection, priority rendering
- **Team Plus ($50/user)**: Above Team — advanced compliance (SOC 2, HIPAA BAA)

### Usage-Based Pricing (Alternative Model)

- **Pay-as-you-go**: $0.05 per extraction (cloud processing)
- **Credits**: Buy 100 credits for $4 (4¢ each), 1000 credits for $30 (3¢ each)
- **Hybrid**: Free desktop app + pay per cloud extraction

**Pros**: Lower barrier to entry; scales with usage  
**Cons**: Unpredictable revenue; harder to forecast; may discourage heavy users

---

## Localization & Regional Pricing

### Adjust for PPP (Purchasing Power Parity)

| Region                            | Pro Price | Discount |
| --------------------------------- | --------- | -------- |
| **US, Canada, Western Europe**    | $12/mo    | 0%       |
| **Eastern Europe, Latin America** | $8/mo     | 33%      |
| **India, Southeast Asia**         | $5/mo     | 58%      |
| **Africa**                        | $4/mo     | 67%      |

**Implementation**: Detect user location via IP; show adjusted pricing on landing page. Verify with payment card country.

---

## Open-Source vs. Commercial

### Hybrid Model (Consider)

- **Desktop app**: Open-source (MIT License) → builds community trust
- **Cloud backend**: Proprietary → monetize API access and integrations
- **Enterprise features**: Proprietary (SSO, compliance, custom integrations)

**Benefits**:

- Attracts developers who want to self-host
- Contributions improve core product
- Still monetize via hosted service and premium features

**Risks**:

- Competitors could fork and undercut on price
- Harder to enforce licensing for enterprise features

**Recommendation**: Start fully proprietary; open-source core extraction library after 12-18 months (once market position is established).

---

## Key Metrics to Track

1. **Free → Pro Conversion Rate**: Target 3-5%
2. **Pro → Team Conversion**: Target 10-15% (as teams grow)
3. **Churn Rate**: Target <5% monthly for paid tiers
4. **LTV (Lifetime Value)**: Pro = $12 × 18 months avg = $216; Team = $30 × 24 months = $720
5. **CAC (Customer Acquisition Cost)**: Target <$50 for Pro, <$300 for Team
6. **LTV:CAC Ratio**: Target 3:1 or higher (healthy SaaS business)

---

## Pricing FAQs

**Q: Can I upgrade/downgrade anytime?**  
A: Yes. Upgrades take effect immediately; downgrades at next billing cycle.

**Q: Do you offer non-profit/education discounts?**  
A: Yes! 40% off for non-profits, 50% off for students/teachers.

**Q: Is there a free trial?**  
A: Yes, 14 days for Pro tier (no credit card required).

**Q: What happens if I exceed API limits?**  
A: We send an email warning at 80% usage. Overage billed at $0.001/request.

**Q: Can I pay annually?**  
A: Yes! Get 2 months free (17% discount) with annual billing.

**Q: Do you offer refunds?**  
A: Yes, 30-day money-back guarantee for first purchase.
