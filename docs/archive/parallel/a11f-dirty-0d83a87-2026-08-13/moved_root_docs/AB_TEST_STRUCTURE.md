# SignKit A/B Test Structure

## Overview

4 variants testing different checkout flows to optimize conversion rate.

## Variants

### Variant 1: Control (Root) - `/root`
**File:** `root.html`  
**Design:** Neo-brutalism  
**CTA:** External link to Gumroad  
**Hypothesis:** Clean, privacy-focused design with external checkout

**Key Features:**
- Bold neo-brutalism aesthetic
- Privacy-first messaging
- Direct external Gumroad link
- Simple, fast-loading page

**Tracking:**
```javascript
variant: 'control'
experiment_id: 'checkout_flow_test'
```

---

### Variant 2: Embedded Checkout - `/buy`
**File:** `buy.html`  
**Design:** Full-page iframe  
**CTA:** Embedded Gumroad checkout  
**Hypothesis:** Keeping users on domain increases trust and conversion

**Key Features:**
- Full-page iframe experience
- No navigation away from signkit.work
- Seamless checkout flow
- Loading indicator for UX

**Tracking:**
```javascript
variant: 'buy'
experiment_id: 'checkout_flow_test'
```

**Technical Details:**
- Iframe URL: `https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj`
- Full viewport height/width
- Payment permission enabled
- Loading state with spinner

---

### Variant 3: SaaS Landing - `/purchase`
**File:** `purchase.html`  
**Design:** Claude v2 (traditional SaaS)  
**CTA:** External link to Gumroad  
**Hypothesis:** Detailed feature showcase increases perceived value

**Key Features:**
- Animated hero section
- Detailed feature tabs
- Social proof elements
- Problem-solution framework
- Comprehensive FAQ
- Multiple CTAs throughout

**Tracking:**
```javascript
variant: 'purchase'
experiment_id: 'checkout_flow_test'
```

**Dependencies:**
- `web/live/css/style.css`
- `web/live/css/animations.css`
- `web/live/js/main.js`
- `web/live/js/animations.js`

---

### Variant 4: Direct Redirect - `/gum`
**File:** `gum.html`  
**Design:** Immediate redirect  
**CTA:** Instant redirect to Gumroad  
**Hypothesis:** Minimal friction for users with high intent

**Key Features:**
- Instant redirect (no landing page)
- Lowest possible friction
- Tests direct purchase intent
- Minimal page load

**Tracking:**
```javascript
variant: 'gum'
experiment_id: 'checkout_flow_test'
```

**Technical Details:**
- Immediate `window.location.href` redirect
- Redirect to: `https://pranaysuyash.gumroad.com/l/signkit-v1`
- Tracks impression before redirect

---

## Routing Logic

### Manual Mode (Current: `AUTO_SPLIT = false`)

```
/           → Shows control page (index.html)
/root       → Shows control page (root.html)
/buy        → Shows embedded checkout (buy.html)
/purchase   → Shows SaaS landing (purchase.html)
/gum        → Redirects to Gumroad (gum.html)
```

Users can manually access any variant via direct URL.

### Auto A/B Mode (`AUTO_SPLIT = true`)

```
/           → Randomly assigns to one of 4 variants (25% each)
              Stores in localStorage for consistency
              Redirects to assigned variant

/root       → Always shows control (no redirect)
/buy        → Always shows embedded checkout (no redirect)
/purchase   → Always shows SaaS landing (no redirect)
/gum        → Always redirects to Gumroad (no redirect)
```

Direct URLs always work regardless of AUTO_SPLIT setting.

---

## Traffic Distribution (When AUTO_SPLIT = true)

```
Root (/)
  ├── 25% → /root (control)
  ├── 25% → /buy (embedded)
  ├── 25% → /purchase (SaaS)
  └── 25% → /gum (redirect)
```

**Persistence:** Variant stored in `localStorage.ab_variant`

**Consistency:** Same user always sees same variant

---

## Metrics to Track

### Primary Metric
- **Conversion Rate:** Purchases / Unique Visitors

### Secondary Metrics
- **Click-through Rate:** CTA Clicks / Page Views
- **Bounce Rate:** Single-page sessions / Total sessions
- **Time on Page:** Average session duration
- **Exit Rate:** Exits from page / Page views

### GA4 Events

**Impression Event:**
```javascript
gtag('event', 'ab_test_impression', {
  variant: 'control' | 'buy' | 'purchase' | 'gum',
  experiment_id: 'checkout_flow_test'
});
```

**CTA Click Event (to add):**
```javascript
gtag('event', 'cta_click', {
  variant: 'control' | 'buy' | 'purchase' | 'gum',
  experiment_id: 'checkout_flow_test',
  cta_location: 'hero' | 'pricing' | 'footer'
});
```

---

## Expected Outcomes

### Hypothesis 1: Embedded Checkout Wins
**If `/buy` has highest conversion:**
- Users prefer staying on domain
- Trust is increased by not leaving site
- Seamless experience reduces friction

**Action:** Make `/buy` the default landing page

### Hypothesis 2: Direct Redirect Wins
**If `/gum` has highest conversion:**
- Users with high intent don't need landing page
- Minimal friction is most important
- Landing page adds unnecessary steps

**Action:** Consider direct redirect for all traffic

### Hypothesis 3: SaaS Landing Wins
**If `/purchase` has highest conversion:**
- Users need detailed information before buying
- Feature showcase increases perceived value
- Social proof and FAQ reduce objections

**Action:** Enhance feature content on all variants

### Hypothesis 4: Control Wins
**If `/root` has highest conversion:**
- Simple, fast-loading page is best
- Privacy-first messaging resonates
- Neo-brutalism design stands out

**Action:** Keep current design, optimize for speed

---

## Testing Timeline

### Phase 1: Manual Testing (Current)
- **Duration:** 1-2 days
- **Goal:** Verify all variants work correctly
- **Traffic:** Manual testing only
- **AUTO_SPLIT:** `false`

### Phase 2: Soft Launch
- **Duration:** 3-7 days
- **Goal:** Collect initial data
- **Traffic:** Small subset (e.g., social media only)
- **AUTO_SPLIT:** `true`

### Phase 3: Full A/B Test
- **Duration:** 14-30 days
- **Goal:** Statistical significance
- **Traffic:** All traffic
- **AUTO_SPLIT:** `true`
- **Sample Size:** Aim for 100+ conversions per variant

### Phase 4: Winner Implementation
- **Duration:** Ongoing
- **Goal:** Optimize winning variant
- **Traffic:** 100% to winner
- **AUTO_SPLIT:** `false` (or redirect all to winner)

---

## Statistical Significance

### Minimum Sample Size
- **Conversions per variant:** 100+
- **Total visitors:** ~4,000+ (assuming 1% conversion rate)
- **Confidence level:** 95%
- **Statistical power:** 80%

### Tools
- [Optimizely Sample Size Calculator](https://www.optimizely.com/sample-size-calculator/)
- [Evan Miller A/B Test Calculator](https://www.evanmiller.org/ab-testing/sample-size.html)

---

## File Reference

```
Landing Page Structure:
├── index.html              # Main entry with routing
├── root.html               # Variant 1: Control
├── buy.html                # Variant 2: Embedded
├── purchase.html           # Variant 3: SaaS
├── gum.html                # Variant 4: Redirect
├── test-variants.html      # Testing dashboard
├── _redirects              # Cloudflare routing
├── assets/
│   └── files/
│       ├── signkit_icon_32x32.png
│       ├── signkit_icon_64x64.png
│       └── ...
├── screenshots/
│   ├── screenshot-1.png
│   ├── screenshot-2.png
│   └── screenshot-3.png
└── web/
    └── live/
        ├── css/
        │   ├── style.css
        │   └── animations.css
        └── js/
            ├── main.js
            └── animations.js
```

---

## Quick Commands

### Test Locally
```bash
python3 -m http.server 8080
open http://localhost:8080/test-variants.html
```

### Deploy to Cloudflare
```bash
git add .
git commit -m "Update landing page variants"
git push origin landing-page
```

### Enable A/B Testing
```javascript
// In index.html, change:
const AUTO_SPLIT = false; // to
const AUTO_SPLIT = true;
```

### Check GA4 Events
```
GA4 Dashboard → Reports → Events → ab_test_impression
```

---

**Last Updated:** November 18, 2025  
**Status:** Ready for deployment  
**Current Mode:** Manual testing (`AUTO_SPLIT = false`)
