# Analytics Improvements for Landing Page

**Date:** November 19, 2025  
**Issue:** Netherlands bot/crawler traffic polluting GA4 data  
**Goal:** Track only real human users, filter out infrastructure noise

---

## 🔍 PROBLEM ANALYSIS

### Current Situation

- Getting lots of traffic from Netherlands
- 0-1 second sessions
- 100% bounce rate
- No scroll, no clicks, no engagement
- Source: Gumroad/gum.new infrastructure + Twitter crawlers

### Root Cause

1. **Gumroad/gum.new EU servers** - API calls, link previews, analytics pings from NL/Germany
2. **Twitter link preview crawlers** - Fetch page for preview cards, hit from EU PoPs
3. **GA4 tracking all hits** - No distinction between bots and humans

### Why This Matters

- Can't tell real users from bots
- Conversion rate calculations are wrong
- Can't optimize what you can't measure accurately

---

## ✅ SOLUTION: Multi-Layer Bot Filtering

### Layer 1: Real User Signal Detection

Add interaction-based tracking that only fires when humans actually engage.

### Layer 2: Bot Filtering in GA4

Configure GA4 to exclude known bots and crawlers.

### Layer 3: Custom Dimensions

Track user type (real vs bot) for better segmentation.

### Layer 4: Clean Dashboard

Create filtered views showing only real user data.

---

## 📝 IMPLEMENTATION PLAN

### Step 1: Add Real User Detection (landing-page branch)

**File to modify:** `index.html` (and all variant HTML files)

**Add this script AFTER your existing GA4 initialization:**

```html
<script>
  // Real User Detection - Only track engaged users
  (function () {
    let realUserDetected = false;
    let engagementTimer = null;

    // Function to mark as real user
    function markRealUser() {
      if (realUserDetected) return;
      realUserDetected = true;

      // Send real user event to GA4
      gtag('event', 'real_user_detected', {
        event_category: 'engagement',
        event_label: 'human_interaction',
        value: 1,
      });

      // Set custom dimension
      gtag('set', 'user_properties', {
        user_type: 'real_human',
      });

      console.log('✅ Real user detected');
    }

    // Detect mouse movement (bots don't move mouse)
    let mouseMoveCount = 0;
    document.addEventListener('mousemove', function () {
      mouseMoveCount++;
      if (mouseMoveCount > 3) {
        markRealUser();
      }
    });

    // Detect scrolling (bots don't scroll)
    let scrollCount = 0;
    window.addEventListener('scroll', function () {
      scrollCount++;
      if (scrollCount > 2) {
        markRealUser();
      }
    });

    // Detect clicks (bots don't click)
    document.addEventListener('click', function () {
      markRealUser();
    });

    // Detect keyboard input (bots don't type)
    document.addEventListener('keydown', function () {
      markRealUser();
    });

    // Detect touch events (mobile users)
    document.addEventListener('touchstart', function () {
      markRealUser();
    });

    // Time on page (real users stay longer than 3 seconds)
    setTimeout(function () {
      if (document.hasFocus()) {
        markRealUser();
      }
    }, 3000);

    // Track engagement time
    let engagementTime = 0;
    setInterval(function () {
      if (document.hasFocus() && realUserDetected) {
        engagementTime += 1;

        // Send engagement milestone events
        if (engagementTime === 10) {
          gtag('event', 'engaged_10s', {
            event_category: 'engagement',
            value: 10,
          });
        } else if (engagementTime === 30) {
          gtag('event', 'engaged_30s', {
            event_category: 'engagement',
            value: 30,
          });
        } else if (engagementTime === 60) {
          gtag('event', 'engaged_60s', {
            event_category: 'engagement',
            value: 60,
          });
        }
      }
    }, 1000);
  })();
</script>
```

### Step 2: Enhanced Bot Detection

**Add this script to detect and label bot traffic:**

```html
<script>
  // Bot Detection
  (function () {
    function isLikelyBot() {
      const ua = navigator.userAgent.toLowerCase();

      // Known bot patterns
      const botPatterns = [
        'bot',
        'crawler',
        'spider',
        'scraper',
        'facebookexternalhit',
        'twitterbot',
        'linkedinbot',
        'slackbot',
        'discordbot',
        'telegrambot',
        'whatsapp',
        'preview',
        'prerender',
        'headless',
        'phantom',
        'selenium',
      ];

      // Check user agent
      for (let pattern of botPatterns) {
        if (ua.includes(pattern)) {
          return true;
        }
      }

      // Check for missing features (bots often lack these)
      if (!navigator.plugins || navigator.plugins.length === 0) {
        if (!navigator.webdriver) {
          // Not a legitimate automation tool
          return true;
        }
      }

      // Check for headless browser
      if (navigator.webdriver === true) {
        return true;
      }

      return false;
    }

    // Label traffic type
    if (isLikelyBot()) {
      gtag('set', 'user_properties', {
        user_type: 'bot_or_crawler',
      });

      gtag('event', 'bot_detected', {
        event_category: 'traffic_quality',
        event_label: navigator.userAgent.substring(0, 100),
      });
    }
  })();
</script>
```

### Step 3: Track Scroll Depth

**Add scroll depth tracking to measure real engagement:**

```html
<script>
  // Scroll Depth Tracking
  (function () {
    let maxScroll = 0;
    const milestones = [25, 50, 75, 90, 100];
    const reached = {};

    function trackScroll() {
      const scrollPercent = Math.round(
        (window.scrollY /
          (document.documentElement.scrollHeight - window.innerHeight)) *
          100
      );

      if (scrollPercent > maxScroll) {
        maxScroll = scrollPercent;
      }

      // Track milestones
      milestones.forEach(function (milestone) {
        if (scrollPercent >= milestone && !reached[milestone]) {
          reached[milestone] = true;
          gtag('event', 'scroll_depth', {
            event_category: 'engagement',
            event_label: milestone + '%',
            value: milestone,
          });
        }
      });
    }

    // Throttle scroll events
    let scrollTimeout;
    window.addEventListener('scroll', function () {
      if (scrollTimeout) {
        clearTimeout(scrollTimeout);
      }
      scrollTimeout = setTimeout(trackScroll, 100);
    });
  })();
</script>
```

### Step 4: Track CTA Clicks

**Enhance button click tracking:**

```html
<script>
  // Enhanced CTA Tracking
  document.addEventListener('DOMContentLoaded', function () {
    // Track all "Buy" button clicks
    const buyButtons = document.querySelectorAll(
      'a[href*="gumroad"], a[href*="gum.new"], button.cta, .buy-button'
    );

    buyButtons.forEach(function (button) {
      button.addEventListener('click', function (e) {
        const buttonText = this.textContent.trim();
        const buttonHref = this.href || 'no-href';

        gtag('event', 'cta_click', {
          event_category: 'conversion',
          event_label: buttonText,
          button_location: buttonHref,
          value: 1,
        });

        console.log('🎯 CTA clicked:', buttonText);
      });
    });

    // Track external link clicks
    const externalLinks = document.querySelectorAll('a[href^="http"]');
    externalLinks.forEach(function (link) {
      link.addEventListener('click', function (e) {
        gtag('event', 'external_link_click', {
          event_category: 'navigation',
          event_label: this.href,
          link_text: this.textContent.trim(),
        });
      });
    });
  });
</script>
```

### Step 5: Session Quality Score

**Calculate and track session quality:**

```html
<script>
  // Session Quality Scoring
  (function () {
    let qualityScore = 0;
    let scoreReported = false;

    function updateQualityScore() {
      qualityScore = 0;

      // Points for real user signals
      if (window.realUserDetected) qualityScore += 30;

      // Points for time on page
      const timeOnPage = Math.floor((Date.now() - window.pageLoadTime) / 1000);
      if (timeOnPage > 5) qualityScore += 10;
      if (timeOnPage > 15) qualityScore += 10;
      if (timeOnPage > 30) qualityScore += 10;

      // Points for scroll depth
      if (window.maxScroll > 25) qualityScore += 10;
      if (window.maxScroll > 50) qualityScore += 10;
      if (window.maxScroll > 75) qualityScore += 10;

      // Points for interactions
      if (window.clickCount > 0) qualityScore += 10;

      return qualityScore;
    }

    // Report quality score on page unload
    window.addEventListener('beforeunload', function () {
      if (!scoreReported) {
        scoreReported = true;
        const finalScore = updateQualityScore();

        gtag('event', 'session_quality', {
          event_category: 'engagement',
          value: finalScore,
          quality_tier:
            finalScore > 50 ? 'high' : finalScore > 20 ? 'medium' : 'low',
        });
      }
    });

    // Also report after 30 seconds for long sessions
    setTimeout(function () {
      if (!scoreReported) {
        const score = updateQualityScore();
        if (score > 30) {
          gtag('event', 'session_quality_checkpoint', {
            event_category: 'engagement',
            value: score,
          });
        }
      }
    }, 30000);
  })();
</script>
```

---

## 🎯 GA4 CONFIGURATION CHANGES

### 1. Enable Bot Filtering

**In GA4 Admin:**

1. Go to **Admin** → **Data Settings** → **Data Filters**
2. Enable **"Exclude all hits from known bots and spiders"**
3. This filters out obvious bots automatically

### 2. Create Custom Dimensions

**Add these custom dimensions:**

1. **user_type**

   - Scope: User
   - Description: Real human vs bot/crawler
   - Values: real_human, bot_or_crawler, unknown

2. **quality_tier**

   - Scope: Event
   - Description: Session quality level
   - Values: high, medium, low

3. **variant**
   - Scope: Session
   - Description: A/B test variant
   - Values: control, root, buy, gum, purchase

### 3. Create Filtered Views

**Create these Explorations in GA4:**

**View 1: Real Users Only**

- Filter: `user_type = real_human`
- Shows only verified human traffic

**View 2: High Quality Sessions**

- Filter: `quality_tier = high OR quality_tier = medium`
- Shows engaged users only

**View 3: Conversion Funnel**

- Steps:
  1. Page view
  2. Real user detected
  3. Scroll > 25%
  4. CTA click
  5. Gumroad redirect

---

## 📊 NEW METRICS TO TRACK

### Real User Metrics

- `real_user_detected` - Count of verified humans
- `engaged_10s`, `engaged_30s`, `engaged_60s` - Time milestones
- `scroll_depth` - How far users scroll
- `cta_click` - Button clicks
- `session_quality` - Overall engagement score

### Bot Metrics

- `bot_detected` - Count of identified bots
- User agent patterns
- Geographic distribution (NL = likely bots)

### Conversion Metrics

- Real user → CTA click rate
- Real user → Gumroad redirect rate
- High quality session → conversion rate

---

## 🚀 DEPLOYMENT STEPS

### On landing-page branch:

1. **Update index.html**

   ```bash
   git checkout landing-page
   # Add all the scripts above to index.html
   ```

2. **Update all variant files**

   - root.html
   - buy.html
   - gum.html
   - purchase.html
   - (Add same scripts to each)

3. **Test locally**

   ```bash
   python3 -m http.server 8001
   # Open http://localhost:8001
   # Check console for "✅ Real user detected"
   # Check GA4 Real-Time for new events
   ```

4. **Deploy**

   ```bash
   git add -A
   git commit -m "Add real user detection and bot filtering"
   git push origin landing-page
   # Cloudflare auto-deploys
   ```

5. **Verify in GA4**
   - Go to Real-Time reports
   - Look for `real_user_detected` events
   - Check `user_type` dimension
   - Verify bot traffic is labeled

---

## 📈 EXPECTED RESULTS

### Before (Current State)

- 100 sessions from Netherlands
- 0-1 second duration
- 100% bounce rate
- Can't tell real from fake

### After (With Improvements)

- 100 sessions total
- 5-10 marked as `real_human`
- 90-95 marked as `bot_or_crawler`
- Clear separation in reports
- Accurate conversion tracking

### Real User Indicators

- `real_user_detected` event fires
- Session duration > 3 seconds
- Scroll depth > 0%
- Mouse movement detected
- Quality score > 20

---

## 🔧 QUICK IMPLEMENTATION

### Minimal Version (5 minutes)

If you want the quickest fix, just add this ONE script:

```html
<script>
  // Minimal Real User Detection
  let realUser = false;
  ['mousemove', 'scroll', 'click', 'touchstart'].forEach(function (event) {
    document.addEventListener(
      event,
      function () {
        if (!realUser) {
          realUser = true;
          gtag('event', 'real_user', {
            event_category: 'engagement',
            value: 1,
          });
        }
      },
      { once: true }
    );
  });
</script>
```

Then in GA4, filter reports by:

- Events where `event_name = real_user`
- This shows only users who interacted

---

## 📝 TESTING CHECKLIST

### Test Real User Detection

- [ ] Open landing page
- [ ] Move mouse → Check console for "✅ Real user detected"
- [ ] Check GA4 Real-Time → See `real_user_detected` event
- [ ] Scroll page → See `scroll_depth` events
- [ ] Click CTA → See `cta_click` event

### Test Bot Detection

- [ ] Check GA4 for Netherlands traffic
- [ ] Filter by `user_type = bot_or_crawler`
- [ ] Verify 0-1 second sessions are labeled as bots
- [ ] Verify real sessions have `user_type = real_human`

### Test Conversion Tracking

- [ ] Complete full purchase flow
- [ ] Verify all events fire in sequence
- [ ] Check conversion funnel in GA4
- [ ] Verify quality score is high (>50)

---

## 🎯 NEXT STEPS

1. **Implement minimal version first** (5 min)

   - Add real user detection script
   - Deploy and test

2. **Add full suite** (30 min)

   - All detection scripts
   - Bot filtering
   - Quality scoring

3. **Configure GA4** (15 min)

   - Enable bot filtering
   - Create custom dimensions
   - Set up filtered views

4. **Monitor for 24 hours**

   - Check real vs bot ratio
   - Verify Netherlands traffic is labeled correctly
   - Adjust thresholds if needed

5. **Create dashboard** (30 min)
   - Real users only view
   - Conversion funnel
   - Quality metrics

---

## 💡 PRO TIPS

### Identifying Real Users

- Session duration > 5 seconds
- Scroll depth > 25%
- Mouse movement detected
- Multiple page interactions
- Quality score > 30

### Identifying Bots

- Session duration < 2 seconds
- No scroll, no clicks
- User agent contains "bot"
- From Netherlands with 0 engagement
- Quality score = 0

### Optimizing for Real Users

- Focus marketing on channels with high real user %
- A/B test variants based on real user conversion
- Ignore bot traffic in decision making
- Use quality score to identify best traffic sources

---

**Ready to implement?** Start with the minimal version and we can add more sophistication as needed.

**Files to modify on landing-page branch:**

- index.html
- root.html
- buy.html
- gum.html
- purchase.html

Let me know if you want me to create the exact code snippets for each file!

## 🧪 My suggestions — deeper verification for Netherlands traffic

Below are detailed, non-code steps to further validate the idea that NL traffic is mostly Gumroad or preview traffic, and to measure any real NL users reliably.

1. Inspect server logs & Cloudflare: export 1-2 days of requests filtered to country='NL' and sort by session length, user agent, referrer.

- Look for UA: facebookexternalhit, Twitterbot, linkedinbot, gumroad links (gum.new, gumroad.com), or obvious headless UAs.
- If you see repeated visits from a short list of UA/IP pairs, those are crawler hits. Add them to the documented 'bot patterns' (ANALYTICS_IMPROVEMENTS.md).

2. Use Gumroad and social preview correlation: Compare the timestamps and UA from the server logs with Gumroad webhooks for a short period; if the shower of traffic right after you posted a link to Gumroad matches preview hits, that confirms the source.

3. Add UTM tags for official Gumroad outbound links — this won't stop preview traffic, but it'll identify actual click-throughs from Gumroad that might be real buyers.

4. GA4 Filtering & dashboards (doc-only): Build a quick Exploration that sets country=NL + event=real_user_detected; this shows real NL sessions without server logs.

5. Use 'preflight' check to avoid opening for real human tracking: when a referrer is `gum.new` or UA indicates `preview`, mark it as `user_type = infrastructure_preview` and also set `bot_detected` — this is safe to implement client-side but we recommend server-side correlation too.

6. Track conversions only from `real_user_detected` sessions: in GA4, use `real_user_detected` as a segment when calculating conversion rates — this will exclude preview traffic from NL.

7. Quarterly review: set a dashboard card for 'anonymous NL sessions' and check if count drops after enabling these protections; if it doesn't, broaden your tracking hypotheses (CDN bots, share links, or ad networks).

8. Test coverage: add a note to the marketing doc that all shared Gumroad URLs should include UTM tags and that we should always check Google Analytics and server logs after a big social promo.

Signature: GitHub Copilot — Raptor mini (analysis note) — 2025-11-19
