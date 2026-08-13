# SignKit Landing Page - Quick Start

**Branch**: `landing-page`  
**Domain**: signkit.work

## 🚀 Local Testing

### Option 1: Simple Server (query params only)

```bash
python3 -m http.server 8080
```

Test URLs:

- http://127.0.0.1:8080/ (Control)
- http://127.0.0.1:8080/?variant=buy (Embedded iframe)
- http://127.0.0.1:8080/purchase.html (Claude variant)
- http://127.0.0.1:8080/?variant=gum (Redirect)

### Option 2: Custom Router (clean URLs)

```bash
python3 serve.py
```

Test URLs:

- http://127.0.0.1:8080/ (Control)
- http://127.0.0.1:8080/buy (Embedded iframe)
- http://127.0.0.1:8080/purchase (Claude variant)
- http://127.0.0.1:8080/gum (Redirect)
- http://127.0.0.1:8080/test-variants.html (Dashboard)

## 📊 A/B Test Variants

| Variant          | Route                          | Description                           |
| ---------------- | ------------------------------ | ------------------------------------- |
| **Control**      | `/`                            | Neo-brutalism design with Gumroad CTA |
| **V2: Embedded** | `/buy` or `?variant=buy`       | gum.new checkout iframe inline        |
| **V3: Claude**   | `/purchase` or `purchase.html` | Claude v2 landing page                |
| **V4: Direct**   | `/gum` or `?variant=gum`       | Immediate Gumroad redirect            |

## 🔗 Product Links

- **Gumroad Product**: https://pranaysuyash.gumroad.com/l/signkit-v1
- **gum.new Embed**: https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj

## 📈 Analytics

- **GA4**: G-PCJDGBMRRN (active)
- **Plausible**: Commented out (paid service - $9/month)

## 🛠️ Auto A/B Split

By default, users must visit specific URLs. To enable **automatic random assignment**:

1. Edit `index.html` line ~950
2. Change: `const AUTO_SPLIT = false;` → `const AUTO_SPLIT = true;`
3. Visitors to `/` will be randomly assigned to a variant

## 🚀 Deployment (Cloudflare Pages)

1. Push changes:

   ```bash
   git push origin landing-page
   ```

2. Cloudflare Pages Settings:

   - **Branch**: landing-page
   - **Build command**: (none - static HTML)
   - **Build output**: / (root)
   - **Domain**: signkit.work

3. Test production:
   - https://signkit.work/ (Control)
   - https://signkit.work/buy (Embedded)
   - https://signkit.work/purchase (Claude)
   - https://signkit.work/gum (Redirect)

## 📄 Documentation

- **AB_TEST_VARIANTS.md** - Complete A/B test documentation
- **LANDING_PAGE_SETUP_NOTES.md** - Setup notes and fixes
- **test-variants.html** - Visual testing dashboard

## ✅ Recent Fixes (Nov 18, 2025)

1. ✅ Fixed /buy iframe: querySelector('.hero') → querySelector('.hero-main')
2. ✅ Footer horizontal layout (purchase.html)
3. ✅ Removed 4th demo dot
4. ✅ Slowed animation to 5s
5. ✅ Fixed screenshot order
6. ✅ Hidden Watch Demo buttons
7. ✅ Plausible properly commented

## 🎯 Next Steps

- [ ] Deploy to Cloudflare Pages
- [ ] Test all variants on production
- [ ] Decide on A/B strategy (manual vs auto-split)
- [ ] Monitor GA4 for conversion rates
- [ ] Optional: Enable Plausible Analytics ($9/month)
