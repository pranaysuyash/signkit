# 🚀 5 CRITICAL TASKS - DO RIGHT NOW

> **⚠️ PARTIALLY OBSOLETE - November 27, 2025**  
> This document was created for pre-launch tasks (November 22, 2025).  
> **Product has since launched.**  
> Some tasks completed (Analytics, GSC), others still relevant (directories, content).  
> For current priorities, see: `docs/CURRENT_STATUS_NOV_27_2025.md`  
> Keeping for reference - some tasks still applicable.

---

**Date:** November 22, 2025  
**Days Until Launch:** 6 days  
**Total Time:** 6.5 hours

---

## ⚡ Task 1: Google Search Console & Sitemap (30 min) 🔥🔥🔥

**Why:** You're 6 days from launch and not indexed by Google yet.

### Steps:
1. Go to https://search.google.com/search-console
2. Add property: `signkit.work`
3. Choose DNS verification
4. Add TXT record to Namecheap DNS
5. Wait 5-10 minutes, click "Verify"
6. Go to Sitemaps section
7. Submit: `sitemap.xml`
8. Use URL Inspection tool to request indexing for:
   - https://signkit.work/
   - https://signkit.work/buy.html
   - https://signkit.work/purchase.html

### Success Criteria:
- ✅ Domain verified in Search Console
- ✅ Sitemap submitted successfully
- ✅ Key pages requested for indexing

---

## ⚡ Task 2: Product Hunt Launch Prep (1 hour) 🔥🔥🔥

**Why:** Product Hunt is your biggest traffic source for launch day (Nov 28).

### Steps:
1. Finalize Product Hunt listing (don't publish yet)
2. Upload 5-7 screenshots from `screenshots_final/`
3. Write compelling description:

```
Title: SignKit - Extract signatures with complete privacy

Tagline: Professional signature extraction. Privacy-first, one-time payment.

Description:
🚀 Launch Special: $19 (increases to $20 on Jan 1st)

SignKit extracts signatures from documents with professional precision
and complete privacy. All processing happens locally on your computer.

✨ Features:
• Precision selection with zoom controls
• Clean PNG export with transparency  
• PDF signing with audit logging
• 100% local processing (privacy-first)
• Cross-platform (macOS, Windows, Linux)

💰 Progressive Pricing:
Launch: $19 (until Dec 31)
Then: +$1 every 3 months
Target: $29 by end of 2027

🔒 Privacy-First:
Your documents never leave your device. No cloud uploads, no tracking.

Try it free, then unlock with a one-time payment. No subscriptions!
```

4. Schedule for 12:01 AM PST Nov 28
5. Line up 20+ supporters for upvotes

### Success Criteria:
- ✅ Product Hunt listing complete
- ✅ Screenshots uploaded
- ✅ Launch scheduled for Nov 28
- ✅ 20+ supporters ready

---

## ⚡ Task 3: Demo Video Creation (2 hours) 🔥🔥🔥

**Why:** Needed for Product Hunt, landing page, and all directory submissions.

### Script (60-90 seconds):
```
0:00-0:10: Hook
"Extract signatures in 30 seconds with complete privacy"

0:10-0:20: Problem
"Tired of messy signature extraction and privacy concerns?"

0:20-0:50: Solution Demo
- Load document
- Select signature with precision tools
- Export clean PNG
- Sign PDF with audit trail

0:50-1:10: Features
- 100% local processing
- No cloud uploads
- Cross-platform
- One-time payment

1:10-1:30: CTA
"Launch special: $19 (increases to $20 on Jan 1st)
Try free, buy once, own forever"
```

### Steps:
1. Record screen demo (use QuickTime/OBS)
2. Add text overlays for key features
3. Export in 1080p
4. Upload to YouTube (unlisted)
5. Embed on landing page

### Success Criteria:
- ✅ 60-90 second demo video
- ✅ Shows key workflow
- ✅ Uploaded to YouTube
- ✅ Embedded on landing page

---

## ⚡ Task 4: Landing Page Updates (1 hour) 🔥🔥

**Why:** Your landing page needs launch pricing and urgency messaging.

### Updates Needed:

#### 1. Hero Section
```html
<div class="pricing-hero">
  <div class="price-badge">
    <span class="current-price">$19</span>
    <span class="future-price">Regular: $29+</span>
  </div>
  <div class="urgency-message">
    🚀 Launch pricing ends December 31st
    <br>
    Price increases to $20 on January 1st
  </div>
</div>
```

#### 2. Pricing Section
```
💰 Transparent Pricing

Launch Price: $19 (until Dec 31, 2025)
Future Price: Increases $1 every 3 months
Target Price: $29 by end of 2027

✓ One-time payment
✓ No subscriptions
✓ Lifetime updates
✓ Lock in your price forever
```

#### 3. CTA Buttons
Update all "Buy Now" buttons:
- Text: "Get SignKit for $19"
- Subtext: "Price increases Jan 1st"

### Steps:
1. Update `web/live/index.html`
2. Add launch pricing banner
3. Update pricing section
4. Update all CTA buttons
5. Test on mobile
6. Deploy to production

### Success Criteria:
- ✅ Launch pricing displayed
- ✅ Urgency messaging added
- ✅ Mobile responsive
- ✅ Deployed to signkit.work

---

## ⚡ Task 5: Top 4 Directory Submissions (2 hours) 🔥🔥

**Why:** These drive immediate traffic and SEO value.

### 5.1 AlternativeTo (30 min)
1. Go to https://alternativeto.net/software/add/
2. Fill form:
   - Name: SignKit
   - Category: Office & Productivity > Document Management
   - Description: Professional signature extraction with complete privacy. 100% local processing, no cloud uploads. One-time payment of $19 (launch special).
   - Website: https://signkit.work
   - Platforms: macOS, Windows, Linux
   - License: Commercial ($19)
3. Upload 5 screenshots
4. Add as alternative to: Adobe Acrobat, DocuSign, HelloSign, PDF Expert
5. Add tags: pdf, signature, privacy, desktop, mac, windows, linux
6. Submit

### 5.2 Slant (30 min)
1. Go to https://www.slant.co/
2. Create account
3. Search: "What are the best PDF signature tools?"
4. Click "Add option"
5. Add SignKit with pros/cons:
   - Pros: Privacy-first, local processing, one-time payment, cross-platform
   - Cons: New product, limited integrations
6. Repeat for:
   - "What are the best privacy-focused document tools?"
   - "What are the best alternatives to Adobe Acrobat?"

### 5.3 Capterra (45 min)
1. Go to https://www.capterra.com/vendors/sign-up
2. Create vendor account
3. Submit SignKit listing:
   - Category: Document Management Software
   - Subcategory: Electronic Signature Software
   - Price: $19 (one-time)
   - Description: Full feature list
4. Upload screenshots
5. Add pricing details
6. Submit for review (takes 1-2 weeks)

### 5.4 G2 (45 min)
1. Go to https://www.g2.com/products/new
2. Create vendor profile
3. Submit product listing:
   - Category: Electronic Signature
   - Price: $19 (one-time)
   - Features: Full list
4. Upload screenshots
5. Add company info
6. Submit for review (takes 1-2 weeks)

### Success Criteria:
- ✅ AlternativeTo submission confirmed
- ✅ Slant has SignKit listed
- ✅ Capterra submission pending review
- ✅ G2 submission pending review

---

## ✅ Completion Checklist

After completing all 5 tasks:

- [ ] Google Search Console verified
- [ ] Sitemap submitted
- [ ] Product Hunt listing ready (scheduled for Nov 28)
- [ ] Demo video created and embedded
- [ ] Landing page updated with launch pricing
- [ ] AlternativeTo submission confirmed
- [ ] Slant listing live
- [ ] Capterra submission pending
- [ ] G2 submission pending

---

## 📊 Impact Assessment

### Immediate Impact (Week 1)
- **SEO:** Google indexing begins
- **Traffic:** 4 directory listings = 100-500 visits
- **Conversions:** Product Hunt = 20-100 sales

### Medium-term Impact (Month 1)
- **SEO:** Improved rankings from backlinks
- **Traffic:** 1,000-5,000 visits from directories
- **Conversions:** 50-200 sales at $19

### Long-term Impact (Year 1)
- **SEO:** Strong domain authority
- **Traffic:** 10,000+ visits from organic + directories
- **Revenue:** $7,000-30,000 depending on execution

---

## ⏰ Time Breakdown

| Task | Time | Priority |
|------|------|----------|
| 1. Google Search Console | 30 min | 🔥🔥🔥 |
| 2. Product Hunt Prep | 1 hour | 🔥🔥🔥 |
| 3. Demo Video | 2 hours | 🔥🔥🔥 |
| 4. Landing Page Updates | 1 hour | 🔥🔥 |
| 5. Directory Submissions | 2 hours | 🔥🔥 |
| **TOTAL** | **6.5 hours** | |

---

## 🎯 Success Metrics

### Today's Goals
- [ ] All 5 tasks completed
- [ ] Launch-ready by end of day
- [ ] 6 days ahead of schedule

### Launch Day Goals (Nov 28)
- [ ] 50+ Product Hunt upvotes
- [ ] 1,000+ website visits
- [ ] 20+ sales at $19
- [ ] Product Hunt top 20

### Week 1 Goals
- [ ] 150+ sales ($2,850 revenue)
- [ ] 5,000+ website visits
- [ ] 50+ email subscribers
- [ ] Featured on 1-2 blogs

---

**START NOW! Begin with Task 1 (Google Search Console) - it's the most important!**

