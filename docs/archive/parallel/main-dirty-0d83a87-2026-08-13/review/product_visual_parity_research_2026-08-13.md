# SignKit product visual parity research

Date: 2026-08-13
Worker: C
Scope: independent research and documentation only
Status: report complete; no source code, existing documentation, deployment, or Git state was changed

## Executive finding

The repository has a coherent local public-surface direction, but the deployed
domain is not serving that direction. The local contract names `index.html` as
the only acquisition and checkout surface, qualifies local processing, binds
checkout to one runtime owner, and redirects retained paths. The live domain
still serves the retired offline, lifetime, and direct Gumroad narrative on the
root and on multiple retained paths. The deployed checkout asset URLs return
HTML instead of JavaScript.

This is production parity and customer trust debt, not a visual polish issue.
The repository is evidence of the intended release surface. The live HTTP
responses are evidence of the current production state. No claim is made here
about Cloudflare deployment identity, payment completion, licence delivery, or
refund execution beyond what the read-only HTTP checks observed.

## Evidence convention

- **Tier 1:** static inspection of repository source, docs, route authorities,
  configuration, and external guidance.
- **Tier 2, S1:** a targeted check or test passed. This proves that the check
  ran and passed, not that it is mutation-sensitive.
- **Tier 3:** integration or deployed HTTP contract observation. A failure is
  still useful evidence of a release gap.
- **Tier 4:** runtime or manual observation. The live-domain content and
  response checks below are Tier 4 external runtime observations limited to
  HTTP status, headers, and response bodies.
- **Not established:** no screen-reader session, full keyboard audit, measured
  contrast audit, or real purchase and delivery run was performed in this
  report.

## Sources reviewed

### Repository sources

The current route, claim, checkout, and visual-direction baseline was read from:

- [`docs/launch_claims/public_surface_map.md`](../launch_claims/public_surface_map.md)
- [`docs/launch_claims/registry.md`](../launch_claims/registry.md)
- [`docs/landing/CANONICAL_SURFACE_ADDENDUM_2026-08-12.md`](../landing/CANONICAL_SURFACE_ADDENDUM_2026-08-12.md)
- [`docs/LANDING_DEPLOYMENT_PROCESS.md`](../LANDING_DEPLOYMENT_PROCESS.md)
- [`docs/LANDING_SURFACE_OWNERSHIP.md`](../LANDING_SURFACE_OWNERSHIP.md)
- [`docs/review/production_surface_mismatch_2026-08-12.md`](production_surface_mismatch_2026-08-12.md)
- [`docs/review/product_visual_direction_audit_2026-08-13.md`](product_visual_direction_audit_2026-08-13.md)
- [`docs/review/customer_claim_reference_audit_2026-08-12.md`](customer_claim_reference_audit_2026-08-12.md)
- [`docs/PUBLIC_SURFACE_QA_MATRIX.md`](../PUBLIC_SURFACE_QA_MATRIX.md)
- [`docs/PRICING.md`](../PRICING.md)
- [`docs/analysis/2026-08-02_launch_readiness_and_pricing_decision.md`](../analysis/2026-08-02_launch_readiness_and_pricing_decision.md)
- [`index.html`](../../index.html), [`_redirects`](../../_redirects),
  [`serve.py`](../../serve.py),
  [`web/live/js/checkout-config.js`](../../web/live/js/checkout-config.js),
  and [`web/live/js/checkout.js`](../../web/live/js/checkout.js)

### External primary guidance

The comparison uses current authoritative guidance, accessed 2026-08-13:

- [W3C Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/)
  for contrast, reflow, headings and labels, focus visibility, focus not
  obscured, target size, dragging alternatives, and predictable behavior.
- [W3C WAI-ARIA Authoring Practices: Developing a Keyboard Interface](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/)
  for keyboard operability, visible and predictable focus, and focus movement.
- [W3C WAI-ARIA Authoring Practices: Dialog Modal Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)
  for any future modal or checkout-confirmation dialog, including focus
  containment, labelling, and a visible close control.
- [MDN: `<button>` HTML element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button)
  for native controls, accessible names, focus styling, contrast, and target
  size.
- [MDN: `<label>` HTML element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/label)
  for explicit form-control labelling and larger activation areas.
- [MDN: `<img>` HTML element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img)
  for meaningful alternative text, intrinsic dimensions, layout-shift
  prevention, and considered lazy loading.

The W3C WCAG document is normative guidance. The WAI-ARIA APG is an
implementation guide and explicitly is not itself a conformance standard. MDN
is used for practical HTML behavior and accessibility implementation guidance.

## Canonical repository direction

### Route and checkout ownership

The current documented contract is explicit:

1. `/` and repository-root `index.html` are the only public acquisition and
   checkout surface.
2. Retained paths such as `/root`, `/buy`, `/purchase`, `/gum`, `/new`,
   `/web/live`, `/web/new_landing_page`, and `/web/cloud_workspace` are
   historical or review paths and must redirect to `/`.
3. `_redirects` and `serve.py` are the route authorities.
4. `web/live/js/checkout-config.js` is the only public provider configuration.
   Its Dodo product ID is empty, so the configured state is Gumroad as the
   actionable fallback. This does not prove payment or licence fulfilment.
5. `web/live/js/checkout.js` owns checkout link state and bounded attribution.

Evidence: Tier 1 static inspection of the route and ownership docs, `_redirects`,
`serve.py`, checkout files, and `index.html`.

### Claim boundary

The registry permits qualified language such as “locally by default”, “one-time
Personal licence”, and “secure checkout through the configured provider”. It
does not permit “100% offline”, “your files never leave your computer”,
unqualified lifetime claims, active Dodo fulfilment claims, fabricated proof,
or public recurring-workflow pricing.

Evidence: Tier 1 static inspection of `docs/launch_claims/registry.md`,
`docs/PRICING.md`, the brand narrative material, and the current root page.

### Current visual direction

The dated visual audit recommends a calm document-operations studio: warm paper
and ink, restrained dark proof surfaces, a controlled local-status signal,
limited amber attention, readable sans controls, restrained editorial display
type, moderate geometry, causal workflow transitions, and a clear distinction
between current local proof and future cloud or hybrid direction.

The current root source is still visibly neo-brutalist. It uses a light field,
Space Grotesk and IBM Plex Sans, strong dark borders, offset shadows, a yellow
price pill, indigo and cyan accents, emoji-led bullets, repeated cards, and
real product screenshots. That direction is distinctive and product-specific,
but it remains more launch-poster and card-led than the recommended calm
document studio. This is a design-direction gap, not a claim that the page is
invalid or inaccessible by appearance alone.

The source now contains a product-specific completion rail with native
`<button>` controls for `source`, `mark`, `clean`, `place`, and `ready`. It also
states that the rail is a keyboard-operable preview and not a live document
processor. This is a meaningful alignment with the recommended causal proof
interaction. Its full usability still needs browser keyboard, focus, reduced
motion, and comprehension verification.

## Static accessibility and interface observations

Current `index.html` inspection found the following primitives:

| Observation | Repository evidence | Guidance relationship | Evidence |
| --- | --- | --- | --- |
| One main landmark with an explicit `id` and `tabindex="-1"` | `index.html:1154` | Supports a skip-link destination and predictable focus movement | Tier 1 |
| Skip link is present | `index.html:1153` | Aligns with keyboard navigation and bypassing repeated content | Tier 1 |
| Visible `:focus-visible` styles are present | `index.html:751-755` | Aligns with WCAG 2.2 2.4.7 and WAI-ARIA keyboard guidance | Tier 1 |
| Reduced-motion media query is present | `index.html:814` | Aligns with the visual audit and preserves a path for motion-sensitive users | Tier 1 |
| Completion steps use native buttons and `aria-current="step"` | `index.html:1233-1238` | Aligns with MDN's native-control recommendation and WAI-ARIA state guidance | Tier 1 |
| Completion result uses `role="status"` and `aria-live="polite"` | `index.html:1240` | Provides a status announcement path for state changes | Tier 1 |
| All 6 images have `alt`, `width`, `height`, and `loading` attributes | Read-only structural count | Aligns with MDN image alternative-text and layout-stability guidance | Tier 1 |
| A semantic footer is present | `index.html:1669` | Supports page structure and the content-information region | Tier 1 |

These observations are not a WCAG conformance claim. The current code still
needs a real keyboard path review, focus visibility review at every state,
contrast measurements for text and UI components, 200% text resize and reflow,
touch-target measurement, link-name review, and assistive-technology testing.
The external checkout destination is also outside the repository's accessibility
boundary and needs provider-surface review.

The earlier `product_visual_direction_audit_2026-08-13.md` records the skip
link, semantic footer, anchor offset, and image-dimension items as open. The
current source inspection found those primitives present, so that portion of
the earlier audit is superseded by current code evidence. It should not be
treated as a claim that the corresponding browser and assistive-technology
behavior is closed.

One repository test is brittle against the current valid markup:
`tests/test_launch_claim_registry.py::test_canonical_surface_has_accessibility_primitives`
asserts the literal string `<main>`, while the current source contains
`<main id="main-content" tabindex="-1">`. The targeted test run therefore
failed one assertion even though the current source has a main landmark. This
is a red test-suite result and must not be reported as a clean accessibility
gate. The closure should assert the element structurally, for example with a
tag-boundary regular expression or an HTML parser, then rerun the focused suite.

## Production parity findings

The following checks were run against `https://signkit.work` on 2026-08-13.
The HTTP headers reported `Thu, 13 Aug 2026 05:45:40` through `05:45:50 GMT`
during the probe window.

### Root and retained routes

| URL | Observed response | Exact observation | Contract result |
| --- | --- | --- | --- |
| `/` | `200`, `text/html` | Title is `SignKit - Extract & Sign PDFs Offline`; body contains “100% offline”, “Your files never leave your computer”, “Own Forever”, direct Gumroad links, and “Downloads and updates are managed through your Gumroad account.” | Fails canonical claim and checkout parity |
| `/index.html` | `308` to `/` | Cloudflare normalizes the explicit HTML path, but not with the repository's documented `301` rule | Fails exact route contract |
| `/root` | `200`, `text/html` | Returns the retired landing narrative | Fails; must redirect |
| `/buy` | `200`, `text/html` | Returns a checkout page | Fails; must redirect |
| `/purchase` | `200`, `text/html` | Returns the retired SaaS-style landing page with offline, lifetime, and Gumroad language | Fails; must redirect |
| `/gum` | `200`, `text/html` | Returns a direct Gumroad redirect page | Fails; must redirect |
| `/new` | `200`, `text/html` | Returns the older “Privacy-First Signature Tool” page with “never leave your computer” and direct Gumroad links | Fails; must redirect |
| `/web/live/` and `/web/live/index.html` | `200`, `text/html` | Return the old landing page, not a dependency-only route | Fails; must redirect or be inaccessible as a public entry |
| `/web/new_landing_page/` | `200`, `text/html` | Returns the older landing page with absolute offline language | Fails; must redirect |
| `/web/cloud_workspace/` | `200`, `text/html` | Returns the old landing page rather than the metadata-first workspace proof | Fails; must redirect |
| slash and `.html` variants | Mostly `308` normalization or `200` | They do not produce the required `301` to `/` | Fails exact route contract |

The deployed response does not contain the current `public_surface_boundary`
marker expected by `tools/test_deployed_surface.py`.

### Static assets and machine-readable files

- `/web/live/js/checkout-config.js`: `200`, `text/html`, body begins with the
  old landing document. It is not the repository's JavaScript configuration.
- `/web/live/js/checkout.js`: `200`, `text/html`, body begins with the old
  landing document and does not contain the canonical `checkout_intent` runtime.
- `/robots.txt`: `200`, `text/plain`, which is consistent with the expected
  content type. The body was not used as evidence of route parity.
- `/sitemap.xml`: `200`, `text/html`, body begins with the old landing document.
  This fails the expected XML surface.

Evidence: Tier 4 external runtime observation from response headers and body
samples. This is not payment proof and does not identify which Cloudflare
deployment produced the response.

## Read-only checks and exact outcomes

The following commands were run after sourcing the existing project environment
file. No command staged, committed, reset, checked out, deployed, or edited an
existing file.

```text
source docs/context/agent-start/STEP1_ENV.sh
python3 tools/audit_public_surface.py --strict
```

Outcome: exit 0, `public surface audit: PASS`, 27 local legacy paths, 27
redirect paths, and 13 governed claims. Warnings remain for direct checkout
references and high-risk claims in retained historical pages, plus 30 historical
docs that reference retired routes. Evidence: Tier 2, S1.

```text
source docs/context/agent-start/STEP1_ENV.sh
bash scripts/test-local-landing.sh
```

Outcome: exit 0. Five local landing checks passed; local `/index.html`,
`robots.txt`, `sitemap.xml`, both checkout assets, and the local redirect
manifest passed. Evidence: Tier 2, S1. This does not prove production parity.

```text
source docs/context/agent-start/STEP1_ENV.sh
python3 -m pytest tests/test_launch_claim_registry.py \
  tests/test_public_surface_audit.py tests/test_new_landing_page_contract.py -q
```

Outcome: exit 1, 18 passed and 1 failed. The failure is the literal `<main>`
assertion described above. Evidence: Tier 2, S1 for the 18 passing checks; the
failed check is a current release-gate defect in the test contract.

```text
source docs/context/agent-start/STEP1_ENV.sh
python3 tools/test_deployed_surface.py --base-url https://signkit.work
```

Outcome: exit 1. The probe reported the missing canonical marker, `200` on
retained routes that must be `301`, `308` normalization where exact `301` is
required, and a non-canonical checkout asset. Evidence: Tier 4 external
runtime observation.

```text
source docs/context/agent-start/STEP1_ENV.sh
bash scripts/test-deployment.sh https://signkit.work
```

Outcome: exit 1 after confirming `/` and `/index.html` as `200`; it stopped at
`/root`, which returned `200` instead of the required `301`. Evidence: Tier 4
external runtime observation.

## Historical-claim disposition

| Surface or claim | Disposition | Reason |
| --- | --- | --- |
| Root live “Extract & Sign PDFs Offline” title and description | Retired production claim, open blocker | Contradicts the qualified local-by-default boundary and current registry |
| “100% offline” and “your files never leave your computer” | Not approved for public use | Checkout, licensing, updates, and enquiry boundaries are documented and prevent an absolute claim |
| “Own Forever”, “lifetime”, and direct Gumroad-only framing | Historical checkout and pricing claim | Current copy is provider-neutral while Dodo is unconfigured and the update boundary is qualified |
| `/root`, `/buy`, `/purchase`, `/gum`, `/new`, and retained web folders | Historical review artifacts in the repository; invalid public entrypoints | The current route contract requires a redirect to `/` |
| Historical strategy and landing docs | Preserve as history; do not silently rewrite | Existing docs explain prior decisions, but must not be treated as current release authority |
| `web/cloud_workspace` | Metadata-first proof only, not a public acquisition route or browser signing product | The current product direction distinguishes local execution from future cloud or hybrid topology |

This disposition does not recommend deleting or rewriting historical files. The
closure is deployment alignment and explicit supersession, with the existing
claim registry and route authorities remaining the editable sources of truth.

## Closure commands

These are concrete next commands for the release owner. They were not run in
this worker task because deployment and source changes are explicitly out of
scope.

1. Fix the brittle accessibility assertion in
   `tests/test_launch_claim_registry.py` so it recognizes a `main` element with
   attributes, then rerun:

   ```bash
   source docs/context/agent-start/STEP1_ENV.sh
   python3 -m pytest tests/test_launch_claim_registry.py \
     tests/test_public_surface_audit.py tests/test_new_landing_page_contract.py -q
   ```

2. Re-run the local release gates:

   ```bash
   source docs/context/agent-start/STEP1_ENV.sh
   python3 tools/audit_public_surface.py --strict
   bash scripts/test-local-landing.sh
   python3 -m py_compile serve.py tools/audit_public_surface.py tools/test_deployed_surface.py
   node --check web/live/js/checkout.js
   ```

3. After the release owner reviews the dirty checkout and approves deployment,
   publish the canonical root with the non-mutating deployment wrapper. The
   wrapper itself refuses to run without an explicit confirmation variable:

   ```bash
   source docs/context/agent-start/STEP1_ENV.sh
   DEPLOY_CONFIRM=signkit-landing \
   DEPLOY_BRANCH=landing-page \
   ./scripts/deploy_canonical_landing.sh
   ```

   This command is intentionally a deployment action. It must not be run as
   part of an audit-only worker task.

4. Verify the deployed route, marker, and checkout asset contract:

   ```bash
   source docs/context/agent-start/STEP1_ENV.sh
   python3 tools/test_deployed_surface.py --base-url https://signkit.work
   bash scripts/test-deployment.sh https://signkit.work
   ```

5. Confirm the deployed JavaScript content types and body signatures directly:

   ```bash
   source docs/context/agent-start/STEP1_ENV.sh
   curl -sS -I https://signkit.work/web/live/js/checkout-config.js
   curl -sS -I https://signkit.work/web/live/js/checkout.js
   curl -sS https://signkit.work/web/live/js/checkout.js | rg 'checkout_intent'
   curl -sS -I https://signkit.work/sitemap.xml
   curl -sS https://signkit.work/sitemap.xml | head -n 2
   ```

6. Complete the visual and accessibility closure pass in a real browser at
   desktop, 390px, and 320px widths. Record keyboard traversal, focus visibility,
   reduced-motion behavior, 200% text resize, contrast measurements, target
   sizes, link names, and the first-viewport CTA position. Add assistive
   technology evidence before making a WCAG conformance statement.

## Acceptance boundary and remaining gaps

The exact user-facing change needed is for every public entrypoint to tell the
same qualified SignKit story: a local-first desktop workflow with a configured
checkout boundary, one canonical route, and no unsupported offline or lifetime
guarantees. The user value is a trustworthy and understandable acquisition
path. The team value is one route, claim, and checkout source of truth. The
operational value is a release surface that can be audited and recovered from
HTTP evidence.

Remaining gaps are explicit:

- Production still needs the canonical deployment and post-deploy proof.
- The focused test suite has one brittle failing assertion.
- No payment, receipt, download, licence activation, retry, duplicate, or
  refund evidence was collected.
- No full browser accessibility or assistive-technology audit was collected.
- The visual direction is documented but not an approved production reskin.
- Historical retained files still produce strict-audit warnings by design.

The next review should re-run all commands above against the live deployed
surface and record the final route matrix, content types, canonical marker,
claim samples, and rollback target. Until then, production parity remains open.

## Review passes

### Pass 1: immediate correctness and completeness

Compared current route, claim, checkout, and visual documents with live HTTP
responses. Confirmed the root and retained-route mismatch, the HTML-at-JavaScript
asset failure, and the local accessibility primitives. Outcome: production
parity remains open; no source or existing documentation was edited.

### Pass 2: architecture and long-term viability

Checked for parallel public route and checkout ownership. The repository's
canonical path remains one root page plus one checkout runtime owner. The
closure path is deployment alignment and test hardening, not a new route or a
second checkout implementation. Outcome: no duplicate source of truth was
introduced by this report.

### Pass 3: rule compliance and supervision readiness

Separated static, test, local runtime, and production HTTP evidence. Preserved
historical claims as historical rather than treating them as current truth.
Recorded exact commands, failures, owners, and closure criteria. Outcome: the
artifact is suitable for release-owner handoff, but it does not authorize
deployment or claim accessibility conformance.

## Anything else?

Yes. The live `/sitemap.xml` returning the old HTML page and the checkout
JavaScript URLs returning HTML are especially important because they indicate a
deployment artifact or routing problem broader than a stale headline. Fixing
only visible copy would leave machine-readable and runtime consumers broken.
