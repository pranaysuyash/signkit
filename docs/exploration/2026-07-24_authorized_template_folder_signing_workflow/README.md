# Authorized Template + Folder Signing Workflow

**Date:** 2026-07-24  
**Status:** Proposed; research and architecture exploration only  
**Decision gate:** Operator sign-off is required before implementation  
**Risk class:** High — signature reuse, authorization, sensitive documents, background processing, and file mutation  
**Evidence level in this document:** Tier 1 static inspection plus Tier 2 targeted tests; no runtime workflow or production-like proof

## Seed

Explore a local automation workflow where a user can:

1. choose one or more authorized signature assets;
2. upload or open representative documents;
3. define one or more signature spaces and assign each space to a signer role;
4. save that configuration as a reusable template/workflow;
5. designate an unsigned-document input folder and a signed-document output folder;
6. lock the workflow so only authorized users can activate or run it; and
7. safely apply the approved workflow to matching documents, with review, recovery, and audit evidence.

For the consolidated GTM/pricing/persona/flows/screens pack used for build planning, see:
[`gtm_full_build_pack_v2.md`](./gtm_full_build_pack_v2.md)

The product should remain local-first and should extend SignKit's canonical PDF signing path. It must not create a parallel signer, template store, audit path, or backend-only execution path.

## Addendum (2026-07-25)

- The shared workflow runtime + mac premium split is now partially implemented:
  - Profile wiring and mac-specific launch entrypoint are in place.
  - Workflow dashboard/grants/recipe console are gated behind profile/entitlement checks.
  - Folder triplet validation and role-field bindings exist in the recipe builder.
  - Onboarding now differentiates standard vs mac-premium profile behavior.
- Decision status: proceed from exploration to controlled implementation on the existing branch.
- Risk class remains high; production use needs workflow E2E and policy-hardening passes.

## Executive Verdict

**Prototype first, then proceed when the trust gates pass.**

The idea is strong because it completes SignKit's existing product thesis:

`extract -> recognize -> place -> review -> export -> reuse`

It also addresses the Executioner's strongest objection to SignKit: one-off signature work has weak frequency, while recurring Legal/HR/admin document packets can create a real habit and a defensible local-first workflow.

The unsafe version is a watcher that silently applies a PNG whenever a PDF arrives. The correct version is a **Controlled Signing Recipe**:

- a versioned workflow definition;
- signature assets referenced by secure vault identity, not a loose file path;
- deterministic document matching;
- explicit signer-role-to-field bindings;
- a bounded execution authorization;
- dry-run and review policies;
- an idempotent, recoverable job state machine;
- atomic output writing and post-write verification;
- an append-only, tamper-evident execution record.

Automatic execution is permitted only inside an explicit grant. Ambiguous documents, stale templates, revoked signatures, changed inputs, expired grants, failed output verification, and unsupported PDFs fail closed into a review lane.

## Terminology Decision

Use these terms consistently:

- **Placement template:** reusable geometry/anchor information for one or more fields.
- **Controlled Signing Recipe:** the full executable workflow: matcher, fields, signature bindings, folders, review policy, output policy, and authorization policy.
- **Signature asset:** a stored visual signature/initial asset with provenance and authorization metadata.
- **Workflow activation:** the explicit act that makes an approved recipe runnable.
- **Execution grant:** a bounded authorization that permits a principal to execute one recipe.
- **Job:** one input document processed against one immutable workflow version.
- **Visual signature application:** placing a signature image into a PDF.
- **Electronic-signature ceremony:** a process that also captures signatory intent, consent, attribution, and retainable records.
- **Digital signature:** certificate-backed cryptographic PDF signing, such as PAdES.

Do not call visual signature application a digital signature. Do not claim that it verifies identity, intent, authority, authenticity, or universal legal validity.

## Current Product Ground Truth

### Implemented and reusable

| Capability | Current evidence | Assessment |
|---|---|---|
| Local PDF signing | `desktop_app/pdf/signer.py` and end-to-end signing tests | Canonical write path to extend |
| Field-aware placement | `desktop_app/pdf/field_detection.py`, viewer field candidates, and anchored replay | Strong basis for field bindings |
| Reusable placement templates | `desktop_app/pdf/template_store.py` | Implemented, but currently one signature placement per template |
| Multi-page bulk placement | `desktop_app/views/bulk_sign_dialog.py` and `desktop_app/views/main_window_parts/pdf.py` | Reusable UI and placement behavior |
| Durable per-document placements | `desktop_app/pdf/document_session_store.py` | Useful for preview/recovery; not a workflow/job store |
| Local audit runs/events | `desktop_app/pdf/db_audit.py` | Useful substrate; not tamper-evident and not a full job ledger |
| Encrypted signature blobs | `desktop_app/processing/vault.py` | Useful substrate; key custody and metadata need hardening |
| Optional backend authentication | `backend/app/routers/auth.py` and desktop API session | Exists, but is not the current local execution boundary |

### Missing or insufficient for this feature

| Gap | Current evidence | Required direction |
|---|---|---|
| Multi-field, multi-signer workflow definition | Template record contains one `signature_path` and one placement | Versioned recipe containing an ordered collection of field bindings |
| Secure asset binding | Templates store raw signature file paths | Bind to vault asset ID plus owner/delegation and revocation state |
| Enforced local authorization | `desktop_app/main.py` skips login by default | Deny-by-default local execution authorization independent of licensing |
| Folder lifecycle | No watcher/queue implementation found | Event-triggered plus reconciliation-based local job intake |
| Idempotency and recovery | No document-level workflow job state machine | Durable job ledger with unique input/workflow keys and explicit states |
| Atomic verified output | `sign_pdf()` writes directly, returns boolean, and prints errors | Structured errors, temporary output, validation, atomic promotion |
| Template approval/versioning | Mutable JSON templates | Immutable approved versions; edits create a new draft |
| Standing authorization | No bounded unattended execution grant | Expiring, revocable, scope-bound grant with maximum-use policy |
| Strong vault key custody | Vault key is stored beside encrypted blobs | OS keychain-wrapped data-encryption key and migration path |
| Privacy-aware audit | Paths/email/error text are stored in plaintext | Data minimization, redaction, retention, and controlled export |

Targeted verification on 2026-07-24:

```text
.venv/bin/python -m pytest \
  desktop_app/tests/test_pdf_template_store.py \
  desktop_app/tests/test_db_audit.py \
  tests/test_integration_workflows.py -q

Result: 19 passed, 8 warnings.
```

The warnings are `datetime.utcnow()` deprecations in `template_store.py`. They do not invalidate the targeted tests, but they are inside the future schema-migration blast radius and must be fixed when the workflow work begins.

## Product Thesis

The differentiator is not "bulk stamp a PDF." It is:

> SignKit safely replays a previously reviewed document-completion decision on recurring local documents, while keeping authorization, exceptions, and proof visible.

This is a better fit than becoming a generic DocuSign alternative:

- SignKit already owns local signature extraction, placement, templates, PDF export, and audit state.
- The recurring input/output folder turns episodic work into an operational loop.
- A local workflow can serve sensitive Legal/HR/admin documents without requiring document upload.
- Review and recovery can be stronger than opaque "automation succeeded" behavior.

## Actor and Authority Model

The recipe must distinguish these identities:

- **Asset owner:** person whose signature/initial asset is stored.
- **Recipe owner:** person allowed to create new recipe versions and approve them.
- **Approver:** person allowed to activate a recipe or approve a bounded unattended grant.
- **Runner:** person allowed to execute an activated recipe.
- **Auditor:** person allowed to inspect/export execution evidence but not sign.

A person may hold more than one role in personal mode. The model must still preserve the distinctions so team-managed mode does not require a rewrite.

### Non-negotiable authority rule

A stored signature asset must not be usable merely because it exists on disk. Every asset binding needs one of:

- self-owned use;
- recorded delegation by the asset owner;
- organization policy authorizing the use; or
- explicit per-run approval.

Revoking an asset or delegation blocks all future jobs immediately. It does not alter previously exported documents or erase their audit history.

## Authorization Modes

### 1. Confirm every job — default

- Runner authenticates.
- App shows the exact document, workflow version, signature assets, fields, and output name.
- Runner explicitly confirms intent to execute.
- Grant is one job only.

### 2. Unlocked session

- Approver authenticates once.
- Grant is bound to one recipe version and one input/output folder pair.
- Grant expires after a short idle period or when the app locks.
- Each job remains visible and cancelable.

### 3. Bounded unattended grant

This is the only mode that allows folder arrivals to complete without a per-document click.

The grant must bind:

- approved recipe version hash;
- allowed signature asset IDs;
- asset-owner/delegation records;
- exact input and output directories;
- allowed document matcher;
- maximum jobs and/or expiry;
- review threshold and hard-stop classes;
- allowed operating-system account/device;
- output naming and overwrite policy;
- approver identity and reauthentication event.

The grant automatically locks on app restart unless the approved policy explicitly permits background continuation. The first implementation should require the app to be open and the workflow visibly active. An operating-system service is a separate future decision.

### Authentication substrate

Local workflow authorization must not depend solely on the optional backend JWT because the core workflow is offline-first and desktop login is currently skipped.

Recommended provider boundary:

- macOS: Keychain-backed secret/key storage and OS user-presence authentication where available;
- Windows: Credential Locker/Windows Hello equivalent;
- Linux: Secret Service/KWallet with an explicit unsupported/fail-closed state when no secure backend exists;
- optional managed-team provider later.

Python `keyring` is a possible portability adapter, but its backend must be diagnosed and allowlisted. A null or degenerate backend must fail closed; no plaintext fallback is allowed.

Licensing is not authentication. A valid license must never authorize signature use.

## Controlled Signing Recipe

```text
ControlledSigningRecipe
  recipe_id
  version
  status: draft | approved | active | suspended | revoked
  name
  document_matcher
  field_bindings[]
  input_folder
  output_folder
  review_folder
  source_retention_policy
  output_policy
  review_policy
  authorization_policy
  created_by
  approved_by
  created_at
  approved_at
  content_hash
```

Each `field_binding` includes:

```text
field_id
field_kind: signature | initials | date | text
signer_role
signature_asset_id
page_selector
anchor_type
anchor_definition
relative_geometry
required
expected_count
manual_fallback_allowed
```

### Important design choice

The recipe stores vault asset references, not exported PNG paths. At execution time, the authorized engine obtains a short-lived working copy in a protected temporary location, signs the PDF, verifies the output, and removes the working copy.

### Versioning rule

An approved recipe version is immutable. Changing a field, signature asset, matcher, folder, naming rule, or authorization policy creates a new draft version. The old version remains inspectable for historical jobs but cannot be silently mutated.

## Document Matching

Document matching is the principal safety boundary.

### Match class A — exact template

Use the source PDF hash or a normalized deterministic fingerprint. This is the only class initially eligible for unattended execution.

### Match class B — deterministic document family

Match on a documented combination of:

- page count and page dimensions;
- normalized text anchors;
- native field names/types where present;
- stable relative geometry;
- document-family identifier;
- absence of unexpected pages/fields.

This may become unattended only after a representative corpus passes and the matcher has hard negative tests.

### Match class C — inferred/scan/OCR family

OCR, heuristic similarity, or model confidence is a proposal, not authority. These jobs require review until corpus evidence supports a narrower deterministic rule. A confidence score alone must never authorize unattended signing.

### Staleness and drift

A recipe becomes `needs_revalidation` when:

- expected anchors disappear or multiply;
- page count/dimensions leave the approved envelope;
- field count changes;
- input PDF is modified after preflight;
- signature asset/delegation changes;
- signer-role mapping changes;
- output verifier detects a mismatch;
- a hard-negative regression is discovered.

## Folder Lifecycle

User-visible configuration:

- **Unsigned input folder:** where matching PDFs are placed.
- **Signed output folder:** where verified completed PDFs are published.
- **Needs review folder:** optional user-visible exception destination.
- **Source archive policy:** keep in place by default; optional move after verified completion.

Input and output must be distinct and must not be nested inside one another. Symlink resolution must be checked before activation so an output cannot loop back into input.

The app also owns internal staging state; it should not require users to manually manage a "processing" folder.

### Job state machine

```text
discovered
  -> stabilizing
  -> validated
  -> fingerprinted
  -> matched
  -> awaiting_authorization | awaiting_review
  -> queued
  -> processing
  -> verifying
  -> completed

Any state may move to:
  -> retryable_failure
  -> needs_review
  -> quarantined
  -> canceled
```

Every transition records actor, timestamp, reason code, input hash, recipe version, and prior state.

### Intake behavior

1. `QFileSystemWatcher` triggers a rescan; it is not treated as a complete event ledger.
2. A periodic reconciliation scan catches coalesced or missed directory events.
3. A file is not eligible until size and modification time are stable across checks and the PDF parser can open it.
4. The engine canonicalizes the path, rejects symlinks escaping the approved input root, and rejects unsupported extensions.
5. The engine hashes the input and creates or resumes a durable job.
6. Duplicate events resolve to the existing job rather than creating duplicate signatures.

### Output behavior

- Never overwrite the source.
- Default output: `{stem}__signed__{recipe_slug}__{short_job_id}.pdf`.
- Render to a temporary file in the output directory.
- Reopen and validate the PDF.
- Verify page count, expected placements, output hash, and absence of a partial file.
- Atomically promote the temporary file to the final name.
- On collision, compare the existing job/output identity; never silently overwrite.
- Only after successful promotion may the optional source-archive action occur.

Qt's `QSaveFile` and `QLockFile` are suitable existing-stack primitives for atomic publication and cross-process workflow locking. The signer itself should expose structured failures rather than returning a bare boolean and printing an error.

## Canonical Architecture

The manual UI and the folder monitor must call the same workflow engine.

```text
Workflow UI / Folder Monitor
            |
            v
  Controlled Workflow Engine
    |       |       |       |
    v       v       v       v
 Matcher  Authorizer  Job Store  Audit/Receipt
    |          |         |
    +----------+---------+
               |
               v
       Canonical PDF Pipeline
 field detection -> placement proposal -> signer -> verifier
               |
               v
       Atomic signed output
```

Recommended module ownership:

- extend/migrate `desktop_app/pdf/template_store.py` into the recipe schema rather than adding a second template truth;
- reuse `desktop_app/pdf/field_detection.py`;
- reuse and harden `desktop_app/pdf/signer.py`;
- reuse `desktop_app/pdf/db_audit.py` as the migration substrate for job/event/receipt tables;
- reuse `desktop_app/processing/vault.py`, with OS-backed key custody;
- add one workflow orchestration package under `desktop_app/workflows/`;
- add one Workflows surface in the desktop UI;
- keep the backend optional and out of the local execution critical path.

The orchestration package should contain cohesive boundaries, not route-style duplication:

```text
desktop_app/workflows/
  models.py
  store.py
  engine.py
  matcher.py
  authorization.py
  folder_monitor.py
  verifier.py
  receipts.py
```

## Audit, Receipts, and Privacy

The current SQLite audit logger is a useful beginning, not proof of immutability.

Each job should preserve:

- recipe ID, version, and content hash;
- input hash and a privacy-minimized display name;
- output hash and path reference;
- signer roles and signature asset IDs, not raw signature pixels;
- authority/grant ID and approving principal;
- match class and evidence;
- proposed and final field bindings;
- overrides and review decisions;
- start/end timestamps;
- retry, failure, cancellation, and recovery events;
- verifier results;
- product/app version and PDF backend used.

For tamper evidence, chain events with an HMAC using an OS-protected audit key. Describe this accurately as tamper-evident local evidence, not independent notarization.

Data policy:

- default logs must not store document contents, OCR text, signature pixels, passwords, access tokens, or raw exception dumps;
- full file paths and emails should be minimized or pseudonymized in normal audit views;
- retention must be configurable by data class;
- deleting a signature asset must not destroy the historical fact that an asset ID was used;
- export receipts should be explicit user actions;
- source documents remain under user control and are not moved by default.

## Electronic-Signature and Digital-Signature Boundary

Under the U.S. ESIGN definition, an electronic signature includes an electronic symbol or process attached to or associated with a record and adopted by a person with intent to sign. Record retention and consumer-consent requirements may also apply. In the EU, eIDAS distinguishes simple, advanced, and qualified electronic signatures; advanced and qualified levels add identity/control/integrity requirements, and qualified signatures rely on qualified certificates/devices.

Therefore:

- Visual image placement can support a user's signing workflow.
- An automated standing grant may evidence operator authorization to apply an asset.
- It does not, by itself, prove the asset owner's identity, consent, authority, or legal intent for every document.
- A legally meaningful remote-signing ceremony needs a separate, jurisdiction-reviewed flow.
- Certificate-backed PDF digital signatures are a separate future capability following PAdES-compatible standards.

Product copy should say **"apply an authorized visual signature"** or **"complete an approved local signing recipe"**, not **"legally sign automatically"**.

## Failure Policy

Hard-stop and send to review:

- no active authorization grant;
- expired/revoked asset or delegation;
- input/output folder mismatch;
- input changed after validation;
- no match or multiple recipe matches;
- missing/duplicate required field;
- password-protected or corrupted PDF;
- unexpected page/field structure;
- output already exists with unrelated identity;
- output verification mismatch;
- audit/job store unavailable;
- secure key store unavailable;
- insufficient disk space or permission failure;
- a second process owns the recipe lock.

Retry automatically only for explicitly classified transient failures, with bounded attempts and visible backoff. Parser errors, authorization errors, matcher ambiguity, and verification errors are not transient.

## User Experience

### Recipe Builder

1. Choose representative PDF(s).
2. Add signer roles.
3. Select authorized signature/initial assets from the vault.
4. Tag all required signature spaces and optional date/text fields.
5. Choose exact-template or document-family matching.
6. Select input, output, and optional review folders.
7. Choose review mode.
8. Run a dry test on positive and negative examples.
9. Review privacy/retention and output naming.
10. Approve and activate the immutable recipe version.

### Workflow Console

Show:

- locked/active status;
- authorization/grant expiry and remaining use count;
- watched folders;
- queued, reviewing, completed, failed, and quarantined counts;
- current job with matched recipe and signatures;
- pause/lock/emergency-stop actions;
- exact failure reasons and recovery actions;
- last verified output and receipt.

### Dry run

Dry run is mandatory before first activation and after any version change. It produces placements, warnings, and expected output names without writing signed outputs.

## Options Considered

### A. Extend existing local pipeline — recommended

Pros:

- preserves local-first product truth;
- reuses current signer, detector, templates, vault, Qt UI, and audit substrate;
- avoids document upload and cloud dependency;
- keeps one canonical signing pipeline.

Cons:

- requires a real local authorization design;
- OS credential behavior varies by platform;
- team authorization is limited until a managed provider exists.

### B. Use current backend login as the lock — rejected as sole boundary

Pros:

- user/password/JWT code already exists.

Cons:

- desktop login is skipped;
- core PDF work is local and offline;
- JWT availability must not decide whether a local signature asset is usable;
- it does not provide secure vault key custody or OS user presence.

The backend may become one authorization provider later, not the canonical local control.

### C. Build cloud e-sign workflow — rejected for this decision

Pros:

- easier centralized identity, invitations, routing, and team policy.

Cons:

- conflicts with the current local-first wedge;
- expands legal, privacy, security, availability, and operational scope;
- duplicates established cloud e-sign products;
- would not reuse the product's strongest differentiation.

### D. Simple watch folder with a chosen PNG — rejected

It is easy to build and unsafe to ship. It has no robust authority, matching, idempotency, recovery, or evidence contract.

## Build Plan in Gated Commit Units

No implementation begins until the proposed decision is accepted.

### Decision 1 — trust class and authority

Approve:

- visual signature application as the initial trust class;
- actor/role model;
- authority/delegation record;
- three authorization modes;
- product-language boundary.

Closure evidence: accepted ADR with Update log and legal/business review owner.

### Commit 1 — versioned workflow and job schema

- Migrate placement templates to multi-field recipes without a second truth source.
- Add immutable versioning, status, matcher, folder, policy, asset-reference, grant, job, event, and receipt models.
- Add schema migration and legacy-template importer.
- Replace naive JSON writes with atomic storage behavior.

Gate: migration round-trip, downgrade/rollback plan, legacy fixtures, invalid/corrupt state tests.

### Commit 2 — vault and authorization boundary

- Introduce signature asset ownership/delegation/revocation metadata.
- Move new recipes from raw paths to vault IDs.
- Add OS-backed key custody provider interface.
- Add deny-by-default authorization policy and bounded grants.
- Keep licensing separate.

Gate: unauthorized, expired, revoked, wrong-user, wrong-folder, wrong-recipe, key-store-unavailable, and restart-lock tests.

### Commit 3 — pure controlled workflow engine

- Create the single orchestration state machine.
- Connect matcher, field proposal, canonical signer, verifier, audit events, and recovery.
- Refactor `sign_pdf()` to structured errors and safe close behavior.
- Add input/output identity and idempotency keys.

Gate: targeted integration tests for success, duplicate, retry, partial failure, cancellation, stale input, signature revocation, and verification failure.

### Commit 4 — atomic output and job receipts

- Add temporary output, reopen validation, atomic promotion, collision handling, and output hash.
- Add tamper-evident event chaining and export receipts.
- Add retention and minimized audit data.

Gate: crash-before-commit, full disk, permission error, existing-output collision, corrupted output, and audit-unavailable tests.

### Commit 5 — Recipe Builder and manual execution

- Add multi-signer/field authoring.
- Add dry run, preflight, review, activate, suspend, revoke, and run controls.
- Add template drift warnings and version comparison.

Gate: offscreen UI tests, keyboard/accessibility checks, real local PDF manual workflow, and screenshot review.

### Commit 6 — folder monitor and Workflow Console

- Use `QFileSystemWatcher` as a wake-up signal plus periodic reconciliation.
- Add stabilizing, queue, pause, lock, retry, quarantine/review, and archive behavior.
- Add `QLockFile`-backed single-runner protection.
- Require app-open activation for the first release.

Gate: duplicate/coalesced events, partial copies, rename/move, app restart, two app instances, nested-folder rejection, symlink escape, huge batch, and cancellation tests.

### Commit 7 — representative-corpus and end-to-end proof

- Build approved positive, negative, drifted, scanned, corrupted, protected, rotated, and mixed-page fixtures.
- Prove exact-template automation.
- Keep document-family and OCR matches review-only until their own evidence gates pass.
- Update user guide, threat model, privacy/data retention, operator runbook, and launch-claim registry.

Gate: Tier 3 end-to-end flow plus Tier 4 observed desktop behavior. Production or regulated-use claims remain blocked without the applicable legal/security review.

## Verification Matrix

### Correctness

- multiple signature assets and signer roles;
- multiple fields per signer;
- same signature in multiple fields;
- date/text fields;
- mixed page sizes and rotations;
- native AcroForm and visual fields;
- exact template and deterministic family matching;
- stable output coordinates;
- output reopens in multiple PDF readers.

### Authorization and abuse

- unauthenticated run;
- authenticated but unauthorized runner;
- revoked asset/delegation;
- expired/maxed grant;
- swapped input folder;
- replaced signature blob;
- edited approved recipe;
- replayed job;
- stolen/copy-restored app data;
- secure key store unavailable;
- malicious paths, symlinks, and filenames.

### Folder and concurrency

- partially copied file;
- duplicate watcher events;
- missed watcher event recovered by reconciliation;
- same file renamed;
- duplicate content under a different filename;
- app crash during processing;
- two app instances;
- output collision;
- output nested under input;
- source removed mid-run;
- removable/network volume disconnect.

### Privacy and operations

- logs contain no signature pixels, tokens, passwords, or document text;
- sensitive paths are minimized;
- retention/deletion behavior is documented and tested;
- every failure has an operator-visible reason and next action;
- pause and emergency lock take effect before the next signature operation;
- the app can explain what happened after restart.

## Product Horizons

### Near product shape

- multi-field recipes;
- exact-template matching;
- manual confirmation;
- input/output folder queue;
- secure local asset reference;
- job ledger and atomic verified output.

### Compounding shape

- deterministic document families;
- remembered reviewed corrections;
- organization-approved recipe library;
- bounded unattended grants;
- policy-controlled retention and audit exports.

### Mature shape

- cross-device/team policy provider without document upload;
- portable signed recipe bundles;
- optional certificate-backed PAdES digital signing;
- independent timestamp/evidence service as an explicit opt-in;
- rule-based routing to downstream local folders or approved integrations.

### Leapfrog concept — Proof-Carrying Recipe

The strongest future concept is not "AI signs documents." It is a recipe that carries its own authority, matcher, field bindings, version, tests, output verifier, and receipt policy. The automation becomes trustworthy because the decision is replayable and inspectable, not because a model is confident.

## Champion vs. Executioner

### Champion's strongest case

- Recurring document packets fix the weak-frequency problem of one-off signature extraction.
- Existing local PDF, template, field, vault, and audit work makes this an extension, not a new product.
- Folder routing turns SignKit into a production instrument.
- Local-first is valuable for sensitive Legal/HR/admin documents.
- The moat becomes reliable replay of document intent, not signature pixels.

### Executioner's strongest kill case

- Silent signature reuse creates forgery, authority, and legal-risk concerns.
- Established e-sign vendors already own identity, consent, routing, and compliance.
- A weak watcher would turn SignKit from a useful tool into a liability.
- Team authorization and secure key custody are materially harder than adding a folder picker.

### Arbitration

Proceed if:

- the product stays local-first;
- the initial trust class is honest visual signature application;
- the first unattended matcher is exact/deterministic;
- authorization is deny-by-default and bounded;
- ambiguous jobs fail to review;
- the recipe/job/audit system is canonical and recoverable.

Pause if:

- the desired product claim is "legally binding automated signature" without a real consent/identity/digital-signature design;
- third-party signature assets can be used without recorded authority;
- OS-backed secret storage cannot be made fail closed;
- the workflow must run as a headless service in the first implementation.

Kill the direction if research with target Legal/HR/admin operators shows that recurring local packets are rare, operators cannot obtain durable signature-use authorization, or required trust depends on cloud identity/certificate services that erase the local-first advantage.

## Six-Hat Coverage

- **White / facts:** current template, field, signing, vault, session, and audit capabilities were inspected; targeted tests passed; authorization and folder execution are missing.
- **Yellow / value:** repeat workflows increase frequency, retention, and operator leverage while reinforcing local privacy.
- **Black / risk:** unauthorized signature reuse, template drift, duplicate processing, partial files, weak key custody, and overclaiming legal validity are critical.
- **Green / alternatives:** exact-template grants, proof-carrying recipes, event-plus-reconciliation intake, vault IDs, dry run, and review quarantine.
- **Red / experience:** the user should feel that automation is fast but visibly under their control; lock state and exception state must be unmistakable.
- **Blue / next action:** approve or revise Decision 1, then implement in dependency order with a gate after every commit.

## Research Anchors

- U.S. ESIGN Act, general validity and consumer consent/record provisions: <https://www.govinfo.gov/app/details/PLAW-106publ229>
- U.S. electronic-signature definition, including intent: <https://www.law.cornell.edu/uscode/text/15/7006>
- European Commission eSignature/eIDAS overview: <https://eidas.ec.europa.eu/>
- European Commission eSignature levels FAQ: <https://ec.europa.eu/digital-building-blocks/sites/spaces/DIGITAL/pages/880312429/eSignature%2BFAQ>
- ETSI PAdES baseline signatures: <https://www.etsi.org/deliver/etsi_EN/319100_319199/31914201/01.02.01_60/en_31914201v010201p.pdf>
- NIST SP 800-63-4 digital identity guidelines: <https://www.nist.gov/publications/nist-sp-800-63-4-digital-identity-guidelines>
- OWASP authorization guidance: <https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html>
- Apple Keychain guidance: <https://developer.apple.com/documentation/security/using-the-keychain-to-manage-user-secrets>
- Qt `QFileSystemWatcher`: <https://doc.qt.io/qtforpython-6.10/PySide6/QtCore/QFileSystemWatcher.html>
- Qt `QSaveFile`: <https://doc.qt.io/qtforpython-6.10/PySide6/QtCore/QSaveFile.html>
- Qt `QLockFile`: <https://doc.qt.io/qtforpython-6/PySide6/QtCore/QLockFile.html>
- Adobe template permissions and reusable field layers: <https://helpx.adobe.com/sign/using/document-templates.html>
- Adobe bulk signing pattern and independent audit records: <https://helpx.adobe.com/acrobat/desktop/e-sign-documents/request-e-signatures/request-in-bulk.html>

These sources inform product and architecture decisions; they do not constitute legal advice or a compliance certification.

## Three-Pass Review Record

### Pass 1 — immediate correctness and completeness

Checked the user's full request: multiple signatures, document upload, signature spaces, reusable templates, authorized execution, unsigned input folder, signed output folder, and plan/research-before-build. Added explicit actor, authority, folder, failure, and output behavior. No application code was built.

### Pass 2 — architecture and long-term viability

Checked canonical ownership and avoided a second signing/template/audit path. Reframed the feature as an extension of the existing PDF pipeline. Added immutable recipe versions, vault references, a job state machine, event-plus-reconciliation intake, atomic verified outputs, and an app-open first release boundary.

### Pass 3 — rule compliance and supervision readiness

Checked high-risk evidence boundaries, authorization abuse cases, privacy, operator recovery, legal-language limits, commit-unit sequencing, acceptance gates, and explicit proceed/pause/kill conditions. Kept all implementation dependent on operator approval of the trust-class decision.

## Anything Else?

Yes:

1. The current vault encryption key is stored beside the encrypted blobs, so copying that folder may copy both ciphertext and key. OS-backed key custody is a prerequisite, not optional hardening.
2. The current placement template stores a raw signature path. That must become a vault asset reference before automated execution.
3. The current desktop app skips login. The existing backend login and license checks cannot be presented as the workflow lock.
4. The current audit tables are editable local SQLite records. Tamper-evident chaining is needed before describing the receipt as integrity evidence.
5. `sign_pdf()` currently converts failures to a boolean and console message. Automation needs structured failure codes and atomic output semantics.
6. The first version should run only while SignKit is open and visibly active. A headless OS service would require a separate threat model, secret-access policy, installer/service lifecycle, and approval.
7. Input originals should remain untouched by default. Moving them after success should be an explicit recipe policy.

## Operator Decision Needed

Approve, revise, or reject these load-bearing decisions before implementation:

1. Initial trust class is authorized visual signature application, not a legal/digital-signature guarantee.
2. Exact-template matching is the first unattended mode; document-family/OCR matching remains review-first.
3. Input originals remain in place by default; signed files go to the designated output folder.
4. First implementation requires SignKit to be open and the workflow visibly active.
5. Bounded unattended execution requires an OS-backed authorization grant and recorded signature-asset authority.

## User Personas, Use Cases, and Flows

### Primary personas

- **Legal Operations Lead**
- Goal: run recurring legal packet completion safely.
- Pain: manual signatures and uncertain traceability on repetitive contracts.
- Value: versioned recipes, immutable recipe history, and explicit approvals.

- **HR Operations Coordinator**
- Goal: process onboarding and policy packets at volume.
- Pain: repeated page variations with multiple signature roles.
- Value: role-tagged binding, dry runs, and clear recovery states.

- **Finance/Procurement AP Analyst**
- Goal: speed approvals without violating internal control.
- Pain: mixed queue states and unclear who approved what.
- Value: grant lifecycle, auditable receipts, and one-click pause/retry.

- **Compliance Lead**
- Goal: avoid silent automation and overclaiming signatures.
- Pain: pressure to “automate and forget.”
- Value: forced review gates, legal boundary in copy, and incident response flow.

### Use-case matrix

- recurring contract packets: legal and procurement review, same document family weekly
- onboarding kits: employee + manager + witness fields across multiple pages
- compliance attestations: date field + signature + initials with strict output naming
- high-volume exception mode: manual review for near-miss documents only
- post-launch scaling: move from manual confirm to bounded unattended grants

### User journey by use case

1. Create template from a canonical source.
2. Tag all signature spaces and bind each to signer role and vault asset.
3. Add optional text/date placeholders and page selectors.
4. Configure exact-match mode and designate folders.
5. Run dry run and review mismatches.
6. Activate and monitor jobs in queue/review/completed states.
7. Export receipts and tune policy if needed.

### Current vs target diff (behavioral)

- Before: one-time manual placement and direct output naming.
- After: reusable recipe versions with explicit policy and output destination mapping.

- Before: no folder automation.
- After: designated unsigned and signed folders with reconciliation-based intake.

- Before: optional or skipped auth boundary.
- After: deny-by-default grant and delegation-aware execution.

- Before: weak visibility into failures.
- After: structured failure taxonomy and resumable recovery.

- Before: no operational recipe context in logs.
- After: recipe version, matcher class, grant ID, and hash lineage in receipts.

## GTM and distribution ideas

### Positioning

`Local-first, repeatable signature completion for sensitive teams.`

### Market wedge

- Legal, HR, AP, and admin teams with recurring document families.
- Operations teams that need speed but cannot send docs to cloud signing platforms.
- Firms with compliance sensitivity but no immediate digital-sign certificate integration.

### GTM sequence

1. Invite 2-3 target teams for private beta.
2. Capture baseline metrics from their current manual process.
3. Launch recipes for exact-match-only mode first.
4. Publish benchmark outcomes (time saved, queue reliability, false-positive rate).
5. Expand to family matching only after review evidence.

### Differentiation narrative

- Not generic template saving.
- Not full legal signature replacement.
- Recipe-first automation with explicit human control and recoverable outcomes.

### Similar idea patterns to borrow (without copying risks)

- **Template-first automation with guardrails**: apply recurring document recipes with strict versioning and review gates.
- **Workflow approval lanes**: explicit draft/approval/active/revoke states before execution.
- **Queue-native productivity**: show jobs in states and require operator intent at trust boundary edges.
- **Operator receipts**: exportable evidence bundle with minimal claims and traceable hashes.

### Competitive positioning matrix

| Capability | This concept | Generic automation tool | Cloud e-sign vendor |
|---|---|---|---|
| Keeps docs local by default | Yes | Usually no | Usually no |
| Reusable multi-role recipes | Yes | Limited | Yes |
| Folder-native unattended execution | Controlled and review-gated | Usually limited | Usually external workflow dependent |
| Authorization as app-native policy | Yes | Varies | Identity-first but often cloud-only |
| Built-in visual placement replay | Yes | Depends on template tooling | Vendor-specific |
| Tamper-evident local receipts | Planned | Often partial | Varies |

### Channel and launch experiments

- Landing page test: “from manual queue to controlled automation” with a short onboarding checklist.
- Use-case campaigns: legal packet, HR onboarding, procurement approval.
- Pilot script: one team, one recipe class (exact match), 2-week hardening window.
- Event: release notes plus incident-response demo to show recoverability.

### Channel ideas

- Founder-led outreach to legal and HR operations managers.
- Webinar: “How recurring signatures break your team’s control model.”
- Template marketplace for anonymized internal families (optional v2).
- Partner-led onboarding for legal process auditors.

## Pricing model refresh

### Design principle

Price by operational control and governance complexity, not raw signature count only.

### Tier 1 — Starter
- 1 operator seat
- 1 active recipe
- 300 signed outputs / month
- Manual confirm only
- Folder workflow and receipt export
- Suggested price: $19/month

### Tier 2 — Team
- 5 operator seats
- 10 active recipes
- 2,000 signed outputs / month
- Bounded unattended grants
- Full audit dashboard and pause/retry controls
- Suggested price: $59/month

### Tier 3 — Business
- 20 operator seats
- 40 active recipes
- 10,000 signed outputs / month
- Multiple folders, role segmentation, and retention policies
- Suggested price: $159/month

### Tier 4 — Enterprise
- seat and folder count negotiable
- dedicated onboarding and policy templates
- controlled integrations and policy review support
- suggested quote by deployment scope

### Pricing guardrails

- Keep legal language around “visual application,” not legally binding claim.
- Add-ons: priority support, additional onboarding credits, compliance packaging.
- Avoid feature baiting with unsafe unattended matching modes.

## Delivery roadmap (90 days)

### Day 1-14: Contract + discovery
- Finalize trust-class decisions.
- Publish migration plan for existing templates.
- Produce baseline onboarding and legal-boundary copy.

### Day 15-40: Core schema + authorization
- Multi-field recipe/version model.
- Vault ID binding.
- Grant lifecycle and OS-backed authorization adapter.

### Day 41-65: Engine + monitor
- Job intake and dedupe engine.
- Exact-match automation path.
- Retry/recovery and evidence output.

### Day 66-85: UX + console
- Dashboard, Recipe Builder, Review Console screens.
- Receipt and run log screens.
- Dry-run and review-first controls.

### Day 86-90: Pilot hardening
- Targeted corpus tests.
- Folder behavior tests (partial copy, rename, duplicates, app restart).
- Private pilot and operational playbook.

## Acceptance criteria for build handoff

- A user can define at least three signature bindings in one recipe.
- A recipe can be locked and only executed by a granted principal.
- An unsigned folder can be processed into a signed folder with clear state visibility.
- Exact-template jobs run unattended only under active grant and exact match.
- Any failure path emits a recoverable state and human-readable reason.
- Recipients can export a receipt with recipe version, grant, and matcher evidence.

## Screen and workflow redesign

### Screen set

- **Dashboard**
  - workflow status
  - active grant countdown
  - queue counters by state
  - emergency lock and pause

- **Recipe Builder**
  - source document
  - signer role and asset binding
  - field tags per page
  - matching mode and folder policy

- **Review Console**
  - failed/mismatched jobs
  - reason codes
  - retry and quarantine actions

- **Run Receipt View**
  - source/output hash summary
  - recipe version and grant record
- export as compliance pack

### Flow map (v1)

```text
Build recipe -> Dry run -> Approve -> Activate grant -> Folder scan -> Validate -> Match -> Review/Run -> Verify -> Emit signed output -> Receipt
```

### Interaction pattern rules

- lock state is always visible
- manual mode always possible
- unattended mode can only use exact-template class
- every destructive action requires confirmation

### UI tone and copy

- Use clear, low-risk wording such as “apply approved visual signature recipe.”
- Avoid legal absolutes such as “legally binding.”
- Show policy and evidence links in every high-risk screen.

### Screen-level acceptance spec

#### Dashboard

- States visible at all times: `Workflow Locked`, `Grant Active`, `Jobs in Retry`, `Need Review`.
- Primary actions: pause, resume, emergency stop, open recipe settings.
- Invariant: user can reach a running job’s failure details in no more than two clicks.

#### Recipe Builder

- Add and remove multiple signature fields before publish.
- Bind each field to both `role` and `vault asset`.
- Reject activation if any required field is missing role or asset.
- Invariant: recipe stores signature assets as vault IDs, not filesystem paths.

Dry-run output for preview must include:
- matched/unmatched fields,
- match class (exact/family/review),
- expected output filename,
- risk warnings.

#### Review Console

- Filter by state: `queued`, `needs_review`, `failed`, `completed`.
- For each item show:
  - input fingerprint,
  - matcher class,
  - failure reason,
  - recovery action options.
- Invariant: no destructive action proceeds without confirmation and audit trace.

#### Receipt View

- Export payload must include:
  - recipe id/version,
  - grant id,
  - input/output hashes,
  - field binding summary,
  - matcher evidence.
- Invariant: no signature raw bytes, no plain access token, no full plaintext path dumps.

### Flow variants

1. Manual-confirm flow
- Operator reviews each queued job.
- Shows placement preview, then explicit confirm.
- Verifies output before moving to completed.

2. Exact-match unattended flow
- Recipe approved and grant active.
- Incoming file auto-accepts only exact-match class.
- Ambiguous jobs route to needs_review.

3. Recovery flow
- On failure, show failure summary and operator actions.
- Retry resumes from preserved job context.
- Cancel prevents further mutations to source/output.

### GTM-style content blocks

#### Homepage section ideas

- Headline: “Sign recurring documents safely, locally, with full control.”
- Subhead: “Reusable recipes, controlled folders, and evidence-first outcomes.”
- CTA: “Create your first recipe”

#### Messaging guardrail

- Never claim legal binding in default product copy.
- Always pair feature claims with trust boundary: “authorized visual signature application.”

#### Persona-led distribution copy

- Legal operations: “Reduce recurring document variance with a controlled, inspectable workflow.”
- HR operations: “Bind employee and manager roles once, then reuse safely.”
- AP and finance: “Run batches with review gates and recoverable errors.”

### Metrics and success criteria

#### Leading signals (first 30 days)

- Onboarding completion rate.
- Recipes created and activated.
- Dry-runs completed before first full run.
- Median time to first successful signed output.

#### Risk signals

- Exact-match false-positive rate.
- Unattended jobs entering review lane.
- Emergency lock activations.
- Mean time to recover from failure.

#### Business signals

- Conversion by workflow tier.
- Recipes per active seat.
- Monthly signed output trend by cohort.

## Implementation backlog (copy/paste into project plan)

### Milestone A — Core model and data

- Implement `Workflow`, `RecipeVersion`, `FieldBinding`, `ExecutionGrant`, `WorkflowJob`, `JobEvent`, `Receipt` models under the existing persistence path.
- Migrate template schema to:
  - multi-field bindings,
  - immutable versioned recipe artifacts,
  - vault asset references.
- Add corruption-tolerant migration for legacy single-placement templates.
- Deliverable: import existing templates, create at least one multi-field recipe version, and keep old versions read-only.

### Milestone B — Authorization and security hardening

- Implement deny-by-default execution gate.
- Add grant creation with scope fields:
  - recipe version,
  - matcher class,
  - folder pair,
  - allowed assets/roles,
  - expiry and usage caps.
- Add explicit role checks (asset owner, approver, runner, auditor).
- Add OS keyring/secure-store adapter interface and fail-closed behavior.
- Deliverable: unauthorized run attempt is blocked with auditable reason.

### Milestone C — Workflow engine

- Add single orchestration engine with state machine:
  - discovered -> validating -> matched -> queued -> processing -> verifying -> completed.
- Add duplicate/coalesce handling with idempotency keys.
- Add structured signer result contract (remove bare boolean + print-only flow).
- Add atomic output staging, reopen check, and promotion.
- Deliverable: same job hash never signs same document twice in one active run.

### Milestone D — Folder monitor and queue

- Add wake-on-change watcher + periodic reconciliation.
- Add file-stability checks and symlink-root guards.
- Add queue transitions into review/fail/retry/quarantine/cancel states.
- Add lock to prevent concurrent runners.
- Deliverable: missed watcher event still recovered by reconciliation.

### Milestone E — Dashboard and builder UX

- Implement Dashboard, Recipe Builder, Review Console, Receipt View screens.
- Add dry-run, review-only mode for non-exact matches.
- Add grant lifecycle UI and emergency stop.
- Add receipt export and retention controls.
- Deliverable: manual confirm path and unattended exact-match path both pass acceptance table.

### Milestone F — Verification and rollout

- Build corpus for:
  - exact-match positives,
  - exact-match negatives,
  - rotated/multipage/malformed PDFs,
  - partial copy and retry windows.
- Add failure taxonomies and localized user-facing recovery messaging.
- Pilot with 2 target teams and publish operator runbook.
- Deliverable: evidence log + user training artifact + go-live checklist.

## User stories and edge cases (build-ready)

### Epics

1. Build and manage controlled recipes.
2. Configure workflow authorization and grants.
3. Process unsigned documents from folder into signed folder.
4. Review, recover, and close jobs safely.
5. Export proof and evidence for compliance/auditing.

### Stories (example slice)

- **As an operations user**, I want to define a recipe with multiple signature fields so I can reuse one approved workflow across many documents.
  - Given a source PDF is selected
  - When I add multiple signature roles and bind vault assets
  - Then I can save a draft and publish version 1 of that recipe.

- **As an approver**, I want to block execution unless authorization is explicitly granted so no unauthorized signing occurs.
  - Given a recipe is active but no valid grant exists
  - When an execution attempt starts
  - Then execution is refused and a block reason is logged.

- **As a runner**, I want unattended exact-template signing from an input folder so repetitive work completes automatically.
  - Given grant and exact-match policy are active
  - When valid files land in the watched folder and stabilize
  - Then jobs move from discovered to completed with receipts.

- **As an operator**, I want automatic recovery paths so ambiguous or failed jobs are explainable and fixable.
  - Given a job fails with a non-transient reason
  - When I open the Review Console
  - Then I can retry with corrected context or quarantine with notes.

- **As an auditor**, I want to export receipts with matching and authorization lineage so evidence is reproducible.
  - Given multiple jobs complete
  - When I export the compliance pack
  - Then each receipt includes recipe/grant/matcher and hash lineage.

### Edge-case matrix (must pass before v1 release)

- Duplicate filename with same content while previous run active.
- Same content with different filename.
- Signature asset revoked between draft and execute.
- Grant expires mid-batch.
- Input copied slowly then renamed.
- App restart during verification.
- Source PDF password-protected / malformed.
- Output folder unavailable at publish time.
- Folder contains unsupported extension.
- Symlink in input path that escapes policy root.

### Non-functional requirements

- **Reliability:** no silent loss of job state under restart; durable persistence for queue events.
- **Security:** fail-closed authorization, secure vault access, no plaintext secrets in audit payloads.
- **Performance:** folder intake should detect a new file and route it within bounded delay for exact-match mode.
- **Privacy:** no signature pixel bytes, credentials, or raw exception bodies in exportable logs.
- **Usability:** recovery action available in one click from failure state.
- **Observability:** clear reason codes and actor/approval stamps on every transition.

## Work item contract (starter backlog)

1. `desktop_app/workflows/models.py` — typed models for recipe versions, jobs, grants, events, receipts.
2. `desktop_app/workflows/store.py` — persistence layer and migrations.
3. `desktop_app/workflows/authorization.py` — local grant and role checks.
4. `desktop_app/workflows/matcher.py` — exact+family match classes.
5. `desktop_app/workflows/engine.py` — state machine, execution entrypoint, retries.
6. `desktop_app/workflows/folder_monitor.py` — watcher + reconcile loop.
7. `desktop_app/workflows/verifier.py` — output integrity checks.
8. `desktop_app/views/main_window_parts/workflow_console.py` — dashboard and controls.
9. `desktop_app/views/main_window_parts/recipe_builder.py` — flow for binding/signature spaces.
10. `desktop_app/pdf/signer.py` — structured result + atomic-safe output behavior.
11. `desktop_app/pdf/db_audit.py` — event schema extension, non-sensitive fields.
12. `docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/workflows_launch_pack.md` — go-live runbook and recovery procedures.
13. `docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/workflows_sprint_board.md` — prioritized tickets with dependencies, DoR, DoD.
14. `docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/workflows_module_interfaces.md` — API and data contract references.
15. `docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/template_to_recipe_migration_checklist.md` — migration and rollout safety checks.
16. `gtm_persona_flows_pricing_screens_pack.md` — GTM positioning, persona use cases, pricing, flow maps, and screen-level design targets.
17. `launch_deck_v1.md` — sales-ready slide pack with positioning, GTM sequence, persona summary, pricing, and screen outcomes.
18. `workflows_screen_and_task_execution_plan.md` — screen acceptance criteria and implementation sequencing.

## Sprint board and rollout sequence

See [workflows_sprint_board.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/workflows_sprint_board.md) for the full priority list, effort envelope, and acceptance.

## Module interface contract

See [workflows_module_interfaces.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/workflows_module_interfaces.md) for:

- typed models,
- public function/class contracts,
- failure-code taxonomy,
- persistence assumptions.

## Migration reference

Use [template_to_recipe_migration_checklist.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/template_to_recipe_migration_checklist.md) during schema changes and rollback planning.

## Acceptance gates before implementation

1. Data model gate
- Legacy recipe migration completed.
- Multi-field versioned recipe can be created.

2. Security gate
- Deny-by-default path blocks all unauthorized and expired-grant executions.
- Key-store failure blocks signing and marks workflow unavailable.

3. Correctness gate
- Exact-match unattended mode passes negative/positive deterministic fixtures.
- Duplicate/renamed files do not duplicate signed output.

4. Recovery gate
- Retry behavior is bounded and stateful.
- Recovery action can resume or cancel without corrupting source/output.

5. Evidence gate
- Receipt export includes recipe/grant/matcher lineage.
- Hash and state trail is human-readable in UI and file export.

## Out-of-scope for v1 (explicit)

- Full cloud identity provider and e-sign certificate integration.
- Headless background service mode while app is closed.
- OCR-assisted matching with unattended execution.
- Legal-intent guarantee language beyond authorized visual placement boundary.

## Definition of "do all"

This pack is complete only when all three layers are present:

1. Product layer: strategy, personas, pricing, GTM, differentiation, guardrails.
2. Workflow layer: recipe model, authorization, folder automation, monitoring, recovery.
3. Delivery layer: milestones, backlog, dependencies, gates, and measurable criteria.

When these are in place, we should move from exploration to v1 implementation tickets.

## Platform strategy decision: Native mac app vs PySide multi-platform

### Recommendation (v1)

Do **not** start a parallel native Mac codebase now.

**Reasoning**
- We already have a PySide desktop path that can deliver the core workflow in one codebase across Mac/Windows/Linux.
- Running workflow logic in parallel in a native Mac app creates split ownership of signing, vault, queue, and audit logic.
- The highest-risk scope for this project is trust/security correctness, not native control polish.
- Premium feel is achievable with a deeper UI refresh, onboarding, and macOS packaging quality (app icon, signing, notarization, onboarding flow) without rewriting platform runtime.

### When native mac becomes the right choice (post-v1)

- When macOS-specific capabilities become mandatory for the trust model:
  - first-class Keychain UX requirements that are impossible to satisfy cleanly through shared bindings,
  - native secure enclave / Touch ID workflows that materially change security posture,
  - strict macOS App Store or hardware distribution constraints.
- When a dedicated Mac-design language is a product differentiator with enough demand to justify duplicated engineering.

### Recommended phased path

1. **Phase 0 (v1):** keep PySide single-source for all desktop platforms.
2. **Phase 1 (post-acceptance):** add a hardened mac package profile (Mac app bundle, notarization, launch UX, marketing copy), no runtime split.
3. **Phase 2 (if justified):** evaluate a thin native mac shell only if it can consume the same workflow package as a service/SDK.

### Premium positioning impact

- Premium pricing can be supported by:
  - workflow safety guarantees,
  - auditability and recovery depth,
  - deployment/operations support,
  - not by runtime rewrite alone.

### Decision record: DR-2026-07-24-01 (Platform strategy)

- **Decision:** Defer native mac runtime split until post-v1.
- **Context:** We are building a trust-sensitive document workflow where correctness and auditability are the moat, not native UI chrome.
- **Options considered:**
  - Parallel native Mac build now
  - PySide as single runtime across desktop with macOS packaging polish
  - Native runtime later on explicit mac-only requirements
- **Reason for choosing PySide-first:**
  - lower blast radius on security and compliance logic,
  - faster proof of concept and pilot,
  - consistent behavior across Windows/Linux/macOS.
- **Trade-offs accepted:**
  - less “native skin” in the first release,
  - mac-specific UX polish deferred to post-v1 token budget.
- **Revisit trigger:**
- pilot feedback identifies a mac-only requirement that materially changes security posture or conversion, or
- customer demand exceeds the complexity cost and justifies duplication.

## Readiness references

- [mac_premium_readiness_checklist.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/mac_premium_readiness_checklist.md) — readiness proof before pricing-premium or native-mac reconsideration.
- [gtm_mac_runtime_split_record.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/gtm_mac_runtime_split_record.md) — decision baseline for native-runtime tradeoff.
- [w16_go_no_go_matrix.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/w16_go_no_go_matrix.md) — quantitative W16 decision logic.
- [gtm_persona_flows_pricing_screens_pack.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/gtm_persona_flows_pricing_screens_pack.md) — marketing, pricing, user flows, and screen design pack.
- [launch_deck_v1.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/launch_deck_v1.md) — one-page launch-ready GTM and commercial summary.
- [workflows_screen_and_task_execution_plan.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/workflows_screen_and_task_execution_plan.md) — screen acceptance and dev sequencing.
