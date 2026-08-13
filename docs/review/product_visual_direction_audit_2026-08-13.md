# SignKit product visual direction audit

Date: 2026-08-13  
Scope: canonical landing page, existing browser workspace, production surface  
Persona: Product Visual Direction Strategist  
Status: Audit complete; implementation plan requires product approval before a production reskin

## Executive decision

SignKit should use a **calm document-operations studio** direction:

- warm paper and ink as the acquisition foundation;
- restrained dark tool surfaces for product proof and high-consequence actions;
- one controlled cyan-green signal for local status and successful preparation;
- a small amber signal for price and attention, not for general decoration;
- editorial display typography for the feeling of relief and completion;
- neutral sans typography for controls, workflow labels, and evidence;
- low-noise motion that reveals document state and causality;
- squared, deliberate geometry with moderate radius, not inflated SaaS cards;
- a clear visual distinction between current local proof and future cloud or hybrid direction.

This direction is appropriate because SignKit handles sensitive documents that
must be finished correctly. The product needs authority and calm, but it does
not need to look like a security terminal, a consumer signing marketplace, or
a generic AI SaaS dashboard.

The current repository has a real landing page and a real browser workspace,
so a plan-only response is not required. The current surfaces are not yet a
finished visual system. The landing is a conversion page with a neo-brutalist
launch treatment. The browser workspace is a metadata-first control-plane proof
with a more editorial and operational treatment. Both are useful evidence, but
their relationship needs to become explicit and their usability gaps need
closure before production promotion.

## Scope and evidence

### Surfaces reviewed

| Surface | Role | Review result |
| --- | --- | --- |
| `/index.html` | Canonical acquisition and checkout surface | Reviewed statically, in a local browser, at desktop and mobile widths |
| `web/cloud_workspace/index.html` | Existing metadata-first browser workspace | Loaded and visually inspected; not a document-signing engine |
| `web/live/*` | Shared checkout assets and retained historical landing surface | Reviewed as dependency and historical surface, not as a production landing owner |
| `https://signkit.work/` | Current production surface | Rechecked; still serves the older offline/lifetime narrative |
| `web/concepts/*` and design docs | Prior explorations and direction records | Sampled to avoid re-proposing rejected or superseded directions |

### Evidence tiers

- Tier 1: static inspection of HTML, CSS, JavaScript, route authorities, and
  design records.
- Tier 2, S1: focused contract and public-surface tests passed. These tests
  prove that the assertions run and pass, not that they are mutation-sensitive.
- Tier 4: local browser load, DOM inspection, responsive measurements, checkout
  fallback interaction, console inspection, and screenshots at `1440x900` and
  `390x844`.
- Tier 4 external observation: the production page still exposes the older
  offline, lifetime, and direct Gumroad story. Production parity is not claimed.

### Commands and observations

```text
/Users/pranay/Projects/agent-start --project ...
  Generated the project context pack. Shared index refresh was unavailable
  because /Users/pranay/Projects/workspace_memory/.venv/bin/python is missing.

python3 tools/audit_public_surface.py --strict
  PASS. 27 local legacy paths and 27 deployed legacy paths were inventoried.
  Warnings remain for claims in retained historical pages.

python3 -m pytest tests/test_new_landing_page_contract.py \
  tests/test_public_surface_audit.py tests/test_launch_claim_registry.py -q
  19 passed. Evidence level: Tier 2, S1.

node --check web/live/js/checkout.js
node --check web/live/js/analytics.js
node --check web/live/js/animations.js
node --check web/live/js/main.js
python3 -m py_compile tools/audit_public_surface.py tools/test_deployed_surface.py
  PASS. Evidence level: Tier 1 syntax validation.

Local browser at http://127.0.0.1:8765/index.html
  No console messages. Six images loaded. No missing alt attributes. One main
  landmark. No horizontal overflow at 390px. Dodo fallback focus moved to the
  provider configuration note. Gumroad was the configured primary state.

Production browser and web inspection at https://signkit.work/
  Older root content remains live, including absolute offline and lifetime
  wording. This is external production evidence, not local implementation
  proof.
```

Visual evidence is preserved outside the repository workspace at:

- `/Users/pranay/.codex/visualizations/2026/08/13/signkit-design-audit/desktop.png`
- `/Users/pranay/.codex/visualizations/2026/08/13/signkit-design-audit/mobile.png`
- `/Users/pranay/.codex/visualizations/2026/08/13/signkit-design-audit/workspace.png`

## Current visual diagnosis

### What is working

1. The canonical root page has a clear job, a visible product preview, a one-time
   price boundary, a local-processing qualification, and a direct path to
   support and policy content. This follows the brand narrative contract.
2. The local page uses a restrained number of strong colours. Navy ink, paper,
   cyan-green, indigo, and amber create a recognizable identity instead of a
   default dark SaaS palette.
3. The product screenshots are real workflow evidence. They show extraction,
   cleanup, and PDF work without inventing a cloud-signing dashboard.
4. The browser workspace has a credible control-plane metaphor. Its split
   dark-story and paper-form layout makes the local versus metadata boundary
   legible, and its copy states that Cloud and Hybrid are planned directions.
5. The current claims are materially safer than the production page. The local
   implementation says "locally by default", identifies checkout as an external
   boundary, and avoids customer counts and benchmark claims.

### What is not yet working

1. **The emotional direction is split.** The landing reads as a launch poster:
   heavy outlines, offset shadows, bright badges, pill price treatment, emoji
   bullets, and repeated card blocks. The workspace reads as an editorial
   operations console with serif display type, paper grain, and dense control
   language. The difference could be intentional, but the current records do
   not define shared tokens or a transition rule between the two.
2. **The landing leads with privacy and price before the completion feeling.**
   The current hero headline is strong and specific, but the surrounding
   treatment makes "local" and "$29" compete with the core emotional promise:
   finish a consequential PDF without fighting document tools. The Product
   Museum decision says the visitor should understand the job and operating
   feeling before internal topology or privacy becomes the centre of gravity.
3. **The page is too card-heavy for the actual workflow.** The three hero cards,
   three trust cards, three screenshots, dark purchase card, enquiry card, FAQ
   grid, and footer columns create a long sequence of separate boxes. This is
   a conventional marketing composition, not yet a causal source-to-PDF
   experience.
4. **The signature interaction is missing.** The page displays screenshots but
   does not let a visitor operate a small semantic sequence from source
   document to selected mark to cleaned result to placed PDF. Existing product
   direction requires one short, keyboard-operable, product-specific
   interaction.
5. **Mobile conversion hierarchy is weak.** At `390x844`, the first hero CTA
   begins around y=1055 because the hero stacks the copy, three cards, and
   preview before the action. The page has no horizontal overflow, but the
   first useful action is not present in the first viewport.
6. **The canonical HTML is structurally unfinished.** The page has one `main`
   element but no semantic `footer` landmark. Its heading anchors have
   `scroll-margin-top: 0px`, there is no skip link, and five of six images have
   no intrinsic `width` and `height` attributes or lazy-loading policy. These
   are concrete usability and performance gaps, not taste differences.
7. **The browser workspace has a stronger system language than the landing,
   but it remains a proof surface.** It provides account, metadata, template,
   transition, and local inspection concepts. It must not be styled or named as
   a full web signing product until the document-byte and execution contract is
   closed.
8. **The production page is visually and semantically stale.** The live page
   still says "100% offline", "your files never leave your computer", and
   "own forever". It also uses the old direct Gumroad and placeholder-link
   pattern. This is a release and trust blocker, not a local visual polish
   task.

## Personality profile

Scores describe the recommended direction, not a claim that the current page
already meets them.

| Dimension | Recommended position | Current landing | Current workspace |
| --- | ---: | ---: | ---: |
| Serious to playful | 82% serious | 58% serious | 88% serious |
| Conservative to experimental | 56% experimental | 72% experimental | 48% experimental |
| Warm to clinical | 62% warm | 55% warm | 64% warm |
| Minimal to expressive | 62% minimal | 38% minimal | 68% minimal |
| Premium to utilitarian | 72% premium | 61% premium | 66% premium |
| Human to technical | balanced, 52% human | 58% human | 42% human |
| Calm to energetic | 78% calm | 48% calm | 76% calm |
| Familiar to distinctive | 64% distinctive | 72% distinctive | 70% distinctive |

The direction deliberately keeps distinction below novelty. The product's
competitive advantage is trustworthy completion, not an unusual visual trick.

## Product Visual Direction Brief

### Product perception target

SignKit should feel like a quiet, capable document studio for work that matters.
The user should feel that the document is under control, the next decision is
visible, and the work can be finished without handing sensitive files to a
large platform.

### Desired attributes

- controlled;
- precise;
- calm;
- warm but not cute;
- technically credible;
- operator-grade;
- quietly premium;
- slightly distinctive;
- honest about current versus planned capability.

### Attributes to avoid

- cyberpunk or neon security theatre;
- generic purple-gradient SaaS;
- consumer e-signature marketplace styling;
- inflated glassmorphism;
- cartoon or emoji-led trust signals;
- fake dashboards or fictional document states;
- urgency-heavy launch advertising;
- dense terminal or control-room language on the acquisition page.

### Theme recommendation

Use a warm-light acquisition surface as the primary identity. Use dark ink
panels for the hero proof and high-consequence purchase region. Do not make a
dark theme the primary landing identity. The product is document-heavy, often
read in bright offices, and asks visitors to inspect screenshots and policy
boundaries. A light paper field gives reading and evidence priority.

The browser workspace may use a dark operational frame because it represents
state and control. That difference is appropriate if it is defined as a
surface role, not left as accidental brand drift.

### Token direction

These are design-direction tokens for the next implementation pass. They are
not permission to add a second CSS source of truth before an implementation
decision is accepted.

| Role | Direction | Example |
| --- | --- | --- |
| Paper | warm, low-glare reading field | `#F7F4EC` |
| Ink | deep green-black for authority | `#102F2B` |
| Muted ink | readable secondary copy | `#40504B` |
| Local signal | cyan-green for current/local/ready state | `#B9D95D` or `#00A88F` |
| Attention | amber for price and review attention | `#E8A92E` |
| Action | indigo only for a primary purchase or selected action | `#4F46E5` |
| Rule | quiet neutral divider | `#D9D6CC` |

Semantic roles must own these values. Do not use cyan-green, amber, and indigo
as equal decorative accents in every card.

### Typography

- Display: a restrained editorial serif for the emotional promise and chapter
  titles. Use it for a few high-value statements, not every heading.
- Body and controls: a neutral sans with strong numerals and clear x-height.
- Utility: a compact mono or tracked sans for workflow labels, statuses, and
  evidence captions.
- Use `text-wrap: balance` or `text-wrap: pretty` on large headings where the
  browser baseline supports it.
- Keep body copy at a readable size on mobile. Do not make the full-page
  screenshot composition the unit of legibility.

### Geometry and layout

- Use a page rhythm based on chapters and transitions, not a grid of equal
  cards.
- Keep moderate radius on containers. Reserve pills for statuses, prices, and
  compact controls.
- Replace repeated offset shadows with one or two intentional depth cues.
- Give the proof interaction the strongest visual focus. Let trust and policy
  content become quieter evidence below it.
- Keep the primary CTA in the first mobile viewport after the headline and one
  proof sentence. Move feature detail below the first action.

### Motion

- Use one orchestrated state transition for the source-to-PDF proof.
- Prefer opacity and transform. Avoid motion that only decorates card entry.
- Respect `prefers-reduced-motion` and preserve the same state meaning without
  animation.
- Make state changes interruptible and keyboard-operable.

### Imagery

- Use real current product captures for current capability.
- Use a deliberately prepared, authorized demonstration document before public
  promotion. Do not expose an accidental sample signature as brand imagery.
- Use abstract diagrams for Cloud and Hybrid direction. Label them as planned
  or illustrative.
- Use no stock photography. The product's own document artifacts are the
  distinctive visual material.

### Signature element

The memorable element should be a **document completion rail**: a short,
operable strip that shows `source -> mark -> clean -> place -> ready` and lets
the visitor advance through the real current workflow. It should feel like a
calm instrument panel, not a simulated SaaS dashboard. This is a justified
risk because it expresses SignKit's actual product difference and reinforces
the Product Museum decision.

## Findings and closure plan

| ID | Priority | Finding | Evidence | Closure path | Owner / gate |
| --- | --- | --- | --- | --- | --- |
| PV-01 | P0 | Production is not aligned with the canonical visual and claim surface | Production web observation; `docs/review/production_surface_mismatch_2026-08-12.md` | Approve exact artifact, deploy through `scripts/deploy_canonical_landing.sh`, run deployed route and claim smoke, record deployment and rollback target | Release owner, Web Platform, Product |
| PV-02 | P1 | Landing lacks the required causal product interaction | Product Museum ADR and current root screenshots | Build one semantic source-to-PDF interaction against current capability evidence; add keyboard, reduced-motion, responsive, and mutation-sensitive checks | Product and Design approval before implementation |
| PV-03 | P1 | Mobile CTA appears after the first viewport | Tier 4 local browser measurement at `390x844` | Reorder hero to headline, proof, CTA, then details; verify CTA visibility and touch target at 390px and 320px | Design and QA |
| PV-04 | P1 | Landing and workspace have no documented shared visual contract | Tier 1 comparison of `index.html` and `web/cloud_workspace/styles.css` | Add a visual-system ADR or extend this brief with shared role tokens, typography roles, spacing rhythm, and allowed surface-specific variation | Product / Design |
| PV-05 | P1 | Landing structure misses semantic footer, skip link, anchor offset, and image dimensions | Tier 1 and Tier 4 DOM inspection | Add semantic footer, skip link, `scroll-margin-top`, intrinsic image dimensions, and appropriate lazy-loading; add focused contract tests | Web Platform / QA |
| PV-06 | P2 | Historical variants and strategy docs still contain stronger or retired language | Strict audit warnings and `docs/landing_page_strategy/*` | Keep historical files, append dated supersession notes, and make tooling distinguish historical claim text from editable production copy | Documentation owner |
| PV-07 | P2 | Public screenshots need an authorization and freshness record | Existing product evidence docs and current screenshot assets | Create a public-demo asset manifest with source capture, approval, date, redaction status, and replacement trigger | Product Ops |
| PV-08 | P2 | Current checkout provider state is honest locally but production activation remains unverified | Local browser fallback interaction; public-surface QA matrix | Run configured-provider and fallback tests against the deployed asset, then attach event and route evidence | Platform / Analytics |

## Proposed implementation order

This is the long-term path. It is intentionally staged so the landing does not
receive a cosmetic reskin that leaves the product story unchanged.

### Stage A: close trust and structural blockers

1. Reconcile production with the canonical root artifact.
2. Add the semantic and performance primitives to the canonical page.
3. Create the public-demo asset manifest and authorize the demonstration files.
4. Keep claim registry, legal copy, checkout configuration, and route authorities
   in one release record.

### Stage B: make the visual system explicit

1. Accept or revise this visual direction brief.
2. Record the shared token and typography contract for the landing and workspace.
3. Define surface roles: acquisition paper, product proof dark panel, workspace
   operational frame, and future-direction lab.
4. Define motion, focus, reduced-motion, breakpoint, and image performance
   budgets.

### Stage C: replace screenshot tourism with a causal proof

1. Build the document completion rail as a semantic DOM interaction.
2. Drive the interaction with current product evidence and explicitly bounded
   states.
3. Move supporting feature cards below the interaction and reduce repeated
   card framing.
4. Put privacy, provider, licence, and refund details after the job and proof,
   while keeping them easy to reach.

### Stage D: verify the whole customer and operator workflow

1. Browser verification at desktop, 390px mobile, and 320px narrow mobile.
2. Keyboard path through the proof interaction, CTA, support, and policy links.
3. Reduced-motion verification with state meaning preserved.
4. Accessibility, image, and route contract tests with a deliberate mutation
   check for each fixed invariant.
5. Deployed route smoke, provider-state smoke, and production screenshot review.

No stage should be marked complete from a passing static test alone.

## Architecture and source-of-truth review

- The canonical acquisition source is `index.html`.
- Checkout behavior remains owned by
  `web/live/js/checkout-config.js` and `web/live/js/checkout.js`.
- Route authority remains split only between `_redirects` and `serve.py`, as
  currently documented. No new landing route should be created.
- Current local product proof must come from the desktop release bundle and
  authorized runtime captures.
- `web/cloud_workspace` remains a metadata-first control-plane proof. It must
  not become a second acquisition page or imply browser-native document
  execution before that contract exists.
- Historical variants remain useful for comparison and recovery. They are not
  alternate design sources of truth.

## Three-pass review record

### Pass 1: immediate correctness and completeness

Checked the live canonical page, current workspace, local assets, route/claim
contracts, mobile overflow, CTA placement, checkout fallback, console output,
and screenshot evidence. Found the structural and mobile gaps listed in PV-03
and PV-05. No source code was edited in this audit.

### Pass 2: architecture and long-term viability

Compared the surfaces with the brand narrative, experience-system direction,
Product Museum decision, ownership matrix, and public-surface map. Confirmed
that a cosmetic reskin would be the wrong next move. The durable next unit is a
shared visual contract plus one causal proof interaction, while preserving the
canonical route and current evidence boundaries.

### Pass 3: rule compliance and supervision readiness

Confirmed that local claims and checkout state are qualified, that retained
historical claims are surfaced as warnings, and that production parity remains
open. Recorded the missing shared-index dependency, exact verification
commands, evidence tiers, owners, gates, and closure paths. No commit or
deployment action was taken.

## Anything else?

Yes. The highest-risk failure is not that the landing looks imperfect. It is
that production, repository, checkout, and future topology surfaces can tell
different stories. The next design unit must therefore ship with visual
direction, claim parity, route parity, evidence freshness, and runtime proof as
one acceptance contract.

## Confidence and remaining uncertainty

Confidence: 0.87.

The local design diagnosis is supported by Tier 1 and Tier 4 evidence. The
production diagnosis is supported by a current external page observation, but
Cloudflare deployment identity, cache state, and the exact release artifact
still require the release owner to verify. The visual direction is a strategic
recommendation, not an approved implementation decision. The next hardening
step is approval of this brief followed by the staged implementation and
verification contract above.
