# SignKit product visual direction task register

Date: 2026-08-13  
Scope: landing surfaces, replacement web-app surfaces, visual-direction strategy, and evidence  
Status: discovery in progress

## Why this register exists

The repository contains several landing and web-app directions. Existing route
and QA documents call the root page canonical, but that does not prove that the
root page is the desired future design. This register separates route ownership
from design selection.

The current pass must identify the design direction first. It must not spend the
Product Visual Direction Strategist persona on a surface that the product will
replace.

## Operator redirect

The operator said:

> review the project first to identify all diff.design directions on the landing and the new web app, then run the persona again

The operator later clarified:

> you are wasting the persona on something we are going to replace

Consequence: legacy root and current metadata workspace changes are not the
design target for this pass. Their existing behavior remains evidence and must
be preserved until a replacement route and migration decision are approved.

## Explicit tasks

| ID | Task | Owner | Status | Evidence or closure check |
| --- | --- | --- | --- | --- |
| VD-01 | Inventory every landing and public surface, including retained and archived variants | primary + landing explorer | complete | Explorer matrix covers root, live, new, concepts, archives, backups, siblings, redirects, sitemap, and deployment helpers. Tier 1. |
| VD-02 | Inventory every new web-app and workspace surface, including concept trees and actual runtime contracts | primary + app explorer | complete | Explorer matrix covers cloud workspace, concepts, backend, desktop relationship, tests, and capability boundaries. Tier 1 plus prior Tier 3/4 records. |
| VD-03 | Separate observed facts, inferred direction, and unsupported claims for each candidate | primary + research explorer | complete | Strategy brief separates observed, inferred, unproven, and falsifiers. |
| VD-04 | Re-run Product Visual Direction Strategist analysis from audience, context, usage intensity, trust, category, and brand relationship | primary | complete | `docs/review/product_visual_direction_strategy_2026-08-13.md`. |
| VD-05 | Research current accessibility, interaction, and category patterns that affect the direction | research explorer | complete | WCAG 2.2, WAI APG, Apple Preview, Adobe, DocuSign, and Dropbox Sign references recorded in explorer output and strategy brief. |
| VD-06 | Select one replacement landing direction and one related app direction, or document why selection is not yet safe | product/design decision | complete for candidate | ADR-0145 selects a non-production document registration studio candidate. Promotion remains gated. |
| VD-07 | Define replacement surface ownership and migration path without creating a second production truth | primary | complete for candidate | ADR-0145 keeps the candidate under `web/concepts/2026-08-13-document-registration-studio/`; route promotion, checkout, and retirement remain release gates. |
| VD-08 | Define design tokens, typography, geometry, imagery, motion, and anti-reference rules | design decision | complete for candidate | Root `DESIGN.md` defines the document registration studio system. |
| VD-09 | Create or update replacement-surface implementation tasks only after VD-06 and VD-07 | primary + workers | complete for candidate | Isolated landing and metadata workbench created. No legacy route files are in the write set. |
| VD-10 | Add tests for replacement behavior and truth boundaries, not legacy markup | primary + test worker | complete for candidate | `tests/test_document_registration_studio_contract.py`: 4 passed, plus an S2 mutation probe for the truth boundary. |
| VD-11 | Run browser review at desktop, 390px, 320px, keyboard focus, and reduced motion | QA owner | complete for candidate | Tier 4 Chrome matrix passed at 1440, 390, and 320 pixels for both surfaces; no overflow or console/page errors. |
| VD-12 | Run three explicit review passes and update all durable docs | primary | in progress | Implementation and browser evidence recorded; final release gates and three-pass compliance note remain. |

## Implicit tasks added by first-principles review

| ID | Task | Reason |
| --- | --- | --- |
| VD-I01 | Map each candidate to the real desktop extraction and PDF workflow | A visual direction cannot be selected from marketing appearance alone. |
| VD-I02 | Check whether prototype interactions are illustrative or reachable product behavior | A live-looking concept must not become a false capability claim. |
| VD-I03 | Check route and deployment authority before calling a candidate canonical | Public reachability and design preference are different contracts. |
| VD-I04 | Check screenshot and asset semantic accuracy | A visible cleanup state cannot be represented by a signed-PDF frame. |
| VD-I05 | Check content vocabulary across landing, app, desktop, backend, and support docs | Visual hierarchy cannot repair conflicting product mental models. |
| VD-I06 | Preserve and classify all existing parallel changes before any implementation | The worktree is materially dirty and contains unrelated product work. |

## Discovery evidence artifacts

- `docs/review/product_visual_direction_strategy_2026-08-13.md`
- `docs/decisions/ADR-0145-signkit-replacement-visual-direction.md`
- `DESIGN.md`
- Local visual inventory screenshots:
  `/Users/pranay/.codex/visualizations/2026/08/13/signkit-direction-inventory/`
- Explorer outputs from the landing, app, and strategy lanes. The agents made no
  repository edits.

## Current scope boundary

In scope now:

- read-only project and runtime inventory;
- visual-direction comparison;
- persona analysis;
- external research where it changes the decision;
- task and decision documentation;
- replacement implementation after direction selection.

Out of scope until an explicit release decision:

- production deployment;
- route promotion of a concept;
- checkout or payment changes;
- deletion of legacy or concept files;
- staging, commit, push, reset, or cleanup of the dirty worktree.

## Evidence discipline

- Tier 0: hypothesis or design proposal.
- Tier 1: static code and documentation inspection.
- Tier 2: focused test execution.
- Tier 3: integration or end-to-end flow.
- Tier 4: browser or operator observation.
- Tier 5: deployed or production-like verification.

Passing tests will be labelled with sensitivity. A contract that only tests
legacy markup cannot be used as evidence for replacement design quality.

## Update log

### 2026-08-13: register created

Created after the operator redirected the work from legacy-surface polishing to
full design-direction discovery. No product implementation was authorized by
this register entry.

### 2026-08-13: discovery and persona pass complete

The inventory found multiple landing directions and one real metadata-first web
workspace. The selected replacement candidate combines customer-work evidence,
Product Museum causality, and a quieter registration-studio system. ADR-0145 and
`DESIGN.md` record the decision. Legacy route promotion remains blocked.

### 2026-08-13: isolated replacement candidate implemented

Created `web/concepts/2026-08-13-document-registration-studio/` with a landing
candidate, a metadata-first workspace candidate, native controls, bounded
source-to-ready state changes, explicit illustrative labels, and no backend or
route changes. The candidate uses no product screenshots, so asset
authorization is not silently assumed.

Static evidence: `git diff --check`, both JavaScript syntax checks, and 4
focused contract tests passed. The contract's S2 mutation probe removed the
illustrative boundary and detected the mutation.

Browser evidence: Chrome headless with reduced motion at 1440x900, 390x844,
and 320x844. Both surfaces returned HTTP 200, had no horizontal overflow, no
console or page errors, and exercised state selection, arrow-key movement,
record selection, and review filtering. Captures are in the local visual
inventory directory. This is Tier 4 local evidence, not production parity.
The first browser pass exposed a focus-index synchronization defect in the
landing step controls; the focus handler was added and the rerun advanced from
Source to Mark at all three widths.

Three-pass note:

1. Immediate correctness: landing states and workspace records are native,
   truth-bound, responsive, keyboard-addressable, and visually inspected.
2. Architecture: candidate ownership is isolated, no production route or API
   was added, and legacy files and parallel work were preserved untouched.
3. Compliance: docs, evidence tiers, reduced motion, focus treatment, and
   release blockers are recorded. Promotion still needs product, claim,
   deployed-parity, and comprehension review.

## Anything else?

Yes. The main risk is not that one page looks weak. The main risk is selecting a
concept because it is visually coherent while its interaction, product truth,
asset evidence, route ownership, or web-app relationship is not ready for
promotion. The direction decision must close those relationships before code
promotion.
