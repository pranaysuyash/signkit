# SignKit Scaling and Expansion Evidence Baseline

**Date:** 2026-07-31
**Status:** Exploration baseline, not a final strategy or launch plan.
**Evidence level:** Tier 1 static inspection plus prior product/market exploration. Buyer demand, conversion, retention, and live provider behavior are unverified.

## Purpose

This baseline separates what SignKit demonstrably has today from opportunities that are plausible but unproven. It supports the [Wayfinder map](SIGNKIT_SCALING_EXPANSION_WAYFINDER_MAP.md) and must not be read as authorization to build every surface listed here.

## First-principles anchors

1. Sensitive document processing is valuable because the customer can retain control. Local execution is therefore a product advantage, not a temporary implementation limitation.
2. A monetizable surface must attach to a repeated, high-consequence customer outcome. Feature breadth alone is not a business model.
3. The web should add coordination, account ownership, or ecosystem reach. It should not duplicate trusted local execution without a user-proven reason.
4. Each expansion must preserve one canonical source of truth for licensing, workflow state, and customer claims.
5. No automation or integration may weaken authorization, review, quarantine, cancellation, auditability, or recovery behavior.

## Current product evidence

| Area | Static evidence | What it establishes | What it does not establish |
|---|---|---|---|
| Local document execution | Desktop extraction, PDF signing, and template flows | SignKit has a local execution core | Reliability at customer scale or legal validity in every jurisdiction |
| Controlled packet operations | `desktop_app/workflows/engine.py`, folder monitoring, execution grants, retry, review, quarantine, cancellation | A repeatable Legal/HR operator loop exists | Frequency of real customer use or willingness to pay |
| Commercial foundation | `desktop_app/license/storage.py`, `desktop_app/config.py`, checkout routing | Base tiers and a modular entitlement seam exist | Secure license issuance, live checkout, billing, or public price validity |
| Web presence | Existing landing and purchase-routing materials | A web acquisition surface exists | A web account product, tenancy boundary, or team control plane |
| Local audit posture | Workflow events, local receipts, and document-oriented records | Auditability is a product direction | Compliance certification, retention policy, or centralized reporting |

## Vertical expansion landscape

| Vertical | Repeatable job | Existing fit | Key unknown | Initial stance |
|---|---|---|---|---|
| Legal operations | Execute approved recurring contract and matter packets locally | Strong: authorization, recipes, review, and audit controls already align | Exact buyer, document volumes, and record-retention requirements | Primary validation wedge |
| HR operations | Onboarding, policy acknowledgement, offer, and employee-file packets | Strong: recurring packets and controlled templates map directly | Whether HR needs external signer collection or internal execution first | Co-primary validation wedge |
| Tax and CA offices | Client authorizations, recurring filings, signature/stamp assets | Strong local/privacy fit, with adjacent historical positioning | Seasonality, jurisdictional rules, and document-system integrations | Research candidate after Legal/HR proof |
| Document-service bureaus | Repeat production of approved client documents | Potentially strong for local throughput and templates | Multi-client isolation, operator accountability, and service workflow needs | Research candidate |
| Regulated healthcare/finance | High-sensitivity forms and approvals | Privacy positioning may fit | Compliance claims, integrations, and liability requirements | Out of early commercialization until proof exists |

## Horizontal expansion landscape

| Surface | Customer outcome | Existing fit | Main risk | Decision status |
|---|---|---|---|---|
| Automated Packet Ops | Complete recurring approved packets with review and recovery | Strong, based on existing workflow engine | Entitlement is not yet secure provider-issued licensing | First commercial module, not public launch-ready |
| Team policy and administration | Govern who can run which approved workflow | Partial: local execution grants exist | A web team layer could create a second authority model | Open |
| Local audit and receipt retention | Explain what happened and recover confidently | Partial: local events and audit records exist | Retention, export, and legal claims must be precise | Open |
| Document-system adapters | Trigger local work from existing systems | Low: no canonical adapter contract is established | Privacy leakage, duplicate workflow state, support burden | Open |
| Account and add-on activation web control plane | Buy, own, activate, and manage products without document upload | Partial: checkout routing and local entitlements exist | Identity, issuer, and customer-support operations are not defined | Likely first web candidate |
| Browser document execution | Work from anywhere in a browser | Weak against the product's local trust advantage | Generic-PDF drift, cloud-risk, and direct incumbent competition | Not an early candidate |

## Web product hypothesis

The viable web role is an **opt-in control plane**, not a second document-processing engine.

Candidate web responsibilities:

- product education, evaluation proof, and checkout;
- account ownership, license and add-on activation, invoices, and support;
- team administration and approved workflow policy only after a canonical authority model exists;
- opt-in workflow-status or receipt summaries that avoid document content by default;
- future integration configuration that instructs a local agent, rather than silently moving documents to a SaaS pipeline.

Responsibilities that remain local by default:

- document intake and content processing;
- signature assets and document outputs;
- full workflow records containing sensitive paths or content;
- execution, retries, recovery, quarantine, and cancellation.

## Integration design hypotheses to test

These are options, not recommendations yet.

| Shape | Description | Privacy posture | Product risk |
|---|---|---|---|
| Local-folder adapter | Existing document system deposits to a controlled local folder | Strong local default | Limited interoperability and operational setup |
| Local-agent adapter | A signed local agent receives metadata/policies and executes locally | Strong if document bytes remain local | Requires identity, device trust, update, and support design |
| Import/export adapter | User explicitly moves a selected document in or out of SignKit | Strong and simple | Lower automation value |
| Cloud relay | Provider stores or relays document bytes before local execution | Weakens local-first position | Creates security, compliance, and support obligations |

The map must decide whether any adapter needs a web control plane, what metadata is permitted to leave the device, and which workflow state remains authoritative locally.

## Commercial architecture hypothesis

The emerging model is not "more tiers." It is:

| Layer | Commercial role |
|---|---|
| Local core | Ownable execution tool with trusted baseline capabilities |
| Workflow modules | Named upgrades tied to repeated jobs, such as Automated Packet Ops |
| Team policy modules | Administration, roles, and governance when a real team need is proven |
| Integration modules | Explicit adapters priced against operational value, never hidden cloud dependency |
| Optional web control plane | Account and team coordination, separate from document execution |

This model protects the core wedge while creating multiple monetizable surfaces. It does not settle recurring versus one-time pricing, seat pricing, usage pricing, or product names. Those are decision tickets.

## Evidence needed before implementation

| Decision class | Minimum evidence before implementation |
|---|---|
| Vertical wedge | Five workflow interviews, real artifact samples where permitted, and explicit buyer/problem fit |
| Web control plane | A written authority model, user-data boundary, support workflow, and recovery path |
| Integration | Trigger-to-result sequence, data classification, idempotency strategy, audit record, and failure recovery |
| Commercial packaging | Purchase-intent signals, cost-to-serve estimate, activation method, and support/fulfilment owner |
| Public claims | Operational proof and legal/business review where privacy, compliance, or retention is mentioned |

## Current conclusion

SignKit has enough local workflow depth to validate a focused vertical and a first operational module. It does not yet have evidence to justify a broad web-app pivot, generic document cloud, enterprise integration claims, or a dense module marketplace. The map exists to turn these hypotheses into decisions without losing the local-first advantage.

## Addendum (2026-07-31): Delivery topology is a customer choice

Founder direction has refined the web hypothesis. The product will not assume that every customer wants a desktop-plus-web bundle. SignKit must be able to serve three deliberate customer choices:

| Topology | Customer promise | Required product truth |
|---|---|---|
| Local | "Keep the workflow on this device, with no sync." | No document, asset, workflow, or audit synchronization. Local recovery and local support path are clear. |
| Cloud | "Use SignKit entirely in the browser." | The web product can execute, store, recover, audit, and support the selected workflow without a desktop dependency. |
| Hybrid | "Use local execution and connected coordination together." | Sync is explicit, inspectable, recoverable, and has a documented source-of-truth and conflict policy. |

### Architectural consequence

Local, Cloud, and Hybrid must share one canonical domain model. They may have different deployment services, storage locations, and failure modes, but they may not develop separate definitions of a document, signature asset, workflow recipe, execution grant, job state, audit event, entitlement, or customer claim.

Every capability needs a topology matrix before it is implemented or marketed. The matrix must state:

1. Availability in Local, Cloud, and Hybrid.
2. Execution owner and authoritative state owner.
3. Whether document bytes, assets, metadata, audit data, or only entitlement data can leave the device.
4. Offline behavior, retry behavior, sync/idempotency behavior, conflict policy, and recovery path.
5. Customer-visible tradeoffs in privacy, latency, access, price, and support.

### Initial non-negotiables

- Local mode must not become a degraded trial of Cloud. It is a complete privacy-first product path.
- Cloud mode must not be a thin desktop remote-control wrapper. If sold as cloud-only, it needs its own complete operational lifecycle.
- Hybrid mode cannot silently merge or replicate sensitive material. The customer must explicitly enable each synchronized class, and conflicts must remain auditable rather than silently overwritten.
- Commercial entitlement belongs to the customer/account, but the product must preserve a locally usable license path for Local customers who do not want account sync.

This makes the next decision more important than feature selection: define the common capability and data contract first, then decide integrations, packaging, and the first web-native workflow against it.

## Addendum (2026-07-31): Features, templates, plans, and use-case exploration

### Evidence from existing repository documents

The repository already contains useful product thought, but it is not one current strategy document. Treat the following as historical inputs unless current code and a current decision confirm them:

| Source | Useful signal | Drift or limitation to preserve explicitly |
|---|---|---|
| `docs/FEATURES_USECASES_WORKFLOWS.md` | Clear individual, Legal, HR, CPA, sales, and real-estate job stories; signature library and placement are understandable customer primitives | November 2025 snapshot says workflow automation and team features do not exist, uses obsolete pricing/comparison claims, and states unverified GDPR/HIPAA compliance |
| `docs/research/bulk_pdf_signing.md` | Strong template, relative-positioning, form-field, queue, resume, progress, and exception-handling research | Research plan, not proof of current bulk-workflow or pricing behaviour; no public revenue estimates from it should be reused |
| `docs/research/digital_certificate_support.md` | Identifies certificate storage, validation, timestamping, revocation, verification, and audit requirements | Architecture proposal only. Digital signing, PAdES/eIDAS, and compliance claims must remain unshipped until independently built and verified |
| `docs/LIGHTWEIGHT_PDF_SIGNING.md` | Documents the local/offline PDF direction and a deliberately lightweight dependency posture | Historical implementation plan; it must not supersede the live PDF and workflow code paths |
| `docs/landing/AB_TEST_VARIANTS.md` | Existing acquisition and checkout experiment ideas | Historical Gumroad routes, traffic, analytics, and conversion assumptions conflict with present checkout configuration and require reconciliation before reuse |

### Feature architecture: templates are executable policy, not saved coordinates

A useful SignKit template has three layers. The same conceptual object should exist in Local, Cloud, and Hybrid even when its implementation differs.

| Layer | Purpose | Local example | Cloud or Hybrid extension |
|---|---|---|---|
| Document layer | Base document, form-field map, variables, and allowed input shape | Approved PDF plus relative placement or detected field anchors | Versioned document source, variables, and controlled field schemas |
| Workflow layer | Roles, preconditions, approval/review routing, expiry, and exception policy | Authorized recipe with grant, matching rule, review, quarantine, and retry policy | Participant roles, internal approvals, reminders, external signing, and guided creation steps |
| Governance layer | Ownership, versioning, entitlement, audit, sharing, and retirement | Local owner, vault references, versioned receipt, and local audit event | Workspace ownership, role-based publishing, read-only sharing, retention, and cross-workspace policy |

The useful product insight from current market evidence is that templates encode the repeatable process itself, not only reusable document content. Adobe distinguishes full document templates from reusable field layers and supports workflow-level prefill, role, routing, expiry, and reporting configuration. [Adobe library templates](https://helpx.adobe.com/sign/adv-user/library-templates/create-template.html) and [Adobe custom workflows](https://helpx.adobe.com/sign/adv-user/send-workflow/overview.html) provide current reference patterns. PandaDoc is similarly moving workflow steps such as data pull, approval, reminder, and payment into each template. [PandaDoc template workflow builder](https://support.pandadoc.com/en/articles/12108203-template-workflow-builder-and-guided-document-creation-full-guide)

### Candidate template families

These are investigation candidates, not product promises or legal templates.

| Family | Repeated customer job | Likely topology | Why it may be valuable | Key boundary |
|---|---|---|---|---|
| Local signing-placement template | Apply the right stored signature or initials to an approved recurring PDF | Local | Fastest continuation of existing asset, PDF, and workflow primitives | Must not imply certificate-backed or legally binding digital signature |
| Controlled packet recipe | Scan, match, review, execute, retry, and receipt a known document family | Local or Hybrid | Converts existing operations workflow into repeatable operational value | Needs strong authorization, dry-run, exception, and audit controls |
| HR onboarding pack | Offer, policy acknowledgement, starter documents, manager approval, employee delivery | Cloud or Hybrid | Recurring, structured, team-owned workflow with clear template value | External signer identity, retention, and employment/legal requirements require validation |
| Legal intake and approval pack | Engagement letters, NDAs, internal approval packets, document review | Local, Cloud, or Hybrid depending on workflow | High consequence and template-driven | Do not overclaim enforceability, identity verification, or secure e-signature without implementation |
| Finance and CA pack | Repeated client letters, approvals, tax-related workflow preparation | Local first | Strong repeatability and privacy fit | Certificate signing, jurisdiction, and tax/legal requirements are separate high-risk work |
| Sales proposal pack | Pull customer data, prepare proposal, route approval, collect acceptance | Cloud or Hybrid | Strong data-mapping and CRM integration value | Becomes a different market if CPQ/payment is treated as core too early |
| Procurement or vendor pack | Supplier onboarding, approval, quote/PO support, vendor document tracking | Hybrid | Repeatable internal approvals with tangible audit value | Integration and role model must precede automation claims |

### Candidate product and plan surfaces

This is a packaging hypothesis only. It deliberately contains no public price.

| Surface | Customer outcome | Topology availability | Candidate packaging boundary |
|---|---|---|---|
| Local Core | Extract, clean, manage assets, manually place, and save documents privately | Local | Ownable local product; no forced account or synchronization |
| Local Template and Batch Pack | Reuse placement templates, preview batches, execute manual/local batches, retain local receipts | Local | Optional module after operational validation |
| Automated Packet Ops | Operate approved recipes with scanning, queueing, review, retry, quarantine, and recovery | Local or Hybrid | Named workflow module, not a vague upper tier |
| Cloud Workspace | Create and run a full browser-native template workflow with roles, document data, approvals, audit, and recovery | Cloud | Subscription candidate only after complete cloud workflow proof |
| Hybrid Workspace | Synchronize explicitly selected templates, workflow policy, statuses, and permitted assets or documents | Hybrid | Connected-workspace module with explicit sync and data boundaries |
| Integration Adapter | Pull approved metadata, trigger a governed workflow, and write an audited result back | Cloud or Hybrid, with local-agent option | Price against operational value and support burden, never hide dependency in the core |
| Enterprise Governance | SSO, workspace policy, retention controls, audit export, administrative provisioning, and supported adapters | Cloud or Hybrid | Sales-led offer after tenancy and operational readiness exist |

### Integration ladder, not an integration catalogue

The market evidence shows that integrations become useful when they are attached to a template or workflow, not when they are a disconnected list of logos. Adobe documents the recurring patterns: Microsoft 365, SharePoint, Teams, Power Automate, Salesforce, Workday, templates, data mapping, webhooks, and administration. [Adobe integrations overview](https://experienceleague.adobe.com/en/docs/document-cloud-learn/sign-learning-hub/integrations/integrations-overview) and [Adobe integrations hub](https://helpx.adobe.com/sign/admin/integration-hub.html) support this observation. PandaDoc likewise configures CRM data pull at the template level and assigns it to workspace administration. [PandaDoc CRM workflow step](https://support.pandadoc.com/en/articles/14711198-pull-data-from-integration-crm-workflow-step)

Proposed research order:

1. **Local import/export and folder adapter:** explicit user-selected files and governed local folders. This strengthens the current local wedge and establishes reliable job semantics.
2. **Template-level webhook and status adapter:** emit an auditable, minimal event on a known lifecycle transition. Define idempotency before adding destinations.
3. **One vertical system adapter:** evaluate either SharePoint/Microsoft 365 for Legal/HR operations or a validated HR/CRM system for the selected wedge. Do not build both first.
4. **Local-agent bridge:** only if Hybrid customers need centralized policy or triggers while keeping sensitive document bytes local.
5. **Enterprise adapter ecosystem:** SSO, managed marketplace, CRM/ERP, and storage integrations only after a canonical tenant, permission, support, and recovery model exists.

### Feature candidates that should not be treated as early expansion

- A public template marketplace. First establish curated, governed, versioned packs with clear ownership and compliance review.
- Payment collection, CPQ, or broad sales-document generation. These can be cloud-native modules later but would distract from document-execution credibility now.
- Digital certificate, timestamp, or legal-validity claims. The research is valuable, but this is a separate security/compliance program with its own evidence bar.
- An undifferentiated catalog of integrations. Each adapter needs a selected workflow, data contract, failure recovery, and operator owner.

### Documentation and claim-reconciliation requirement

Before any web or plan launch, historical pricing, checkout, feature-comparison, compliance, and automation statements must be reconciled against live code and the selected topology. The goal is not to erase history; it is to keep dated source material while appending current claim-safe guidance and linking it to the canonical strategy.

## Addendum (2026-08-04): Cloud MCP signature extraction discussion

The operator clarified that MCP discussion applies to the future Cloud and
Hybrid expansion, not to the current local desktop product. A proposed
Cloud/Hybrid MCP surface for signature extraction is recorded in
`docs/analysis/2026-08-04_cloud_mcp_signature_extraction_discussion.md`.

The current proposed order is metadata-only workflow tools, followed by
owner-scoped asynchronous extraction jobs after extraction parity and the
privacy/storage contract are accepted. MCPMeter is treated as a possible
distribution and usage-metering adapter, not as SignKit's canonical billing,
identity, entitlement, or workflow source of truth.
