# SignKit Landing Page - Quick Start Guide

## 🚀 Deploy to Cloudflare Pages in 5 Minutes

### Prerequisites
- GitHub account with repository access
- Cloudflare account (free tier works)
- Domain `signkit.work` added to Cloudflare

---

## Step 1: Push to GitHub (30 seconds)

```bash
# Ensure you're on the landing-page branch
git branch

# Stage and commit all changes
git add .
git commit -m "feat: Cloudflare Pages deployment ready"

# Push to GitHub
git push origin landing-page
```

---

## Step 2: Connect to Cloudflare (2 minutes)

1. Go to https://dash.cloudflare.com/
2. Click **Workers & Pages** → **Pages**
3. Click **Create a project** → **Connect to Git**
4. Select your repository
5. Choose branch: `landing-page`
6. Click **Begin setup**

---

## Step 3: Configure Build (30 seconds)

**Framework preset:** None  
**Build command:** (leave empty)  
**Build output directory:** `/`  
**Root directory:** (leave empty)

Click **Save and Deploy**

---

## Step 4: Wait for Deployment (1-2 minutes)

Watch the build log. When complete, you'll see:
```
✅ Success! Your site is live at:
https://signkit-landing.pages.dev
```

---

## Step 5: Test All Variants (1 minute)

Open these URLs and verify they load:

- ✅ https://signkit-landing.pages.dev/
- ✅ https://signkit-landing.pages.dev/root
- ✅ https://signkit-landing.pages.dev/buy
- ✅ https://signkit-landing.pages.dev/purchase
- ✅ https://signkit-landing.pages.dev/gum

---

## Step 6: Add Custom Domain (1 minute)

1. In Cloudflare Pages, click **Custom domains**
2. Click **Set up a custom domain**
3. Enter: `signkit.work`
4. Click **Activate domain**

Cloudflare automatically configures DNS. Wait 5 minutes for SSL.

---

## ✅ Done!

Your landing page is now live at:
- **Cloudflare URL:** https://signkit-landing.pages.dev
- **Custom Domain:** https://signkit.work

---

## 🧪 Test All Variants

Visit: https://signkit.work/test-variants.html

This dashboard lets you test all 4 variants:
1. Control (Neo-brutalism)
2. Embedded Checkout
3. SaaS Landing
4. Direct Redirect

---

## 📊 Enable A/B Testing

When ready to start A/B testing:

1. Edit `index.html`
2. Find line: `const AUTO_SPLIT = false;`
3. Change to: `const AUTO_SPLIT = true;`
4. Commit and push:
   ```bash
   git add index.html
   git commit -m "Enable A/B testing"
   git push origin landing-page
   ```

Cloudflare auto-deploys in ~1 minute.

---

## 📈 View Analytics

Go to: https://analytics.google.com/

1. Select property: `G-PCJDGBMRRN`
2. Navigate to **Reports** → **Events**
3. Look for event: `ab_test_impression`
4. View by `variant` parameter

---

## 🐛 Troubleshooting

### Pages not loading?
```bash
# Check deployment status
# Go to Cloudflare dashboard → Your project → Deployments
```

### Assets not loading?
```bash
# Verify files exist in repo
ls -la assets/files/
ls -la screenshots/
```

### Need to rollback?
```bash
# In Cloudflare dashboard:
# Your project → Deployments → Previous deployment → Rollback
```

---

## 📞 Need Help?

- **Deployment Guide:** See `CLOUDFLARE_DEPLOYMENT.md`
- **Full Checklist:** See `DEPLOYMENT_CHECKLIST.md`
- **A/B Test Details:** See `AB_TEST_STRUCTURE.md`
- **Cloudflare Support:** https://community.cloudflare.com/

---

## 🎯 What's Next?

1. ✅ Deploy to Cloudflare Pages
2. ✅ Test all variants
3. ✅ Add custom domain
4. ⬜ Monitor analytics for 24 hours
5. ⬜ Enable A/B testing (`AUTO_SPLIT = true`)
6. ⬜ Run test for 14-30 days
7. ⬜ Analyze results
8. ⬜ Implement winning variant

---

**Total Time:** ~5 minutes  
**Difficulty:** Easy  
**Cost:** Free (Cloudflare Pages free tier)
