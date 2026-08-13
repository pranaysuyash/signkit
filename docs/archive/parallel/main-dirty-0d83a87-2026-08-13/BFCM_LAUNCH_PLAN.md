# Black Friday & Cyber Monday (BFCM) Launch Plan

Last Updated: 2025-11-21

This document outlines the plan for preparing, executing, and monitoring a successful Black Friday / Cyber Monday (BFCM) launch for SignKit. It includes timelines, landing page, analytics, promotional assets, support, and rollback plans.

## Objectives

- Reach high visibility on BFCM weekend
- Convert new users with a special limited-time offer
- Ensure a stable, monitored deploy and fast issue response

## Timeline (High Level)

- T-minus 7 days — Finalize assets, QA, and marketing copy
- T-minus 3 days — Final smoke test, staging deploy, and test purchases
- T-minus 1 day — Deploy to production, monitor systems, ensure tracking
- Launch day — Start campaign (email + Product Hunt + Twitter + Reddit), monitor 24/7
- Day +1 — Re-check analytics, verify numbers, begin fulfilment and support tasks

## Promotion & Messaging

- Offer: Lifetime license at $29 (BFCM launch special). Consider a discount code or special bundle.
- Messaging: Focus on privacy, local extraction, quick sign workflow.
- Channels: Email (existing list), Twitter, Product Hunt, Reddit (r/programming, r/privacy), Hacker News (as appropriate), and affiliate partners.

## Analytics & Tracking

- GA4: track as `purchase_event`, `variant`, `experiment_id`
- Conversion goals: Add funnel steps `view_product` → `click_buy` → `purchase_completed`
- Ensure `web/live/js/analytics.js` central logic contains the BFCM UTM tracking and `ab_test_impression` events
- Validate server-side (backend) GA measurement if implemented (for higher-fidelity conversion counts)

## Landing Page & A/B Testing

- Use `web/live` canonical content; `main` is the live branch for variant testing.
- Make sure root-level pages link to `web/live` assets and use consistent CTAs.
- Keep `AUTO_SPLIT = true` if running A/B traffic during BFCM; prefer `AUTO_SPLIT = false` for controlled/progressive rollouts.

## Critical Pre-Launch Checks (T-minus 7 to 3 days)

- Screenshots: Add all 4 real screenshots to `web/live/assets/screenshots/` (optimised images)
- CTA Links: Verify all CTA buttons point to correct Gumroad product URL
- Checkout: Run manual test purchases and verify license delivery and email flow
- DNS & SSL: Confirm custom domain `signkit.work` routes correctly
- Analytics: Confirm GA4 property is capturing `purchase` events
- Perform load test on deploy pipeline (if available)

## Production Deployment Strategy

- Cloudflare Pages: ensure the build directory is set to `web/live` when deploying from `main`. Document the final choice in `CLOUDFLARE_DEPLOYMENT.md`.
- For critical releases, deploy during a low-traffic maintenance window (e.g., early morning) and enable a short TTL on cache for fast rollbacks.

## Testing Scripts & Automated Checks

- Add an end-to-end test that performs a `purchase` flow (if not present), or use `tests/e2e/analytics.deploy.test.js`
- Add a smoke test to verify the following on `main` after merge: index, purchase, buy and root pages load with spec'ed assets
- Consider adding a GitHub Action step to check that root pages reference `web/live` rather than archived `web/claude_landing_page_v2` paths.

## Communication & Support

- Prepare email template (marketing) for BFCM promotion and follow-up drives
- Staff support for 48–72 hours post-launch (Slack or messages) for real-time problem solving
- Have a rollback or hotfix plan: revert PRs and invalidate caches

## Measurement: KPIs to track

- Traffic and sessions (source / medium / campaign)
- CTA click rate (Per variant and root pages)
- Checkout starts and completed purchases (conversion rate)
- DNS & CDN cache hit rate
- Customer support tickets & resolved within target SLA

-## Post-Launch (Day +1 to 30)

- Compare performance vs baseline; declare winners if running A/B test
- Run refund and license analytics for possible abuse; use the gumroad API if required
- Promote winner variant and follow-up promotions if high-conversion variant found.

-## Responsible Parties

- Product Owner: @pranaysuyash
- Marketing Lead: TBD
- Dev & Backend: @pranaysuyash
- QA & Support: TBD

-## Appendix & Resources

- `README_LANDING_PAGE.md`, `CLOUDFLARE_DEPLOYMENT.md`, `DEPLOYMENT_STATUS.md` for operational deployment tasks
- Deployment scripts: `wrangler` instructions, `deploy_dist/` content

---

Generated automatically during the landing sync - keep this doc up to date with task owners and dates.
