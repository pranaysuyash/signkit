# SignKit CDO Product System Audit

Date: 2026-08-12
Scope: local desktop app, new landing page, current browser workspace, and the planned Local, Cloud, Hybrid product direction
Operating model: solo founder with agents; no deployment, commit, legal, or certification work included in this execution slice

## Executive diagnosis

The product has real local workflow depth, but the system currently describes itself differently at each boundary. The desktop app exposes a local companion backend as if it were cloud sync; the browser workspace describes metadata-only proof as cloud execution; the new page describes a local-first tool without showing the planned topology choice. The strategic risk is not visual inconsistency alone. It is that customers cannot form one reliable mental model of where their documents run, what the web product does, and what is actually available today.

## Product truth map

| Surface | Current capability | Customer-facing role | Evidence |
| --- | --- | --- | --- |
| Desktop app | Extraction, Vault, PDF placement/export, workflow engine, grants, review/retry paths | Current Local product | Static code plus existing desktop runtime evidence |
| Browser workspace | Authenticated metadata register, templates, state transitions, receipts, synthetic proof fixture | Current metadata-only browser proof; not document execution | Tier 4 runtime proof in `docs/expansion/SIGNKIT_CONTRACTDESK_WEB_RUNTIME_PROOF_2026-08-12.md` |
| New page | Acquisition and product narrative | Must explain the current Local product and planned topology model without implying Cloud or Hybrid is shipped | Browser QA plus static contract |
| Cloud topology | Complete browser-native execution, storage, recovery, audit, and support | Planned direction | Architecture decision, no production proof |
| Hybrid topology | Local execution with explicit connected coordination and reversible sync categories | Planned direction | Architecture decision, no production proof |

## Systemic findings

### P0: Boundary language contradicts the architecture

The local application used `Backend: Online`, `Cloud-sync active`, and `cloud features enabled` for a local companion service. The browser workspace used `New cloud execution` for metadata-only state. This is a structural trust failure because the words change the implied data boundary and capability contract.

### P1: The product model is hidden instead of taught

Local, Cloud, and Hybrid exist in strategy and architecture records but were not presented as a customer-visible product choice. Without a topology model, the new page makes the web direction look like an unrelated future and the desktop app look like an isolated utility.

### P1: Current proof and future direction are mixed

The browser workspace has a valuable receipt and execution-passport interaction, but the UI does not sufficiently distinguish live metadata behavior from synthetic proof or future cloud-native execution. This creates maturity risk even where the underlying proof is honest.

### P1: The product is feature-rich but workflow-poor at the narrative layer

The local code has the right arc: capture, extract, clean, store, place, review, export, repeat. The public surface still needs to lead with the larger job: prepare sensitive PDFs correctly, locally, and repeatedly.

### P2: Commercial and capability language is fragmented

Older tier and launch specifications use annual Basic/Professional/Enterprise framing while the newer direction uses Local, Cloud, Hybrid, workflow modules, and topology-aware value. This is a planning conflict, not a reason to add more pricing tiers now.

## First-principles product direction

SignKit should be one document-execution system with three deliberate operating models:

- **Local:** the complete current product for private document preparation on one device.
- **Cloud:** a complete browser-native product only when it can own execution, storage, recovery, audit, and support without desktop dependency.
- **Hybrid:** local execution plus explicit, inspectable coordination. It must never mean silent universal sync.

The unifying product object is an **Execution Passport**: template/version, allowed topology, roles, data boundary, execution state, evidence, recovery action, and source of truth. The user should be able to answer where work ran, what left the device, what happened, and what can happen next.

## Priority task ledger

| Priority | Task | Status | Closure evidence |
| --- | --- | --- | --- |
| P0 | Align topology vocabulary across desktop, browser, and public surfaces | Complete in this slice | 27 focused tests, browser recheck, Lighthouse |
| P0 | Keep Local as a complete, first-class product rather than a degraded plan | In progress | Local runtime audit of extraction, PDF, Vault, and workflow journeys |
| P1 | Make the new page teach Local, Cloud, Hybrid and status-label future capability | Complete in this slice | New-page contract and browser audit |
| P1 | Make browser workspace disclose metadata-only proof and synthetic fixture scope | Complete in this slice | Workspace contract, one main landmark, browser proof |
| P1 | Establish Execution Passport as the shared workflow vocabulary and data contract | Next product unit | Schema/mapping decision plus local/browser integration fixtures |
| P1 | Build one complete Local vertical workflow around a repeated job | Open | One end-to-end workflow with recovery, receipt, and operator visibility |
| P2 | Decide first Cloud-native workflow from buyer/problem evidence | Open | Founder decision, workflow evidence, and capability/data contract |
| P2 | Define Hybrid sync categories and authority rules | Open | Explicit data taxonomy, conflict policy, deletion/recovery behavior |
| P2 | Reconcile older pricing/spec language with topology-aware packaging | Open | One commercial model document; no public pricing change in this slice |

## What changed in this slice

- Desktop status language now names the local companion boundary rather than implying cloud sync.
- The new page now presents Local, Cloud, and Hybrid as one product model, with only Local marked available now.
- The browser workspace now calls its current surface a metadata-only browser proof, renames the creation action as a workflow record, and exposes the topology choice.
- The browser workspace now keeps one main landmark, names the passport's current metadata boundary, and avoids presenting a metadata record as document execution.
- The new page pricing list now describes the actual personal workflow and its footer links back to the topology model.
- Added contract coverage for the shared vocabulary and future-capability labelling.

## Verification completed in this slice

- Static and focused tests: 27 passed across the new page, topology contract, governed claims, landing surface, and public-surface audit.
- JavaScript syntax: `web/cloud_workspace/app.js`, `web/new_landing_page/js/main.js`, and `web/live/js/checkout.js` passed `node --check`.
- Browser new page: one main landmark, no console errors, no horizontal overflow, Local/Cloud/Hybrid section rendered, pricing copy and topology footer link observed.
- Browser workspace: one main landmark, `SECTION` app shell, one form grid, `Create workflow record` observed, topology switchboard rendered, no console errors, no horizontal overflow.
- New-page Lighthouse: Accessibility 100, SEO 100, Best Practices 77, Agentic Browsing 97 mobile / 99 desktop.
- Workspace Lighthouse: Accessibility 96, SEO 91, Best Practices 100, Agentic Browsing 100 mobile / 99 desktop.
- Desktop Qt runtime test remains unrun because the current checkout has no `.venv/bin/python` or `.venv/bin/pytest`, and the system Python has no PySide6. The static desktop topology contract passed instead.

Evidence sensitivity: the contract tests reached S2 for the new topology invariants because each was observed failing before its implementation patch and passing afterward. Browser observations are Tier 4 for the rendered static surfaces. Lighthouse scores are supporting audit evidence, not proof of product capability.

## What is not claimed

- Cloud document execution is not shipped.
- Hybrid synchronization is not shipped.
- The browser proof does not create a signed document.
- Local processing language is not a certification or legal-validity claim.
- No deployment or commit status is included in this product audit.

## Next implementation unit

The next local product unit is the Execution Passport contract and a read-only projection from the local workflow/job model to the browser metadata model. It should begin with schemas, ownership, topology, event receipts, idempotency, and recovery semantics before any document upload or sync. This is the smallest unit that makes the vision real without creating a second product or a second execution engine.
