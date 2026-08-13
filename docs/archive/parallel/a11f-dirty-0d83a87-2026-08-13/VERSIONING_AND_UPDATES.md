# Versioning and Update Strategy

## Version Philosophy (Affinity-Style)

Following Affinity Designer/Photo's approach: **Major versions are separate products**.

### Version 1.x Strategy

**License Model:**

- One-time purchase: $29
- Covers ALL v1.x updates (1.0, 1.1, 1.2, ... 1.99)
- Free updates for v1 lifetime
- No subscription

**What's Included in v1 License:**

- ✅ Bug fixes (1.0.1, 1.0.2, etc.)
- ✅ Minor features (1.1.0, 1.2.0, etc.)
- ✅ Performance improvements
- ✅ New export formats
- ✅ UI/UX enhancements
- ✅ Security patches
- ✅ macOS compatibility updates

**What's NOT Included:**

- ❌ Major version upgrade (v2.0 would be separate purchase)

### Version 2.0 (Future)

**When v2.0 Launches:**

- New product listing on Gumroad
- New price: $39 (or $29 with 50% upgrade discount)
- Separate from v1 license
- v1 users get loyalty upgrade pricing

**What Justifies v2.0:**

- Major architectural rewrite
- Significant new capabilities (AI-powered extraction, batch processing, cloud sync)
- New business model considerations
- Incompatible changes requiring new codebase

## Semantic Versioning

We use **SemVer** (MAJOR.MINOR.PATCH):

```
v1.2.3
│ │ │
│ │ └─ PATCH: Bug fixes, security patches
│ └─── MINOR: New features, backward compatible
└───── MAJOR: Breaking changes, new product generation
```

### Examples:

**v1.0.0** - Initial release

- Core extraction features
- PDF signing
- Library management

**v1.1.0** - Minor update (free for v1 license holders)

- Added batch processing
- New export format (SVG)
- Performance improvements

**v1.0.1** - Patch (free for v1 license holders)

- Fixed JPEG loading bug
- Security validator improvements

**v2.0.0** - Major update (NEW PRODUCT, separate purchase)

- AI-powered auto-detection
- Cloud synchronization
- Team collaboration features
- New pricing: $39 (or $19 upgrade from v1)

## Update Delivery Mechanism

### Option 1: GitHub Releases (Recommended)

**How it works:**

1. App checks: `https://api.github.com/repos/pranaysuyash/signkit/releases/latest`
2. Compares current version with latest
3. Shows notification if update available
4. User downloads manually from GitHub

**Pros:**

- ✅ Free hosting
- ✅ Simple implementation
- ✅ No infrastructure needed
- ✅ Transparent versioning

**Cons:**

- ❌ Manual download/install
- ❌ Users must replace app
- ❌ No automatic updates

### Option 2: Sparkle Framework (macOS)

**What it is:**

- Industry-standard auto-updater for macOS apps
- Used by: Sketch, Tower, Tweetbot, etc.

**How it works:**

1. Include Sparkle framework in app bundle
2. Host `appcast.xml` file (version manifest)
3. App checks for updates automatically
4. One-click download and install

**appcast.xml example:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle">
    <channel>
        <title>Signature Extractor Updates</title>
        <item>
            <title>Version 1.1.0</title>
            <sparkle:version>1.1.0</sparkle:version>
            <sparkle:minimumSystemVersion>11.0</sparkle:minimumSystemVersion>
            <pubDate>Mon, 20 Nov 2025 10:00:00 +0000</pubDate>
            <enclosure
                url="https://github.com/pranaysuyash/signkit/releases/download/v1.1.0/SignatureExtractor_ARM64.dmg"
                sparkle:version="1.1.0"
                type="application/octet-stream"
            />
            <description><![CDATA[
                <h2>What's New in 1.1.0</h2>
                <ul>
                    <li>Added batch processing</li>
                    <li>Performance improvements</li>
                    <li>Bug fixes</li>
                </ul>
            ]]></description>
        </item>
    </channel>
</rss>
```

**Pros:**

- ✅ Professional auto-updates
- ✅ One-click install
- ✅ Delta updates (smaller downloads)
- ✅ Industry standard

**Cons:**

- ❌ macOS only (need separate for Windows)
- ❌ Requires code signing ($99/year Apple Developer)
- ❌ More complex setup

### Option 3: Gumroad License Check

**How it works:**

1. Check Gumroad API: "Is this license valid?"
2. Gumroad returns: license tier, version entitled
3. Block major version upgrades if not entitled

**Implementation:**

```python
# Check license entitlement
response = requests.post('https://api.gumroad.com/v2/licenses/verify', {
    'product_id': 'YOUR_PRODUCT_ID',
    'license_key': user_license,
    'increment_uses_count': False
})

if response.ok:
    data = response.json()
    if data['success']:
        # Check which version they're entitled to
        purchase_date = data['purchase']['created_at']
        if purchase_date < V2_LAUNCH_DATE:
            entitled_version = 1
        else:
            entitled_version = 2

        if CURRENT_VERSION.major > entitled_version:
            show_upgrade_dialog()
```

**Pros:**

- ✅ Control version entitlements
- ✅ Works cross-platform
- ✅ Can offer upgrade discounts programmatically

**Cons:**

- ❌ Requires internet connection
- ❌ Dependency on Gumroad API
- ❌ Privacy concerns (phones home)

## Recommended Approach

### Phase 1: Launch (v1.0.0) - Manual Updates

- **Update check:** GitHub API
- **Delivery:** Manual download from GitHub Releases
- **Notification:** In-app banner when update available
- **Why:** Simple, no infrastructure, focus on product

### Phase 2: Growth (v1.x) - Semi-Automatic

- **Update check:** GitHub API + Gumroad license verify
- **Delivery:** Still manual but with better UX
- **In-app:** "Update Available → Download → Auto-install"
- **Why:** Better UX without complex infrastructure

### Phase 3: Mature (v2.0+) - Automatic Updates

- **macOS:** Sparkle framework
- **Windows:** WinSparkle or custom updater
- **Gumroad:** Version entitlement checks
- **Code signing:** Required at this stage
- **Why:** Professional polish, user expectation

## Version Gating Strategy

### In-App Checks

```python
# config.py
APP_VERSION = "1.2.3"
APP_VERSION_MAJOR = 1

# license/validator.py
class LicenseValidator:
    def check_version_entitlement(self, license_key: str) -> bool:
        """Check if license covers current app version."""
        try:
            # Option A: Embed purchase date in license
            # Format: v1-YYYYMMDD-RANDOMHASH
            if license_key.startswith('v1-'):
                return APP_VERSION_MAJOR == 1
            elif license_key.startswith('v2-'):
                return APP_VERSION_MAJOR == 2

            # Option B: Check with Gumroad API
            response = self._verify_with_gumroad(license_key)
            return response['entitled_major_version'] >= APP_VERSION_MAJOR

        except Exception:
            # Graceful degradation: allow usage if check fails
            return True
```

### Update Dialog UX

**Minor update (1.1.0 → 1.2.0):**

```
┌─────────────────────────────────────┐
│  Update Available                   │
├─────────────────────────────────────┤
│                                     │
│  Version 1.2.0 is now available     │
│  (you have 1.1.0)                   │
│                                     │
│  What's new:                        │
│  • Faster processing                │
│  • New export formats               │
│  • Bug fixes                        │
│                                     │
│  This is a FREE update included     │
│  with your v1 license.              │
│                                     │
│  [ Download ] [ Remind Later ]      │
│  [ Skip This Version ]              │
└─────────────────────────────────────┘
```

**Major update (1.x → 2.0):**

```
┌─────────────────────────────────────┐
│  Signature Extractor 2.0 Available  │
├─────────────────────────────────────┤
│                                     │
│  A new major version is available   │
│  with exciting new features:        │
│                                     │
│  • AI-powered auto-detection        │
│  • Cloud sync & collaboration       │
│  • Batch processing for 100s        │
│  • Advanced editing tools           │
│                                     │
│  Your v1 license: $29               │
│  Upgrade to v2: $19 (save $10!)     │
│  Regular price: $39                 │
│                                     │
│  [ Get Upgrade ] [ Learn More ]     │
│  [ Keep Using v1 ]                  │
└─────────────────────────────────────┘
```

## Release Process

### For Minor Updates (1.x.y)

```bash
# 1. Update version in code
echo "APP_VERSION = '1.2.0'" > desktop_app/version.py

# 2. Update CHANGELOG
echo "## v1.2.0 - 2025-11-20
- Added batch processing
- Performance improvements
- Bug fixes
" >> CHANGELOG.md

# 3. Commit and tag
git add -A
git commit -m "Release v1.2.0"
git tag -a v1.2.0 -m "Release v1.2.0 - Batch processing & improvements"
git push origin main
git push origin v1.2.0

# 4. GitHub Actions builds both architectures automatically
# 5. DMGs uploaded to GitHub Release
# 6. Users get in-app notification
```

### For Major Updates (2.0)

```bash
# 1. Create new Gumroad product
# Product: "Signature Extractor v2"
# Price: $39 (or $19 with v1 discount code)

# 2. Update license format in code
# v1 licenses: "v1-20251113-abc123"
# v2 licenses: "v2-20260101-xyz789"

# 3. Release as usual
git tag -a v2.0.0 -m "Release v2.0.0 - Major upgrade"
git push origin v2.0.0

# 4. Update website/marketing
# - Announce v2 launch
# - Offer upgrade discount
# - Keep v1 available for existing users
```

## DMG Storage Strategy

### ❌ NOT in Git Repository

- DMG files are **large binaries** (200-400MB each)
- Would bloat repository size
- Git is designed for source code, not artifacts

### ✅ GitHub Releases

- DMGs stored as **Release Assets**
- Unlimited bandwidth for public repos
- Auto-cleanup after 90 days (configurable)
- Perfect for distribution

### ✅ CDN/Gumroad (Optional)

- Upload DMG to Gumroad as product file
- Gumroad handles distribution
- License verification built-in
- Better for paid products

## File Structure

```
.gitignore              # Excludes dist/, build/, *.dmg
dist/                   # Local builds (gitignored)
  ├── SignatureExtractor.app
  └── SignatureExtractor_ARM64.dmg

build/                  # PyInstaller artifacts (gitignored)

build-tools/            # Source files (tracked in git)
  ├── *.spec           # Build specifications
  └── *.sh             # Build scripts

.github/workflows/      # CI/CD (tracked in git)
  └── build-macos.yml  # Builds & uploads to GitHub Releases

# DMGs only exist in:
# 1. GitHub Releases (public download)
# 2. Gumroad (for paying customers)
# 3. Local dist/ folder (temporary, not committed)
```

## Summary

**v1.x Strategy:**

- ✅ One-time $29 license
- ✅ Covers ALL v1 updates forever
- ✅ Manual updates via GitHub initially
- ✅ DMGs in GitHub Releases (not repo)
- ✅ Simple update notification

**v2.0 Strategy:**

- ✅ New product, separate purchase
- ✅ $39 regular or $19 upgrade from v1
- ✅ Gumroad license distinguishes v1 vs v2
- ✅ In-app upgrade prompts
- ✅ Both versions supported concurrently

**Technical:**

- ✅ Drag-and-drop already implemented
- ✅ CI/CD builds both architectures
- ✅ DMGs stored in GitHub Releases
- ✅ Update checks via GitHub API
- ✅ Version gating via license prefix
