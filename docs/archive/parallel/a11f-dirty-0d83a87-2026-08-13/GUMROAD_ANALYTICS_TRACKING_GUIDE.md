# Gumroad Analytics Tracking Guide

**Date:** November 16, 2025  
**Purpose:** Guide for tracking Gumroad product page analytics with Google Analytics  
**Product:** SignKit (https://pranaysuyash.gumroad.com/l/signkit-v1)

---

## 🎯 The Challenge

Since your landing page is hosted on Gumroad, you **cannot directly add Google Analytics tracking code** to the Gumroad product page. Gumroad doesn't allow custom JavaScript injection for security reasons.

However, there are several effective workarounds to track your product's performance.

---

## ✅ What You CAN Track

### 1. **Gumroad's Built-in Analytics** (Primary Source)

Gumroad provides comprehensive analytics in your dashboard:

**Available Metrics:**
- Page views
- Conversion rate (views → purchases)
- Revenue
- Number of sales
- Traffic sources (referrers)
- Geographic data
- Device types

**How to Access:**
1. Log into Gumroad
2. Go to your product page
3. Click "Analytics" tab
4. View detailed metrics

**Pros:**
- ✅ Most accurate for product page performance
- ✅ Includes conversion data
- ✅ No setup required
- ✅ Tracks actual purchases

**Cons:**
- ❌ Not integrated with your other analytics
- ❌ Limited customization
- ❌ Can't track custom events

---

### 2. **UTM Parameters for Traffic Source Tracking** (Recommended)

Use UTM parameters to track where your Gumroad traffic comes from in Google Analytics.

**How It Works:**
1. Create UTM-tagged links to your Gumroad page
2. Track clicks on these links in Google Analytics
3. Gumroad will show you which UTM sources converted

**Example UTM Links:**

```
# Product Hunt Launch
https://pranaysuyash.gumroad.com/l/signkit-v1?utm_source=producthunt&utm_medium=launch&utm_campaign=nov2025

# Reddit Post
https://pranaysuyash.gumroad.com/l/signkit-v1?utm_source=reddit&utm_medium=social&utm_campaign=r_productivity

# Email Newsletter
https://pranaysuyash.gumroad.com/l/signkit-v1?utm_source=newsletter&utm_medium=email&utm_campaign=launch_week

# Twitter/X
https://pranaysuyash.gumroad.com/l/signkit-v1?utm_source=twitter&utm_medium=social&utm_campaign=launch

# SEO Blog Post
https://pranaysuyash.gumroad.com/l/signkit-v1?utm_source=blog&utm_medium=organic&utm_campaign=signature_extraction_guide
```

**Setup:**

1. **Create UTM Links:**
   - Use Google's Campaign URL Builder: https://ga-dev-tools.google/campaign-url-builder/
   - Or create manually following the pattern above

2. **Track in Google Analytics:**
   - Set up GA4 on signkit.work (your domain)
   - Add UTM-tagged links on your website
   - Track outbound clicks to Gumroad

3. **View Results:**
   - In GA4: Reports → Acquisition → Traffic acquisition
   - Filter by campaign/source/medium
   - See which sources drive the most clicks to Gumroad

**Pros:**
- ✅ Track traffic sources accurately
- ✅ See which marketing channels work
- ✅ Gumroad shows UTM data in referrers
- ✅ Easy to implement

**Cons:**
- ❌ Only tracks clicks, not actual page views on Gumroad
- ❌ Doesn't track behavior on Gumroad page

---

### 3. **Custom Domain with Redirect** (Advanced Option)

Set up a custom domain that redirects to Gumroad while tracking the visit.

**How It Works:**
1. Set up signkit.work/buy (or /download)
2. Add GA tracking code to this page
3. Immediately redirect to Gumroad product page
4. Track the visit before redirect

**Implementation:**

```html
<!-- On signkit.work/buy -->
<!DOCTYPE html>
<html>
<head>
    <title>Redirecting to SignKit Purchase...</title>
    
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-XXXXXXXXXX');
        
        // Track the purchase intent
        gtag('event', 'purchase_intent', {
            'event_category': 'conversion',
            'event_label': 'gumroad_redirect'
        });
        
        // Redirect after tracking
        setTimeout(function() {
            window.location.href = 'https://pranaysuyash.gumroad.com/l/signkit-v1';
        }, 100);
    </script>
    
    <!-- Fallback for users with JS disabled -->
    <meta http-equiv="refresh" content="0;url=https://pranaysuyash.gumroad.com/l/signkit-v1">
</head>
<body>
    <p>Redirecting to purchase page...</p>
    <p>If you are not redirected, <a href="https://pranaysuyash.gumroad.com/l/signkit-v1">click here</a>.</p>
</body>
</html>
```

**Pros:**
- ✅ Track every visit to your "buy" page
- ✅ Full control over tracking
- ✅ Can add custom events
- ✅ Professional branded URL

**Cons:**
- ❌ Requires hosting a redirect page
- ❌ Adds slight delay (100ms)
- ❌ Still can't track behavior on Gumroad

---

### 4. **Track Conversions via Gumroad Webhooks** (Most Powerful)

Use Gumroad's webhooks to send purchase data to your analytics.

**How It Works:**
1. Set up a webhook endpoint on your server
2. Gumroad sends purchase data to your endpoint
3. Your server forwards data to Google Analytics
4. Track actual conversions, not just clicks

**Setup:**

1. **Create Webhook Endpoint:**

```python
# Example Flask endpoint
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/gumroad-webhook', methods=['POST'])
def gumroad_webhook():
    data = request.json
    
    # Extract purchase data
    product_id = data.get('product_id')
    sale_id = data.get('sale_id')
    email = data.get('email')
    price = data.get('price')
    
    # Send to Google Analytics via Measurement Protocol
    ga_payload = {
        'v': '1',
        'tid': 'G-XXXXXXXXXX',  # Your GA4 Measurement ID
        'cid': sale_id,
        't': 'event',
        'ec': 'ecommerce',
        'ea': 'purchase',
        'el': product_id,
        'ev': price
    }
    
    requests.post('https://www.google-analytics.com/collect', data=ga_payload)
    
    return 'OK', 200
```

2. **Configure in Gumroad:**
   - Go to Settings → Advanced → Webhooks
   - Add your webhook URL: `https://yourdomain.com/gumroad-webhook`
   - Select events: "sale"

**Pros:**
- ✅ Track actual purchases in GA
- ✅ Real conversion data
- ✅ Can enrich with additional data
- ✅ Most accurate attribution

**Cons:**
- ❌ Requires server setup
- ❌ More complex implementation
- ❌ Need to maintain webhook endpoint

---

## 📊 Recommended Tracking Strategy

### Phase 1: Launch (Immediate)

**Use UTM Parameters:**
1. Create UTM links for all marketing channels
2. Track clicks to Gumroad in GA4
3. Monitor Gumroad's built-in analytics for conversions

**Setup Time:** 30 minutes  
**Complexity:** Low  
**Data Quality:** Good

### Phase 2: Post-Launch (Week 1)

**Add Custom Domain Redirect:**
1. Set up signkit.work/buy redirect page
2. Add GA tracking before redirect
3. Use this URL in all marketing

**Setup Time:** 2 hours  
**Complexity:** Medium  
**Data Quality:** Better

### Phase 3: Optimization (Month 1)

**Implement Webhook Tracking:**
1. Set up webhook endpoint
2. Send conversion data to GA
3. Build complete funnel view

**Setup Time:** 4-6 hours  
**Complexity:** High  
**Data Quality:** Best

---

## 🎯 Complete Tracking Setup

### What to Track

**1. Traffic Sources (UTM Parameters):**
- Product Hunt clicks
- Reddit clicks
- Twitter/X clicks
- Email clicks
- SEO/Blog clicks
- Paid ad clicks

**2. Purchase Intent (Redirect Page):**
- Visits to signkit.work/buy
- Click-through rate to Gumroad
- Time on redirect page

**3. Conversions (Webhooks):**
- Actual purchases
- Revenue
- Customer email (hashed)
- License activations

**4. In-App Events (Desktop App):**
- License activation success
- First extraction
- PDF signing usage
- Export operations

### Complete Funnel View

```
Marketing Channel (UTM)
    ↓
signkit.work/buy (GA4 tracking)
    ↓
Gumroad Product Page (Gumroad analytics)
    ↓
Purchase (Webhook → GA4)
    ↓
License Activation (App → GA4)
    ↓
Product Usage (App → GA4)
```

---

## 📋 Implementation Checklist

### Immediate (Pre-Launch)
- [ ] Create UTM links for all marketing channels
- [ ] Set up Google Analytics 4 on signkit.work
- [ ] Test UTM tracking with sample clicks
- [ ] Document UTM naming convention

### Week 1 (Post-Launch)
- [ ] Set up signkit.work/buy redirect page
- [ ] Add GA tracking to redirect page
- [ ] Update all marketing materials with new URL
- [ ] Test redirect and tracking

### Month 1 (Optimization)
- [ ] Set up webhook endpoint
- [ ] Configure Gumroad webhook
- [ ] Test webhook with test purchase
- [ ] Build GA4 dashboard with all data

---

## 🔗 Useful Resources

**UTM Builder:**
- https://ga-dev-tools.google/campaign-url-builder/

**Gumroad Analytics:**
- https://help.gumroad.com/article/147-analytics

**Gumroad Webhooks:**
- https://help.gumroad.com/article/268-webhooks

**Google Analytics 4:**
- https://support.google.com/analytics/answer/10089681

**GA4 Measurement Protocol:**
- https://developers.google.com/analytics/devguides/collection/protocol/ga4

---

## 💡 Pro Tips

1. **Use Consistent UTM Naming:**
   - Always lowercase
   - Use underscores, not spaces
   - Document your convention

2. **Track Outbound Clicks:**
   - Add event tracking to all Gumroad links
   - Measure click-through rate

3. **Compare Data Sources:**
   - GA4 clicks vs Gumroad views
   - Identify discrepancies
   - Adjust tracking as needed

4. **Test Everything:**
   - Test UTM links before launch
   - Verify tracking in GA4 real-time
   - Do test purchases to verify webhooks

5. **Privacy Compliance:**
   - Don't send PII to GA without consent
   - Hash email addresses
   - Follow GDPR/privacy laws

---

## 🎯 Expected Results

**With UTM Tracking:**
- Know which marketing channels drive traffic
- Calculate cost per click by channel
- Optimize marketing spend

**With Redirect Page:**
- Track 100% of purchase intent
- Measure conversion rate accurately
- Build complete funnel

**With Webhooks:**
- Track actual revenue in GA
- Attribute sales to marketing channels
- Calculate true ROI

---

## ❓ FAQ

**Q: Can I add Google Analytics directly to Gumroad?**  
A: No, Gumroad doesn't allow custom JavaScript for security reasons.

**Q: Will UTM parameters affect my Gumroad page?**  
A: No, Gumroad ignores UTM parameters but shows them in referrer data.

**Q: Do I need all three tracking methods?**  
A: No, start with UTM parameters and add others as needed.

**Q: How accurate is UTM tracking?**  
A: Very accurate for traffic sources, but doesn't track actual page views on Gumroad.

**Q: Can I track individual user behavior on Gumroad?**  
A: No, only Gumroad can track behavior on their pages.

---

**Last Updated:** November 16, 2025  
**Status:** Ready for implementation  
**Priority:** High (Week 1 post-launch)
