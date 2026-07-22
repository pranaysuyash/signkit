# Signature Platform Product Vision: From Extraction to E‑Sign Suite

## Addendum (2026-07-16)

This is a historical broad-platform exploration. The current direction is not a
cloud-first “DocuSign-class” clone. Use
`docs/research/2026-07-16_signkit_market_legal_vertical_research.md` and
`docs/analysis/2026-07-16_local_first_trust_architecture_decision.md` for the canonical
local-first trust modes, jurisdiction/provider boundaries, vertical model, pricing
hypotheses, and validation plan. Existing ideas below remain useful inputs, but their
phases, legal statements, market positioning, and architecture are not implementation
commitments unless adopted by a newer decision record.

This document lays out how the current signature extraction tool evolves into a vertically integrated, DocuSign‑class e‑signature platform. It covers product vision, user journeys, features, architecture, compliance, and a phased roadmap aligned to the existing codebase.

---

## 1) North Star & Principles

- North Star: Make it fast, private, and trustworthy to prepare, send, and sign documents using real signatures — from local extraction to legally defensible e‑signatures at scale.
- Principles:
  - Privacy-first: local by default, cloud optional with clear controls.
  - Precision and control: pro-grade extraction, alignment, and rendering.
  - Trust by design: tamper-evident PDFs, audit trails, identity options.
  - Progressive complexity: start simple, layer advanced capabilities.
  - Interoperable: export, import, and integrate without lock‑in.

---

## 2) Personas & Jobs-To-Be-Done

- Solo Professional: needs quick extraction and occasional signing with clients; values simplicity and privacy.
- SMB Admin/HR/Legal: prepares and sends recurring agreements (offer letters, NDAs); needs templates, reminders, and audit trails.
- Enterprise Legal/Compliance: requires identity verification, PKI-based signatures, strict data governance, and delegated administration.
- Developers/Integrators: need APIs and webhooks to embed signing into workflows.

Jobs:
- Extract signature images from scans/photos and store them safely.
- Prepare documents with fields; place signatures precisely.
- Send for signature, track status, remind signers, and archive.
- Ensure documents are tamper-evident with a complete audit trail.
- Meet regulatory/contractual requirements (ESIGN/UETA, eIDAS levels).

---

## 3) Product Pillars

1) Best‑in‑class Signature Extraction
- Manual and assisted extraction (threshold, color controls, background removal).
- ML‑assisted detection options (local model, opt‑in cloud accel).
- Signature library with tagging and variants (black, blue ink, transparent).

2) Document Preparation & Templates
- PDF viewer, page thumbnails, zoom, rotate, crop.
- Drag‑and‑drop fields: signature, initials, text, date, checkbox.
- Templates with placeholders and roles; reusable across envelopes.

3) Signing Experience
- In‑app (desktop) signing, web signing, mobile‑responsive signing.
- Image‑based signature placement (with anti‑aliasing and color fidelity).
- Advanced: Digital signatures (PKI) with tamper seals and timestamps.

4) Workflow & Collaboration
- Envelopes with multiple recipients, routing order, reminders, expirations.
- Real‑time status, activity feed, and audit events.
- Bulk send, merging variables, and CSV uploads.

5) Trust, Security & Compliance
- Tamper‑evidence for PDFs; cryptographic seals where applicable.
- Identity options: email OTP, SMS OTP, ID verification (3rd‑party), SSO.
- SOC 2 roadmap; privacy posture; data retention and residency controls.

---

## 4) End‑to‑End Workflows

Simple Solo Sign (image‑based):
1. Import PDF → place own signature from library → flatten → export signed PDF.
2. Optionally email with signing certificate digest + app’s audit receipt.

Multi‑Signer Envelope (web or desktop to web):
1. Upload PDF(s) → add recipients (roles: signer, CC) → place fields by role.
2. Send → recipients get email link → guided signing flow → submit.
3. System applies tamper seal (PKI if available), archives document, emits audit log and webhooks.

In‑Person Signing (desktop or tablet):
1. Host prepares fields → signer signs on device → finalize and seal on completion.

Template‑Driven Sending:
1. Create template with roles/fields → team uses template, maps recipients, and sends in seconds.

---

## 5) Signature Models & Legal Considerations

- Image‑Based Signature (baseline):
  - Places raster signature image in the PDF content stream and flattens layers.
  - Legally acceptable in many ESIGN/UETA contexts when combined with intent, consent, and audit trail; not inherently cryptographic.

- Electronic Signatures (ESIGN/UETA‑compliant):
  - Requires explicit consent, clear attribution, intent to sign, and robust audit logging.
  - Email + IP + time + device + OTP provide reasonable signer attribution.

- Digital Signatures (PKI, eIDAS Advanced/Qualified path):
  - Create a CMS (PKCS#7) signature over the PDF byte range with a signer certificate; embed in PDF signature dictionary.
  - Add TSA timestamp, revocation info (OCSP/CRL), and LTV to support long‑term validation.
  - For enterprise: integrate with trusted CAs or qualified trust service providers (QTSPs) rather than becoming a CA initially.

---

## 6) Architecture Overview

Current stack: Desktop (PySide6) + FastAPI backend components. Target a hybrid model: privacy‑first desktop that can operate offline, plus cloud services for envelopes/signing.

High‑Level Components:
- Desktop App (PySide6): extraction, local library, basic signing, document prep.
- Web App (React/Vue/Svelte): recipient signing UX, sender dashboard, templates.
- API (FastAPI): users, orgs, documents, envelopes, recipients, fields, audit, webhooks.
- Worker (Celery/RQ/Arq): PDF rendering, flattening, PKI signing, email delivery, reminders.
- Storage: S3‑compatible (minio/local dev), encrypted at rest; optional local store for desktop‑only mode.
- Database: PostgreSQL (multi‑tenant isolation via org_id + RLS if desired).
- Key Management: Cloud KMS/HSM for service keys; per‑org signing keys where applicable.
- Observability: structured logs, traces; admin console.

API Surface (illustrative):
- POST /documents (upload PDF)
- POST /envelopes (create envelope)
- POST /envelopes/{id}/recipients (add signer/CC)
- POST /envelopes/{id}/fields (place fields per recipient)
- POST /envelopes/{id}/send
- GET  /envelopes/{id} (status)
- GET  /signing/{token} (recipient signing session)
- POST /signing/{token}/submit
- POST /webhooks (events: envelope.sent, viewed, signed, completed)
- Existing: POST /extraction/upload, POST /extraction/process_image

Data Model (core tables):
- users, organizations, memberships
- documents (id, org_id, storage_uri, hash, size)
- envelopes (id, org_id, status, expires_at, metadata)
- recipients (id, envelope_id, role, routing_order, email, auth_method)
- fields (id, envelope_id, recipient_id, page, x, y, w, h, type, required)
- signatures (id, user_id/org_id, image_uri, color, style, created_at)
- events_audit (id, actor, action, ip, user_agent, ts, envelope_id, doc_id)
- keys_certificates (id, org_id, type, kid, created_at, expires_at, metadata)

PDF Rendering & Signing:
- Image overlay: place signature raster with correct DPI, color, and transparency; embed as XObject; optionally flatten into content stream.
- PKI signing: compute ByteRange, digest, create CMS signature with signer cert chain; embed in PDF signature field; add DSS for LTV.
- Libraries: pikepdf, PyPDF2, borb, or a service in Go/Java for strong PDF signing support (build vs buy decision below).

Multi‑Tenancy & Isolation:
- Org‑scoped keys, storage prefixes, and row‑level security.
- Per‑tenant webhook signing secrets.

---

## 7) Security, Privacy, and Compliance

- Data Protection:
  - Encryption at rest (S3 SSE, DB TDE, desktop local vault) and in transit (TLS1.2+).
  - Optional customer‑managed keys (CMK) for enterprise.

- Access Control:
  - Role‑based permissions; org membership; IP allowlists (enterprise).
  - Scoped tokens for webhooks and recipient signing sessions.

- Audit & Integrity:
  - Immutable audit log with append‑only semantics; integrity checksums.
  - Tamper‑evident PDFs via PKI where enabled; hash receipts for image‑based mode.

- Identity & Attribution:
  - Email link with signed token; optional OTP via email/SMS; optional IDV vendor.
  - SSO/SAML/OIDC for enterprise senders and internal signers.

- Compliance Roadmap:
  - Phase 1: ESIGN/UETA best practices, DPA/ToS/Privacy Policy.
  - Phase 2: SOC 2 Type I → Type II; regional data residency.
  - Phase 3: eIDAS Advanced via trusted CA partnership; TSA timestamps.

---

## 8) Build vs Buy

- PDF Signing Engine: buy/partner (e.g., iText/Ascertia) for PKI robustness in early phases; build image overlay/flatten in‑house.
- Identity Verification: partner (Onfido, Persona) as optional add‑on.
- Email/SMS: buy (SES/SendGrid, Twilio) with provider abstraction.
- Storage: managed S3; minio for dev.
- KMS/HSM: cloud KMS initially; HSM for enterprise/regulated segments.

---

## 9) Pricing & Packaging (high‑level)

- Starter (Solo): local extraction + basic image‑based signing; pay‑once desktop, optional low‑cost cloud envelope add‑on.
- Pro (SMB): templates, multi‑recipient, reminders, audit logs, API + webhooks.
- Business: SSO, team workspaces, advanced audit, data retention, sandbox env.
- Enterprise: SAML/SCIM, dedicated tenancy, PKI signing, CMK/HSM, compliance add‑ons.

Reference: docs/PRICING.md, docs/PRICING_IMPLEMENTATION.md for details.

---

## 10) Risks & Mitigations

- Legal defensibility gap (image‑based only):
  - Mitigate with strong audit trails, signer attribution, and clear consent flows; sequence PKI support next.

- PDF signing complexity:
  - Mitigate via proven libraries/vendor early; isolate behind service boundary.

- Scope creep vs. velocity:
  - Strict phases; ship thin slices (MVP → GA) with measurable milestones.

- Security/compliance maturity:
  - Adopt security baseline now; plan SOC 2 program with staged controls.

---

## 11) 90‑Day Execution Plan (from current repo)

Phase 0: Harden Extractor (Weeks 1–3)
- Stabilize UI flows; rotate/crop; autosave; quick export presets.
- Complete local library persistence and tagging.
- Tests for image processing edge cases and regression.

Phase 1: Prep & Local Signing (Weeks 2–6, overlaps allowed)
- Desktop PDF viewer; field placement for self‑signing.
- Signature library picker with variants; precise placement; flatten to PDF.
- Export “Signed with Signature Extractor” receipt with digest and audit metadata.

---

## 12) Add‑Ons and Local Understanding (Text PDFs Only)

Position RAG as an optional add‑on to keep the core simple and private. Initial scope supports text‑based PDFs (no OCR).

Feature ideas aligned to vertical integration:
- Understand Sidebar (local): TL;DR, Q&A with page citations, basic key terms.
- Clause Library (local): save/compare common clauses; highlight deviations from playbooks.
- Auto‑Placement Helpers: detect signature/initial/date boxes heuristically; suggest placements.
- Field Mapping Templates: map roles to common documents (NDA, SOW) to place fields faster.
- Version Compare: per‑paragraph diff between two PDFs with side‑by‑side view.
- Redline as PDF: generate a simple visual diff layer and export.
- Stamps & Seals: date/time/company stamp builder; consistent look across documents.
- Batch Initials: auto‑place initials on each page edge per template.

Packaging:
- Add‑on for Lifetime; included in Pro. Clear copy: “Runs locally. Text PDFs only (for now).”

Guardrails:
- Disclaimers (“not legal advice”), citations by page, cancelable jobs; explicit unsupported notice for scans.

Phase 2: Cloud Envelopes (Weeks 5–10)
- Backend: envelopes, recipients, fields, send, status; email delivery; web signing UI.
- Webhooks and audit logs; dashboard to track envelopes.
- OTP option for signers; reminders and expirations.

Phase 3: Templates & Teams (Weeks 9–13)
- Template system with roles and placeholders; team workspaces.
- Bulk send and variables; CSV import.

Phase 4: PKI & Tamper Seals (Weeks 12–18)
- Introduce PKI signing service; TSA timestamps; LTV embedding.
- Admin UI for org certificates; policy controls.

Success Metrics per Phase
- Time‑to‑first‑signature, completion rate, support tickets, document validation pass rate, audit trail completeness, conversion from desktop‑only to envelope senders.

---

## 12) Technical Deep‑Dive: PDF Overlay & PKI

Image Overlay Algorithm (simplified):
1. Read PDF; select target page; compute pixel‑to‑point transform.
2. Insert signature as an XObject (PNG) with transparency; place via matrix.
3. Optionally flatten by writing into the page content stream; recompress.
4. Recalculate cross‑references; maintain original metadata; write output.

PKI Signing Steps (high‑level):
1. Prepare a hidden signature field and a visual appearance (optional).
2. Compute ByteRange; hash per PDF spec (usually SHA‑256).
3. Create CMS signature with signer certificate; include chain and revocation.
4. Add DSS (OCSP/CRL) and timestamp token (TSA) for LTV.
5. Validate with Acrobat/Preview; add negative tests; monitor real‑world opens.

---

## 13) Integration Strategy

- Bridge Period: export signed PDFs and push/pull to third‑party e‑sign tools via API while we roll out our envelope stack.
- Import: accept PDFs prepared elsewhere, allow countersign in our platform.
- Eventually: first‑class platform for sending/signing with optional bridges maintained for interoperability.

---

## 14) Linking to Existing Docs

- Roadmap: docs/ROADMAP.md
- Pricing: docs/PRICING.md, docs/PRICING_IMPLEMENTATION.md, docs/PRICING_TRIAL_VERSION.md
- Marketing: docs/MARKETING_PLAN.md
- Technical gaps: docs/TECHNICAL_GAPS.md
- Desktop spec: docs/desktop-frontend/pyqt-spec.md
- ML auto‑detection: docs/AUTO_DETECTION_ML.md

---

## 15) Next Actions

- Confirm Phase 1 scope: desktop PDF viewer + local self‑signing with audit receipt.
- Define API contracts for envelopes/recipients/fields; stub endpoints in FastAPI.
- Choose PDF library path for overlay now; shortlist PKI vendors/libraries.
- Add “Send Envelope” button flow in desktop to hand‑off to web for recipient signing.

This plan turns the current precision extraction advantage into a complete, trustworthy signature platform while preserving privacy‑first workflows and enabling enterprise‑grade capabilities when needed.

---

## 16) Out‑of‑the‑Box Ideas & Bets

- AI Field Autoplacement and Template Learning
  - Detect signature/date/initial lines and auto‑place fields using layout + text cues.
  - Learn from user corrections to improve per‑org templates automatically.

- Generative Signature Variants (Responsible Use)
  - From one sample, synthesize natural variants while preserving personal style.
  - Guardrails: watermarking and export controls to deter misuse; explicit consent.

- Steganographic Signature Watermarking
  - Embed a reversible, invisible watermark in signature images that binds to a document hash and recipient.
  - Detect copy‑paste misuse across documents; enable leak forensics.

- Public Proof Anchoring (Optional Transparency)
  - Anchor envelope/document hashes via OpenTimestamps or similar to create a public, time‑stamped proof without content disclosure.
  - Use only as an opt‑in transparency feature; consider jurisdictional guidance.

- Handwriting Biometrics (Stylus/Trackpad Capture)
  - Capture pressure/velocity curves for in‑person signing to increase evidentiary weight.
  - Store as encrypted, policy‑gated artifacts; never required for remote sign.

- Local‑First P2P In‑Person Signing
  - QR‑based pairing between host and signer device for air‑gapped, offline signing; sync results later.

- Contract Intelligence Guardrails
  - LLM‑assisted checks for missing initials, mismatched dates, unstated parties; suggest placements and blockers before send.

- Recipient‑Unique Watermarking & Leak Traps
  - Per‑recipient micro‑variations in visual appearance or metadata to trace leaks; configurable intensity.

- Email Ingestion and “Magic Send”
  - Forward an email with attachments to a unique address to auto‑create an envelope; map recipients from email headers.

- Browser Overlay for Any PDF
  - Extension overlays fields on web‑rendered PDFs (Gmail/Drive/SharePoint) and hands off to cloud envelope flow.

- Verifiable Credentials for Identity
  - Support DID/VC for signer attestations where ecosystems exist (enterprise pilots); fall back to OTP/SSO for mainstream.

- Privacy Vault with User‑Owned Keys
  - End‑to‑end encrypted cloud sync where only user devices hold data keys; org policies decide feature availability.

- Offline Envelopes with Deferred Send
  - Prepare and collect signatures offline at events; queue sends when back online, preserving audit continuity.

- Smart Redaction & Content Freeze
  - Auto‑redact PII before external sharing; content freeze that highlights any post‑signature byte changes.

- SDK/Embedded Mode and White‑Label
  - Lightweight JS and REST SDKs to embed signing in other products; white‑label skins and custom domains.

- Notary & RON Pathway
  - Partner integrations for Remote Online Notarization; schedule + KBA/IDV + recording storage policies.

- Green Mode
  - Optimize processing energy and choose low‑carbon regions for background jobs; expose sustainability reports to enterprise.

Pilot Picks (low effort, high differentiation)
- AI field autoplacement with learning loop in desktop and cloud prep.
- Recipient‑unique watermarks to deter leaks.
- Email ingestion → envelope creation for SMB speed.
