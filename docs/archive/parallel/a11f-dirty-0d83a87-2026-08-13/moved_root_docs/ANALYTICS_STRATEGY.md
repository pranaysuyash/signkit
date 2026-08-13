# In-App Analytics Strategy for SignKit

## 1. The Verdict: YES (With Conditions)

**Recommendation:** You **should** implement in-app analytics, but it must be **Privacy-First** and **Opt-In/Transparent**.

### Why? (The Pros)
1.  **Product Validation:** You are charging $29. You need to know *what* features justify that price. Are users using the PDF signer? or just extracting signatures?
2.  **Error Discovery:** In a desktop app, you rarely see crashes unless users report them. Analytics can auto-report exceptions (e.g., "OpenCV failed to load image").
3.  **Performance Tuning:** You can track how long extraction takes on different hardware.
4.  **Conversion Tracking:** If you have a "Trial" mode, you need to know where users drop off before buying.

### Why Not? (The Cons & Risks)
1.  **Privacy Brand:** Your USP is "Local-First / Privacy". Sending data home contradicts this if not explained well.
2.  **Trust:** If a user thinks you are uploading their signature, they will refund immediately.
3.  **Offline Complexity:** Since the app works offline, you need a system to queue events and send them later.

---

## 2. WHAT to Track (The "Safe" List)

We strictly separate **Usage Data** from **User Content**.

### ✅ DO Track (Events)
*   **Lifecycle:** `App Launched`, `App Closed`, `Version Updated`.
*   **Features:**
    *   `Extraction Performed` (Params: Threshold value, Color used).
    *   `PDF Loaded` (Params: Page count).
    *   `Signature Placed` (Params: Count).
    *   `Exported Image` (Params: Format).
*   **Performance:** `Extraction Duration (ms)`, `Startup Time (ms)`.
*   **Errors:** `Crash/Exception` (Type, Stack trace, Module).
*   **System:** OS Version, Screen Resolution (for responsive UI debugging).

### ❌ NEVER Track
*   **Image Content:** Never upload the signature or document.
*   **File Paths:** `/Users/pranay/Documents/Contract.pdf` reveals PII.
*   **Input Values:** Never track text typed into fields (unless search/filter).

---

## 3. HOW to Implement

### Architecture: "Store-and-Forward"
Since the app is offline-first, we cannot just fire HTTP requests.

1.  **Local Buffer:**
    *   Create a simple SQLite table `analytics_queue` in the user's data dir.
    *   When an event happens, write it to the DB.
2.  **Background Worker:**
    *   A `QThread` runs every X minutes (or on app close).
    *   Checks for internet connection.
    *   Batches events (JSON) and POSTs them to your server.
    *   On 200 OK, delete from DB.

### Technology Stack
*   **Client (Desktop):**
    *   Build a custom `TelemetryClient` class in Python.
    *   Use `platform` module for system info.
    *   Use `sqlite3` for buffering.
*   **Server (Collector):**
    *   **Option A (Self-Hosted - Recommended):** A simple Cloudflare Worker or FastAPI endpoint that inserts into a ClickHouse/Postgres DB.
    *   **Option B (SaaS):** PostHog (Open Source, Privacy-friendly). You can proxy it through your own domain (e.g., `telemetry.signkit.work`) to avoid ad-blockers and look professional.

### Privacy Implementation (The "Trust" UI)
1.  **Onboarding Dialog:**
    *   Add a checkbox: `[x] Help improve SignKit by sending anonymous usage data.`
    *   Add a link: "See what we collect" (Shows a sample JSON payload).
2.  **Settings:**
    *   Allow toggling this off at any time.

---

## 4. Implementation Plan

### Phase 1: The Infrastructure
1.  Create `desktop_app/analytics/` module.
2.  Implement `TelemetryManager` with `log_event(name, props)` method.
3.  Implement SQLite buffering.

### Phase 2: Instrumentation
1.  Hook into `MainWindow.__init__` -> `log_event("App Started")`.
2.  Hook into `SignatureExtractor.process_selection` -> `log_event("Signature Extracted", {"threshold": 120})`.
3.  Hook into `sys.excepthook` -> Catch unhandled exceptions and log them.

### Phase 3: The Collector
1.  Set up a PostHog instance (easiest to start).
2.  Configure the desktop app with the Project API Key.

---

## Summary
**Do it.** But make it "Anonymous Usage Statistics", not "Tracking". The insight you gain into *how* people use the tool is worth the small engineering effort, as long as you respect the privacy boundary.
