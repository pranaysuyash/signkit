# SignKit Domain Setup Guide

## Current Status
- ✅ Domain `signkit.work` added to Cloudflare
- ✅ Domain is Active in Cloudflare
- ✅ Cloudflare Pages project deployed: `signkit-landing`
- 🔄 Need to connect domain to Pages deployment

---

## Step 1: Connect Domain to Cloudflare Pages

### In Cloudflare Dashboard:

1. **Go to Workers & Pages**
   - URL: https://dash.cloudflare.com/
   - Click **Workers & Pages** in left sidebar

2. **Select Your Project**
   - Click on `signkit-landing`

3. **Add Custom Domain**
   - Click **Custom domains** tab
   - Click **Set up a custom domain**
   - Enter: `signkit.work`
   - Click **Continue**

4. **Cloudflare Will Auto-Configure**
   - Cloudflare will automatically create a CNAME record
   - This points `signkit.work` → `signkit-landing.pages.dev`
   - SSL certificate will be provisioned automatically

5. **Wait for Activation**
   - Status will show "Initializing" → "Active"
   - Usually takes 1-5 minutes
   - SSL certificate provisioning: 5-15 minutes

---

## Step 2: Verify Namecheap Nameservers

Since your domain is already **Active** in Cloudflare, your nameservers are likely already configured correctly. But let's verify:

### Check Current Nameservers in Cloudflare:

1. Go to: https://dash.cloudflare.com/
2. Click on `signkit.work` domain
3. Scroll down to see your assigned nameservers (usually something like):
   ```
   anya.ns.cloudflare.com
   brad.ns.cloudflare.com
   ```

### Verify in Namecheap:

1. **Login to Namecheap**
   - Go to: https://www.namecheap.com/
   - Login to your account

2. **Go to Domain List**
   - Click **Domain List** in left sidebar
   - Find `signkit.work`
   - Click **Manage**

3. **Check Nameservers**
   - Scroll to **Nameservers** section
   - Should be set to **Custom DNS**
   - Should show Cloudflare nameservers (e.g., `anya.ns.cloudflare.com`, `brad.ns.cloudflare.com`)

4. **If NOT Set to Cloudflare:**
   - Select **Custom DNS**
   - Enter the nameservers from Cloudflare dashboard
   - Click **Save**
   - Wait 24-48 hours for propagation (usually faster)

---

## Step 3: Verify DNS Records in Cloudflare

After connecting the custom domain to Pages, verify the DNS records:

1. **Go to Cloudflare Dashboard**
   - Click on `signkit.work` domain
   - Click **DNS** → **Records**

2. **You Should See:**
   ```
   Type    Name              Content
   CNAME   signkit.work      signkit-landing.pages.dev
   CNAME   www               signkit-landing.pages.dev (optional)
   ```

3. **If Records Don't Exist:**
   - Cloudflare Pages should create them automatically
   - If not, add manually:
     - Type: `CNAME`
     - Name: `@` (for root domain)
     - Target: `signkit-landing.pages.dev`
     - Proxy status: Proxied (orange cloud)

---

## Step 4: Test Your Domain

### Wait for Propagation
- DNS changes can take 5 minutes to 48 hours
- Usually propagates within 15-30 minutes

### Test URLs:

Once active, test these URLs:

```
https://signkit.work/
https://signkit.work/root
https://signkit.work/buy
https://signkit.work/purchase
https://signkit.work/gum
https://signkit.work/test-variants.html
```

### Check SSL Certificate:
- Look for green padlock in browser
- Certificate should be issued by Cloudflare
- Valid for `signkit.work` and `*.signkit.work`

---

## Troubleshooting

### Issue: Domain not resolving

**Check:**
1. Nameservers in Namecheap match Cloudflare
2. DNS records exist in Cloudflare
3. Wait 15-30 minutes for propagation

**Solution:**
```bash
# Check DNS propagation
dig signkit.work
nslookup signkit.work

# Check from different locations
https://www.whatsmydns.net/#CNAME/signkit.work
```

### Issue: SSL Certificate Error

**Check:**
1. SSL/TLS mode in Cloudflare
2. Certificate provisioning status

**Solution:**
1. Go to Cloudflare → SSL/TLS
2. Set mode to **Full (strict)**
3. Wait 5-15 minutes for certificate

### Issue: "Too many redirects"

**Check:**
1. SSL/TLS mode
2. Page Rules

**Solution:**
1. Set SSL/TLS to **Full (strict)**
2. Clear browser cache
3. Try incognito mode

---

## Current Cloudflare Pages URLs

While waiting for custom domain:

- **Main:** https://d5834d2a.signkit-landing.pages.dev
- **Control:** https://d5834d2a.signkit-landing.pages.dev/root
- **Buy:** https://d5834d2a.signkit-landing.pages.dev/buy
- **Purchase:** https://d5834d2a.signkit-landing.pages.dev/purchase
- **Gum:** https://d5834d2a.signkit-landing.pages.dev/gum

---

## What You DON'T Need to Change in Namecheap

Since your domain is already Active in Cloudflare, you likely don't need to change anything in Namecheap. The nameservers are already pointing to Cloudflare.

**DO NOT change:**
- ❌ A Records (Cloudflare manages this)
- ❌ CNAME Records (Cloudflare manages this)
- ❌ MX Records (unless you have email)
- ❌ TXT Records (unless you have specific needs)

**ONLY change if needed:**
- ✅ Nameservers (should already be set to Cloudflare)

---

## Summary Checklist

- [x] Domain added to Cloudflare ✅
- [x] Domain is Active in Cloudflare ✅
- [x] Cloudflare Pages deployed ✅
- [ ] Custom domain connected to Pages project
- [ ] DNS records verified
- [ ] SSL certificate active
- [ ] Domain resolving correctly
- [ ] All variants tested

---

## Quick Commands

### Check DNS Propagation
```bash
# Check if domain resolves
dig signkit.work

# Check CNAME record
dig signkit.work CNAME

# Check from multiple locations
curl -I https://signkit.work
```

### Check SSL Certificate
```bash
# Check SSL certificate
openssl s_client -connect signkit.work:443 -servername signkit.work

# Or use online tool
https://www.ssllabs.com/ssltest/analyze.html?d=signkit.work
```

---

## Next Steps After Domain is Active

1. ✅ Test all landing page variants
2. ✅ Verify GA4 tracking works
3. ✅ Test A/B routing logic
4. ✅ Enable A/B testing (set `AUTO_SPLIT = true`)
5. ✅ Monitor analytics
6. ✅ Optimize based on data

---

**Last Updated:** November 18, 2025  
**Status:** Domain Active in Cloudflare, needs connection to Pages  
**Deployment:** https://d5834d2a.signkit-landing.pages.dev  
**Target Domain:** signkit.work
