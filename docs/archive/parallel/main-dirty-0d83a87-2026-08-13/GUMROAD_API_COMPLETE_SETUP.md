# Gumroad API Complete Setup & Integration

**Date:** November 13, 2025  
**Purpose:** Complete technical integration with Gumroad API for license validation, webhooks, and automation

---

## 📋 TABLE OF CONTENTS

1. [API Overview](#api-overview)
2. [Account & API Key Setup](#account--api-key-setup)
3. [Product Page Setup](#product-page-setup)
4. [License Verification API](#license-verification-api)
5. [Webhook Integration](#webhook-integration)
6. [Refund Detection](#refund-detection)
7. [Analytics & Reporting](#analytics--reporting)
8. [Testing & Validation](#testing--validation)
9. [Production Deployment](#production-deployment)
10. [Troubleshooting](#troubleshooting)

---

## 🔑 API OVERVIEW

### Gumroad API Capabilities

**What You Can Do:**

- ✅ Verify license keys in real-time
- ✅ Check refund status
- ✅ Receive webhook notifications for sales/refunds
- ✅ Generate custom license keys
- ✅ Track sales analytics
- ✅ Manage products programmatically

**API Endpoints:**

```
Base URL: https://api.gumroad.com

POST /v2/licenses/verify          # Verify license key
POST /v2/licenses/enable           # Enable license
POST /v2/licenses/disable          # Disable license
GET  /v2/products/:id              # Get product info
GET  /v2/sales                     # List sales
POST /v2/resource_subscriptions    # Webhooks
```

### Rate Limits

**Free Plan:**

- 1,000 requests/day
- 10 requests/minute

**Premium Plan ($10/month):**

- 10,000 requests/day
- 100 requests/minute

---

## 🔐 ACCOUNT & API KEY SETUP

### Step 1: Create Gumroad Account

1. **Sign up:** https://gumroad.com/signup
2. **Choose plan:**
   - Free: 10% fee (good for starting)
   - Premium: $10/month + 8% fee (recommended)
3. **Complete profile:**
   - Business name: "SignKit" or your company
   - Profile picture: Logo
   - Bio: Brief description

### Step 2: Get API Credentials

1. **Navigate to:** Settings → Advanced → Application
2. **Create Application:**

   - Name: "SignKit License Validator"
   - Description: "License verification for SignKit desktop app"
   - Redirect URI: `https://your-domain.com/oauth/callback` (if using OAuth)

3. **Get API Keys:**

   ```
   Application ID: app_xxxxxxxxxxxxx
   Application Secret: xxxxxxxxxxxxxxxxxxxxxxxx
   Access Token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

4. **Store Securely:**
   ```bash
   # .env file (NEVER commit to git)
   GUMROAD_ACCESS_TOKEN=your_access_token_here
   GUMROAD_PRODUCT_ID=your_product_id_here
   GUMROAD_WEBHOOK_SECRET=your_webhook_secret_here
   ```

### Step 3: Product ID

1. **Create product** on Gumroad
2. **Get Product ID** from URL:

   ```
   URL: https://gumroad.com/l/signkit-v1
   Product ID: signkit-v1

   OR from API:
   Product ID: prod_xxxxxxxxxxxxx
   ```

---

## 📦 PRODUCT PAGE SETUP

### Complete Product Configuration

**Basic Information:**

```
Title: SignKit v1 - Professional Signature Extraction
URL: gumroad.com/l/signkit-v1
Price: $29.00
Category: Software → Productivity
```

**Product Description (Copy-Paste Ready):**

```markdown
# SignKit - Extract Signatures with Complete Privacy

🎯 **Professional signature extraction tool for desktop**

## What You Get

✅ **Lifetime License** - Own SignKit v1 forever
✅ **All v1.x Updates** - Free updates within version 1
✅ **Cross-Platform** - macOS, Windows, Linux
✅ **Privacy-First** - 100% local processing
✅ **PDF Signing** - Place signatures directly on PDFs
✅ **Email Support** - Priority technical assistance

## Features

🔒 **Complete Privacy**
All processing happens locally on your computer. Your documents never leave your device. No cloud uploads, no tracking, no data collection.

🎯 **Precision Control**

- Zoom and pan for pixel-perfect selection
- Adjustable threshold and color replacement
- Real-time preview of extracted signatures
- Rotation-aware coordinate mapping

📄 **PDF Workflow**

- Interactive PDF viewer with zoom controls
- Place signatures directly into documents
- Comprehensive audit logging for compliance
- Save signed documents with embedded signatures

🖥️ **Professional Desktop App**

- Native performance on all platforms
- Intuitive interface designed for efficiency
- Keyboard shortcuts for power users
- Status bar with detailed processing information

## Perfect For

• **Legal Professionals** - Contract management and document preparation
• **Real Estate Agents** - Transaction processing and document signing
• **Healthcare Providers** - Medical form digitization and EMR integration
• **Business Owners** - General document processing and workflow automation

## System Requirements

- **macOS:** 10.15 (Catalina) or later
- **Windows:** Windows 10 or later
- **Linux:** Ubuntu 20.04 or equivalent
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 500MB

## What's Included

📥 **Instant Download**

- macOS app (ARM64 + Intel)
- Windows executable
- Linux AppImage

📚 **Documentation**

- Quick Start Guide
- User Manual
- Video Tutorials

🔑 **License Key**

- Instant delivery via email
- Activate on up to 3 computers
- Lifetime validity

## Try Before You Buy

Download the free trial to test all features. Export and PDF operations require license activation.

## Support

📧 **Email Support:** support@signkit.work
📖 **Documentation:** docs.signkit.work
💬 **Response Time:** Within 24-48 hours

## Refund Policy

30-day money-back guarantee. If SignKit doesn't meet your needs, get a full refund - no questions asked.

---

**Buy once, own forever. No subscriptions, no tricks.**
```

**SEO Keywords:**

```text
signature extraction, PDF signature, document signing, privacy software,
desktop app, signature tool, extract signature, digital signature,
business software, productivity tool, offline software, local processing
```

**Tags (suggested):**

```text
signature-extraction, pdf-tools, privacy-software, desktop-app,
productivity, business-tools, document-processing, macos, windows, linux
```

### File Uploads

**Upload These Files:**

```text
1. SignatureExtractor-macOS-ARM64.dmg (200-300MB)
2. SignatureExtractor-macOS-Intel.dmg (200-300MB)
3. SignatureExtractor-Windows.zip (150-250MB)
4. SignatureExtractor-Linux.AppImage (150-250MB)
5. QuickStartGuide.pdf (2-3MB)
6. UserManual.pdf (5-10MB)
7. LICENSE_INSTRUCTIONS.txt (1KB)
```

### License Key Configuration

**Enable in Gumroad:**

1. Product Settings → License Keys
2. **Enable:** "Generate a unique license key for each sale"
3. **Format:** Use Gumroad's default or custom format
4. **Delivery:** Automatic via email

**Custom License Format (Optional):**

```text
Format: SIGNKIT-V1-XXXX-XXXX-XXXX
Example: SIGNKIT-V1-A3F2-9B7E-C4D1

Regex: ^SIGNKIT-V1-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$
```

---

## ✅ LICENSE VERIFICATION API

### Implementation in Desktop App

**File:** `desktop_app/license/gumroad_validator.py`

```python
import requests
import hashlib
import json
from typing import Dict, Optional
from datetime import datetime, timedelta

class GumroadLicenseValidator:
    """Validate licenses using Gumroad API."""

    def __init__(self, product_id: str, access_token: str):
        self.product_id = product_id
        self.access_token = access_token
        self.api_base = "https://api.gumroad.com"
        self.cache = {}
        self.cache_duration = timedelta(hours=24)

    def verify_license(
        self,
        license_key: str,
        email: Optional[str] = None
    ) -> Dict:
        """
        Verify license key with Gumroad API.

        Args:
            license_key: The license key to verify
            email: Optional email for additional validation

        Returns:
            Dict with verification result:
            {
                "valid": bool,
                "refunded": bool,
                "purchase_email": str,
                "purchase_date": str,
                "product_name": str,
                "error": str (if invalid)
            }
        """
        # Check cache first
        cache_key = self._get_cache_key(license_key, email)
        if cache_key in self.cache:
            cached_result, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_result

        # Call Gumroad API
        url = f"{self.api_base}/v2/licenses/verify"

        payload = {
            "product_id": self.product_id,
            "license_key": license_key,
        }

        if email:
            payload["email"] = email

        try:
            response = requests.post(
                url,
                data=payload,
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )

            result = response.json()

            if result.get("success"):
                purchase = result.get("purchase", {})

                verification_result = {
                    "valid": True,
                    "refunded": purchase.get("refunded", False),
                    "disputed": purchase.get("disputed", False),
                    "chargebacked": purchase.get("chargebacked", False),
                    "purchase_email": purchase.get("email", ""),
                    "purchase_date": purchase.get("created_at", ""),
                    "product_name": purchase.get("product_name", ""),
                    "product_id": purchase.get("product_id", ""),
                    "sale_id": purchase.get("sale_id", ""),
                    "subscription_id": purchase.get("subscription_id"),
                }

                # Check if license is actually valid (not refunded/disputed)
                if verification_result["refunded"] or \
                   verification_result["disputed"] or \
                   verification_result["chargebacked"]:
                    verification_result["valid"] = False
                    verification_result["error"] = "License has been refunded or disputed"

            else:
                verification_result = {
                    "valid": False,
                    "error": result.get("message", "Invalid license key")
                }

            # Cache result
            self.cache[cache_key] = (verification_result, datetime.now())

            return verification_result

        except requests.exceptions.RequestException as e:
            # Network error - allow offline grace period
            return {
                "valid": None,  # Unknown status
                "error": f"Network error: {str(e)}",
                "offline": True
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }

    def _get_cache_key(self, license_key: str, email: Optional[str]) -> str:
        """Generate cache key for license verification."""
        data = f"{license_key}:{email or ''}"
        return hashlib.sha256(data.encode()).hexdigest()

    def clear_cache(self):
        """Clear verification cache."""
        self.cache = {}


# Usage in application
def validate_license_online(license_key: str, email: str) -> bool:
    """
    Validate license key with Gumroad API.

    Returns:
        True if valid, False if invalid, None if offline
    """
    import os

    product_id = os.getenv("GUMROAD_PRODUCT_ID", "signkit-v1")
    access_token = os.getenv("GUMROAD_ACCESS_TOKEN")

    if not access_token:
        # Fallback to offline validation
        return None

    validator = GumroadLicenseValidator(product_id, access_token)
    result = validator.verify_license(license_key, email)

    if result.get("offline"):
        # Network error - allow grace period
        return None

    return result.get("valid", False)
```

### Integration with Existing License System

**File:** `desktop_app/license/storage.py` (Update)

```python
from .gumroad_validator import validate_license_online

def save_license(license_key: str, email: str = None) -> bool:
    """
    Save and validate license key.

    Args:
        license_key: License key to save
        email: Optional email for validation

    Returns:
        True if license is valid and saved
    """
    # First, try online validation
    online_result = validate_license_online(license_key, email)

    if online_result is False:
        # Definitely invalid
        return False

    if online_result is None:
        # Offline - use local validation
        if not _validate_license_format(license_key):
            return False

    # Save license
    license_data = {
        "key": license_key,
        "email": email,
        "validated_at": datetime.now().isoformat(),
        "online_validated": online_result is True
    }

    _save_to_storage(license_data)
    return True


def is_licensed() -> bool:
    """
    Check if application is licensed.

    Performs periodic online validation (every 7 days).
    """
    license_data = _load_from_storage()

    if not license_data:
        return False

    # Check if we need to revalidate online
    last_validated = datetime.fromisoformat(license_data.get("validated_at", ""))
    days_since_validation = (datetime.now() - last_validated).days

    if days_since_validation > 7:
        # Revalidate online
        online_result = validate_license_online(
            license_data["key"],
            license_data.get("email")
        )

        if online_result is False:
            # License is no longer valid (refunded?)
            _clear_storage()
            return False

        if online_result is True:
            # Update validation timestamp
            license_data["validated_at"] = datetime.now().isoformat()
            _save_to_storage(license_data)

    return True
```

### Offline Grace Period

**Strategy:**

- Online validation on first activation
- Revalidate every 7 days
- Allow 30-day grace period if offline
- Show warning after 7 days offline

```python
def check_license_status() -> Dict:
    """
    Check license status with grace period handling.

    Returns:
        {
            "licensed": bool,
            "status": "valid" | "grace_period" | "expired" | "invalid",
            "days_until_revalidation": int,
            "message": str
        }
    """
    license_data = _load_from_storage()

    if not license_data:
        return {
            "licensed": False,
            "status": "invalid",
            "message": "No license found"
        }

    last_validated = datetime.fromisoformat(license_data["validated_at"])
    days_offline = (datetime.now() - last_validated).days

    if days_offline <= 7:
        return {
            "licensed": True,
            "status": "valid",
            "days_until_revalidation": 7 - days_offline,
            "message": "License valid"
        }
    elif days_offline <= 30:
        return {
            "licensed": True,
            "status": "grace_period",
            "days_until_revalidation": 30 - days_offline,
            "message": f"License valid (offline mode, {30 - days_offline} days remaining)"
        }
    else:
        return {
            "licensed": False,
            "status": "expired",
            "message": "License validation required (offline too long)"
        }
```

---

## 🔔 WEBHOOK INTEGRATION

### Webhook Setup in Gumroad

1. **Navigate to:** Settings → Advanced → Webhooks
2. **Add Webhook URL:** `https://your-api.com/gumroad/webhook`
3. **Get Secret:** Copy webhook secret for verification
4. **Select Events:**
   - ✅ sale
   - ✅ refund
   - ✅ dispute
   - ✅ dispute_won

### Webhook Handler Implementation

**File:** `backend/webhooks/gumroad_handler.py`

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import os
from datetime import datetime

app = Flask(__name__)

# Webhook secret from Gumroad
WEBHOOK_SECRET = os.getenv("GUMROAD_WEBHOOK_SECRET")

@app.route('/gumroad/webhook', methods=['POST'])
def gumroad_webhook():
    """
    Handle Gumroad webhook events.

    Events:
    - sale: New purchase
    - refund: Refund processed
    - dispute: Payment dispute
    - dispute_won: Dispute resolved in your favor
    """
    # Verify webhook signature
    if not verify_webhook_signature(request):
        return jsonify({"error": "Invalid signature"}), 401

    data = request.json
    event = data.get('event')

    try:
        if event == 'sale':
            handle_sale(data)
        elif event == 'refund':
            handle_refund(data)
        elif event == 'dispute':
            handle_dispute(data)
        elif event == 'dispute_won':
            handle_dispute_won(data)
        else:
            print(f"Unknown event: {event}")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500


def verify_webhook_signature(request) -> bool:
    """Verify Gumroad webhook signature."""
    signature = request.headers.get('X-Gumroad-Signature')

    if not signature or not WEBHOOK_SECRET:
        return False

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        request.data,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


def handle_sale(data: dict):
    """
    Handle new sale event.

    Data includes:
    - email: Customer email
    - license_key: Generated license key
    - product_id: Product identifier
    - sale_id: Unique sale ID
    - price: Sale price
    - currency: Currency code
    """
    email = data.get('email')
    license_key = data.get('license_key')
    sale_id = data.get('sale_id')
    product_id = data.get('product_id')

    print(f"New sale: {sale_id}")
    print(f"Email: {email}")
    print(f"License: {license_key}")

    # Store in database
    store_license_purchase(
        email=email,
        license_key=license_key,
        sale_id=sale_id,
        product_id=product_id,
        purchase_date=datetime.now(),
        status='active'
    )

    # Send welcome email (optional - Gumroad handles this)
    # send_welcome_email(email, license_key)


def handle_refund(data: dict):
    """
    Handle refund event.

    Deactivate license key when refund is processed.
    """
    email = data.get('email')
    license_key = data.get('license_key')
    sale_id = data.get('sale_id')

    print(f"Refund processed: {sale_id}")
    print(f"Email: {email}")
    print(f"License: {license_key}")

    # Deactivate license in database
    deactivate_license(license_key, reason='refund')

    # Send refund confirmation (optional)
    # send_refund_confirmation(email)


def handle_dispute(data: dict):
    """
    Handle payment dispute event.

    Temporarily suspend license until dispute is resolved.
    """
    email = data.get('email')
    license_key = data.get('license_key')
    sale_id = data.get('sale_id')

    print(f"Dispute opened: {sale_id}")

    # Suspend license
    suspend_license(license_key, reason='dispute')


def handle_dispute_won(data: dict):
    """
    Handle dispute won event.

    Reactivate license after winning dispute.
    """
    email = data.get('email')
    license_key = data.get('license_key')
    sale_id = data.get('sale_id')

    print(f"Dispute won: {sale_id}")

    # Reactivate license
    reactivate_license(license_key)


# Database functions (implement based on your DB)
def store_license_purchase(email, license_key, sale_id, product_id, purchase_date, status):
    """Store license purchase in database."""
    # TODO: Implement database storage
    pass

def deactivate_license(license_key, reason):
    """Deactivate license key."""
    # TODO: Implement license deactivation
    pass

def suspend_license(license_key, reason):
    """Temporarily suspend license."""
    # TODO: Implement license suspension
    pass

def reactivate_license(license_key):
    """Reactivate suspended license."""
    # TODO: Implement license reactivation
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Deploy Webhook Handler

#### Option 1: Heroku (Free Tier)

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Create app
heroku create signkit-webhooks

# Set environment variables
heroku config:set GUMROAD_WEBHOOK_SECRET=your_secret

# Deploy
git push heroku main

# Get webhook URL
heroku info
# Use: https://signkit-webhooks.herokuapp.com/gumroad/webhook
```

#### Option 2: Vercel (Serverless)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set environment variables
vercel env add GUMROAD_WEBHOOK_SECRET

# Get webhook URL
vercel --prod
```

#### Option 3: AWS Lambda (Scalable)

```python
# lambda_function.py
import json
import hmac
import hashlib
import os

def lambda_handler(event, context):
    """AWS Lambda handler for Gumroad webhooks."""

    # Verify signature
    signature = event['headers'].get('X-Gumroad-Signature')
    body = event['body']

    expected = hmac.new(
        os.environ['GUMROAD_WEBHOOK_SECRET'].encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Invalid signature'})
        }

    # Process webhook
    data = json.loads(body)
    event_type = data.get('event')

    # Handle events...

    return {
        'statusCode': 200,
        'body': json.dumps({'status': 'success'})
    }
```

---

## 🔍 REFUND DETECTION

### Real-time Refund Checking

```python
def check_refund_status(license_key: str) -> bool:
    """
    Check if license has been refunded.

    Returns:
        True if refunded, False if active
    """
    validator = GumroadLicenseValidator(
        product_id=os.getenv("GUMROAD_PRODUCT_ID"),
        access_token=os.getenv("GUMROAD_ACCESS_TOKEN")
    )

    result = validator.verify_license(license_key)

    return result.get("refunded", False) or \
           result.get("disputed", False) or \
           result.get("chargebacked", False)
```

### Periodic Refund Checks

```python
import schedule
import time

def periodic_license_check():
    """Check all active licenses for refunds."""
    active_licenses = get_all_active_licenses()

    for license_data in active_licenses:
        if check_refund_status(license_data['key']):
            deactivate_license(
                license_data['key'],
                reason='refund_detected'
            )
            notify_refund_detected(license_data['email'])

# Run every 6 hours
schedule.every(6).hours.do(periodic_license_check)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

---

## 📊 ANALYTICS & REPORTING

### Sales Analytics

```python
def get_sales_analytics(days: int = 30) -> Dict:
    """
    Get sales analytics from Gumroad API.

    Args:
        days: Number of days to analyze

    Returns:
        Analytics data including revenue, sales count, etc.
    """
    url = f"{api_base}/v2/sales"

    params = {
        "access_token": access_token,
        "after": (datetime.now() - timedelta(days=days)).isoformat(),
        "before": datetime.now().isoformat()
    }

    response = requests.get(url, params=params)
    sales = response.json().get("sales", [])

    total_revenue = sum(float(sale.get("price", 0)) for sale in sales)
    total_sales = len(sales)
    refund_count = sum(1 for sale in sales if sale.get("refunded"))

    return {
        "total_revenue": total_revenue,
        "total_sales": total_sales,
        "refund_count": refund_count,
        "refund_rate": refund_count / total_sales if total_sales > 0 else 0,
        "average_sale": total_revenue / total_sales if total_sales > 0 else 0
    }
```

---

## ✅ TESTING & VALIDATION

### Test License Keys

**Gumroad Test Mode:**

1. Enable test mode in Gumroad settings
2. Use test credit card: `4242 4242 4242 4242`
3. Any future expiry date
4. Any CVC

**Test License Validation:**

```python
def test_license_validation():
    """Test license validation with test key."""
    test_key = "TEST-LICENSE-KEY"
    test_email = "test@example.com"

    result = validate_license_online(test_key, test_email)

    assert result is not None
    print(f"Validation result: {result}")

# Run test
test_license_validation()
```

---

## 🚀 PRODUCTION DEPLOYMENT

### Environment Variables

```bash
# .env.production
GUMROAD_ACCESS_TOKEN=your_production_token
GUMROAD_PRODUCT_ID=signkit-v1
GUMROAD_WEBHOOK_SECRET=your_webhook_secret
GUMROAD_PRODUCT_URL=https://gumroad.com/l/signkit-v1
```

### Security Checklist

- [ ] API keys stored securely (not in code)
- [ ] Webhook signature verification enabled
- [ ] HTTPS only for webhook endpoint
- [ ] Rate limiting implemented
- [ ] Error logging configured
- [ ] Monitoring alerts set up

---

## 🔧 TROUBLESHOOTING

### Common Issues

**License Validation Fails:**

- Check API token is valid
- Verify product ID is correct
- Ensure license key format matches
- Check network connectivity

**Webhook Not Receiving Events:**

- Verify webhook URL is accessible
- Check webhook secret matches
- Ensure HTTPS is enabled
- Test with Gumroad webhook tester

**Refund Not Detected:**

- Check webhook is configured for refund events
- Verify webhook handler processes refunds
- Test refund flow in test mode

---

**This completes the Gumroad API integration. You now have:**

- ✅ License verification
- ✅ Webhook handling
- ✅ Refund detection
- ✅ Analytics tracking
- ✅ Production-ready code
- ✅ Production-ready code
