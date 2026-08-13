# Experiments Calendar — Signature Extractor (No Trial)

## Goals
- Maximize net revenue and purchase conversion with a no‑trial strategy.
- Validate price points, messaging, and paywall UX quickly.

## Primary Metrics
- Website → purchase rate
- First run → purchase rate (if download-before-buy)
- Refund rate (Lifetime)
- AOV uplift from bundles/coupons

## Week 1 — Price + Copy
- Test A: Lifetime price $29 vs $39 (50/50 split)
- Test B: CTA copy “Own it forever” vs “Buy once, use forever”
- Test C: Guarantee copy “30‑day money‑back” vs “Love it or money back”
- Assets: Two pricing page variants each; same hero video
- Win rule: Highest net revenue (conversion × price) with refund penalty factored

## Week 2 — Paywall UX
- Test D: Paywall location — Export dialog vs persistent status bar button only
- Test E: Paywall timing — On first export click vs after 1 preview
- Test F: Discount surfacing — Inline “LAUNCH20” vs modal during paywall
- Win rule: Highest purchase rate without increasing refunds

## Week 3 — Bundles & Value Props
- Test G: Bundle — Lifetime $39 incl. Preset Pack vs Lifetime $29 bare
- Test H: Cross‑sell — Post‑purchase Preset Pack $9 vs $19
- Test I: Social proof — 3 quotes carousel vs compact one‑liner
- Win rule: Highest AOV with acceptable purchase conversion

## Week 4 — Channels & Landing Media
- Test J: Hero video above‑the‑fold vs below, with/without autoplay muted
- Test K: Landing variant for Real Estate vs General (headline + subhead)
- Test L: Channel UTM comparison — PH/Reddit/HN/YouTube Shorts
- Win rule: Scale channels with best CAC and revenue per visitor

## Guardrails
- Minimum sample per variant: 300 unique visitors
- Run tests sequentially when traffic is low
- Record refunds by variant; kill variants with refund > 7%

## Implementation Notes
- Use a lightweight server‑side split or static variants with distinct URLs
- Persist variant assignment per user via localStorage + URL param
- Log purchase events with variant metadata for attribution

