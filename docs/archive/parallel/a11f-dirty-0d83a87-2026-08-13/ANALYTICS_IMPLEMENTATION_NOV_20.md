# Analytics Implementation Documentation - Nov 20, 2025

## Overview

This document details the implementation of advanced analytics for the SignKit landing page A/B test. The setup includes Google Analytics 4 (GA4) for quantitative metrics and Microsoft Clarity for qualitative user behavior analysis.

## Key Features

1.  **A/B Testing**: Tracking 4 distinct landing page variants.
2.  **Internal Traffic Exclusion**: Robust cookie-based exclusion for team devices.
3.  **Enhanced Event Tracking**: Custom events for checkout intent, scroll depth, and purchases.
4.  **Redundancy Removal**: Centralized logic in `analytics.js` to prevent duplicate firing.

## Architecture & Migration Analysis

### Previous State (Pre-Nov 20)

- **Tracking**: Basic GA4 page views only.
- **Implementation**: Scattered inline scripts in each HTML file.
- **Issues**:
  - **Redundancy**: Scroll tracking logic was duplicated in `root.html` and `purchase.html`.
  - **Inconsistency**: No unified way to track which variant a user was seeing.
  - **Pollution**: Internal traffic (developer testing) was mixing with real user data.
  - **Maintenance**: Changing a tracking ID required editing 4+ files.

### Current State (Post-Nov 20)

- **Tracking**: Full A/B test suite with granular events (`variant_view`, `checkout_intent`).
- **Implementation**:
  **Centralized**: Core logic moved to `web/live/js/analytics.js`.
  - **Configurable**: HTML files only set configuration (Variant ID) and import the logic.
  - **Consistency**: `buy.html` now imports `analytics.js` so CTA and external link tracking behave consistently across variants.
- **Improvements**:
  - **Clean Data**: Cookie-based internal traffic exclusion ensures 100% clean metrics.
  - **Scalable**: Adding a new variant only requires copying the header script block.
  - **Rich Context**: Every event now carries the `variant` parameter automatically.

### Key Decisions & "Why"

1.  **Cookie-based Exclusion vs. IP Filtering**:

    - _Why_: IP filtering is unreliable with dynamic IPs, VPNs, and mobile networks.
    - _Decision_: Use a persistent cookie (`ga_internal=true`) set via a secret query param (`?internal=1`). This follows the user/device, not the network.

2.  **Centralized `analytics.js`**:

    - _Why_: `root.html` and `purchase.html` had identical scroll tracking code.
    - _Decision_: Refactored into a single file. The HTML now just sets `gtag('config', ..., { 'variant': 'xyz' })`, and the JS file reads that context.

3.  **`variant_view` Event**:
    - _Why_: Standard `page_view` is hard to segment by A/B variant in standard GA4 reports without custom dimensions.
    - _Decision_: Fire a dedicated event that explicitly names the variant (`root`, `buy`, `gum`, `purchase`) for easy funnel visualization.

## Tools & IDs

- **Google Analytics 4 (GA4)**: `G-PCJDGBMRRN`
- **Microsoft Clarity**: `u8zyh41jr0`

## Implementation Details

### 1. Internal Traffic Exclusion

We implemented a cookie-based override to exclude internal traffic reliably, bypassing IP rotation issues.

- **Mechanism**:

  1.  Visit any variant with `?internal=1` (e.g., `signkit.work/?internal=1`).
  2.  This sets a cookie: `ga_internal=true` (valid for 1 year).
  3.  On every page load, if this cookie is present, we execute:
      ```javascript
      gtag('set', 'user_properties', { traffic_type: 'internal' });
      ```
  4.  **GA4 Configuration**: A Data Filter in GA4 Admin excludes traffic with `traffic_type = 'internal'`.

- **Code Location**: In the `<head>` of `index.html`, `root.html`, `buy.html`, `gum.html`, and `purchase.html`, immediately before the `gtag('config')` call.

### 2. A/B Testing Variants

We are testing 4 variants to determine the optimal conversion flow.

| Variant      | URL Path                      | Description                                 |
| :----------- | :---------------------------- | :------------------------------------------ |
| **Root**     | `/` (`root.html`)             | The control version (Neo-brutalist design). |
| **Buy**      | `/buy` (`buy.html`)           | Direct embedded Gumroad checkout.           |
| **Gum**      | `/gum` (`gum.html`)           | Auto-redirect to Gumroad product page.      |
| **Purchase** | `/purchase` (`purchase.html`) | Claude v2 design with "Get Started" CTAs.   |

- **Tracking**:
  - Each file sets a global `variant` parameter in `gtag('config')`.
  - A `variant_view` event is fired on load with the specific variant name.

### 3. Event Tracking

#### `variant_view`

- **Trigger**: Page load.
- **Parameters**: `variant` (e.g., 'root', 'buy').
- **Purpose**: To count sessions per variant accurately.

#### `checkout_intent`

- **Trigger**: Clicking any "Get Started", "Buy", or Gumroad link.
- **Parameters**: `location` (variant name), `event_label` (button text).
- **Implementation**:
  - **Root**: Handled by `analytics.js` (detects `a[href*="gumroad"]` and `.btn-primary`).
  - **Purchase**: Handled by `analytics.js` (detects `data-href` attributes on buttons).
  - **Gum**: Implicit (the page itself is a redirect to checkout).

#### `scroll_depth`

- **Trigger**: Scrolling to 25%, 50%, 75%, 90%.
- **Parameters**: `percent` (numeric), `depth` (string '25%'), `variant`.
- **Implementation**: Centralized in `web/live/js/analytics.js`.

#### `purchase`

- **Trigger**: User lands on `purchase.html` (or root) with `?order=success`.
- **Parameters**: `transaction_id`, `value` (29.00), `currency` (USD).
- **Implementation**: Inline script in `purchase.html` checks URL parameters.

### 4. Code Structure & Cleanup

- **`web/live/js/analytics.js`**:

  - Contains shared logic for Scroll Depth, Bot Detection, and CTA clicking.
  - Refactored to accept the global `variant` parameter set in the HTML.
  - Renamed `purchase_intent` to `checkout_intent` for consistency.

- **`web/live/js/main.js`**:

  - Updated CTA button handlers to respect `data-href` attributes.
  - Removed conflicting "alert" placeholders.

- **HTML Files**:
  - Removed redundant inline scroll tracking scripts (index.html now imports `analytics.js`, replacing its previous inline handlers).
  - Added Microsoft Clarity script to `<head>`.

## How to Verify

1.  **Exclude Yourself**:

    - Go to `http://localhost:8000/?internal=1` (or your deployed URL).
    - Check browser cookies for `ga_internal=true`.
    - Verify in GA4 DebugView that `traffic_type` is set to `internal`.

2.  **Test Events**:

    - Open `purchase.html`.
    - Scroll down -> Check for `scroll_depth` events.
    - Click "Get Started" -> Check for `checkout_intent`.
    - Append `?order=success&sale_id=123` -> Check for `purchase` event.

3.  **Check Clarity**:
    - Log in to Microsoft Clarity.
    - Verify that sessions are being recorded (note: Clarity may have a slight delay).
