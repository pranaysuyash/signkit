# SignKit launch-claim registry

Date: 2026-08-02
Owner: SignKit launch surface
Canonical public source: `/index.html`

This registry is the release gate for customer-facing claims on the canonical
root landing page. A claim is allowed only when its wording, implementation
path, evidence tier, and release state are explicit. The page uses HTML comments
such as `<!-- launch-claim: personal_price -->` to bind each public claim family
to this table. These comments are non-rendered and are checked by
`tests/test_launch_claim_registry.py`.

Evidence tiers follow `motto_v4.md`: Tier 1 is static inspection, Tier 2 is a
targeted test, Tier 3 is an integration or end-to-end flow, Tier 4 is runtime or
manual observation, and Tier 5 is production-like or real-data verification.

## Registered public claim families

| Claim ID | Allowed public wording and boundary | Implementation path | Enforcing test | Evidence tier | Release state |
| --- | --- | --- | --- | --- | --- |
| `job_local_pdf` | SignKit helps extract, clean, save, and place signatures on PDFs locally by default. | `index.html` hero and workflow copy; `PRODUCT.md` product purpose | `tests/test_launch_claim_registry.py::test_required_job_language_is_present` | Tier 2 static regression plus existing extraction/PDF tests | Approved launch copy; no regulated-signature guarantee |
| `local_processing_boundary` | Core extraction and PDF work run locally by default. Checkout receives purchase and delivery information. | `index.html` boundary note and Personal card; `legal/PRIVACY_POLICY.md` | `tests/test_launch_claim_registry.py::test_privacy_boundary_is_qualified` | Tier 2 targeted static test; legal docs are source evidence | Approved with boundary wording; optional licence/update network use remains disclosed |
| `personal_price` | $29 is the one-time launch price and $39 is the regular Personal price. | `index.html` price pill, hero, and Personal card; `docs/PRICING.md` | `tests/test_launch_claim_registry.py::test_price_decision_is_explicit` | Tier 2 targeted static test plus pricing record | Approved launch decision |
| `one_time_pricing` | Personal is a one-time licence with no recurring charges. | `index.html` trust strip and FAQ; `legal/TERMS_OF_SERVICE.md` | `tests/test_launch_claim_registry.py::test_recurring_price_is_not_published` | Tier 2 targeted static test plus legal terms | Approved; major-update boundary remains in the licence docs |
| `checkout_provider_state` | Secure checkout is available through the configured provider. Gumroad is the current fallback while Dodo is not configured. | `index.html` checkout notes; `web/live/js/checkout-config.js` and `web/live/js/checkout.js` are the runtime owner files; checkout intent records placement and bounded UTM entry attribution | `tests/test_launch_claim_registry.py::test_provider_copy_is_state_neutral` | Tier 1 current config inspection; Tier 3 provider smoke is owned by checkout/deployment work | Copy approved; Dodo activation and production payment verification are not claimed |
| `platform_availability` | SignKit targets macOS, Windows, and Linux. The release bundle is the source of truth for current downloads. | `index.html` platform badges and FAQ; release build manifests | `tests/test_launch_claim_registry.py::test_platform_copy_names_release_bundle_source_of_truth` | Tier 1 static inspection; bundle contents require release verification | Qualified launch copy |
| `personal_included_workflow` | Personal includes signature extraction and cleanup, a local signature Vault, PDF placement/export, and minor updates within the purchased major version. | `index.html` Personal card; desktop extraction, Vault, and PDF modules | `tests/test_launch_claim_registry.py::test_personal_workflow_terms_are_present` | Tier 2 targeted tests over existing desktop workflow suites | Approved where the release bundle contains the named capability |
| `licence_updates` | Minor updates are included within the purchased major version. Do not promise every future major release. | `index.html` FAQ; `legal/TERMS_OF_SERVICE.md` and `docs/PRICING_IMPLEMENTATION.md` | `tests/test_launch_claim_registry.py::test_update_boundary_is_qualified` | Tier 1 legal/static inspection | Approved constrained wording |
| `refund_policy` | The canonical policy is a 30-day money-back guarantee. Requests go through the purchase provider or support with the purchase email and order reference. | `index.html` refund FAQ; `legal/TERMS_OF_SERVICE.md` and `legal/EULA.md` | `tests/test_launch_claim_registry.py::test_refund_copy_matches_legal_policy` | Tier 2 targeted static test plus legal-document inspection | Approved only while the cited legal documents remain current |
| `recurring_workflow_enquiry` | Recurring packet operations are an enquiry/pilot path with no public Team, Business, or Automated Packet Ops price. The enquiry receives only what the visitor chooses to type. | `index.html` workflow section and enquiry URL; workflow docs | `tests/test_launch_claim_registry.py::test_workflow_enquiry_is_unpriced_and_data_bounded` | Tier 2 targeted static test; enquiry handling still needs runtime/provider verification | Enquiry-only, not a public purchase promise |
| `operator_context` | Legal, HR, finance, real-estate, and admin operators are example contexts, not customer counts, ratings, or outcome claims. | `index.html` trust-strip context copy; `PRODUCT.md` audience | `tests/test_launch_claim_registry.py::test_no_social_proof_or_benchmarks_are_published` | Tier 1 static inspection | Approved contextual copy; no social proof |
| `product_evidence` | Product screenshots show the extraction/PDF workflow and are not a substitute for a production benchmark or customer proof. | `index.html` product preview and screenshots; current runtime capture docs | `tests/test_launch_claim_registry.py::test_product_preview_is_not_marketed_as_benchmark` | Tier 4 current runtime capture exists in `docs/review/`; public asset freshness remains a release check | Approved as product evidence with no benchmark language |
| `public_surface_boundary` | The root path is the only public acquisition surface. Retained landing and experiment paths redirect to it. | `_redirects`, `serve.py`, and the canonical URL in `index.html` | `tests/test_launch_claim_registry.py::test_public_surface_is_canonical` | Tier 2 targeted route-contract test; deployment redirect behavior still needs a production smoke check | Approved route policy |

## Not permitted on the root launch page

- Fabricated customer counts, ratings, testimonials, review badges, or
  extracted-signature totals.
- Speed or performance promises such as a fixed number of seconds.
- Absolute privacy language such as “your data never touches our servers” or
  “100% offline” when checkout, licence, update, or enquiry boundaries are not
  represented.
- “Dodo Payments delivers” or any wording that implies Dodo is active while its
  public product ID is empty.
- Public Team, Business, or Automated Packet Ops prices before those offers have
  a contract, fulfilment path, and release evidence.

## Release review checklist

Before publishing the root page, re-check the registry against the live
`index.html`, current checkout configuration, release bundle, legal documents,
and the targeted test. A passing static test does not prove Dodo payment
activation, provider fulfilment, or production conversion. Those require the
checkout/deployment smoke workflow and must be reported separately.

The route contract also inventories retained project HTML and redirects it to
the canonical root. After publishing, verify that the deployed
`web/live/js/checkout-config.js` and `web/live/js/checkout.js` responses are
JavaScript rather than an HTML fallback; otherwise the checkout provider state
cannot be considered active evidence.
