# ChatGPT UX Review Analysis & Implementation Plan

**Date:** November 2, 2025
**Review Source:** ChatGPT detailed UI/UX audit
**Current Status:** Analysis and gap identification complete
**Next Steps:** Prioritized implementation roadmap

---

## Executive Summary

ChatGPT conducted a comprehensive UI/UX review focusing on:
1. **Runtime and reliability risks** - 7 critical issues identified
2. **UX upgrades** - 9 high-impact improvements suggested
3. **Cross-platform & accessibility** - 4 key areas
4. **Polish items** - 3 refinements
5. **Draft copy** - Complete status messages, onboarding sheet, and diagnostics format

### Current State Analysis

**✅ What's Already Implemented:**
- Mixin-based architecture (solid separation of concerns)
- Early theme application with macOS dark mode support
- PDF capability detection and status messaging
- Tabbed interface for multiple workflows
- Backend health check system (basic)
- Application identity configuration

**⚠️ What Needs Attention:**
- Many improvements suggested in review are NOT yet implemented
- Some risks identified are present in current code
- UX copy needs significant enhancement
- Missing accessibility features
- No persistent backend health indicator
- No first-run onboarding

---

## Detailed Gap Analysis

### 1. Runtime and Reliability Risks

#### 1.1 Implicit Mixin Contracts ⚠️
**Status:** PRESENT RISK

**Finding:**
> "You call self._on_tab_changed, self._init_status_bar, self._setup_main_toolbar, self._setup_extraction_ui, self._setup_pdf_ui, self._setup_dark_mode_support, and self._check_backend_health without visible definitions here. If any mixin drops or a name shifts, you will crash at runtime or silently skip health checks."

**Current Code Evidence:**
- [main_window.py:57](desktop_app/views/main_window.py#L57) - `self.tab_widget.currentChanged.connect(self._on_tab_changed)`
- [main_window.py:62-67](desktop_app/views/main_window.py#L62-L67) - Calls to `_setup_extraction_ui()`, `_setup_pdf_ui()`, `_init_status_bar()`, `_setup_main_toolbar()`
- [main_window.py:78](desktop_app/views/main_window.py#L78) - `self._setup_dark_mode_support()`
- [main_window.py:84](desktop_app/views/main_window.py#L84) - `self._check_backend_health()`

**What We Have:**
- Mixins are properly imported and inherited
- Methods exist in respective mixins
- No smoke tests to verify mixin contract compliance

**Recommendation:**
```python
# Add to tests/test_main_window.py
def test_mixin_contract():
    """Verify all mixin methods exist before MainWindow instantiation."""
    window = MainWindow(mock_client, mock_session)
    assert hasattr(window, '_on_tab_changed')
    assert hasattr(window, '_init_status_bar')
    assert hasattr(window, '_setup_main_toolbar')
    assert hasattr(window, '_setup_extraction_ui')
    assert hasattr(window, '_setup_pdf_ui')
    assert hasattr(window, '_setup_dark_mode_support')
    assert hasattr(window, '_check_backend_health')
    window.close()
```

**Priority:** MEDIUM (add smoke tests)

---

#### 1.2 Timer Health Check on UI Thread ⚠️
**Status:** PRESENT RISK

**Finding:**
> "QTimer.singleShot(10, self._check_backend_health) will run whatever network call you do on the main thread if that method is synchronous. That risks micro-freezes on launch."

**Current Code Evidence:**
- [main_window.py:84](desktop_app/views/main_window.py#L84) - `QTimer.singleShot(10, self._check_backend_health)`
- [api/client.py:68-85](desktop_app/api/client.py#L68-L85) - `health_check()` uses synchronous `requests.get()` with 3s timeout

**Analysis:**
- Health check IS synchronous
- 10ms timer means it runs almost immediately after window shows
- 3-second timeout could freeze UI for 3 seconds on network issues
- Backend may not be ready in 10ms (race condition)

**What We Need:**
```python
# In extraction.py or new health_mixin.py
def _check_backend_health(self) -> None:
    """Check backend health asynchronously with exponential backoff."""
    self._backend_check_attempt = getattr(self, '_backend_check_attempt', 0) + 1
    max_attempts = 5

    # Exponential backoff: 100ms, 500ms, 1s, 2s, 5s
    delays = [100, 500, 1000, 2000, 5000]

    def _async_health_check():
        ok, payload = self.api_client.health_check(timeout=2.0)
        return ok, payload

    def _on_health_result(result):
        ok, payload = result
        if ok:
            self._update_backend_status("online", payload)
            self._backend_check_attempt = 0
        else:
            if self._backend_check_attempt < max_attempts:
                delay = delays[min(self._backend_check_attempt, len(delays)-1)]
                QTimer.singleShot(delay, self._check_backend_health)
            else:
                self._update_backend_status("offline", payload)

    def _on_health_error(error):
        LOG.error("Health check error: %s", error, exc_info=True)
        if self._backend_check_attempt < max_attempts:
            delay = delays[min(self._backend_check_attempt, len(delays)-1)]
            QTimer.singleShot(delay, self._check_backend_health)
        else:
            self._update_backend_status("offline", {"error": str(error)})

    # Run in background thread
    future = run_async(_async_health_check)
    # Note: Need to implement proper signal/slot for result handling
```

**Priority:** HIGH (can cause UI freezes)

---

#### 1.3 Hardcoded Health URL ⚠️
**Status:** PRESENT RISK

**Finding:**
> "The Help menu points to http://127.0.0.1:8001/health. If the server port changes via config or CLI, this link lies."

**Current Code Evidence:**
- [main_window.py:113](desktop_app/views/main_window.py#L113) - Hardcoded `"http://127.0.0.1:8001/health"`
- [api/client.py:11-12](desktop_app/api/client.py#L11-L12) - `ApiClient` has configurable `base_url`

**Fix:**
```python
# In main_window.py or native_dialogs.py
def _setup_menus(self) -> None:
    # ... existing code ...

    self.check_health_action = QAction("Open Backend Health", self)
    self.check_health_action.triggered.connect(
        lambda: self._open_url(f"{self.api_client.base_url}/health")
    )
    help_menu.addAction(self.check_health_action)
```

**Priority:** MEDIUM (easy fix, good correctness)

---

#### 1.4 Status Bar Dependency ⚠️
**Status:** PRESENT RISK

**Finding:**
> "You call self.status_bar.showMessage. If _init_status_bar ever fails to attach status_bar, you crash."

**Current Code Evidence:**
- [main_window.py:69,75](desktop_app/views/main_window.py#L69) - `self.status_bar.showMessage(...)`
- [status.py:27-39](desktop_app/views/main_window_parts/status.py#L27-L39) - `_init_status_bar()` creates `self.status_bar`
- No guard against missing status_bar in other code

**Analysis:**
- `_init_status_bar()` is called before status messages (good)
- BUT: No try/except or hasattr checks
- If exception occurs in _init_status_bar, subsequent calls will crash

**Recommendation:**
```python
# Add defensive property in PaneStatusMixin
@property
def status_bar(self) -> QStatusBar:
    """Get status bar, creating if needed."""
    if not hasattr(self, '_status_bar') or self._status_bar is None:
        LOG.warning("Status bar accessed before initialization, creating now")
        self._init_status_bar()
    return self._status_bar

@status_bar.setter
def status_bar(self, value: QStatusBar):
    self._status_bar = value
```

**Priority:** LOW (unlikely to fail, but good defensive coding)

---

#### 1.5 Docs Path at Runtime ⚠️
**Status:** PRESENT RISK

**Finding:**
> "docs/HELP.md and docs/SHORTCUTS.md may not exist in packaged builds. If you depend on those files in the app bundle, put them in Qt resources or open a hosted version."

**Current Code Evidence:**
- [main_window.py:103,107](desktop_app/views/main_window.py#L103) - `lambda: self._open_document("docs/HELP.md")`
- [toolbar.py:71](desktop_app/views/main_window_parts/toolbar.py#L71) - `lambda: self._open_document("docs/HELP.md")`

**Analysis:**
- Relative paths work in development
- Will FAIL in packaged .app bundle unless docs are included
- Need resource bundling strategy

**Solutions:**

**Option A: Qt Resources (Best)**
```bash
# Create resources.qrc
# Add to build process
pyside6-rcc resources.qrc -o resources_rc.py
```

**Option B: Fallback to Web (Pragmatic)**
```python
def _open_document(self, doc_path: str) -> None:
    """Open local doc or fallback to web version."""
    local_path = os.path.join(os.path.dirname(__file__), "..", "..", doc_path)
    if os.path.exists(local_path):
        # Open local file
        QDesktopServices.openUrl(QUrl.fromLocalFile(local_path))
    else:
        # Fallback to online docs
        web_map = {
            "docs/HELP.md": "https://docs.signature-extractor.com/help",
            "docs/SHORTCUTS.md": "https://docs.signature-extractor.com/shortcuts",
        }
        url = web_map.get(doc_path, "https://docs.signature-extractor.com")
        QDesktopServices.openUrl(QUrl(url))
```

**Priority:** HIGH (critical for distribution)

---

#### 1.6 Platform Parity Drift ⚠️
**Status:** DESIGN DECISION NEEDED

**Finding:**
> "Tab document mode and movable tabs are gated only for macOS. If you want consistent interaction patterns, decide whether reordering tabs is a universal affordance or a platform-specific one."

**Current Code Evidence:**
- [main_window.py:58-60](desktop_app/views/main_window.py#L58-L60) - macOS-only tab features

**Analysis:**
- Document mode is macOS-specific visual style (good)
- Movable tabs are functional - why limit to macOS?

**Recommendation:**
```python
# Make movable tabs universal, keep document mode macOS-only
self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
self.tab_widget.setMovable(True)  # Universal
self.tab_widget.currentChanged.connect(self._on_tab_changed)

if sys.platform == "darwin":
    self.tab_widget.setDocumentMode(True)  # macOS-specific styling
```

**Priority:** LOW (cosmetic decision)

---

### 2. UX Upgrades That Will Pay Off

#### 2.1 Backend Health Indicator That Persists ⭐⭐⭐
**Status:** PARTIALLY IMPLEMENTED (transient only)

**Finding:**
> "Instead of a fleeting status message, show a small circular indicator in the status bar or toolbar that turns green when online, amber when probing, red when offline."

**Current Implementation:**
- [status.py:37-39](desktop_app/views/main_window_parts/status.py#L37-L39) - Backend status label exists!
- Shows "Backend: checking…" in yellow
- BUT: Not updated with health check results

**What We Have:**
```python
self.backend_status_label = QLabel("Backend: checking…")
self.backend_status_label.setStyleSheet("color: #a37f00; padding: 2px 8px;")
self.status_bar.addPermanentWidget(self.backend_status_label)
```

**What We Need:**
```python
def _update_backend_status(self, status: str, payload: dict) -> None:
    """Update persistent backend health indicator.

    Args:
        status: "checking", "online", "offline", "degraded"
        payload: Health check response or error dict
    """
    styles = {
        "checking": ("Backend: Starting check...", "#a37f00", "⏳"),
        "online": ("Backend: Online", "#2e7d32", "●"),
        "offline": ("Backend: Offline", "#c62828", "●"),
        "degraded": ("Backend: Version mismatch", "#f57c00", "⚠"),
    }

    text, color, icon = styles.get(status, styles["offline"])
    self.backend_status_label.setText(f"{icon} {text}")
    self.backend_status_label.setStyleSheet(f"color: {color}; padding: 2px 8px;")

    # Build tooltip
    if status == "online":
        backend_url = self.api_client.base_url
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        version = payload.get("version", "unknown")
        tooltip = f"Connected to {backend_url}\nLast check: {timestamp}\nVersion: {version}"
    elif status == "offline":
        error = payload.get("error", "Unknown error")
        tooltip = f"Cannot reach {self.api_client.base_url}\nError: {error}\nClick to troubleshoot"
    else:
        tooltip = text

    self.backend_status_label.setToolTip(tooltip)

    # Make clickable
    self.backend_status_label.mousePressEvent = lambda e: self._on_backend_status_clicked()

def _on_backend_status_clicked(self) -> None:
    """Handle click on backend status - open health page or troubleshooting."""
    if self._backend_online:
        self._open_url(f"{self.api_client.base_url}/health")
    else:
        self._open_document("docs/TROUBLESHOOTING.md")
```

**Priority:** HIGH (great UX improvement, infrastructure already exists)

---

#### 2.2 PDF Feature State That Is Obvious ⭐⭐
**Status:** NOT IMPLEMENTED

**Finding:**
> "Disable or gray out the PDF tab when dependencies are missing. Tooltip: what is missing and a one-click 'Open PDF setup guide.'"

**Current Implementation:**
- [main_window.py:68-75](desktop_app/views/main_window.py#L68-L75) - Shows status message about PDF availability
- Tab is always shown and enabled even if PDF unavailable

**What We Need:**
```python
# In _setup_pdf_ui or pdf.py
if not PDF_AVAILABLE:
    # Disable tab
    pdf_tab_index = self.tab_widget.indexOf(pdf_widget)
    self.tab_widget.setTabEnabled(pdf_tab_index, False)

    # Set tooltip explaining why
    missing_deps = []
    if PDF_IMPORT_ERROR:
        if "pypdfium2" in PDF_IMPORT_ERROR:
            missing_deps.append("pypdfium2")
        if "pikepdf" in PDF_IMPORT_ERROR:
            missing_deps.append("pikepdf")

    tooltip = (
        "PDF features are not available.\n\n"
        f"Missing dependencies: {', '.join(missing_deps)}\n\n"
        "Install with: pip install pypdfium2 pikepdf\n\n"
        "Click for setup guide"
    )
    self.tab_widget.setTabToolTip(pdf_tab_index, tooltip)

    # Make tab clickable to show setup guide
    # (requires custom tab bar widget)
```

**Priority:** MEDIUM (nice UX, but tab is visible either way)

---

#### 2.3 First-Run Onboarding ⭐⭐⭐
**Status:** NOT IMPLEMENTED

**Finding:**
> "On first run, show a light-weight sheet: how to import a signature, where files are saved, where logs live, and a 'Run connectivity check' button."

**Implementation Plan:**
```python
# Create desktop_app/views/onboarding_dialog.py
class OnboardingDialog(QDialog):
    """First-run onboarding sheet."""

    def __init__(self, api_client, session, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.session = session
        self.setWindowTitle("Welcome to Signature Extractor")
        self.setMinimumWidth(600)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Welcome to Signature Extractor")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Turn a photo or scan of your signature into clean, ready files. "
            "Optional PDF tools help you place and sign inside documents."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Quick start section
        # ... (implement based on ChatGPT's draft copy)

        # Buttons
        button_layout = QHBoxLayout()

        dont_show = QPushButton("Don't show this again")
        dont_show.clicked.connect(self._on_dont_show)
        button_layout.addWidget(dont_show)

        button_layout.addStretch()

        start_btn = QPushButton("Start Importing")
        start_btn.clicked.connect(self.accept)
        button_layout.addWidget(start_btn)

        layout.addLayout(button_layout)

    def _on_dont_show(self):
        # Save preference to QSettings
        from PySide6.QtCore import QSettings
        settings = QSettings()
        settings.setValue("onboarding/shown", True)
        self.reject()

# In main_window.py __init__
def __init__(self, ...):
    # ... existing code ...

    # Show onboarding on first run
    QTimer.singleShot(100, self._maybe_show_onboarding)

def _maybe_show_onboarding(self):
    from PySide6.QtCore import QSettings
    settings = QSettings()
    if not settings.value("onboarding/shown", False, type=bool):
        from desktop_app.views.onboarding_dialog import OnboardingDialog
        dialog = OnboardingDialog(self.api_client, self.session, self)
        dialog.exec()
```

**Priority:** MEDIUM (great for new users, but app is usable without it)

---

#### 2.4 License Affordances ⭐⭐
**Status:** PARTIALLY IMPLEMENTED

**Current Implementation:**
- [main_window.py:92-99](desktop_app/views/main_window.py#L92-L99) - License menu with Enter/Buy options

**Improvements Needed:**
1. Show current license status in menu
2. Disable "Enter License" when already activated
3. Add keyboard shortcuts
4. Show license email

**Implementation:**
```python
def _setup_menus(self) -> None:
    # ... existing code ...

    license_menu = menu_bar.addMenu("License")

    # Show current status as first item (non-clickable label)
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

        self.enter_license_action = QAction("Enter License...", self)
        self.enter_license_action.setShortcut("Cmd+Shift+L")
        self.enter_license_action.triggered.connect(self.on_enter_license)
        license_menu.addAction(self.enter_license_action)

        self.buy_license_action = QAction("Buy License...", self)
        self.buy_license_action.setShortcut("Cmd+Shift+B")
        self.buy_license_action.triggered.connect(self.on_buy_license)
        license_menu.addAction(self.buy_license_action)
```

**Priority:** MEDIUM (nice UX, but license system works)

---

#### 2.5 Keyboard Shortcuts and Discoverability ⭐⭐⭐
**Status:** PARTIALLY IMPLEMENTED

**Current Implementation:**
- [main_window.py:106-108](desktop_app/views/main_window.py#L106-L108) - Shortcuts menu item exists
- [docs/KEYBOARD_SHORTCUTS.md](docs/KEYBOARD_SHORTCUTS.md) - Documentation exists
- [toolbar.py:43,48,53](desktop_app/views/main_window_parts/toolbar.py#L43) - Some shortcuts defined

**What's Missing:**
1. Shortcuts not shown in menu labels
2. Missing common shortcuts (Close, Next/Prev tab, Toggle theme, Show logs)
3. Platform-specific chords not visible

**Implementation:**
```python
# Update menu labels to show shortcuts
def _setup_menus(self) -> None:
    # ... existing code ...

    help_menu = menu_bar.addMenu("Help")

    self.open_help_action = QAction("Help && Troubleshooting", self)
    self.open_help_action.setShortcut("F1")  # or Cmd+?
    self.open_help_action.triggered.connect(lambda: self._open_document("docs/HELP.md"))
    help_menu.addAction(self.open_help_action)

    self.open_shortcuts_action = QAction("Keyboard Shortcuts", self)
    self.open_shortcuts_action.setShortcut("Cmd+K")
    self.open_shortcuts_action.triggered.connect(lambda: self._open_document("docs/SHORTCUTS.md"))
    help_menu.addAction(self.open_shortcuts_action)

    # Add more shortcuts
    file_menu = menu_bar.addMenu("File")

    close_action = QAction("Close Window", self)
    close_action.setShortcut(QKeySequence.StandardKey.Close)  # Cmd+W
    close_action.triggered.connect(self.close)
    file_menu.addAction(close_action)

    view_menu = menu_bar.addMenu("View")

    next_tab_action = QAction("Next Tab", self)
    next_tab_action.setShortcut("Ctrl+Tab")
    next_tab_action.triggered.connect(self._next_tab)
    view_menu.addAction(next_tab_action)

    prev_tab_action = QAction("Previous Tab", self)
    prev_tab_action.setShortcut("Ctrl+Shift+Tab")
    prev_tab_action.triggered.connect(self._prev_tab)
    view_menu.addAction(prev_tab_action)

def _next_tab(self):
    idx = self.tab_widget.currentIndex()
    self.tab_widget.setCurrentIndex((idx + 1) % self.tab_widget.count())

def _prev_tab(self):
    idx = self.tab_widget.currentIndex()
    self.tab_widget.setCurrentIndex((idx - 1) % self.tab_widget.count())
```

**Priority:** MEDIUM (discoverability is important)

---

#### 2.6 Window State Persistence ⭐⭐
**Status:** NOT IMPLEMENTED

**Finding:**
> "Restore last window geometry, last active tab, and last opened folder. The tiny delight of 'it remembered' keeps users sticky."

**Implementation:**
```python
# In main_window.py
def __init__(self, ...):
    super().__init__(parent)
    # ... existing init ...

    # Restore window state
    self._restore_window_state()

def _restore_window_state(self):
    """Restore window geometry and tab from last session."""
    from PySide6.QtCore import QSettings
    settings = QSettings()

    # Restore geometry
    geometry = settings.value("window/geometry")
    if geometry:
        self.restoreGeometry(geometry)

    # Restore active tab
    last_tab = settings.value("window/activeTab", 0, type=int)
    if 0 <= last_tab < self.tab_widget.count():
        self.tab_widget.setCurrentIndex(last_tab)

def closeEvent(self, event):
    """Save window state before closing."""
    from PySide6.QtCore import QSettings
    settings = QSettings()

    settings.setValue("window/geometry", self.saveGeometry())
    settings.setValue("window/activeTab", self.tab_widget.currentIndex())

    super().closeEvent(event)
```

**Priority:** LOW (nice polish, but not critical)

---

#### 2.7 Error Microcopy ⭐
**Status:** NEEDS IMPROVEMENT

**Current Implementation:**
- [main_window.py:71-75](desktop_app/views/main_window.py#L71-L75) - Shows raw import error in status

**Improvement:**
```python
# In main_window.py __init__
if PDF_AVAILABLE:
    self.status_bar.showMessage("Ready - PDF features enabled", 2000)
else:
    # User-friendly message with action
    missing = []
    if PDF_IMPORT_ERROR and "pypdfium2" in str(PDF_IMPORT_ERROR):
        missing.append("pypdfium2")
    if PDF_IMPORT_ERROR and "pikepdf" in str(PDF_IMPORT_ERROR):
        missing.append("pikepdf")

    msg = f"Ready - PDF features unavailable (install {', '.join(missing) if missing else 'PDF libraries'})"
    self.status_bar.showMessage(msg, 4000)

    LOG.warning("PDF features disabled: %s", PDF_IMPORT_ERROR)

    # Add "Show Details" button to status bar
    details_btn = QPushButton("Setup Guide")
    details_btn.clicked.connect(lambda: self._open_document("docs/PDF_SETUP.md"))
    self.status_bar.addPermanentWidget(details_btn)
```

**Priority:** LOW (message is already acceptable)

---

#### 2.8 Drag and Drop Affordance ⭐⭐
**Status:** PARTIALLY IMPLEMENTED

**Finding:**
> "Let users drop a file anywhere on the window, not just inside a specific pane. Cursor change plus a subtle overlay text that says 'Drop to open.'"

**Current Implementation:**
- Drag & drop works in ImageView widgets
- Not global to main window

**Implementation:**
```python
# In main_window.py
def __init__(self, ...):
    super().__init__(parent)
    # ... existing init ...

    self.setAcceptDrops(True)

def dragEnterEvent(self, event):
    """Accept file drops anywhere on window."""
    if event.mimeData().hasUrls():
        event.acceptProposedAction()
        # Show overlay
        self._show_drop_overlay()

def dragLeaveEvent(self, event):
    """Hide drop overlay when drag leaves window."""
    self._hide_drop_overlay()

def dropEvent(self, event):
    """Handle dropped files."""
    self._hide_drop_overlay()

    urls = event.mimeData().urls()
    if urls:
        file_path = urls[0].toLocalFile()
        # Route to appropriate handler based on file type
        if file_path.lower().endswith('.pdf'):
            self.tab_widget.setCurrentIndex(self._pdf_tab_index)
            # Load PDF
        else:
            self.tab_widget.setCurrentIndex(self._extraction_tab_index)
            # Load image

        event.acceptProposedAction()

def _show_drop_overlay(self):
    """Show semi-transparent overlay with 'Drop to open' message."""
    # Implementation: Create QLabel overlay with styled text
    pass

def _hide_drop_overlay(self):
    """Hide drop overlay."""
    pass
```

**Priority:** MEDIUM (nice UX upgrade)

---

#### 2.9 Theming Toggle ⭐
**Status:** NOT IMPLEMENTED

**Finding:**
> "Add a quick theme toggle in the Help or View menu so people can flip without digging. Respect the OS setting by default, but make manual override obvious."

**Implementation:**
```python
# In theme.py or main_window.py
def _setup_menus(self):
    # ... existing code ...

    view_menu = menu_bar.addMenu("View")

    appearance_menu = view_menu.addMenu("Appearance")

    self.theme_auto_action = QAction("Automatic (Follow System)", self)
    self.theme_auto_action.setCheckable(True)
    self.theme_auto_action.triggered.connect(lambda: self._set_theme_mode("auto"))
    appearance_menu.addAction(self.theme_auto_action)

    self.theme_light_action = QAction("Light Mode", self)
    self.theme_light_action.setCheckable(True)
    self.theme_light_action.triggered.connect(lambda: self._set_theme_mode("light"))
    appearance_menu.addAction(self.theme_light_action)

    self.theme_dark_action = QAction("Dark Mode", self)
    self.theme_dark_action.setCheckable(True)
    self.theme_dark_action.triggered.connect(lambda: self._set_theme_mode("dark"))
    appearance_menu.addAction(self.theme_dark_action)

    # Set current mode
    self._update_theme_menu()

def _set_theme_mode(self, mode: str):
    """Set theme mode: auto, light, or dark."""
    from PySide6.QtCore import QSettings
    settings = QSettings()
    settings.setValue("appearance/mode", mode)

    self._update_theme_menu()
    self._apply_theme()  # Re-apply theme with new mode

def _update_theme_menu(self):
    """Update theme menu checkmarks."""
    from PySide6.QtCore import QSettings
    settings = QSettings()
    mode = settings.value("appearance/mode", "auto", type=str)

    self.theme_auto_action.setChecked(mode == "auto")
    self.theme_light_action.setChecked(mode == "light")
    self.theme_dark_action.setChecked(mode == "dark")
```

**Priority:** LOW (system detection works well)

---

### 3. Cross-Platform and Accessibility

#### 3.1 High DPI and Icons ⚠️
**Status:** NEEDS VERIFICATION

**Finding:**
> "Ensure get_icon('file') resolves to an SVG or multiple DPIs. Pixellated icons hurt perceived quality."

**Current Code:**
- [resources/icons.py](desktop_app/resources/icons.py) - Need to check implementation

**Action:** Verify icon implementation, ensure SVG or @2x support

**Priority:** MEDIUM (quality matters)

---

#### 3.2 Focus Visibility ⚠️
**Status:** NEEDS TESTING

**Finding:**
> "Confirm focus rings are visible in dark theme, especially on tabs and menu items."

**Action:** Manual testing in dark mode

**Priority:** MEDIUM (accessibility)

---

#### 3.3 Screen Reader Labels ⚠️
**Status:** NOT IMPLEMENTED

**Finding:**
> "Provide accessibleName for the tab widget and top-level actions so VoiceOver and NVDA announce sensible names."

**Implementation:**
```python
# In main_window.py
self.tab_widget.setAccessibleName("Main workflow tabs")

# In extraction.py
self.src_view.setAccessibleName("Source image pane")
self.preview_view.setAccessibleName("Preview pane")
self.res_view.setAccessibleName("Result image pane")

# In toolbar.py
open_action.setAccessibleName("Open image or PDF")
export_action.setAccessibleName("Export processed image")
```

**Priority:** HIGH (accessibility is important)

---

#### 3.4 Contrast ⚠️
**Status:** NEEDS AUDIT

**Finding:**
> "Dark mode palettes often miss WCAG contrast on disabled states. Audit disabled text and badge tones."

**Action:** Contrast audit with tools like WebAIM

**Priority:** MEDIUM (accessibility)

---

### 4. Small Polish Items

#### 4.1 Tab Overflow
**Status:** NOT APPLICABLE (only 2 tabs)

#### 4.2 Consistent Copy ⚠️
**Status:** NEEDS REVIEW

**Finding:**
> "Use a consistent style for menu nouns and verbs. Example: 'Help and Troubleshooting' vs 'Keyboard Shortcuts'. Either use sentence case everywhere or Title Case everywhere."

**Current:**
- "Help & Troubleshooting" (Title Case with &)
- "Keyboard Shortcuts" (Title Case)
- "Open Backend Health" (Title Case)

**Recommendation:** Standardize to Title Case (already mostly there)

**Priority:** LOW (cosmetic)

---

#### 4.3 Loading Feel
**Status:** PARTIALLY ADDRESSED

**Current:**
- Backend status shows "checking…"
- Could add spinner

**Implementation:**
```python
# In status.py
def _update_backend_status(self, status: str, payload: dict):
    if status == "checking":
        # Create animated spinner
        self.backend_status_label.setText("⏳ Backend: Checking...")
        # Or use QMovie for animated GIF
```

**Priority:** LOW (nice polish)

---

## Priority Roadmap

### Immediate (This Week) - Critical Fixes

1. **✅ Async Health Check** - HIGH PRIORITY
   - Prevents UI freezes
   - Implements exponential backoff
   - File: Create `desktop_app/views/main_window_parts/health_mixin.py`
   - Estimated time: 2-3 hours

2. **✅ Persistent Backend Health Indicator** - HIGH PRIORITY
   - Infrastructure exists, just needs wiring
   - Great UX improvement
   - File: Update `status.py` and `extraction.py`
   - Estimated time: 1-2 hours

3. **✅ Fix Hardcoded Health URL** - MEDIUM PRIORITY
   - Easy fix
   - File: `main_window.py:113`
   - Estimated time: 5 minutes

4. **✅ Docs Path Fallback** - HIGH PRIORITY
   - Critical for distribution
   - File: Create `_open_document` fallback in `native_dialogs.py`
   - Estimated time: 1 hour

5. **✅ Accessibility Names** - HIGH PRIORITY
   - Important for screen readers
   - Files: `main_window.py`, `extraction.py`, `toolbar.py`
   - Estimated time: 30 minutes

### Short-Term (Next 2 Weeks) - Major Features

6. **📋 First-Run Onboarding** - MEDIUM PRIORITY
   - Great for new users
   - File: Create `desktop_app/views/onboarding_dialog.py`
   - Estimated time: 4-6 hours

7. **📋 Enhanced License UI** - MEDIUM PRIORITY
   - Better status display
   - File: Update `main_window.py` menu setup
   - Estimated time: 2-3 hours

8. **📋 Improved Keyboard Shortcuts** - MEDIUM PRIORITY
   - Add missing shortcuts
   - Show in menus
   - Files: `main_window.py`, `toolbar.py`
   - Estimated time: 2 hours

9. **📋 Global Drag & Drop** - MEDIUM PRIORITY
   - Better file opening UX
   - File: Update `main_window.py`
   - Estimated time: 3-4 hours

### Long-Term (Next Month) - Polish

10. **📋 Window State Persistence** - LOW PRIORITY
    - QSettings integration
    - File: `main_window.py`
    - Estimated time: 1 hour

11. **📋 Theme Toggle Menu** - LOW PRIORITY
    - Manual override option
    - File: `theme.py` or `main_window.py`
    - Estimated time: 2 hours

12. **📋 Mixin Smoke Tests** - MEDIUM PRIORITY
    - Prevent runtime failures
    - File: Create `tests/test_main_window.py`
    - Estimated time: 2 hours

13. **📋 Contrast Audit** - MEDIUM PRIORITY
    - WCAG compliance
    - Files: All styling
    - Estimated time: 3-4 hours

14. **📋 Icon Quality Verification** - MEDIUM PRIORITY
    - Ensure HiDPI support
    - File: `resources/icons.py`
    - Estimated time: 2-3 hours

---

## ChatGPT Draft Copy Integration

The review included comprehensive UX copy drafts for:

### ✅ Status Messages
- Backend health states (checking, online, offline, degraded)
- PDF capability states
- Licensing states
- Import/export flow messages
- Long-running task feedback

**Action:** Create `desktop_app/resources/copy.py` with all message templates

### ✅ First-Run Onboarding Sheet
- Complete structure provided
- Quick start section
- Connectivity section
- PDF setup section
- File location section

**Action:** Implement in `OnboardingDialog` class

### ✅ Diagnostic Summary Format
- Structured copy-paste format
- Environment info
- Backend status
- PDF availability
- License state
- Paths
- Recent action

**Action:** Create `desktop_app/utils/diagnostics.py` with formatter

---

## Documentation Tasks

### Create New Docs

1. **TROUBLESHOOTING.md** - Backend connectivity guide
2. **PDF_SETUP.md** - Installing PDF dependencies
3. **COPY_GUIDELINES.md** - UX copy standards from ChatGPT review

### Update Existing Docs

1. **HELP.md** - Add new features as implemented
2. **SHORTCUTS.md** - Keep in sync with actual shortcuts
3. **IMPLEMENTATION_PLAN.md** - Track progress

---

## Testing Checklist

Before marking items complete:

### Visual QA
- [ ] Backend indicator visible and updates correctly
- [ ] All tooltips accurate and helpful
- [ ] Focus rings visible in light and dark modes
- [ ] Icons crisp at all display scales
- [ ] Disabled states have proper contrast

### Functional QA
- [ ] Health checks don't freeze UI
- [ ] All keyboard shortcuts work
- [ ] Drag & drop works from Finder
- [ ] Docs open in packaged build
- [ ] Window state persists across sessions
- [ ] Tab enable/disable works correctly

### Accessibility QA
- [ ] Screen reader announces all major elements
- [ ] Keyboard navigation works everywhere
- [ ] Color contrast meets WCAG AA
- [ ] Focus order is logical

### Cross-Platform QA
- [ ] macOS: Native feel maintained
- [ ] macOS: Menu bar shows correct app name
- [ ] macOS: Toolbar integrated with title bar
- [ ] All features work on non-macOS (if applicable)

---

## Next Steps

1. ✅ Review this analysis with user
2. 📋 Get approval on priority order
3. 📋 Start with "Immediate" tier items
4. 📋 Create feature branches for each major item
5. 📋 Test thoroughly before marking complete
6. 📋 Update documentation as features land
7. 📋 Track progress in `IMPLEMENTATION_STATUS_VS_DOCS.md`

---

## Key Takeaways

**Strengths of Current Codebase:**
- Clean mixin architecture
- Good macOS integration foundation
- Status bar infrastructure in place
- Theme detection working well

**Areas Needing Attention:**
- Async operations (health checks)
- Distribution readiness (docs, resources)
- Accessibility (screen reader labels, contrast)
- UX polish (onboarding, persistent indicators)
- Copy quality (use ChatGPT's drafts)

**Biggest Wins Available:**
1. Async health check → prevents freezes
2. Persistent health indicator → professional feel
3. First-run onboarding → reduces friction
4. Accessibility labels → inclusive app
5. Docs fallback → distribution-ready

---

**Analysis completed:** November 2, 2025
**Reviewed by:** Claude (Sonnet 4.5)
**Source:** ChatGPT comprehensive UI/UX review
**Status:** Ready for implementation planning
