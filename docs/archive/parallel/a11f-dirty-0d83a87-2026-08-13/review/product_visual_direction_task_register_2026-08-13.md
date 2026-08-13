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
| VD-01 | Inventory every landing and public surface, including retained and archived variants | primary + landing explorer | in progress | path matrix with visual, claim, asset, route, and test evidence |
| VD-02 | Inventory every new web-app and workspace surface, including concept trees and actual runtime contracts | primary + app explorer | in progress | path matrix with product truth, density, workflow, and reachability evidence |
| VD-03 | Separate observed facts, inferred direction, and unsupported claims for each candidate | primary + research explorer | pending | evidence-tiered comparison |
| VD-04 | Re-run Product Visual Direction Strategist analysis from audience, context, usage intensity, trust, category, and brand relationship | primary | pending | decision-grade brief |
| VD-05 | Research current accessibility, interaction, and category patterns that affect the direction | research explorer | pending | dated sources and applicability notes |
| VD-06 | Select one replacement landing direction and one related app direction, or document why selection is not yet safe | product/design decision | pending | ADR or dated decision addendum |
| VD-07 | Define replacement surface ownership and migration path without creating a second production truth | primary | pending | route and ownership contract |
| VD-08 | Define design tokens, typography, geometry, imagery, motion, and anti-reference rules | design decision | pending | project-local `DESIGN.md` or approved equivalent |
| VD-09 | Create or update replacement-surface implementation tasks only after VD-06 and VD-07 | primary + workers | blocked on direction | task-specific acceptance contracts |
| VD-10 | Add tests for replacement behavior and truth boundaries, not legacy markup | primary + test worker | blocked on direction | S2/S3-sensitive contracts |
| VD-11 | Run browser review at desktop, 390px, 320px, keyboard focus, and reduced motion | QA owner | blocked on implementation | Tier 4 artifact and command log |
| VD-12 | Run three explicit review passes and update all durable docs | primary | pending | pass notes plus acceptance report |

## Implicit tasks added by first-principles review

| ID | Task | Reason |
| --- | --- | --- |
| VD-I01 | Map each candidate to the real desktop extraction and PDF workflow | A visual direction cannot be selected from marketing appearance alone. |
| VD-I02 | Check whether prototype interactions are illustrative or reachable product behavior | A live-looking concept must not become a false capability claim. |
| VD-I03 | Check route and deployment authority before calling a candidate canonical | Public reachability and design preference are different contracts. |
| VD-I04 | Check screenshot and asset semantic accuracy | A visible cleanup state cannot be represented by a signed-PDF frame. |
| VD-I05 | Check content vocabulary across landing, app, desktop, backend, and support docs | Visual hierarchy cannot repair conflicting product mental models. |
| VD-I06 | Preserve and classify all existing parallel changes before any implementation | The worktree is materially dirty and contains unrelated product work. |

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

## Anything else?

Yes. The main risk is not that one page looks weak. The main risk is selecting a
concept because it is visually coherent while its interaction, product truth,
asset evidence, route ownership, or web-app relationship is not ready for
promotion. The direction decision must close those relationships before code
promotion.
