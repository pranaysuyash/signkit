# Post-Launch Monitoring Dashboard

**SignKit Metrics & Analytics Guide**

Track what matters, ignore vanity metrics, make data-driven decisions.

---

## 🎯 Executive Dashboard (Daily Check)

**The "3-Minute Morning Review"**

Check these 3 metrics every morning:

1. **💰 Revenue (Yesterday)**: $XXX (goal: $100/day by Month 1)
2. **👥 Active Users (Yesterday)**: XXX (goal: 50/day by Month 1)
3. **🐛 Critical Issues**: X (goal: 0)

**Traffic Light System**:
- 🟢 **Green**: All goals met, no critical issues
- 🟡 **Yellow**: 1-2 metrics below goal, no critical issues
- 🔴 **Red**: Revenue < 50% of goal OR critical bugs

**Action**:
- Green: Keep doing what you're doing
- Yellow: Investigate and adjust
- Red: Drop everything, fix it today

---

## 📊 Key Metrics by Category

### 1. Acquisition Metrics

**How people find you**

| Metric | Definition | Target | Track |
|--------|------------|--------|-------|
| **Website Visitors** | Unique visitors to signkit.work | 500/week → 2K/month | Google Analytics |
| **Traffic Sources** | Where visitors come from | Diversified | GA Sources |
| **Gumroad Views** | Product page views | 200/week → 1K/month | Gumroad Dashboard |
| **Free Trial Downloads** | Desktop app downloads | 100/week → 500/month | Gumroad (free product) |
| **Email Signups** | Newsletter subscribers | 50/week → 200/month | Email provider |

**Weekly Questions**:
- Which channel drove the most traffic?
- Which channel has the best conversion rate?
- Where should we invest more time/money?

### 2. Activation Metrics

**How people use the product**

| Metric | Definition | Target | Track |
|--------|------------|--------|-------|
| **First Extraction** | % who extract first signature | > 50% | App analytics |
| **Time to Value** | Time from install to first extraction | < 5 min | App analytics |
| **Feature Adoption** | % using PDF signing, library, etc. | > 30% | App analytics |
| **Completion Rate** | Upload → Select → Export success | > 40% | App funnel |
| **Error Rate** | Crashes or errors per session | < 5% | Error logging |

**Weekly Questions**:
- Where do users drop off in the workflow?
- Which features are most/least used?
- What errors are users encountering?

### 3. Revenue Metrics

**The money part**

| Metric | Definition | Target | Track |
|--------|------------|--------|-------|
| **Paid Conversions** | Free trial → paid license | 10+ /week | Gumroad sales |
| **Revenue** | Total sales revenue | $300/week → $1.5K/month | Gumroad |
| **Conversion Rate** | % of trial users who buy | > 10% | Gumroad analytics |
| **Average Order Value** | Revenue per customer | $29 (baseline) | Gumroad |
| **Refund Rate** | % requesting refunds | < 3% | Gumroad refunds |

**Weekly Questions**:
- Is conversion rate improving?
- What's the main objection to purchasing?
- Are refunds indicating a quality issue?

### 4. Retention Metrics

**How people stick around**

| Metric | Definition | Target | Track |
|--------|------------|--------|-------|
| **Day 2 Return** | % who come back next day | > 20% | App analytics |
| **Day 7 Return** | % who use within a week | > 15% | App analytics |
| **Day 30 Return** | % active after a month | > 10% | App analytics |
| **Avg Sessions/User** | How often users open app | 3+ per month | App analytics |
| **Churn Rate** | % who stop using | < 10% monthly | App analytics |

**Weekly Questions**:
- Why do users stop using the app?
- What brings users back?
- How can we increase frequency of use?

### 5. Referral & Virality

**Word of mouth**

| Metric | Definition | Target | Track |
|--------|------------|--------|-------|
| **NPS Score** | Net Promoter Score (survey) | > 50 | Manual survey |
| **Social Mentions** | Twitter, Reddit, etc. | 10+ /week | Social listening |
| **Referral Signups** | Users from referral links | 5+ /week | Referral system |
| **Testimonials** | Written reviews/feedback | 2+ /week | Manual collection |
| **K-Factor** | Viral coefficient (users per user) | > 0.5 | Calculated |

**Weekly Questions**:
- What do happy customers say about us?
- What are the common complaints?
- How can we make sharing easier?

### 6. Support & Quality

**Customer happiness**

| Metric | Definition | Target | Track |
|--------|------------|--------|-------|
| **Support Tickets** | Requests per week | < 20 | Email/help desk |
| **Response Time** | Avg time to first response | < 24 hrs | Email metrics |
| **Resolution Time** | Avg time to close ticket | < 48 hrs | Email metrics |
| **Common Issues** | Top 5 problems | Document | Manual tracking |
| **Bug Reports** | Issues per week | < 5 | GitHub Issues |

**Weekly Questions**:
- What are users struggling with?
- Which issues are most common?
- How can we prevent them?

---

## 🔧 Tools & Setup

### Analytics Stack (Minimal Setup)

**Option A: Free & Simple**
- **Website**: Plausible ($9/mo) or Google Analytics (free)
- **Sales**: Gumroad built-in analytics
- **App Usage**: Custom logging to local file
- **Support**: Gmail with labels
- **Dashboard**: Google Sheets (manual updates)

**Option B: Integrated & Automated**
- **Website**: Google Analytics 4
- **Sales**: Gumroad + Zapier → Google Sheets
- **App Usage**: PostHog (free tier) or Mixpanel
- **Support**: Help Scout ($20/mo) or Front
- **Dashboard**: Looker Studio (free) or Tableau

**Recommendation for Launch**: Option A (free/cheap, manual)
**Upgrade at**: 100+ customers OR $5K+ revenue

### Event Tracking Implementation

**Desktop App Events to Track**:

```python
# In desktop_app/analytics.py (create this file)

import json
from datetime import datetime
from pathlib import Path

class Analytics:
    def __init__(self):
        self.enabled = False  # Opt-in only
        self.log_file = Path.home() / ".signkit" / "analytics.log"

    def track_event(self, event_name, properties=None):
        """Track user action"""
        if not self.enabled:
            return

        event = {
            "timestamp": datetime.now().isoformat(),
            "event": event_name,
            "properties": properties or {}
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")

# Events to track
analytics = Analytics()

# App lifecycle
analytics.track_event("app_launched")
analytics.track_event("app_closed", {"session_duration": 300})

# Feature usage
analytics.track_event("image_uploaded", {"file_size": 1024000})
analytics.track_event("signature_extracted", {"threshold": 127})
analytics.track_event("pdf_signed", {"pages": 3})
analytics.track_event("saved_to_library")

# Conversion funnel
analytics.track_event("license_dialog_shown")
analytics.track_event("license_activated", {"plan": "standard"})

# Errors
analytics.track_event("error_occurred", {"error_type": "file_not_found"})
```

**Privacy Note**: Only track with explicit user consent. Add toggle in settings.

### Gumroad Analytics

**Built-in Metrics** (automatically tracked):
- Page views
- Add to cart clicks
- Purchases
- Revenue
- Refunds
- Affiliate conversions

**Custom Tracking** (via URL parameters):
```
https://pranaysuyash.gumroad.com/l/signkit-v1?source=twitter
https://pranaysuyash.gumroad.com/l/signkit-v1?source=producthunt
https://pranaysuyash.gumroad.com/l/signkit-v1?source=reddit
```

Track which channels drive sales!

---

## 📈 Weekly Reporting Template

### Weekly Metrics Report

**Week of**: [Date]

**📊 Overview**
- Revenue: $XXX (±X% vs last week)
- Customers: XX (+X new this week)
- Website Visitors: XXX (±X%)
- Free Downloads: XX

**🎯 Funnel**
- Website → Download: X%
- Download → First Use: X%
- First Use → Purchase: X%
- Overall Conversion: X%

**🏆 Wins**
- [Biggest achievement this week]
- [Customer testimonial]
- [Metric that improved]

**🐛 Issues**
- [Top bug reported]
- [Support request theme]
- [Metric that declined]

**📝 Learnings**
- [Key insight from user feedback]
- [What worked in marketing]
- [What didn't work]

**🎯 Next Week Priorities**
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

**📸 Screenshots**
- [Analytics dashboard]
- [Notable mention/review]

---

## 🎨 Dashboard Design (Google Sheets)

### Tab 1: Executive Summary

**Daily Stats**:
| Date | Revenue | Customers | Users | Support | Notes |
|------|---------|-----------|-------|---------|-------|
| 11/18 | $87 | 3 | 42 | 2 | Launched! |
| 11/19 | $145 | 5 | 68 | 4 | PH spike |

**Weekly Totals**:
| Week | Revenue | New Customers | Total Customers | Growth |
|------|---------|---------------|-----------------|--------|
| 1 | $580 | 20 | 20 | - |
| 2 | $725 | 25 | 45 | +125% |

**Charts**:
- Revenue over time (line chart)
- Conversion funnel (funnel chart)
- Traffic sources (pie chart)

### Tab 2: Acquisition

**Traffic Sources**:
| Source | Visitors | Downloads | Purchases | Conv % |
|--------|----------|-----------|-----------|--------|
| Product Hunt | 450 | 85 | 12 | 14.1% |
| Twitter | 230 | 32 | 4 | 12.5% |
| Reddit | 180 | 28 | 3 | 10.7% |
| Direct | 120 | 18 | 2 | 11.1% |

### Tab 3: Revenue

**Sales Log**:
| Date | Time | Email | Amount | Source | License |
|------|------|-------|--------|--------|---------|
| 11/18 | 10:23 | user@... | $29 | Twitter | ABC123 |

**Revenue Summary**:
- Total Revenue: $XXX
- Avg Order Value: $29
- Refunds: $0 (0%)
- Net Revenue: $XXX

### Tab 4: Support

**Ticket Log**:
| Date | User | Issue | Status | Resolution Time |
|------|------|-------|--------|-----------------|
| 11/18 | user@... | License not working | Closed | 2 hrs |

**Common Issues**:
| Issue | Count | % of Total |
|-------|-------|------------|
| License activation | 8 | 40% |
| Windows install | 5 | 25% |
| Export fails | 4 | 20% |

---

## 🚨 Alerts & Thresholds

### Set Up Automatic Alerts

**Critical Alerts** (immediate action):
- Revenue drops > 50% from yesterday → Slack/email alert
- Error rate > 10% → Email alert
- Refund request → Email notification
- Negative review/mention → Social media alert

**Warning Alerts** (investigate within 24h):
- Conversion rate drops > 20%
- Support tickets spike > 2x average
- Website down > 5 min
- App crashes > 5 reports

**Tools**:
- Google Analytics alerts
- Gumroad email notifications
- Uptime monitoring (UptimeRobot free)
- Social media monitoring (Google Alerts)

---

## 📊 Month-End Review

### Monthly Deep Dive

**1. Financial Health**
- [ ] Revenue vs. target
- [ ] Customer acquisition cost
- [ ] Lifetime value estimate
- [ ] Profitability trajectory
- [ ] Cash runway

**2. Product Health**
- [ ] Feature adoption rates
- [ ] Bug/crash rates
- [ ] Performance metrics
- [ ] User satisfaction (NPS)
- [ ] Roadmap progress

**3. Growth Health**
- [ ] Traffic trends
- [ ] Conversion trends
- [ ] Retention cohorts
- [ ] Viral coefficient
- [ ] Channel performance

**4. Competitive Health**
- [ ] New competitors
- [ ] Feature parity
- [ ] Pricing landscape
- [ ] Market trends
- [ ] Differentiation

**5. Team Health**
- [ ] Workload sustainability
- [ ] Morale/burnout check
- [ ] Skill gaps
- [ ] Resource needs
- [ ] Process improvements

---

## 🎯 Success Milestones

### Track Progress Against Goals

**Launch Week** (Week 1):
- [ ] 10+ paying customers
- [ ] 100+ downloads
- [ ] 500+ website visitors
- [ ] 0 critical bugs
- [ ] Product Hunt Top 10

**Month 1**:
- [ ] 50+ paying customers ($1,450 revenue)
- [ ] 500+ total users
- [ ] 2,000+ website visitors
- [ ] 10+ testimonials
- [ ] < 3% refund rate

**Month 3**:
- [ ] 150+ paying customers ($4,350 revenue)
- [ ] 1,500+ total users
- [ ] 5,000+ website visitors
- [ ] Break-even (revenue > costs)
- [ ] Clear growth trajectory

**Month 6**:
- [ ] 300+ paying customers ($8,700 revenue)
- [ ] Profitable
- [ ] V1.1 shipped
- [ ] First partnership deal
- [ ] Featured in publication

**Year 1**:
- [ ] 1,000+ customers
- [ ] $30K+ revenue
- [ ] Product-market fit validated
- [ ] Sustainable growth channel
- [ ] Team of 2-3 (if needed)

---

## 📝 Data Collection Checklist

### Daily
- [ ] Check Gumroad sales (5 min)
- [ ] Review support inbox (10 min)
- [ ] Monitor social mentions (5 min)
- [ ] Check website analytics (5 min)
- [ ] Update tracking sheet (5 min)

**Total**: 30 min/day

### Weekly
- [ ] Compile weekly report (30 min)
- [ ] Analyze conversion funnel (20 min)
- [ ] Review customer feedback (30 min)
- [ ] Plan next week priorities (30 min)
- [ ] Team sync (if applicable) (30 min)

**Total**: 2 hours/week

### Monthly
- [ ] Deep dive analysis (2 hours)
- [ ] Cohort analysis (1 hour)
- [ ] Competitive research (1 hour)
- [ ] Roadmap review (1 hour)
- [ ] Financial planning (1 hour)

**Total**: 6 hours/month

---

## 🔍 Analysis Techniques

### Cohort Analysis

**Question**: Do customers who signed up in Week 1 stick around longer than Week 2 customers?

**Method**:
1. Group customers by signup week
2. Track their activity over time
3. Compare retention rates

**Example**:
| Cohort | Week 1 | Week 2 | Week 3 | Week 4 |
|--------|--------|--------|--------|--------|
| Nov W1 | 100% | 45% | 32% | 28% |
| Nov W2 | 100% | 52% | 38% | ? |

**Insight**: Week 2 cohort has better retention → investigate why

### Funnel Analysis

**Question**: Where do users drop off in the purchase journey?

**Funnel**:
1. Website visitor: 1000 (100%)
2. Download page: 400 (40%)
3. Downloaded: 200 (20%)
4. Opened app: 150 (15%)
5. Extracted signature: 80 (8%)
6. Saw license dialog: 60 (6%)
7. Purchased: 15 (1.5%)

**Insight**: Biggest drop-off is visitor → download page. Improve messaging!

### A/B Test Analysis

**Question**: Does $19 convert better than $29?

**Setup**:
- 50% see $19 pricing
- 50% see $29 pricing
- Run for 2 weeks minimum

**Results**:
| Variant | Visitors | Purchases | Conv Rate | Revenue |
|---------|----------|-----------|-----------|---------|
| $19 | 500 | 35 | 7.0% | $665 |
| $29 | 500 | 25 | 5.0% | $725 |

**Insight**: $29 makes more revenue despite lower conversion → keep $29

---

## 🎓 Learn from Data

### Questions to Ask Weekly

**Acquisition**:
- Which channel brought the most qualified users?
- What content resonated most?
- Where should I invest more time?

**Activation**:
- What's preventing users from extracting their first signature?
- Which features are confusing?
- How can I simplify the workflow?

**Revenue**:
- Why are people not buying?
- What objections do they have?
- How can I demonstrate value better?

**Retention**:
- Why do users come back (or not)?
- What triggers re-engagement?
- How can I increase frequency?

**Referral**:
- What makes users tell their friends?
- Where are they sharing?
- How can I make sharing easier?

---

## ✅ Launch Day Checklist

**Before Launch**:
- [ ] Google Analytics installed and tested
- [ ] Gumroad webhook configured (optional)
- [ ] Tracking spreadsheet created
- [ ] Social listening alerts set up
- [ ] Support email monitored

**Launch Day**:
- [ ] Baseline metrics screenshot (0 sales, 0 visitors)
- [ ] Check analytics every 2 hours
- [ ] Log every sale in tracking sheet
- [ ] Document every support request
- [ ] Screenshot notable moments

**Week 1**:
- [ ] Daily metrics updates
- [ ] First weekly report compiled
- [ ] Learnings documented
- [ ] Adjust strategy based on data

---

## 🎯 Final Thoughts

**Remember**:
- Metrics are tools, not goals
- Focus on learning, not vanity metrics
- Quality > quantity (especially early on)
- Your first 10 customers teach you more than your next 1000

**Avoid**:
- ❌ Obsessing over hourly stats
- ❌ Comparing to others' launches
- ❌ Tracking too many metrics
- ❌ Analysis paralysis

**Do**:
- ✅ Set aside dedicated time for analysis
- ✅ Act on insights within a week
- ✅ Celebrate small wins
- ✅ Learn from every customer

---

**Good luck with your launch!** 📊🚀

*Questions about metrics? Email: founder@signkit.work*
