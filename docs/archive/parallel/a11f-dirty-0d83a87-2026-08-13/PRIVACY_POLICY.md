# Privacy Policy - SignKit

**Last Updated:** November 15, 2025  
**Effective Date:** November 15, 2025

## Overview

SignKit is designed with privacy as a core principle. This policy explains how we handle your data (spoiler: we barely collect any).

## The Short Version

**We don't collect, store, or transmit your documents or signatures. Everything happens locally on your computer.**

## Data Collection

### What We DON'T Collect

- ❌ Your documents or images
- ❌ Your extracted signatures
- ❌ Your PDF files
- ❌ Your processing settings or preferences
- ❌ Your usage patterns or behavior
- ❌ Your personal information (beyond what's needed for licensing)
- ❌ Analytics or tracking data

### What We DO Collect

**For License Validation Only:**
- Email address (if provided during purchase)
- License key
- License activation timestamp

**Stored Locally on Your Computer:**
- License information (in `~/.signkit/license.json`)
- Your signature library (in `~/.signkit/library/`)
- Application preferences (in `~/.signkit/config.json`)

**Note:** All of the above is stored ONLY on your computer. We never see it.

## How the Application Works

### Local Processing

**100% Local:** All image processing, signature extraction, and PDF operations happen entirely on your computer using:
- OpenCV for image processing
- PIL/Pillow for image manipulation
- PyPDF libraries for PDF operations

**No Cloud Uploads:** Your files never leave your device. There are no servers processing your documents.

**No Internet Required:** The core application works completely offline. Internet is only needed for:
- Initial license activation (one-time)
- Optional software updates (manual)

### Optional Backend (If Enabled)

The application includes an optional local backend server that runs on your computer (`localhost:8001`). This is:
- **Local only:** Runs on your computer, not in the cloud
- **Optional:** Core features work without it
- **No external communication:** Doesn't send data anywhere

## License Management

### License Activation

When you purchase a license:
1. You receive a license key via email from Gumroad
2. You enter the key in the application
3. The application validates the key format locally
4. License information is stored on your computer only

**No Phone Home:** License validation happens locally. We don't track license usage or activations.

### Test License

For testing purposes, the email `pranay@example.com` acts as a test license. This is hardcoded in the application and doesn't communicate with any server.

## Third-Party Services

### Gumroad (Payment Processing)

When you purchase Signature Extractor:
- **Payment handled by:** Gumroad (https://gumroad.com)
- **Information collected:** Name, email, payment details
- **Gumroad's privacy policy:** https://gumroad.com/privacy
- **We receive:** Only your email and purchase confirmation

### No Other Third Parties

We don't use:
- ❌ Analytics services (Google Analytics, Mixpanel, etc.)
- ❌ Crash reporting services (Sentry, Bugsnag, etc.)
- ❌ Advertising networks
- ❌ Social media tracking pixels
- ❌ Any other third-party services

## Data Storage

### On Your Computer

All application data is stored locally:
- **Location:** `~/.signkit/` (macOS/Linux) or `%USERPROFILE%\.signkit\` (Windows)
- **Contents:** License info, signature library, preferences
- **Control:** You can delete this folder anytime to remove all data

### On Our Servers

**We don't have servers.** We don't store any of your data.

## Data Sharing

**We don't share your data because we don't have your data.**

The only information we have is:
- Your email (from Gumroad, for license delivery)
- Purchase confirmation (from Gumroad, for our records)

We will never:
- Sell your information
- Share your information with third parties
- Use your information for marketing (beyond purchase confirmation)

## Your Rights

### Access and Deletion

Since all data is stored locally on your computer:
- **Access:** You can view all data in `~/.signkit/`
- **Deletion:** Delete the folder to remove all application data
- **Export:** Copy the folder to backup your data

### License Information

To request deletion of your email from our records:
- Email: support@signkit.work
- We'll delete your email within 7 days
- Your license will continue to work (it's validated locally)

## Security

### Local Security

Your data security depends on your computer's security:
- Keep your operating system updated
- Use strong passwords
- Enable disk encryption (FileVault, BitLocker, etc.)
- Use antivirus software

### Application Security

The application implements:
- Input validation to prevent malicious files
- File size limits (50MB max)
- Path sanitization to prevent directory traversal
- Secure temporary file handling
- Resource usage limits

See `docs/SECURITY.md` for technical details.

## Children's Privacy

Signature Extractor is not directed at children under 13. We don't knowingly collect information from children.

## Changes to This Policy

We may update this policy occasionally. Changes will be:
- Posted on our website
- Included in application updates
- Effective immediately upon posting

Continued use of the application after changes constitutes acceptance.

## International Users

Signature Extractor works the same everywhere because:
- All processing is local (no data crosses borders)
- No servers to comply with regional laws
- GDPR, CCPA, etc. don't apply (we don't collect data)

## Contact

Questions about privacy?
- **Email:** privacy@signkit.work
- **Website:** https://signkit.work
- **Response time:** Within 7 days

## Summary

**Privacy-First Design:**
- ✅ All processing happens locally
- ✅ No data collection or tracking
- ✅ No cloud uploads
- ✅ Works completely offline
- ✅ You control your data

**This is not just a privacy policy - it's how the application is fundamentally designed.**

---

**Questions?** If anything is unclear, please contact us. We're happy to explain how we protect your privacy.
