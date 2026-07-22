# SignKit market, legal-signature, vertical, and pricing research

**Date:** 2026-07-16
**Status:** Canonical research baseline; implementation proposals require staged validation
**Boundary:** Local-first signed-document workspace, not a generic PDF editor or cloud-first DocuSign clone

## Executive decision

SignKit's strongest long-term position is **the private workstation for preparing,
signing, validating, and evidencing sensitive documents**. The current extraction,
Vault, PDF placement, field detection, templates, batch processing, and local audit
work together form the foundation.

1. **Local document work remains the default.** Documents, signatures, templates,
   workspaces, indexes, and ordinary audit history stay on the user's device or an
   explicitly selected office-controlled location.
2. **Trust is selectable per transaction.** Choose local self-signing, an
   evidence-backed e-signature ceremony, or a certificate/qualified signature through
   the user's certificate or a regulated partner.
3. **Online services are narrow capabilities.** Remote invitations, identity checks,
   regulated signatures, timestamps, and optional encrypted sync are invoked only when
   required.

This creates a useful category between basic offline PDF tools and cloud agreement
platforms: **local-first document execution with upgradeable legal evidence**.

## Current product truth

Static inspection confirms local signature extraction/cleanup, a Vault with usage
history, PDF viewing and placement, field detection, reusable placement templates,
bulk/template paths, a batch extraction queue, PDF audit logs/run manifests, and
signed-PDF export.

These audit logs are operation history, not yet a legally designed signing ceremony or
cryptographically verifiable evidence package. Image placement must remain labelled as
local PDF signing, not universally binding remote e-signature.

## Research method and evidence boundary

This pass reviewed current code and SignKit docs; official sources for the US, EU, and
India; current official competitor pricing/product pages; and official legal,
accounting/tax, and real-estate workflow material.

No paid market-size report or primary customer-interview dataset was available. TAM,
conversion, willingness-to-pay, and persona-frequency claims in older docs remain
hypotheses. Unsupported CAGR and revenue projections are not carried forward.

## Market structure

### Horizontal platforms

DocuSign sells cloud envelopes, templates, audit trails, reminders, identity checks,
integrations, and administration. Its current public US annual pricing is approximately
$11/month Personal, $30/user/month Standard, and $45/user/month Business Pro, subject
to allowances/add-ons. Adobe Acrobat sells a wider PDF suite: approximately $14.99/month
Standard and $19.99/month Pro for individual annual plans.

**Implication:** do not compete on cloud-envelope breadth. Compete on ownership,
offline use, sensitive-file handling, extraction quality, high-volume local preparation,
and transparent trust upgrades.

### Vertical platforms

Vertical products embed signatures inside the real job:

- Clio connects legal document generation, matter storage, intake, court forms,
  e-filing, and signatures.
- TaxDome connects taxpayer/client records, spouse/preparer roles, return delivery,
  templates, reminders, KBA or EU QES/AdES, payment, status, and certificates.
- DocuSign Rooms connects transaction rooms, forms, compliance review, deadlines,
  broker approval, templates, and signatures.

Industry packs therefore cannot be decorative template bundles. They must encode
roles, document sets, required fields, review gates, deadlines, evidence levels, export
structure, and system-of-record handoff.

### Local-first gap

The product thesis is:

- finish sensitive PDFs without uploading working copies;
- reuse signatures, seals, stamps, and placement rules locally;
- process messy scans and repeated document sets efficiently;
- produce a clear evidence package when a signature may be disputed;
- escalate to regulated identity/certificate services without moving the whole workflow
  into a third-party repository.

This is a thesis to validate in interviews, not a proven market-share claim.

## Priority personas and jobs

### Legal operations professional — primary

**Roles:** solo lawyer, paralegal, legal assistant, small-firm operations.
**Jobs:** engagement letters, NDAs, affidavits, authorisations, settlement documents,
exhibits, and closing bundles.
**Pain:** inconsistent scans/signatures, confidential files crossing services, missed
fields, and separated executed copies/evidence.
**Local-first value:** matter-contained files, reusable party/role templates, redaction,
comparison, privilege-conscious processing, and defensible exports.
**Trust:** consent, attribution, integrity, chronology, witness/notary metadata where
applicable, and explicit exceptions for special-formality documents.

### CA/accounting/tax practice — primary in India

**Roles:** chartered accountant, tax preparer, assistant, audit team.
**Jobs:** engagement letters, management representations, declarations,
authorisations, tax signature pages, client approvals, DSC filings, annual packs.
**Pain:** taxpayer/spouse/preparer roles, repetitive packs, missing signatures,
DSC-token friction, sensitive financial data, and deadlines.
**Local-first value:** client/year workspaces, checklists, bulk field mapping, DSC
readiness, local evidence exports, and filing-workflow handoff.
**Trust:** distinguish ordinary approvals from filings requiring a registered DSC or
portal verification; an image signature never substitutes for a DSC.

### Real-estate transaction professional — primary

**Roles:** agent, broker, coordinator, property lawyer/conveyancer.
**Jobs:** listings, disclosures, offers, addenda, inspection acknowledgements, leases,
broker approvals, handover and closing packets.
**Pain:** revisions, deadlines, repeated party data, page initials, missing forms,
compliance review, fragmented copies.
**Local-first value:** property transaction workspace, form-set templates, compare,
initial/date rules, deadline checklist, complete closing archive.
**Trust:** jurisdiction/form rules, attribution, version integrity, broker approval, and
completion history.

### Secondary personas

- **HR/people operations:** offer letters, NDAs, acknowledgements, contractor,
  onboarding, and exit packs; needs retention and countersigning controls.
- **Document-service/back-office teams:** scan cleanup, asset extraction, classification,
  field placement, completeness review, batch exceptions, deterministic output, and
  controlled delivery.

## Industry capability matrix

| Capability | Legal | CA/accounting | Real estate | HR | Priority |
| --- | --- | --- | --- | --- | --- |
| Local workspace | Matter | Client + period | Property + deal | Employee | Now-next |
| Document-set checklist | Filing/closing | Return/audit | Disclosure/closing | Onboard/exit | Now-next |
| Role-aware fields | Client/counsel/witness | Taxpayer/spouse/CA | Buyer/seller/broker | Employee/manager/HR | Next |
| Placement templates | High | High | High | High | Foundation exists |
| Missing-field validation | High | High | High | High | Next |
| Batch initials/dates | Medium | High | High | Medium | Next |
| Compare/content freeze | High | Medium | High | Medium | Next |
| Irreversible redaction export | High | High | Medium | High | Next |
| Evidence package | High | High | High | High | Trust foundation |
| DSC/PKCS#11 signing | Medium | Critical in India | Situational | Situational | Trust foundation |
| Remote invitation/status | High | High | High | High | Optional service |
| Witness/in-person ceremony | High | Low | Medium | Low | Later vertical |
| System export | Legal DMS | Tax/practice suite | Transaction system | HRIS | Integration stage |

## How SignKit can provide legally accepted signatures

There is no worldwide certificate that makes every signature valid. Select the legal
and evidence profile required by the document and jurisdiction.

### Level A — local self-sign and PDF completion

Add document hashing, explicit “I intend to sign” confirmation, signed-at time,
app/device identifier, optional reason/location, and an exportable receipt to the
current flow.

This strengthens evidence of a local action. It does not independently verify identity,
recipient consent, or a regulated certificate and must not be labelled qualified,
certified, or universally legally binding.

### Level B — evidence-backed electronic-signature ceremony

1. Freeze the exact document version and calculate SHA-256.
2. Show the complete document and required disclosures.
3. Capture agreement to electronic records where applicable.
4. Capture an explicit intent-to-sign action.
5. Attribute the signer through authenticated profile, email link, OTP, in-person
   witness, or a stronger identity service.
6. Bind each action to signer, role, document hash, field/page/coordinates, UTC time,
   and ceremony ID.
7. Finalize the PDF so later changes are detectable.
8. Produce a readable completion certificate and machine-readable signed evidence.
9. Preserve an append-only event chain and reproducible final document.
10. Provide independent desktop and portable CLI verification.

US ESIGN prevents denial solely because a record/signature is electronic but does not
remove other substantive requirements. Consumer workflows can require affirmative
consent and access/retention disclosures. UETA adds transaction, intent, attribution,
and record-retention concepts. Counsel must review excluded document types and
state/sector requirements.

### Level C — certificate-backed local digital signature

Support a user's certificate/private key through the OS keychain, PKCS#11 token, or
smart card. Create standards-compatible PDF signatures, preferably PAdES, and validate
the chain, revocation, and timestamp.

SignKit acts as a Signature Creation Application and validator. It generally need not
become a Certificate Authority merely to use a certificate issued by a trusted CA. It
must never export private keys and must use appropriately licensed components.

### Level D — regulated or qualified remote signature

- **India:** integrate a CCA-licensed CA/eSign Service Provider. The official model
  covers verified identity, consent, one-time HSM keys, certificate issuance, signing,
  and audit trail. Submit the document hash, not the document, where supported. Support
  users' registered DSCs for Income Tax and other portal-specific workflows.
- **EU:** integrate a Trust Service Provider for advanced signatures and a Qualified
  Trust Service Provider plus QSCD/qualified certificate for QES. QES has the legal
  effect of a handwritten signature across EU Member States; simple and advanced
  signatures retain evidentiary effect with different assurance.
- **Elsewhere:** add jurisdiction profiles only after primary-source and counsel review.

### Required evidence schema

- ceremony ID and schema version;
- original/final SHA-256, byte length, and MIME type;
- signer ID/role and attribution method;
- consent disclosure version and acceptance;
- intent-to-sign event;
- fields, pages, coordinates, and completion events;
- UTC times and trusted timestamp token when used;
- IP/user-agent only for online flows under a retention/privacy policy;
- device/app version for local flows;
- identity-provider result references, not unnecessary raw identity data;
- certificate chain, algorithm, revocation evidence, and validation result;
- event-chain hashes, finalization, void/decline/failure/retry events;
- verification instructions and retention policy.

### Legal-review gates

Counsel must define excluded documents, consumer disclosure/withdrawal, witness/notary,
stamp-duty/registration, retention, identity-evidence privacy, certificate wording,
provider contracts, incident response, key compromise, revocation, and disputes before
public legal claims or production rollout.

## Local-first trust architecture

| Data | Default location | External use |
| --- | --- | --- |
| Source/final PDFs | Local workspace | Encrypted remote or provider-required flow |
| Signature images/stamps | Local encrypted Vault | Never uploaded by default |
| Templates/client metadata | Local | Explicit office-controlled sync/export |
| Evidence events | Local append-only store | Minimal encrypted remote relay |
| Identity proof | Provider reference/token | Regulated identity provider |
| Certificate private key | Hardware/OS key store | Never stored by SignKit cloud |
| Document hash | Local | TSA/eSign/verification service |

Modes shown before signing:

- **Private:** offline preparation, self-sign, local certificate signing, verify.
- **In person:** one-device signer/witness ceremony and evidence.
- **Connected:** encrypted remote invitation/event relay; owner retains canonical files.
- **Regulated:** hash/certificate operation through a licensed trust provider.

No silent cloud fallback is allowed.

## Product roadmap

### Defensible local completion

- canonical client/matter/transaction workspace and document set;
- hash/content-freeze service;
- versioned evidence schema and hash-chained log;
- consent/intent ceremony;
- certificate plus portable verifier;
- PKCS#11 discovery and PAdES signing proof-of-concept;
- visible trust mode and honest export labels;
- irreversible redaction, compare, and backup/export/recovery.

### Vertical workflows

- role-aware templates and document/field checklists;
- legal matter, CA client-period, and property transaction packs;
- bulk initials/dates and missing-signature review;
- deterministic bundles and evidence export;
- vertical onboarding/configuration without forking the core.

### Connected and regulated trust

- encrypted remote ceremony with expiry, decline, reminder, and revocation;
- selectable email/OTP attribution;
- India ESP and local DSC workflow;
- EU TSP/QTSP AdES/QES;
- trusted timestamp and long-term validation;
- operator view for failures, retries, provider events, and disputes.

### Practice operations

- office-controlled shared workspace/self-hosted relay;
- roles, approvals, policies, retention, and consolidated audit;
- evidence-led integrations with legal, tax, real-estate, and HR systems;
- APIs only after canonical local models/events stabilise.

## Pricing and packaging

Separate durable local software from services with recurring external costs.

### Personal — $39 one time; retain $29 launch offer

Current extraction, cleanup, Vault, PDF placement, templates, local export, and basic
local receipt. One person and a reasonable number of owned devices; purchased major
version plus promised minor updates.

### Professional — research target $89 one time

Workspaces, batch document sets, role templates, compare, redaction, completeness,
evidence-backed local/in-person ceremonies, completion certificates, verification, and
local DSC/PKCS#11/PAdES where supported. Include all vertical profiles rather than
charging separately by profession.

Test $69/$89/$119 through interviews and purchase-intent tests.

### Practice — research target $249 one time per five-seat office

Office-controlled sharing, permissions, approvals, policies, consolidated audit,
deployment guidance, and priority support. Optional annual maintenance/support after
included updates; no mandatory subscription for continued local use. Validate support
cost and willingness to pay before promising this package.

### Trust services — usage-based or optional connected plan

Remote sends, SMS/OTP, identity checks, qualified signatures, India eSign, and trusted
timestamps have provider costs. Sell transparent credits or an optional plan while
local software continues when credits expire. Show provider, assurance, unit cost, and
evidence outcome before confirmation.

## User research plan

Recruit 8–12 participants in each primary vertical (Legal, Indian CA/tax, Real Estate)
and 5–8 HR/back-office comparison participants.

Ask each participant to walk through their last real packet: origins/destinations,
third-party uploads, privacy concerns, missed fields, acceptable-signature rules,
reviewer/evidence needs, DSC/KBA/witness/notary cases, current spend, adoption blockers,
feature ranking, and package pricing. Demonstrate the real app, then ask for a purchase
or paid pilot; compliments are not demand evidence.

Store anonymised notes, workflow maps, feature frequencies, problem statements, buying
objections, and paid-pilot outcomes in a dated research folder. Use synthetic or
participant-redacted documents only.

## Metrics

- time to validated final bundle; documents/session; missing-field catches; template
  reuse; batch completion; percentage fully offline; verification success;
- complete consent/intent/attribution/integrity/retention rate; tamper detection;
  certificate/revocation/timestamp validation; provider failure/dispute rates;
- conversion by vertical/package; upgrade and trust-service attach; support cost,
  refunds, and paid-pilot conversion.

## Risks and non-goals

- Never claim “legally binding everywhere”; show jurisdiction, assurance, and evidence.
- One canonical document/role/policy/template/evidence model; no vertical code forks.
- Avoid raw identity-document storage unless strictly required and validated.
- Partner rather than becoming a CA/QTSP in the foreseeable strategy.
- Remote collaboration never becomes required for local signing.
- Do not generate synthetic signature variants.
- Blockchain anchoring does not replace identity, consent, or valid certificates.

## Primary sources and current references

### Law, regulation, standards

- US ESIGN, 15 USC 7001: https://uscode.house.gov/view.xhtml?req=(title:15%20section:7001%20edition:prelim)
- Uniform Electronic Transactions Act: https://www.uniformlaws.org/viewdocument/final-act-21
- EU eSignature types: https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/What+is+eSignature
- EU eSignature FAQ: https://ec.europa.eu/digital-building-blocks/sites/spaces/DIGITAL/pages/880312429/eSignature+FAQ
- ETSI PAdES EN 319 142-1: https://www.etsi.org/deliver/etsi_en/319100_319199/31914201/01.02.00_20/en_31914201v010200a.pdf
- NIST FIPS 186-5: https://csrc.nist.gov/pubs/fips/186-5/final
- India CCA eSign: https://cca.gov.in/eSign.html
- India active CA/eSign/TSA services: https://www.cca.gov.in/CAServicesPublic.html
- India Income Tax DSC registration: https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/register-digital-signature-certificate

### Competition and vertical workflows

- DocuSign pricing: https://ecom.docusign.com/plans-and-pricing/esignature
- Adobe pricing: https://www.adobe.com/acrobat/pricing.html
- Clio legal documents: https://www.clio.com/features/legal-documents/
- Clio legal e-signature: https://www.clio.com/features/legal-e-signature-software/
- TaxDome signature workflow: https://help.taxdome.com/article/291-e-signatures-explained
- DocuSign Rooms: https://www.docusign.com/products/rooms-for-real-estate

## Decisions versus hypotheses

**Recommended decisions:** keep local-first as centre; make trust explicit/selectable;
partner for regulated trust; keep one vertical-configurable core; separate perpetual
software from recurring services; require counsel and E2E evidence before legal claims.

**Hypotheses to validate:** Legal and Indian CA practices are the first highest-value
buyers; Professional sustains $89; offices prefer one-time plus optional maintenance;
privacy drives purchases; real-estate adoption can precede association-form integration.

## Review record

### Pass 1 — immediate correctness and completeness

Checked the request against current code, older product/pricing/GTM/vertical docs, and
the primary-source set. Corrected the earlier response's gap by documenting exactly how
SignKit can implement electronic and certificate-backed signing. Separated verified
current capabilities from proposed work and unsupported market assumptions.

### Pass 2 — architecture and long-term viability

Checked local-first behaviour end to end: source document, preparation, ceremony,
evidence, final PDF, verification, regulated provider, and operator failure visibility.
Consolidated all professions on one canonical model and rejected vertical forks,
cloud-first storage, CA operation, and image-only legal claims.

### Pass 3 — rule compliance and supervision readiness

Checked payment/pricing claims, high-risk legal language, external-provider boundaries,
data minimisation, evidence tiers, failure modes, decision ownership, validation gates,
rollback, and documentation routing. Remaining unknowns are explicitly assigned to user
research, security review, provider sandboxes, independent PDF validation, and counsel.
