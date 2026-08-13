# SignKit launch readiness and pricing decision

Date: 2026-08-02
Status: accepted for the canonical root landing copy; checkout activation remains a separate runtime gate
Scope: `index.html`, `docs/PRICING.md`, and the launch-claim registry

## Decision

Keep the canonical root page as a job-led purchase surface for SignKit Personal.
The visitor should understand one concrete job before choosing a purchase path:

> Extract, clean, save, and place a signature on a sensitive PDF locally by
> default.

The Personal offer is **$29 one time at launch** and **$39 at the regular
Personal price**. There is no public Team, Business, or Automated Packet Ops
price. Recurring packet operations remain an enquiry and pilot path until their
workflow contract, deployment boundary, fulfilment process, and evidence are
ready for a public offer.

The page keeps its existing structure, selectors, checkout data attributes,
workflow enquiry URL, and accessibility landmarks. It does not become a concept
prototype or a second landing design.

## Value delivered

- **Visitor:** can understand the local-by-default PDF job, see the accepted
  Personal price, choose the configured purchase route, or enquire about
  recurring work without being asked to upload a document.
- **Business and team:** has one honest launch offer and a clear separation
  between Personal purchase and unpriced workflow discovery. Unsupported proof
  and inactive-provider language no longer create avoidable trust or compliance
  risk.
- **Internal operations:** has a claim registry, enforcing static test, dated
  price decision, and explicit provider/runtime gap for handoff to checkout and
  deployment owners.

## Claim and privacy boundary

The public page now uses the documented boundary rather than absolute privacy
copy:

- Core extraction and PDF work run locally by default.
- Checkout receives purchase and delivery information through the configured
  provider.
- A recurring workflow enquiry receives only what the visitor chooses to type;
  the page tells visitors not to attach documents or include sensitive contents.

This preserves the local-first product value without implying that checkout,
licence activation, update checks, or a contact form are local-only. The
canonical claim inventory and release states live in
`docs/launch_claims/registry.md`.

## Provider state and purchase path

The current checkout configuration has an empty Dodo product ID. The root page
therefore uses state-neutral copy:

> Secure checkout is available through the configured provider. Gumroad is the
> current fallback while Dodo is not configured.

This is not a claim that Dodo is active, that a Dodo transaction has been
verified, or that a provider has delivered a licence. The checkout/deployment
worker owns runtime routing and smoke verification. The page preserves both
provider data attributes so that the runtime owner can update the actionable
destination without introducing a duplicate checkout path.

## Refund and licence wording

The repository's current `legal/TERMS_OF_SERVICE.md` and `legal/EULA.md` both
state a 30-day money-back guarantee and identify the provider used for the
purchase as the first refund route. The root FAQ may therefore use the canonical
30-day wording and direct the buyer to the selected provider or support with the
purchase email and order reference. It must not promise a stronger or broader
refund outcome.

Minor updates are described as included within the purchased major version.
The page does not promise every future major release, regulated signatures, or
an outcome that depends on a third party.

## Platform availability

The page retains macOS, Windows, and Linux as platform targets, while explicitly
stating that the exact release bundle is the source of truth for current
downloads. Platform badges are not a promise that every platform binary is
attached to every release.

## External pricing exploration, context only

On 2026-08-02, official pricing pages were reviewed to understand the shape of
the market. These are date-sensitive references, not claims that SignKit is
cheaper, better, or a substitute for any competitor:

- [Adobe Acrobat plans and pricing](https://www.adobe.com/acrobat/pricing.html)
  shows Acrobat Pro subscription options.
- [DocuSign eSignature plans and pricing](https://ecom.docusign.com/en-api-US/plans-and-pricing/esignature)
  shows a Personal subscription with envelope-based allowances.
- [Smallpdf pricing and plans](https://smallpdf.com/pricing) shows free,
  subscription, team, and business tiers.

These links should be re-checked before any future comparison copy. The launch
page should continue to sell the local, job-led workflow and one-time ownership
without a savings or superiority guarantee.

## Options considered

1. **Keep the old absolute copy.** Rejected because “100% offline,” “your data
   never touches our servers,” and direct Dodo-delivery language contradict the
   documented checkout and licence boundaries.
2. **Move the root page to Gumroad-only copy.** Rejected because checkout
   configuration is owned by the runtime worker and the root page must remain
   compatible with the configured provider and fallback.
3. **Publish recurring packet pricing.** Rejected because recurring workflow
   fulfilment, deployment, and evidence are not closed as a public offer.
4. **Replace the root page with the Product Museum concept.** Rejected for this
   launch decision. The existing canonical page remains the purchase surface;
   concept work stays in its preserved parallel artifacts.

## Readiness and evidence

| Area | Current evidence | Tier | Readiness |
| --- | --- | --- | --- |
| Root claim language | Static inspection and targeted regression test | Tier 2 | Ready for copy review |
| Local extraction/PDF workflow | Existing desktop tests and current product captures | Tier 2 to Tier 4 | Capability evidence exists; release bundle still controls availability |
| Price decision | `docs/PRICING.md`, legal terms, and this decision | Tier 1 | Accepted: $29 launch, $39 regular Personal |
| Refund policy | `legal/TERMS_OF_SERVICE.md` and `legal/EULA.md` | Tier 1 | Copy may use canonical 30-day policy |
| Checkout provider | Empty Dodo ID in current config; Gumroad URL present | Tier 1 | Runtime smoke and provider fulfilment remain open |
| Customer conversion | No production purchase verification or Dodo activation evidence | Tier 0 to Tier 1 | Do not claim conversion, activation, or customer counts |

## Review passes

1. **Immediate correctness and completeness:** checked the root page against
   the accepted price, privacy boundary, provider state, refund policy, platform
   qualification, enquiry path, and prohibited proof terms. The static registry
   test now covers each registered claim marker.
2. **Architecture and long-term viability:** preserved one canonical root page,
   removed its dormant variant redirect logic, kept checkout ownership in the
   existing provider scripts, and left legacy variants untouched for the
   deployment worker's redirect work.
3. **Rule compliance and supervision readiness:** recorded evidence tiers,
   release states, external pricing context, and the explicit runtime gap. A
   passing static test is not represented as payment activation or production
   readiness.

## Implementation and verification contract

The implementation is limited to the owned files listed in the handoff:

- `index.html`
- `docs/PRICING.md`
- `docs/launch_claims/registry.md`
- `docs/analysis/2026-08-02_launch_readiness_and_pricing_decision.md`
- `tests/test_launch_claim_registry.py`

The static regression test must fail if unsupported proof terms or unregistered
claim markers are reintroduced. The checkout worker separately owns runtime
provider state and landing smoke workflows.

## Anything else?

Yes. The claim registry is a release artifact, not a one-time audit. Any future
copy change, new screenshot, provider switch, price change, or workflow offer
must update the registry and its enforcing test in the same change. A passing
static test cannot prove a payment provider has activated, delivered a licence,
or fulfilled a refund. Those claims need a fresh runtime or production-like
evidence tier and a separate readiness update.

## Update log

- 2026-08-02: accepted the launch price, provider-neutral checkout wording,
  local-by-default privacy boundary, recurring-enquiry constraint, and claim
  registry as the root landing release contract.

## Verification addendum (2026-08-02)

The local launch contract is now covered by the claim and route/provider tests,
but the current production deployment has not adopted the canonical route
boundary yet. Running `bash scripts/test-deployment.sh https://signkit.work`
returned HTTP 200 for `/root` where the new contract requires HTTP 301 to `/`.
This is a deployment-state finding, not a reason to restore the historical
variant routes. Publish the current root `_redirects` manifest, then rerun the
same production smoke command until every legacy route form redirects and the
root, robots, and sitemap checks pass.

The same live check observed that `/web/live/js/checkout-config.js` and
`/web/live/js/checkout.js` currently return the obsolete landing HTML instead of
JavaScript. The deployed page therefore cannot be credited with the new
provider-state behavior until the current root is published and the content
type/body checks pass. Historical deployment status and checklist pages now
carry dated superseded pointers so they cannot be mistaken for current
evidence.

## Three-pass review record (2026-08-02)

1. **Immediate correctness and completeness:** 18 targeted claim, route, and
   provider-state tests pass; local smoke and shell syntax checks pass; the
   public copy has no banned proof, absolute privacy, or unconfigured-Dodo
   fulfilment claims.
2. **Architecture and long-term viability:** the root is the single canonical
   acquisition surface; exact and wildcard redirects cover retained HTML;
   checkout configuration remains one source of truth; Gumroad becomes the
   visibly styled primary action when Dodo is absent or malformed; Team,
   Business, and Automated Packet Ops pricing remains enquiry-only.
3. **Rule compliance and supervision readiness:** claim registry, pricing
   addendum, deployment docs, superseded-guide pointers, and “Anything else?”
   are durable. Production routing and provider JavaScript are still stale, and
   Tier 3 payment evidence is absent, so the verdict remains fix-first rather
   than launch-ready.
