# Landing Page Setup - Complete Notes

## Branch: landing-page

### A/B Test Variants

1. **Control (/)** - Neo-brutalism design with CTA buttons to Gumroad
2. **Variant 2 (/buy)** - Embedded gum.new checkout iframe: `https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj`
3. **Variant 3 (/purchase)** - Claude v2 design with Gumroad CTA
4. **Variant 4 (/gum)** - Direct redirect to: `https://pranaysuyash.gumroad.com/l/signkit-v1`

### Product Links

- **Gumroad Product**: `https://pranaysuyash.gumroad.com/l/signkit-v1`
- **gum.new Checkout**: `https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj`

### Analytics Setup

- **Google Analytics 4**: `G-PCJDGBMRRN` (active, free)
- **Plausible Analytics**: Commented out (paid service - $9/month)
  - Can be enabled later by uncommenting in index.html and purchase.html
  - Script: `https://plausible.io/js/pa-Z7IHNxIIEUXGeZe1RBq2s.js`

### Files Structure

```
landing-page branch:
├── index.html (Control + /buy + /gum routing logic)
├── purchase.html (Claude v2 variant)
├── screenshots/ (3 product screenshots)
├── assets/files/ (icons)
├── web/live/css/ (CSS for purchase.html)
└── web/live/js/ (JS for purchase.html)
```

### Local Testing

- Run: `python3 serve.py` (custom routing server)
- Or: `python3 -m http.server 8080`
- Test URLs:
  - http://127.0.0.1:8080/ (control)
  - http://127.0.0.1:8080/buy (gum.new iframe)
  - http://127.0.0.1:8080/purchase (Claude variant)
  - http://127.0.0.1:8080/gum (redirect)

### Purchase.html Fixes Applied

1. ✅ Removed 4th demo dot (3 steps only)
2. ✅ Fixed screenshot order:
   - Step 1: screenshot-1.png (Upload)
   - Step 2: screenshot-2.png (Select Signature)
   - Step 3: screenshot-3.png (Place on PDF)
3. ✅ Slowed animation: 3s → 5s transitions
4. ✅ Hidden "Watch Demo" button (nav + hero)
5. ✅ Footer links now display inline in one row (changed CSS from `display: block` to `display: inline-block`)

### Messaging Updates

- Changed "Lifetime" → "Own Forever"
- Removed fake "Launch Special 25% off" discount
- All pricing: $29

### Deployment

- **Platform**: Cloudflare Pages (free tier)
- **Branch to deploy**: landing-page
- **Domain**: signkit.work
- **Build settings**: None needed (static HTML)

### A/B Testing Options

- **Manual**: Users visit different URLs (/buy, /purchase, /gum)
- **Auto-split**: Set `AUTO_SPLIT = true` in index.html for automatic random assignment

### TODO Before Launch

- [ ] Test all 4 variants on signkit.work domain
- [ ] Verify gum.new iframe works on deployed site
- [ ] Decide on A/B test strategy (manual vs auto-split)
- [ ] Optional: Enable Plausible Analytics ($9/month)
- [ ] Optional: Add Cloudflare Web Analytics (free, via dashboard)
