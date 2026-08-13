# BFCM Readiness 2025 - Complete Action Plan

**Date:** November 21, 2025  
**Days Until Black Friday:** 7 days  
**Status:** URGENT - Final Week Prep

---

## 🎯 CRITICAL PATH (Next 7 Days)

### TODAY (Nov 21) - Search Console & Sitemaps

#### Google Search Console Setup
**Status:** ✅ Registered  
**Next Steps:**

1. **Verify Domain Ownership** (30 minutes)
   - Go to [Google Search Console](https://search.google.com/search-console)
   - Add property: `signkit.work`
   - Choose verification method:
     - **DNS Verification (Recommended):** Add TXT record to Namecheap
     - **HTML File:** Upload verification file to `web/live/`
     - **HTML Tag:** Add meta tag to `index.html`

2. **Submit Sitemap** (15 minutes)
   ```
   Primary sitemap URL: https://signkit.work/sitemap.xml
   ```
   
   **Create sitemap.xml if not exists:**
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
     <url>
       <loc>https://signkit.work/</loc>
       <lastmod>2025-11-21</lastmod>
       <changefreq>daily</changefreq>
       <priority>1.0</priority>
     </url>
     <url>
       <loc>https://signkit.work/buy.html</loc>
       <lastmod>2025-11-21</lastmod>
       <changefreq>weekly</changefreq>
       <priority>0.9</priority>
     </url>
     <url>
       <loc>https://signkit.work/purchase.html</loc>
       <lastmod>2025-11-21</lastmod>
       <changefreq>weekly</changefreq>
       <priority>0.9</priority>
     </url>
     <url>
       <loc>https://signkit.work/legal/privacy-policy.html</loc>
       <lastmod>2025-11-21</lastmod>
       <changefreq>monthly</changefreq>
       <priority>0.5</priority>
     </url>
     <url>
       <loc>https://signkit.work/legal/terms-of-service.html</loc>
       <lastmod>2025-11-21</lastmod>
       <changefreq>monthly</changefreq>
       <priority>0.5</priority>
     </url>
   </urlset>
   ```

3. **Submit to Search Console**
   - In Search Console, go to Sitemaps section
   - Enter: `sitemap.xml`
   - Click Submit
   - Wait 24-48 hours for indexing

4. **Request Indexing for Key Pages** (Priority)
   - Go to URL Inspection tool
   - Submit these URLs for immediate indexing:
     - `https://signkit.work/`
     - `https://signkit.work/buy.html`
     - `https://signkit.work/purchase.html`

#### Bing Webmaster Tools (Bonus - 20 minutes)
- Register at [Bing Webmaster Tools](https://www.bing.com/webmasters)
- Import from Google Search Console (easiest)
- Submit same sitemap

---

## 📱 APP DIRECTORY SUBMISSIONS

### Tier 1: SUBMIT TODAY (High Impact, Free)

#### 1. Product Hunt
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥🔥🔥 CRITICAL  
**Timeline:** Submit for Nov 28 launch

**Action Items:**
- [ ] Create Product Hunt account
- [ ] Prepare launch post:
  ```
  Title: SignKit - Extract signatures from documents with complete privacy
  
  Tagline: Professional signature extraction tool. Privacy-first, one-time payment.
  
  Description:
  🎉 Black Friday Special: 35% OFF - Just $19!
  
  SignKit extracts signatures from documents with professional precision
  and complete privacy. All processing happens locally on your computer.
  
  ✨ Features:
  • Precision selection with zoom controls
  • Clean PNG export with transparency
  • PDF signing with audit logging
  • 100% local processing (privacy-first)
  • Cross-platform (macOS, Windows, Linux)
  
  💰 Black Friday Deal:
  Regular: $29 | Today: $19 (35% OFF)
  
  🔒 Privacy-First:
  Your documents never leave your device. No cloud uploads, no tracking.
  
  Try it free, then unlock with a one-time payment. No subscriptions!
  ```
- [ ] Upload 5-7 screenshots
- [ ] Upload demo video
- [ ] Schedule for 12:01 AM PST Nov 28
- [ ] Line up 20+ supporters for upvotes

**Resources:**
- Product Hunt Maker Guide: https://www.producthunt.com/makers
- Launch Checklist: https://blog.producthunt.com/how-to-launch-on-product-hunt-7c1843e06399

#### 2. AlternativeTo
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥🔥 HIGH  
**Timeline:** Submit today

**Action Items:**
- [ ] Go to https://alternativeto.net/software/add/
- [ ] List SignKit as alternative to:
  - Adobe Acrobat (signature extraction)
  - DocuSign (signature management)
  - HelloSign (document signing)
  - PDF Expert (PDF tools)
- [ ] Add detailed description
- [ ] Upload screenshots
- [ ] Add tags: pdf, signature, privacy, desktop, mac, windows, linux
- [ ] Link to website and Gumroad

**Why This Matters:**
- High SEO value
- Users actively searching for alternatives
- Permanent listing (not time-limited)

#### 3. Slant
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥🔥 HIGH  
**Timeline:** Submit today

**Action Items:**
- [ ] Go to https://www.slant.co/
- [ ] Search for "signature extraction tools"
- [ ] Add SignKit to relevant questions:
  - "What are the best PDF signature tools?"
  - "What are the best privacy-focused document tools?"
  - "What are the best alternatives to Adobe Acrobat?"
- [ ] Write detailed pros/cons
- [ ] Add to comparisons

#### 4. Capterra
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥🔥 MEDIUM-HIGH  
**Timeline:** Submit today (review takes 1-2 weeks)

**Action Items:**
- [ ] Go to https://www.capterra.com/vendors/sign-up
- [ ] Create vendor account
- [ ] Submit SignKit listing
- [ ] Category: Document Management Software
- [ ] Subcategory: Electronic Signature Software
- [ ] Add detailed description, screenshots, pricing
- [ ] Request reviews from beta users

**Note:** Free listing, but review process takes time. Submit ASAP.

#### 5. G2
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥🔥 MEDIUM-HIGH  
**Timeline:** Submit today (review takes 1-2 weeks)

**Action Items:**
- [ ] Go to https://www.g2.com/products/new
- [ ] Create vendor profile
- [ ] Submit product listing
- [ ] Category: Electronic Signature
- [ ] Add screenshots, features, pricing
- [ ] Invite beta users to leave reviews

**Note:** Reviews are critical on G2. Plan review campaign.

### Tier 2: SUBMIT THIS WEEK (Medium Impact, Free)

#### 6. MacUpdate
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥 MEDIUM  
**Timeline:** Submit by Nov 23

**Action Items:**
- [ ] Go to https://www.macupdate.com/developer/submit
- [ ] Submit macOS version
- [ ] Add detailed description
- [ ] Upload .dmg file
- [ ] Add screenshots
- [ ] Set pricing: $29 (mention BF deal in description)

**Why This Matters:**
- Mac-specific audience
- Good for SEO
- Users actively searching for Mac apps

#### 7. MacWorld App Directory
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥 MEDIUM  
**Timeline:** Submit by Nov 23

**Action Items:**
- [ ] Contact MacWorld: https://www.macworld.com/about/contact
- [ ] Pitch for app directory inclusion
- [ ] Mention Black Friday launch
- [ ] Offer review copy

#### 8. Softpedia
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥 MEDIUM  
**Timeline:** Submit by Nov 24

**Action Items:**
- [ ] Go to https://www.softpedia.com/get/Submit-Software.shtml
- [ ] Submit for all platforms (Mac, Windows, Linux)
- [ ] Add detailed description
- [ ] Upload installers
- [ ] Add screenshots

#### 9. SourceForge
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥 LOW-MEDIUM  
**Timeline:** Submit by Nov 24

**Action Items:**
- [ ] Go to https://sourceforge.net/
- [ ] Create project page
- [ ] Upload releases
- [ ] Add documentation
- [ ] Set up download tracking

**Note:** Good for open-source credibility if you open-source parts.

#### 10. FileHorse
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥 LOW-MEDIUM  
**Timeline:** Submit by Nov 24

**Action Items:**
- [ ] Go to https://www.filehorse.com/submit-software/
- [ ] Submit for Mac and Windows
- [ ] Add screenshots and description

### Tier 3: NICHE DIRECTORIES (Submit After Launch)

#### 11. Privacy Tools Directory
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥 MEDIUM (Niche)  
**Timeline:** Week of Nov 25

**Action Items:**
- [ ] Submit to https://www.privacytools.io/
- [ ] Emphasize offline processing
- [ ] Highlight privacy features
- [ ] No cloud, no tracking angle

#### 12. Awesome Privacy (GitHub)
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥 LOW-MEDIUM  
**Timeline:** Week of Nov 25

**Action Items:**
- [ ] Fork https://github.com/pluja/awesome-privacy
- [ ] Add SignKit to Document Tools section
- [ ] Submit pull request
- [ ] Engage with community

#### 13. Legal Tech Directories
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥 MEDIUM (B2B)  
**Timeline:** December

**Directories:**
- LawSites: https://www.lawsitesblog.com/
- Legal Technology Resource Center
- ABA Legal Technology Resource Center

**Action Items:**
- [ ] Research submission process
- [ ] Prepare legal use case materials
- [ ] Submit after gathering testimonials

#### 14. Real Estate Software Directories
**Status:** 🔴 NOT SUBMITTED  
**Impact:** 🔥 MEDIUM (B2B)  
**Timeline:** December

**Directories:**
- BiggerPockets Tools
- Real Estate Technology Directory
- NAR Technology Directory

### Tier 4: PAID/PREMIUM (Consider After Revenue)

#### 15. AppSumo
**Status:** 🔴 NOT APPLIED  
**Impact:** 🔥🔥🔥 VERY HIGH  
**Timeline:** Apply in December

**Action Items:**
- [ ] Apply at https://appsumo.com/partners/
- [ ] Prepare lifetime deal offer
- [ ] Wait for approval (selective)
- [ ] Plan for 100-500 sales if accepted

**Note:** 30% fee but massive audience. Apply after initial traction.

#### 16. StackSocial
**Status:** 🔴 NOT APPLIED  
**Impact:** 🔥🔥 HIGH  
**Timeline:** Apply in December

**Action Items:**
- [ ] Apply at https://stacksocial.com/sell
- [ ] Similar to AppSumo
- [ ] Good for deals and bundles

---

## 🎨 MARKETING ASSETS STATUS

### Screenshots
**Status:** ✅ COMPLETE (in `screenshots_final/`)  
**Action:** Verify all are optimized and < 500KB each

### Demo Video
**Status:** 🔴 NEEDS CREATION  
**Priority:** 🔥🔥🔥 CRITICAL

**Action Items:**
- [ ] Record 60-90 second demo
- [ ] Show: Load document → Select signature → Export → Sign PDF
- [ ] Add text overlays for key features
- [ ] Export in 1080p
- [ ] Upload to YouTube (unlisted for now)
- [ ] Embed on landing page

**Script:**
```
0:00-0:10: Hook - "Extract signatures in 30 seconds"
0:10-0:20: Problem - "Tired of messy signature extraction?"
0:20-0:50: Solution - Demo of extraction process
0:50-1:10: Features - Privacy, PDF signing, library
1:10-1:30: CTA - "Try free, buy for $19 today"
```

### Landing Page
**Status:** ⚠️ NEEDS BF BANNER  
**Priority:** 🔥🔥🔥 CRITICAL

**Action Items:**
- [ ] Add Black Friday banner to `web/live/index.html`
- [ ] Add countdown timer
- [ ] Update pricing: ~~$29~~ $19
- [ ] Add urgency messaging
- [ ] Test on mobile
- [ ] Deploy to production

**Banner Design:**
```html
<div class="bf-banner">
  🎉 BLACK FRIDAY SPECIAL: 35% OFF - Just $19! 
  <span class="countdown">Ends in: [TIMER]</span>
</div>
```

### Social Media Graphics
**Status:** 🔴 NEEDS CREATION  
**Priority:** 🔥🔥 HIGH

**Needed:**
- [ ] Black Friday announcement (1200x630)
- [ ] Feature highlights (1080x1080) - 3 variations
- [ ] Demo GIF (for Twitter/Reddit)
- [ ] Product Hunt thumbnail
- [ ] Email header graphic

**Tools:**
- Canva (free templates)
- Figma (if you have design skills)
- Screenshot + text overlay

---

## 📧 EMAIL & SOCIAL PREP

### Email Sequences
**Status:** 🔴 NEEDS WRITING  
**Priority:** 🔥🔥 HIGH

**Sequence:**
1. **Nov 26 (T-2):** "Black Friday Preview - 35% OFF SignKit"
2. **Nov 28 (Launch):** "🎉 Black Friday is HERE - Get SignKit for $19"
3. **Nov 30 (T-2):** "Last 48 hours - Black Friday ends Monday"
4. **Dec 1 (Final):** "⏰ Final Hours - Cyber Monday ends tonight"

**Action Items:**
- [ ] Write all 4 emails
- [ ] Set up in email platform (Mailchimp/ConvertKit)
- [ ] Schedule sends
- [ ] Test on mobile

### Social Media Posts
**Status:** 🔴 NEEDS WRITING  
**Priority:** 🔥🔥 HIGH

**Platforms:**
- Twitter/X
- LinkedIn
- Reddit (various subreddits)
- Facebook groups
- Hacker News

**Action Items:**
- [ ] Write launch tweet thread
- [ ] Prepare Reddit posts (5 variations for different subreddits)
- [ ] Write LinkedIn post
- [ ] Prepare Hacker News "Show HN" post
- [ ] Schedule where possible

---

## 🔍 SEO OPTIMIZATION

### On-Page SEO
**Status:** ⚠️ NEEDS REVIEW  
**Priority:** 🔥 MEDIUM

**Action Items:**
- [ ] Add meta descriptions to all pages
- [ ] Optimize title tags:
  - Home: "SignKit - Extract Signatures with Complete Privacy | $19 Black Friday"
  - Buy: "Buy SignKit - Professional Signature Extraction Tool"
- [ ] Add Open Graph tags for social sharing
- [ ] Add Twitter Card tags
- [ ] Add structured data (Schema.org):
  ```json
  {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "SignKit",
    "operatingSystem": "macOS, Windows, Linux",
    "applicationCategory": "BusinessApplication",
    "offers": {
      "@type": "Offer",
      "price": "19.00",
      "priceCurrency": "USD"
    }
  }
  ```

### robots.txt
**Status:** ⚠️ NEEDS VERIFICATION  
**Action Items:**
- [ ] Create/verify `robots.txt`:
  ```
  User-agent: *
  Allow: /
  Sitemap: https://signkit.work/sitemap.xml
  ```

---

## 📊 ANALYTICS SETUP

### Google Analytics 4
**Status:** ✅ CONFIGURED  
**Action Items:**
- [ ] Verify tracking on all pages
- [ ] Set up conversion goals:
  - Goal 1: Click "Buy Now" button
  - Goal 2: Visit Gumroad checkout
  - Goal 3: Purchase completed (if trackable)
- [ ] Set up UTM parameters for all marketing links
- [ ] Test in real-time view

### Microsoft Clarity
**Status:** ✅ CONFIGURED  
**Action Items:**
- [ ] Verify heatmaps are recording
- [ ] Set up session recordings
- [ ] Review user flows

### Gumroad Analytics
**Status:** ⚠️ NEEDS SETUP  
**Action Items:**
- [ ] Enable Gumroad analytics
- [ ] Set up webhook for purchase notifications
- [ ] Connect to Zapier (optional) for automation

---

## 🎯 LAUNCH DAY CHECKLIST (Nov 28)

### Pre-Launch (12:00 AM - 8:00 AM EST)
- [ ] 12:01 AM: Product Hunt goes live
- [ ] 12:05 AM: Verify PH listing is live
- [ ] 12:10 AM: Share PH link on Twitter
- [ ] 12:15 AM: Post in relevant Slack/Discord communities
- [ ] 8:00 AM: Send launch email to list
- [ ] 8:30 AM: Post on Reddit (r/SideProject)

### Morning (8:00 AM - 12:00 PM EST)
- [ ] 9:00 AM: Post on Twitter (main thread)
- [ ] 9:30 AM: Post on LinkedIn
- [ ] 10:00 AM: Post on Hacker News (if appropriate)
- [ ] 10:30 AM: Post on Reddit (r/macapps)
- [ ] 11:00 AM: Engage with all comments/questions
- [ ] 11:30 AM: Share first milestone (if any sales)

### Afternoon (12:00 PM - 6:00 PM EST)
- [ ] Monitor Product Hunt ranking
- [ ] Respond to all comments within 1 hour
- [ ] Share customer testimonials
- [ ] Post updates on social media
- [ ] Monitor analytics dashboard
- [ ] Check for any technical issues

### Evening (6:00 PM - 11:59 PM EST)
- [ ] Post on more Reddit communities
- [ ] Share demo video clips
- [ ] Engage with Product Hunt community
- [ ] Prepare next day's content
- [ ] Review day's metrics
- [ ] Plan adjustments for Day 2

---

## 🚨 EMERGENCY CONTACTS & BACKUP PLANS

### Technical Issues
**If website goes down:**
- [ ] Cloudflare status check
- [ ] Namecheap DNS check
- [ ] Have backup landing page ready
- [ ] Post status updates on social media

**If Gumroad has issues:**
- [ ] Have LemonSqueezy account ready as backup
- [ ] Can manually process orders if needed
- [ ] Communicate delays transparently

### Support Plan
**Expected volume:** 10-50 support requests on launch day

**Preparation:**
- [ ] Create FAQ document
- [ ] Prepare canned responses for common questions
- [ ] Set up support email monitoring
- [ ] Have license key backup system ready

**Common Questions:**
1. How do I download after purchase?
2. License key not working
3. Installation issues
4. Feature requests
5. Refund requests

---

## 📈 SUCCESS METRICS

### Day 1 Goals (Nov 28)
- [ ] 50+ Product Hunt upvotes
- [ ] 1,000+ website visits
- [ ] 20+ sales ($380 revenue)
- [ ] 10+ testimonials/reviews
- [ ] Product Hunt top 20

### Week 1 Goals (Nov 28 - Dec 4)
- [ ] 150+ sales ($2,850 revenue)
- [ ] 5,000+ website visits
- [ ] 50+ email subscribers
- [ ] Product Hunt top 10
- [ ] Featured on 1-2 blogs

### Month 1 Goals (Nov 28 - Dec 28)
- [ ] 300+ sales ($8,700 revenue)
- [ ] 10,000+ website visits
- [ ] 200+ email subscribers
- [ ] 5+ blog features
- [ ] 4.5+ star rating

---

## 💰 REVENUE PROJECTIONS

### Conservative (Minimum Success)
- Week 1: 50 sales × $19 = $950
- Month 1: 100 sales × $24 avg = $2,400
- **Total: $3,350**

### Realistic (Good Success)
- Week 1: 150 sales × $19 = $2,850
- Month 1: 250 sales × $25 avg = $6,250
- **Total: $9,100**

### Optimistic (Home Run)
- Week 1: 300 sales × $19 = $5,700
- Month 1: 500 sales × $26 avg = $13,000
- **Total: $18,700**

---

## ✅ DAILY TASK BREAKDOWN

### Friday, Nov 22
- [ ] Complete sitemap.xml and submit to Search Console
- [ ] Submit to AlternativeTo, Slant, Capterra, G2
- [ ] Create demo video
- [ ] Write email sequences
- [ ] Design Black Friday banner

### Saturday, Nov 23
- [ ] Submit to MacUpdate, Softpedia, SourceForge
- [ ] Create social media graphics
- [ ] Write all social media posts
- [ ] Set up Product Hunt listing (don't publish yet)
- [ ] Test purchase flow end-to-end

### Sunday, Nov 24
- [ ] Add BF banner to landing page
- [ ] Deploy landing page updates
- [ ] Schedule email sequences
- [ ] Prepare Reddit posts
- [ ] Final QA testing

### Monday, Nov 25
- [ ] Submit to remaining directories
- [ ] Schedule Product Hunt launch for Nov 28
- [ ] Pre-schedule social media posts
- [ ] Send "coming soon" teaser email
- [ ] Final checklist review

### Tuesday, Nov 26
- [ ] Send "24 hours until BF" email
- [ ] Post final teaser on social media
- [ ] Verify all systems are go
- [ ] Get good sleep!

### Wednesday, Nov 27
- [ ] Light promotion
- [ ] Monitor systems
- [ ] Prepare for launch day
- [ ] Final prep

### Thursday, Nov 28 - LAUNCH DAY! 🚀
- [ ] Execute launch day checklist (see above)
- [ ] Monitor 24/7
- [ ] Engage with community
- [ ] Celebrate first sales!

---

## 🎁 BONUS: POST-BFCM PLAN

### Week 2 (Dec 5-11)
- [ ] Send thank you email to customers
- [ ] Request testimonials and reviews
- [ ] Analyze what worked/didn't
- [ ] Plan regular pricing strategy
- [ ] Continue marketing momentum

### Week 3-4 (Dec 12-25)
- [ ] Holiday promotion ($24 special)
- [ ] "Best of 2025" submissions
- [ ] Build email list
- [ ] Gather feature requests
- [ ] Plan v1.1 updates

### January 2026
- [ ] New Year productivity push
- [ ] Regular price ($29)
- [ ] Content marketing
- [ ] SEO optimization
- [ ] Community building

---

## 📞 NEED HELP?

**Resources:**
- Product Hunt Launch Guide: https://blog.producthunt.com/how-to-launch-on-product-hunt-7c1843e06399
- Google Search Console Help: https://support.google.com/webmasters
- Gumroad Creator Guide: https://help.gumroad.com/

**Community:**
- Indie Hackers: https://www.indiehackers.com/
- r/SideProject: https://reddit.com/r/SideProject
- Product Hunt Makers: https://www.producthunt.com/makers

---

**Last Updated:** November 21, 2025  
**Status:** 🔴 URGENT - 7 days until launch  
**Next Review:** Daily until launch

🚀 **LET'S MAKE THIS LAUNCH AMAZING!**
