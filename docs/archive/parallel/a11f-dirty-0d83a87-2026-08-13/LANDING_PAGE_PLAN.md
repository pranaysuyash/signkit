# Landing Page Plan — Signature Extractor (PDF Bundle)

## Goals
- Communicate the vertical workflow: Extract → Organize → Place on PDFs.
- Price framing: $39 lifetime with $29 intro banner.
- Conversion-first: clear CTA, social proof, quick FAQ, refund promise.

## Page Structure
- Hero
  - Headline: “Extract and sign — all on your desktop.”
  - Subhead: “Clean signatures in seconds, then place them on PDFs. Private by default.”
  - Primary CTA: `Buy Lifetime — $39` with a small `Intro $29` badge.
  - Secondary CTA: `Watch 45s demo`.
- Visual Proof
  - Before/after slider of a messy scan → clean transparent signature.
  - 15s GIF: drag from library → drop on PDF → Save Signed PDF.
- Features (3–5 bullets)
  - Precise selection with zoom + threshold control
  - Export clean PNGs; local signature library
  - PDF viewer + signature placement (new)
  - Offline by default; no uploads
- Comparison Band
  - Use table from `docs/PRICING.md` for Adobe/DocuSign/Smallpdf vs us.
- Pricing
  - Card: “Lifetime — $39” with `Own it forever` + refund badge; intro ribbon `$29 launch`.
- FAQ (6–8 items)
  - Trial vs refund; privacy; OS support; updates policy; license scope; how it compares.
- Footer
  - Legal links: Privacy Policy, Terms/EULA, Refund policy, Third‑party notices.

## Copy Sources
- Use/keep in sync with `docs/COPY_DECK.md`, `docs/PRICING.md`.
- Pull comparison table from `docs/PRICING.md`.

## CTAs & Links
- Primary: `/buy` → provider checkout (configurable via env).
- Secondary: `/demo` video hosted on YouTube/Vimeo.
- Support: `mailto:support@yourdomain` and Help Center.

## Assets Checklist
- 3–5 annotated screenshots (selection, preview, export dialog, PDF placement)
- 2 short GIFs (30–45s hero, 15s PDF placement)
- App icon + logo

## Technical Notes
- Static `updates.json` hosted under `/downloads/updates.json` for in-app checks.
- Download URLs per platform placed behind stable routes.
- Add UTM params to checkout for attribution.

## A/B Tests (optional)
- CTA copy: “Own it forever” vs “Buy once, sign forever”.
- Price anchoring band: show “$39 regular — $29 launch” vs simple `$39` with badge.
- Guarantee copy variations.

## Implementation Tasks
- Build a simple static site (Next.js, Astro, or plain HTML) with the above sections.
- Wire environment-driven checkout URL.
- Add analytics (privacy-friendly; Plausible/Umami) with clear cookie note if needed.

