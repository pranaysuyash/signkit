# SignKit Landing Page - Cloudflare Pages Deployment

> A/B testing framework for SignKit landing page with 4 variants optimized for conversion

## 🎯 Overview

This landing page setup enables A/B testing of 4 different checkout flows to optimize conversion rate for SignKit, a privacy-first PDF signature extraction tool.

## 📁 Project Structure

```
.
├── index.html                    # Main entry with A/B routing logic
├── root.html                     # Variant 1: Control (neo-brutalism)
├── buy.html                      # Variant 2: Embedded checkout
├── purchase.html                 # Variant 3: SaaS landing
├── gum.html                      # Variant 4: Direct redirect
├── test-variants.html            # Testing dashboard
├── _redirects                    # Cloudflare Pages routing
├── wrangler.toml                 # Cloudflare configuration
├── .cfignore                     # Deployment exclusions
│
├── 📚 Documentation
│   ├── QUICK_START.md            # 5-minute deployment guide
│   ├── CLOUDFLARE_DEPLOYMENT.md  # Comprehensive deployment guide
│   ├── DEPLOYMENT_CHECKLIST.md   # Step-by-step checklist
│   └── AB_TEST_STRUCTURE.md      # A/B test details
│
├── assets/                       # Icons and static files
│   └── files/
│       ├── signkit_icon_32x32.png
│       ├── signkit_icon_64x64.png
│       └── ...
│
├── screenshots/                  # Product screenshots
│   ├── screenshot-1.png
│   ├── screenshot-2.png
│   └── screenshot-3.png
│
└── web/                          # Additional resources
    └── claude_landing_page_v2/
        ├── css/
        └── js/
```

## 🚀 Quick Deploy

### 1. Push to GitHub
```bash
git add .
git commit -m "feat: Cloudflare Pages deployment"
git push origin landing-page
```

### 2. Deploy to Cloudflare
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. **Workers & Pages** → **Pages** → **Create project**
3. Connect GitHub repo, select `landing-page` branch
4. Build settings: Framework = None, Output = `/`
5. Click **Save and Deploy**

### 3. Add Custom Domain
1. In Cloudflare Pages: **Custom domains** → **Set up**
2. Enter: `signkit.work`
3. Cloudflare auto-configures DNS

**Done!** 🎉

See [QUICK_START.md](QUICK_START.md) for detailed 5-minute guide.

## 🧪 A/B Test Variants

### Variant 1: Control (`/root`)
- **Design:** Neo-brutalism
- **CTA:** External Gumroad link
- **Hypothesis:** Simple, privacy-focused design converts best

### Variant 2: Embedded (`/buy`)
- **Design:** Full-page iframe checkout
- **CTA:** Embedded Gumroad checkout
- **Hypothesis:** Keeping users on domain increases trust

### Variant 3: SaaS (`/purchase`)
- **Design:** Traditional SaaS landing
- **CTA:** External Gumroad link
- **Hypothesis:** Detailed features increase perceived value

### Variant 4: Direct (`/gum`)
- **Design:** Immediate redirect
- **CTA:** Instant redirect to Gumroad
- **Hypothesis:** Minimal friction for high-intent users

## 📊 A/B Testing Modes

### Manual Mode (Current)
```javascript
const AUTO_SPLIT = false; // in index.html
```
- Root `/` shows control page
- Users access variants via direct URLs: `/root`, `/buy`, `/purchase`, `/gum`
- Good for testing and QA

### Auto A/B Mode
```javascript
const AUTO_SPLIT = true; // in index.html
```
- Root `/` randomly assigns visitors (25% each variant)
- Assignment stored in localStorage for consistency
- Tracks impressions in GA4

## 📈 Analytics

All variants track to Google Analytics 4:
- **Property:** `G-PCJDGBMRRN`
- **Event:** `ab_test_impression`
- **Parameters:** `variant`, `experiment_id`

View results: [GA4 Dashboard](https://analytics.google.com/) → Events → `ab_test_impression`

## 🧰 Local Testing

### Start Server
```bash
python3 -m http.server 8080
```

### Test Dashboard
Open: http://localhost:8080/test-variants.html

### Test Individual Variants
- Control: http://localhost:8080/root
- Embedded: http://localhost:8080/buy
- SaaS: http://localhost:8080/purchase
- Redirect: http://localhost:8080/gum

### Run Tests
```bash
chmod +x test-pages.sh
./test-pages.sh
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [QUICK_START.md](QUICK_START.md) | Deploy in 5 minutes |
| [CLOUDFLARE_DEPLOYMENT.md](CLOUDFLARE_DEPLOYMENT.md) | Comprehensive deployment guide |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Step-by-step checklist |
| [AB_TEST_STRUCTURE.md](AB_TEST_STRUCTURE.md) | A/B test details and metrics |

## ✅ Pre-Deployment Checklist

- [x] All HTML files created and tested
- [x] Assets verified (icons, screenshots)
- [x] CSS/JS dependencies present
- [x] `_redirects` file configured
- [x] `.cfignore` excludes unnecessary files
- [x] GA4 tracking on all variants
- [x] Local testing passed
- [x] Documentation complete

## 🔧 Configuration Files

### `_redirects`
Cloudflare Pages routing rules for clean URLs

### `wrangler.toml`
Cloudflare configuration (optional, for CLI deployment)

### `.cfignore`
Excludes Python, backend, and build files from deployment

## 🎯 Success Metrics

### Primary
- **Conversion Rate:** Purchases / Unique Visitors

### Secondary
- Click-through Rate
- Bounce Rate
- Time on Page
- Exit Rate

## 🐛 Troubleshooting

### Pages not loading?
Check Cloudflare dashboard → Deployments for build status

### Assets 404?
Verify paths are relative and files exist in repo

### Iframe not loading?
Check browser console for CSP errors, verify Gumroad URL

### A/B routing not working?
Verify `AUTO_SPLIT` setting, clear localStorage

See [CLOUDFLARE_DEPLOYMENT.md](CLOUDFLARE_DEPLOYMENT.md) for detailed troubleshooting.

## 🔄 Deployment Workflow

```
Local Development
    ↓
Git Push to landing-page branch
    ↓
Cloudflare Auto-Deploy (~1 min)
    ↓
Live at signkit.work
```

## 📞 Support

- **Cloudflare:** [Community Forum](https://community.cloudflare.com/)
- **Gumroad:** [Help Center](https://help.gumroad.com/)
- **GA4:** [Analytics Help](https://support.google.com/analytics/)
- **SignKit:** support@signkit.work

## 🎉 What's Next?

1. ✅ Deploy to Cloudflare Pages
2. ✅ Test all variants manually
3. ⬜ Monitor analytics for 24 hours
4. ⬜ Enable A/B testing (`AUTO_SPLIT = true`)
5. ⬜ Run test for 14-30 days (100+ conversions per variant)
6. ⬜ Analyze results and identify winner
7. ⬜ Implement winning variant as default
8. ⬜ Iterate and optimize

## 📄 License

Part of SignKit project. See main repository for license details.

---

**Status:** ✅ Ready for deployment  
**Last Updated:** November 18, 2025  
**Branch:** `landing-page`  
**Deployment Target:** Cloudflare Pages  
**Custom Domain:** signkit.work
