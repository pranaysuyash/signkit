# SignKit.work Domain Setup Guide

Complete setup instructions for `signkit.work` domain with Namecheap, Google Workspace, and Gumroad integration.

---

## 📋 Overview

- **Domain**: signkit.work
- **Registrar**: Namecheap
- **Email**: Google Workspace (psrstech.com)
- **Landing Page**: Gumroad hosted
- **Cost**: ₹264 Year 1, ₹928/year renewals

---

## 🌐 Part 1: Domain Redirect Setup

### Namecheap Advanced DNS Configuration

1. Go to [Namecheap Dashboard](https://ap.www.namecheap.com/)
2. Click **Domain List** → **Manage** next to `signkit.work`
3. Click **Advanced DNS** tab

### URL Redirect Records

**Delete any existing redirect records**, then add these two:

#### Root Domain Redirect

```text
Type: URL Redirect Record
Host: @
Value: https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj
Redirect Type: Temporary (302)
URL Masking: OFF
```

#### WWW Subdomain Redirect

```text
Type: URL Redirect Record
Host: www
Value: https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj
Redirect Type: Temporary (302)
URL Masking: OFF
```

### Why These Settings?

- **Temporary (302)**: Allows future A/B testing and landing page changes without SEO penalty
- **Masking OFF**: Ensures Gumroad checkout works correctly; users see actual product URL
- **Both @ and www**: Covers all variations (signkit.work and www.signkit.work)

### HTTPS Note

✅ HTTPS works automatically - Namecheap handles SSL for redirects. No certificate needed.

---

## 📧 Part 2: Email Setup with Google Workspace

### Step 1: Add DNS Records in Namecheap

In **Advanced DNS** tab, add these records:

#### MX Records (Mail Routing)

```text
Type: MX | Host: @ | Value: ASPMX.L.GOOGLE.COM      | Priority: 1  | TTL: Automatic
Type: MX | Host: @ | Value: ALT1.ASPMX.L.GOOGLE.COM | Priority: 5  | TTL: Automatic
Type: MX | Host: @ | Value: ALT2.ASPMX.L.GOOGLE.COM | Priority: 5  | TTL: Automatic
Type: MX | Host: @ | Value: ALT3.ASPMX.L.GOOGLE.COM | Priority: 10 | TTL: Automatic
Type: MX | Host: @ | Value: ALT4.ASPMX.L.GOOGLE.COM | Priority: 10 | TTL: Automatic
```

#### TXT Records (Authentication)

**SPF Record (Sender Authentication):**

```text
Type: TXT
Host: @
Value: v=spf1 include:_spf.google.com ~all
TTL: Automatic
```

**DMARC Record (Email Policy):**

```text
Type: TXT
Host: _dmarc
Value: v=DMARC1; p=none; rua=mailto:founder@psrstech.com
TTL: Automatic
```

### Step 2: Verify Domain in Google Workspace

1. Go to [Google Workspace Admin Console](https://admin.google.com)
2. Navigate to **Account** → **Domains** → **Manage domains**
3. Click **Add a domain** → Select **Add a domain alias**
4. Enter: `signkit.work`
5. Google will provide a TXT verification record like:

   ```text
   Type: TXT
   Host: @
   Value: google-site-verification=XXXXXXXXXXXXXXXXXXXX
   TTL: Automatic
   ```

6. Add this TXT record to Namecheap Advanced DNS
7. Wait 5-10 minutes, then click **Verify** in Google Workspace

### Step 3: Add Email Aliases

Once domain is verified:

1. In Google Workspace Admin, go to **Directory** → **Users**
2. Click on your account (founder@psrstech.com)
3. Click **User information** → **Email aliases** → **Add an alias**
4. Add these essential aliases:

```text
support@signkit.work  (Essential - for customer support)
founder@signkit.work  (Optional - for partnerships/outreach)
```

**Note:** You can add more specialized emails later (privacy@, legal@, etc.) if needed, but these two are sufficient for launch.

### Email Benefits

✅ **Receive** emails at all @signkit.work addresses in your existing Gmail  
✅ **Send/Reply FROM** any alias (looks professional)  
✅ All Gmail features (labels, filters, search, spam protection)  
✅ No extra cost (uses existing Google Workspace license)

---

## ⚙️ Part 3: Nameserver Configuration

### Current Setup (Keep As-Is)

```text
Nameservers: Namecheap BasicDNS
dns1.registrar-servers.com
dns2.registrar-servers.com
```

**✅ No changes needed!** You're managing DNS through Namecheap's interface.

### When Would You Change Nameservers?

Only if:

- Moving to Cloudflare for advanced features/CDN
- Using a hosting platform that requires their nameservers
- Implementing Cloudflare Workers for A/B testing (see below)

---

## 🧪 Part 4: A/B Testing Setup

You have two Gumroad landing pages:

- **Version A**: `https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj`
- **Version B**: `https://gum.new/gum/cmhyh0is2000s04l7glct4xtb`

### Option 1: Manual Week-by-Week Testing (Simplest)

**Best for: Launch phase, low traffic**

1. Week 1: Point domain to Version A
2. Track sales in Gumroad analytics
3. Week 2: Change redirect to Version B
4. Compare conversion rates

**Pros:**

- Zero setup, free
- Quick to implement

**Cons:**

- Not simultaneous (external factors can skew results)
- Requires manual switching

### Option 2: URL Shortener with Split Testing

**Best for: Quick simultaneous testing without code**

Services that offer this:

- **Rebrandly** (free tier): Custom short links with A/B testing
- **Short.io** ($20/mo): Advanced analytics, split testing
- **BL.INK** ($24/mo): Enterprise features

**Setup:**

1. Create account on chosen service
2. Create "Smart Link" with 50/50 traffic split:
   - Destination A: Version A Gumroad URL
   - Destination B: Version B Gumroad URL
3. Get your smart link URL (e.g., `https://rebrand.ly/signkit`)
4. Update Namecheap redirect to point to smart link
5. Track conversions in service dashboard

**Pros:**

- Real 50/50 traffic split
- Built-in analytics
- No coding required

**Cons:**

- Extra redirect hop (slight delay)
- Costs money (except Rebrandly free tier)

### Option 3: Cloudflare Workers (Technical, Free)

**Best for: High traffic, custom analytics, zero cost**

**Prerequisites:**

- Change nameservers to Cloudflare
- Basic JavaScript knowledge

**Setup Steps:**

1. **Add Domain to Cloudflare:**

   - Sign up at [cloudflare.com](https://cloudflare.com)
   - Add `signkit.work`
   - Change nameservers in Namecheap to Cloudflare's (provided after signup)

2. **Create Worker:**

   Go to Workers → Create a Service → Quick Edit

   ```javascript
   addEventListener('fetch', (event) => {
     event.respondWith(handleRequest(event.request));
   });

   async function handleRequest(request) {
     // Your two Gumroad landing pages
     const variants = [
       'https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj', // Version A
       'https://gum.new/gum/cmhyh0is2000s04l7glct4xtb', // Version B
     ];

     // 50/50 random split
     const variantIndex = Math.random() < 0.5 ? 0 : 1;

     // Optional: Track which variant was shown
     const headers = new Headers();
     headers.set('X-AB-Variant', variantIndex === 0 ? 'A' : 'B');

     // Redirect to chosen variant
     return Response.redirect(variants[variantIndex], 302);
   }
   ```

3. **Add Route:**

   - Workers → Routes → Add route
   - Route: `signkit.work/*`
   - Service: Your worker name

4. **Track Results:**
   - Use Gumroad's built-in analytics
   - Compare sales for each page
   - Or add analytics tracking in Worker code

**Pros:**

- Free (100k requests/day on free tier)
- True 50/50 split
- Fast (Cloudflare edge network)
- Can add custom analytics/tracking

**Cons:**

- Requires nameserver change (30min-2hr propagation)
- Needs JavaScript knowledge
- More complex setup

### Option 4: Static HTML Page with JavaScript Redirect

**Best for: No budget, simple setup, okay with slight delay**

**Setup:**

1. **Create `index.html`:**

   ```html
   <!DOCTYPE html>
   <html lang="en">
     <head>
       <meta charset="UTF-8" />
       <meta name="viewport" content="width=device-width, initial-scale=1.0" />
       <title>SignKit - Redirecting...</title>
       <meta name="robots" content="noindex" />
       <style>
         body {
           margin: 0;
           padding: 0;
           font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
             sans-serif;
           display: flex;
           align-items: center;
           justify-content: center;
           height: 100vh;
           background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
           color: white;
         }
         .loader {
           text-align: center;
         }
         .spinner {
           border: 4px solid rgba(255, 255, 255, 0.3);
           border-radius: 50%;
           border-top: 4px solid white;
           width: 40px;
           height: 40px;
           animation: spin 1s linear infinite;
           margin: 0 auto 20px;
         }
         @keyframes spin {
           0% {
             transform: rotate(0deg);
           }
           100% {
             transform: rotate(360deg);
           }
         }
       </style>
       <script>
         // Your two Gumroad landing pages
         const variants = [
           'https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj', // Version A
           'https://gum.new/gum/cmhyh0is2000s04l7glct4xtb', // Version B
         ];

         // 50/50 random redirect
         const randomVariant = variants[Math.random() < 0.5 ? 0 : 1];

         // Optional: Track variant in localStorage for consistency
         if (!sessionStorage.getItem('variant')) {
           const chosen = Math.random() < 0.5 ? 0 : 1;
           sessionStorage.setItem('variant', chosen);
         }

         const chosenVariant = variants[sessionStorage.getItem('variant')];

         // Redirect immediately
         window.location.replace(chosenVariant);
       </script>
     </head>
     <body>
       <div class="loader">
         <div class="spinner"></div>
         <p>Loading SignKit...</p>
       </div>
     </body>
   </html>
   ```

2. **Host Page (Choose One):**

   **GitHub Pages (Free):**

   - Create repo: `signkit-landing`
   - Add `index.html`
   - Settings → Pages → Deploy from main branch
   - Get URL: `https://yourusername.github.io/signkit-landing`

   **Netlify (Free):**

   - Drag folder with `index.html` to [netlify.com/drop](https://netlify.com/drop)
   - Get URL: `https://random-name.netlify.app`
   - Can add custom domain later

3. **Update Namecheap Redirect:**
   - Change redirect value to your hosted page URL
   - Users hit `signkit.work` → your HTML page → redirects to random Gumroad page

**Pros:**

- Free
- Simple HTML/JS
- Session consistency (same user sees same variant)

**Cons:**

- ~200ms delay (extra page load)
- SEO implications (noindex tag helps)
- Needs hosting

---

## 🎯 A/B Testing Recommendation

### For Black Friday Launch (15 days away)

**Use Option 1** - Manual week-by-week testing:

1. Launch with Version A for first week
2. Collect sales data from Gumroad
3. Switch to Version B for second week
4. Compare conversion rates

**Why?**

- Zero setup time = focus on launch
- Gumroad analytics give you all the data you need
- Can implement better testing after initial sales

### Post-Launch (December onwards)

**Upgrade to Option 2 or 3:**

- Option 2 (Rebrandly) if you want simplicity
- Option 3 (Cloudflare Workers) if you want free + powerful

---

### Setup Checklist

### Domain & Redirect

- [ ] Add URL redirect for `@` (root) → Gumroad page
- [ ] Add URL redirect for `www` → Gumroad page
- [ ] Set both redirects to Temporary (302)
- [ ] Verify HTTPS works: visit `https://signkit.work`

### Email Setup

- [ ] Add MX record in Namecheap DNS (SMTP.GOOGLE.COM)
- [ ] Add SPF TXT record in Namecheap DNS
- [ ] Add Google verification TXT record in Namecheap DNS
- [ ] Wait 10 minutes for DNS propagation
- [ ] Verify domain in Google Workspace Admin
- [ ] Add email alias: `support@signkit.work`
- [ ] Add email alias: `founder@signkit.work` (optional)
- [ ] Test: Send email to `support@signkit.work`
- [ ] Test: Reply FROM `support@signkit.work` in Gmail

### Nameservers

- [ ] Verify Namecheap BasicDNS is active (no changes needed)

### A/B Testing (Optional)

- [ ] Choose testing method (Option 1-4)
- [ ] If Option 3: Change to Cloudflare nameservers
- [ ] If Option 4: Host HTML page and update redirect
- [ ] Document which variant is active
- [ ] Set reminder to switch/check results

---

## 🧪 Testing & Verification

### Test Domain Redirect

```bash
# Check redirect works
curl -I https://signkit.work

# Should show:
# HTTP/1.1 302 Found
# Location: https://gum.new/gum/...
```

### Test Email Receiving

1. Send test email to `support@signkit.work`
2. Check `founder@psrstech.com` Gmail inbox
3. Should arrive within 1-2 minutes

### Test Email Sending

1. In Gmail, click **Compose**
2. Click **From** dropdown
3. Select `support@signkit.work`
4. Send test email to yourself
5. Verify sender shows as `support@signkit.work`

### DNS Propagation Check

Use these tools to verify DNS changes are live:

- [whatsmydns.net](https://whatsmydns.net) - Global DNS checker
- [mxtoolbox.com](https://mxtoolbox.com) - MX record validator
- [dnschecker.org](https://dnschecker.org) - Multi-location DNS lookup

**Note:** DNS changes can take 5 minutes to 48 hours (usually ~30 minutes)

---

## 📊 Analytics & Tracking

### Gumroad Analytics (Built-in)

Track in Gumroad dashboard:

- Page views per variant
- Conversion rate
- Revenue per variant
- Traffic sources

### Optional: Add UTM Parameters

For better tracking, add UTM parameters to your Gumroad URLs:

**Version A:**

```text
https://gum.new/gum/cmhyha3rs001h04l7ccem2nkj?utm_source=signkit&utm_medium=redirect&utm_campaign=variant_a
```

**Version B:**

```text
https://gum.new/gum/cmhyh0is2000s04l7glct4xtb?utm_source=signkit&utm_medium=redirect&utm_campaign=variant_b
```

This gives you detailed traffic analytics in Gumroad.

---

## 🔧 Troubleshooting

### Domain doesn't redirect

**Check:**

- URL Redirect Records exist in Namecheap Advanced DNS
- Records are enabled (not disabled)
- Wait 30 minutes for DNS propagation
- Try incognito/private browsing (clears cache)

**Fix:**

```bash
# Clear DNS cache (macOS)
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder

# Clear DNS cache (Windows)
ipconfig /flushdns
```

### Email not arriving

**Check:**

- MX records are correct in Namecheap DNS
- Domain verified in Google Workspace
- Email aliases added to your account
- Check spam folder in Gmail
- Wait 1 hour for DNS propagation

**Verify MX records:**

```bash
nslookup -type=mx signkit.work

# Should show Google's MX servers
```

### Can't send from @signkit.work

**Check:**

- Domain verified in Google Workspace (green checkmark)
- Aliases added to your Google account
- SPF record exists in DNS
- Try Gmail web (not mobile app)

**Fix:**

1. Go to Gmail → Settings → Accounts
2. Check if `support@signkit.work` is listed
3. If not, domain verification may have failed
4. Re-verify in Google Workspace Admin

### HTTPS certificate error

**Not an issue!** Namecheap provides SSL for redirects automatically. If you see a brief warning, it resolves itself during redirect.

---

## 💰 Cost Summary

| Item                  | Year 1   | Renewal (Year 2+) |
| --------------------- | -------- | ----------------- |
| Domain (signkit.work) | ₹264     | ₹928/year         |
| Google Workspace      | $0\*     | $0\*              |
| Email hosting         | $0\*     | $0\*              |
| A/B testing (manual)  | $0       | $0                |
| **Total**             | **₹264** | **₹928/year**     |

\*Using existing Google Workspace license (psrstech.com)

### Optional A/B Testing Costs

- Rebrandly free tier: $0 (limited features)
- Short.io: $20/month
- Cloudflare Workers: $0 (free tier)
- Static HTML hosting: $0 (GitHub Pages/Netlify)

---

## 📞 Support Contacts

### Namecheap Support

- URL: [support.namecheap.com](https://support.namecheap.com)
- Live Chat: 24/7
- Email: support@namecheap.com

### Google Workspace Support

- URL: [support.google.com/a](https://support.google.com/a)
- Phone: Varies by plan
- Help Center: Extensive documentation

### Gumroad Support

- URL: [help.gumroad.com](https://help.gumroad.com)
- Email: support@gumroad.com
- Response time: 24-48 hours

---

## 🚀 Next Steps

1. **Complete domain setup** (redirects + email)
2. **Verify everything works** (test redirect, send/receive emails)
3. **Update Gumroad product page** if needed
4. **Launch Black Friday campaign** (Nov 29)
5. **Monitor analytics** in Gumroad dashboard
6. **Implement proper A/B testing** post-launch (December)

---

## 📝 Change Log

| Date         | Change                           | By      |
| ------------ | -------------------------------- | ------- |
| Nov 14, 2025 | Initial setup documentation      | Copilot |
| Nov 14, 2025 | Domain registered (signkit.work) | Pranay  |

---

**Questions or issues?** Email: founder@psrstech.com
