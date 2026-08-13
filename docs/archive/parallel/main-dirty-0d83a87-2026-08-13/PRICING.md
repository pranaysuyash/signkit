# Signature Extractor — Pricing Strategy (PDF Bundle Launch)

## Addendum (2026-07-16)

The $29 launch / $39 Personal one-time offer remains the active base-product direction.
Competitor figures and Stripe/Paddle references below are historical snapshots; Dodo
Payments is now the primary checkout and Gumroad is the alternate. Proposed Professional,
Practice, and usage-based trust-service packaging is research—not a launched offer—and
is documented with a validation protocol in
`docs/research/2026-07-16_signkit_market_legal_vertical_research.md`. Do not publish the
research prices until customer interviews and purchase-intent tests are complete.

## TL;DR

**$39 lifetime (intro offer $29) with no trial.** Now includes the vertically integrated PDF viewer + signing workflow, lifetime updates, and 30-day refund.

---

## Offers

### 🪪 Lifetime Desktop — $39 (launch promo $29)
- All image extraction tools (crop, threshold, clean export)
- New PDF workflow: open, place stored signatures, save flattened PDFs
- Offline by default, perpetual license file
- 30-day money-back guarantee

> Grandfather existing $29 customers into the PDF build automatically. Landing page should highlight the early-bird $29 price until PDF GA; move list price to $39 afterwards.

### 💼 Pro Workspace — $15/mo or $129/year (Future)
- Adds multi-user sync, batch processing, shared libraries, browser extension
- Priority support + detailed audit exports
- Target release 6–12 months after PDF bundle GA

### 🏢 Team / Enterprise — (Future)
- Volume licensing, SSO, custom cloud retention, admin dashboard
- Price on request once demand proven

---

## Value Narrative Updates
- **Vertical integration story:** “Extract → Organize → Place on PDFs” in one desktop app, no cloud uploads.
- **Price framing:** $39 lifetime equals ~2 months of Adobe Acrobat Pro or DocuSign Personal.
- **Risk reversal:** Keep 30-day refund copy prominent; add “PDF signing included” badge next to CTA.
- **Existing users:** Email campaign upgrading current $29 buyers automatically, reinforcing lifetime promise.

---

## Landing Page Comparison Copy

Use this section on the pricing card or a “Why switch?” band below the hero.

| Solution | Pricing | Key Limits | Signature Extractor Advantage |
| --- | --- | --- | --- |
| Adobe Acrobat Pro | $19.99/mo (annual) | Heavy install, cloud sign-in required, overkill for extraction | $39 once, tuned for signatures, runs offline |
| DocuSign Personal | $10/mo (annual) | 5 envelopes/month, browser-only, no image cleanup | Local library + PDF signing, unlimited exports |
| Smallpdf Pro | $12/mo (annual) | Web-first, limited fine control, recurring fee | Desktop precision tools, no subscription |
| Signature Extractor | **$39 lifetime** (intro **$29**) | – | Own it forever, privacy-first, PDF workflow included |

Support copy for the comparison band:
- “Own the workflow: clean signatures, drop them on PDFs, export instantly.”
- “No subscriptions, no upload anxiety — everything stays on your machine.”
- CTA variation: “Buy once, sign forever ($29 launch price)”

---

## Launch & Transition Checklist
1. Update pricing section on landing page with comparison table + PDF badge.
2. Record refreshed walkthrough demo showing PDF placement in under 60 seconds.
3. Add FAQ item: “How does this compare to Adobe/DocuSign pricing?”
4. Notify early buyers: confirm they keep lifetime access and get the PDF upgrade free.
5. Monitor conversion impact of $39 headline vs $29 launch banner; be ready to A/B copy.

---

Keep Stripe/Paddle flows aligned with the no-trial approach; see `docs/PRICING_IMPLEMENTATION.md` for checkout and licensing details.

## Addendum (2026-08-02): Launch price and public-claim boundary

The accepted launch decision keeps the Personal offer deliberately simple:

- **$29 one-time launch price** for the Personal licence.
- **$39 regular Personal price** after the launch offer.
- No public Team, Business, or Automated Packet Ops price. Recurring packet
  operations remain an enquiry and pilot path until the workflow contract,
  deployment boundary, and fulfilment evidence are ready.

The root landing page is the only launch source. Its public claim inventory and
release state are tracked in `docs/launch_claims/registry.md`. The page must
describe the job as extract, clean, save, and place signatures on PDFs locally by
default. Checkout receives purchase and delivery information. A recurring
workflow enquiry receives only what the visitor chooses to type.

The Dodo product ID is empty in the current checkout configuration, so public
copy is provider-neutral: secure checkout is available through the configured
provider, with Gumroad as the current fallback while Dodo is not configured.
This wording does not claim that Dodo activation, payment verification, or
licence fulfilment has been completed.

The 30-day money-back policy is supported by `legal/TERMS_OF_SERVICE.md` and
`legal/EULA.md`. Landing copy may state the policy and direct the buyer to the
provider used for purchase or to support with the purchase email and order
reference. It must not strengthen the policy beyond those documents.

### External pricing exploration (context only, date-sensitive)

The 2026-08-02 exploration reviewed official pricing pages for context. These
references are not a superiority, savings, or outcome guarantee and should not
be turned into public comparison copy without a fresh review:

- [Adobe Acrobat plans and pricing](https://www.adobe.com/acrobat/pricing.html)
  presents subscription options for Acrobat Pro.
- [DocuSign eSignature plans and pricing](https://ecom.docusign.com/en-api-US/plans-and-pricing/esignature)
  presents a Personal subscription with envelope-based allowances.
- [Smallpdf pricing and plans](https://smallpdf.com/pricing) presents free,
  subscription, team, and business tiers.

These pages are date-sensitive third-party references. Re-check them before any
future pricing comparison, and preserve the local workflow value proposition
without implying that a one-time Personal purchase is cheaper or better for
every visitor.

The sections above this addendum are retained historical pricing exploration,
not current public launch copy. In particular, do not reuse their “lifetime
updates,” “runs offline,” “no cloud uploads,” competitor price figures, or
Stripe/Paddle checkout language without a fresh evidence review. The current
public source is the root landing page, its claim registry, and the Dodo/Gumroad
configuration described here.
