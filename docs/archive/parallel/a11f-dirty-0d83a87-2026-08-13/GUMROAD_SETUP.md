# Gumroad Product Setup Guide

This guide walks you through setting up the Signature Extractor product on Gumroad for automated license key delivery and payment processing.

## Prerequisites

- Gumroad account (premium account recommended for advanced features)
- Signature Extractor application ready for distribution
- Test license key configured in the application (`pranay@example.com`)

## Step 1: Create Product

### 1.1 Basic Product Information

1. **Login to Gumroad** and go to your Products dashboard
2. **Click "Add a product"**
3. **Product Details:**
   - **Title**: "Signature Extractor - Professional Signature Extraction Tool"
   - **Description**:
     ```
     Extract signatures from documents with precision control.

     ✨ Features:
     • Precision selection with zoom/pan controls
     • Color customization & threshold adjustment
     • EXIF auto-rotation for mobile photos
     • Export as transparent PNG with metadata
     • PDF signing with audit logging
     • Privacy-focused: all processing happens locally

     🖥️ Desktop application for macOS, Windows, and Linux
     🔄 Free trial available - test before you buy
     📧 Instant license key delivery
     ```

4. **Upload Preview Images:**
   - App screenshots (minimum 1200x800px)
   - Logo (400x400px)
   - Feature showcase images

### 1.2 Pricing Configuration

**Main Product:**
- **Price**: $29.00 (or your chosen price)
- **Suggested Price**: $29.00
- **Name a fair price**: Enabled (allows customers to pay more)
- **Support**: Enabled
- **Add-ons**: Disabled (simple pricing)

**Free Trial Option:**
- Create a separate "Free Trial" product priced at $0
- Link to main product for upgrade
- Limited functionality (export/PDF restrictions enforced by app)

### 1.3 File Uploads

**Main Distribution Files:**
1. **macOS**: `SignatureExtractor-macOS.zip` (or .dmg)
2. **Windows**: `SignatureExtractor-Windows.zip` (or .exe)
3. **Linux**: `SignatureExtractor-Linux.tar.gz`

**Include with Purchase:**
- Application installer/executable
- Quick Start Guide PDF
- License activation instructions

## Step 2: License Key Automation

### 2.1 Configure License Key Delivery

1. **Go to Product Settings** → "Chargebacks & Refunds"
2. **Enable "Automatically deliver license keys"**
3. **License Key Format**: Use Gumroad's generated keys or custom format
4. **Key Storage**: Save to a database for validation (optional but recommended)

### 2.2 Custom License Key Generation (Advanced)

For more control, use Gumroad's webhook API:

**Webhook Endpoint**: `https://your-api.com/gumroad/webhook`

**Webhook Handling Code**:
```python
import hashlib
import hmac
from flask import Flask, request, jsonify

app = Flask(__name__)

# Your Gumroad webhook secret
WEBHOOK_SECRET = "your_gumroad_webhook_secret"

@app.route('/gumroad/webhook', methods=['POST'])
def gumroad_webhook():
    # Verify webhook signature
    signature = request.headers.get('X-Gumroad-Signature')
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        request.data,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return "Invalid signature", 401

    data = request.json
    event = data.get('event')

    if event == 'sale':
        # Generate custom license key
        license_key = generate_license_key(data)
        # Store in your database
        store_license(data['email'], license_key)

    return "OK", 200

def generate_license_key(sale_data):
    """Generate a custom license key based on sale data."""
    import uuid
    import secrets

    # Generate secure random key
    key = f"SIGEXT-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
    return key
```

### 2.3 Email Template Configuration

**Purchase Confirmation Email**:
```html
Subject: Your Signature Extractor License Key

Thanks for purchasing Signature Extractor!

🎯 Your License Key: {{license_key}}

📥 Download Links:
- macOS: {{mac_download_url}}
- Windows: {{windows_download_url}}
- Linux: {{linux_download_url}}

🚀 Getting Started:
1. Download the application for your platform
2. Install and launch Signature Extractor
3. Go to License → Enter License Key
4. Enter your license key above

💡 Need help? Reply to this email or visit our support site.

Enjoy extracting signatures with precision!
```

## Step 3: Product URL Configuration

Update the application to use your actual Gumroad product URL:

**File**: `desktop_app/views/license_restriction_dialog.py`

```python
# Update this line with your actual Gumroad product URL
PURCHASE_URL = "https://gumroad.com/l/your-actual-product-id"
```

**Environment Configuration**:
```env
# .env.example
GUMROAD_PRODUCT_URL=https://gumroad.com/l/your-product-id
```

## Step 4: Testing Setup

### 4.1 Test Purchase Flow

1. **Create test product** with $0 price for testing
2. **Make test purchase** using your own account
3. **Verify license key delivery**
4. **Test license activation** in the application

### 4.2 Test License Validation

**Manual License Test**:
```bash
# Test with a purchased license key
python -c "
import sys; sys.path.insert(0, 'desktop_app')
from license import save_license, is_licensed

# Replace with actual test license key
test_license = 'SIGEXT-ABCD1234-EFGH5678'
save_license(test_license, email='test@example.com')
print(f'License valid: {is_licensed()}')
"
```

### 4.3 Test Webhook (if using custom license generation)

```bash
# Test webhook endpoint with simulated Gumroad data
curl -X POST https://your-api.com/gumroad/webhook \
  -H "Content-Type: application/json" \
  -H "X-Gumroad-Signature: test_signature" \
  -d '{
    "event": "sale",
    "email": "test@example.com",
    "product_id": "your-product-id"
  }'
```

## Step 5: Launch Configuration

### 5.1 Product Settings

**Final Configuration**:
- **Status**: Published
- **Visibility**: Public
- **Affiliates**: Enabled (optional, 30% commission)
- **Coupons**: Create launch discount coupons
- **Sales Tax**: Configure for your jurisdiction

### 5.2 Launch Checklist

- [ ] Product images uploaded and optimized
- [ ] Description finalized with SEO keywords
- [ ] Pricing confirmed
- [ ] License key automation tested
- [ ] Email templates configured
- [ ] Support email ready
- [ ] Refund policy set (30 days recommended)
- [ ] Tax configuration complete

## Step 6: Post-Launch Management

### 6.1 Monitoring

**Key Metrics to Track**:
- Daily sales volume
- Conversion rate (free trial → paid)
- License activation success rate
- Customer support requests
- Refund rate

**Gumroad Analytics**:
- Monitor your Gumroad dashboard daily
- Set up email notifications for new sales
- Track affiliate performance if enabled

### 6.2 Customer Support

**Support Workflow**:
1. **License Issues**: Verify purchase email and resend key
2. **Technical Issues**: Refer to troubleshooting documentation
3. **Refund Requests**: Process through Gumroad interface
4. **Feature Requests**: Log for future development

**Support Email Template**:
```
Subject: Re: Signature Extractor Support Request

Hi [Customer Name],

Thanks for reaching out about Signature Extractor!

[Provide personalized solution based on their issue]

For quick solutions, check our FAQ: [link]
For technical issues, try our troubleshooting guide: [link]

Best regards,
Signature Extractor Support
```

### 6.3 Updates and Patches

**Version Management**:
1. **Update version number** in `desktop_app/config.py`
2. **Test compatibility** with existing licenses
3. **Upload updated files** to Gumroad
4. **Notify customers** of major updates

**Update Notification**:
```python
# Add to desktop_app/config.py
APP_VERSION = "1.0.1"
UPDATES_URL = "https://api.signatureextractor.app/updates.json"

# Check for updates on startup
def check_for_updates():
    # Implement update checking logic
    pass
```

## Troubleshooting

### Common Issues

**License Key Not Working**:
1. Verify customer's purchase in Gumroad dashboard
2. Check for typos in license key entry
3. Ensure application version matches requirements

**Download Issues**:
1. Verify file integrity with checksums
2. Check platform compatibility
3. Provide alternative download links if needed

**Webhook Failures**:
1. Check webhook URL accessibility
2. Verify webhook secret matches Gumroad settings
3. Monitor webhook logs for errors

### Support Resources

- **Gumroad Documentation**: https://gumroad.com/help
- **Application Docs**: Link to your documentation
- **Community Forum**: Set up for user discussions
- **Email Support**: support@yourdomain.com

## Security Considerations

- **Webhook Security**: Always verify webhook signatures
- **License Key Storage**: Use secure, encrypted storage
- **API Rate Limiting**: Protect against abuse
- **Data Privacy**: Comply with GDPR/CCPA requirements

This setup guide ensures you have a complete, professional payment and licensing system integrated with your Signature Extractor application.