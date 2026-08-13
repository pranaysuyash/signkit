# Signature Extractor - Testing Guide

## Quick Start Testing

### 1. Launch the App

```bash
# From Finder
open dist/SignatureExtractor.app

# Or from terminal
./dist/SignatureExtractor.app/Contents/MacOS/SignatureExtractor
```

**First Launch Note:** macOS may block the app because it's not signed. To allow it:

1. Right-click the app → Select "Open"
2. Click "Open" in the security dialog
3. Or: System Preferences → Security & Privacy → Click "Open Anyway"

### 2. Test License System

The app includes a **test license** for testing all features:

**Test License Email:** `pranay@example.com`

#### Testing Trial Mode (Restricted Features)

1. Launch the app without entering a license
2. Try to export a signature → Should show restriction dialog
3. Try to use PDF features → Should show restriction dialog
4. Verify "Purchase License" button opens Gumroad page

#### Testing Full Access

1. Enter license: `pranay@example.com` (any key works with this email)
2. Verify all features unlock immediately
3. Test that export works
4. Test that PDF features work
5. Restart app → Verify license persists

### 3. Core Feature Testing

#### A. Image Upload & Processing

**Test Case 1: Upload JPG Image**

```
1. Click "Upload" or drag-drop a JPG file
2. Verify image displays in source pane
3. Draw selection around signature
4. Click "Process"
5. Verify signature appears in processed pane
```

**Test Case 2: Upload PNG Image**

```
1. Upload a PNG with transparency
2. Verify transparency is preserved
3. Process signature
4. Verify output maintains transparency
```

**Test Case 3: EXIF Rotation (Mobile Photos)**

```
1. Upload a photo taken with phone (rotated)
2. Verify auto-rotation works correctly
3. Selection should work on rotated image
```

#### B. Rotation

**Test Case 4: Rotate Source Image**

```
1. Upload an image
2. Click rotate clockwise (90°)
3. Verify image rotates correctly
4. Draw selection and process
5. Verify coordinates are preserved
6. Rotate counter-clockwise
7. Verify image returns to original orientation
```

#### C. Threshold Adjustment

**Test Case 5: Threshold Control**

```
1. Process a signature
2. Adjust threshold slider (0-255)
3. Verify signature becomes lighter/darker
4. Find optimal threshold for clean signature
5. Process again with new threshold
```

#### D. Color Selection

**Test Case 6: Custom Colors**

```
1. Process a signature
2. Try different colors:
   - Black (#000000)
   - Blue (#0000FF)
   - Custom color
3. Verify color applies correctly
4. Export and verify color in saved file
```

#### E. Export Functionality

**Test Case 7: Export PNG**

```
1. Process a signature
2. Click "Export PNG"
3. Choose location
4. Verify file saves
5. Open saved file → Verify quality
```

**Test Case 8: Export JPG**

```
1. Process a signature
2. Click "Export JPG"
3. Verify quality settings option
4. Save and verify output
```

#### F. Library Management

**Test Case 9: Save to Library**

```
1. Process a signature
2. Click "Add to Library"
3. Enter a name
4. Verify appears in library list
5. Close and reopen app
6. Verify library persists
```

**Test Case 10: Load from Library**

```
1. Double-click library item
2. Verify signature loads
3. Verify can reprocess with different settings
4. Verify rotation works on library items
```

**Test Case 11: Delete from Library**

```
1. Right-click library item
2. Select "Delete"
3. Confirm deletion
4. Verify item removed
```

#### G. PDF Operations

**Test Case 12: Open PDF**

```
1. Click "PDF" tab
2. Click "Open PDF"
3. Select a PDF file
4. Verify PDF pages display
5. Navigate between pages
```

**Test Case 13: Paste Signature on PDF**

```
1. Open a PDF
2. Process a signature (on Extraction tab)
3. Go to PDF tab
4. Click "Paste Signature"
5. Click on PDF to place signature
6. Resize/position signature
7. Verify looks correct
```

**Test Case 14: Save Signed PDF**

```
1. Place signature on PDF
2. Click "Save PDF"
3. Choose location
4. Verify signed PDF saves
5. Open in Preview/Adobe → Verify signature appears
```

### 4. Error Handling Tests

#### Test Case 15: Invalid File Format

```
1. Try to upload .txt file
2. Verify appropriate error message
3. Try to upload .docx
4. Verify rejection with clear message
```

#### Test Case 16: Very Large Image

```
1. Upload very large image (>50MB)
2. Verify size validation works
3. Check error message is helpful
```

#### Test Case 17: Corrupted Image

```
1. Try to upload corrupted/incomplete image
2. Verify graceful error handling
3. App should not crash
```

### 5. Performance Tests

#### Test Case 18: Large Image Processing

```
1. Upload 20MB image (high resolution)
2. Time: Should process < 5 seconds
3. Verify memory usage reasonable
4. Verify UI remains responsive
```

#### Test Case 19: Multiple Operations

```
1. Upload, process, rotate, adjust threshold
2. Do this 10 times in a row
3. Verify no memory leaks
4. Verify performance doesn't degrade
```

### 6. UI/UX Tests

#### Test Case 20: Window Resize

```
1. Resize window to various sizes
2. Verify layout adapts
3. Verify no clipping or overlapping
4. Test minimum window size
```

#### Test Case 21: Dark Mode (macOS)

```
1. Switch macOS to dark mode
2. Verify app UI updates
3. Verify all text is readable
4. Verify buttons/controls visible
```

#### Test Case 22: Zoom and Pan

```
1. Upload large image
2. Use mouse wheel to zoom
3. Verify smooth zoom
4. Pan around image
5. Verify panning works correctly
```

### 7. Session Persistence

#### Test Case 23: App Restart

```
1. Process signature
2. Quit app (Cmd+Q)
3. Relaunch app
4. Verify license persists
5. Verify library persists
6. Recent state should reset (expected)
```

### 8. Backend Integration (Optional)

The app works **offline-first** but has optional backend features.

#### Test Case 24: Offline Operation

```
1. Disconnect from internet
2. Upload and process signatures
3. Verify all core features work
4. Rotate, export, save to library
5. All should work without internet
```

#### Test Case 25: Backend Auto-Start

```
1. Launch app with internet
2. Check status bar for backend status
3. Verify backend starts automatically (if configured)
4. Or verify graceful fallback to offline mode
```

## Test Checklist for Friends/Beta Testers

Ask them to complete this checklist:

- [ ] App launches successfully
- [ ] License activation works (`pranay@example.com`)
- [ ] Can upload and process at least 3 different images
- [ ] Rotation works correctly
- [ ] Export works (PNG and JPG)
- [ ] Library save/load works
- [ ] PDF features work (if they test PDFs)
- [ ] No crashes during normal use
- [ ] Performance is acceptable
- [ ] UI is intuitive and easy to understand
- [ ] Overall experience is positive

## What to Watch For

### Critical Issues (Blockers)

- ❌ App won't launch
- ❌ App crashes frequently
- ❌ License system doesn't work
- ❌ Core extraction fails
- ❌ Can't export results

### Important Issues (Should Fix)

- ⚠️ Performance is slow (>10s for processing)
- ⚠️ UI is confusing
- ⚠️ Error messages are unclear
- ⚠️ Features are hard to discover

### Nice to Fix (Post-Launch)

- 💡 UI could be prettier
- 💡 Could use keyboard shortcuts
- 💡 Feature requests
- 💡 Minor visual glitches

## Reporting Issues

When reporting issues, include:

1. **What were you trying to do?**
2. **What actually happened?**
3. **Steps to reproduce**
4. **macOS version**
5. **Screenshot (if UI issue)**
6. **Does it happen every time?**

## Quick Smoke Test (2 minutes)

For quick validation:

```bash
1. Launch app                     ✓/✗
2. Enter test license             ✓/✗
3. Upload test image              ✓/✗
4. Draw selection & process       ✓/✗
5. Export to PNG                  ✓/✗
6. Save to library                ✓/✗
7. Load from library              ✓/✗
8. Quit and relaunch              ✓/✗
```

All steps should complete without errors.

## Test Images

You can create test images or use:

- Scanned documents with signatures
- Photos of signatures
- Digital signatures
- Screenshots with signatures

## Expected Behavior

### ✅ Should Work

- All image formats (PNG, JPG, JPEG)
- Images with transparency
- High-resolution images
- Mobile photos (with EXIF rotation)
- Offline operation
- License activation and persistence
- All export formats
- Library management
- PDF signing

### ⚠️ Known Limitations

- Maximum file size: 50MB
- Maximum dimensions: 10000x10000px
- Backend features may require internet (optional)
- macOS Gatekeeper warning on first launch (expected)

## Success Criteria

The app is ready if:

- ✅ No critical crashes
- ✅ License system works
- ✅ Core extraction works reliably
- ✅ Export produces quality results
- ✅ UI is usable and intuitive
- ✅ Performance is acceptable (<5s processing)
- ✅ Friends can use it without instructions

## Next Steps After Testing

1. Gather all feedback
2. Prioritize issues (Critical → Important → Nice)
3. Fix critical issues
4. Update this guide based on findings
5. Do another test round if needed
6. When stable → Prepare for wider release

## Questions to Ask Friends

1. What was your first impression?
2. Was anything confusing?
3. Did you encounter any errors?
4. How was the performance?
5. Would you pay $29 for this?
6. What features are missing?
7. On a scale of 1-10, how would you rate it?
8. Would you recommend it to others?

---

**Remember:** This is a test build. Expect some rough edges. The goal is to find and fix issues before the public launch!
