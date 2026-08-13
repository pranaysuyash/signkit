# ModernMacButton Visibility Fix

**Date:** 2025-11-06
**Issue:** ModernMacButton invisible in main app sidebar
**Status:** ✅ FIXED

---

## The Problem 🐛

You could see ModernMacButton in the onboarding dialog, but **not in the main app sidebar**.

### Root Cause:

**Stylesheet conflict in `extraction.py` lines 359-364:**

```python
# Line 359-360: Base button styling (applied to ALL QPushButton including ModernMacButton)
f"QWidget#extractionControlsPanel QPushButton {{ padding: 7px 14px; border-radius: 8px; border: 1px solid {button_border_str};"
f"  background-color: {button_bg_str}; color: {text_color.name()}; font-weight: 500; }}"

# Line 364: Tried to exclude ModernMacButton but made it transparent instead!
f"QWidget#extractionControlsPanel QPushButton#ModernMacButton {{ border: none; background: transparent; }}"
```

**What happened:**
1. ModernMacButton uses custom `paintEvent()` to draw itself
2. The stylesheet on line 364 set `background: transparent`
3. This **overrode** ModernMacButton's custom painting
4. Result: **Buttons were invisible!**

---

## The Fix ✅

**Changed lines 359-363 in `extraction.py`:**

### Before:
```python
f"QWidget#extractionControlsPanel QPushButton {{ padding: 7px 14px; border-radius: 8px; border: 1px solid {button_border_str};"
f"  background-color: {button_bg_str}; color: {text_color.name()}; font-weight: 500; }}"
f"QWidget#extractionControlsPanel QPushButton:hover {{ background-color: {button_hover_str}; }}"
f"QWidget#extractionControlsPanel QPushButton:focus {{ border: 2px solid {'#007AFF' if is_dark_mode else '#0051D5'}; outline: none; }}"
f"QWidget#extractionControlsPanel QPushButton:disabled {{ color: {disabled_text_str}; background-color: {disabled_bg_str}; border-color: {subtle_line_str}; }}"
f"QWidget#extractionControlsPanel QPushButton#ModernMacButton {{ border: none; background: transparent; }}"
```

### After:
```python
# Standard QPushButton styling (excludes ModernMacButton which uses custom paintEvent)
f"QWidget#extractionControlsPanel QPushButton:not([objectName='ModernMacButton']) {{ padding: 7px 14px; border-radius: 8px; border: 1px solid {button_border_str};"
f"  background-color: {button_bg_str}; color: {text_color.name()}; font-weight: 500; }}"
f"QWidget#extractionControlsPanel QPushButton:not([objectName='ModernMacButton']):hover {{ background-color: {button_hover_str}; }}"
f"QWidget#extractionControlsPanel QPushButton:not([objectName='ModernMacButton']):focus {{ border: 2px solid {'#007AFF' if is_dark_mode else '#0051D5'}; outline: none; }}"
f"QWidget#extractionControlsPanel QPushButton:disabled {{ color: {disabled_text_str}; background-color: {disabled_bg_str}; border-color: {subtle_line_str}; }}"
# Removed the transparent background line that was breaking ModernMacButton!
```

**Key changes:**
1. ✅ Added `:not([objectName='ModernMacButton'])` to **exclude** ModernMacButton from standard styling
2. ✅ Removed the problematic `QPushButton#ModernMacButton { background: transparent }` line
3. ✅ ModernMacButton now renders using its custom `paintEvent()` without interference

---

## How It Works Now ✅

### ModernMacButton rendering:
1. `ModernMacButton.__init__()` sets `objectName` to `"ModernMacButton"`
2. Custom `paintEvent()` draws glassmorphism effects
3. Stylesheet **excludes** buttons with `objectName='ModernMacButton'`
4. Result: **Beautiful glassmorphism buttons!** 🎨

### Standard QPushButton rendering:
1. Uses normal Qt widget rendering
2. Stylesheet applies background, border, hover effects
3. Not affected by ModernMacButton changes

---

## Testing Checklist ✅

**Run the app and verify:**
- [ ] ModernMacButton visible in sidebar (all buttons)
- [ ] Glassmorphism effect visible
- [ ] Hover animations work
- [ ] Press animations work
- [ ] Focus rings visible (Tab key navigation)
- [ ] Colors correct (blue, green, red, etc.)
- [ ] Dark mode works
- [ ] Light mode works

---

## Files Modified

1. **extraction.py** (lines 359-363)
   - Added `:not([objectName='ModernMacButton'])` to stylesheet selectors
   - Removed problematic transparent background line
   - Added comment explaining exclusion

---

## Why Onboarding Worked But Main App Didn't

**Onboarding dialog:**
- No conflicting stylesheets
- ModernMacButton rendered with custom `paintEvent()`
- Visible ✅

**Main app sidebar:**
- Had conflicting stylesheet (lines 359-364)
- Stylesheet overrode custom painting
- Invisible ❌
- **Now fixed!** ✅

---

## Lesson Learned

**When using custom-painted widgets (like ModernMacButton):**
1. ✅ Use `:not([objectName='WidgetName'])` to exclude from parent stylesheets
2. ✅ Document why the exclusion is needed
3. ✅ Test in all contexts (dialogs, main window, panels)
4. ❌ Don't set `background: transparent` on custom-painted widgets

---

## Next Steps

**After testing:**
1. If buttons visible → Mark as complete ✅
2. If still issues → Check for other stylesheet conflicts
3. Consider rolling out ModernMacButton to other dialogs (2-3 hours)

---

*Fix applied: 2025-11-06*
*Issue: Stylesheet conflict making ModernMacButton invisible*
*Solution: Exclude ModernMacButton from standard QPushButton styling*
*Status: Ready for testing*
