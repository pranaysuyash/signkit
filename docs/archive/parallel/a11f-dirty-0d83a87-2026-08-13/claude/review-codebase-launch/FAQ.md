# Frequently Asked Questions (FAQ)

Common questions about SignKit - Professional Signature Extractor

---

## General Questions

### What is SignKit?

SignKit is a professional desktop application that extracts signatures from images and documents with pixel-perfect precision. It allows you to select signature regions, adjust processing parameters, and export transparent PNG files for use in digital documents.

### What platforms does SignKit support?

- **macOS**: 10.15 (Catalina) or later (both Apple Silicon and Intel Macs)
- **Windows**: Windows 10 (64-bit) or later
- **Linux**: Ubuntu 20.04+, Fedora 35+, or equivalent

### Is there a free trial?

Yes! You can download and use SignKit with limited features:
- ✅ Full signature extraction and preview
- ✅ All image controls (zoom, threshold, color)
- ❌ Export disabled (trial mode watermark)
- ❌ PDF signing disabled

Purchase a license for $29 to unlock all features.

### How much does SignKit cost?

**$29 one-time payment** - no subscription required.
- Lifetime license for the version purchased
- Free updates within major version (1.x)
- 30-day money-back guarantee

### Is my payment secure?

Yes. All payments are processed through Gumroad, a trusted e-commerce platform used by thousands of creators. We never see or store your credit card information.

---

## Privacy & Security

### Where are my images processed?

**All image processing happens locally on your computer.** Your signatures and documents never leave your device unless you explicitly enable optional cloud features (coming in future versions).

### Do you collect any data?

We collect minimal data:
- ✅ License key and email (for validation only)
- ❌ No images or signatures
- ❌ No usage analytics (unless you opt-in)
- ❌ No tracking cookies

See our [Privacy Policy](../legal/PRIVACY_POLICY.md) for details.

### Is SignKit HIPAA/GDPR compliant?

SignKit's local-first architecture supports compliance requirements:
- **GDPR**: ✅ Local processing, minimal data collection, user data rights supported
- **HIPAA**: ✅ Potential compliance (consult your legal counsel for specific use cases)
- **SOC 2**: Audit logging supports compliance workflows

### Can I use SignKit for sensitive documents?

Yes. Since all processing happens locally and no data is uploaded to external servers, SignKit is suitable for confidential documents. However, always follow your organization's security policies.

---

## Technical Questions

### Does SignKit require internet?

**Core features work offline:**
- ✅ Signature extraction
- ✅ Image processing
- ✅ Export to PNG/JPG
- ✅ PDF signing

**Internet required for:**
- License validation (first time only)
- Checking for updates
- Optional cloud features (future)

### What image formats are supported?

**Input**: PNG, JPEG/JPG, BMP, TIFF
**Output**: PNG (with transparency), JPG (with background)

### What's the maximum image size?

- **File size**: 50MB maximum
- **Dimensions**: 10,000 x 10,000 pixels
- **Selection**: 25 million pixels per selection

Large images are automatically optimized for performance.

### Can I extract multiple signatures from one image?

Currently, you can extract one signature at a time. For multiple signatures:
1. Extract and save the first signature
2. Make a new selection for the second signature
3. Repeat for additional signatures

Batch processing is planned for v1.1 (Q1 2026).

### Does SignKit support handwritten text?

SignKit is optimized for **signatures** (short, artistic text). It may work for handwritten text, but results will vary. For best results:
- Use high-contrast images (dark ink on white paper)
- Adjust threshold slider for optimal separation
- Consider OCR software for full handwritten document digitization

---

## Licensing Questions

### How do I activate my license?

1. Purchase from [Gumroad](https://pranaysuyash.gumroad.com/l/signkit-v1)
2. You'll receive an email with your license key
3. Open SignKit → **License** → **Enter License Key**
4. Paste your key and click **Activate**
5. Features unlock immediately

### Can I use my license on multiple computers?

**Single-user license**: Use on up to **3 devices** you personally own and use.
**Multi-user**: Contact us for team/organization licensing.

### What happens when I upgrade my computer?

Deactivate your license on the old computer (License → Deactivate), then activate on the new one. If you no longer have access to the old computer, email support@signkit.work.

### Do I get free updates?

- **Minor updates** (1.x): ✅ Free forever
- **Major updates** (2.0+): May require upgrade fee (discounted for existing users)

### What if I lose my license key?

Email support@signkit.work with your purchase email address. We'll resend your key within 24 hours.

### Can I get a refund?

**30-day money-back guarantee** - no questions asked. Email support@signkit.work with your order number.

---

## Usage Questions

### How do I extract a signature?

1. Click **Upload Image** (or Cmd/Ctrl+O)
2. Click and drag to select the signature region
3. Adjust **Threshold** slider to refine the extraction
4. (Optional) Change signature color
5. Click **Save to Library** or **Export PNG**

See [User Guide](USER_GUIDE.md) for detailed walkthrough.

### My extracted signature has white background - how do I fix it?

Make sure you're exporting as **PNG** (not JPG). PNG format supports transparency. If you need JPG, use the "Export JPG" option which adds a white background intentionally.

### The signature looks too thick/thin after extraction

Adjust the **Threshold** slider:
- Move **left** (lower value) = thinner signature, keeps lighter details
- Move **right** (higher value) = thicker signature, removes gray areas

Experiment with different values to find the perfect balance.

### Can I change the signature color?

Yes! Click the **Color** button and choose any color. This is useful for:
- Matching corporate branding
- Creating blue-ink digital signatures
- Making signatures stand out on colored documents

### How do I sign a PDF?

1. Go to **PDF** tab
2. Click **Open PDF**
3. Select a signature from **My Signatures**
4. Click on the PDF where you want to place it
5. Resize/reposition as needed
6. Click **Sign PDF** to save

The original PDF is never modified - a new signed PDF is created.

### Can I sign multiple pages?

Yes! After placing a signature on one page:
1. Navigate to the next page
2. Place signature as before
3. Repeat for all pages
4. Click **Sign PDF** once at the end

All signatures are applied to a single output PDF.

### How do I save signatures for reuse?

After extracting a signature, click **Save to Library**. It's stored in:
- **macOS**: `~/Library/Application Support/SignatureExtractor/`
- **Windows**: `%APPDATA%/SignatureExtractor/`
- **Linux**: `~/.local/share/SignatureExtractor/`

Access saved signatures from the **My Signatures** panel.

---

## Troubleshooting

### The app won't open (macOS)

**Error**: "App can't be opened because Apple cannot check it for malicious software"

**Solution**:
1. Right-click SignatureExtractor.app → **Open**
2. Click **Open** in the dialog
3. App will open and remember this choice

**Alternative**:
1. System Preferences → Security & Privacy → General
2. Click **"Open Anyway"** next to the warning

This is normal for unsigned apps. Notarization coming soon.

### Windows Defender blocks the app

**Error**: "Windows protected your PC"

**Solution**:
1. Click **More info**
2. Click **Run anyway**

This is normal for new applications. Code signing coming soon.

### Backend won't start / "Offline Mode" shown

**Causes**:
- Port 8001 already in use
- Firewall blocking localhost connections
- Antivirus quarantining backend

**Solutions**:
1. Check if port 8001 is available
2. Allow SignKit in firewall/antivirus
3. Core features still work offline - only cloud features affected

### License validation fails

**Error**: "Invalid license key"

**Checklist**:
- ✅ Copy-paste license key (don't type manually)
- ✅ Include dashes if present
- ✅ Check for extra spaces before/after
- ✅ Verify email matches purchase email
- ✅ Check internet connection

Still failing? Email support@signkit.work

### Exported signature looks different than preview

**Possible causes**:
- Image compression (use PNG, not JPG)
- Color profile mismatch
- Viewing in different software

**Solution**: Always export as PNG for exact match to preview.

### Selection area is wrong after rotating image

This is a known issue in v1.0. **Workaround**:
1. Rotate image **before** making selection
2. Rotate using Cmd/Ctrl+R or toolbar button
3. Make selection after rotation is complete

Fixed in v1.0.1 (coming soon).

---

## Feature Requests

### Can SignKit automatically detect signatures?

Not yet, but it's planned! Version 1.1 (Q1 2026) will include auto-detection using contour analysis. You'll be able to:
- Upload image → auto-detect all signatures
- Select from detected options
- Manual override still available

### Will there be a mobile app?

Yes! Mobile companion app is planned for v1.2 (Q2 2026) for:
- Quick signature capture with camera
- Sync with desktop (optional cloud)
- On-the-go signing

### Can I batch-process multiple documents?

Batch PDF signing is available now (paid license). Batch extraction for multiple images is planned for v1.1.

### Will there be browser extension?

Yes! Chrome/Firefox extension planned for v1.1 (Q1 2026) for:
- Right-click image → Extract signature
- Quick extraction without opening desktop app
- Requires desktop app installed

### Can I suggest a feature?

Absolutely! Email feature@signkit.work with:
- Feature description
- Your use case
- How often you'd use it

We read every suggestion and prioritize based on user feedback.

---

## Support

### How do I get help?

1. **Check this FAQ** (you're here!)
2. **Read documentation**: [User Guide](USER_GUIDE.md), [Installation Guide](INSTALLATION_GUIDE.md)
3. **Generate diagnostic report**: Help → Generate Diagnostic Report
4. **Email support**: support@signkit.work

### What information should I include in support requests?

- Operating system and version
- SignKit version (Help → About)
- Step-by-step description of issue
- Screenshots if applicable
- Diagnostic report (Help → Generate Diagnostic Report)

### What's your support response time?

- **Critical issues** (app won't start, license issues): 24-48 hours
- **Technical support**: 2-3 business days
- **General questions**: 3-5 business days

### Do you offer phone support?

Email support only at this time. For enterprise/team licenses ($500+), we offer scheduled video call support.

### Can I request a new feature?

Yes! See "Feature Requests" section above.

---

## Legal

### What's your refund policy?

**30-day money-back guarantee** - no questions asked. Email support@signkit.work with your order number.

Refunds processed within 5-7 business days to original payment method.

### What are the license terms?

See [End User License Agreement (EULA)](../legal/EULA.md) for complete terms.

**Summary**:
- Single-user license for personal/commercial use
- Use on up to 3 devices you own
- No redistribution or resale
- No reverse engineering

### Can I use SignKit for commercial purposes?

Yes! The standard license includes commercial use rights. You can:
- ✅ Use in your business
- ✅ Process client documents
- ✅ Integrate into workflows
- ❌ Resell as a service (contact us for API licensing)

### Do you offer enterprise licenses?

Yes! Email enterprise@signkit.work for:
- Volume licensing (10+ users)
- Custom deployment
- Dedicated support
- Service Level Agreements (SLAs)

---

## Company

### Who makes SignKit?

SignKit is developed by **PSRS Tech**, an independent software company focused on privacy-first productivity tools.

### How can I contact you?

- **Support**: support@signkit.work
- **Sales**: sales@signkit.work
- **General**: founder@signkit.work
- **Website**: [signkit.work](https://signkit.work)

### Are you hiring?

Not currently, but check back! Follow us on Twitter [@signkit](https://twitter.com/signkit) for announcements.

---

## Still have questions?

**Email us**: support@signkit.work

We typically respond within 24-48 hours for critical issues, 2-3 business days for technical questions.

---

*Last updated: November 2025*
