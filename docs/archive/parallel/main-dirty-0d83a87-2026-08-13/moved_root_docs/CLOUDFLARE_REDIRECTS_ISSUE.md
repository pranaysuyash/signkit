# Cloudflare Pages _redirects Issue - RESOLVED

**Status**: ✅ RESOLVED  
**Date**: November 18, 2025  
**Solution**: Delete the `_redirects` file - Cloudflare Pages handles extensionless URLs natively

---

# Cloudflare Pages _redirects Issue - Detailed Writeup

## Project Context
We're deploying a landing page for SignKit (signkit.work) on Cloudflare Pages with an A/B testing setup for different checkout flows.

## What We're Trying to Achieve

### A/B Test Structure
We want to test 4 different checkout variants:
1. **`/root`** → Control variant (serves `root.html` - neo-brutal design)
2. **`/buy`** → Embedded gum.new checkout (serves `buy.html`)
3. **`/gum`** → Direct Gumroad redirect (serves `gum.html`)
4. **`/purchase`** → Claude v2 landing page (serves `purchase.html`)

### Goal
Each route should serve its specific HTML file WITHOUT redirecting. We want URL rewrites (status 200), not redirects (301/302/308).

## Current Setup

### File Structure
```
/
├── index.html (main landing page)
├── root.html (control variant)
├── buy.html (gum.new embedded)
├── gum.html (gumroad redirect)
├── purchase.html (claude v2 page)
├── _redirects (Cloudflare Pages routing config)
├── wrangler.toml
├── .pages-include
└── assets/, screenshots/, web/
```

### Current _redirects File
```
# Cloudflare Pages routing configuration
# https://developers.cloudflare.com/pages/configuration/redirects/

# A/B test variants - each route serves its specific HTML file
/root           /root.html        200
/buy            /buy.html         200
/gum            /gum.html         200
/purchase       /purchase.html    200
```

### Deployment Configuration
- **Platform**: Cloudflare Pages
- **Project Name**: signkit-landing
- **Production Branch**: landing-page
- **Build Output Directory**: `.` (root)
- **Domain**: signkit.work
- **Preview URL**: https://5a7b35e7.signkit-landing.pages.dev

## The Problem

### Issue
All routes return **HTTP 308 Permanent Redirect** instead of serving the HTML files with status 200.

### Test Results
```bash
$ curl -I https://signkit.work/root
HTTP/2 308 
location: /root

$ curl -I https://signkit.work/buy
HTTP/2 308 
location: /buy

$ curl -I https://5a7b35e7.signkit-landing.pages.dev/root
HTTP/2 308 
location: /root
```

The 308 redirects to the same path, creating a redirect loop.

## What We've Tried

### Attempt 1: Initial _redirects Configuration
**What we did**: Created `_redirects` file pointing routes to index.html
```
/root           /index.html       200
/buy            /index.html       200
/gum            /index.html       200
/purchase       /purchase.html    200
```
**Result**: 308 redirects
**Why it failed**: All routes pointed to index.html, but we actually have separate HTML files for each variant

### Attempt 2: Updated _redirects to Match File Names
**What we did**: Changed _redirects to point each route to its specific HTML file
```
/root           /root.html        200
/buy            /buy.html         200
/gum            /gum.html         200
/purchase       /purchase.html    200
```
**Result**: Still 308 redirects
**Why it failed**: Unknown - this should work according to Cloudflare docs

### Attempt 3: Git Push to Trigger Auto-Deployment
**What we did**: 
- Committed and pushed _redirects changes to landing-page branch
- Expected Cloudflare Pages to auto-deploy

**Result**: No new deployment triggered
**Why it failed**: Auto-deployment might not be configured or webhook broken

### Attempt 4: Manual Deployment via Wrangler CLI
**What we did**:
```bash
# Created temp directory with only needed files
mkdir -p /tmp/signkit-deploy
cp -r index.html root.html buy.html purchase.html gum.html test-variants.html _redirects assets screenshots web /tmp/signkit-deploy/

# Deployed via wrangler
wrangler pages deploy /tmp/signkit-deploy --project-name=signkit-landing --branch=landing-page --commit-dirty=true
```

**Result**: 
- Deployment succeeded
- Output: "Uploaded 0 files (129 already uploaded)"
- Output: "✨ Uploading _redirects"
- Still getting 308 redirects

**Why it failed**: Unknown - _redirects file was uploaded but not being processed correctly

## Verified Facts

1. ✅ All HTML files exist and are deployed (verified in /tmp/signkit-deploy)
2. ✅ _redirects file is present and uploaded to Cloudflare
3. ✅ Deployment completed successfully
4. ✅ Files are accessible at preview URL
5. ❌ _redirects rules are NOT being applied (still getting 308)

## Possible Causes

### Theory 1: Path Conflict
The route `/root` trying to serve `root.html` might be causing a conflict. Cloudflare might be interpreting this as a directory vs file issue.

### Theory 2: _redirects Syntax Issue
Maybe Cloudflare Pages requires different syntax for rewrites vs redirects, or doesn't support status 200 rewrites the way we expect.

### Theory 3: Build Configuration
The `pages_build_output_dir = "."` in wrangler.toml might not be correct, or there's a missing configuration.

### Theory 4: File Extension Handling
Cloudflare Pages might automatically strip `.html` extensions and our _redirects rules are conflicting with this behavior.

### Theory 5: Caching/Propagation
The changes might not have propagated yet, though this seems unlikely since we tested both production and preview URLs.

## Questions for ChatGPT

1. **Why would `/root` with a 200 rewrite to `/root.html` return a 308 redirect in Cloudflare Pages?**

2. **Is there a specific syntax or configuration needed for Cloudflare Pages to properly handle rewrites (status 200) vs redirects?**

3. **Do the target files need to be in a specific location or format for _redirects to work?**

4. **Could there be a conflict between the route path `/root` and the file `root.html`?**

5. **Does Cloudflare Pages support status 200 rewrites in _redirects, or only 301/302 redirects?**

6. **Is there an alternative approach (like using Cloudflare Workers, _headers file, or different routing) that would work better for this use case?**

## Additional Context

- We're using Cloudflare Pages (not Workers)
- No build step required (static HTML files)
- GitHub repo: pranaysuyash/signkit
- Branch: landing-page
- This is for A/B testing different checkout flows to optimize conversion rates
- We need to track each variant separately in Google Analytics (already configured with variant-specific tracking)

## Desired Outcome

When a user visits:
- `https://signkit.work/root` → Serves `root.html` with HTTP 200 (URL stays `/root`)
- `https://signkit.work/buy` → Serves `buy.html` with HTTP 200 (URL stays `/buy`)
- `https://signkit.work/gum` → Serves `gum.html` with HTTP 200 (URL stays `/gum`)
- `https://signkit.work/purchase` → Serves `purchase.html` with HTTP 200 (URL stays `/purchase`)

No redirects, no URL changes, just clean rewrites.


---

## THE SOLUTION (Thanks to ChatGPT)

### Root Cause
The `_redirects` file was causing a redirect loop by fighting with Cloudflare Pages' built-in `.html` canonicalization feature.

**The Loop:**
1. Request `/root`
2. `_redirects` rule tries to "rewrite" `/root` → `/root.html` with status 200
3. Cloudflare Pages canonicalizes `/root.html` → `/root` with 308
4. Back to step 1 → infinite loop

### Why This Happened
- **Cloudflare Pages automatically serves extensionless URLs**: If `root.html` exists, `/root` serves it with HTTP 200 automatically
- **`_redirects` doesn't support true rewrites**: Status 200 in `_redirects` is only for proxying patterns like `/blog/* → /news/:splat`, not for serving static files
- **We were over-engineering**: Trying to use Netlify-style rewrites on Cloudflare Pages

### The Fix
**Delete the `_redirects` file entirely.**

Cloudflare Pages natively handles:
- `/root` → serves `root.html` (200)
- `/buy` → serves `buy.html` (200)
- `/gum` → serves `gum.html` (200)
- `/purchase` → serves `purchase.html` (200)

No configuration needed!

### Test Results After Fix
```bash
$ curl -I https://signkit.work/root
HTTP/2 200 
content-type: text/html; charset=utf-8

$ curl -I https://signkit.work/buy
HTTP/2 200 
content-type: text/html; charset=utf-8

$ curl -I https://signkit.work/gum
HTTP/2 200 
content-type: text/html; charset=utf-8

$ curl -I https://signkit.work/purchase
HTTP/2 200 
content-type: text/html; charset=utf-8
```

✅ All routes working perfectly!

---

## A/B Testing Strategy

### Current Setup (Manual Variants)
- Each variant has its own URL: `/root`, `/buy`, `/gum`, `/purchase`
- Users can be sent directly to specific variants
- Google Analytics tracks each variant separately
- No automatic assignment

### Future: Automatic A/B Testing
When ready to enable automatic variant assignment:

1. **Set `AUTO_SPLIT = true` in `index.html`**
2. **How it works:**
   - User visits `/` or `/index.html`
   - JavaScript randomly assigns them to a variant (25% each)
   - Stores choice in `localStorage`
   - Redirects to assigned variant
   - Subsequent visits use same variant

3. **Direct links still work:**
   - `/root`, `/buy`, `/gum`, `/purchase` always work
   - No auto-redirect on these paths
   - Only `/` triggers the A/B logic

### Key Insight
**No Cloudflare configuration needed for A/B testing.** It's all handled client-side with JavaScript in `index.html`.

---

## Branch Strategy

### Production Landing Page
- **Branch**: `landing-page`
- **Purpose**: Landing page and A/B test variants only
- **Domain**: signkit.work
- **Files**: HTML pages, assets, screenshots
- **Changes**: Only when updating landing page copy, design, or A/B test variants

### Main Application Development
- **Branch**: `main`
- **Purpose**: Desktop app development (Python/FastAPI/React)
- **Files**: `desktop_app/`, `backend/`, `tests/`, etc.
- **Changes**: All feature development, bug fixes, new functionality

### When to Touch Each Branch
- **`landing-page`**: Only for marketing/landing page updates
- **`main`**: All desktop app development work

The branches are completely independent. You can work on new features in `main` without affecting the live landing page.

---

## Lessons Learned

1. **Cloudflare Pages ≠ Netlify**: Don't assume Netlify patterns work on Cloudflare
2. **Read the platform docs**: Cloudflare's built-in features often eliminate need for config files
3. **Simpler is better**: No `_redirects` file = no problems
4. **Test with curl**: Quick way to see actual HTTP status codes
5. **ChatGPT for platform-specific issues**: Great for debugging deployment platform quirks

---

## References

- [Cloudflare Pages Serving Pages](https://developers.cloudflare.com/pages/configuration/serving-pages/)
- [Cloudflare Pages Redirects](https://developers.cloudflare.com/pages/configuration/redirects/)
- [Cloudflare Pages A/B Testing Guide](https://developers.cloudflare.com/pages/how-to/ab-testing/)
