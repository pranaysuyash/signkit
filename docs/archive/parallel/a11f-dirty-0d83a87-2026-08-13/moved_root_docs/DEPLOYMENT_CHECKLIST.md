# SignKit Landing Page - Deployment Checklist

## ✅ Pre-Deployment Verification

### Files Ready

- [x] `index.html` - Main entry with A/B routing
- [x] `root.html` - Control variant (neo-brutalism)
- [x] `buy.html` - Full-page iframe checkout
- [x] `purchase.html` - Claude v2 design
- [x] `gum.html` - Direct Gumroad redirect
- [x] `test-variants.html` - Testing dashboard
- [x] `_redirects` - Cloudflare routing rules
- [x] `wrangler.toml` - Cloudflare configuration
- [x] `.cfignore` - Deployment exclusions

### Assets Verified (Cloudflare Pages)
 
 [x] `assets/files/signkit_icon_32x32.png`
 [x] `assets/files/signkit_icon_16x16.png`
 [x] `assets/files/signkit_icon_256x256.png`
 [x] `assets/files/signkit_icon_64x64.png`
 - [x] `web/live/assets/screenshots/step1-upload.png`
 - [x] `web/live/assets/screenshots/step2-select.png`
 - [x] `web/live/assets/screenshots/step3-clean.png`
 - [x] `web/live/assets/screenshots/step4-sign.png`

### Dependencies (for purchase.html)
 
 - [x] `web/live/css/style.css`
 - [x] `web/live/css/animations.css`
 - [x] `web/live/js/main.js`
 - [x] `web/live/js/animations.js`

### Local Testing

- [x] All pages load without errors
- [x] All assets load correctly
- [x] Iframe on `/buy` displays full-page
- [x] Redirect on `/gum` works
- [x] GA4 tracking present on all variants

## 🚀 Deployment Steps

### Step 1: Commit and Push to GitHub

```bash
# Check current branch
git branch

# Should be on: landing-page

# Stage all changes
git add .

# Commit
git commit -m "feat: Cloudflare Pages deployment setup with A/B testing"

# Push to GitHub
git push origin landing-page
```

### Step 2: Connect to Cloudflare Pages

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **Workers & Pages** → **Pages**
3. Click **Create a project**
4. Select **Connect to Git**
5. Choose your GitHub repository
6. Select branch: `landing-page`

### Step 3: Configure Build Settings

**Framework preset:** None

**Build command:** (leave empty)

**Build output directory:** `/`

**Root directory:** (leave empty or `/`)

**Environment variables:** None needed

### Step 4: Deploy

1. Click **Save and Deploy**
2. Wait for deployment to complete (~1-2 minutes)
3. Note your deployment URL: `https://signkit-landing.pages.dev`

### Step 5: Test Deployment

Visit each variant on the deployed URL:

- [ ] `https://signkit-landing.pages.dev/` (index with routing)
- [ ] `https://signkit-landing.pages.dev/root` (control)
- [ ] `https://signkit-landing.pages.dev/buy` (iframe checkout)
- [ ] `https://signkit-landing.pages.dev/purchase` (Claude v2)
- [ ] `https://signkit-landing.pages.dev/gum` (redirect)
- [ ] `https://signkit-landing.pages.dev/test-variants.html` (dashboard)

### Step 6: Configure Custom Domain

1. In Cloudflare Pages, go to your project
2. Click **Custom domains** tab
3. Click **Set up a custom domain**
4. Enter: `signkit.work`
5. Cloudflare will automatically configure DNS
6. Wait for SSL certificate provisioning (~5 minutes)

### Step 7: Verify Custom Domain

- [ ] `https://signkit.work/` loads correctly
- [ ] `https://signkit.work/root` loads control variant
- [ ] `https://signkit.work/buy` loads iframe checkout
- [ ] `https://signkit.work/purchase` loads Claude v2
- [ ] `https://signkit.work/gum` redirects to Gumroad
- [ ] SSL certificate is active (green padlock)

## 🧪 A/B Testing Configuration

### Current State: Manual Testing Mode

`AUTO_SPLIT = false` in `index.html`

This means:

- Root `/` shows the control page (no auto-redirect)
- Users can manually access each variant via direct URLs
- Good for testing and QA

### Enable Auto A/B Testing

When ready to start A/B testing:

1. Edit `index.html`
2. Change `const AUTO_SPLIT = false;` to `const AUTO_SPLIT = true;`
3. Commit and push
4. Cloudflare will auto-deploy

This will:

- Randomly assign visitors to one of 4 variants (25% each)
- Store assignment in localStorage for consistency
- Track impressions in GA4

## 📊 Analytics Verification

### Google Analytics 4

1. Go to [GA4 Dashboard](https://analytics.google.com/)
2. Select property: `G-PCJDGBMRRN`
3. Navigate to **Reports** → **Realtime**
4. Visit each variant URL
5. Verify events appear in realtime

### Check A/B Test Events

1. In GA4, go to **Reports** → **Events**
2. Look for event: `ab_test_impression`
3. Click on event to see parameters
4. Verify `variant` parameter shows: control, buy, purchase, gum

## 🔧 Post-Deployment Configuration

### Cloudflare Settings to Review

1. **Speed** → **Optimization**

   - [ ] Enable Auto Minify (HTML, CSS, JS)
   - [ ] Enable Brotli compression
   - [ ] Enable Rocket Loader (optional)

2. **Caching** → **Configuration**

   - [ ] Browser Cache TTL: 4 hours (default is fine)
   - [ ] Always Online: Enabled

3. **Security** → **Settings**
   - [ ] Security Level: Medium
   - [ ] Challenge Passage: 30 minutes
   - [ ] Browser Integrity Check: Enabled

### DNS Settings

After custom domain setup, verify:

- [ ] CNAME record for `signkit.work` points to Cloudflare Pages
- [ ] SSL/TLS mode: Full (strict)
- [ ] Always Use HTTPS: Enabled
- [ ] Automatic HTTPS Rewrites: Enabled

## 🐛 Troubleshooting

### Issue: Pages not loading

**Check:**

1. Deployment status in Cloudflare dashboard
2. Browser console for errors
3. Network tab for failed requests

**Solution:**

- Redeploy from Cloudflare dashboard
- Clear browser cache
- Check `_redirects` file syntax

### Issue: Assets not loading (404)

**Check:**

1. Asset paths in HTML files
2. Files exist in repository
3. `.cfignore` not excluding needed files

**Solution:**

- Verify asset paths are relative
- Check file exists in repo
- Review `.cfignore` exclusions
- Ensure runtime `uploads/` files are NOT pushed to the repo. If uploads appear in the repo, remove them with `git rm -r --cached uploads` and add `uploads/**` to `.gitignore`.

### Issue: Iframe not loading on /buy

**Check:**

1. Browser console for CSP errors
2. Gumroad URL is correct
3. Network tab shows iframe request

**Solution:**

- Verify Gumroad URL: `https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj`
- Check iframe `allow="payment"` attribute
- Test in different browser

### Issue: A/B routing not working

**Check:**

1. `AUTO_SPLIT` value in `index.html`
2. Browser console for JavaScript errors
3. localStorage for `ab_variant` key

**Solution:**

- Verify `AUTO_SPLIT = true` if auto-routing desired
- Clear localStorage: `localStorage.clear()`
- Check browser console for errors

### Issue: GA4 not tracking

**Check:**

1. GA4 property ID: `G-PCJDGBMRRN`
2. Browser console for gtag errors
3. Ad blockers disabled

**Solution:**

- Verify GA4 script loads
- Check property ID is correct
- Test in incognito mode

## 📝 Rollback Procedure

If something goes wrong:

1. Go to Cloudflare Pages dashboard
2. Click on your project
3. Go to **Deployments** tab
4. Find previous working deployment
5. Click **...** menu → **Rollback to this deployment**
6. Confirm rollback

## 🎯 Success Criteria

Deployment is successful when:

- [ ] All 5 variants load without errors
- [ ] All assets (images, CSS, JS) load correctly
- [ ] `/buy` shows full-page iframe checkout
- [ ] `/gum` redirects to Gumroad
- [ ] Custom domain `signkit.work` works with SSL
- [ ] GA4 tracking events appear in dashboard
- [ ] Mobile responsive on all variants
- [ ] Page load time < 3 seconds

## 📞 Support Contacts

- **Cloudflare Pages:** [Community Forum](https://community.cloudflare.com/)
- **Gumroad:** [Help Center](https://help.gumroad.com/)
- **GA4:** [Google Analytics Help](https://support.google.com/analytics/)

## 🎉 Next Steps After Deployment

1. **Monitor Analytics**

   - Check GA4 daily for traffic and conversions
   - Review A/B test performance

2. **Enable Auto A/B Testing**

   - Once confident, set `AUTO_SPLIT = true`
   - Monitor variant performance

3. **Optimize Based on Data**

   - Identify winning variant
   - Iterate on design
   - Test new variants

4. **Set Up Alerts**
   - Cloudflare: Uptime monitoring
   - GA4: Custom alerts for conversions

---

**Deployment Date:** ******\_******

**Deployed By:** ******\_******

**Deployment URL:** ******\_******

**Custom Domain:** signkit.work

**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete
