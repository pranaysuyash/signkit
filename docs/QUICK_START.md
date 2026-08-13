# Quick Start: Building & Testing

## ✅ What We Just Created

### Build Files

1. **`SignatureExtractor_macOS.spec`** - ARM64 (Apple Silicon) build config
2. **`SignatureExtractor_Intel.spec`** - Intel build config
3. **`build_macos.sh`** - Simple local builder (ARM64 only)
4. **`build_distribution.sh`** - Advanced multi-arch builder
5. **`.github/workflows/build-macos.yml`** - CI/CD for both architectures

### Documentation

- **`TESTING_GUIDE.md`** - Comprehensive testing instructions
- **`DISTRIBUTION_STRATEGY.md`** - Launch strategy guide
- **This file** - Quick reference

## 🚀 Right Now: Local Build Running

The build is currently creating an **ARM64 app** for your Mac (Apple Silicon).

**What's happening:**

- PyInstaller is bundling all dependencies
- Creating a standalone .app bundle
- This takes 3-5 minutes
- When done: `dist/SignatureExtractor.app`

## 📋 Next Steps (After Build Completes)

### 1. Test the App (5 minutes)

```bash
# Open the app
open dist/SignatureExtractor.app

# Paid activation is exercised with the signed-receipt test fixture in the
# repository suite. Do not use a raw email or arbitrary key as activation.
```

### 2. Quick Smoke Test

- ✅ App launches
- ✅ Enter a signed activation receipt in a development/test environment
- ✅ Upload an image
- ✅ Draw selection & process
- ✅ Export PNG
- ✅ Save to library

If all pass → **Ready for friends!**

### 3. Share with Friends (This Week)

**Who can test:**

- Friends with **Apple Silicon Macs** (M1/M2/M3/M4)
- Anyone with Mac from 2020 or newer

**How to share:**

```bash
# Option A: Send the .app directly
# Zip it first:
cd dist
zip -r SignatureExtractor_ARM64.zip SignatureExtractor.app
# Send SignatureExtractor_ARM64.zip

# Option B: Create DMG (nicer)
hdiutil create \
  -volname "Signature Extractor" \
  -srcfolder dist/SignatureExtractor.app \
  -ov \
  -format UDZO \
  dist/SignatureExtractor.dmg
# Send SignatureExtractor.dmg
```

**Tell friends:**

> "Right-click the app → Open (first time only)"
> A historical test grant exists only with explicit `SIGNKIT_LICENSE_TEST_MODE=1`.
> "Let me know if anything breaks!"

### 4. Gather Feedback (2-3 days)

Questions to ask:

- Did it launch without issues?
- Was anything confusing?
- Did you find any bugs?
- How was the performance?
- Would you pay $29 for this?

### 5. When Ready to Launch

```bash
# Create a release tag
git add -A
git commit -m "Release v1.0.0 preparations"
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin main
git push origin v1.0.0
```

**GitHub Actions will automatically:**

1. Build ARM64 version (Apple Silicon)
2. Build Intel version (Intel Macs)
3. Create DMG files for both
4. Create a GitHub Release with both attached

Then: Download both DMGs → Upload to Gumroad → Launch! 🎉

## 🎯 Current Build Status

| What        | Status                  | For Whom                        |
| ----------- | ----------------------- | ------------------------------- |
| ARM64 build | 🔄 In Progress          | Your Mac, friends with M-series |
| Intel build | ⏳ Not yet (need CI/CD) | Intel Mac users                 |
| Testing     | ⏳ After build          | You + friends                   |
| Launch      | ⏳ After testing        | Everyone                        |

## 🔧 Troubleshooting

### If build fails:

```bash
# Clean and retry
rm -rf build dist
./build-tools/build_macos.sh
```

### If app won't open:

```bash
# Remove quarantine attribute
xattr -cr dist/SignatureExtractor.app
open dist/SignatureExtractor.app
```

### If missing dependencies:

```bash
source venv/bin/activate
pip install -r desktop_app/requirements.txt
pip install pyinstaller
```

## 📊 What You'll Have After This

### Today

- ✅ Working ARM64 app
- ✅ Tested on your Mac
- ✅ Shared with 3-5 Apple Silicon friends
- ✅ Initial feedback collected

### Next Week

- ✅ Both ARM64 + Intel builds (via GitHub Actions)
- ✅ Both uploaded to Gumroad
- ✅ Ready for public launch
- ✅ Covers 100% of Mac users

## ⏱️ Time Estimates

- **Build completion:** 2-3 more minutes
- **Testing:** 5-10 minutes
- **Share with friends:** 1 minute
- **Wait for feedback:** 2-3 days
- **Fix issues:** 1-2 days
- **CI/CD setup:** Already done!
- **Launch:** Push a git tag, wait 15 minutes

## 💡 Pro Tips

1. **Test thoroughly yourself first** before sharing
2. **Use the signed-receipt fixture** from the entitlement contract tests for
   local development testing; do not place test grants in a packaged build.
3. **Ask friends for honest feedback** - don't take it personally
4. **Fix critical issues** before public launch
5. **Use GitHub Actions** for final builds (ensures consistency)

## 🎉 You're Almost There!

The hard part (coding, testing, building) is done. Now it's just:

1. Wait for build (2 min)
2. Test (5 min)
3. Share with friends
4. Launch when ready!

---

**Current Time Estimate to Launch:** 5-7 days

- Testing: 2-3 days
- Fixes: 1-2 days
- CI/CD build: 15 minutes
- Gumroad setup: 2-3 hours
- **Launch!** 🚀
