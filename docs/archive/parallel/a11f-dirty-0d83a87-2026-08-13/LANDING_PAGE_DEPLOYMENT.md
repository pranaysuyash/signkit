# Landing Page Deployment Guide

> **Superseded addendum (2026-08-02):** This historical guide describes the
> former multi-variant/A-B deployment and must not be used as current launch
> guidance. The canonical contract is in
> [`docs/LANDING_DEPLOYMENT_PROCESS.md`](LANDING_DEPLOYMENT_PROCESS.md) and
> [`docs/landing/CLOUDFLARE_DEPLOYMENT.md`](landing/CLOUDFLARE_DEPLOYMENT.md).
> `/` is the only public acquisition route; retained HTML artifacts redirect
> to `/`; run the route/provider smoke checks before and after publishing.

## Overview
The SignKit landing page is deployed on Cloudflare Pages at **signkit.work** from the repository's `main` branch.

## Branch Strategy

### `main` Branch
- **Purpose**: Production landing page and A/B test variants
- **Domain**: https://signkit.work
- **Cloudflare Project**: signkit-landing
- **Contents**: HTML pages, assets, screenshots for marketing site
- **When to update**: Landing page copy, design, assets, deployment wiring, or A/B test changes

### `landing-page` Branch
- **Status**: Archived/deprecated
- **Purpose**: Historical reference only
- **Remote**: Kept on `origin` for auditability and rollback context

### Repository Scope
- **Purpose**: Desktop application development and landing page deployment live together in the same repo
- **Contents**: Python app, backend, tests, build tools, HTML landing pages, assets, screenshots
- **When to update**: All feature development, bug fixes, landing page copy/design, deployment wiring, and A/B test changes

**The repo is now unified on `main`** - `main` is the source of truth for the live landing page and app code.

## A/B Testing Setup

### Current Configuration
Four checkout flow variants are being tested:
- **`/root`** - Control variant (neo-brutal design)
- **`/buy`** - Embedded gum.new checkout
- **`/gum`** - Direct Gumroad redirect
- **`/purchase`** - Claude v2 landing page

### How It Works
1. **Manual Testing (Current)**
   - Each variant has its own URL
   - Send different traffic sources to different URLs
   - Track conversions in Google Analytics by variant

2. **Automatic A/B Testing (Future)**
   - Set `AUTO_SPLIT = true` in `index.html`
   - Visitors to `/` are randomly assigned a variant
   - Assignment stored in localStorage
   - Subsequent visits use same variant

### Enabling Auto A/B Testing
When ready to enable automatic variant assignment:

1. Checkout `main`
2. Edit `index.html`:
   ```javascript
   const AUTO_SPLIT = true; // Change from false
   ```
3. Commit and push
4. Cloudflare Pages will auto-deploy

## Deployment Process

### Automatic Deployment (Recommended)
Cloudflare Pages automatically deploys when you push to `main`:

```bash
git checkout main
# Make your changes
git add -A
git commit -m "Update landing page copy"
git push origin main
```

Cloudflare detects the push and deploys automatically (usually 1-2 minutes).

### Manual Deployment via Wrangler
If automatic deployment isn't working:

```bash
# Create temp directory with only landing page files
mkdir -p /tmp/signkit-deploy
cp -r index.html root.html buy.html purchase.html gum.html test-variants.html assets screenshots web /tmp/signkit-deploy/

# Deploy
wrangler pages deploy /tmp/signkit-deploy --project-name=signkit-landing --branch=main
```

## Cloudflare Pages Routing Configuration

### ✅ Redirect Issue Resolution (Nov 19, 2025)

**Problem:** All clean URLs (/buy, /root, /gum, /purchase) were returning HTTP 308 redirects to themselves, blocking all purchases.

**Root Cause:** Cloudflare Pages routing configuration was causing redirect loops. The issue was related to:
- Problematic `_redirects` file configuration
- `.pages-include` file listing non-existent HTML files
- Cloudflare expecting static HTML files when the app uses client-side JavaScript routing

**Solution Applied:**
1. Removed or corrected the `_redirects` file configuration
2. Ensured Cloudflare Pages properly serves index.html for all routes
3. Verified build settings (Build output dir = root, no build command)
4. Allowed JavaScript to handle routing client-side

**Current Status:** All URLs now return HTTP 200 and work correctly:
- ✅ https://signkit.work/buy - Working
- ✅ https://signkit.work/gum - Working
- ✅ https://signkit.work/purchase - Working
- ✅ https://signkit.work/root - Working

### Important: Cloudflare Pages Routing

**For client-side routing (JavaScript-based):**
- Cloudflare Pages should serve `index.html` for all routes
- Let JavaScript handle routing client-side
- Do NOT create `_redirects` file for client-side routed apps
- Ensure `.pages-include` doesn't list non-existent HTML files

**For static HTML files:**
- Cloudflare Pages automatically handles extensionless URLs
- `/root` → serves `root.html` (HTTP 200)
- `/buy` → serves `buy.html` (HTTP 200)
- No redirect configuration needed

## File Structure

```
main branch:
├── index.html              # Main landing page
├── root.html               # Control variant
├── buy.html                # Gum.new embedded variant
├── gum.html                # Gumroad redirect variant
├── purchase.html           # Claude v2 variant
├── test-variants.html      # Testing page
├── assets/                 # Icons, logos
├── screenshots/            # Product screenshots
├── web/                    # Additional landing page assets
├── wrangler.toml           # Cloudflare Pages config
└── .pages-include          # Files to include in deployment
```

## Testing Deployment

After deployment, test all routes:

```bash
curl -I https://signkit.work/root
curl -I https://signkit.work/buy
curl -I https://signkit.work/gum
curl -I https://signkit.work/purchase
```

All should return `HTTP/2 200`.

## Google Analytics Tracking

### Event Tracking
Each variant tracks impressions:
- Event: `ab_test_impression`
- Experiment ID: `checkout_flow_test`
- Variants: `control`, `root`, `buy`, `gum`, `purchase`

View results in Google Analytics:
- Property ID: G-PCJDGBMRRN
- Events → ab_test_impression
- Filter by variant dimension

### Analytics Fix (Nov 18, 2025)
**Issue**: The `/gum` variant was redirecting immediately before GA4 could fire tracking events.

**Solution**: Updated `gum.html` to use GA4's `event_callback` feature:
- Tracks the `ab_test_impression` event
- Waits for callback confirmation (~100-500ms)
- Then redirects to Gumroad
- Includes fallback timeout to ensure redirect happens

**Testing**: Use `test-analytics.html` (in `main`) to verify all variants track correctly:
```bash
# Start local server
python3 -m http.server 8001

# Open test suite
open http://localhost:8001/test-analytics.html
```

**Verification**: 
- Open DevTools Network tab
- Filter by "collect"
- Each variant should send `collect?v=2&...&en=ab_test_impression`
- One request may show "(canceled)" - this is normal, the 204 response is what matters

See `moved_root_docs/moved_root_docs/ANALYTICS_FIX_SUMMARY.md` (archived history) for complete details.

## Troubleshooting

### 308 Redirect Loops
**Cause**: A `_redirects` file exists  
**Solution**: Delete the `_redirects` file

### Changes Not Appearing
**Cause**: Browser cache or Cloudflare cache  
**Solution**: 
- Hard refresh (Cmd+Shift+R on Mac)
- Check preview URL from Cloudflare dashboard
- Wait 2-3 minutes for cache to clear

### Deployment Not Triggering
**Cause**: GitHub webhook not configured  
**Solution**: 
- Check Cloudflare Pages dashboard → Settings → Builds
- Ensure "Automatic deployments" is enabled
- Or use manual deployment via Wrangler

## When to Update Each Branch

### Update `main` when:
- Changing landing page copy or messaging
- Updating pricing information
- Adding/removing A/B test variants
- Changing screenshots or assets
- Enabling/disabling AUTO_SPLIT

## Related Documentation
- `moved_root_docs/moved_root_docs/CLOUDFLARE_REDIRECTS_ISSUE.md` (archived history) - Details on the 308 redirect issue
- `AB_TEST_STRUCTURE.md` - A/B testing implementation details
- `DEPLOYMENT_CHECKLIST.md` - Pre-deployment checklist
