# SignKit Landing Page A/B Test Variants

## Traffic Distribution

### Option 1: Manual URLs (Default)

Share different URLs for different audiences:

- `signkit.work` → Control
- `signkit.work/buy` → Embedded checkout
- `signkit.work/purchase` → Claude design
- `signkit.work/gum` → Direct redirect

**Use when:** Testing different channels (Twitter vs Reddit vs Email)

### Option 2: Automatic Random Split

Enable `AUTO_SPLIT = true` in `index.html` to automatically redirect visitors to random variants.

**How it works:**

1. User visits `signkit.work`
2. JavaScript randomly assigns variant (25% each)
3. User is redirected to assigned route
4. Variant stored in `localStorage` for consistency

**Enable automatic split:**

```javascript
// In index.html, change this line:
const AUTO_SPLIT = true; // Change from false to true
```

**Use when:** Sending all traffic to one URL and want automatic split testing

---

## Overview

Four checkout flow variants to test conversion rates:

| Variant          | Route       | Description                                          | Tracking              |
| ---------------- | ----------- | ---------------------------------------------------- | --------------------- |
| **Control**      | `/` (root)  | Neo-brutalism landing page with external Gumroad CTA | `variant: 'control'`  |
| **V2: Embedded** | `/buy`      | gum.new embedded checkout inline                     | `variant: 'buy'`      |
| **V3: Claude**   | `/purchase` | Claude v2 landing page design                        | `variant: 'purchase'` |
| **V4: Direct**   | `/gum`      | Immediate redirect to Gumroad product page           | `variant: 'gum'`      |

---

## Variant Details

### Control (Main Landing Page)

- **File:** `index.html`
- **Route:** `https://signkit.work/`
- **Design:** Neo-brutalism style with bold typography
- **CTA:** External link to `https://pranaysuyash.gumroad.com/l/signkit`
- **Hypothesis:** Clean, modern design with clear value props drives conversions

### V2: Embedded Checkout (/buy)

- **File:** `index.html` (dynamic route)
- **Route:** `https://signkit.work/buy`
- **Design:** Same as control + gum.new iframe embedded inline
- **Embed:** `https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj`
- **Hypothesis:** Keeping users on signkit.work domain increases trust and reduces friction

### V3: Claude Design (/purchase)

- **File:** `purchase.html`
- **Route:** `https://signkit.work/purchase`
- **Design:** More traditional SaaS landing page with animations
- **Features:** Detailed feature breakdown, animated demos, social proof
- **Hypothesis:** Comprehensive information and polished animations build confidence

### V4: Direct Redirect (/gum)

- **File:** `index.html` (JavaScript redirect)
- **Route:** `https://signkit.work/gum`
- **Action:** Immediate redirect to `https://pranaysuyash.gumroad.com/l/signkit`
- **Hypothesis:** Minimal friction - send users directly to checkout

---

## Implementation

### index.html (Control + V2 + V4)

```javascript
const path = window.location.pathname;

// V2: /buy with gum.new embedded
if (path === '/buy') {
  const iframe = document.createElement('iframe');
  iframe.src = 'https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj';
  // ... embed after hero
}

// V4: /gum direct redirect
if (path === '/gum') {
  window.location.href = 'https://pranaysuyash.gumroad.com/l/signkit';
}

// Track variant impressions
gtag('event', 'ab_test_impression', {
  variant: path.substring(1),
  experiment_id: 'checkout_flow_test',
});
```

### purchase.html (V3)

Standalone page with Claude v2 design:

- Updated meta tags and OG image
- Fixed asset paths to `web/live/`
- Added GA4 tracking with variant: 'purchase'

---

## GA4 Events

All variants track to the same GA4 property: `G-PCJDGBMRRN`

### Custom Event: `ab_test_impression`

```javascript
gtag('event', 'ab_test_impression', {
  variant: 'control' | 'buy' | 'purchase' | 'gum',
  experiment_id: 'checkout_flow_test',
});
```

### Conversion Event: `purchase`

Gumroad automatically sends conversion data via their integration.

---

## Testing Locally

```bash
# Start local server
python3 -m http.server 8080

# Test each variant:
http://127.0.0.1:8080/              # Control
http://127.0.0.1:8080/buy           # V2: Embedded
http://127.0.0.1:8080/purchase      # V3: Claude
http://127.0.0.1:8080/gum           # V4: Direct (will redirect)
```

---

## Cloudflare Pages Setup

1. **Production branch:** `landing-page`
2. **Build directory:** `/` (root)
3. **Environment:**

   - No build command needed
   - Static HTML deployment

4. **Custom Domain:** `signkit.work`

All routes will work automatically:

- Cloudflare Pages serves `index.html` for `/` and `/buy` and `/gum`
- Cloudflare Pages serves `purchase.html` for `/purchase`

---

## Metrics to Track

### Primary Metric

- **Conversion Rate:** Purchases / Unique Visitors

### Secondary Metrics

- **Engagement Rate:** Time on page, scroll depth
- **CTA Click Rate:** CTA clicks / Page views
- **Bounce Rate:** Immediate exits

### Breakdown by Variant

```sql
-- GA4 BigQuery query example
SELECT
  event_params.value.string_value AS variant,
  COUNT(DISTINCT user_pseudo_id) AS visitors,
  COUNTIF(event_name = 'purchase') AS purchases,
  SAFE_DIVIDE(COUNTIF(event_name = 'purchase'), COUNT(DISTINCT user_pseudo_id)) AS conversion_rate
FROM `your-project.analytics_XXXXXX.events_*`
WHERE event_name IN ('ab_test_impression', 'purchase')
GROUP BY variant
ORDER BY conversion_rate DESC
```

---

## Winner Criteria

Run test for **minimum 1000 visitors** or **2 weeks**, whichever comes first.

**Statistical significance:** 95% confidence level (p < 0.05)

**Decision framework:**

- If V2/V3/V4 > Control by >10% → Switch to winner
- If Control within ±5% of all variants → Keep control (simplest)
- If no clear winner → Iterate with hybrid approach

---

## Next Steps

1. ✅ Deploy to Cloudflare Pages
2. ⏳ Drive traffic to main page (distribute evenly)
3. ⏳ Monitor GA4 for 2 weeks
4. ⏳ Analyze results and pick winner
5. ⏳ Iterate with winner + new variants

---

## Files Structure

```
landing-page branch:
├── index.html                  # Control + V2 (/buy) + V4 (/gum)
├── purchase.html               # V3 (/purchase)
├── screenshots/                # Product screenshots
│   ├── screenshot-1.png
│   ├── screenshot-2.png
│   └── screenshot-3.png
├── assets/
│   └── files/                  # Icons
│       ├── signkit_icon_16x16.png
│       ├── signkit_icon_32x32.png
│       ├── signkit_icon_64x64.png
│       └── signkit_icon_256x256.png
└── AB_TEST_VARIANTS.md         # This file
```

---

## Questions?

See `/web/neobrutalism_chatgpt/DEPLOYMENT_GUIDE.md` for Cloudflare Pages deployment details.
