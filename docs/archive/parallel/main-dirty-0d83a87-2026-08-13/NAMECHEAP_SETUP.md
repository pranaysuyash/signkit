# Namecheap Configuration for SignKit Landing Page

> What you need to do (or verify) in Namecheap for signkit.work

**Domain:** signkit.work  
**Registrar:** Namecheap  
**DNS Provider:** Cloudflare  
**Last Updated:** November 18, 2025

---

## ✅ What's Already Done

Based on your Cloudflare showing the domain as "Active", your nameservers are likely already configured correctly. But let's verify.

---

## 🎯 What To Do at Namecheap

### Step 1: Login to Namecheap

1. Go to https://www.namecheap.com/
2. Click **Sign In**
3. Enter your credentials

---

### Step 2: Navigate to Domain Management

1. Click **Domain List** in the left sidebar
2. Find `signkit.work` in your list
3. Click **Manage** button next to it

---

### Step 3: Check Nameservers

Scroll down to the **Nameservers** section.

#### ✅ If You See This (CORRECT):

```
Nameserver Type: Custom DNS

Nameserver 1: anya.ns.cloudflare.com
Nameserver 2: brad.ns.cloudflare.com
```

**Or similar Cloudflare nameservers like:**
- `ns1.cloudflare.com` / `ns2.cloudflare.com`
- `chad.ns.cloudflare.com` / `dana.ns.cloudflare.com`
- Any `*.ns.cloudflare.com` combination

**✅ YOU'RE DONE! No changes needed at Namecheap.**

---

#### ❌ If You See This (INCORRECT):

```
Nameserver Type: Namecheap BasicDNS
or
Nameserver Type: Custom DNS
Nameserver 1: dns1.registrar-servers.com
Nameserver 2: dns2.registrar-servers.com
```

**❌ YOU NEED TO CHANGE THIS**

---

### Step 4: Change Nameservers (If Needed)

**Only do this if your nameservers are NOT pointing to Cloudflare:**

1. In the **Nameservers** section, select **Custom DNS**

2. Get your Cloudflare nameservers:
   - Go to https://dash.cloudflare.com/
   - Click on `signkit.work` domain
   - Scroll down to see your assigned nameservers
   - They'll look like: `anya.ns.cloudflare.com` and `brad.ns.cloudflare.com`

3. Enter them in Namecheap:
   ```
   Nameserver 1: [your-cloudflare-ns1].ns.cloudflare.com
   Nameserver 2: [your-cloudflare-ns2].ns.cloudflare.com
   ```

4. Click the green **✓** checkmark to save

5. **Wait 24-48 hours** for propagation (usually faster, 1-4 hours)

---

## 🚫 What NOT To Change at Namecheap

### ❌ DO NOT Touch These Settings:

1. **Domain Privacy** - Keep as is (recommended: enabled)
2. **Auto-Renew** - Keep enabled to avoid losing domain
3. **Domain Lock** - Keep enabled for security
4. **Contact Information** - Only update if needed
5. **DNS Records** - Don't add any! Cloudflare manages all DNS

### ⚠️ Important: DNS Management

Once nameservers point to Cloudflare:
- **ALL DNS records are managed in Cloudflare**
- Any DNS changes in Namecheap will be IGNORED
- Only change nameservers back if you want to stop using Cloudflare

---

## 🔍 How to Verify It's Working

### Check 1: Nameserver Propagation

```bash
# On Mac/Linux terminal
dig NS signkit.work

# Or use online tool
https://www.whatsmydns.net/#NS/signkit.work
```

**Expected Result:**
```
signkit.work.  IN  NS  anya.ns.cloudflare.com.
signkit.work.  IN  NS  brad.ns.cloudflare.com.
```

### Check 2: Domain Resolution

```bash
# Check if domain resolves
dig signkit.work

# Or visit in browser
https://signkit.work
```

**Expected Result:**
- Domain should resolve to Cloudflare IP
- Landing page should load

### Check 3: Cloudflare Dashboard

1. Go to https://dash.cloudflare.com/
2. Click on `signkit.work`
3. Look for **Status: Active** (green checkmark)

**If Active:** ✅ Everything is configured correctly!

---

## 📋 Checklist

Use this to verify your Namecheap setup:

- [ ] Logged into Namecheap
- [ ] Found `signkit.work` in Domain List
- [ ] Clicked **Manage**
- [ ] Checked **Nameservers** section
- [ ] Verified nameservers point to Cloudflare (`*.ns.cloudflare.com`)
- [ ] If not, changed to Cloudflare nameservers
- [ ] Saved changes (green checkmark)
- [ ] Waited for propagation (1-48 hours)
- [ ] Verified domain is Active in Cloudflare
- [ ] Tested https://signkit.work loads

---

## ⏱️ Timeline

### If Nameservers Already Correct
- **Time needed:** 0 minutes
- **Action:** None! You're done.

### If Changing Nameservers
- **Change time:** 2 minutes
- **Propagation:** 1-48 hours (usually 1-4 hours)
- **Full activation:** Up to 48 hours

---

## 🐛 Troubleshooting

### Issue: Can't find signkit.work in Namecheap

**Possible causes:**
- Domain registered under different account
- Domain transferred to different registrar

**Solution:**
- Check email for domain registration confirmation
- Search all Namecheap accounts you have
- Check if domain was transferred

### Issue: Nameservers won't save

**Possible causes:**
- Domain is locked
- Invalid nameserver format
- Browser cache issue

**Solution:**
- Unlock domain first (in Domain Settings)
- Verify nameserver format: `name.ns.cloudflare.com`
- Try different browser or clear cache

### Issue: Changes not taking effect

**Possible causes:**
- DNS propagation delay
- Browser cache
- ISP DNS cache

**Solution:**
- Wait 24-48 hours
- Clear browser cache
- Try incognito mode
- Use different network (mobile data)
- Check propagation: https://www.whatsmydns.net/

---

## 📞 Support

### Namecheap Support
- **Live Chat:** Available 24/7 on Namecheap.com
- **Email:** support@namecheap.com
- **Phone:** Check Namecheap website for number
- **Help Center:** https://www.namecheap.com/support/

### Cloudflare Support
- **Community:** https://community.cloudflare.com/
- **Docs:** https://developers.cloudflare.com/
- **Dashboard:** https://dash.cloudflare.com/

---

## 🎯 Summary

### Most Likely Scenario (90% chance):
**Your nameservers are already pointing to Cloudflare.**

Since Cloudflare shows your domain as "Active", this means:
- ✅ Nameservers are correct
- ✅ No changes needed at Namecheap
- ✅ Just wait for DNS propagation (if domain was just added)

### What You Should Do:
1. **Login to Namecheap** (2 minutes)
2. **Check nameservers** (1 minute)
3. **If they're Cloudflare nameservers:** ✅ Done! Close Namecheap.
4. **If they're NOT:** Change them to Cloudflare nameservers

### After Verification:
- **No further action needed at Namecheap**
- **All DNS managed in Cloudflare**
- **Domain will work once DNS propagates**

---

## 🚀 Next Steps After Namecheap

Once nameservers are verified:

1. ✅ Wait for DNS propagation (1-48 hours)
2. ✅ Test https://signkit.work
3. ✅ Test all landing page variants
4. ✅ Verify GA4 tracking
5. ✅ Enable A/B testing when ready

---

**Domain:** signkit.work  
**Registrar:** Namecheap  
**DNS:** Cloudflare  
**Status:** Active  
**Action Required:** Verify nameservers (likely already correct)
