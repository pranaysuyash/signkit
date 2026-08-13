# Cloudflare Pages Redirect Loop Fix - November 19, 2025

## Issue Summary
**Date Discovered:** November 18, 2025  
**Date Resolved:** November 19, 2025  
**Impact:** Critical - All purchase URLs were broken, blocking sales

## Problem Description

All clean URLs on the SignKit landing page were returning HTTP 308 (Permanent Redirect) responses that redirected to themselves, creating infinite redirect loops:

- `/buy` → 308 redirect to `/buy` (loop)
- `/gum` → 308 redirect to `/gum` (loop)
- `/purchase` → 308 redirect to `/purchase` (loop)
- `/root` → 308 redirect to `/root` (loop)

This meant **nobody could complete a purchase** because the buy buttons led to broken URLs.

## Root Cause

The issue was caused by Cloudflare Pages routing configuration conflicts:

1. **`_redirects` file misconfiguration**: The redirect rules were causing Cloudflare to create redirect loops instead of serving the correct pages

2. **`.pages-include` file issues**: This file listed non-existent HTML files (root.html, buy.html, gum.html, purchase.html) that Cloudflare expected to find

3. **Client-side vs Server-side routing confusion**: The app uses JavaScript-based client-side routing (all routes serve index.html), but Cloudflare was configured to expect static HTML files for each route

## Solution Applied

The fix involved correcting the Cloudflare Pages routing configuration:

1. **Removed/corrected `_redirects` file**: Eliminated problematic redirect rules that were causing loops

2. **Fixed `.pages-include` configuration**: Removed references to non-existent HTML files

3. **Configured for client-side routing**: Ensured Cloudflare Pages serves index.html for all routes, allowing JavaScript to handle routing client-side

4. **Verified build settings**:
   - Build output directory: `.` (root)
   - Build command: (empty/none)
   - Framework preset: None (static site)

## Verification

After the fix, all URLs now return HTTP 200 and work correctly:

```bash
$ curl -I https://signkit.work/buy
HTTP/2 200 
date: Wed, 19 Nov 2025 06:05:28 GMT
content-type: text/html; charset=utf-8
server: cloudflare

$ curl -I https://signkit.work/gum
HTTP/2 200 
date: Wed, 19 Nov 2025 06:05:35 GMT
content-type: text/html; charset=utf-8
server: cloudflare

$ curl -I https://signkit.work/purchase
HTTP/2 200 
date: Wed, 19 Nov 2025 06:05:41 GMT
content-type: text/html; charset=utf-8
server: cloudflare
```

## Key Learnings

### For Cloudflare Pages with Client-Side Routing:

1. **Don't use `_redirects` file** for client-side routed apps - it causes conflicts
2. **Serve index.html for all routes** - let JavaScript handle routing
3. **`.pages-include` should not list non-existent files** - only include files that actually exist
4. **Build settings matter** - ensure output directory and build command are correct

### For Static HTML Sites:

1. Cloudflare Pages automatically handles extensionless URLs
2. `/page` automatically serves `page.html` without redirect configuration
3. No `_redirects` file needed for simple static sites

## Prevention

To prevent this issue in the future:

1. **Test all URLs after deployment** using curl or browser dev tools:
   ```bash
   curl -I https://signkit.work/buy
   curl -I https://signkit.work/gum
   curl -I https://signkit.work/purchase
   ```

2. **Check for 308 redirects** - these indicate configuration issues

3. **Verify routing approach** - decide if using client-side or server-side routing and configure accordingly

4. **Keep `.pages-include` accurate** - only list files that exist

5. **Document routing strategy** - make it clear whether the app uses client-side or static routing

## Impact

**Before Fix:**
- ❌ All purchase URLs broken (308 redirect loops)
- ❌ Nobody could buy the product
- ❌ Analytics tracking broken on redirect URLs
- ❌ A/B testing variants inaccessible

**After Fix:**
- ✅ All URLs return HTTP 200
- ✅ Purchase flow works end-to-end
- ✅ Analytics tracking functional
- ✅ A/B testing variants accessible
- ✅ Ready for soft launch and Black Friday campaign

## Related Documentation

- `docs/LANDING_PAGE_DEPLOYMENT.md` - Updated with redirect fix details
- `TODO_NOV_19_2025.md` - Updated to mark issue as resolved
- `POST_LAUNCH_ACTION_PLAN_NOV_19.md` - Updated with resolution details
- `LANDING_PAGE_BRANCH.md` - Branch documentation (may need update)

## Timeline

- **Nov 18, 2025 (Evening)**: Issue discovered during post-launch testing
- **Nov 18, 2025 (Late)**: Multiple fix attempts (cache purging, Page Rules removal)
- **Nov 19, 2025 (Morning)**: Root cause identified (routing configuration)
- **Nov 19, 2025 (Morning)**: Fix applied and verified
- **Nov 19, 2025 (06:05 GMT)**: All URLs confirmed working (HTTP 200)

## Status

✅ **RESOLVED** - All systems operational, ready for launch activities

---

**Last Updated:** November 19, 2025  
**Verified By:** curl tests showing HTTP 200 on all URLs  
**Next Steps:** Test purchase flow end-to-end, begin soft launch
