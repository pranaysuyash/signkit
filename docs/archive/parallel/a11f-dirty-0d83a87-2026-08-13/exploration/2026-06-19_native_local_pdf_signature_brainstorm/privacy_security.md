# Privacy, Security, and Compliance Brainstorm

Role: Privacy, security, and compliance reviewer

This note is a product brainstorm, not legal advice.

## Point Of View

A native PDF and signature app wins trust only if the trust story is visible in the product, not buried in policy text. For this category, "local-first" is not just a deployment choice. It is the product promise: documents should stay on the device by default, processing should be explainable, retention should be user-controlled, and the app should make it hard to accidentally leak sensitive content through logs, caches, exports, or unsafe sharing.

The bar is higher than "we do not upload files." Signature workflows sit next to identity, consent, approvals, and sometimes legally meaningful records. That means the app should separate visible signatures from cryptographic signatures, separate review from application, and separate candidate data from committed records. The safest product is one that can show where every document came from, what was done to it, when it was done, who approved it, and what evidence exists that sensitive content was actually removed when redaction is claimed.

## Top Risks / Threat Model Items

- Sensitive PDFs linger in temp files, thumbnails, caches, autosave state, crash dumps, or swap.
- A "local-only" claim becomes false if license checks, update checks, analytics, OCR, or model downloads quietly make network calls.
- Signature assets are copied, reused, or tampered with without provenance, making it unclear what is original, edited, or forged.
- Redaction is treated like a visual overlay instead of true content removal.
- Logs, error reports, and debug traces leak names, addresses, tax IDs, account numbers, or full document paths.
- Shared machines expose documents across users because session storage, libraries, or exports are not isolated.
- PDFs themselves are hostile inputs and can carry malformed objects, embedded files, scripts, huge images, or parser-triggering payloads.
- Users may apply the wrong signature to the wrong document, or sign after content changed, without a visible warning.
- A signature image may imply legal or identity assurance that the app cannot actually prove.
- Audit trails may exist but not be tamper-evident, which weakens chain-of-custody value.
- Retention may be too permissive, leaving old documents, OCR text, and derived previews around forever.

## Privacy-First Features The App Should Have

- Default to local-only processing with a clear "no network required" posture for core PDF and signature work.
- Show a visible processing mode badge for each document: local, offline, update-check only, or external service required.
- Keep a per-document sensitivity setting, such as personal, confidential, regulated, or legal hold.
- Store documents, previews, thumbnails, OCR text, and extracted signature assets in a clearly separated local vault.
- Offer one-click "forget this document" and "forget this session" actions that remove working copies, previews, and derived artifacts.
- Encrypt sensitive local storage at rest where feasible, especially the signature library and audit records.
- Make temp storage ephemeral and easy to audit, with a clear cleanup path after close, export, or session end.
- Keep OCR, layout analysis, and signature extraction on-device, with explicit opt-in for any model download or external compute.
- Provide a document lineage panel that shows input file hash, derived outputs, redactions, exports, and reuse events.
- Capture consent states for any action that materially changes a document, such as applying a signature, filling a field, or exporting a redacted copy.
- Add preview-before-commit behavior for destructive actions.
- Separate original source files from exported artifacts so users can compare them later.
- Support local-only retention policies, including auto-delete after N days, keep until manually deleted, or keep for legal hold.
- Allow users to choose whether OCR text is persisted, stored only in memory, or discarded after export.
- Make clipboard use explicit and optionally disable it for sensitive workflows.
- Provide a redaction workflow that preserves evidence of what was removed without preserving the removed content itself.

## Security / Compliance Guardrails That Matter

- No silent telemetry, analytics, or crash reporting that can leak document metadata.
- No network egress in the default path unless the user explicitly opts into updates, activation, or a remote service.
- Signed releases, dependency review, and vulnerability scanning for any library that parses PDFs or images.
- Strict input validation for PDFs, images, paths, and export destinations.
- Tamper-evident audit logs for document operations, exports, redactions, and signature application.
- Clear separation between:
  - visible signature images
  - cryptographic PDF signatures
  - approval metadata
  - redaction
  - annotation
- Explicit consent gates before:
  - sharing externally
  - exporting a signed copy
  - applying redaction
  - enabling OCR persistence
  - using any cloud-backed feature
- A compliance posture that says "supports controls" instead of "is compliant" unless a specific certification or review exists.
- Jurisdiction-aware messaging so the app does not imply universal legal validity for every signature workflow.
- Support for legal hold or retention freeze so users can prevent deletion when needed.
- A documented retention matrix for documents, previews, audit logs, and derived artifacts.
- A secure export manifest that records document hashes, timestamps, applied operations, and any local verification status.
- A distinction between "reviewed" and "verified" when the app cannot cryptographically prove identity or document integrity.
- Safe defaults for shared computers, including per-user app data isolation and explicit lock/logout behavior.
- A policy for embedded content and external links in PDFs, since those can break privacy or open attack paths.
- Administrative override controls for enterprise deployments, but only if they remain local/admin-managed rather than cloud-admin controlled by default.

## Things The App Should Avoid Claiming Or Doing

- Avoid saying "compliance-ready" as a blanket claim.
- Avoid saying "legally binding signature" unless a real certificate-backed signing flow exists and its limits are documented.
- Avoid saying "secure redaction" when the workflow only draws a black box.
- Avoid saying "zero data collection" if any license, update, or crash pathway still transmits anything.
- Avoid saying "fully private" if documents can leave the machine through optional services, sync, or network-based OCR.
- Avoid implying the app can verify identity, intent, or authorization on its own.
- Avoid marketing visible signature stamping as equivalent to cryptographic signing.
- Avoid promising that deletion is absolute in the presence of OS backups, swap, filesystem snapshots, or previously exported copies.
- Avoid storing sensitive content in plain text logs, UI histories, debug screenshots, or clipboard history.
- Avoid auto-sharing sample documents or debugging artifacts without explicit user approval.

## Open Questions / Unresolved Policy Issues

- Should the app support any networked feature at all, or only as an explicit opt-in enterprise add-on?
- Should the local signature vault be encrypted with an app-managed key, an OS keychain, or user-supplied passphrase protection?
- How much of the audit trail should be immutable versus user-deletable?
- Should OCR text be retained by default, or should persistence be opt-in per document?
- What is the default retention period for source files, exported PDFs, previews, and operational logs?
- Should redaction require a second confirmation step or reviewer approval before export?
- Do we need a "chain of custody" mode for regulated use cases, and if so what metadata is required?
- Should the app support digital signatures separately from image-based signatures in the main workflow?
- What is the minimum evidence needed before the UI can say a document was redacted, signed, or verified?
- How should the app behave on shared or managed devices where the host OS account is not private?
- Which compliance language is safe to expose in-product without a jurisdiction-specific legal review?

## Trust Features That Would Make The Product Safer And More Credible

- A document lineage panel with input hash, operations, exports, and retained artifacts.
- A visible "data flow" indicator that shows whether the document is staying local.
- A redaction verification report that proves removed text is not still extractable from the export.
- An export receipt that includes file hash, timestamp, applied actions, and processing mode.
- A per-document privacy dashboard showing retention state, OCR persistence, cache cleanup status, and signature provenance.
- A separate signature vault with provenance metadata, last-used history, and manual revoke/delete controls.
- A hard "pause before export" review screen for documents marked confidential or regulated.
- A one-click local cleanup action that clears working copies, previews, and derived text.
- A tamper-evident audit log viewer for user and admin review.
- A "what leaves the machine" settings page that is honest, specific, and short.
- Network activity indicators that make any non-local dependency obvious at the moment it happens.
- A provenance badge for each signature asset showing source, capture date, and whether it has been edited or reused.
- A document comparison view that shows original versus redacted or signed output before final export.

## Bottom Line

If privacy and trust are first-class goals, the app should behave like a controlled document workspace, not a file editor with a privacy disclaimer. The strongest product pattern is: local by default, explicit on every sensitive action, auditable after the fact, and conservative about legal claims. That combination is what will make the app credible for personal, professional, and regulated workflows.
