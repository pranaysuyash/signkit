# Implementation Plan: ChatGPT UX Review
**Date:** November 2, 2025
**Based on:** ChatGPT comprehensive UI/UX audit
**Priority:** HIGH → MEDIUM → LOW tasks

---

## Phase 1: Critical Fixes (This Week)
**Goal:** Prevent UI freezes, enable distribution, improve accessibility
**Estimated Time:** 6-9 hours total

### Task 1.1: Async Backend Health Check ⚡ CRITICAL
**Why:** Prevents 3-second UI freezes on network issues
**Impact:** HIGH - User experience, app responsiveness
**Time:** 2-3 hours

**Files to modify:**
- Create: `desktop_app/views/main_window_parts/health_mixin.py`
- Update: `desktop_app/views/main_window_parts/__init__.py`
- Update: `desktop_app/views/main_window.py`

**Implementation steps:**
```python
# 1. Create health_mixin.py with async health check
class HealthCheckMixin:
    def _check_backend_health(self) -> None:
        """Async health check with exponential backoff."""
        # Use run_async() from extraction.py
        # Implement exponential backoff: 100ms, 500ms, 1s, 2s, 5s
        # Update backend_status_label based on results

    def _update_backend_status(self, status: str, payload: dict) -> None:
        """Update persistent backend indicator."""
        # status: "checking", "online", "offline", "degraded"
        # Update label text, color, icon
        # Set tooltip with details
        # Make clickable

    def _on_backend_status_clicked(self) -> None:
        """Handle click - open health page or troubleshooting."""
```

**Testing:**
- [ ] Launch app with backend down - should not freeze
- [ ] Backend comes online - indicator turns green within 5s
- [ ] Click indicator when online - opens health page
- [ ] Click indicator when offline - opens troubleshooting

---

### Task 1.2: Persistent Backend Health Indicator ✅ HIGH VALUE
**Why:** Infrastructure exists, just needs wiring
**Impact:** HIGH - Professional feel, constant feedback
**Time:** 1-2 hours

**Files to modify:**
- Update: `desktop_app/views/main_window_parts/status.py`
- Update: `desktop_app/views/main_window_parts/health_mixin.py` (from 1.1)

**Implementation steps:**
```python
# In status.py - already has backend_status_label!
# Just needs:
# 1. Color coding (green/yellow/red)
# 2. Icons (●, ⏳, ⚠)
# 3. Tooltip with timestamp and URL
# 4. Click handler
```

**Testing:**
- [ ] Indicator visible in status bar
- [ ] Color changes based on health state
- [ ] Tooltip shows helpful information
- [ ] Click opens appropriate action

---

### Task 1.3: Fix Hardcoded Health URL ⚡ QUICK WIN
**Why:** Backend URL is configurable, menu link should match
**Impact:** MEDIUM - Correctness
**Time:** 5 minutes

**Files to modify:**
- Update: `desktop_app/views/main_window.py:113`

**Change:**
```python
# Before:
self.check_health_action.triggered.connect(
    lambda: self._open_url("http://127.0.0.1:8001/health")
)

# After:
self.check_health_action.triggered.connect(
    lambda: self._open_url(f"{self.api_client.base_url}/health")
)
```

**Testing:**
- [ ] Menu item opens correct URL
- [ ] Works with custom backend URL in config

---

### Task 1.4: Docs Path Fallback 📦 CRITICAL FOR DISTRIBUTION
**Why:** Relative paths fail in packaged .app bundle
**Impact:** HIGH - Distribution readiness
**Time:** 1 hour

**Files to modify:**
- Update: `desktop_app/views/main_window_parts/native_dialogs.py`
- Or add method to: `desktop_app/views/main_window.py`

**Implementation:**
```python
def _open_document(self, doc_path: str) -> None:
    """Open local doc or fallback to web version.

    Tries:
    1. Relative to codebase (development)
    2. Relative to executable (packaged)
    3. Web-hosted docs (last resort)
    """
    import os
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QDesktopServices

    # Try relative to this file (development)
    local_path = os.path.join(
        os.path.dirname(__file__), "..", "..", doc_path
    )

    if os.path.exists(local_path):
        url = QUrl.fromLocalFile(os.path.abspath(local_path))
        QDesktopServices.openUrl(url)
        return

    # Try relative to executable (packaged)
    if getattr(sys, 'frozen', False):
        bundle_path = os.path.join(sys._MEIPASS, doc_path)
        if os.path.exists(bundle_path):
            url = QUrl.fromLocalFile(bundle_path)
            QDesktopServices.openUrl(url)
            return

    # Fallback to web
    WEB_DOCS = {
        "docs/HELP.md": "https://docs.signature-extractor.com/help",
        "docs/SHORTCUTS.md": "https://docs.signature-extractor.com/shortcuts",
        "docs/TROUBLESHOOTING.md": "https://docs.signature-extractor.com/troubleshooting",
        "docs/PDF_SETUP.md": "https://docs.signature-extractor.com/pdf-setup",
    }

    web_url = WEB_DOCS.get(doc_path, "https://docs.signature-extractor.com")
    QDesktopServices.openUrl(QUrl(web_url))
```

**Testing:**
- [ ] Docs open in development
- [ ] Docs open in packaged build (future)
- [ ] Falls back to web gracefully

---

### Task 1.5: Accessibility Names 🦮 HIGH PRIORITY
**Why:** Screen reader users need descriptive labels
**Impact:** HIGH - Accessibility, inclusive design
**Time:** 30 minutes

**Files to modify:**
- Update: `desktop_app/views/main_window.py`
- Update: `desktop_app/views/main_window_parts/extraction.py`
- Update: `desktop_app/views/main_window_parts/toolbar.py`
- Update: `desktop_app/views/main_window_parts/pdf.py`

**Implementation:**
```python
# In main_window.py
self.tab_widget.setAccessibleName("Main workflow tabs")
self.tab_widget.setAccessibleDescription(
    "Switch between signature extraction and PDF signing workflows"
)

# In extraction.py
self.src_view.setAccessibleName("Source image pane")
self.src_view.setAccessibleDescription("Original image with selection tool")

self.preview_view.setAccessibleName("Preview pane")
self.preview_view.setAccessibleDescription("Preview of extracted signature")

self.res_view.setAccessibleName("Result image pane")
self.res_view.setAccessibleDescription("Final processed signature ready for export")

# In toolbar.py
open_action.setAccessibleName("Open image or PDF file")
export_action.setAccessibleName("Export processed signature")
save_library_action.setAccessibleName("Save signature to library")

# In pdf.py
self.pdf_view.setAccessibleName("PDF document viewer")
self.signature_list.setAccessibleName("Saved signatures list")
```

**Testing:**
- [ ] VoiceOver (macOS) announces all elements correctly
- [ ] Tab navigation reaches all interactive elements
- [ ] Descriptions are helpful and concise

---

## Phase 2: Major Features (Next 2 Weeks)
**Goal:** Onboarding, license UI, keyboard shortcuts, drag & drop
**Estimated Time:** 11-16 hours total

### Task 2.1: First-Run Onboarding Dialog 🎓
**Why:** Reduces friction for new users
**Impact:** MEDIUM - New user experience
**Time:** 4-6 hours

**Files to create:**
- Create: `desktop_app/views/onboarding_dialog.py`
- Update: `desktop_app/views/main_window.py`

**Content sections (from ChatGPT draft):**
1. Welcome title & subtitle
2. Quick start (4 steps)
3. Connectivity status & check button
4. PDF setup status & guide button
5. Export folder location & change button
6. Footer actions (Start / Quick Guide / Don't show again)

**Implementation:**
```python
# OnboardingDialog structure
class OnboardingDialog(QDialog):
    def __init__(self, api_client, session, parent=None):
        # Title & subtitle
        # Quick start section with 4 cards
        # Connectivity section with live status
        # PDF section with setup button
        # Paths section with folder browser
        # Footer with 3 buttons

    def _run_connectivity_check(self):
        # Async check with progress feedback

    def _open_pdf_guide(self):
        # Open PDF setup documentation

    def _change_export_folder(self):
        # Native folder picker

    def _dont_show_again(self):
        # Save to QSettings
```

**Integration:**
```python
# In main_window.py __init__
QTimer.singleShot(100, self._maybe_show_onboarding)

def _maybe_show_onboarding(self):
    settings = QSettings()
    if not settings.value("onboarding/shown", False, type=bool):
        dialog = OnboardingDialog(self.api_client, self.session, self)
        dialog.exec()
```

**Testing:**
- [ ] Shows on first launch
- [ ] Doesn't show on subsequent launches
- [ ] Can be re-opened from Help menu
- [ ] Connectivity check works
- [ ] PDF guide opens
- [ ] Folder selection works

---

### Task 2.2: Enhanced License UI 📜
**Why:** Better status visibility and management
**Impact:** MEDIUM - User experience
**Time:** 2-3 hours

**Files to modify:**
- Update: `desktop_app/views/main_window.py` (menu setup)
- Update: `desktop_app/views/license_dialog.py` (if exists)

**Implementation:**
```python
# In _setup_menus()
license_menu = menu_bar.addMenu("License")

# Show current status
if is_licensed():
    status_action = QAction("✓ Licensed", self)
    status_action.setEnabled(False)
    license_menu.addAction(status_action)

    manage_action = QAction("Manage License...", self)
    manage_action.setShortcut("Cmd+Shift+L")
    manage_action.triggered.connect(self.on_manage_license)
    license_menu.addAction(manage_action)
else:
    status_action = QAction("⚠ Trial Mode", self)
    status_action.setEnabled(False)
    license_menu.addAction(status_action)

    # ... Enter License, Buy License actions with shortcuts
```

**Testing:**
- [ ] Menu shows correct status (licensed vs trial)
- [ ] Shortcuts work
- [ ] Enter License disabled when already licensed
- [ ] Manage License shows current email

---

### Task 2.3: Improved Keyboard Shortcuts ⌨️
**Why:** Discoverability and productivity
**Impact:** MEDIUM - User experience
**Time:** 2 hours

**Files to modify:**
- Update: `desktop_app/views/main_window.py`
- Update: `docs/KEYBOARD_SHORTCUTS.md`

**New shortcuts to add:**
```python
# File menu
close_action = QAction("Close Window", self)
close_action.setShortcut(QKeySequence.StandardKey.Close)  # Cmd+W

# View menu
next_tab_action = QAction("Next Tab", self)
next_tab_action.setShortcut("Ctrl+Tab")

prev_tab_action = QAction("Previous Tab", self)
prev_tab_action.setShortcut("Ctrl+Shift+Tab")

toggle_fullscreen = QAction("Toggle Full Screen", self)
toggle_fullscreen.setShortcut("Ctrl+Cmd+F")

# Tools menu
copy_diagnostics_action = QAction("Copy Diagnostics", self)
copy_diagnostics_action.setShortcut("Cmd+Shift+D")

open_logs_action = QAction("Open Logs Directory", self)
open_logs_action.setShortcut("Cmd+Shift+O")
```

**Testing:**
- [ ] All shortcuts work
- [ ] Shown in menu labels
- [ ] No conflicts
- [ ] Documented in SHORTCUTS.md

---

### Task 2.4: Global Drag & Drop 🎯
**Why:** Better file opening UX
**Impact:** MEDIUM - User experience
**Time:** 3-4 hours

**Files to modify:**
- Update: `desktop_app/views/main_window.py`

**Implementation:**
```python
# Add to MainWindow class
def __init__(self, ...):
    super().__init__(parent)
    # ... existing code ...
    self.setAcceptDrops(True)
    self._drop_overlay = None

def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
        event.acceptProposedAction()
        self._show_drop_overlay()

def dragLeaveEvent(self, event):
    self._hide_drop_overlay()

def dropEvent(self, event):
    self._hide_drop_overlay()
    urls = event.mimeData().urls()
    if not urls:
        return

    file_path = urls[0].toLocalFile()

    # Route to appropriate tab
    if file_path.lower().endswith('.pdf'):
        self.tab_widget.setCurrentIndex(self._pdf_tab_index)
        # Trigger PDF load
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        self.tab_widget.setCurrentIndex(self._extraction_tab_index)
        # Trigger image load
    else:
        QMessageBox.warning(
            self,
            "Unsupported File",
            f"Cannot open {os.path.basename(file_path)}"
        )

    event.acceptProposedAction()

def _show_drop_overlay(self):
    """Show 'Drop to open' overlay."""
    if not self._drop_overlay:
        self._drop_overlay = QLabel("Drop files to open", self)
        self._drop_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drop_overlay.setStyleSheet(
            "background-color: rgba(0, 120, 215, 180);"
            "color: white;"
            "font-size: 32px;"
            "font-weight: bold;"
            "border-radius: 16px;"
        )

    self._drop_overlay.setGeometry(self.rect())
    self._drop_overlay.show()

def _hide_drop_overlay(self):
    if self._drop_overlay:
        self._drop_overlay.hide()
```

**Testing:**
- [ ] Drop image anywhere - loads in extraction tab
- [ ] Drop PDF anywhere - loads in PDF tab
- [ ] Overlay shows during drag
- [ ] Overlay hides after drop/cancel
- [ ] Cursor changes appropriately

---

## Phase 3: Polish & Long-Term (Next Month)
**Goal:** Window state, theme toggle, testing, audits
**Estimated Time:** 10-13 hours total

### Task 3.1: Window State Persistence 💾
**Time:** 1 hour

**Files to modify:**
- Update: `desktop_app/views/main_window.py`

**Implementation:**
```python
def _restore_window_state(self):
    settings = QSettings()
    geometry = settings.value("window/geometry")
    if geometry:
        self.restoreGeometry(geometry)

    last_tab = settings.value("window/activeTab", 0, type=int)
    if 0 <= last_tab < self.tab_widget.count():
        self.tab_widget.setCurrentIndex(last_tab)

def closeEvent(self, event):
    settings = QSettings()
    settings.setValue("window/geometry", self.saveGeometry())
    settings.setValue("window/activeTab", self.tab_widget.currentIndex())
    super().closeEvent(event)
```

---

### Task 3.2: Theme Toggle Menu 🌓
**Time:** 2 hours

**Files to modify:**
- Update: `desktop_app/views/main_window_parts/theme.py`

**Implementation:**
```python
# Add View > Appearance submenu with:
# - Automatic (Follow System) [✓]
# - Light Mode
# - Dark Mode

def _set_theme_mode(self, mode: str):
    settings = QSettings()
    settings.setValue("appearance/mode", mode)
    self._apply_theme()
```

---

### Task 3.3: Mixin Smoke Tests 🧪
**Time:** 2 hours

**Files to create:**
- Create: `tests/test_main_window.py`

**Tests:**
```python
def test_mixin_contract():
    """Verify all mixin methods exist."""
    window = MainWindow(mock_client, mock_session)
    assert hasattr(window, '_on_tab_changed')
    # ... all other mixin methods
    window.close()

def test_health_check_non_blocking():
    """Verify health check doesn't block UI."""
    # Measure time to window.show()
    # Should be < 100ms even with backend down
```

---

### Task 3.4: Contrast Audit 🎨
**Time:** 3-4 hours

**Tools:**
- WebAIM Contrast Checker
- macOS Accessibility Inspector

**Areas to audit:**
- Disabled button text
- Status bar labels
- Inactive pane borders
- Tooltips in dark mode
- Focus indicators

**Action:** Document findings, fix violations

---

### Task 3.5: Icon Quality Verification 🖼️
**Time:** 2-3 hours

**Files to review:**
- `desktop_app/resources/icons.py`
- All icon assets

**Checks:**
- [ ] SVG format or @2x/@3x variants
- [ ] No pixelation at 200% scaling
- [ ] Appropriate fallbacks
- [ ] macOS SF Symbols consideration

---

## Additional Documentation Tasks

### Create New Docs

1. **TROUBLESHOOTING.md**
   - Backend connectivity issues
   - PDF library installation
   - License activation problems
   - Export failures

2. **PDF_SETUP.md**
   - System requirements
   - Installing pypdfium2
   - Installing pikepdf
   - Troubleshooting import errors

3. **COPY_GUIDELINES.md**
   - Status message templates
   - Error message format
   - Tooltip conventions
   - Accessibility text

### Create Resource Files

1. **desktop_app/resources/copy.py**
   - All status messages from ChatGPT draft
   - Centralized UX copy

2. **desktop_app/utils/diagnostics.py**
   - Format diagnostic summary
   - Copy to clipboard helper

---

## Success Criteria

### Phase 1 Complete When:
- [ ] App launches without UI freezes
- [ ] Backend health indicator is persistent and accurate
- [ ] Docs open in development and packaged builds
- [ ] Screen reader announces all major elements
- [ ] No hardcoded URLs remain

### Phase 2 Complete When:
- [ ] New users see helpful onboarding
- [ ] License status is always visible
- [ ] All keyboard shortcuts work and documented
- [ ] Files can be dropped anywhere on window
- [ ] UX copy follows ChatGPT standards

### Phase 3 Complete When:
- [ ] Window remembers size and tab
- [ ] Theme can be manually overridden
- [ ] Smoke tests catch mixin issues
- [ ] All UI passes WCAG AA contrast
- [ ] Icons are crisp at all scales

---

## Risk Mitigation

### Risk: Breaking existing functionality
**Mitigation:**
- Create feature branches for each task
- Test thoroughly before merging
- Keep changes isolated to specific files

### Risk: Time estimates too optimistic
**Mitigation:**
- Start with Phase 1 (highest value)
- Adjust timeline after first few tasks
- Defer Phase 3 if needed

### Risk: QSettings not working in packaged build
**Mitigation:**
- Test early with PyInstaller
- Document QSettings path in docs
- Provide fallbacks where critical

---

## Progress Tracking

Update this section as tasks complete:

### Phase 1: ⬜ 0/5 Complete
- [ ] Task 1.1: Async health check
- [ ] Task 1.2: Persistent health indicator
- [ ] Task 1.3: Fix hardcoded URL
- [ ] Task 1.4: Docs path fallback
- [ ] Task 1.5: Accessibility names

### Phase 2: ⬜ 0/4 Complete
- [ ] Task 2.1: First-run onboarding
- [ ] Task 2.2: Enhanced license UI
- [ ] Task 2.3: Improved keyboard shortcuts
- [ ] Task 2.4: Global drag & drop

### Phase 3: ⬜ 0/5 Complete
- [ ] Task 3.1: Window state persistence
- [ ] Task 3.2: Theme toggle menu
- [ ] Task 3.3: Mixin smoke tests
- [ ] Task 3.4: Contrast audit
- [ ] Task 3.5: Icon quality verification

---

**Plan created:** November 2, 2025
**Based on:** [CHATGPT_UX_REVIEW_ANALYSIS_NOV_2_2025.md](./CHATGPT_UX_REVIEW_ANALYSIS_NOV_2_2025.md)
**Next step:** User approval to begin Phase 1
