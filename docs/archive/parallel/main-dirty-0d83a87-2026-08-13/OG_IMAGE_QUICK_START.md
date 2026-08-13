# OG Image Quick Start - Action Items

## What You Need To Do

### 1. Create Your OG Image (15-30 minutes)

**Option A: Use Canva (Easiest)**
1. Go to https://canva.com
2. Create a design with dimensions: **1200 x 630 pixels**
3. Use this content:
   ```
   Headline: SignKit
   Subheadline: Extract & Sign PDFs Offline
   
   Key Points:
   • 100% Offline - Your files never leave your device
   • $29 One-Time - No subscriptions
   • Privacy-First - No cloud upload
   
   Include: App screenshot or mockup
   Add: Your logo (signkit_icon_256x256.png)
   ```
4. Download as PNG
5. Name it: `og-image.png`

**Option B: Quick Template**
Use this Canva template structure:
- Background: Clean gradient or solid color (#4f46e5 or #f5f5f5)
- Logo: Top left (64x64px)
- Headline: Large, bold, centered
- 3 bullet points with icons
- Small app screenshot at bottom
- Website URL at bottom right

### 2. Upload the Image

Save your `og-image.png` file to:
```
/assets/og-image.png
```

Then upload it to your server at:
```
https://signkit.work/assets/og-image.png
```

### 3. Verify It's Working

**Test on Twitter:**
1. Go to: https://cards-dev.twitter.com/validator
2. Enter: https://signkit.work
3. Click "Preview card"
4. You should see your new OG image

**Test on Facebook:**
1. Go to: https://developers.facebook.com/tools/debug/
2. Enter: https://signkit.work
3. Click "Debug"
4. Click "Scrape Again" to refresh cache

**Test on LinkedIn:**
1. Go to: https://www.linkedin.com/post-inspector/
2. Enter: https://signkit.work
3. Click "Inspect"

### 4. Update Other Pages (Optional)

If you have other HTML files (buy.html, gum.html, etc.), update their OG tags too:

```html
<meta property="og:image" content="https://signkit.work/assets/og-image.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:image" content="https://signkit.work/assets/og-image.png" />
```

## Design Inspiration

**Good Examples:**
- https://ogimage.gallery/ (browse examples)
- Search "SaaS OG image" on Dribbble
- Look at Product Hunt featured products

**Key Elements:**
1. Large, readable headline (60px+ font)
2. Clear value proposition
3. Visual element (screenshot, mockup, or illustration)
4. Brand colors and logo
5. Price or CTA if relevant

## Common Mistakes to Avoid

❌ Text too small (won't be readable)
❌ Too much information (cluttered)
❌ Low contrast (hard to read)
❌ Wrong dimensions (gets cropped)
❌ File too large (>5MB)

✅ Large, bold text
✅ Simple, focused message
✅ High contrast
✅ 1200x630px exactly
✅ Under 1MB file size

## Current Status

- [x] HTML meta tags updated in index.html
- [ ] Create og-image.png (1200x630px)
- [ ] Upload to /assets/og-image.png
- [ ] Test on Twitter Card Validator
- [ ] Test on Facebook Sharing Debugger
- [ ] Test on LinkedIn Post Inspector
- [ ] Update other HTML files (buy.html, gum.html, etc.)

## Need Help?

**Quick Options:**
1. **Hire on Fiverr**: Search "OG image design" ($10-30)
2. **Use AI**: Try Midjourney or DALL-E for background
3. **Use Template**: Canva has free OG image templates

**Content for Designer:**
```
Project: OG Image for SignKit
Dimensions: 1200 x 630 pixels
Format: PNG

Content:
- Logo: [attach signkit_icon_256x256.png]
- Headline: "SignKit"
- Subheadline: "Extract & Sign PDFs Offline"
- Key points:
  • 100% Offline
  • $29 One-Time
  • No Subscriptions
- Include: Clean app screenshot
- Style: Modern, professional, high contrast
- Colors: Use #4f46e5 (purple) and #ffb800 (yellow)
```

---

**Once you create the image, just upload it and test!**

