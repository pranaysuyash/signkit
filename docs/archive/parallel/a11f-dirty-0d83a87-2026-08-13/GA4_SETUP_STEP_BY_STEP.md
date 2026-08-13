# Google Analytics 4 Setup Guide for SignKit

**Date:** November 16, 2025  
**Status:** Step-by-step setup instructions  
**Time Required:** 15-20 minutes

---

## ✅ What You've Done So Far

- ✅ Created a Google Analytics 4 property
- ✅ Selected "Web" as the platform

Great! Now let's complete the setup.

---

## 📋 Step-by-Step Setup

### Step 1: Get Your Measurement ID

You should see a screen showing your **Measurement ID** (looks like `G-XXXXXXXXXX`).

**If you see it:**
1. Copy the Measurement ID (it starts with `G-`)
2. Save it somewhere - you'll need it in Step 3

**If you don't see it:**
1. Click on "Admin" (gear icon in bottom left)
2. Under "Property" column, click "Data Streams"
3. Click on your web stream
4. You'll see the Measurement ID at the top right

---

### Step 2: Configure Data Stream Settings

While you're on the Data Stream page:

1. **Stream name:** Change to "SignKit Website" (optional but clearer)

2. **Enhanced measurement:** Make sure these are enabled (they should be by default):
   - ✅ Page views
   - ✅ Scrolls
   - ✅ Outbound clicks (IMPORTANT - this tracks clicks to Gumroad!)
   - ✅ Site search
   - ✅ Form interactions
   - ✅ File downloads

3. Click "Save" if you made changes

---

### Step 3: Create Your Redirect/Tracking Page

Now you need to create a simple HTML page that will track visits and redirect to Gumroad.

**Option A: If you have signkit.work hosted (Recommended)**

Create a file called `buy.html` or `download.html` on your signkit.work domain:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Get SignKit - Redirecting...</title>
    
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        
        // Initialize GA4
        gtag('config', 'G-XXXXXXXXXX', {
            'page_title': 'Purchase Intent',
            'page_location': window.location.href
        });
        
        // Track purchase intent event
        gtag('event', 'begin_checkout', {
            'event_category': 'ecommerce',
            'event_label': 'gumroad_redirect',
            'value': 29
        });
        
        // Get UTM parameters from URL
        const urlParams = new URLSearchParams(window.location.search);
        const utmSource = urlParams.get('utm_source') || '';
        const utmMedium = urlParams.get('utm_medium') || '';
        const utmCampaign = urlParams.get('utm_campaign') || '';
        
        // Build Gumroad URL with UTM parameters
        let gumroadUrl = 'https://pranaysuyash.gumroad.com/l/signkit-v1';
        if (utmSource) {
            gumroadUrl += '?utm_source=' + utmSource;
            if (utmMedium) gumroadUrl += '&utm_medium=' + utmMedium;
            if (utmCampaign) gumroadUrl += '&utm_campaign=' + utmCampaign;
        }
        
        // Redirect after tracking (100ms delay ensures tracking fires)
        setTimeout(function() {
            window.location.href = gumroadUrl;
        }, 100);
    </script>
    
    <!-- Fallback for users with JavaScript disabled -->
    <meta http-equiv="refresh" content="0;url=https://pranaysuyash.gumroad.com/l/signkit-v1">
    
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 2rem;
        }
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 4px solid white;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        a {
            color: white;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="spinner"></div>
        <h1>Redirecting to SignKit...</h1>
        <p>Taking you to the purchase page</p>
        <p style="margin-top: 2rem; font-size: 0.9rem;">
            If you are not redirected automatically, 
            <a href="https://pranaysuyash.gumroad.com/l/signkit-v1">click here</a>.
        </p>
    </div>
</body>
</html>
```

**IMPORTANT:** Replace `G-XXXXXXXXXX` (appears twice) with your actual Measurement ID!

**Option B: If you don't have signkit.work hosted yet**

You can use a free service like:
- **GitHub Pages** (free, easy)
- **Netlify** (free, very easy)
- **Vercel** (free, very easy)

I can help you set up any of these if needed.

---

### Step 4: Upload Your Tracking Page

**If using your own hosting:**
1. Upload `buy.html` to your server
2. Make it accessible at `https://signkit.work/buy` or `https://signkit.work/download`
3. Test by visiting the URL - it should redirect to Gumroad

**If using GitHub Pages (Quick Setup):**

1. Create a new repository called `signkit-landing`
2. Create `index.html` with the code above
3. Go to Settings → Pages
4. Enable GitHub Pages from `main` branch
5. Your page will be at `https://yourusername.github.io/signkit-landing/`
6. (Optional) Set up custom domain `signkit.work` to point here

---

### Step 5: Create UTM-Tagged Links

Now create links for each marketing channel. Use this template:

```
https://signkit.work/buy?utm_source=SOURCE&utm_medium=MEDIUM&utm_campaign=CAMPAIGN
```

**Examples for your launch:**

```bash
# Product Hunt
https://signkit.work/buy?utm_source=producthunt&utm_medium=launch&utm_campaign=nov2025

# Reddit - r/productivity
https://signkit.work/buy?utm_source=reddit&utm_medium=social&utm_campaign=productivity

# Reddit - r/macapps
https://signkit.work/buy?utm_source=reddit&utm_medium=social&utm_campaign=macapps

# Twitter/X
https://signkit.work/buy?utm_source=twitter&utm_medium=social&utm_campaign=launch

# Email Newsletter
https://signkit.work/buy?utm_source=newsletter&utm_medium=email&utm_campaign=launch_week

# Hacker News
https://signkit.work/buy?utm_source=hackernews&utm_medium=social&utm_campaign=show_hn

# Direct Link (no UTM)
https://signkit.work/buy
```

**Save these links!** You'll use them in all your marketing.

---

### Step 6: Test Your Setup

1. **Test the redirect:**
   - Visit `https://signkit.work/buy`
   - Should redirect to Gumroad within 1 second
   - Check that you land on your Gumroad product page

2. **Test GA4 tracking:**
   - Go to GA4 → Reports → Realtime
   - Visit your redirect page in another tab
   - Within 30 seconds, you should see:
     - 1 active user
     - Page view event
     - begin_checkout event

3. **Test UTM tracking:**
   - Visit `https://signkit.work/buy?utm_source=test&utm_medium=test&utm_campaign=test`
   - Check GA4 Realtime → Event name: begin_checkout
   - Click on the event to see UTM parameters

---

### Step 7: Set Up Conversion Tracking (Optional but Recommended)

1. In GA4, go to **Admin** → **Events**
2. Click **Create event**
3. Create a custom event called `purchase_complete`
4. Go to **Admin** → **Conversions**
5. Click **New conversion event**
6. Add `purchase_complete` as a conversion

This will let you track when people actually purchase (you'll need to set up webhooks for this later).

---

### Step 8: Create a Dashboard

1. Go to **Reports** → **Library**
2. Click **Create new report**
3. Add these cards:
   - **Traffic sources** (where people come from)
   - **Events** (what actions they take)
   - **Conversions** (purchases)
   - **Real-time users** (current activity)

Or use the default reports - they're pretty good!

---

## 📊 What You Can Track Now

### Immediate Tracking (No Code Changes)

✅ **Traffic to your redirect page:**
- How many people click your links
- Which marketing channels drive traffic
- Geographic location of visitors
- Device types (desktop, mobile, tablet)

✅ **Purchase intent:**
- How many people intend to buy (visit redirect page)
- Conversion rate from click to Gumroad visit

✅ **UTM attribution:**
- Which campaigns drive the most traffic
- Cost per click by channel (if you track spend)
- ROI by marketing channel

### Future Tracking (Requires Additional Setup)

⏳ **Actual purchases** (need webhooks)
⏳ **In-app events** (need app integration)
⏳ **User behavior on Gumroad** (only Gumroad can track this)

---

## 🎯 Quick Reference

### Your Measurement ID
```
G-XXXXXXXXXX  (replace with your actual ID)
```

### Your Redirect URL
```
https://signkit.work/buy
```

### Your Gumroad URL
```
https://pranaysuyash.gumroad.com/l/signkit-v1
```

### UTM Template
```
https://signkit.work/buy?utm_source=SOURCE&utm_medium=MEDIUM&utm_campaign=CAMPAIGN
```

---

## 🔍 Viewing Your Data

### Real-Time Data (Immediate)
1. Go to GA4
2. Click **Reports** → **Realtime**
3. See current visitors and events

### Historical Data (After 24-48 hours)
1. Go to **Reports** → **Acquisition** → **Traffic acquisition**
2. See all traffic sources
3. Filter by campaign, source, or medium

### Custom Reports
1. Go to **Explore**
2. Create custom reports with any dimensions/metrics
3. Save for future use

---

## ✅ Checklist

- [ ] Got Measurement ID from GA4
- [ ] Created redirect page with tracking code
- [ ] Replaced `G-XXXXXXXXXX` with actual Measurement ID (2 places)
- [ ] Uploaded redirect page to signkit.work/buy
- [ ] Tested redirect (goes to Gumroad)
- [ ] Tested GA4 tracking (shows in Realtime)
- [ ] Created UTM links for all marketing channels
- [ ] Saved UTM links for use in marketing
- [ ] Set up conversion tracking (optional)
- [ ] Created dashboard (optional)

---

## 🆘 Troubleshooting

**Problem: Not seeing data in GA4 Realtime**
- Wait 30-60 seconds after visiting page
- Check that Measurement ID is correct
- Make sure you're not using an ad blocker
- Try in incognito/private browsing mode

**Problem: Redirect not working**
- Check that JavaScript is enabled
- Verify the Gumroad URL is correct
- Check browser console for errors (F12)

**Problem: UTM parameters not showing**
- Make sure you're using the full URL with parameters
- Check that parameters are properly formatted
- Wait 24-48 hours for data to appear in reports

**Problem: Can't upload to signkit.work**
- Use GitHub Pages as temporary solution
- Or use Netlify/Vercel (free and easy)
- I can help you set these up

---

## 📞 Need Help?

If you get stuck on any step, let me know:
- Which step you're on
- What error you're seeing (if any)
- Screenshot of the issue (if helpful)

I'll guide you through it!

---

## 🎯 Next Steps After Setup

1. **Test everything** - Make sure tracking works
2. **Create UTM links** - For all marketing channels
3. **Update marketing materials** - Use new links everywhere
4. **Monitor data** - Check GA4 daily during launch
5. **Set up webhooks** - Track actual purchases (Week 1)

---

**Last Updated:** November 16, 2025  
**Status:** Ready to implement  
**Time Required:** 15-20 minutes
