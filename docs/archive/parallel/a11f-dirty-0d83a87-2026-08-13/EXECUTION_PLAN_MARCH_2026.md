# SIGNKIT — EXECUTION PLAN

**Created:** March 24, 2026
**Source:** Full Product Audit (docs/FULL_PRODUCT_AUDIT_MARCH_2026.md)
**Current Grade:** C+
**Target Grade (90 days):** B+
**Ceiling:** A-

---

## A++ DEFINITION FOR SIGNKIT

An A++ SignKit is:
- **One headline, one CTA, zero ambiguity.** User understands in 3 seconds what it does and why it's different.
- **Free trial that proves extraction quality** before asking for payment. User sees the "aha" moment in under 30 seconds.
- **Extraction quality that handles messy inputs** — shadows, colored paper, phone photos. Not just clean scans.
- **Connected workflow** — extract → review → place on PDF → save, without switching mental models.
- **Real trust signals** — verified privacy claims, real testimonials, clean legal docs, no fake numbers.
- **Rich signature library** — search, tags, favorites, recent, "quick sign" from library.
- **Premium feel** — smooth animations, instant preview, thoughtful empty states, keyboard shortcuts for power users.
- **Growth engine** — demo video shareable on social, comparison pages ranking on SEO, referral loop built in.
- **Clear monetization** — free tier proves value, $29 one-time converts impulse buyers, $79 pro captures power users.

---

## DEDUPLICATED ISSUE REGISTER

### P0 — FIX THIS WEEK (blocks revenue or destroys trust)

| ID | Title | Category | Current Problem | Root Cause Hypothesis | User Impact | Business Impact | Recommended Fix | Effort | Acceptance Criteria | Success Metric |
|----|-------|----------|----------------|----------------------|-------------|-----------------|-----------------|--------|--------------------|--------------------|
| P0-01 | Broken CTA URLs in web/live/index.html | Conversion | All CTA buttons link to `https://gumroad.com/l/YOUR_PRODUCT_ID` — a placeholder that does nothing | Multiple landing page variants created, deploy drift, never verified the deployed version | Clicking "Get SignKit" does nothing. User leaves. | 100% conversion loss for anyone hitting this page | Replace `YOUR_PRODUCT_ID` with `pranaysuyash.gumroad.com/l/signkit-v1` in web/live/index.html | 10 min | All CTA buttons navigate to working Gumroad checkout | Click-through rate > 0 on CTAs |
| P0-02 | Fabricated social proof on landing page | Trust | "1,200+ Happy Customers", "12,847 Signatures Extracted", "4.8/5 Rating" displayed as real on purchase.html | Template placeholder never replaced with real data | User who notices feels被骗. Competitor who notices has ammunition. | Reputational risk. Legal risk (FTC guidelines on fake testimonials). | Remove the social proof strip entirely until real numbers exist. Replace with "Launching soon — be an early adopter" or remove section. | 30 min | No fake numbers visible anywhere on any landing page variant | Zero fabricated claims across all deployed pages |
| P0-03 | Legal documents contain unfilled placeholders | Trust / Legal | Terms of Service and EULA have `[Your State/Country]`, `[Your City/State]`, `[Your Business Address]` | Templates copied, never completed | User who reads ToS before buying will assume scam or amateur operation | Legal unenforceability. Trust destruction. | Fill in all placeholders with actual business information. If entity is "Signature Tools LLC", confirm and use consistently. | 1 hr | All `[placeholder]` text replaced with real values in legal/TERMS_OF_SERVICE.md, legal/EULA.md | Zero placeholder text in any legal document |
| P0-04 | main.js has syntax error — missing closing brace | Reliability | web/live/js/main.js line 405: file ends with `expected }` | Code was partially edited, never tested | JavaScript on purchase.html landing page fails silently. CTA click handlers may not fire. Analytics may not fire. | Broken interactive elements on the best landing page. Analytics data loss. | Add missing `}` to close the function/block. Test that all CTA buttons fire click handlers. | 10 min | main.js passes syntax check. All CTA buttons on purchase.html are clickable and tracked. | Zero JS console errors on page load |
| P0-05 | Copyright year says 2025 | Credibility | Footer shows "© 2025 SignKit" in March 2026 | Never updated after new year | Signals the product is abandoned or unmaintained | Lowers trust for anyone checking freshness | Change to "© 2025–2026 SignKit" or "© 2026 SignKit" across all landing page variants | 5 min | All footer copyright references show 2026 | — |
| P0-06 | Onboarding dialog says "Signature Extractor" | Consistency | desktop_app/views/onboarding_dialog.py title is "Welcome to Signature Extractor" | Legacy name from before rebrand to SignKit | User confusion — is this SignKit or Signature Extractor? | Weakens brand identity | Change title to "Welcome to SignKit" | 5 min | Onboarding dialog title matches product name | — |
| P0-07 | "HIPAA Compliant" badge on purchase.html | Legal Risk | Footer displays "HIPAA Compliant" badge without certification | Marketing aspiration, not verified claim | Healthcare user relies on this, discovers it's unsubstantiated, reports to HHS | FTC enforcement risk. Healthcare compliance fraud liability. | Remove the badge immediately. Replace with "Privacy-First Design" or "No Cloud Storage" which are factual claims. | 5 min | No compliance certification claims without documentation | Zero unsubstantiated compliance claims |
| P0-08 | Privacy policy email domain mismatch | Trust | Top of privacy policy: `privacy@signatureextractor.app`. Bottom and other docs: `support@signkit.work` | Multiple domain names used during development | User trying to contact privacy@ gets bounced or confused | GDPR requires a functional privacy contact email | Unify to `support@signkit.work` everywhere. Set up email forwarding if needed. | 15 min | Single consistent contact email across all documents | — |
| P0-09 | "Coming soon" testimonials section | Trust | purchase.html has "Coming soon. Early customer quotes will be added here." | Section built as placeholder before launch | Signals "nobody has used this yet" — actively hurts credibility | Reduces conversion for users who scroll past hero | Remove the testimonials section entirely. Add it back only when real quotes exist. | 5 min | No placeholder testimonials visible | — |

### P1 — FIX WITHIN 2 WEEKS (major conversion/trust blockers)

| ID | Title | Category | Current Problem | Root Cause Hypothesis | User Impact | Business Impact | Recommended Fix | Effort | Acceptance Criteria | Success Metric |
|----|-------|----------|----------------|----------------------|-------------|-----------------|-----------------|--------|--------------------|--------------------|
| P1-01 | No free trial or demo mode | Conversion | Product requires $29 payment before user can see extraction quality | Anti-SaaS ideology went too far; no risk-reversal beyond refund | User cannot evaluate quality → won't pay → leaves | Estimated 60-80% conversion loss at checkout | Implement trial mode: 3 free PNG exports, then paywall. Or build a web-based demo that shows extraction on sample images. | 1-2 weeks | New user can extract and export 3 signatures before seeing upgrade prompt | Trial-to-paid conversion rate measurable |
| P1-02 | No demo video | Conversion | YouTube embed references `YOUR_VIDEO_ID`, is hidden | Never recorded | User cannot evaluate UX quality, speed, or output before paying | Landing page does 40% of selling instead of 100% | Record 30-60 second screen capture showing: upload photo → adjust threshold → clean PNG export → place on PDF → save | 2-3 hrs | Embedded video on landing page, playable, shows real product | Video play rate, watch completion rate |
| P1-03 | No before/after visual proof | Conversion | Landing page shows static screenshots, no extraction quality demo | Never created | User asks "does extraction actually work on messy signatures?" and gets no answer | Unanswered question = abandoned visit | Create animated GIF or side-by-side showing: photo of signature on lined paper → clean transparent PNG | 1-2 hrs | Before/after visual on landing page above the fold or in hero section | Scroll depth past hero increases |
| P1-04 | Landing page fragment confusion | UX / Trust | 5+ variants: index.html, root.html, purchase.html, buy.html, gum.html, web/live/index.html | A/B testing setup created variants, never consolidated | Unclear which page users actually see. Deploy status unclear. | Marketing spend wasted on broken variants. Analytics fragmented. | Audit Cloudflare Pages deploy. Pick ONE canonical page (recommend: fix and use purchase.html). Redirect all other paths to canonical. | 3-5 hrs | Single canonical landing page. All other URLs redirect (301). Analytics unified. | Single page tracking all traffic |
| P1-05 | "View product details" button goes to same URL as primary CTA | UX | Ghost button and primary button both link to Gumroad | Designed as "learn more" but never built a product detail page | User clicks "View product details" expecting product info, gets checkout. Feels欺骗. | Wastes a CTA slot. Confuses user intent (exploring vs buying). | Either: (a) build a simple product detail page with feature deep-dive, or (b) remove the ghost button entirely and let the primary CTA breathe. | 1-3 hrs | Ghost button either goes to a real product page or is removed | — |
| P1-06 | analytics.js `var` declaration issues | Code Quality | Multiple `var` declarations inside blocks (lines 137, 171, 204, 255, 268) | Quick implementation, no linting | Works in browsers but fails strict mode / linting | Technical debt accumulation | Refactor `var` to `const`/`let` at proper scope. Add ESLint config. | 30 min | Zero lint errors in analytics.js | — |
| P1-07 | EULA references inconsistent legal entity | Trust / Legal | EULA says "Signature Tools LLC". No other document confirms this entity exists. | Template artifact or real entity not documented elsewhere | User wonders if this is a real company | Legal enforceability of EULA depends on correct entity | Confirm legal entity. Use consistently in all legal docs, footer, and about section. | 30 min | Single legal entity name across all documents | — |
| P1-08 | No sample image on first launch | Activation | User opens app → empty extraction view → must find their own image to test | Never implemented | Time to "aha" moment is dependent on user having a signature image ready | Delayed activation increases buyer's remorse | Auto-load a bundled sample signature image in extraction view on first launch. User sees threshold slider working immediately. | 2-3 hrs | First-run shows sample image with working extraction preview | Time to first extraction decreases |
| P1-09 | Extraction and PDF signing are disconnected | UX / Workflow | User extracts signature in tab 1 → must switch to tab 3 (PDF Signer) → must find signature in vault → manually place | Features built as separate modules, never integrated | User expects "extract then sign" as one flow, gets two separate tools | Friction reduces both extraction and signing usage | Add "Sign a PDF with this signature" button in extraction result view. Opens PDF picker → places signature. | 3-5 days | User can go from extraction result to signed PDF without switching tabs manually | Cross-feature usage rate increases |
| P1-10 | Product naming inconsistency | Brand | "SignKit" on landing page, "Signature Extractor" in onboarding, strategy docs, code. "Signature Tools LLC" in EULA. | Product renamed during development, not all references updated | User confusion about what the product is actually called | Weakens brand recognition and recall | Audit all files. Unify to "SignKit" in all user-facing text. Keep "Signature Extractor" only in internal/code contexts if needed. | 2-3 hrs | All user-facing text says "SignKit". Zero "Signature Extractor" references in UI, docs, landing pages. | — |

### P2 — FIX WITHIN 30 DAYS (structural improvements)

| ID | Title | Category | Current Problem | Root Cause Hypothesis | User Impact | Business Impact | Recommended Fix | Effort | Acceptance Criteria | Success Metric |
|----|-------|----------|----------------|----------------------|-------------|-----------------|-----------------|--------|--------------------|--------------------|
| P2-01 | No auto-detect signature region | Feature | User must manually select/zoom to find signature area | Feature not built; manual selection was MVP | Tedious for multi-page documents or large scans | Limits perceived quality of extraction | Implement basic contour detection to auto-highlight probable signature region on image load | 1 week | On image load, a selection rectangle appears around the detected signature area | Auto-detect accuracy > 80% on test set |
| P2-02 | Signature library is basic | Feature / Retention | Vault tab shows list with preview. No search, no tags, no sorting, no favorites. | MVP-level implementation | Power users with 10+ signatures can't find what they need | Weakens retention driver (library = lock-in) | Add search bar, tag system, sort by name/date/usage, favorite toggle | 1 week | User can search, tag, sort, and favorite signatures in vault | Vault usage (signatures stored) increases |
| P2-03 | No keyboard shortcuts documented | UX | Keyboard shortcuts exist in code but are not discoverable | Implemented but not surfaced | Power users can't use them; casual users don't know they exist | Missed retention/efficiency opportunity | Add keyboard shortcut cheatsheet (Help menu + `?` shortcut). Show tooltips with shortcut hints. | 3-4 days | Help → Keyboard Shortcuts menu exists. Common shortcuts have tooltip hints. | Shortcut usage measurable |
| P2-04 | Neo-brutalist design doesn't convey trust | Brand / Conversion | Landing page uses trendy brutalist style with heavy shadows and rotated shapes | Design trend choice, not brand-aligned choice | Privacy-conscious user expects clean, professional, trustworthy — gets edgy, experimental | May deter professional/regulated users who are the ideal target | Redesign landing page with clean, professional aesthetic. White background, clear typography, subtle shadows. Let the product screenshots do the talking. | 1-2 weeks | Landing page conveys "professional, trustworthy, precise" not "trendy, experimental" | Bounce rate decreases, time on page increases |
| P2-05 | No loading/processing feedback | UX | When processing large images, no visible progress indicator | Not implemented | User thinks app has frozen on large files | Perceived performance issue, potential support tickets | Add subtle progress indicator during extraction processing. Show "Processing..." with estimated time for files > 5MB. | 2-3 days | Processing state visible for all extraction operations > 500ms | Perceived speed rating improves |
| P2-06 | 3622-line extraction.py monolith | Tech Debt | Single file contains entire extraction UI, logic, and controls | Features accumulated without refactoring | Slows development. Bug surface area. Merge conflicts. | Engineering velocity degrades over time | Split into: extraction_view.py (UI), extraction_controls.py (sliders/inputs), extraction_preview.py (image display), extraction_export.py (export dialog) | 1-2 weeks | No file > 800 lines. Clear module boundaries. | Development velocity on extraction features |
| P2-07 | _create_button duplicated across 4+ files | Tech Debt | Button factory function copy-pasted with different defaults in extraction.py, pdf.py, onboarding_dialog.py, vault_tab.py | Quick implementation, no shared module | Visual inconsistency — different tabs have different button styles | UX inconsistency, maintenance burden | Extract to desktop_app/widgets/button_factory.py. Single source of truth. | 3-4 hrs | One import, one function. All tabs use same factory. | Zero duplicate button factory functions |
| P2-08 | No empty state guidance | UX | Extraction tab shows blank area with no guidance on what to do | Not designed | First-time user stares at empty screen, confused | Increases time to first action | Add friendly empty state: illustration + "Drop a document here or click to upload" + "Try with sample image" link | 3-4 hrs | Empty state visible when no image is loaded. "Try sample" button loads demo image. | Time to first upload decreases |
| P2-09 | No offline verification proof | Trust | "100% offline" claimed but user has no way to verify | Not implemented | Privacy-conscious user skeptical | Reduces trust for the exact audience that values privacy most | Add "Network Monitor" in Help menu that shows: "0 network requests made since app launch" with live counter | 1 day | Help → Privacy Proof shows zero network requests | Feature mention in reviews/testimonials |
| P2-10 | No recent documents history | Retention | User must re-open files from file picker every time | Not implemented | Friction for repeat workflows (signing the same documents weekly) | Reduces repeat usage | Add "Recent Documents" in File menu and as quick-access in extraction/PDF tabs | 2-3 days | File → Recent Documents shows last 10 opened files | Repeat session usage increases |

### P3 — FIX WITHIN 90 DAYS (moat + scale)

| ID | Title | Category | Current Problem | Root Cause Hypothesis | User Impact | Business Impact | Recommended Fix | Effort | Acceptance Criteria | Success Metric |
|----|-------|----------|----------------|----------------------|-------------|-----------------|-----------------|--------|--------------------|--------------------|
| P3-01 | No batch processing | Feature | Must extract signatures one at a time | Gated behind "Pro tier" that doesn't exist | Power users with 20+ documents waste time | Lost pro-tier revenue opportunity | Build basic batch mode: select folder → extract all signatures → review results in grid | 2-3 weeks | User can select multiple files and extract signatures in batch | Batch feature usage rate |
| P3-02 | No SVG export | Feature | Only PNG/JPEG export available | Planned for Pro tier | Designers can't use signatures in vector workflows | Limits addressable market | Add SVG export option to export dialog | 3-5 days | SVG option in export dialog. Exports valid SVG. | SVG export adoption rate |
| P3-03 | Threshold is only extraction control | Feature Quality | Single slider for background removal. No edge cleanup, no noise removal, no contrast boost. | MVP approach | Messy signatures (phone photos, shadows, colored paper) produce poor results | Limits extraction quality ceiling | Add: noise cleanup toggle, contrast boost slider, edge sharpen toggle | 1 week | Three additional controls in extraction panel. Measurably cleaner output on messy inputs. | Extraction quality satisfaction score |
| P3-04 | No signing templates | Retention | User must re-position signature on every PDF | Not built | Repetitive positioning for recurring document types (same contract template) | Reduces repeat workflow efficiency | Allow saving "signature placement templates" — position + size for specific document layouts | 1-2 weeks | User can save and reuse signature placement positions | Template usage rate |
| P3-05 | No SEO content | Growth | No blog, no comparison pages, no how-to guides | Marketing strategy documented but not executed | Zero organic search traffic | Entirely dependent on paid/direct traffic | Write 5 foundational articles: "DocuSign alternative", "How to extract signature from photo", "Offline PDF signing", "Best signature tools 2026", "Privacy-first document signing" | 2-3 weeks | 5 articles published, indexed, targeting specific keywords | Organic traffic measurable |
| P3-06 | No referral mechanism | Growth | No way to share or refer | Not built | Product has zero virality | Growth is entirely linear | Add "Share SignKit" in app (generates referral link with discount). Add social sharing for "I just signed a PDF offline" moment. | 1 week | Referral link generation works. Tracked in analytics. | Referral click rate |
| P3-07 | No Pro tier monetization | Revenue | Everything is $29. No upsell path. | Pro tier documented but not built | Leaves money on the table from power users willing to pay more | Revenue ceiling at $29/user forever | Launch Pro tier ($79): batch processing, SVG export, DOCX signing, priority support. Gate features behind license key. | 2-3 weeks | Pro license key unlocks additional features. Purchase flow exists. | Pro tier conversion rate |
| P3-08 | No desktop app analytics | Data | No tracking of extraction usage, export frequency, feature adoption | Not implemented | Unknown which features users actually use | Product decisions based on assumptions | Add privacy-respecting local analytics: extraction count, export format, feature usage. Opt-in sync to server. | 1 week | Events logged locally. Optional sync endpoint. Dashboard accessible. | Data-driven product decisions possible |
| P3-09 | No Product Hunt launch | Growth | Marketing strategy planned but not executed | Waiting for product readiness | Missing the single highest-leverage launch channel for indie tools | One-time launch opportunity wasted or delayed | Prepare and execute Product Hunt launch: tagline, screenshots, maker comment, hunter outreach. Coordinate with free trial launch. | 1-2 weeks prep | Product Hunt page live. Day-of engagement plan executed. | PH upvotes, traffic spike, conversion |
| P3-10 | Cloudflare deploy process unclear | Infrastructure | deploy_dist/ exists but relationship to web/live/ is unclear. wrangler.toml has placeholder account_id. | Deployment was set up but documentation/process lost | Uncertain whether landing page fixes actually reach production | Deploy friction slows iteration | Document deploy process. Create single deploy command. Verify Cloudflare Pages config. | 2-3 hrs | `npm run deploy` or equivalent pushes to production. Verified working. | Deploy cycle time < 5 min |

---

## QUICK WINS vs STRUCTURAL FIXES vs MOAT FEATURES

### Quick Wins (< 1 day each, immediate impact)
1. P0-01: Fix broken CTA URLs — 10 min
2. P0-02: Remove fake social proof — 30 min
3. P0-05: Update copyright year — 5 min
4. P0-06: Fix onboarding title — 5 min
5. P0-07: Remove HIPAA badge — 5 min
6. P0-09: Remove "Coming soon" testimonials — 5 min
7. P0-08: Fix email domain mismatch — 15 min
8. P1-05: Remove or fix ghost CTA button — 1 hr
9. P1-06: Fix analytics.js var declarations — 30 min
10. P2-08: Add empty state guidance — 3-4 hrs
11. P2-09: Add offline verification proof — 1 day

**Total quick win effort: ~2 days**
**Impact: Moves trust from D to C, fixes active bugs**

### Structural Fixes (1-2 weeks, foundational)
1. P0-03: Fix legal placeholders — 1 hr
2. P1-01: Implement free trial mode — 1-2 weeks
3. P1-04: Consolidate landing pages — 3-5 hrs
4. P1-08: Sample image on first launch — 2-3 hrs
5. P1-09: Connect extraction→PDF flow — 3-5 days
6. P1-10: Unify product naming — 2-3 hrs
7. P2-04: Redesign landing page for trust — 1-2 weeks
8. P2-06: Refactor extraction.py — 1-2 weeks
9. P2-07: Unify button factory — 3-4 hrs
10. P2-10: Add recent documents — 2-3 days

**Total structural effort: ~5-6 weeks**
**Impact: Moves grade from C+ to B**

### Moat Features (2-4 weeks, differentiation)
1. P1-02 + P1-03: Demo video + before/after GIF — 1 day
2. P2-01: Auto-detect signature region — 1 week
3. P2-02: Rich signature library — 1 week
4. P3-01: Batch processing — 2-3 weeks
5. P3-03: Enhanced extraction controls — 1 week
6. P3-04: Signing templates — 1-2 weeks
7. P3-07: Pro tier launch — 2-3 weeks
8. P3-05: SEO content — 2-3 weeks
9. P3-09: Product Hunt launch — 1-2 weeks

**Total moat effort: ~10-12 weeks**
**Impact: Moves grade from B to B+/A-**

---

## GRADE LIFT PLAN

### C+ → B (requires: trust fixes + trial + landing page)
**Blocking issues to resolve:**
- Fix all P0 issues (broken CTAs, fake numbers, legal placeholders, syntax errors)
- Implement free trial (P1-01)
- Consolidate landing page (P1-04)
- Add demo video (P1-02)
- Add sample image on first launch (P1-08)

**Timeline:** 2-3 weeks
**Confidence:** High — all issues are well-understood with clear fixes

### B → B+ (requires: workflow connection + UX polish + first growth)
**Blocking issues to resolve:**
- Connect extraction→PDF flow (P1-09)
- Auto-detect signature region (P2-01)
- Rich signature library (P2-02)
- Empty state guidance (P2-08)
- Keyboard shortcuts (P2-03)
- Redesign landing page for trust (P2-04)
- First 5 SEO articles (P3-05)

**Timeline:** 4-6 weeks after reaching B
**Confidence:** Medium — auto-detect quality needs testing

### B+ → A- (requires: pro features + growth engine + premium feel)
**Blocking issues to resolve:**
- Batch processing (P3-01)
- Enhanced extraction controls (P3-03)
- Signing templates (P3-04)
- Pro tier monetization (P3-07)
- Product Hunt launch (P3-09)
- Referral mechanism (P3-06)
- SVG export (P3-02)

**Timeline:** 8-12 weeks after reaching B+
**Confidence:** Medium — depends on pro tier market fit

---

## 30-DAY ROADMAP

### Week 1: Trust Emergency (all P0 issues)
| Day | Task | ID | Owner |
|-----|------|----|-------|
| 1 | Fix broken CTA URLs in web/live/index.html | P0-01 | Dev |
| 1 | Fix main.js syntax error | P0-04 | Dev |
| 1 | Remove fake social proof from purchase.html | P0-02 | Dev |
| 1 | Remove HIPAA badge | P0-07 | Dev |
| 1 | Remove "Coming soon" testimonials | P0-09 | Dev |
| 1 | Update copyright to 2026 | P0-05 | Dev |
| 2 | Fill in legal document placeholders | P0-03 | Dev/Legal |
| 2 | Confirm legal entity name, unify across docs | P1-07 | Legal |
| 2 | Fix privacy policy email inconsistency | P0-08 | Dev |
| 2 | Fix onboarding dialog title | P0-06 | Dev |
| 3 | Audit Cloudflare Pages deploy. Pick canonical landing page. | P1-04 | Dev |
| 3 | Remove or fix "View product details" ghost button | P1-05 | Dev |
| 3 | Fix analytics.js var declarations | P1-06 | Dev |
| 3 | Unify product naming across all files | P1-10 | Dev |
| 4-5 | Record 30-second demo video | P1-02 | Product |
| 5 | Create before/after GIF for extraction | P1-03 | Product |

### Week 2: Activation + Trial
| Day | Task | ID | Owner |
|-----|------|----|-------|
| 6-8 | Implement free trial mode (3 free exports) | P1-01 | Dev |
| 9 | Add sample image on first launch | P1-08 | Dev |
| 9 | Add empty state guidance in extraction tab | P2-08 | Dev |
| 10 | Embed demo video on landing page | P1-02 | Dev |
| 10 | Add before/after GIF to landing page hero | P1-03 | Dev |

### Week 3: UX Polish
| Day | Task | ID | Owner |
|-----|------|----|-------|
| 11-13 | Connect extraction→PDF flow ("Sign PDF" button from result) | P1-09 | Dev |
| 14-15 | Add keyboard shortcuts + cheatsheet | P2-03 | Dev |
| 15 | Add loading/processing feedback for large images | P2-05 | Dev |

### Week 4: Foundation for Growth
| Day | Task | ID | Owner |
|-----|------|----|-------|
| 16-17 | Add "Network Monitor" / offline verification proof | P2-09 | Dev |
| 17 | Add Recent Documents to File menu | P2-10 | Dev |
| 18-19 | Begin landing page redesign (clean, professional) | P2-04 | Design |
| 20 | Document deploy process. Fix wrangler.toml. | P3-10 | Dev |

---

## 60-DAY ROADMAP (Weeks 5-8)

### Week 5-6: Extraction Quality
| Task | ID | Owner |
|------|----|-------|
| Implement auto-detect signature region (contour detection) | P2-01 | Dev |
| Add noise cleanup toggle | P3-03 | Dev |
| Add contrast boost slider | P3-03 | Dev |
| Add edge sharpen toggle | P3-03 | Dev |
| Refactor extraction.py into smaller modules | P2-06 | Dev |
| Unify _create_button into shared widget | P2-07 | Dev |

### Week 7-8: Library + Retention
| Task | ID | Owner |
|------|----|-------|
| Rich signature library: search, tags, sort, favorites | P2-02 | Dev |
| Signing templates (save/restore placement positions) | P3-04 | Dev |
| SVG export | P3-02 | Dev |
| Publish first 5 SEO articles | P3-05 | Content |
| Launch redesigned landing page | P2-04 | Dev/Design |

---

## 90-DAY ROADMAP (Weeks 9-12)

### Week 9-10: Pro Tier
| Task | ID | Owner |
|------|----|-------|
| Batch processing mode | P3-01 | Dev |
| Pro license tier ($79): batch + SVG + DOCX + priority support | P3-07 | Dev |
| DOCX signing support | P3-07 | Dev |
| Implement pro feature gating | P3-07 | Dev |

### Week 11-12: Launch + Growth
| Task | ID | Owner |
|------|----|-------|
| Referral mechanism (in-app share link) | P3-06 | Dev |
| Desktop app analytics (local tracking) | P3-08 | Dev |
| Product Hunt launch preparation | P3-09 | Marketing |
| Product Hunt launch execution | P3-09 | All |
| Gumroad listing optimization (screenshots, description, FAQ) | — | Marketing |

---

## EXACT FEATURE RECOMMENDATIONS WITH RATIONALE

### Top 5 Features to Add Next

| # | Feature | Rationale | Effort | Impact |
|---|---------|-----------|--------|--------|
| 1 | **Free trial (3 exports)** | Single biggest conversion lever. Users need to see extraction quality before paying. A 30-day refund is not a substitute — it requires trust to buy first. | 1-2 weeks | Critical |
| 2 | **Auto-detect signature region** | Reduces manual work from "zoom in and carefully select" to "it found it for me." Massive perceived quality boost. Also enables batch processing later. | 1 week | High |
| 3 | **Batch processing** | The feature that justifies a Pro tier. Real estate agents, lawyers, and HR departments process dozens of documents. This is their #1 workflow need. | 2-3 weeks | High |
| 4 | **Rich signature library** | Search, tags, favorites, recent. This is the retention engine — the more signatures you store, the harder it is to switch to a competitor. | 1 week | High |
| 5 | **Enhanced extraction controls** | Noise cleanup, contrast boost, edge sharpen. Currently the threshold slider alone can't handle messy inputs. These controls close the quality gap. | 1 week | Medium-High |

### Top 5 UX Improvements

| # | Improvement | Rationale | Current State | Target State |
|---|-------------|-----------|---------------|--------------|
| 1 | **Sample image on first launch** | Reduce time-to-aha from "find your own image" to zero | Empty extraction view | Sample signature pre-loaded with working threshold |
| 2 | **Connected extraction→PDF flow** | User expects extract→sign as one workflow | Two disconnected tabs | "Sign a PDF" button in extraction result |
| 3 | **Empty state with guidance** | Blank screen causes confusion | Empty extraction view | Illustrated empty state with CTA + "Try sample" |
| 4 | **Processing feedback** | Large images feel like they've frozen | No progress indicator | Spinner/progress bar for operations > 500ms |
| 5 | **Keyboard shortcut cheatsheet** | Power users need discoverability | Shortcuts exist in code, not surfaced | Help → Keyboard Shortcuts menu + tooltip hints |

### Top 5 Conversion Improvements

| # | Improvement | Rationale | Expected Impact |
|---|-------------|-----------|-----------------|
| 1 | **Free trial mode (3 exports)** | Must prove quality before asking for money | +100-200% conversion rate |
| 2 | **Demo video on landing page** | Show don't tell. 30 seconds of real product. | +30-50% time on page, +15-25% conversion |
| 3 | **Before/after GIF in hero** | Instant visual proof that extraction works | +20-30% scroll depth, +10-15% conversion |
| 4 | **Remove all fake social proof** | Trust is binary. Fake numbers destroy it permanently. | Prevents PR disaster, rebuilds trust floor |
| 5 | **Single canonical landing page** | Stop fragmenting traffic across 5 broken variants | +20-30% effective traffic (consolidated analytics) |

### Top 5 Retention Improvements

| # | Improvement | Rationale | Expected Impact |
|---|-------------|-----------|-----------------|
| 1 | **Rich signature library (search/tags/favorites)** | Library depth = switching cost = retention | Signatures stored per user increases |
| 2 | **Recent documents list** | Reduces friction for repeat workflows | Repeat session frequency increases |
| 3 | **Signing templates** | Save signature placement for recurring document types | Weekly signing workflow efficiency increases |
| 4 | **Quick-sign from library** | One-click "sign this PDF with my default signature" | Time to sign decreases, daily usage increases |
| 5 | **Usage history / audit log** | "You signed 23 documents this month" creates habit awareness | Engagement awareness, referral trigger |

### Top 5 Ways to Make the App Feel Premium and Non-Generic

| # | Improvement | Why It Matters |
|---|-------------|----------------|
| 1 | **Instant threshold preview** — slider changes should update the preview in < 50ms. Perceived quality is speed. | Users associate instant feedback with professional tools. |
| 2 | **Smooth zoom/pan with momentum** — the image viewer should feel like an iOS photo viewer, not a web browser. | Touch-like interactions feel premium on desktop. |
| 3 | **Smart auto-detect with subtle animation** — when the signature region is detected, show a smooth animated rectangle drawing around it. | Animation conveys intelligence. Static rectangles feel like a script. |
| 4 | **Thoughtful micro-interactions** — button press states, export completion animation, signature placed confirmation. | The difference between "tool" and "product" is in the 100ms details. |
| 5 | **Consistent design system** — one button style, one spacing system, one font hierarchy across all tabs and dialogs. Currently the copy-pasted `_create_button` produces visual chaos. | Visual consistency is the #1 signal of craft. Inconsistency is the #1 signal of amateur. |

---

## WHAT TO NOT BUILD YET

| Feature | Why Not Now | When to Revisit |
|---------|-------------|-----------------|
| **Cloud sync** | Contradicts privacy value prop. Adds massive complexity. No user demand yet. | Only if users explicitly request it AND you can do it with E2E encryption. |
| **Mobile app** | Desktop-first is correct. Mobile signing is a different product. | After $100K ARR. Proven demand for desktop. |
| **Enterprise SSO / RBAC** | Zero enterprise customers. SSO is a 3-month project. | After 5+ enterprise prospects request it. |
| **API access** | No integration partners. No ecosystem. | After Product Hunt launch generates developer interest. |
| **Browser extension** | Massive scope creep. Different tech stack. Different distribution. | Never, unless pivoting to a platform play. |
| **AI/ML extraction (deep learning)** | Current CV approach works for clean inputs. ML adds model size, inference time, training data needs. | After threshold-based approach proves insufficient for 20%+ of user inputs. |
| **Multi-language support** | Product is English-only. No localization demand yet. | After 1,000 paid users and international traffic data. |
| **Team collaboration** | No team features, no shared libraries, no multi-user. | After Pro tier proves individual power users will pay $79. |
| **Blockchain/document verification** | Notarization is a feature for year 2, not month 2. | Never, unless targeting legal/compliance verticals specifically. |
| **Custom signature fonts/styling** | The product is about extracting real signatures, not generating fake ones. | Never. Contradicts core value prop. |

---

## ANALYTICS / EVENTS TO INSTRUMENT

### Desktop App Events (local-first, optional sync)
| Event | Trigger | Properties |
|-------|---------|------------|
| `app_launch` | App starts | version, platform, first_run (bool) |
| `extraction_started` | User uploads image | file_type, file_size_kb, source (drag_drop / file_picker / sample) |
| `extraction_completed` | Extraction finishes | duration_ms, image_width, image_height, auto_detect_used (bool) |
| `threshold_changed` | User moves threshold slider | value, source (slider / keyboard) |
| `export_completed` | User exports signature | format (png/jpeg/svg), destination (file / clipboard / library) |
| `pdf_opened` | User opens PDF | file_size_kb, page_count |
| `signature_placed` | User places signature on PDF | source (library / extraction), resize_count |
| `pdf_saved` | User saves signed PDF | pages_signed, save_duration_ms |
| `vault_signature_added` | Signature saved to library | total_signatures_in_library |
| `vault_signature_used` | Signature retrieved from library | total_signatures_in_library |
| `trial_export_blocked` | Trial user hits export paywall | exports_remaining (0) |
| `upgrade_clicked` | User clicks upgrade/purchase | source (paywall / menu / about) |
| `onboarding_completed` | User finishes onboarding | steps_viewed, time_spent_s |
| `error_occurred` | Any error | error_type, error_message, context |

### Landing Page Events (already partially tracked)
| Event | Trigger | Properties |
|-------|---------|------------|
| `page_view` | Page loads | variant, referrer, utm_source |
| `hero_cta_click` | Hero CTA clicked | variant, destination |
| `demo_video_play` | Video plays | watch_duration_s |
| `scroll_depth` | Scroll milestones | percent (25/50/75/100) |
| `faq_expanded` | FAQ item opened | question_text |
| `pricing_viewed` | Pricing section visible | time_to_view_s |
| `checkout_initiated` | CTA to Gumroad clicked | source (hero / pricing / final) |

---

## EXPERIMENTS TO RUN

| # | Experiment | Hypothesis | Metric | Duration | Sample Size |
|---|-----------|------------|--------|----------|-------------|
| 1 | **Free trial vs no trial** | 3 free exports will increase trial-to-paid conversion by 2x vs current no-trial model | Conversion rate (landing → paid) | 4 weeks | 500 visitors per variant |
| 2 | **Hero headline: extraction vs signing** | "Extract clean signatures from any document" will outperform "Sign PDFs offline" for the primary audience | CTA click-through rate | 2 weeks | 300 visitors per variant |
| 3 | **Demo video placement: hero vs below fold** | Video in hero section will increase engagement vs video below screenshots | Video play rate, time on page | 2 weeks | 300 visitors per variant |
| 4 | **Price anchoring: $29 vs $39 with $29 launch** | Showing $39 original → $29 launch will increase perceived value without hurting conversion | Conversion rate, refund rate | 4 weeks | 500 visitors per variant |
| 5 | **Before/after GIF vs static screenshot** | Animated GIF in hero will increase scroll depth by 30%+ | Scroll depth past hero, time on page | 2 weeks | 300 visitors per variant |
| 6 | **Landing page style: neo-brutalist vs clean professional** | Clean professional design will outperform neo-brutalist for trust-sensitive audience | Bounce rate, conversion rate | 4 weeks | 500 visitors per variant |
| 7 | **Auto-detect on vs off** | Auto-detect will reduce time-to-first-export by 50%+ | Time from upload to first export | 2 weeks | 100 users |
| 8 | **Export limit: 3 vs 5 vs unlimited trial** | 3 exports is the optimal balance between proving value and creating urgency | Conversion rate, time to conversion | 4 weeks | 300 users per variant |

---

## SUMMARY: EXECUTION PRIORITIES

### This week (Days 1-5):
Kill all P0 trust bombs. Fix broken CTAs. Remove fake numbers. Fill legal placeholders. Record demo video.

### Next 2 weeks (Days 6-14):
Ship free trial. Add sample image on first launch. Embed demo video + GIF on landing page. Consolidate to single landing page.

### Days 15-30:
Connect extraction→PDF flow. Add keyboard shortcuts. Add empty states. Add processing feedback. Start landing page redesign.

### Days 31-60:
Auto-detect signature region. Rich signature library. Enhanced extraction controls. Refactor extraction.py. Publish SEO content. Launch redesigned landing page.

### Days 61-90:
Batch processing. Pro tier ($79). SVG export. Signing templates. Referral mechanism. Product Hunt launch.

### What changes the grade:
- **C+ → B:** P0 fixes + free trial + demo video + landing consolidation (Weeks 1-3)
- **B → B+:** Connected workflow + auto-detect + library + SEO (Weeks 4-8)
- **B+ → A-:** Pro tier + batch + templates + Product Hunt (Weeks 9-12)
