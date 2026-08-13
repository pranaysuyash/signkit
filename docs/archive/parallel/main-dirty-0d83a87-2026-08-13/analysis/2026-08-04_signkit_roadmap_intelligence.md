# SignKit Roadmap Intelligence and Open Exploration

**Date:** 2026-08-04  
**Status:** Exploration complete, roadmap decisions open  
**Scope:** Code, tests, configuration, product docs, research docs, concepts, historical plans, current architecture, use cases, and new product exploration.  
**Authority:** This document is an inventory and exploration map. It is not permission to build every item listed here.

## 1. Purpose

This document records the full feature and roadmap surface discovered in the
SignKit checkout. It separates:

- behavior that exists in code;
- behavior covered by tests;
- behavior observed during runtime work;
- behavior described as in development;
- explicit historical roadmap proposals;
- architecture-derived implications;
- new ideas discovered during exploration;
- ideas that should remain research-only or be rejected.

The goal is to prevent old plans, marketing copy, concepts, and unfinished code
from being mistaken for one current product commitment.

## 2. Evidence vocabulary

| Label | Meaning |
| --- | --- |
| Implemented | Code path exists and is intended to be usable. |
| Test-covered | A targeted test exercises the behavior. |
| Runtime-observed | A manual or integration run observed the behavior. |
| In development | Current code or current docs show an active but incomplete path. |
| Explicit proposal | A document directly proposes the capability. |
| Inferred | The architecture implies the capability even if no roadmap sentence names it. |
| Research horizon | Feasibility, market, legal, or architecture exploration only. |
| Historical | Older plan or marketing material that may no longer match the current product. |
| Rejected/deferred | A boundary or decision says not to treat it as current product behavior. |

Static inspection is Tier 1. Targeted tests are Tier 2. Integration flows are
Tier 3. Manual runtime observations are Tier 4. Production-like or real-data
proof is Tier 5. No document in this file upgrades evidence by wording alone.

## 3. Current product thesis

SignKit is a local-first document-completion system for sensitive signed
documents. Its product arc is:

```
capture -> extract -> clean -> store -> place -> review -> export -> repeat
                                      |
                                      +-> template / recipe / workflow / evidence
```

The immediate personal job is to recover a usable handwritten signature and
finish a PDF without handing the source material to a cloud service.

The deeper product opportunity is controlled, repeatable document work with
local execution, explicit authorization, operator visibility, and recoverable
evidence.

The product is not automatically any of the following:

- a cloud e-signature provider;
- a certificate authority;
- a regulated-signature compliance product;
- a general PDF editor;
- a generic enterprise workflow platform;
- a cloud document-storage system;
- a claim that an image of a signature has legal force.

Primary sources:

- [PRODUCT.md](../../PRODUCT.md)
- [DESIGN.md](../../DESIGN.md)
- [docs/PRICING.md](../PRICING.md)
- [docs/research/2026-07-16_signkit_market_legal_vertical_research.md](../research/2026-07-16_signkit_market_legal_vertical_research.md)
- [docs/analysis/2026-07-16_local_first_trust_architecture_decision.md](2026-07-16_local_first_trust_architecture_decision.md)

## 4. Live checkout and ownership boundary

The checkout is materially dirty. The current working tree contains parallel
changes across desktop, backend, build, web, tests, docs, concepts, and generated
context. This exploration preserved those changes. It did not reset, stage,
commit, delete, or overwrite them.

| Product area | Canonical-looking source | Boundary |
| --- | --- | --- |
| Local extraction | `desktop_app/processing/extractor.py` | Intended owner of local extraction behavior. |
| Desktop application | `desktop_app/` | Local interaction, Vault, PDF, workflows, and operator UI. |
| PDF domain | `desktop_app/pdf/` | Rendering, placement, fields, annotations, templates, audit. |
| Local automation | `desktop_app/workflows/` | Recipes, jobs, monitoring, grants, matching, verification. |
| Browser control plane | `backend/app/routers/workspace.py`, `services/workspace.py`, `web/cloud_workspace/` | Metadata and execution coordination only at present. |
| Public acquisition | `index.html`, `_redirects`, checkout JavaScript | Landing and provider routing. |
| Concepts | `web/concepts/`, `web/archives/`, `web/backups/` | Review and exploration only. Not production sources of truth. |

The backend extraction service is provisional until parity fixtures, canonical
core selection, migration, deprecation, and rollback are established. Do not
create a second extraction engine or a second workspace route family.

## 5. Implemented and substantially present capabilities

### 5.1 Image ingestion and safety

Sources: `desktop_app/processing/`, `desktop_app/api/`,
`desktop_app/views/`, `backend/app/services/extraction.py`,
`tests/test_security.py`, and `tests/test_extraction_service.py`.

- PNG, JPEG, and JPG handling.
- Native file selection.
- Drag-and-drop workflow.
- Local file path handling.
- Extension validation.
- Magic-number validation.
- PIL/image validation.
- File-size, dimension, and total-pixel limits.
- Null-byte, path-length, traversal, system-directory, and suspicious-path rejection.
- Secure temporary file behavior.
- Empty-file and invalid-image rejection.
- Selection-coordinate and selection-size validation.
- EXIF orientation normalization.

### 5.2 Selection and image viewing

Sources: `desktop_app/widgets/image_view.py`,
`desktop_app/views/main_window.py`, and `desktop_app/views/main_window_parts/`.

- Rectangle selection.
- Selection persistence.
- Selection dimensions and position.
- Clear selection.
- Select and Pan modes.
- Zoom in/out, fit, reset, wheel zoom, and keyboard controls.
- Coordinate display and pane focus.
- Source, preview, and result panes.
- Visibility changes after selection and processing.
- Rotation controls.
- Result-only rotation.
- Source rotation path.
- Preview cropping.
- Context-sensitive control enablement.
- Coordinate mapping across zoom and rotation.
- Bounded PDF rendering cache.

The image-view rotation method contains a stub comment because the actual
rotation belongs to the extraction mixin. This is an ownership note, not a
second implementation.

### 5.3 Processing and extraction

Sources: `desktop_app/processing/extractor.py`, extraction views, and
`desktop_app/tests/test_extractor.py`.

- Threshold processing and auto-threshold mode.
- Debounced live previews.
- Color selection, hex input, and validation.
- Background removal and alpha output.
- Transparent PNG output.
- Quality analysis with score and rating.
- Auto-detection of candidate regions.
- Versioned golden-box fixture.
- Forensic/K-means mode.
- Watermark metadata and source hashing in forensic output.
- Async processing helpers.
- Processing failure explanations.

Proposals or research signals, not complete product claims:

- Otsu and adaptive thresholding.
- Morphological cleanup.
- Erode/dilate controls.
- Gaussian blur and anti-aliasing.
- Grayscale and ink-preserving output.
- Vectorization and SVG export.
- OCR and typed-text extraction.
- Signature-versus-seal classification.
- ML-based detection and optional model download.
- Training corpus, benchmarking, and user feedback loops.

Sources: [docs/ROADMAP.md](../ROADMAP.md), [docs/AUTO_DETECTION_ML.md](../AUTO_DETECTION_ML.md), [docs/research/batch_processing.md](../research/batch_processing.md), and [docs/analysis/FEATURE_EXPANSION_ROADMAP_2026-06-17.md](FEATURE_EXPANSION_ROADMAP_2026-06-17.md).

### 5.4 Export, clipboard, Vault, and library

Present or substantially present:

- PNG-24, PNG-8, and JPEG export.
- Transparent, white, black, and custom backgrounds.
- JPEG quality control.
- Trim-to-content.
- DPI/resolution paths.
- Native save dialog.
- Filename generation and export-location memory.
- Export success/failure messages.
- Save-to-library quick path.
- Clipboard copy path.
- Encrypted local Vault blobs.
- Local metadata index.
- Restrictive key/file permissions when initialized.
- Signature thumbnails, names, tags/search signals, usage history, open/reuse,
  delete, refresh, and metadata fallback behavior.
- Signature asset IDs and workflow references.
- Metadata sidecars and JSON export proposal.
- SVG export proposal.

Open work:

- Corrupt metadata recovery.
- Vault backup and restore.
- Key rotation and key-loss recovery.
- Asset provenance, intended-use, consent, and revocation.
- Secure deletion evidence.
- Shared/team Vault ownership.
- Cross-device synchronization.

Sources: `desktop_app/views/export_dialog.py`, `desktop_app/views/vault_tab.py`,
`desktop_app/views/library_tab.py`, `desktop_app/processing/library_storage.py`,
and related tests.

### 5.5 PDF workspace

Sources: `desktop_app/pdf/`,
`desktop_app/views/main_window_parts/pdf.py`, and PDF tests.

- Open/close PDFs.
- Multi-page rendering and navigation.
- Page numbers, zoom, pan, and render cache.
- Signature placement, movement, resizing, and multiple signatures.
- Bulk placement.
- Field-candidate detection.
- Native form-field detection.
- Choice and radio fields.
- Field taxonomy and anchor metadata.
- Ratio-based placement.
- Highlight and note annotations.
- PDF save.
- PDF audit logs and run manifests.
- Document session persistence.
- Optional PDF stack profiles.
- Output verification.

Explicit or inferred next capabilities:

- Reusable placement templates and template versioning.
- Anchor-text, page-aware, and field-mapped placement.
- Form auto-fill.
- Document comparison.
- Redaction.
- PDF merge/split and password protection.
- PDF/A handling.
- Tamper evidence.
- Evidence-package export.
- Certificate-backed signing.
- Signature validation.
- Timestamping.
- Signing order and multi-party completion.
- Undo/redo.

Sources: [docs/LIGHTWEIGHT_PDF_SIGNING.md](../LIGHTWEIGHT_PDF_SIGNING.md), [docs/IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md), [docs/research/bulk_pdf_signing.md](../research/bulk_pdf_signing.md), [docs/research/digital_certificate_support.md](../research/digital_certificate_support.md), [docs/research/undo_redo_system.md](../research/undo_redo_system.md), and [docs/analysis/LONG_TERM_PDF_WORKSPACE_ARCHITECTURE_2026-06-18.md](LONG_TERM_PDF_WORKSPACE_ARCHITECTURE_2026-06-18.md).

### 5.6 Templates, recipes, and local workflow engine

Present:

- Local PDF template storage, migration, update, delete, and multi-binding.
- Recipe creation and editing.
- Exact, family, and review-only matcher modes.
- Unsigned input, signed output, and optional review folders.
- Folder separation validation.
- Role-based signature bindings.
- Page and ratio coordinates.
- Template import.
- Dry run.
- Draft and activated recipe states.
- Folder discovery and new-file detection.
- Already-queued suppression.
- PDF-driver validation.
- Grant, asset-scope, and folder-scope validation.
- Queueing, processing, review routing, output verification.
- Pause, resume, retry, cancel, failed, completed, and quarantine states.
- Operator controls, job history, status summaries, and local audit signals.

Open hardening:

- Idempotency keys and stronger duplicate identity.
- Crash recovery and partial-batch recovery.
- Backpressure and scheduling.
- Notifications.
- Retention.
- Cross-device reconciliation.
- Cross-topology event mapping.
- Operator explanations for failed or skipped items.

Sources: `desktop_app/pdf/template_store.py`,
`desktop_app/workflows/models.py`, `store.py`, `engine.py`,
`folder_monitor.py`, `matcher.py`, `authorization.py`,
`verifier.py`, and the workflow views/tests.

### 5.7 Authorization, licensing, and packaging

Present:

- Trial, Starter, Team, and Business tiers.
- Export, PDF-operation, and workflow-automation entitlements.
- Workflow automation add-on.
- Grant creation and revocation.
- Approver subjects, runner roles, allowed assets, allowed folders,
  maximum jobs, expiry, and fail-closed behavior.
- Upgrade routing for locked screens.
- Standard and macOS Premium profiles.
- PyInstaller and platform build specs.
- Entrypoint and profile tests.
- macOS bundle and code-signing paths.
- Native runtime QA artifacts.
- macOS menu-bar, Dock, file-association, native palette, SF Symbols,
  accessibility, dark-mode, and auto-update directions.

Open work:

- Real organization identity and membership.
- Permission inheritance and revocation propagation.
- Provider receipt verification.
- Refund/chargeback handling.
- Duplicate activation handling.
- Full install/launch proof per platform.
- Signed release artifacts.
- Update channels and rollback.
- Crash diagnostics with privacy controls.
- VoiceOver, high-contrast, and reduced-motion audits.
- App Store decision.
- DMG and installer experience.

Sources: [DESIGN.md](../../DESIGN.md), [docs/MACOS_NATIVE_INTEGRATION_PLAN.md](../MACOS_NATIVE_INTEGRATION_PLAN.md), `build-tools/`, `desktop_app/launch_profile.py`, and `docs/review/`.

### 5.8 Backend workspace control plane

Present:

- Registration and login.
- JWT authentication.
- Owner-scoped execution access.
- Versioned template catalog.
- Execution creation.
- Participant and reviewer fields.
- Explicit state transitions.
- Cancellation.
- Append-only execution events.
- Event sequence numbers.
- Terminal-state replay rejection.
- Browser receipt/passport UI.
- Metadata-only storage.

Not proven or not present:

- Independent participant/reviewer identity.
- Document-byte storage contract.
- Signature-byte storage contract.
- Private object storage.
- Retention and deletion execution.
- Cloud-to-desktop worker mapping.
- Membership management.
- Cross-tenant isolation beyond owner scope.
- Hosted deployment and production API binding.
- Browser PDF execution.

Sources: `backend/app/routers/workspace.py`,
`backend/app/services/workspace.py`, `backend/app/schemas/workspace.py`,
`backend/app/models/workspace.py`, `web/cloud_workspace/`, and
[docs/analysis/2026-08-03_super_app_feature_matrix.md](2026-08-03_super_app_feature_matrix.md).

### 5.9 Public acquisition and commercial surface

Present or substantially present:

- Canonical root landing page.
- Redirect handling.
- Checkout provider routing.
- Dodo primary path when configured.
- Gumroad fallback.
- Plan-specific routing.
- Analytics hooks.
- Landing and deployment smoke tests.
- Pricing, EULA, privacy, terms, and refund surfaces.
- Product screenshots.
- Concept/archive separation.

Open work:

- Production redirect and content-type proof.
- Dodo product configuration.
- Payment fulfillment and activation delivery.
- Refund reconciliation.
- Honest customer proof.
- Support workflow.
- Conversion instrumentation.
- Stale public claim cleanup.

## 6. Explicit roadmap and research inventory

### Extraction

- Better automatic, adaptive, and scan-normalized thresholding.
- Morphology, noise cleanup, edge smoothing, anti-aliasing.
- Grayscale, ink-preserving, vector, and SVG output.
- OCR, typed-text extraction, signature classification.
- Signature candidate confidence and human acceptance.
- Lightweight local ML model, training data, benchmarking, feedback.
- Multiple-signature detection.
- Seal/stamp separation.
- Mobile and camera capture.

### PDF and document

- Undo/redo.
- Advanced annotations.
- Form auto-fill.
- Redaction.
- Document comparison.
- Merge/split.
- Password protection.
- Resize.
- Page templates.
- Signature fields and anchor placement.
- Bulk signing and batch queues.
- Certificate-backed signing, PAdES, timestamping, validation.
- Evidence packages and signing order.

### Workflow

- Batch processing.
- Bulk PDF signing.
- Folder automation.
- Recipe and template versioning.
- Review queues and approval policies.
- Retry, quarantine, scheduled jobs, notifications.
- Job limits, team roles, organization controls.
- Run manifests, audit exports, and recovery tools.

### Connectivity

- Local REST API.
- CLI.
- MCP interface.
- Browser extension.
- DocuSign, Adobe Sign, and Dropbox Sign adapters.
- Google Drive, Dropbox, and OneDrive adapters.
- Zapier, Make, Slack, and Teams adapters.
- Email intake, scanner integration, CRM, and document-management adapters.

### Cloud and hybrid

- Cloud template catalog.
- Browser workspace.
- Metadata execution register.
- Local worker pairing.
- Encrypted sync.
- Cross-device Vault.
- Cloud backup.
- Remote review.
- Team workspace.
- Membership and roles.
- Private storage.
- Retention and deletion controls.
- Consent ledger.
- Document-byte sync only by explicit opt-in.

### Platform and commercial

- macOS native controls, dark mode, SF Symbols, VoiceOver, high contrast.
- File associations, Open With, auto-update, Sparkle.
- Mac App Store, Windows installer, Linux AppImage, universal binary.
- Release channels, crash reporting, privacy-preserving analytics.
- Personal, Starter, Team, Business, Enterprise, workflow add-on.
- Subscription and lifetime experiments.
- Referral, affiliate, AppSumo, Product Hunt, directories.
- SEO, email onboarding, videos, podcasts, comparison pages, vertical sales packs.

## 7. Explicit use-case inventory

### Personal and independent

- Freelancers signing contracts.
- Consultants signing proposals.
- Remote workers signing forms while traveling.
- Students signing applications and recommendations.
- Rental, tax, and personal forms.
- Email-signature images.
- Personal brand and portfolio assets.

### Professional

- Real-estate disclosures and contracts.
- Accounting and tax returns.
- Legal agreements and filings.
- Sales proposals, quotes, and contracts.
- Insurance claim documents.
- Financial-advisor client packets.
- Contractor and architect approvals.
- Notary and administrative packet preparation.

### Organizational

- HR offer letters and onboarding.
- Employee policy acknowledgements.
- Vendor and procurement packets.
- Contract renewals.
- Accounts-payable approvals.
- Tax-return batches.
- Insurance claims.
- Loan and mortgage documents.
- Property management.
- Compliance evidence.
- Records and document operations.

### Advanced or speculative

- Signature provenance.
- Forgery detection and comparison.
- Seal/stamp separation.
- Multi-language OCR.
- Voice-assisted workflows.
- Tamper evidence.
- Cryptographic verification.
- Blockchain anchoring.
- Autonomous routing.
- Agentic document operations.

Sources: [docs/USE_CASES.md](../USE_CASES.md), [docs/FEATURES_USECASES_WORKFLOWS.md](../FEATURES_USECASES_WORKFLOWS.md), [docs/PRODUCT_STRATEGY.md](../PRODUCT_STRATEGY.md), and [docs/research/2026-07-16_signkit_market_legal_vertical_research.md](../research/2026-07-16_signkit_market_legal_vertical_research.md).

## 8. Architecture-derived roadmap

These items follow from the current code shape and are required if expansion is
to avoid parallel truths.

### 8.1 Canonical execution contract

```
WorkspaceExecution
  -> command envelope
  -> WorkflowJob child
  -> state transition
  -> event receipt
  -> output/evidence reference
```

Required properties:

- topology: local, cloud, or hybrid;
- correlation ID;
- idempotency key;
- command version;
- actor and role;
- input/output references;
- retry count;
- state transition;
- failure reason;
- recovery action;
- audit timestamp;
- source of truth;
- rollback behavior.

### 8.2 Signature asset contract

Before synchronizing Vault data, define a versioned record containing asset ID,
encrypted content reference, source hash, extraction method, processing settings,
quality score, owner, intended use, allowed workflows, timestamps, revocation,
and deletion state.

### 8.3 Document evidence contract

Every completed document should be able to explain its input, template, asset,
coordinates, authorization, validations, warnings, output, human review, and
reproduction or rejection path.

### 8.4 Policy engine

Extend grants into identity, organization membership, role/capability claims,
asset/folder/template/document scope, volume, expiry, approval, revocation,
audit reason, and offline behavior.

### 8.5 Recovery-first operator design

Every operation needs visible status, failure explanation, retry decision,
quarantine behavior, source preservation, output verification, operator next
action, and an audit receipt.

### 8.6 Model, pipeline, and data separation

For OCR, auto-detection, document classification, and future AI features, keep
model behavior, pipeline orchestration, and schemas/labels/fixtures/thresholds/
benchmarks separate.

## 9. New open exploration

### 9.1 Signature Asset Passport

Turn the Vault into a trustable asset system. Each asset carries source
provenance, processing history, consent, quality, use scope, and revocation.

### 9.2 Document Completion Passport

Produce a portable local evidence bundle containing input/output hashes, template
version, asset references, operator, grant, validation, and review history.

### 9.3 Private document-operations agent

Expose the same authorized execution model through a local CLI, API, or MCP
surface for queue inspection, recipe runs, approvals, retries, and evidence export.

### 9.4 Vertical workflow packs

Potential bounded packs:

- HR onboarding;
- legal contract execution;
- real-estate disclosures;
- accounting and tax returns;
- insurance claim documents;
- procurement and vendor packets.

Each pack must define roles, templates, validation, review, retention, and safe
language. An industry label must not imply legal compliance.

### 9.5 Human review as the automation differentiator

Make review explicit: explain routing, show candidate fields, compare expected
and observed structure, approve/reject/edit/reprocess, retain reviewer identity,
and generate a receipt.

### 9.6 Private collaboration

Share recipes, templates, metadata, state, and evidence while keeping document
bytes on authorized local workers.

### 9.7 Local intelligence extensions

Support extraction models, OCR packs, field detectors, PDF adapters, templates,
and connectors through versioned, permissioned, trusted plugin contracts.

### 9.8 Signature capture graph

Use local relationships between signatures, templates, documents, and roles to
improve recommendations without sending raw documents to a server.

### 9.9 Document operations observatory

Expose queue health, review backlog, failure clusters, template drift, asset use,
quality, retry rate, output verification, and privacy/storage state.

### 9.10 The durable category may be document completion

The future category may be identify fields, insert approved assets, fill permitted
data, review, validate, export, and produce evidence. Signature extraction
remains the wedge.

## 10. Product differences to protect

| Difference | SignKit direction | Alternative to avoid |
| --- | --- | --- |
| Privacy | Local by default, explicit sync consent | Silent cloud upload. |
| Execution | Repeatable and inspectable workflows | Black-box automation. |
| Assets | Versioned and scoped Vault assets | Untracked image files. |
| Review | Human review and recovery are first-class | “Automation succeeded” without proof. |
| Legal language | Distinguish image placement from regulated signing | Broad legal guarantees. |
| Architecture | One shared execution and PDF contract | Separate desktop, browser, and cloud engines. |
| Collaboration | Share control metadata before document bytes | Cloud storage by default. |
| Product posture | B2C craft with operator depth | Generic enterprise dashboard. |
| AI | Local, explainable, benchmarked assistance | Unvalidated accuracy claims. |

Adobe already covers cloud signature requests, recipient ordering, reminders,
authentication, and cloud storage. SignKit should not copy that surface without a
clear local-execution or trust advantage. See [Adobe’s official workflow](https://helpx.adobe.com/acrobat/desktop/e-sign-documents/request-e-signatures/send-for-signing.html).

## 11. Dependency-ordered candidate roadmap

This is a candidate sequence, not an approved build schedule.

### Foundation gate

- Confirm canonical extraction owner.
- Remove or label duplicate/temporary backend extraction paths.
- Establish end-to-end local extraction fixtures.
- Establish PDF placement and save fixtures.
- Establish Vault recovery and deletion behavior.
- Establish one release artifact per supported platform.
- Establish honest product and launch claims.

### Local completion gate

- Complete extraction quality and failure explanations.
- Complete PDF placement, fields, annotations, and export.
- Complete template and recipe versioning.
- Complete retry, cancellation, quarantine, and recovery.
- Complete operator audit and evidence export.

### Team operations gate

- Complete identity and organization roles.
- Complete policy/grant lifecycle.
- Complete shared recipe/template contracts.
- Complete review lane.
- Complete duplicate and retry semantics.
- Complete operator observability.

### Hybrid coordination gate

- Define asset and document data boundaries.
- Define sync consent.
- Define encrypted transfer and key ownership.
- Map `WorkspaceExecution` to `WorkflowJob`.
- Add correlation, idempotency, and rollback.
- Keep document bytes local until the storage decision is accepted.

### Ecosystem gate

- Stabilize local CLI/API/MCP contract.
- Add one connector through the canonical pipeline.
- Add plugin permissions and compatibility policy.
- Add connector retry and audit behavior.

### Trust and regulated gate

- Separate image placement from certificate-backed signing.
- Research certificate and timestamp providers.
- Define identity, intent, custody, and evidence.
- Run legal and security review.
- Require Tier 3+ evidence before customer-facing claims.

## 12. Build, research, defer, and reject classification

### Strong build candidates

- Local extraction quality.
- PDF placement correctness.
- Vault reliability.
- Template and recipe correctness.
- Workflow recovery.
- Audit and evidence receipts.
- Operator visibility.
- Packaging and release proof.
- Personal-to-team boundaries.

### Research before building

- Cloud document storage.
- Cross-device Vault sync.
- Certificate-backed signing.
- Browser PDF execution.
- Mobile capture.
- ML training and feedback.
- External e-signature adapters.
- Enterprise compliance packs.
- Autonomous document routing.

### Defer unless evidence changes

- Blockchain anchoring.
- Broad generic PDF-editor features.
- A large connector marketplace.
- Many simultaneous vertical packs.
- Cloud-first signature storage.
- Full mobile application.
- Broad marketing automation.

### Avoid as product claims

- “Legally binding” without a specific supported contract.
- “HIPAA compliant” or “GDPR compliant” as blanket claims.
- “AI-powered accuracy” without a benchmark corpus.
- “Never leaves your device” when an enabled path uploads data.
- “Fully automated” when review or recovery is manual.
- “Enterprise ready” based only on local UI and unit tests.

## 13. Risk register and closure paths

| Risk | Current state | Closure path |
| --- | --- | --- |
| Hosted landing is stale | Production route/content-type proof is not accepted | Run route, content-type, and checkout smoke against deployment. |
| Payment fulfillment is unproven | Dodo configuration is incomplete and Gumroad is fallback | Complete receipt, activation, retry, refund, and reconciliation flow. |
| Cloud upload privacy boundary | Existing extraction route is not a safe cloud workflow | Privacy/storage ADR, owner scope, retention, deletion, encryption, Tier 3 tests. |
| Duplicate extraction ownership | Desktop is intended owner; backend is provisional | Fixture parity, canonical-core decision, migration, deprecation, rollback. |
| Workflow recovery | Controls exist, populated runtime proof is incomplete | Execute a batch with failure, retry, quarantine, and evidence receipt. |
| Auto-detection quality | Golden fixture and sample runtime evidence exist | Labeled corpus and precision/recall or equivalent report. |
| Vault corruption | Invalid metadata can reset in-memory state | Backup, restore, corruption recovery, key ownership, deletion tests. |
| Legal signature confusion | Image placement and regulated signing are adjacent | Separate language, UI labels, contracts, and certificate roadmap. |
| Parallel work drift | Large dirty checkout | Recheck ownership before each implementation group; avoid broad rewrites. |

## 14. Metrics and evidence to add

### Product quality

- Extraction success by input class.
- Candidate-detection precision and recall.
- Manual correction rate.
- PDF placement correction rate.
- Export failure rate.
- Vault recovery success.
- Template match rate.

### Workflow reliability

- Queue completion.
- Review routing.
- Retry success.
- Quarantine rate.
- Duplicate suppression.
- Operator recovery time.
- Output verification.

### Trust and privacy

- Local-only execution rate.
- Explicit sync-consent rate.
- Raw document uploads.
- Retention compliance.
- Deletion verification.
- Audit-receipt completeness.

### Commercial

- Landing-to-checkout conversion.
- Purchase-to-activation success.
- Duplicate activation rate.
- Refund rate.
- Workflow add-on adoption.
- Repeat document completion.
- Support contact rate.
- Paid customer use-case distribution.

## 15. Source inventory

### Product and strategy

- `PRODUCT.md`
- `DESIGN.md`
- `docs/ROADMAP.md`
- `docs/PRODUCT_STRATEGY.md`
- `docs/USE_CASES.md`
- `docs/FEATURES_USECASES_WORKFLOWS.md`
- `docs/FEATURE_LIST.md`
- `docs/PRICING.md`
- `docs/DOMAIN_EXPANSION_STRATEGY.md`
- `docs/VERTICAL_INTEGRATION_PRODUCT_VISION.md`
- `docs/SIGNKIT_ECOSYSTEM_MASTER_PLAN.md`

### Architecture and decisions

- `docs/decisions/ADR-0140-super-app-vertical-horizontal-integration.md`
- `docs/decisions/2026-07-31_product_museum_experience_architecture.md`
- `docs/analysis/2026-07-31_topology_aware_workspace_foundation.md`
- `docs/analysis/2026-08-02_app_feature_and_build_readiness.md`
- `docs/analysis/2026-08-02_launch_readiness_and_pricing_decision.md`
- `docs/analysis/2026-08-03_super_app_feature_matrix.md`
- `docs/analysis/2026-08-04_cloud_mcp_signature_extraction_discussion.md`
- `docs/analysis/2026-07-16_local_first_trust_architecture_decision.md`
- `docs/analysis/2026-07-16_signkit_workflow_conversion_decision.md`
- `docs/analysis/2026-06-28_signkit_sensitive_document_positioning.md`
- `docs/analysis/2026-07-01_broader_improvement_survey.md`
- `docs/analysis/2026-07-01_performance_optimization_audit.md`

### Historical roadmap and research

- `docs/LLM_REVIEW_PROMPT.md`
- `docs/COMPREHENSIVE_REVIEW_PROMPT.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/IMPLEMENTATION_PLAN_CHATGPT_REVIEW_NOV_2_2025.md`
- `docs/CRITICAL_SUCCESS_GAPS_ANALYSIS.md`
- `docs/POST_LAUNCH_DEVELOPMENT_PLAN.md`
- `docs/FEATURE_RESEARCH_INDEX.md`
- `docs/analysis/FEATURE_EXPANSION_ROADMAP_2026-06-17.md`
- `docs/analysis/ROADMAP_30_60_90_2026-06-17.md`
- `docs/analysis/LONG_TERM_PDF_WORKSPACE_ARCHITECTURE_2026-06-18.md`
- `docs/analysis/SIGNATURE_FIELD_AND_PDF_EDITING_SPEC_2026-06-17.md`
- `docs/analysis/UNIQUE_PROPOSITION_BRIEF_2026-06-17.md`
- `docs/analysis/VISION_AND_STRATEGY.md`
- `docs/research/batch_processing.md`
- `docs/research/bulk_pdf_signing.md`
- `docs/research/digital_certificate_support.md`
- `docs/research/keyboard_shortcuts.md`
- `docs/research/undo_redo_system.md`
- `docs/AUTO_DETECTION_ML.md`
- `docs/LIGHTWEIGHT_PDF_SIGNING.md`

### Exploration and concepts

- `docs/exploration/2026-06-19_wide_open_brainstorm/`
- `docs/exploration/2026-06-19_native_local_pdf_signature_brainstorm/`
- `docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/`
- `docs/exploration/2026-07-31_product_museum_wide_open_brainstorm.md`
- `web/concepts/`
- `web/archives/`
- `web/backups/`

### Code, tests, and runtime surfaces

- `desktop_app/processing/`
- `desktop_app/pdf/`
- `desktop_app/workflows/`
- `desktop_app/license/`
- `desktop_app/views/`
- `desktop_app/api/`
- `backend/app/`
- `web/cloud_workspace/`
- `web/live/`
- `build-tools/`
- `tests/`
- `desktop_app/tests/`
- `backend/tests/`
- `flows/`

## 16. Open decisions

1. Is SignKit primarily a local personal tool, a local document-operations
   system, or a hybrid platform?
2. Is the durable category signature extraction, PDF signing, or document
   completion?
3. Which one or two verticals deserve a full workflow pack first?
4. Does cloud store metadata only, encrypted assets, or document bytes?
5. What is the exact legal boundary between image placement and digital signing?
6. Is the browser workspace an operator console, a customer product, or both?
7. Is MCP/CLI a first-class interface or an integration experiment?
8. Should certificate-backed signing be built, partnered, or excluded?
9. What evidence is required before calling workflows ready?
10. Which old marketing and pricing promises must be retired?
11. Which capabilities belong in Personal, Team, and Business tiers?
12. What repeated workflow proves willingness to pay?

## 17. “Anything else?” sweep

The largest missed implication is that SignKit has two different kinds of trust:

1. **Content trust:** the extracted signature or placed PDF looks correct.
2. **Process trust:** the system explains who authorized the action, what happened,
   what failed, what was reviewed, and how to recover.

Better image processing does not create process trust. Better workflow state does
not create legal validity. Better cloud coordination does not create privacy
permission.

The most valuable future artifact may not be a signed PDF. It may be a portable,
defensible completion record that lets a human or organization understand the
document’s history without surrendering all source material to a third party.

## 18. Exploration conclusion

The idea survived the broad exploration under these conditions:

- local execution remains real product behavior;
- the personal workflow remains excellent;
- workflow automation stays explainable and recoverable;
- cloud remains an explicit topology choice;
- document bytes do not move without a privacy/storage decision;
- image signatures are not marketed as regulated digital signatures;
- extraction quality is benchmarked rather than asserted;
- shared execution, asset, PDF, and evidence contracts remain canonical;
- concepts and future surfaces remain additive until an explicit migration gate.

The recommended long-term direction is a privacy-first document-completion
operating system, with signature extraction as the wedge and controlled local
workflow execution as the compounding advantage.

## 19. Update log

### 2026-08-04

- Consolidated current code, tests, product docs, research, architecture
  decisions, historical roadmaps, concepts, and new exploration.
- Added evidence vocabulary and separation between implementation, proposal,
  inference, research, and historical material.
- Recorded local, team, cloud, hybrid, ecosystem, and regulated horizons.
- Recorded architecture-derived contracts, risks, metrics, and open decisions.
- Preserved all unrelated and parallel checkout changes.

