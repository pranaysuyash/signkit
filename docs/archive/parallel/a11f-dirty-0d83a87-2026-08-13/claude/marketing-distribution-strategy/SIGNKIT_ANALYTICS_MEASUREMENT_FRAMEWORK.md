# SignKit Analytics & Measurement Framework
## Data-Driven Decision Making Guide

**Last Updated:** November 15, 2025
**Review Cadence:** Weekly (metrics), Monthly (strategy)

---

## PHILOSOPHY

**"In God we trust. All others must bring data." - W. Edwards Deming**

This framework ensures every product decision, marketing campaign, and feature investment is grounded in measurable outcomes, not opinions or gut feelings.

---

## METRICS HIERARCHY

### North Star Metric

**Primary:** Monthly Recurring Revenue (MRR) + Lifetime Sales Revenue

**Why:** Balances short-term cash flow (lifetime sales) with long-term sustainability (Pro tier MRR)

**Target Trajectory:**
- Month 1: $3,000
- Month 3: $8,000
- Month 6: $15,000
- Month 12: $35,000 ($25K lifetime + $10K MRR)
- Month 14: $50,000 ($35K lifetime + $15K MRR)

---

### Tier 1: Business Health Metrics (Check Daily)

#### Revenue Metrics

**1. Daily Sales**
- **Definition:** Number of units sold per day
- **Target:**
  - Week 1: 15-25/day
  - Month 1: 3-8/day
  - Month 6: 8-15/day
- **Data Source:** Gumroad dashboard
- **Alert:** If <2 sales/day for 3 consecutive days → investigate

**2. Gross Revenue (Daily)**
- **Definition:** Total $ collected before fees
- **Target:**
  - Week 1: $450-750/day
  - Month 1: $90-240/day
  - Month 6: $240-450/day
- **Data Source:** Gumroad dashboard
- **Alert:** If <$100/day for 5 consecutive days → run promotion

**3. Net Revenue (After Fees)**
- **Definition:** Revenue after Gumroad 10% fee
- **Calculation:** Gross × 0.9
- **Target:** 90% of gross
- **Data Source:** Calculated from Gumroad
- **Alert:** If net < 88% of gross → check for unusual refunds

#### Conversion Metrics

**4. Landing Page Conversion Rate**
- **Definition:** (Purchases / Unique Visitors) × 100
- **Target:** 3-5%
- **Data Source:** Plausible Analytics + Gumroad
- **Alert:** If <2% for 7 consecutive days → A/B test landing page

**5. Email-to-Purchase Conversion**
- **Definition:** (Purchases from email / Email subscribers) × 100
- **Target:** 20-30% within 30 days of subscribing
- **Data Source:** ConvertKit + Gumroad (UTM tracking)
- **Alert:** If <15% → revise email sequence

---

### Tier 2: Growth Metrics (Check Weekly)

#### Traffic & Audience

**6. Website Traffic (Unique Visitors/Week)**
- **Definition:** Unique visitors to landing page
- **Target:**
  - Month 1: 1,000-2,000/week
  - Month 3: 2,500-4,000/week
  - Month 6: 5,000-8,000/week
- **Data Source:** Plausible Analytics
- **Alert:** If week-over-week decline >20% → investigate source

**7. Traffic by Source**
- **Definition:** % of traffic from each channel
- **Target Distribution (Month 6):**
  - Organic (SEO): 40-50%
  - Social (Twitter, LinkedIn): 20-30%
  - Referral (Product Hunt, Reddit, etc.): 15-25%
  - Direct: 10-15%
  - Paid: 0-10%
- **Data Source:** Plausible Analytics (UTM parameters)
- **Alert:** If any single source >60% → diversify

**8. Email List Growth**
- **Definition:** New subscribers per week
- **Target:**
  - Month 1: 50-100/week
  - Month 3: 100-200/week
  - Month 6: 200-400/week
- **Data Source:** ConvertKit
- **Alert:** If <30/week for 2 consecutive weeks → improve lead magnet

**9. Social Media Followers (Twitter)**
- **Definition:** Net new followers per week
- **Target:**
  - Month 1: 50-100/week
  - Month 3: 100-200/week
  - Month 6: 200-400/week
- **Data Source:** Twitter Analytics
- **Alert:** If follower growth <20/week → increase engagement

#### Product Engagement

**10. Trial-to-Purchase Conversion** (If offering trial)
- **Definition:** (Purchases / Trial activations) × 100
- **Target:** N/A (no trial currently, direct purchase model)
- **Note:** May add trial in Month 6, target 18-25% conversion

**11. Time to First Value**
- **Definition:** Minutes from app launch to first signature extracted
- **Target:** <5 minutes
- **Data Source:** In-app analytics (opt-in, privacy-respecting)
- **Alert:** If >10 minutes average → improve onboarding

**12. Feature Adoption Rate**
- **Definition:** % of users who use [feature] within 7 days
- **Target (by feature):**
  - PDF signing: 60%+
  - Library save: 70%+
  - Threshold adjustment: 80%+
  - Color customization: 30%+
- **Data Source:** In-app analytics
- **Alert:** If core feature <50% → improve discoverability

---

### Tier 3: Quality Metrics (Check Weekly)

#### Customer Satisfaction

**13. Refund Rate**
- **Definition:** (Refunds / Total sales) × 100
- **Target:** <5% (industry avg for digital products: 5-10%)
- **Data Source:** Gumroad
- **Alert:** If >10% → investigate quality issues

**14. Net Promoter Score (NPS)**
- **Definition:** % Promoters (9-10) - % Detractors (0-6)
- **Target:**
  - Month 1: NPS > 30 (good)
  - Month 6: NPS > 50 (excellent)
- **Data Source:** Email survey (send to customers after 14 days)
- **Alert:** If NPS <20 → urgent product improvements needed

**Question:** "How likely are you to recommend SignKit to a colleague? (0-10)"

**15. Customer Support Volume**
- **Definition:** Support emails per 100 customers
- **Target:** <10 support emails per 100 customers per month
- **Data Source:** support@signkit.work inbox
- **Alert:** If >20 emails per 100 customers → common issue needs fixing

**16. Average Response Time**
- **Definition:** Hours from customer email to first response
- **Target:** <24 hours (business days)
- **Data Source:** Email client (manual tracking or Help Scout)
- **Alert:** If >48 hours → hire VA for support

#### Technical Quality

**17. App Crash Rate**
- **Definition:** % of sessions that end in crash
- **Target:** <0.5%
- **Data Source:** Crash reporting tool (Sentry, Rollbar, or built-in)
- **Alert:** If >2% → emergency bug fix

**18. Bug Report Rate**
- **Definition:** % of customers who report bugs
- **Target:** <5%
- **Data Source:** Support emails tagged "bug"
- **Alert:** If >10% → major quality issue

---

### Tier 4: Financial Metrics (Check Monthly)

#### Unit Economics

**19. Customer Acquisition Cost (CAC)**
- **Definition:** Total marketing spend / New customers
- **Target (by channel):**
  - Organic (SEO, social): $0-5 (time only)
  - Paid ads: <$40
  - Overall blended: <$20
- **Data Source:** Marketing budget spreadsheet + sales data
- **Alert:** If CAC >$60 on paid ads → pause ads

**20. Lifetime Value (LTV)**
- **Definition:** Average revenue per customer over lifetime
- **Calculation:**
  - Lifetime-only customers: $39 (simple)
  - Pro tier upgrades (assume 15%): $39 + (0.15 × $129 × 3 years) = $97
  - Blended LTV: ~$50-70 (conservative)
- **Target:** LTV > 3× CAC (goal: LTV = $60, CAC = $20, ratio = 3:1)
- **Data Source:** Calculated from purchase data + upgrade rates
- **Alert:** If LTV:CAC <2:1 → improve retention or reduce CAC

**21. Monthly Recurring Revenue (MRR)** (After Pro tier launch)
- **Definition:** Predictable monthly revenue from Pro subscriptions
- **Target:**
  - Month 10: $1,000-1,500
  - Month 12: $2,000-3,000
  - Month 14: $3,000-5,000
- **Data Source:** Stripe or Gumroad subscriptions
- **Alert:** If MRR growth <10% month-over-month → improve Pro value prop

**22. Churn Rate** (After Pro tier launch)
- **Definition:** (Cancellations this month / Total subscribers start of month) × 100
- **Target:** <5% monthly (60% annual retention)
- **Data Source:** Stripe or Gumroad
- **Alert:** If >7% monthly → investigate cancellation reasons

**23. Gross Margin**
- **Definition:** (Revenue - COGS) / Revenue
- **COGS:** Gumroad fees (10%), server costs (~$50/mo), tools (~$100/mo)
- **Target:** >85% gross margin
- **Data Source:** Financial tracking spreadsheet
- **Alert:** If <80% → review cost structure

---

## DATA COLLECTION SETUP

### Essential Tools (Week 1)

**1. Gumroad Analytics**
- **What to track:** Sales, revenue, refunds, average order value
- **Cost:** Free (included in 10% fee)
- **Setup time:** 0 (already in place)

**2. Plausible Analytics** (Recommended) or Google Analytics
- **What to track:** Website traffic, traffic sources, conversion funnel
- **Cost:** $9/month (Plausible) or Free (Google Analytics)
- **Setup time:** 15 minutes
- **Implementation:**
  ```html
  <!-- Add to landing page <head> -->
  <script defer data-domain="signkit.work" src="https://plausible.io/js/script.js"></script>
  ```
- **Events to track:**
  - Page view: Landing page
  - Click: "Buy Now" button
  - Click: "Watch Demo" video
  - External link: Social media clicks

**3. UTM Parameters (Traffic Attribution)**
- **Format:** `signkit.work/?ref=[source]&utm_medium=[medium]&utm_campaign=[campaign]`
- **Examples:**
  - Product Hunt: `?ref=producthunt&utm_medium=launch&utm_campaign=nov2025`
  - Twitter: `?ref=twitter&utm_medium=social&utm_campaign=organic`
  - Email: `?ref=email&utm_medium=email&utm_campaign=nurture_sequence`
- **Tool:** UTM.io or Google Campaign URL Builder
- **Setup:** Create master spreadsheet of all UTM links

**4. Email Marketing Analytics (ConvertKit or Mailchimp)**
- **What to track:**
  - Open rate (target: 25-40%)
  - Click rate (target: 5-15%)
  - Unsubscribe rate (target: <1%)
  - Conversion rate (target: 20-30% within 30 days)
- **Cost:** Free (0-1K subscribers)
- **Setup time:** 30 minutes

---

### Optional Tools (Month 2-3)

**5. In-App Analytics (Privacy-Respecting)**
- **What to track:**
  - Feature usage (which features are used most?)
  - Session duration (how long do users spend in app?)
  - Time to first signature extraction
  - Crash reports
- **Recommended:** Build custom analytics (opt-in, anonymous)
  - Store data locally in SQLite
  - Opt-in prompt on first launch: "Help improve SignKit by sharing anonymous usage data?"
  - NO personal data (no emails, no file names)
  - Send weekly summary to server (JSON payload)
- **Alternative (easier):** PostHog (open-source, privacy-focused)
- **Cost:** Free self-hosted or $0-49/month cloud
- **Setup time:** 2-4 hours

**6. Customer Feedback Tool**
- **Options:**
  - Simple: Google Form embedded in app ("Send Feedback")
  - Advanced: Canny (public roadmap + voting)
- **Cost:** Free (Google Forms) or $50/month (Canny)
- **Setup time:** 30 minutes

**7. Heatmap/Session Recording** (Use sparingly, privacy concerns)
- **Tool:** Hotjar or Microsoft Clarity
- **What to track:** Where users click on landing page, scroll depth
- **Cost:** Free tier available
- **Privacy note:** Disclose in privacy policy, avoid recording sensitive data
- **Recommendation:** Use for 30 days post-launch to optimize landing page, then disable

---

## METRICS DASHBOARD (Weekly Review)

### Simple Spreadsheet Template

Create a Google Sheet with tabs:

**Tab 1: Weekly Metrics**

| Week | Sales | Revenue | Visitors | Conversion % | Email Subs | Refunds | NPS |
|------|-------|---------|----------|--------------|------------|---------|-----|
| 1 | 120 | $3,480 | 3,500 | 3.4% | 180 | 2 | 45 |
| 2 | 85 | $2,465 | 2,800 | 3.0% | 120 | 3 | 42 |
| 3 | 95 | $2,755 | 3,200 | 3.0% | 150 | 1 | 48 |
| 4 | 105 | $3,045 | 3,600 | 2.9% | 180 | 4 | 50 |

**Tab 2: Traffic Sources**

| Week | Organic | Social | Product Hunt | Reddit | Email | Direct | Paid |
|------|---------|--------|--------------|--------|-------|--------|------|
| 1 | 500 | 800 | 1,200 | 600 | 200 | 200 | 0 |
| 2 | 700 | 900 | 400 | 500 | 150 | 150 | 0 |
| 3 | 900 | 1,000 | 200 | 600 | 300 | 200 | 0 |

**Tab 3: Feature Adoption** (If tracking in-app analytics)

| Feature | Week 1 Adoption % | Week 2 | Week 3 | Week 4 |
|---------|-------------------|--------|--------|--------|
| PDF Signing | 45% | 52% | 58% | 62% |
| Library Save | 62% | 68% | 70% | 72% |
| Threshold Adjust | 78% | 80% | 82% | 84% |
| Color Picker | 25% | 28% | 30% | 32% |

**Tab 4: Financial**

| Month | Gross Revenue | Gumroad Fees | Net Revenue | Marketing Spend | CAC | LTV:CAC |
|-------|---------------|--------------|-------------|-----------------|-----|---------|
| 1 | $12,000 | $1,200 | $10,800 | $200 | $1.67 | 23.4:1 |
| 2 | $18,500 | $1,850 | $16,650 | $400 | $2.35 | 16.6:1 |
| 3 | $25,000 | $2,500 | $22,500 | $600 | $2.40 | 16.3:1 |

---

## EXPERIMENT FRAMEWORK

### Running A/B Tests

**When to A/B Test:**
- Landing page copy (test at 100+ visitors/day minimum)
- Pricing ($29 vs $39)
- Email subject lines (test with 200+ subscribers)
- Feature UI (test with 50+ active users)

**How to Run Tests:**

**1. Landing Page Pricing Test**
- **Hypothesis:** Pricing at $29 will convert 20% better than $39
- **Variables:**
  - Control: $39 pricing
  - Variant: $29 pricing
- **Split:** 50/50
- **Sample size:** 200 visitors per variant (400 total)
- **Duration:** 7 days or until statistical significance
- **Success metric:** Conversion rate
- **Tool:** Gumroad has built-in variants (if available) or manual split by week

**2. Email Subject Line Test**
- **Hypothesis:** Specific number ("Save 2 hours/week") will beat vague claim ("Save time")
- **Variables:**
  - Control: "Extract signatures faster with SignKit"
  - Variant A: "Save 2 hours per week extracting signatures"
  - Variant B: "Stop wasting time on signatures (Try SignKit)"
- **Split:** 33/33/33
- **Sample size:** 300+ subscribers
- **Success metric:** Open rate, click-through rate
- **Tool:** ConvertKit A/B test feature

**3. Feature Discoverability Test**
- **Hypothesis:** Adding tooltip on first launch will increase feature adoption by 30%
- **Variables:**
  - Control: No tooltip
  - Variant: Tooltip: "Tip: Save signatures to library for quick reuse"
- **Split:** 50/50 (random assignment on first launch)
- **Sample size:** 100+ new users
- **Success metric:** % who use library within 7 days
- **Tool:** In-app analytics with feature flag

---

## COHORT ANALYSIS

### Monthly Cohorts

Track customers by month they purchased:

| Cohort | Month 0 (Purchase) | Month 1 | Month 2 | Month 3 | Month 6 |
|--------|---------------------|---------|---------|---------|---------|
| **Nov 2025** | 120 customers | 8 Pro upgrades (6.7%) | 12 Pro (10%) | 15 Pro (12.5%) | TBD |
| **Dec 2025** | 85 customers | TBD | TBD | TBD | TBD |
| **Jan 2026** | 95 customers | TBD | TBD | TBD | TBD |

**Insights:**
- Which cohort has highest Pro upgrade rate?
- Is there a seasonal pattern (holiday purchases less likely to upgrade)?
- Which marketing channel cohort converts best to Pro?

---

## COMPETITIVE INTELLIGENCE TRACKING

### Monitor Competitors (Monthly)

**Adobe Acrobat:**
- **Metrics to track:**
  - Pricing changes
  - New features announced
  - Marketing campaigns (Google Ads text, social media)
  - App Store review rating (macOS App Store, Microsoft Store)
- **Tools:** Google Alerts, SimilarWeb, App Annie
- **Cadence:** Monthly check

**DocuSign:**
- Same metrics as Adobe
- Focus on: Pricing changes, new extraction features

**Smallpdf, PDF.io, iLovePDF (web tools):**
- **Metrics:** New features, pricing, SEO rankings
- **Tool:** Ahrefs (track keyword rankings)

**Dashboard:**

| Competitor | Current Price | Our Advantage | Threat Level |
|------------|---------------|---------------|--------------|
| Adobe Acrobat | $19.99/mo ($240/yr) | 85% cheaper, offline | Low (no extraction focus) |
| DocuSign | $10/mo ($120/yr) | 75% cheaper, desktop | Low (e-signature focus) |
| Smallpdf | $12/mo ($144/yr) | 80% cheaper, privacy | Medium (web competitor) |
| **New Entrant?** | TBD | TBD | Monitor monthly |

---

## ALERTS & AUTOMATION

### Automated Weekly Email Digest

Set up Zapier (or custom script) to email you every Monday:

**Subject:** SignKit Weekly Metrics - Week of [Date]

**Body:**
```
Weekly Summary:

📊 SALES:
- Sales this week: 95 (+10% vs last week)
- Revenue: $2,755 (+12% vs last week)
- Cumulative customers: 320

📈 TRAFFIC:
- Visitors: 3,200 (+8% vs last week)
- Conversion rate: 3.0% (-0.4pp vs last week) ⚠️

📧 EMAIL:
- New subscribers: 150 (+25% vs last week)
- Email open rate: 32% (target: 25-40%) ✅

⚠️ ALERTS:
- Conversion rate dropped below 3.5% - investigate landing page
- 4 refunds this week (4.2% refund rate) - within target but monitor

💡 ACTION ITEMS:
1. A/B test landing page headline (conversion dip)
2. Follow up with refund customers (understand why)
3. Schedule weekly content (2 blog posts, 1 video)

[Link to full dashboard]
```

---

## KEY INSIGHTS TO SURFACE WEEKLY

Ask these questions every Monday:

**1. What's working?**
- Which marketing channel drove the most sales this week?
- Which blog post or social post got the most engagement?
- What positive feedback did we receive?

**2. What's not working?**
- Did any metric decline >20% week-over-week?
- Are we getting the same support question repeatedly? (product issue)
- Did any A/B test fail?

**3. What should we do differently next week?**
- Based on data, where should we invest more time?
- What should we stop doing?
- What experiment should we run?

---

## PRIVACY & ETHICS

### Data Collection Principles

**1. Transparency:**
- Clearly state what data we collect (in Privacy Policy)
- Explain why we collect it (improve product)
- Provide opt-out for in-app analytics

**2. Minimalism:**
- Collect only what's needed
- Never collect: file names, signature images, personal documents
- Only collect: feature usage counts, session duration, crash reports

**3. Security:**
- Encrypt data in transit (HTTPS)
- Anonymize user IDs (hash email addresses)
- Store minimal data (delete after 90 days if not needed)

**4. User Control:**
- In-app toggle: "Share anonymous usage data to improve SignKit"
- Default: OFF (user must opt-in)
- Respect Do Not Track browser header

---

## QUARTERLY BUSINESS REVIEW (QBR) Template

**Every 3 months (Dec, Mar, Jun, Sep), prepare:**

### Q1 Review (Dec 2025 - Feb 2026)

**Headline Metrics:**
- Total customers: [X]
- Total revenue: $[X]
- MRR: $[X]
- NPS: [X]

**What Worked:**
- [Channel/feature] drove [X%] of sales
- [Campaign] converted at [X%]
- Customer feedback: [top positive theme]

**What Didn't Work:**
- [Feature/channel] underperformed expectations
- [Metric] missed target by [X%]
- Customer complaints: [top negative theme]

**Learnings:**
- [Insight 1]
- [Insight 2]
- [Insight 3]

**Q2 Priorities:**
- [Top 3 focus areas based on data]

---

## SUMMARY: Metrics to Check Daily

**Every morning (5 minutes):**
1. Gumroad dashboard - sales yesterday
2. Support inbox - any urgent issues
3. Twitter mentions - respond to comments

**Every Monday (30 minutes):**
4. Review weekly dashboard (spreadsheet)
5. Identify 1-2 action items based on data
6. Plan week's content/marketing focus

**Every month (2 hours):**
7. Deep dive into underperforming metrics
8. Review product roadmap (reprioritize based on usage data)
9. Competitive intelligence check

---

**"What gets measured gets managed." - Peter Drucker**

This framework ensures SignKit's growth is data-driven, customer-focused, and sustainable.

---

*Last Updated: November 15, 2025*
*Next Review: Weekly (every Monday morning)*
