# SignKit Landing Page - Cloudflare Pages Deployment Guide

## Overview

This landing page is set up for deployment to Cloudflare Pages with A/B testing for 4 variants:

1. **Control (/)** - Neo-brutalism design (index.html with AUTO_SPLIT routing)
2. **Root (/root)** - Neo-brutalism design (root.html - direct access)
3. **Buy (/buy)** - Full-page embedded Gumroad checkout (buy.html)
4. **Purchase (/purchase)** - Claude v2 SaaS-style landing page (purchase.html)
5. **Gum (/gum)** - Direct redirect to Gumroad product page (gum.html)

## File Structure

```
.
├── index.html          # Main entry with A/B routing logic
├── root.html           # Control variant (neo-brutalism)
├── buy.html            # Full-page iframe checkout
├── purchase.html       # Claude v2 design
├── gum.html            # Direct Gumroad redirect
├── test-variants.html  # Local testing dashboard
├── _redirects          # Cloudflare Pages routing rules
├── wrangler.toml       # Cloudflare configuration
├── assets/             # Icons and static files
├── screenshots/        # Product screenshots
└── web/                # Additional landing page variants
```

## Deployment Steps

### Option 1: Deploy via Cloudflare Dashboard (Recommended)

1. **Connect Repository**

   - Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
   - Navigate to Pages
   - Click "Create a project"
   - Connect your GitHub repository
   - Select the `landing-page` branch

2. **Configure Build Settings**

   - Framework preset: `None`
   - Build command: (leave empty)
   - Build output directory: `/`
   - Root directory: `/`

3. **Environment Variables** (if needed)

   - None required for static site

4. **Deploy**
   - Click "Save and Deploy"
   - Cloudflare will build and deploy your site
   - You'll get a URL like: `signkit-landing.pages.dev`

### Option 2: Deploy via Wrangler CLI

1. **Install Wrangler**

   ```bash
   npm install -g wrangler
   ```

2. **Login to Cloudflare**

   ```bash
   wrangler login
   ```

3. **Deploy**
   ```bash
   wrangler pages deploy . --project-name=signkit-landing
   ```

## Custom Domain Setup

1. **Add Custom Domain**

   - In Cloudflare Pages dashboard, go to your project
   - Click "Custom domains"
   - Add `signkit.work`
   - Cloudflare will automatically configure DNS

2. **DNS Configuration**
   - Cloudflare will create a CNAME record pointing to your Pages deployment
   - SSL/TLS will be automatically provisioned

## A/B Testing Configuration

### How It Works

1. **Root Path (`/`)**:

   - Serves `index.html`
   - JavaScript checks `AUTO_SPLIT` flag
   - If `true`: randomly assigns user to one of 4 variants (25% each)
   - Stores variant in `localStorage` for consistency
   - Redirects to assigned variant path

2. **Direct Paths**:
   - `/root` - Always shows control (neo-brutalism)
   - `/buy` - Always shows embedded checkout
   - `/purchase` - Always shows Claude v2 design
   - `/gum` - Always redirects to Gumroad

### Enable Auto A/B Testing

Edit `index.html` and change:

```javascript
const AUTO_SPLIT = false; // Change to true
```

### Disable Auto A/B Testing

Keep `AUTO_SPLIT = false` in `index.html` to allow manual testing via direct URLs.

## Analytics Tracking

All variants track impressions to Google Analytics 4:

- **Property ID**: `G-PCJDGBMRRN`
- **Event**: `ab_test_impression`
- **Parameters**:
  - `variant`: control | buy | purchase | gum
  - `experiment_id`: checkout_flow_test

### View Results in GA4

1. Go to GA4 dashboard
2. Navigate to Events
3. Look for `ab_test_impression` event
4. Filter by `variant` parameter to see distribution

## Testing Locally

### Start Local Server

```bash
# Using Python
python3 -m http.server 8080

# Using Node.js
npx http-server -p 8080

# Using PHP
php -S localhost:8080
```

### Test Dashboard

Open `http://localhost:8080/test-variants.html` to access the testing dashboard with links to all variants.

### Test Individual Variants

- Control: `http://localhost:8080/` or `http://localhost:8080/root`
- Buy: `http://localhost:8080/buy`
- Purchase: `http://localhost:8080/purchase`
- Gum: `http://localhost:8080/gum`

## File Dependencies (Cloudflare Pages)

NOTE: Cloudflare Pages is our canonical deployment method. While older docs include S3/CloudFront steps, most deploys use Cloudflare Pages with the built-in Pages CDN. If you prefer S3/CloudFront, see the `web/neobrutalism_chatgpt/DEPLOYMENT_GUIDE.md` for an example.

### Required Files

- `index.html` - Main routing logic
- `root.html` - Control variant
- `buy.html` - Embedded checkout
- `purchase.html` - Claude v2 design
- `gum.html` - Redirect variant
- `_redirects` - Cloudflare routing rules

### Required Assets (for Cloudflare Pages)

- `assets/files/signkit_icon_32x32.png`
- `assets/files/signkit_icon_16x16.png`
- `assets/files/signkit_icon_256x256.png`
- `assets/files/signkit_icon_64x64.png`
  _Prefer placing your landing page images inside the variant folder._ For Cloudflare Pages deploys we recommend adding screenshots into each landing variant's asset folder, for example:

`web/live/assets/screenshots/step1-upload.png`
   Note: Some landing variants reference the repo root `screenshots/` folder (e.g., `index.html`, `root.html`, `purchase.html`) whereas others (like `web/live`) use per-variant `./assets/screenshots/`. For consistency, we recommend placing screenshots in both locations during a deployment or updating the HTML to use per-variant paths. This document prefers per-variant `web/<variant>/assets/screenshots/` as the canonical location for future variants.
`web/live/assets/screenshots/step2-select.png`
`web/live/assets/screenshots/step3-clean.png`

If you keep images in the repo root `screenshots/`, make sure your build step copies them to the variant folder prior to publishing.

### Required CSS/JS (for purchase.html)

`web/live/css/style.css`
`web/live/css/animations.css`
`web/live/js/main.js`
`web/live/js/animations.js`

## End-to-End Analytics Tests

We've added a couple of Puppeteer-based E2E tests to validate event tracking on the deployed site:

- `tests/e2e/analytics.deploy.test.js` - Simulates a real human session (mouse movement, scroll, CTA click) and verifies that gtag dataLayer pushes include `real_user_detected`, `cta_click`, and `purchase_intent`.
- `tests/e2e/bot-check.js` - Simulates a bot user agent and verifies that `bot_detected` is fired and that engagement events are suppressed.

Run these tests locally (requires Node.js and npm):

```bash
npm install
npm run test:e2e:deploy
npm run test:e2e:bot
```

Notes:

- `scroll_depth` events can be flaky in headless browsers due to differences in viewport handling and CSS layout. In headful mode (non-headless), the scrolling may register more reliably. If the test doesn't consistently capture `scroll_depth`, it's still useful to validate other engagement events.
- Tests capture the client-side `dataLayer` pushes but do not assert actual ingestion into GA servers. Use GA Debug view or the Realtime Dashboard in GA for end-to-end verification.

## Troubleshooting

### Issue: Redirects not working

**Solution**: Ensure `_redirects` file is in the root directory and properly formatted.

### Issue: Assets not loading

**Solution**: Check that all asset paths are relative (no leading `/` unless intentional).

### Issue: A/B routing not working

**Solution**:

1. Check browser console for JavaScript errors
2. Verify `AUTO_SPLIT` is set correctly in `index.html`
3. Clear `localStorage` to reset variant assignment

### Issue: Iframe not loading on /buy

**Solution**:

1. Check browser console for CSP or iframe errors
2. Verify Gumroad URL is correct
3. Ensure `allow="payment"` attribute is present on iframe

## Performance Optimization

### Cloudflare Optimizations (Automatic)

- Brotli compression
- HTTP/2 and HTTP/3
- Global CDN distribution
- Automatic image optimization (if enabled)

### Manual Optimizations

1. **Compress Images**

   ```bash
   # Install imagemagick
   brew install imagemagick

   # Optimize screenshots
   mogrify -strip -quality 85 screenshots/*.png
   ```

2. **Minify CSS/JS** (if needed)
   - Cloudflare can do this automatically via dashboard settings

## Security

### Headers

Cloudflare Pages automatically adds security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`

### Custom Headers (Optional)

Create `_headers` file in root:

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
```

## Monitoring

### Cloudflare Analytics

- Available in Cloudflare dashboard
- Shows page views, unique visitors, bandwidth
- Real-time and historical data

### Google Analytics 4

- Tracks all variant impressions
- Custom events for A/B test tracking
- Conversion tracking (if configured)

## Rollback

If you need to rollback to a previous deployment:

1. Go to Cloudflare Pages dashboard
2. Click on your project
3. Go to "Deployments" tab
4. Find the previous successful deployment
5. Click "..." menu and select "Rollback to this deployment"

## Support

For issues with:

- **Cloudflare Pages**: [Cloudflare Community](https://community.cloudflare.com/)
- **Landing Page**: Check GitHub issues or contact support@signkit.work
- **Gumroad Integration**: [Gumroad Help](https://help.gumroad.com/)
