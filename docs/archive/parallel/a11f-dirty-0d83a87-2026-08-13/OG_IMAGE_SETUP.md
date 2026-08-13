# Open Graph (OG) Image Setup Guide

## Current Issue
When sharing https://signkit.work on X (Twitter) or LinkedIn, it shows a screenshot of the app instead of a proper marketing image.

## Solution

### 1. Create a Dedicated OG Image

**Recommended Dimensions:**
- **1200 x 630 pixels** (standard OG image size)
- Works for: Twitter, LinkedIn, Facebook, Slack, Discord, etc.

**Design Guidelines:**
- Clear, bold headline: "SignKit - Extract & Sign PDFs Offline"
- Key value props: "100% Offline • No Subscriptions • $29 One-Time"
- App screenshot or mockup
- Your logo
- Clean, professional design with high contrast
- Avoid small text (won't be readable in previews)

**File Format:**
- PNG or JPG
- Keep under 5MB (ideally under 1MB)
- Name it: `og-image.png` or `og-image-signkit.png`

### 2. Where to Place the Image

Save your OG image in one of these locations:
```
/assets/og-image.png
```
or
```
/og-image.png
```

### 3. Update HTML Meta Tags

Replace the current OG image meta tags with:

```html
<!-- Open Graph / Facebook -->
<meta property="og:type" content="website" />
<meta property="og:url" content="https://signkit.work" />
<meta property="og:title" content="SignKit - Extract & Sign PDFs Offline" />
<meta property="og:description" content="Privacy-first desktop app to extract signatures and sign PDFs. 100% offline. No subscriptions. $29 one-time purchase." />
<meta property="og:image" content="https://signkit.work/assets/og-image.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="SignKit - Privacy-first PDF signature tool" />

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:url" content="https://signkit.work" />
<meta name="twitter:title" content="SignKit - Extract & Sign PDFs Offline" />
<meta name="twitter:description" content="Privacy-first desktop app to extract signatures and sign PDFs. 100% offline. No subscriptions. $29 one-time purchase." />
<meta name="twitter:image" content="https://signkit.work/assets/og-image.png" />
<meta name="twitter:image:alt" content="SignKit - Privacy-first PDF signature tool" />

<!-- LinkedIn -->
<meta property="og:site_name" content="SignKit" />
```

### 4. Design Tools for Creating OG Images

**Free Options:**
1. **Canva** (https://canva.com)
   - Template: "Facebook Post" or "Twitter Post"
   - Resize to 1200x630px
   - Use their free templates

2. **Figma** (https://figma.com)
   - Create a 1200x630px frame
   - Design from scratch or use community templates

3. **OG Image Generator Tools:**
   - https://www.opengraph.xyz/
   - https://ogimage.gallery/
   - https://og-playground.vercel.app/

**Paid Options:**
- Adobe Photoshop
- Sketch
- Affinity Designer

### 5. OG Image Content Suggestions

**Layout Option 1: Hero Style**
```
┌─────────────────────────────────────┐
│  [Logo]  SignKit                    │
│                                     │
│  Extract & Sign PDFs Offline        │
│  Privacy-First • No Subscriptions   │
│                                     │
│  [App Screenshot/Mockup]            │
│                                     │
│  $29 One-Time Purchase              │
│  100% Offline • Own Forever         │
└─────────────────────────────────────┘
```

**Layout Option 2: Split Screen**
```
┌──────────────────┬──────────────────┐
│                  │  SignKit          │
│  [App           │                   │
│   Screenshot]    │  Extract & Sign   │
│                  │  PDFs Offline     │
│                  │                   │
│                  │  ✓ 100% Offline   │
│                  │  ✓ No Subs        │
│                  │  ✓ $29 One-Time   │
└──────────────────┴──────────────────┘
```

**Layout Option 3: Feature Focus**
```
┌─────────────────────────────────────┐
│  SignKit - Privacy-First PDF Tool   │
│                                     │
│  🔐 100% Offline                    │
│  💰 $29 One-Time (No Subscriptions) │
│  ⚡ Extract & Sign in Seconds       │
│                                     │
│  [Small App Preview]                │
│                                     │
│  signkit.work                       │
└─────────────────────────────────────┘
```

### 6. Testing Your OG Image

After uploading, test your OG image on these validators:

1. **Twitter Card Validator**
   - https://cards-dev.twitter.com/validator
   - Paste your URL and click "Preview card"

2. **Facebook Sharing Debugger**
   - https://developers.facebook.com/tools/debug/
   - Paste your URL and click "Debug"
   - Click "Scrape Again" to refresh cache

3. **LinkedIn Post Inspector**
   - https://www.linkedin.com/post-inspector/
   - Paste your URL and click "Inspect"

4. **Open Graph Check**
   - https://www.opengraph.xyz/
   - Quick preview of how it looks

### 7. Cache Busting

Social platforms cache OG images. If you update your image:

1. **Add a version parameter:**
   ```html
   <meta property="og:image" content="https://signkit.work/assets/og-image.png?v=2" />
   ```

2. **Or rename the file:**
   ```
   og-image-v2.png
   ```

3. **Force refresh on platforms:**
   - Twitter: Use Card Validator
   - Facebook: Use Sharing Debugger and click "Scrape Again"
   - LinkedIn: Use Post Inspector

### 8. Quick Checklist

- [ ] Create 1200x630px OG image
- [ ] Save as `og-image.png` in `/assets/` folder
- [ ] Upload to your server
- [ ] Update HTML meta tags
- [ ] Test on Twitter Card Validator
- [ ] Test on Facebook Sharing Debugger
- [ ] Test on LinkedIn Post Inspector
- [ ] Share on social media to verify

### 9. Example Meta Tags (Complete)

```html
<head>
  <!-- Basic Meta -->
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SignKit - Extract & Sign PDFs Offline</title>
  <meta name="description" content="Privacy-first desktop app to extract signatures and sign PDFs. 100% offline. No subscriptions. $29 one-time purchase." />
  
  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://signkit.work" />
  <meta property="og:title" content="SignKit - Extract & Sign PDFs Offline" />
  <meta property="og:description" content="Privacy-first desktop app to extract signatures and sign PDFs. 100% offline. No subscriptions. $29 one-time purchase." />
  <meta property="og:image" content="https://signkit.work/assets/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="SignKit - Privacy-first PDF signature tool" />
  <meta property="og:site_name" content="SignKit" />
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:url" content="https://signkit.work" />
  <meta name="twitter:title" content="SignKit - Extract & Sign PDFs Offline" />
  <meta name="twitter:description" content="Privacy-first desktop app to extract signatures and sign PDFs. 100% offline. No subscriptions. $29 one-time purchase." />
  <meta name="twitter:image" content="https://signkit.work/assets/og-image.png" />
  <meta name="twitter:image:alt" content="SignKit - Privacy-first PDF signature tool" />
  
  <!-- Additional -->
  <link rel="canonical" href="https://signkit.work" />
</head>
```

### 10. Pro Tips

1. **Use high contrast colors** - Images appear small in feeds
2. **Keep text large** - Minimum 60px font size for headlines
3. **Test on mobile** - Most social media is viewed on phones
4. **Brand consistency** - Use your brand colors and fonts
5. **Include a call-to-action** - "$29 One-Time" or "Get Started"
6. **Show the product** - Include a screenshot or mockup
7. **Avoid clutter** - Less is more for social previews

### 11. Alternative: Dynamic OG Images

For more advanced setups, you can generate OG images dynamically:

- **Vercel OG Image Generation**: https://vercel.com/docs/concepts/functions/edge-functions/og-image-generation
- **Cloudinary**: https://cloudinary.com/documentation/social_media_cards
- **imgix**: https://docs.imgix.com/

---

**Need Help?**
- Check existing OG images for inspiration: https://ogimage.gallery/
- Use Canva templates: Search "Open Graph" or "Social Media"
- Hire a designer on Fiverr (search "OG image design")

