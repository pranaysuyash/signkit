# Code Signing & Notarization Guide for SignKit

## Overview

Code signing and notarization are **optional** but recommended for macOS builds to:

- Remove "unidentified developer" warnings
- Enable Gatekeeper approval
- Build user trust
- Allow distribution outside the Mac App Store

**Current Status:** SignKit builds are **unsigned and un-notarized**. They work perfectly but require users to right-click → Open on first launch.

---

## Prerequisites

### 1. Apple Developer Account

- **Cost:** $99/year
- **Sign up:** https://developer.apple.com/programs/

### 2. Developer Certificates

You need two certificates from Apple:

1. **Developer ID Application** (for code signing)
2. **Developer ID Installer** (optional, for .pkg installers)

### 3. App-Specific Password

For notarization, create an app-specific password:

1. Go to https://appleid.apple.com/account/manage
2. Sign in with your Apple ID
3. Generate app-specific password under Security section

### 4. Tools

- **Xcode Command Line Tools** (already installed on macOS)
- **notarytool** (included with Xcode 13+)

---

## Step 1: Install Certificates

### Download Certificates from Apple Developer Portal

1. Go to https://developer.apple.com/account/resources/certificates/list
2. Create/download "Developer ID Application" certificate
3. Double-click the downloaded certificate to install in Keychain

### Verify Installation

```bash
security find-identity -v -p codesigning
```

Should show something like:

```
1) ABC123DEF456... "Developer ID Application: Your Name (TEAM_ID)"
```

---

## Step 2: Sign the App Bundle

### Basic Signing

```bash
cd /path/to/signature-extractor-app/dist

# Sign the app bundle
codesign --force --deep --sign "Developer ID Application: Your Name (TEAM_ID)" \
  --options runtime \
  --entitlements ../build-tools/entitlements.plist \
  SignKit.app

# Verify signing
codesign --verify --verbose=4 SignKit.app
spctl --assess --verbose=4 --type execute SignKit.app
```

### Create Entitlements File

Create `build-tools/entitlements.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Allow JIT compilation for Python runtime -->
    <key>com.apple.security.cs.allow-jit</key>
    <true/>

    <!-- Allow unsigned executable memory (needed for PyInstaller) -->
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>

    <!-- Disable library validation (needed for bundled libraries) -->
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>

    <!-- Hardened runtime -->
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>

    <!-- Network access (for backend server) -->
    <key>com.apple.security.network.server</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>

    <!-- File access -->
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>

    <!-- Printing -->
    <key>com.apple.security.print</key>
    <true/>
</dict>
</plist>
```

---

## Step 3: Create Signed DMG

```bash
cd dist

# Create a signed DMG
hdiutil create -volname "SignKit" \
  -srcfolder SignKit.app \
  -ov -format UDZO \
  SignKit_Signed.dmg

# Sign the DMG
codesign --force --sign "Developer ID Application: Your Name (TEAM_ID)" \
  SignKit_Signed.dmg

# Verify
codesign --verify --verbose=4 SignKit_Signed.dmg
```

---

## Step 4: Notarize with Apple

### Using notarytool (Xcode 13+)

```bash
# Store credentials (one-time setup)
xcrun notarytool store-credentials "signkit-notary" \
  --apple-id "your-email@example.com" \
  --team-id "YOUR_TEAM_ID" \
  --password "app-specific-password"

# Submit for notarization
xcrun notarytool submit SignKit_Signed.dmg \
  --keychain-profile "signkit-notary" \
  --wait

# If successful, staple the notarization ticket
xcrun stapler staple SignKit_Signed.dmg

# Verify notarization
xcrun stapler validate SignKit_Signed.dmg
spctl --assess --type open --context context:primary-signature --verbose SignKit_Signed.dmg
```

### Check Notarization Status

```bash
# Get submission history
xcrun notarytool history --keychain-profile "signkit-notary"

# Get detailed log for a submission
xcrun notarytool log <submission-id> --keychain-profile "signkit-notary"
```

---

## Step 5: Automate in CI/CD

### GitHub Actions Integration

Add secrets to your GitHub repository:

- `APPLE_CERTIFICATE_BASE64` (Developer ID cert exported as base64)
- `APPLE_CERTIFICATE_PASSWORD` (cert password)
- `APPLE_ID` (your Apple ID email)
- `APPLE_TEAM_ID` (your team ID)
- `APPLE_APP_PASSWORD` (app-specific password)

Update `.github/workflows/build-all-platforms.yml`:

```yaml
- name: Import Code Signing Certificate
  if: runner.os == 'macOS'
  env:
    CERTIFICATE_BASE64: ${{ secrets.APPLE_CERTIFICATE_BASE64 }}
    CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
  run: |
    echo "$CERTIFICATE_BASE64" | base64 --decode > certificate.p12
    security create-keychain -p actions build.keychain
    security default-keychain -s build.keychain
    security unlock-keychain -p actions build.keychain
    security import certificate.p12 -k build.keychain -P "$CERTIFICATE_PASSWORD" -T /usr/bin/codesign
    security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k actions build.keychain
    rm certificate.p12

- name: Sign App Bundle
  if: runner.os == 'macOS'
  run: |
    codesign --force --deep --sign "Developer ID Application" \
      --options runtime \
      --entitlements build-tools/entitlements.plist \
      dist/SignKit.app

- name: Create and Sign DMG
  if: runner.os == 'macOS'
  run: |
    hdiutil create -volname "SignKit" -srcfolder dist/SignKit.app -ov -format UDZO dist/SignKit_Signed.dmg
    codesign --force --sign "Developer ID Application" dist/SignKit_Signed.dmg

- name: Notarize DMG
  if: runner.os == 'macOS'
  env:
    APPLE_ID: ${{ secrets.APPLE_ID }}
    APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
    APPLE_APP_PASSWORD: ${{ secrets.APPLE_APP_PASSWORD }}
  run: |
    xcrun notarytool submit dist/SignKit_Signed.dmg \
      --apple-id "$APPLE_ID" \
      --team-id "$APPLE_TEAM_ID" \
      --password "$APPLE_APP_PASSWORD" \
      --wait
    xcrun stapler staple dist/SignKit_Signed.dmg
```

---

## Export Certificate for CI

To get the base64-encoded certificate:

```bash
# Export from Keychain
security find-identity -v -p codesigning
# Note the identity hash (e.g., ABC123DEF456...)

# Export as .p12 with password
security export -k login.keychain -t identities -f pkcs12 \
  -P "your-export-password" \
  -o developer_id.p12 \
  ABC123DEF456...

# Convert to base64
base64 -i developer_id.p12 -o developer_id_base64.txt

# Copy the contents of developer_id_base64.txt to GitHub secrets
cat developer_id_base64.txt

# Clean up
rm developer_id.p12 developer_id_base64.txt
```

---

## Troubleshooting

### Common Issues

**"The application is damaged and can't be opened"**

- Solution: Quarantine attribute. Run: `xattr -cr SignKit.app`

**"resource fork, Finder information, or similar detritus not allowed"**

- Solution: Clean extended attributes: `xattr -cr SignKit.app` before signing

**Notarization fails with "invalid signature"**

- Ensure you signed with `--options runtime`
- Check entitlements are properly configured
- Verify all nested binaries are signed

**"The executable does not have the hardened runtime enabled"**

- Add `--options runtime` to codesign command
- Check entitlements file is valid

### Verify What's Signed

```bash
# Check signature
codesign -dv --verbose=4 SignKit.app

# List all signed binaries in bundle
find SignKit.app -type f -exec file {} \; | grep Mach-O | cut -d: -f1 | xargs codesign -dv
```

---

## Cost-Benefit Analysis

### Benefits

✅ No "unidentified developer" warning  
✅ Users can double-click to open immediately  
✅ Increased trust and professionalism  
✅ Better distribution on enterprise networks  
✅ Required for Mac App Store (if you go that route)

### Costs

❌ $99/year for Apple Developer account  
❌ Additional build complexity  
❌ Notarization adds ~10-15 minutes per build  
❌ Need to manage certificates and renew annually  
❌ Requires secure storage of credentials in CI

### Recommendation for SignKit

**For MVP/Early Launch:** Skip it. Current approach works fine:

- Users right-click → Open (one time)
- Saves $99/year + complexity
- Focus on product and users first

**When to Add Signing:**

- Revenue > $5k/month (justify $99 cost)
- User complaints about security warnings
- Enterprise customers requiring signed apps
- Preparing for Mac App Store submission

---

## Alternative: User Instructions

Instead of signing, provide clear instructions:

### macOS Security Instructions

**First-time users see "unidentified developer" warning:**

1. Right-click (or Control-click) on SignKit.app
2. Select "Open" from the menu
3. Click "Open" in the dialog
4. App will open and remember this choice

**Or use terminal:**

```bash
xattr -cr /Applications/SignKit.app
open /Applications/SignKit.app
```

---

## Quick Reference

| Task                  | Command                                                                       |
| --------------------- | ----------------------------------------------------------------------------- |
| Sign app              | `codesign --force --deep --sign "Developer ID" --options runtime SignKit.app` |
| Verify signature      | `codesign --verify --verbose=4 SignKit.app`                                   |
| Remove quarantine     | `xattr -cr SignKit.app`                                                       |
| Check Gatekeeper      | `spctl --assess --verbose=4 --type execute SignKit.app`                       |
| Submit notarization   | `xcrun notarytool submit SignKit.dmg --keychain-profile "profile"`            |
| Staple ticket         | `xcrun stapler staple SignKit.dmg`                                            |
| Validate notarization | `xcrun stapler validate SignKit.dmg`                                          |

---

## Resources

- [Apple Code Signing Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [notarytool Documentation](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution/customizing_the_notarization_workflow)
- [Hardened Runtime Entitlements](https://developer.apple.com/documentation/security/hardened_runtime)
- [PyInstaller Code Signing](https://pyinstaller.org/en/stable/feature-notes.html#macos-code-signing)

---

## Status for SignKit

**Current:** Unsigned builds work perfectly. Users need to right-click → Open once.

**Future:** When revenue justifies $99/year, follow this guide to add signing/notarization.

**Priority:** **LOW** - Focus on product features and user acquisition first.
