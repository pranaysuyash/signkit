# BFCM (Black Friday/Cyber Monday) Checklist

This checklist is a single-page executable list for the BFCM launch. Mark the items complete as you run them.

## Pre-Launch (7–3 days)

- [ ] Finalize landing screenshots in `/web/live/assets/screenshots`
- [ ] Verify `web/live` uses correct version of CSS/JS and that `index.html` references `web/live/*`
- [ ] Confirm Gumroad product URL and checkout flow (test purchase to verify license delivery)
- [ ] Add UTM tracking to all marketing links
- [ ] QA all root pages (index.html, buy.html, purchase.html, root.html, gum.html)
- [ ] Add `AUTO_SPLIT` config if testing variants or set ABA testing to passive
- [ ] Finalize promo assets (email, social images, tweets, producthunt copy)
- [ ] Add GA4 and Clarity tracking tags and verify with Realtime Debug
- [ ] Add monitoring channel (Slack, PagerDuty) for launch alerts

## T-minus 3–1 days

- [ ] Smoke test deploy to staging and run `tests/e2e/analytics.deploy.test.js`
- [ ] Ensure `wrangler` or Cloudflare pages settings are correct for the chosen branch
- [ ] Finalize PR for landing `web/live` sync and merge to `main` only after approvals
- [ ] Set cache TTL to low values for faster rollbacks (short-term) for CDN

## Launch Day

- [ ] Ensure monitoring dashboards for GA, server logs, and Cloudflare Pages are live
- [ ] Start campaign (send marketing emails, post on social channels)
- [ ] Monitor for spikes in traffic; adjust CDN & caches if needed
- [ ] Keep support staffed for quick replies

## Post-Launch (Day +1 to 7)

- [ ] Collect conversion analytics and social metrics
- [ ] Identify best-performing variant for next promotion
- [ ] Follow-up email to purchasers (Welcome + Setup guide)
- [ ] Check refunds and license issuance for possible abuse

---

Ready? Use this checklist on a PR to validate landing updates before merging to `main`.
