# SignKit Content Designer Persona Audit

Date: 2026-08-13
Scope: content design, information architecture, terminology, workflow guidance, trust language, accessibility language, documentation, and content governance across the current SignKit product surfaces
Persona source: `/Users/pranay/.codex/attachments/82ded2f3-3539-4d50-bb83-84d1265d8ee4/pasted-text.txt`
Status: audit artifact complete; no product implementation changes were made in this audit
Confidence: 0.88

## Executive result

SignKit has enough product depth to support a strong content system. It already contains a coherent underlying job:

1. bring in a source image or PDF,
2. select and clean a signature image,
3. inspect the result,
4. save a reusable local asset,
5. place that asset on a PDF,
6. review the output,
7. export it,
8. optionally repeat the work through a controlled local workflow.

The current content experience does not teach that job as one system. It presents a set of tabs, internal implementation nouns, technical controls, policy statements, legacy names, and future workflow concepts. A user can often complete an action after discovering the interface, but the user is asked to reconstruct the product model while working.

The content design diagnosis is therefore:

> SignKit has a credible local document workflow, but its content system is not yet a single, user-readable contract for what the product does, what each state means, what the user should do next, and what the product does not claim.

This is a content architecture problem, not a request for more marketing copy. The long-term fix is a governed vocabulary, state model, content matrix, recovery language system, and evidence-aware documentation source map. Copy changes should follow that model.

### Highest-risk findings

| ID | Severity | Finding | User consequence |
| --- | --- | --- | --- |
| CD-P0-01 | P0 | Product boundary terms contradict one another. The onboarding dialog says “Works 100% offline”; the bootstrap log says “cloud features enabled”; the public and product contracts correctly qualify local processing. | Users cannot reliably tell whether documents leave the device, whether a local companion is a cloud service, or whether a PDF action is image placement or regulated signing. |
| CD-P0-02 | P0 | User-facing nouns are not canonical across desktop, browser, public, help, legal, and legacy surfaces. | Users must translate between “Signature Extraction”, “My Signatures”, “Notary Vault”, “PDF Signing”, “Execution Passport”, “recipe”, “job”, “grant”, and “workflow record”. |
| CD-P0-03 | P0 | High-consequence states expose technical or overly strong language without enough recovery guidance. | A failed export, authorization block, vault failure, or verification result can leave the user unsure whether data was changed, whether the result is trustworthy, and what action is safe next. |
| CD-P1-01 | P1 | Onboarding combines product positioning, manual extraction, backend health, licensing, pricing, plan personas, and recurring workflow automation in one dialog. | First-run users receive too many decisions before completing their first useful task. |
| CD-P1-02 | P1 | Extraction controls expose implementation concepts instead of a clear decision path. | “Standard (Threshold)”, “Forensic (Ink Separation)”, “Auto Clean”, threshold values, color hex values, and mode tooltips make the user choose algorithms before seeing the result. |
| CD-P1-03 | P1 | PDF language says “signing” and “signed PDF” where the current product boundary is image signature placement and export. | The wording can imply identity verification, cryptographic signing, or legal validity that the product does not establish. |
| CD-P1-04 | P1 | Local workflow states and browser workflow states describe related work with different state vocabularies. | Operators cannot form one durable model of what “needs review”, “retry”, “approved”, “signed”, “exported”, “completed”, and “exception” mean across surfaces. |
| CD-P1-05 | P1 | Help and user-guide content is materially stale or stronger than the current governed claims. | A user can receive contradictory instructions about controls, supported platforms, offline behavior, licensing, version updates, and support contacts. |
| CD-P1-06 | P1 | Accessibility labels are incomplete for interactive controls, especially compact controls, navigation, sliders, icon-only PDF navigation, and status changes. | A keyboard or assistive technology user cannot reliably identify the control, its current value, its result, or the next action. |
| CD-P1-07 | P1 | Browser workspace language is honest about metadata-only proof, but still introduces “control plane”, “topology”, “execution passport”, and “metadata-first” before the basic user job is established. | Operators may understand the architecture before they understand how to create, review, recover, and close a workflow record. |
| CD-P1-08 | P1 | Retained legacy surfaces contain stronger claims, direct checkout paths, placeholder values, and social proof outside the canonical claim contract. | A historical or alternate entry path can still create an expectation the current product cannot support. |
| CD-P2-01 | P2 | Empty, loading, success, warning, destructive, and recovery states are not governed as a reusable content pattern. | Similar situations receive different verbs, different detail levels, and different amounts of recovery guidance. |
| CD-P2-02 | P2 | Technical identifiers, raw paths, raw exception strings, and provider implementation details appear in user-facing surfaces. | The product feels like an internal console at the moment users need confidence. |
| CD-P2-03 | P2 | The product has strong domain depth but weak comprehension evidence. | Static contract tests can prove strings and routes, but cannot prove that a new user understands the workflow or that an operator can recover from a failed run. |

These priorities are not a claim that the product is unusable. They identify the order in which content architecture should be corrected so later polish does not reinforce contradictory mental models.

## 1. Persona lens and method

The persona source defines the content designer as responsible for the information, language, structure, and guidance that let a user accomplish a goal. It explicitly expands the job beyond copywriting to information architecture, mental models, system states, progressive disclosure, empty states, errors, warnings, onboarding, forms, search, tables, permissions, AI uncertainty, accessibility, localization, content systems, research, collaboration, and measurable comprehension.

The audit applied that lens to the full product surface rather than reviewing isolated strings. The source sections used as the audit contract are:

| Persona concern | Source lines | Audit question |
| --- | --- | --- |
| Core responsibility | `pasted-text.txt:1-45` | Does the product tell the user what matters at the point of action? |
| Information and hierarchy | `pasted-text.txt:49-170` | Is the most important information visible before technical detail? |
| Terminology and labels | `pasted-text.txt:216-312` | Are nouns stable, understandable, and consistent? |
| Workflow and sequencing | `pasted-text.txt:316-390` | Does each step make the next responsible action obvious? |
| Progressive disclosure and states | `pasted-text.txt:394-506` | Are complexity and detail revealed only when useful? |
| Warnings, destructive actions, onboarding | `pasted-text.txt:510-601` | Are risk, consequence, and recovery clear? |
| Help and decision support | `pasted-text.txt:605-677` | Can a user make a choice without knowing implementation details? |
| Forms, search, tables, settings, permissions | `pasted-text.txt:680-822` | Are inputs, filters, access decisions, and results self-explanatory? |
| AI confidence and trust | `pasted-text.txt:826-908` | Does the product distinguish suggestion, result, uncertainty, and human review? |
| Voice and content systems | `pasted-text.txt:1018-1134` | Is there a reusable voice and pattern system rather than one-off copy? |
| Research and comprehension | `pasted-text.txt:1138-1188` | Is content validated by understanding and recovery, not only presence? |
| Accessibility and localization | `pasted-text.txt:1433-1590` | Does content survive assistive technology, zoom, translation, and varied literacy? |
| Decision framework and all states | `pasted-text.txt:1593-1674` | Has the product been audited across the full state matrix? |
| Failure modes and evaluation | `pasted-text.txt:1786-1903` | Are we avoiding copy as a cosmetic patch and measuring the right outcomes? |

### Evidence notation

* Tier 0: assumption only.
* Tier 1: static inspection of current code or documentation.
* Tier 2: targeted test or contract check passed. The focused test result in this audit is S1 evidence. No content change was made, so it is not S2 or S3 evidence.
* Tier 3: integration or end-to-end flow verified.
* Tier 4: runtime or manual behavior observed.
* Tier 5: production-like or real-data verification.

This audit combines Tier 1 static inspection, Tier 2 S1 focused tests, Tier 4 offscreen Qt construction and local HTTP smoke evidence, and historical prior audit evidence. Current browser interaction and comprehension testing were not available in this session. Those limitations are recorded rather than hidden.

## 2. Product truth before content polish

The product truth that content must teach is already present in the project documentation and code, but it is distributed.

### Current product capability

The product contract describes SignKit as a local-first desktop application for extracting, cleaning, saving, and placing signature images on PDFs. The current desktop window initializes a local extractor and local vault in `desktop_app/views/main_window.py:89-109`. The visible tabs observed in the Qt construction check were:

1. Signature Extraction
2. PDF Signing
3. Workflow Dashboard (Premium)
4. Workflow Grants (Premium)
5. Recipe Builder (Premium)
6. Vault

The public page correctly describes the current product as local by default and identifies the working flow as extraction, cleanup, local reuse, PDF placement, and export in `index.html:1083-1200` and `index.html:1343-1387`.

The browser workspace has a different, narrower capability. Its own copy says it stores workflow metadata, supports a metadata-first register, and does not host document signing in `web/cloud_workspace/index.html:21-34`. The workspace does not itself establish a cloud document execution product.

### First-principles content model

The content system should teach one product with explicit operating boundaries:

| Operating model | What it means now | What it must not imply |
| --- | --- | --- |
| Local | The complete current workflow for preparing and exporting documents on the device. | No absolute claim that every future support, licensing, update, or optional service path is network-free. |
| Browser register | Metadata, workflow records, templates, receipts, and controlled proof. | Browser-native signing, cloud storage of document bytes, identity verification, or legal signing certification. |
| Cloud | A future product direction only until it owns execution, storage, recovery, audit, and support without desktop dependency. | A shipped capability. |
| Hybrid | A future direction for explicit local execution plus inspectable coordination. | Silent universal synchronization or an undefined data boundary. |

The underlying user job should be named plainly:

> Prepare a signature image and place it on a PDF, with the working files kept on the device by default.

The recurring workflow job should be named separately:

> Repeat a controlled document process, show which items need a person, and keep a record of what happened.

These two jobs are related, but they should not compete for attention during first-run onboarding. The first job is the default local path. The second job is an advanced operator path.

## 3. Current experience map

| Surface | Current role | Strong content already present | Content design risk |
| --- | --- | --- | --- |
| Public root `index.html` | Acquisition and purchase expectation | Local-first framing, qualified checkout boundary, current price, platform qualification, workflow enquiry boundary | Image placement versus legal signing is not plainly distinguished; provider details repeat; legal links are raw Markdown; launch and regular price hierarchy is easy to misread. |
| Onboarding dialog | First-run orientation and activation | “Welcome to SignKit”, local framing, manual flow steps, premium workflow steps, health check, license access | Too much product, pricing, plan, backend, and automation content before first success. Includes “Works 100% offline”. |
| Extraction tab | Primary local task | Source, crop preview, result, selection, process, export, save, library | Technical controls and compact labels make the task feel like an image-processing console. Quality, selection, and result states do not consistently explain what to do next. |
| PDF tab | Placement and export | Open PDF, placement, page navigation, appearance controls, save output | “Signing” and “signed PDF” imply more than image placement. Icon-only navigation and raw errors weaken comprehension and accessibility. |
| Vault | Reuse and history | Search, preview, metadata, copy, delete confirmation, decryption failure state | “Notary Vault” implies legal authority; “My Signatures” and “Signature Library” create competing names. Metadata is technical and object naming is weak. |
| Workflow dashboard | Advanced repeated work and operations | Filters, states, retry, quarantine, pause, scan, run, audit-oriented job table | Operator language is dense, internal IDs are prominent, and the next safe action is less visible than engine state. |
| Grants | Advanced authorization | Approver, runners, revoke, grant IDs, authorization decisions | “Subject”, “grant”, “runner roles”, and “approver” require an access model that is not taught before the user is asked to use it. |
| Recipe Builder | Advanced repeatable configuration | Template, folders, role mapping, dry run, draft and activation | “Recipe”, “template”, “role”, and ratio fields are not clearly separated in user language. |
| Browser workspace | Metadata-first workflow register | Explicit trust boundary, local versus planned topologies, record creation, review-oriented statuses | “Control plane”, “topology”, “passport”, and synthetic proof language lead the experience. Basic record creation and recovery should lead. |
| Help and user guide | Self-service support | Concrete controls, shortcuts, local paths, PDF setup, error categories | Stale names and claims conflict with current product state. Placeholder support details remain. |
| Legal and claim documents | Trust and contractual boundary | Qualified local-by-default boundary, provider disclosure, refund language, claim registry | Different terms and link destinations make the legal surface feel separate from the product. |
| Retained legacy pages | Historical assets and redirects | Public-surface audit recognizes retired routes and warnings | Legacy pages retain checkout links, unsupported social proof, placeholder IDs, and absolute local claims. |

## 4. Mental model and information hierarchy audit

### Finding CD-P0-02: The product model is distributed across internal modules

The desktop interface exposes six top-level tabs, but the user goal is not six separate products. The current tab names present implementation or feature groupings before the relationship between them is clear. “Signature Extraction” and “PDF Signing” are understandable enough in isolation, but “Vault”, “Workflow Dashboard”, “Workflow Grants”, and “Recipe Builder” need a model before they become navigable.

The public page gives a better task arc, but it does not fully carry that arc into the desktop app. The browser workspace then introduces a second architecture vocabulary with “execution register”, “control plane”, “topology”, and “execution passport”. These terms may be useful in an advanced operator or architecture view, but they should not be the primary explanation of the product.

#### Recommended information hierarchy

The first layer should answer four questions:

1. What am I trying to finish?
2. What file or asset am I working on?
3. What has the system done so far?
4. What is the safest next action?

The second layer may explain:

1. local versus connected boundary,
2. processing method,
3. confidence or quality signals,
4. audit details,
5. authorization and folder scope,
6. technical diagnostics.

The current product often reverses those layers. For example, a user sees “Standard (Threshold)” and “Forensic (Ink Separation)” before seeing a clear statement such as “Choose how SignKit separates the signature from its background. Start with Recommended.”

#### Proposed desktop navigation model

Keep the underlying modules, but expose a user model around the job:

* Prepare: import, select, clean, inspect.
* Saved signatures: reuse and manage local signature images.
* Place on PDF: open, place, review, export.
* Repeat work: advanced templates, runs, review, and permissions.
* Help and privacy: support, boundaries, diagnostics, licensing.

The existing internal modules can remain behind these labels. This is a content and information hierarchy refactor, not a recommendation to delete the existing workflow engine or vault code.

## 5. Terminology audit and proposed canonical glossary

### Current terminology collisions

| Current term | Where observed | Problem | Proposed user-facing term | Engineering or advanced alias |
| --- | --- | --- | --- | --- |
| Signature Extraction | Tab, help, public page | Correct domain term, but can describe both the task and the module. | Prepare a signature | Signature extraction module |
| Choose Image / Open & Upload Image / Open a signed document | Extraction and onboarding | Three entry labels for one action. “Signed document” can be mistaken for a PDF workflow. | Open source image | Upload/import compatibility alias |
| Source | Extraction panel | Accurate but abstract for a first-time user. | Source image | Source asset |
| Crop preview | Extraction panel | Technical but useful after selection. | Selected area | Crop preview |
| Result | Extraction panel | Too generic for a high-value artifact. | Cleaned signature | Extraction result |
| My Signatures | Extraction compact section | Personal and clear, but not aligned with Vault. | Saved signatures | Library collection |
| Signature Library | PDF tab | Clearer than Vault but a second name. | Saved signatures | Vault collection |
| Notary Vault | Vault header | “Notary” implies legal office, authority, or notarization. | Signature Vault or Saved signatures | NotaryVault class name may remain internal until migrated |
| PDF Signing | Tab and help | Current product places an image signature. The term can imply cryptographic or regulated signing. | Place on PDF | PDF signing implementation alias only if capability is legally reviewed |
| Save Signed PDF | PDF action | Implies a legally signed document. | Export PDF with placed signature | Save signed PDF compatibility label only after claim review |
| Standard (Threshold) | Extraction mode | Exposes algorithm instead of user outcome. | Recommended cleanup | Threshold mode |
| Forensic (Ink Separation) | Extraction mode and verification | “Forensic” raises an evidence and authenticity expectation. | Advanced ink separation | Forensic mode only in a documented, qualified expert workflow |
| Auto Clean | Extraction checkbox | Does not define what changes or how to review it. | Clean automatically | Adaptive cleanup |
| Quality: Unknown | Extraction result | A state without explanation or action. | Quality not measured yet | Quality score unavailable |
| Local service | Status | Better than cloud language, but still technical. | SignKit local processing: online/offline | Companion backend |
| Backend | Onboarding and diagnostics | Internal implementation term. | Local processing service | Backend |
| Workflow Dashboard | Desktop tab | Broad and technical. | Repeat work | Workflow console |
| Job | Workflow table | Useful to operators, but needs a user definition. | Document run | Workflow job |
| Recipe | Builder | Internal metaphor; not obvious for all users. | Processing plan | Recipe |
| Template | Builder and browser | Useful, but must mean reusable document structure, not an execution rule. | Document template | Template |
| Grant | Grants | Access-control term that needs explanation. | Permission to run | Execution grant |
| Subject | Authorization | Implementation noun; not a user-friendly identity label. | Authorized person or account | Principal subject |
| Runner roles | Grants | Ambiguous whether it means people, roles, or machines. | People allowed to run | Runner roles |
| Execution register | Browser | Advanced operational language. | Workflow records | Execution register |
| Execution Passport | Browser | Strong concept for evidence, but not a starting point. | Activity record | Execution Passport |
| Topology | Browser | Architecture term. | Where work runs | Topology |
| Metadata-only | Browser | Honest but abstract. | Record details only, no document file | Metadata-only |
| Proof packet | Browser fixture | “Proof” can sound like production evidence. | Sample workflow record | Proof fixture |
| Authenticated by SignKit | Verification dialog | Can be read as identity or legal authenticity. | SignKit watermark found | Watermark verification |

### Canonical language rules

1. Use “place a signature image on a PDF” when describing the current core PDF action.
2. Use “export” for the produced file. Say “signed PDF” only when the product capability and legal wording have been explicitly reviewed for that context.
3. Use “saved signatures” in primary UI. If “Vault” is retained, explain it as “Saved signatures” in the subtitle and help text.
4. Use “local processing” for the customer-facing boundary. Use “backend” only in diagnostics or developer documentation.
5. Use “document run” for one repeated-work execution in user-facing operator views. Keep “job” as an advanced detail or API term.
6. Use “permission to run” before “grant”. Explain the grant object only when the operator needs to inspect or revoke it.
7. Use “where work runs” before “topology”.
8. Reserve “forensic”, “authenticity”, and “authenticated” for a separately reviewed claim set with explicit evidence, limitation, and intended audience.
9. Never use “100% offline”, “zero data leaves your device”, or equivalent absolute language when the product has licensing, updates, support, checkout, optional connected workflows, or local companion services.
10. Do not use “cloud” to describe a local companion process.

## 6. Workflow sequencing and progressive disclosure

### Core local flow

The most important journey should have a visible sequence:

```text
Open source image
  -> Select the signature
  -> Clean the selection
  -> Review the cleaned result
  -> Save to Saved signatures or export
  -> Open a PDF
  -> Place the saved signature
  -> Review pages and appearance
  -> Export the PDF with the placed signature
```

The current extraction UI contains most of these actions, but the relationship is not consistently presented as a sequence. It shows panels, control groups, and action buttons. The onboarding quick start also calls the final step “Run”, which is ambiguous in a manual extraction workflow.

### Recommended step model

| Step | Primary question | Primary action | Secondary detail |
| --- | --- | --- | --- |
| 1. Open | What image contains the signature? | Open source image | Supported formats, sample, camera input |
| 2. Select | Which area should SignKit use? | Draw selection | Selection dimensions and reset |
| 3. Clean | How should the selected area be separated? | Use Recommended cleanup | Advanced mode, threshold, color controls |
| 4. Review | Is the result usable? | Compare source and cleaned result | Quality signal, transparency, zoom |
| 5. Save or export | Where should I use it next? | Save to Saved signatures or export image | Format, background, local vault details |
| 6. Place | Where should it appear in the PDF? | Click a saved signature, then place | Page, position, size, rotation |
| 7. Review and export | Is the PDF ready to leave the app? | Export PDF with placed signature | Page count, output path, verification limits |

Technical controls should remain available, but the primary path should default to a recommended choice. A user should be able to complete the task without learning thresholding, clustering, hex color values, or worker implementation.

### Advanced repeated workflow

The advanced flow should be introduced only after the local manual flow is understood:

```text
Choose a document template
  -> Define a processing plan
  -> Map signature roles to saved signatures
  -> Choose input and output folders
  -> Choose a review queue
  -> Set who may run it
  -> Dry run with a sample
  -> Activate the plan
  -> Monitor document runs
  -> Review exceptions
  -> Retry, quarantine, cancel, or export
```

The current recipe builder and workflow console contain this depth, but the user is exposed to “role-based signature space mapping”, ratio fields, grant subjects, and engine states before the product has defined the objects in user language.

## 7. State, empty, loading, error, warning, and recovery audit

The persona specifically requires content for all states. SignKit has many relevant states in code, but the copy is not yet governed as a state system.

### State model proposed for user-facing language

| Internal or current state | User-facing state | What the user needs to know | Next action |
| --- | --- | --- | --- |
| No image uploaded | No source image yet | SignKit needs an image that contains the signature. | Open source image |
| Invalid selection | Selection is too small or incomplete | The selected area cannot produce a useful result. | Draw a larger selection or reset |
| Loading | Preparing preview | The selected area is being processed locally. | Wait, cancel if supported |
| Quality unknown | Review needed | SignKit has not measured or cannot measure quality yet. | Inspect source and cleaned result |
| Vault not initialized | Saved signatures unavailable | The local saved-signature store is not ready. | Retry initialization, open support, do not imply data loss |
| No signatures saved | Nothing saved yet | Save a cleaned signature to reuse it on future PDFs. | Save a signature |
| No filter match | No saved signatures match this search | The saved collection is not empty, but this filter returned no result. | Clear search or change filters |
| PDF not loaded | No PDF open | Open a PDF to place a saved signature. | Open PDF |
| Page 0/0 | No page available | There is no loaded document to navigate. | Open PDF |
| Export blocked by license | Export is unavailable in this plan | Preview remains available if true, and the license requirement is specific. | Review license options or continue preview |
| Backend offline | Local processing service unavailable | Explain which action is affected and whether local manual work remains available. | Retry connection, continue local path, or open diagnostics |
| Job queued | Waiting to start | The run has been accepted but has not started. | Wait or cancel |
| Matching | Checking the document against the plan | Explain what is being checked, not only the internal state. | Wait |
| Needs review | A person must decide | State why, show the affected file or field, and provide decision actions. | Review, approve, correct, or quarantine |
| Retry | The previous attempt can be tried again | State whether retry is safe and what will be repeated. | Retry or inspect reason |
| Failed | The run did not finish | State whether output exists, whether input is unchanged, and what recovery is available. | Review reason, retry, or quarantine |
| Cancelled | The run was stopped | State whether any output was created and whether the input remains unchanged. | Reopen or run again if safe |
| Completed | The run finished | State output location, evidence record, and any remaining review. | Open output or record completion |

### Error pattern

Every user-facing error should use this order:

1. Plain-language result: what did not happen?
2. Impact: did the source remain unchanged, and was an output created?
3. Recovery: what can the user do now?
4. Detail: expandable technical detail for support or diagnostics.
5. Reference: a stable support identifier if the issue is logged.

Example:

> Could not export the PDF.
>
> No new PDF was created. Your source document remains unchanged.
>
> Check that the destination folder is writable, then try Export again. If it fails again, send the diagnostic reference `SK-...` to support.
>
> Technical detail: permission denied for destination folder.

The current code frequently passes raw exception text into `QMessageBox`, including `desktop_app/views/vault_tab.py:239`, `desktop_app/views/verify_dialog.py:135-139`, the workflow console run failure path, and PDF open/save paths. Raw detail is useful for support, but it should not be the primary content.

### Warning and destructive pattern

For delete, revoke, quarantine, cancel, and overwrite actions, the confirmation must name:

* the object,
* the exact consequence,
* whether the action can be undone,
* what is not affected,
* the explicit action button.

The vault delete confirmation is a good starting point because it says the signature will be permanently deleted. It should still name the selected object and use an explicit button such as “Delete saved signature” rather than generic “Yes”. The grant revoke flow should similarly explain which future runs are affected and whether existing outputs remain.

## 8. Onboarding and help audit

### Onboarding dialog

The dialog begins well with “Welcome to SignKit” and a local-sensitive-document promise in `desktop_app/views/onboarding_dialog.py:77-104`. It then introduces three feature cards, a quick-start sequence, backend health, license activation, strategic upgrade content, plan cards, personas, and help links.

The primary issue is sequencing. A first-run user needs to complete one small success before receiving a full product catalog. The current dialog asks the user to understand both manual signature preparation and recurring packet automation. It also says:

> Contracts, intake forms, HR packets, and signed PDFs stay on your device. Works 100% offline.

That statement is too absolute for the current product boundary and conflicts with the governed local-by-default language. Replace it with a qualified statement such as:

> Your working images and PDFs are processed on this device by default. SignKit may use the network for licensing, updates, support, or an explicitly enabled connected workflow.

The first-run content should be reduced to:

1. one sentence about the current local workflow,
2. a three-step first task,
3. one primary action, “Open a source image”,
4. a short “Learn about privacy and connected services” link,
5. a secondary “Skip guided start” action.

Backend health and license information should appear when it affects an action, not before the user has an opportunity to complete a local preparation task.

### Help and user guide

`docs/HELP.md` and `docs/USER_GUIDE.md` provide useful operational detail, but they are not current content authorities. Specific conflicts include:

* `docs/USER_GUIDE.md:1-105` uses old labels such as “Choose Image”, “Save”, and “Library” without matching the current module vocabulary everywhere.
* The guide says “No internet required, works completely offline”, “Nothing. Zero data leaves your Mac”, and “Files never uploaded to cloud”. These are stronger than the current product contract.
* The guide says macOS only and Windows/Linux later, while the current public root describes macOS, Windows, and Linux release availability.
* It includes a stale “Production License $29” statement, a test email, a placeholder support email, a placeholder repository link, and an outdated version/date.
* It says “Any standard image format” after separately naming PNG/JPEG, which creates a support ambiguity.
* `docs/HELP.md` describes “Source rotation will re-upload corrected image”, while the current local-first boundary needs a clear explanation of whether that action is local state or a network operation.
* The help dialog fallback points to `docs.signature-extractor.com`, while the product and public surfaces are SignKit surfaces. The link authority must be checked before exposing it as support.

Recommended documentation hierarchy:

1. In-product contextual help for the current control and next action.
2. A current task guide for prepare, save, place, export.
3. An advanced operator guide for repeated workflows.
4. A privacy and boundary guide that is generated or checked against the claim registry.
5. Technical diagnostics and API documentation separately.

Do not make the user guide a second product contract. It should derive labels, capabilities, and claims from canonical sources.

## 9. Forms, search, tables, permissions, and settings

### Forms

The browser workspace has explicit labels for email, password, participant, reviewer, effective date, and operator note. This is a strong structural base. It still uses “Execution topology” and options such as “Local companion” and “Cloud metadata-only” before explaining the user outcome. The form should ask “Where should this record be handled?” and explain the options in plain language.

The recipe builder labels are structurally present, but “Unsigned docs folder”, “Signed output folder”, “review queue folder”, and “Matcher mode” need sentence-level guidance. A form field should tell the operator what belongs there, what the system will do with it, and what happens if the folder is unavailable.

The grants form uses “Approver subject”, “Runner Roles”, and a `Create Grant` action. The user-facing first layer should be:

* Who approves this workflow?
* Which people may run it?
* Which folders may it read and write?
* How long is this permission valid?

“Grant ID” and subject strings can remain in an advanced details view.

### Search and filters

The Vault placeholder “Search source, tags, or mode” is concise but assumes the user knows the metadata model. Use “Search saved signatures by name or tag” as the primary placeholder, with advanced filters exposed separately.

The workflow filter list has “Queued”, “Needs Review”, “Retry”, “Failed”, and “Completed”. Add one-line explanations or tooltips and ensure filters are mutually understandable. “Retry” is an action-capable state, while the others are outcome states. Consider a two-part model: status filters and recovery filters.

### Tables

The workflow table columns `Job ID`, `Recipe`, `Input`, `Output`, `State`, `Match`, `Attempts`, and `Last reason` are useful for operators but over-weight internal identifiers. The default table should lead with:

* Document or packet name,
* Current state,
* What needs attention,
* Last updated,
* Safe next action.

Advanced identifiers, attempts, matching class, and paths should remain available in row details or an evidence panel.

### Settings and preferences

The current Preferences dialog is very small and mostly supports onboarding visibility. That is acceptable for current scope, but future settings must be grouped by user concern:

* Local processing and storage,
* Saved signatures and vault,
* PDF export,
* Workflow permissions,
* Licensing and updates,
* Privacy, diagnostics, and support.

Do not expose raw configuration keys or environment terminology in the user settings surface.

## 10. AI, quality, verification, and trust language

The persona requires a clear distinction between machine output, confidence, and human judgment. SignKit uses mode and quality language that needs qualification.

### Extraction quality

“Quality: Unknown” is not enough. The user needs to know whether quality is unavailable because processing has not run, because the image is unsuitable, or because the metric does not apply. A quality signal should include:

* what was evaluated,
* whether the signal is a recommendation or a guarantee,
* what uncertainty remains,
* what the user should inspect,
* whether the original source is preserved.

Suggested content:

> Review the cleaned signature against the source. This quality signal is a processing aid, not proof that the signature is authentic or legally valid.

### Mode choice

“Forensic (Ink Separation)” is high-risk language. The existing verifier uses “Verify Signature Authenticity”, “Forensic Verification”, “origin and integrity”, “Authenticated by SignKit”, and “No Watermark Found” in `desktop_app/views/verify_dialog.py:16-139`. Even if the watermark is verified correctly, “authenticated” and “authenticity” can be interpreted as identity, provenance, or legal validity. The content should state exactly what was detected:

> SignKit watermark found. This confirms that the file contains a SignKit watermark. It does not confirm the identity of the signer, the legal validity of the document, or that the image was not otherwise altered.

If this verification capability is intended only for internal watermark integrity, rename the dialog to “Check SignKit watermark” and move forensic language to technical documentation until a reviewed claim contract exists.

### Human review

The workflow state `Needs Review` is a strong product concept. It should become the common content pattern across extraction, PDF placement, local runs, and browser records. Every machine-assisted result should answer:

1. What did SignKit detect or prepare?
2. What is uncertain?
3. What should the person inspect?
4. What action closes the review?

This is more trustworthy than a single green check or a numeric quality score without context.

## 11. Accessibility and inclusive content audit

The current runtime construction check found 76 buttons and nine textless buttons without accessible names. Some are color swatches with tooltips and some are Qt internal extension buttons, so not every item is a product defect. The result still identifies a meaningful accessibility review area.

Specific observations include:

* The main tab widget has an accessible name and description in `desktop_app/views/main_window.py:104-110`, which is a good pattern.
* The PDF previous and next controls are icon-only `◀` and `▶` buttons in `desktop_app/views/pdf_tab.py:123-125` without a visible or programmatic name in the inspected code.
* The extraction threshold slider has an object name and value label, but the runtime inspection found no accessible name and no tooltip for the slider itself.
* Several line edits and combo boxes had empty accessible names in the runtime construction check.
* Compact mode shortens buttons to “Open”, “Mode”, “Clear”, “Clean”, “Export”, “Save”, “JSON”, and “Delete” in `desktop_app/views/main_window_parts/extraction.py:3822-3855`. This saves space but removes object context and can create ambiguity for screen readers and sighted users.
* Status labels such as “Checking backend...”, “Backend offline”, “Loading...”, and “Quality: Unknown” need live-region or focus-management behavior where appropriate, not only text updates.
* The browser workspace uses `role="status"`, `aria-live`, labels, and a main landmark in several places. This is a useful pattern to carry into desktop equivalents.
* The public page has meaningful image alt text in the current root, but historical surfaces still contain weaker or marketing-oriented labels. The canonical public surface must remain the only route for current content.

### Accessibility content requirements

For every control, verify:

1. Name: what is this control?
2. Role: what kind of interaction is it?
3. State: what is selected, disabled, loading, or unavailable?
4. Value: what is the current threshold, page, zoom, or filter?
5. Outcome: what changed after activation?
6. Recovery: what should happen if it fails?

Content should not rely on color, emoji, position, or icon shape alone. The current interface uses emoji in tab labels and status icons. Keep visual personality if desired, but provide text equivalents and do not make the emoji part of the only meaning.

### Localization and plain language

No full localization implementation was found or verified in this audit. The content system should nevertheless avoid hard-coded sentence fragments that make translation and pluralization brittle. Store user-facing status messages and action labels as structured content, use explicit plural rules, avoid idioms such as “one file is a tool problem”, and do not concatenate raw paths into primary messages.

## 12. Voice, tone, and brand alignment

The brand narrative contract provides a strong baseline: controlled, local by default, and finished in one calm workflow. It recommends concrete verbs such as extract, clean, save, place, and export. Those verbs should become the foundation of the product UI.

### Voice characteristics to keep

* Calm: state the outcome and next action without drama.
* Precise: qualify privacy, licensing, connectivity, and document validity claims.
* Practical: use verbs users can act on.
* Respectful: avoid making a user feel responsible for understanding internal architecture.
* Operationally honest: distinguish current capability, planned direction, sample proof, and unsupported outcome.

### Voice failures to correct

* “cloud features enabled” in a local backend startup message.
* “100% offline” in onboarding.
* “Forensic Verification” and “Authenticated by SignKit” without a narrow explanation.
* “Execution topology”, “control plane”, and “metadata-first” as primary user language.
* Generic “Error” titles with raw exception text.
* “Save Signed PDF” where the current action is image placement and export.
* “Notary Vault” where the product does not establish notarization.

### Content density rule

The product should prefer one useful sentence and one next action over a paragraph of implementation detail. Detailed explanation belongs behind an “About this result”, “Technical details”, “Why this is unavailable”, or support link. Progressive disclosure must preserve access to detail without making the default path depend on it.

## 13. Public, legal, claims, and commercial content

### Current root page

The current root page is the strongest public content surface found. It qualifies local-by-default language, describes the personal workflow, names the checkout boundary, identifies current platform support, and keeps recurring operations in an enquiry and pilot path.

The remaining issues are content hierarchy and precision:

1. The price presentation combines launch and regular price references in several compact locations. The user should see one current purchase price, one clearly subordinate explanation of the offer period, and one plain statement of what happens after checkout.
2. The page uses “signed documents” and “PDF signing” in headings and image alt text without a nearby plain distinction between image placement and identity-backed signing.
3. The provider note explains Dodo and Gumroad implementation state more than it explains the user outcome. The primary question is where receipt, download, and license delivery details appear.
4. Legal links point to Markdown documents. A production-facing page should provide a readable rendered legal route or a deliberate download experience.
5. The current root copy and the legal documents need one synchronized definition of local processing, optional connected services, support, updates, and refunds.

### Claim registry

`docs/launch_claims/registry.md:1-70` is a useful authority for public claims. It currently still mentions evidence tiers following `motto_v4.md`, which is governance drift after the project moved to v5. That line should be corrected as part of the content system repair.

The registry must own or reference:

* canonical public wording,
* current capability status,
* evidence tier,
* product and legal dependency,
* owner,
* review date,
* permitted surfaces,
* prohibited stronger variants.

The claim registry should not be copied into onboarding, help, legal, and legacy pages by hand. Those surfaces should be checked against it or generated from a shared content contract.

### Legal and support content

The privacy policy is more qualified than the stale user guide, but it still uses the older “Signature Extractor” title and includes an older link destination. Legal content should use the current product name and the same user-facing boundary vocabulary as the app. This is a content consistency and user trust requirement, not merely a legal editing task.

No legal approval is inferred by this audit. The recommendation is to send the narrowed wording and current capability map for the appropriate business or legal review before changing customer-facing legal claims.

### Retained legacy surfaces

The public-surface auditor returned status `pass`, with 13 claims, 27 legacy redirect paths, 27 server legacy paths, no blocking errors, and warnings for retained pages containing direct checkout references, unsupported high-risk claims, placeholder product IDs, placeholder or inflated social proof, and historical route references. This is evidence that routing is governed, not evidence that retained content is safe to leave unreviewed.

Historical content should be explicitly marked as historical or removed from public reach after preservation review. It should not remain a second source of product truth.

## 14. Advanced workflow and operator content

The advanced workflow UI demonstrates important product depth: queued, matching, signing, verifying, completed, needs review, failed, retry, and cancelled states; grants; folder scope; pause; quarantine; dry run; and audit-oriented results. The content problem is that the UI speaks to the engine before it speaks to the operator.

### Operator dashboard

The workflow console describes itself as a “Minimal operator dashboard for workflow jobs and grants” and exposes actions such as “Run selected”, “Retry selected”, “Open input”, “Open output”, “Quarantine selected”, “Cancel selected”, “Scan folders”, “Run queued”, “Auto-run queued after scan”, and “Pause”. This is operationally meaningful, but the first-order content should be:

* what is waiting,
* what needs a human,
* what is safe to retry,
* what output exists,
* what will happen if the user acts.

Recommended table and action labels:

| Current | Preferred first-layer label | Explanation |
| --- | --- | --- |
| Run selected | Start selected runs | Starts only the selected records. |
| Retry selected | Try selected runs again | Repeats the failed step if the input and output conditions are safe. |
| Quarantine selected | Move selected items to review | Stops automatic handling and preserves the item for investigation. |
| Open input | Open source file | Shows the source that was read. |
| Open output | Open produced file | Shows the output if one exists. |
| Last reason | Why this needs attention | Plain-language cause, with technical detail expandable. |
| Engine paused | Processing is paused | Explain what will resume when the operator starts it. |
| Active Grants | People allowed to run | Advanced permissions view can retain grant terminology. |

### Recipe builder

The recipe builder is a legitimate advanced tool, but it should first teach its object model:

* Template: the reusable document structure.
* Processing plan: the rules for matching and placing signatures.
* Saved signature: the local asset assigned to a role.
* Input folder: where new source files are read.
* Output folder: where produced files are written.
* Review folder: where uncertain or failed items are placed.
* Permission: who may run the plan.

The existing labels “Save Draft Recipe” and “Save & Activate Recipe” are reasonable after this model is taught. The field-level errors “Template required”, “Folder required”, and “Invalid folder” need a named field and recovery explanation.

### Grants and permissions

The grant manager contains important authorization concepts, but `Approver subject`, `Runner Roles`, `Grant ID`, and raw authorization codes are not suitable as the only content. The permissions surface should show a short summary first:

> Alex can run “New hire packet” using files from `/Input/New hires` and save results to `/Output/New hires` until 2026-09-01.

Then provide advanced details, revoke, history, and reason. This makes authorization inspectable without requiring the user to understand internal principal terminology.

## 15. Content system and governance recommendation

The long-term solution is a small content system with one source of truth for each class of language. Do not create another parallel page or duplicate claim registry.

### Proposed canonical artifacts

| Artifact | Canonical responsibility | Suggested location | Required consumers |
| --- | --- | --- | --- |
| Product vocabulary | User-facing nouns, definitions, banned aliases, migration notes | `docs/content/PRODUCT_GLOSSARY.md` | Desktop, browser, public, help, legal review |
| State matrix | State, meaning, user impact, action, output guarantee, recovery | `docs/content/STATE_CONTENT_MATRIX.md` | Desktop, browser, workflow engine, tests |
| Error catalog | Stable error IDs, plain message, recovery, technical detail, support reference | `docs/content/ERROR_CATALOG.md` or structured source | UI, logs, diagnostics, support |
| Content pattern library | Empty, loading, success, warning, destructive, license, offline, review patterns | `docs/content/PATTERN_LIBRARY.md` | All UI surfaces |
| Claim registry | Public and customer-facing claims, evidence, legal dependency | Existing `docs/launch_claims/registry.md` | Public, onboarding, pricing, help, legal review |
| Surface map | Canonical route, owner, status, allowed claims, retirement state | Existing `docs/launch_claims/public_surface_map.md` plus review addenda | Deployment and content review |
| Comprehension test plan | Tasks, success criteria, misunderstandings, recovery scenarios | `docs/research/content_comprehension_plan.md` | Product, design, engineering, research |

The content artifacts should be versioned and tested like code. The data/configuration rule applies because terminology, state labels, claims, prompts, and templates change product behavior and customer expectations.

### Review gates

Every meaningful user-facing content change should answer:

1. Which user goal or state changed?
2. Which canonical term is used?
3. Which other surface uses the same term?
4. Does the change imply a stronger privacy, legal, authenticity, or availability claim?
5. What does the user see on success, failure, retry, and cancellation?
6. What does an operator see?
7. What accessibility name and state are exposed?
8. What test or comprehension task proves the wording works?

## 16. Research and comprehension validation plan

Static checks cannot prove comprehension. The next evidence unit should test the content model with representative users or internal proxies who have not seen the implementation.

### Test group A: first local task

Task: “Open a source image, prepare the signature, save it, place it on a PDF, and export the result.”

Observe:

* whether the participant chooses the intended first action,
* whether they understand selection versus cleanup,
* whether they can tell source and result apart,
* whether they can find saved signatures,
* whether they distinguish placement from legal signing,
* whether they can identify the exported file,
* whether they can explain where working files were processed.

### Test group B: failure recovery

Tasks:

* export to a non-writable folder,
* open a malformed image,
* retry a failed workflow run,
* review a needs-review item,
* revoke a permission,
* delete a saved signature.

Success means the participant can state what happened, whether the source changed, whether an output exists, and what next action is safe.

### Test group C: trust boundaries

Ask participants to explain, in their own words:

* what stays on the device,
* when the network may be used,
* what the browser workspace stores,
* whether the product creates a legal signing certificate,
* what a watermark result proves,
* what a quality score proves.

Any answer that overstates the product is a content defect even if the string passed a snapshot test.

### Metrics

Track:

* first-attempt task completion,
* time to first useful result,
* wrong-action rate,
* terminology recall,
* recovery success,
* confidence calibration,
* support questions caused by vocabulary,
* accessibility task completion,
* localization review defects,
* misleading-claim incidents.

Do not optimize only for shorter text, click-through, or visual neatness. Content is successful when the user understands the system and can act safely.

## 17. Prioritized implementation roadmap

### Phase 0: establish content truth before surface polish

Owner group: product, content, engineering, legal or business reviewer where claims are affected.

1. Approve the current product boundary: local preparation and PDF image placement, not a regulated signing claim.
2. Decide the approved terms for saved signatures, PDF placement, local processing, document run, processing plan, permission, and workflow record.
3. Correct the claim registry v4 reference and reconcile `PRODUCT.md`, brand narrative, privacy policy, EULA, terms, user guide, and help guide.
4. Mark or retire retained legacy pages that contain direct checkout paths, placeholder values, unsupported claims, or social proof.
5. Remove placeholders and test identities from user documentation.

Closure evidence: one approved glossary, one claim registry review, no contradictory absolute offline or authenticity language on reachable current surfaces, and a documented disposition for every retained legacy warning.

### Phase 1: fix the primary local workflow

Owner group: desktop product and content.

1. Reduce first-run onboarding to the first local success path.
2. Rename or qualify PDF placement language.
3. Replace extraction algorithm-first labels with outcome-first labels and advanced disclosure.
4. Add a visible sequence from open through export.
5. Normalize empty, loading, success, error, and recovery messages.
6. Add accessible names, values, and state announcements for all primary controls.
7. Replace raw exception text in primary user messages with safe summaries and expandable detail.

Closure evidence: a complete local task can be followed by a new user, a failure can be recovered without support intervention, and accessibility inspection identifies every primary control and state.

### Phase 2: make advanced operations explainable

Owner group: workflow product, content, engineering, operations.

1. Introduce the object model before recipe, grant, job, and topology details.
2. Create one shared user-facing state map for desktop and browser records.
3. Make “needs review” the common human-decision pattern.
4. Lead operator tables with document, state, reason, last updated, and safe action.
5. Move IDs, paths, engine terms, and authorization codes into details views.
6. Define dry run, activation, retry, quarantine, cancellation, and output guarantees.

Closure evidence: an operator can create a processing plan, understand a failed run, safely retry or quarantine it, and explain what the audit record contains.

### Phase 3: content system and research loop

Owner group: content design, product, research, engineering.

1. Add the glossary, state matrix, error catalog, and pattern library.
2. Add content contract tests for canonical labels, prohibited claims, accessible names, and state mappings.
3. Run comprehension studies for first task, failure recovery, trust boundaries, and accessibility.
4. Add localization readiness checks before expanding locales.
5. Review content as part of feature acceptance, not after visual QA.

Closure evidence: content artifacts are versioned, tested, used by all current surfaces, and updated with the corresponding product decisions.

## 18. Findings register with exact closure paths

### P0 findings

#### CD-P0-01: boundary and capability language conflict

Evidence:

* `desktop_app/views/onboarding_dialog.py:117-120` says “Works 100% offline”.
* `desktop_app/app_bootstrap.py:94-103` prints “cloud features enabled” for a local companion backend and “running in offline mode” on startup failure.
* `docs/BRAND_NARRATIVE_CONTRACT.md:1-120`, `PRODUCT.md`, and the current root page use more qualified local-by-default language.
* The browser workspace explicitly distinguishes local, cloud, and hybrid directions in `web/cloud_workspace/index.html:21-34` and `93-102`.

Impact: privacy, availability, and product topology are not explained consistently.

Closure: approve one boundary vocabulary, replace absolute and implementation language, then add contract checks across onboarding, bootstrap-visible status, public root, help, legal, and browser surfaces.

#### CD-P0-02: no single canonical product vocabulary

Evidence:

* Desktop uses `Signature Extraction`, `PDF Signing`, `Notary Vault`, `Workflow Dashboard`, `Workflow Grants`, and `Recipe Builder`.
* Extraction uses `My Signatures`, `Source`, `Result`, `Standard (Threshold)`, and `Forensic (Ink Separation)`.
* Browser uses `Execution register`, `Control plane`, `Topology`, `Execution Passport`, `Metadata-only`, and `Proof packet`.
* Help and user-guide content use older names and product identity.

Impact: users must translate between surface vocabularies.

Closure: create the glossary and state matrix first, then migrate the primary UI and documentation. Keep internal aliases only where migration or API compatibility requires them.

#### CD-P0-03: high-consequence recovery and trust states are not governed

Evidence:

* Raw exception text is used in vault, PDF, workflow, and verification dialogs.
* Verification uses authenticity and authentication language in `desktop_app/views/verify_dialog.py:16-139`.
* License restrictions use “PDF signing” and “signed documents” in `desktop_app/views/license_restriction_dialog.py:20-35`.
* Workflow has meaningful failure and review states, but primary content is engine-oriented.

Impact: users can leave an action without knowing whether the source changed, output exists, or the result is trustworthy.

Closure: implement a state matrix and error catalog, then map every destructive, export, verification, license, authorization, retry, and cancellation path to plain outcome, impact, recovery, and technical detail.

### P1 findings

#### CD-P1-01: onboarding overload

Evidence: `desktop_app/views/onboarding_dialog.py:112-260` and the extended plan/persona sections later in the file.

Closure: split first-run guidance from plan discovery, health, licensing, and advanced workflow education.

#### CD-P1-02: extraction exposes technical choices before user intent

Evidence: `desktop_app/views/main_window_parts/extraction.py:793-843`.

Closure: default to recommended cleanup; put threshold, clustering, ink separation, and color controls under advanced details with explanations and review guidance.

#### CD-P1-03: PDF wording overstates the current action

Evidence: `desktop_app/views/pdf_tab.py:85-125`, `docs/HELP.md`, public root headings and alt text, and restriction copy in `desktop_app/views/license_restriction_dialog.py:27-31`.

Closure: use “Place on PDF” and “Export PDF with placed signature” in primary user language; have business or legal review any retained “signing” claim.

#### CD-P1-04: state vocabulary differs across local and browser workflows

Evidence: local workflow states in `desktop_app/workflows/models.py` include queued, matching, signing, verifying, completed, needs review, failed, retry, and cancelled. Browser state actions in `web/cloud_workspace/app.js` include pending review, awaiting participant, received, ready for review, needs correction, approved, signed, exported, and exception.

Closure: define a shared semantic state layer with surface-specific presentation only where the underlying meaning genuinely differs.

#### CD-P1-05: support documentation is stale and contradictory

Evidence: `docs/USER_GUIDE.md:1-105`, `docs/HELP.md:1-126`, help fallback code, and current root claims.

Closure: rewrite current task guidance from the approved glossary and claim registry, remove placeholders, and record version/date ownership.

#### CD-P1-06: accessible names and compact labels are incomplete

Evidence: offscreen Qt construction found 76 buttons and nine textless buttons without accessible names, plus empty accessible names on inspected line edits and combos. Icon-only PDF navigation appears in `desktop_app/views/pdf_tab.py:123-125`. Compact labels appear in `desktop_app/views/main_window_parts/extraction.py:3822-3855`.

Closure: complete a control inventory, add accessible names and value/state descriptions, test keyboard and assistive technology paths, and avoid context-free compact labels.

#### CD-P1-07: browser workspace leads with architecture terms

Evidence: `web/cloud_workspace/index.html:15-34`, `38-40`, `68-71`, `79-101`, and `123-128`.

Closure: lead with create, review, record, and recover. Keep topology and passport details as an explicit trust and evidence layer.

#### CD-P1-08: legacy surfaces remain a claim risk

Evidence: `tools/audit_public_surface.py --json` reported no blocking errors but warnings for direct checkout references, “100% offline”, “your data never touches our servers”, inflated social proof, placeholder product IDs, and 30 historical documents referencing retired routes.

Closure: preserve historical documentation, but mark it historical, prevent public reachability, and remove or disposition all high-risk legacy claims.

### P2 findings

#### CD-P2-01: no shared state-content pattern library

Evidence: similar state concepts use different messages and dialog patterns across extraction, vault, PDF, workflow, license, and browser surfaces.

Closure: create the state matrix, error catalog, and pattern library before adding more feature copy.

#### CD-P2-02: raw implementation detail leaks into primary content

Evidence: backend URLs, raw exceptions, job IDs, grant IDs, paths, engine state, and provider names appear in user-facing contexts.

Closure: separate plain summary from expandable technical detail and diagnostics.

#### CD-P2-03: no current comprehension evidence

Evidence: focused tests verify contracts, but no current session browser interaction or user comprehension study was available. Prior browser QA is historical evidence and was not treated as current proof.

Closure: run first-task, recovery, trust-boundary, and accessibility comprehension studies.

#### CD-P2-04: generic action labels weaken object context

Evidence: `Open`, `Save`, `Delete`, `Run`, `Retry`, `Cancel`, and `Close` appear across compact or advanced contexts.

Closure: use object-aware labels when consequence or ambiguity is material, such as “Delete saved signature” and “Export PDF”.

#### CD-P2-05: search and table labels prioritize implementation metadata

Evidence: Vault search and workflow table labels in `desktop_app/views/vault_tab.py` and `desktop_app/views/main_window_parts/workflow_console.py`.

Closure: lead with user-recognizable names, state, reason, and action; move IDs and paths into detail views.

#### CD-P2-06: legal and support surfaces do not share one visible content identity

Evidence: older “Signature Extractor” titles, raw Markdown links, help fallback domains, and current SignKit public naming.

Closure: align product name, route, boundary vocabulary, support destination, and version ownership.

#### CD-P2-07: localization readiness is unverified

Evidence: no full localization catalog or localization test was verified during this audit; hard-coded sentence construction and technical fragments are present.

Closure: inventory strings, establish plural and date rules, remove concatenated user messages, and test translated layouts before locale expansion.

## 19. Verification record

### Checks run in this audit

| Check | Command or method | Result | Evidence tier |
| --- | --- | --- | --- |
| Instruction and project context | Read shared agent rules, project motto, context pack, and ran `/Users/pranay/Projects/agent-start --project ...` | Context loaded. The agent-start indexing step warned that the workspace-memory virtual environment was missing, so indexing was skipped and shared-only context continued. | Tier 1 |
| Focused contract and desktop checks | `venv/bin/python -m pytest -q tests/test_launch_claim_registry.py tests/test_public_surface_audit.py tests/test_landing_surface_contract.py tests/test_new_landing_page_contract.py tests/test_execution_passport_contract.py tests/test_execution_passport_browser_contract.py tests/test_topology_experience_contract.py tests/test_main_window_contract.py tests/test_app_bootstrap_profile_access.py desktop_app/tests/test_main_window_logic.py desktop_app/tests/test_pdf_features.py desktop_app/tests/test_pdf_improvements.py` | `103 passed, 3 skipped in 4.81s`. Skips require a Qt event loop for timer-driven behavior. | Tier 2, S1 only |
| Qt construction and accessibility inventory | Offscreen `QApplication` and `MainWindow` construction | Window title `SignKit`, six tabs, 76 buttons, nine textless buttons without accessible names, inspected controls and labels inventoried. | Tier 4 |
| JavaScript syntax | `node --check web/cloud_workspace/app.js` and `node --check web/live/js/checkout.js` | Passed. | Tier 1 |
| Public-surface contract auditor | `venv/bin/python tools/audit_public_surface.py --json` | `status: pass`, 13 claims, 27 redirect legacy paths, 27 server legacy paths, no errors, warnings for retained high-risk legacy content. | Tier 2, S1 |
| Local HTTP smoke | Started `venv/bin/python serve.py`, checked root, redirect paths, and assets with `curl` | Root returned 200, legacy paths returned 301, inspected assets returned 200, current root markers were present. | Tier 4 |
| Browser interaction | Playwright CLI attempt through the installed wrapper | Not available in this session because `playwright-cli` could not be resolved. No current browser interaction or accessibility claim is made. | Not available |
| Comprehension research | User study or assistive technology session | Not run in this audit. | Not available |

### What is verified versus inferred

Verified directly:

* The current source contains the named strings, states, surfaces, and contradictions listed in this document.
* The current desktop window can be constructed offscreen with six visible tabs.
* The focused contract suite passes at S1.
* Current JavaScript files checked for syntax pass.
* The local server exposes the canonical root and redirects inspected.
* The public-surface auditor identifies retained legacy warnings without blocking errors.

Inferred from the content and interface evidence:

* New users will need to reconstruct the relationship between tabs and the core job.
* Users may interpret “signed PDF”, “authenticated”, “forensic”, or “100% offline” more strongly than the current implementation contract supports.
* Operators may struggle to recover from advanced workflow failures because current content emphasizes engine state and identifiers.
* Accessibility comprehension is incomplete where accessible names and compact labels were not present in static construction.

These inferences require user comprehension or assisted technology testing for Tier 3 or Tier 4 confirmation.

## 20. Three review passes required by the project doctrine

### Pass 1: immediate correctness and completeness

Checked the full persona scope against public, onboarding, extraction, PDF, Vault, workflow, browser, help, legal, claims, accessibility, and legacy surfaces. Confirmed that the audit includes user information, hierarchy, terminology, sequencing, states, errors, onboarding, forms, permissions, AI trust, accessibility, localization, research, voice, and content governance.

Outcome: the primary gap is systemic content architecture and not isolated wording. High-risk claims and recovery states are recorded as P0 or P1.

### Pass 2: architecture and long-term viability

Checked for duplicate content authorities and parallel product models. Preserved the existing claim registry as the claim authority, the public-surface map as the route authority, and the existing local and browser implementations as distinct capability surfaces. The recommendation is to add a vocabulary and state layer, not a second product route or a second workflow engine.

Outcome: the proposed glossary, state matrix, error catalog, and pattern library are the smallest durable content architecture that can unify current surfaces without deleting useful advanced capabilities.

### Pass 3: rule compliance and supervision readiness

Checked evidence tiers, uncertainty, current dirty work, user-facing claims, accessibility, operator workflow, documentation continuity, and explicit closure paths. No commit, stage, reset, cleanup, branch, deployment, or external communication was performed. The working tree was already heavily modified and contains parallel work; it was preserved untouched.

Outcome: this artifact is complete as an audit handoff, not a claim that the content issues are implemented. Each remaining gap has an owner group, a closure condition, and a validation path.

## 21. Acceptance contract

### Exact user-facing behavior assessed

This audit assessed how SignKit tells a person to prepare a signature, place it on a PDF, save and export the result, use saved signatures, run repeated workflows, recover from failures, understand the local and browser boundaries, and interpret quality or verification outcomes.

### Business and team value delivered

The document identifies the content decisions that protect trust, reduce support burden, clarify the current paid product, prevent overclaiming, and make the advanced workflow legible to operators. It also provides a sequence for turning existing product depth into a coherent customer experience.

### Internal and operational value delivered

The document provides a canonical vocabulary proposal, shared state model, severity register, content governance artifacts, accessibility inventory, research plan, exact code and documentation locations, verification record, and staged closure criteria. It gives engineering, product, design, research, support, and legal reviewers a common handoff surface.

### Artifact changed

* Added `docs/review/content_designer_audit_2026-08-13.md`.
* No product source, tests, routes, configs, claims, legal files, or generated artifacts were modified by this audit.

### Files and work preserved

The repository was already dirty across desktop, backend, web, docs, tests, build files, generated context, and untracked work. That work was not reset, overwritten, staged, committed, cleaned, or deleted. The deleted tracked sample image and all pre-existing modified or untracked files remain as found.

### Remaining gaps and hardening path

* Current browser interaction and assistive technology behavior remain unverified because the Playwright CLI was unavailable. Run the browser and accessibility matrix after the content implementation phase.
* User comprehension remains unverified. Run the first-task, recovery, trust-boundary, and accessibility studies before claiming content readiness.
* P0 and P1 terminology, boundary, and verification language remain in the app. Implement the Phase 0 and Phase 1 roadmap before treating this audit as a release-readiness approval.
* Business or legal review is needed for any change involving PDF signing terminology, authenticity, watermark verification, refund, licensing, privacy, or connected-service claims.
* The agent-start indexing warning should be resolved separately if full workspace-memory indexing is required for future audits.

### Final disposition

The content design audit is documented and evidence-backed within the available runtime limits. The app is not yet content-system complete. The correct next decision is approval of the canonical vocabulary and product boundary, followed by the first local workflow content pass.

