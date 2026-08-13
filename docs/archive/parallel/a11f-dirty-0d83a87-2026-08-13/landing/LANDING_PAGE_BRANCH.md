# Landing Page Deployment - Complete Documentation

**Branch Name**: `main`  
**Purpose**: A/B testing framework for SignKit product launch  
**Domain**: https://signkit.work (via Cloudflare Pages)  
**Status**: Production-ready, deployed November 2025

---

## Overview

The landing page is now deployed from the repository's `main` branch. It contains multiple landing page variants for A/B testing different checkout flows and messaging approaches.

The canonical live landing site lives in the repository root pages plus `web/live/` assets.

The old `landing-page` branch is archived/deprecated and is kept on the remote for historical reference only.

---

## Branch Architecture

### Why Keep It In Main?

The landing page stays in the main codebase because:

1. **Single source of truth** - Marketing pages and app docs stay in one branch
2. **Static HTML hosting** - Cloudflare Pages serves HTML/CSS/JS directly from the repository
3. **A/B testing framework** - Enables rapid iteration on conversion experiments
4. **Cleaner operations** - Fewer branch-specific deployment paths to maintain

### What's in This Branch

```
main/
├── index.html                      # Control variant (neo-brutalism design)
├── purchase.html                   # Claude v2 variant
├── serve.py                        # Local development server with routing
├── test-variants.html              # Testing dashboard
├── screenshots/                    # Product screenshots (3 images)
│   ├── screenshot-1.png           # Upload interface
│   ├── screenshot-2.png           # Signature selection
│   └── screenshot-3.png           # PDF signing
├── assets/files/                   # App icons
│   ├── signkit_icon_16x16.png
│   ├── signkit_icon_32x32.png
│   ├── signkit_icon_64x64.png
│   └── signkit_icon_256x256.png
├── web/live/     # Claude (or current) variant assets (canonical)
│   ├── css/style.css
│   ├── css/animations.css
│   └── js/main.js
└── Documentation files:
    ├── AB_TEST_VARIANTS.md
    ├── LANDING_PAGE_README.md
    └── LANDING_PAGE_SETUP_NOTES.md
```

---

## A/B Test Variants

The branch implements **4 distinct checkout flow variants** to test conversion rates:

### 1. Control (Root / `/root`)

- **File**: `index.html`
- **Design**: Neo-brutalism style with bold typography, bright colors
- **CTA**: External link to Gumroad (`https://pranaysuyash.gumroad.com/l/signkit-v1`)
- **Hypothesis**: Clean, privacy-first messaging with clear value props drives conversions
- **Route**: `https://signkit.work/` or `https://signkit.work/root`

### 2. Embedded Checkout (`/buy`)

- **File**: `index.html` (dynamic JavaScript)
- **Design**: Same as control + embedded gum.new checkout iframe
- **Embed**: `https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj`
- **Hypothesis**: Keeping users on signkit.work domain increases trust and reduces friction
- **Route**: `https://signkit.work/buy`
- **Technical**: Iframe inserted at body root level (outside `.page` container) via JavaScript

### 3. Claude Design (`/purchase`)

- **File**: `purchase.html`
- **Design**: Traditional SaaS landing page with animations, detailed features, social proof
- **Features**: Animated demo carousel, comprehensive feature breakdown, FAQ accordion
- **Hypothesis**: Polished animations and detailed information build confidence
- **Route**: `https://signkit.work/purchase`

### 4. Direct Redirect (`/gum`)

- **File**: `index.html` (JavaScript redirect)
- **Design**: None - immediate redirect to Gumroad
- **Target**: `https://pranaysuyash.gumroad.com/l/signkit-v1`
- **Hypothesis**: Minimal friction - send high-intent users directly to checkout
- **Route**: `https://signkit.work/gum`

---

## Traffic Routing System

### Manual URLs (Default)

By default, each variant has its own URL. Traffic is split by sending different audiences to different URLs:

- `signkit.work/root` → Control
- `signkit.work/buy` → Embedded
- `signkit.work/purchase` → Claude
- `signkit.work/gum` → Direct redirect

**Use case**: Testing different channels (Twitter vs Reddit vs Email)

### Automatic Random Split (Optional)

Set `AUTO_SPLIT = true` in `index.html` (line ~948) to enable automatic random assignment:

```javascript
const AUTO_SPLIT = false; // Change to true to enable
```

**How it works:**

1. User visits `signkit.work/` (root only)
2. JavaScript randomly assigns variant (25% each: root, buy, purchase, gum)
3. User is redirected to assigned route
4. Variant stored in `localStorage` for session consistency

**Important**: AUTO_SPLIT only triggers on `/` or `/index.html`. Direct routes (`/root`, `/buy`, `/purchase`, `/gum`) **always** show their respective variants regardless of AUTO_SPLIT setting.

---

## Technical Implementation

### Routing Logic

The branch uses **client-side JavaScript routing** combined with a **custom Python development server**:

#### Production (Cloudflare Pages)

Cloudflare automatically serves:

- `index.html` for `/`, `/root`, `/buy`, `/gum`
- `purchase.html` for `/purchase`

JavaScript in `index.html` handles variant logic based on `window.location.pathname`.

#### Local Development (serve.py)

```bash
python3 serve.py
```

Custom HTTP server that maps routes to files:

- `/` → `index.html`
- `/root` → `index.html`
- `/buy` → `index.html`
- `/purchase` → `purchase.html`
- `/gum` → `index.html`

Allows testing clean URLs without query parameters.

### Embedded Checkout Implementation

The `/buy` variant dynamically inserts a gum.new iframe:

```javascript
if (path === '/buy' || variantParam === 'buy' || hash === 'buy') {
  const embedContainer = document.createElement('div');
  embedContainer.id = 'gumroad-embed';
  embedContainer.style.cssText =
    'margin: 40px auto; max-width: 800px; padding: 0 20px;';

  // Insert at root body level (after .page container)
  const page = document.querySelector('.page');
  if (page) {
    page.parentNode.insertBefore(embedContainer, page.nextSibling);

    const iframe = document.createElement('iframe');
    iframe.src = 'https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj';
    iframe.style.cssText =
      'width: 100%; height: 800px; border: none; border-radius: 8px;';
    embedContainer.appendChild(iframe);
  }
}
```

**Key detail**: Iframe is inserted at **body root level** (outside the neo-brutalism card) so it appears as a full-width section below the hero.

---

## Analytics & Tracking

### Google Analytics 4

- **Property ID**: `G-PCJDGBMRRN`
- **Active**: Yes (free)
- **Events**:
  - `ab_test_impression` - Fires when variant is shown
    - `variant`: 'control', 'root', 'buy', 'gum', 'purchase'
    - `experiment_id`: 'checkout_flow_test'
  - `purchase` - Sent by Gumroad via integration

### Analytics Fix (November 18, 2025)

**Problem**: The `/gum` variant was redirecting to Gumroad immediately, before GA4 could fire the tracking event. This resulted in lost pageview and impression data.

**Root Cause**: JavaScript redirect (`window.location.href`) executed in the same script block as GA4 initialization, causing the page to navigate away before the async analytics script could send data.

**Solution**: Implemented GA4's `event_callback` pattern in `gum.html`:

```javascript
gtag('event', 'ab_test_impression', {
  variant: 'gum',
  experiment_id: 'checkout_flow_test',
  event_callback: function () {
    // Redirect ONLY after analytics confirms event sent
    window.location.href = 'https://pranaysuyash.gumroad.com/l/signkit-v1';
  },
  event_timeout: 2000, // Fallback: redirect after 2s even if callback doesn't fire
});

// Additional fallback in case gtag doesn't load
setTimeout(function () {
  window.location.href = 'https://pranaysuyash.gumroad.com/l/signkit-v1';
}, 2500);
```

**Impact**:

- User sees brief loading screen (~100-500ms) before redirect
- Analytics event fires successfully before navigation
- Fallback timeouts ensure redirect happens even if analytics fails
- All other variants (control, root, buy, purchase) were already working correctly

**Testing**: Use `test-analytics.html` to verify tracking:

```bash
python3 -m http.server 8001
open http://localhost:8001/test-analytics.html
```

**Verification in Production**:

1. Open DevTools Network tab
2. Filter by "collect"
3. Visit each variant URL
4. Look for `collect?v=2&...&en=ab_test_impression` requests
5. Status 204 = success (canceled requests are normal, GA4 sends multiple)

See `ANALYTICS_FIX_SUMMARY.md` for complete technical details.

### Plausible Analytics

- **Status**: Disabled (commented out)
- **Cost**: $9/month
- **Script**: `https://plausible.io/js/pa-Z7IHNxIIEUXGeZe1RBq2s.js`
- **Note**: Can be enabled later by uncommenting in `index.html` and `purchase.html`

### Tracking Implementation

```javascript
// Track variant impressions
if (
  path === '/root' ||
  path === '/buy' ||
  path === '/purchase' ||
  path === '/gum'
) {
  const v =
    (path !== '/' ? path.substring(1) : 'control') || variantParam || hash;
  gtag('event', 'ab_test_impression', {
    variant: v === 'root' ? 'control' : v,
    experiment_id: 'checkout_flow_test',
  });
}
```

---

## Product Links

### Gumroad Product

- **URL**: `https://pranaysuyash.gumroad.com/l/signkit-v1`
- **Price**: $29 one-time payment
- **Description**: "Own Forever" - no subscriptions

### gum.new Embedded Checkout

- **URL**: `https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj`
- **Usage**: Embedded in `/buy` variant
- **Benefits**: Same Gumroad checkout, but embedded inline on signkit.work domain

---

## Local Development

### Quick Start

```bash
# Clone and use the main branch
git checkout main

# Option 1: Simple HTTP server (query params only)
python3 -m http.server 8080

# Option 2: Custom router (clean URLs)
python3 serve.py
```

### Testing URLs

**With serve.py:**

- http://127.0.0.1:8080/ - Control (or auto-redirect if AUTO_SPLIT=true)
- http://127.0.0.1:8080/root - Control (always)
- http://127.0.0.1:8080/buy - Embedded iframe (always)
- http://127.0.0.1:8080/purchase - Claude variant (always)
- http://127.0.0.1:8080/gum - Direct redirect (always)
- http://127.0.0.1:8080/test-variants.html - Testing dashboard

**With simple HTTP server:**

- http://127.0.0.1:8080/?variant=buy
- http://127.0.0.1:8080/#buy
- http://127.0.0.1:8080/purchase.html

### Testing Dashboard

Navigate to http://127.0.0.1:8080/test-variants.html for a visual dashboard showing all 4 variants with descriptions and test buttons.

---

## Deployment (Cloudflare Pages)

### Setup

1. **Cloudflare Pages Settings**:

   - **Production branch**: `main`
   - **Build command**: None (static HTML)
   - **Build output directory**: `/` (root)
   - **Custom domain**: `signkit.work`

2. **Deployment Process**:

   ```bash
   git add -A
   git commit -m "Update landing page"
   git push origin main
   ```

   Cloudflare auto-deploys within ~1 minute.

3. **Production URLs**:
   - https://signkit.work/ - Root (auto-redirect if enabled)
   - https://signkit.work/root - Control
   - https://signkit.work/buy - Embedded
   - https://signkit.work/purchase - Claude
   - https://signkit.work/gum - Redirect

### Environment Configuration

No environment variables needed. Everything is client-side JavaScript and static HTML.

---

## Design & Messaging

### Control Variant (Neo-Brutalism)

- **Visual Style**: Bold borders, bright accent colors, playful rotations
- **Typography**: Space Grotesk font family
- **Colors**:
  - Primary accent: `#ffb800` (yellow)
  - Secondary: `#4f46e5` (indigo)
  - Tertiary: `#00c2a8` (teal)
  - Danger: `#ff3366` (red)
- **Key messaging**:
  - "Extract & Sign PDFs Offline"
  - "Your files never touch the cloud"
  - "$29 - Own Forever"

### Claude Variant

- **Visual Style**: Modern SaaS with gradients, animations, glassmorphism
- **Typography**: Inter + Space Grotesk
- **Features**:
  - Animated hero with floating blobs
  - 3-step demo carousel (5s transitions)
  - Tabbed solution showcase
  - FAQ accordion
  - Pricing comparison table
- **Messaging Updates** (Nov 2025):
  - Changed "Lifetime" → "Own Forever"
  - Removed fake "Launch Special 25% off" discount
  - All pricing: $29 (honest, no tricks)

---

## File Structure Details

### index.html (Control + Dynamic Variants)

**Lines 1-560**: HTML structure and embedded CSS for neo-brutalism design

**Lines 563-935**: HTML content:

- `.page` → `.shell` → `.top-bar`, `.grid`, `.footer`
- `.grid` contains `.hero-main` (left) and `.preview-card` (right)

**Lines 943-1054**: JavaScript logic:

- AUTO_SPLIT configuration
- Route detection (`window.location.pathname`)
- Variant assignment and localStorage
- Iframe injection for `/buy` variant
- Redirect logic for `/gum` variant
- GA4 tracking events

### purchase.html (Claude Variant)

**Complete standalone page** with:

- External CSS: `web/live/css/style.css`
- External JS: `web/live/js/main.js`
- Animations: `web/live/css/animations.css`

**Sections**:

1. Navigation with progress bar
2. Hero with animated background
3. Social proof strip
4. Problem section (3 pain points)
5. Solution tabs (Extract, Library, Sign)
6. Pricing card
7. FAQ accordion
8. Final CTA
9. Footer

**Recent fixes** (Nov 18, 2025):

- Footer links display inline (not stacked)
- Demo carousel: 3 steps (removed 4th)
- Animation speed: 3s → 5s
- Screenshots updated to correct order
- "Watch Demo" buttons hidden

---

## Common Issues & Solutions

### Issue: Iframe not appearing on /buy

**Cause**: querySelector targeting wrong element (was `.grid`, should be `.page`)

**Solution**: Iframe inserted at body root level after `.page` container:

```javascript
const page = document.querySelector('.page');
page.parentNode.insertBefore(embedContainer, page.nextSibling);
```

### Issue: Auto-redirect happening on direct routes

**Cause**: AUTO_SPLIT condition too broad

**Solution**: Only trigger on exact root path:

```javascript
if (AUTO_SPLIT && (path === '/' || path === '/index.html')) {
  // ... redirect logic
}
```

### Issue: LocalStorage persisting old variants

**Cause**: Variant stored in localStorage for session consistency

**Solution**: Clear localStorage or open in incognito mode for testing:

```javascript
localStorage.clear();
```

### Issue: Gumroad embed script conflicting

**Cause**: Unused `<script src="https://gumroad.com/js/gumroad-embed.js">` was included

**Solution**: Removed - we use gum.new iframe, not Gumroad's embed library

---

## Git Workflow

### Branch Management

```bash
# Switch to main
git checkout main

# Make changes
# ...

# Commit and push
git add -A
git commit -m "Descriptive message"
git push origin main
```

**Important**:

- Keep `main` as the single source of truth for the landing page
- Keep the archived `landing-page` branch only as historical reference on the remote

### Recent Commits (Nov 18, 2025)

1. "Add auto A/B split option + update Claude variant messaging"
2. "Fix A/B test routing: remove Gumroad script, add /root route, fix iframe insertion point"

---

## Success Metrics

### Primary Metric

**Conversion Rate**: Purchases / Unique Visitors

Track per variant in GA4:

```sql
-- GA4 BigQuery query
SELECT
  event_params.value.string_value AS variant,
  COUNT(DISTINCT user_pseudo_id) AS visitors,
  COUNTIF(event_name = 'purchase') AS purchases,
  SAFE_DIVIDE(
    COUNTIF(event_name = 'purchase'),
    COUNT(DISTINCT user_pseudo_id)
  ) AS conversion_rate
FROM `project.analytics_XXXXXX.events_*`
WHERE event_name IN ('ab_test_impression', 'purchase')
GROUP BY variant
ORDER BY conversion_rate DESC
```

### Secondary Metrics

- Time on page
- Scroll depth
- CTA click rate
- Bounce rate

---

## Test Duration & Winner Criteria

### Minimum Requirements

- **Visitors**: Minimum 1000 visitors per variant
- **Duration**: Minimum 2 weeks
- **Confidence**: 95% confidence level (p < 0.05)

### Decision Framework

- If any variant > Control by **>10%** → Switch to winner
- If Control within **±5%** of all variants → Keep control (simplest)
- If no clear winner → Iterate with hybrid approach

---

## Future Enhancements

### Potential Additions

1. **More variants**:

   - Video demo on hero
   - Testimonials section
   - Comparison table (vs cloud alternatives)
   - Urgency/scarcity messaging

2. **Advanced tracking**:

   - Heatmaps (Hotjar/Microsoft Clarity)
   - Session recordings
   - Funnel analysis

3. **Optimization**:

   - Image lazy loading
   - Critical CSS inlining
   - Service worker caching

4. **Integrations**:
   - Email capture (ConvertKit/Mailchimp)
   - Live chat support
   - Exit-intent popups

---

## Contact & Support

- **Website**: https://signkit.work
- **Email**: support@signkit.work
- **Repository**: signkit (pranaysuyash)
- **Branch**: `main`

---

## Quick Reference

### Key Files

| File                          | Purpose                         |
| ----------------------------- | ------------------------------- |
| `index.html`                  | Control + /buy + /gum variants  |
| `purchase.html`               | Claude v2 variant               |
| `serve.py`                    | Local development server        |
| `test-variants.html`          | Testing dashboard               |
| `AB_TEST_VARIANTS.md`         | Complete A/B test documentation |
| `LANDING_PAGE_README.md`      | Quick start guide               |
| `LANDING_PAGE_SETUP_NOTES.md` | Setup notes and fixes           |

### Key Variables

| Variable                    | Location             | Purpose                               |
| --------------------------- | -------------------- | ------------------------------------- |
| `AUTO_SPLIT`                | index.html line ~948 | Enable/disable auto traffic splitting |
| `G-PCJDGBMRRN`              | GA4 tracking ID      | Analytics property                    |
| `cmhyha3rs001h04l7ccem2nkj` | gum.new product ID   | Embedded checkout                     |

### Key Routes

| Route       | Variant         | File          | Always Works?        |
| ----------- | --------------- | ------------- | -------------------- |
| `/`         | Auto or Control | index.html    | AUTO_SPLIT dependent |
| `/root`     | Control         | index.html    | ✅ Always            |
| `/buy`      | Embedded        | index.html    | ✅ Always            |
| `/purchase` | Claude          | purchase.html | ✅ Always            |
| `/gum`      | Redirect        | index.html    | ✅ Always            |

---

**Last Updated**: November 18, 2025  
**Status**: Production, actively testing  
**Next Review**: After 1000+ visitors or 2 weeks
