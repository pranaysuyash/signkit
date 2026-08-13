# SignKit super-app feature matrix and first implementation slices

Date: 2026-08-03  
Status: partial readiness audit. Local contracts are testable. A hosted
super-app release is not proven.

This is an additive planning and evidence artifact. It does not replace the
desktop app, the root landing page, the protected workspace API, or retained
concept/review trees.

## 1. Current product surfaces and evidence

| Surface | Current source of truth | What is actually implemented | Evidence | Readiness boundary |
| --- | --- | --- | --- | --- |
| Public acquisition and checkout | `index.html`, `_redirects`, `wrangler.toml`, `web/live/js/checkout-config.js`, `web/live/js/checkout.js` | Root `index.html` is the canonical Cloudflare Pages landing source. Dodo is primary only when a valid `pdt_...` ID is configured; Gumroad is the fallback. Legacy HTML and direct concept entrypoints are intended to 301 to `/`. | `tests/test_landing_surface_contract.py`; `scripts/test-local-landing.sh`; focused run below: 5 tests and local smoke passed. Tier 2. | Current public deployment is stale: `bash scripts/test-deployment.sh https://signkit.work` fails at `/root` with HTTP 200 instead of 301. Do not call hosted checkout or redirect behavior ready. |
| Desktop extraction and PDF workspace | `desktop_app/views/main_window.py`, `desktop_app/views/main_window_parts/extraction.py`, `desktop_app/views/main_window_parts/pdf.py`, `desktop_app/processing/extractor.py`, `desktop_app/pdf/` | Local image selection and cleanup, encrypted signature Vault, PDF rendering/placement, form/annotation helpers, audit logging, and export code exist. | `desktop_app/tests/` includes extractor, Vault, PDF, annotation, field detection, and workflow suites. [`docs/review/runtime_qa_audit_2026-07-31.md`](../review/runtime_qa_audit_2026-07-31.md) records a remediated premium launch and manual checks, but explicitly says populated workflow execution, retry/quarantine, PDF placement/save, and populated Vault behavior were not exercised. Tier 2 to Tier 4 depending on path. | Release artifacts still require build, install, launch, signing, and per-platform runtime proof. Static tests do not prove a shipped DMG or Windows/Linux package. |
| Desktop recurring workflow operator surface | `desktop_app/workflows/`, `desktop_app/views/main_window_parts/workflow_console.py` | Recipe, grant, folder monitor, matching, verification, queued/retry/failed/completed states, pause/resume, quarantine, and operator actions are present. | `desktop_app/tests/test_workflow_engine.py`, `test_workflow_store.py`, `test_workflow_screen_smoke.py`, `test_folder_monitor.py`, `test_modular_entitlements.py`. Tier 2. | The operator can see local state, but no cross-topology event contract or hosted role model exists yet. |
| Browser workspace control plane | `web/cloud_workspace/index.html`, `web/cloud_workspace/app.js`, `backend/app/routers/workspace.py`, `backend/app/services/workspace.py`, `backend/app/models/workspace.py`, `backend/app/schemas/workspace.py` | Authenticated owner-scoped template discovery, execution creation, explicit review/participant-confirmation transitions, cancellation, and ordered event receipt. It stores metadata only, not documents or signatures. | `backend/tests/test_workspace_service.py` and an isolated SQLite + uvicorn API flow: register 201, login 200, template 200, create 201, two transitions 200/200, terminal replay 409. Tier 2 and Tier 3. | `backend/app/main.py` mounts `/workspace-app` for local/server use. Cloudflare Pages deploys the repository root and has no backend hosting or production API binding. Hosted browser workspace is not ready. |
| Extraction API capability | `backend/app/routers/extraction.py`, `backend/app/services/extraction.py`, `backend/app/security.py` | Upload, region selection, and processed PNG response with extension, magic-number, size, dimensions, pixel, color, threshold, and path checks. | Static inspection and backend test inventory. Tier 1. | No current browser client calls `/extraction`. Upload routes are not owner-authenticated and `/uploads/images` is statically mounted, so this is not a safe Cloud document surface until the privacy and authorization contract is redesigned. |
| Concepts and review artifacts | `web/concepts/`, `web/archives/`, `web/backups/`, `docs/review/`, `docs/decisions/` | Product Museum, topology, workbench, customer-work, and workspace concepts are retained for comparison and research. | `_redirects` and `tests/test_landing_surface_contract.py` classify direct HTML artifacts as non-public. Tier 2. | Concepts must remain additive until an explicit product decision and migration gate. They are not launch surfaces or API sources of truth. |

### End-to-end workflow map

1. **Personal acquisition:** visitor input -> root static page -> checkout provider
   resolution in `checkout.js` -> external provider purchase/delivery -> GA4 and
   provider/operator records. Missing or malformed Dodo fails closed and makes
   Gumroad actionable. Payment, entitlement delivery, activation, retry,
   duplicate prevention, and refund remain unverified Tier 3 gates.
2. **Cloud execution register:** owner account form -> `/auth/register` or
   `/auth/login` -> JWT -> `/workspace/templates` and
   `/workspace/executions` -> `workspace_executions` plus append-only
   `workspace_execution_events` -> browser passport, state metrics, and receipt.
   Invalid transitions return 409; API errors render a user message or alert.
   Current events record the owner acting on behalf of reviewer/participant, not
   independent identity or a legal signature.
3. **Local document completion:** file or camera input -> extraction selection
   and cleanup -> encrypted local Vault -> PDF viewer/placement/signing adapter
   -> audited output PDF and local operator UI. Retry and quarantine behavior
   belongs to `desktop_app/workflows/`; output paths and audit events are local.
4. **Browser extraction (not yet a real workflow):** a future browser input may
   call the existing `/extraction` router, but there is currently no web caller,
   owner scoping, document retention contract, or browser PDF output. Build this
   only by extending the canonical extraction/workspace pipeline, not by adding
   a second upload route.

## 2. Vertical and horizontal feature matrix

| Capability | Local desktop | Browser Cloud | Hybrid target | Canonical data/API contract | Failure, retry, and observability |
| --- | --- | --- | --- | --- | --- |
| Extract and clean signature | Implemented path in `desktop_app/processing/extractor.py` and extraction views | Not wired | Local extraction with explicit sync consent later | Reuse extraction algorithms and validation; do not create a second extractor | Invalid/garbage image rejected; show actionable error; capture local error log and input reference without raw sensitive content. Tier 2 now, Tier 3 after end-to-end fixture run. |
| Encrypted signature Vault | `desktop_app/processing/vault.py` Fernet blobs, JSON metadata, and restrictive permissions when a new key is created | Not implemented | Encrypted transfer only after consent and key ownership decision | Define a versioned signature-asset record before sync; no raw path or plaintext secret in events | Missing blobs raise an error and deletion is logged; corrupt metadata currently resets the in-memory index and there is no backup-recovery path. Recovery, key-permission auditing, and deletion evidence are open. Tier 1 to Tier 2 now, Tier 3 before sync. |
| PDF render, placement, annotations, export | `desktop_app/pdf/renderer.py`, `viewer.py`, `signer.py`, `annotations.py`, `form_fields.py` | Browser PDF viewer/editing is not implemented | Local render remains authoritative until sync contract exists | Use one PDF adapter contract and one coordinate mapping model; browser may consume the contract, not fork it | Unsupported PDF or optional dependency shows install/status path; export failure preserves source and audit reason. Tier 2 now, Tier 3 for release fixtures. |
| Controlled recurring workflows | `desktop_app/workflows/engine.py`, `store.py`, `folder_monitor.py`, `authorization.py`, `verifier.py` | Cloud currently has metadata-only `hr-onboarding-core` control plane | Shared versioned execution object, topology field, and explicit consent | `WorkspaceExecution` plus event receipts is the current cloud contract; map desktop jobs to it only through an ADR | States include queued, review, retry, failed, completed, cancelled. Every retry must be idempotent and operator-visible. Tier 2 local, Tier 3 after cross-topology contract test. |
| Auth and roles | Local license and workflow authorization | JWT owner scope in `backend/app/utils/dependencies.py`; participant/reviewer are fields, not users | Membership and role claims required | Extend `/workspace` router and schemas; do not add `workspace-v2` routes | Expired/invalid token 401, foreign execution 404, illegal transition 409. Log event type and actor ID, never passwords or document bytes. Tier 3 required before external actors. |
| Checkout, licensing, entitlement | `desktop_app/license/`, `desktop_app/config.py` | Static provider routing only | Activation receipt tied to provider and device policy | One public checkout config plus one entitlement service contract | Provider timeout, duplicate webhook, refund, and activation retry need idempotency keys and an operator reconciliation view. No Tier 3 payment proof exists. |
| Operator visibility | Desktop workflow console and local audit DB | Browser passport and receipt | Unified run/event vocabulary | Preserve `event_type`, `status_from`, `status_to`, sequence, actor, timestamp | Every failed/retried/skipped action must expose reason and next action. Add correlation/run IDs before cross-topology execution. |
| Privacy and retention | Local-first storage and local policy docs | Current workspace stores names, emails, date, and notes only | Per-surface consent, retention, deletion, export, encryption, and access rules | Add a data map and retention policy before document upload or sync | Do not expose public uploads. Current extraction upload/static mount is a release blocker for Cloud. Tier 3 security review required. |

## 3. First implementation slices

These are dependency-ordered commit units, not calendar estimates.

### Slice 1: make the canonical web release observable and reproducible

**Touch:** deployment workflow/config and web test ownership around `index.html`,
`_redirects`, `web/live/js/checkout-config.js`, `web/live/js/checkout.js`,
`scripts/test-local-landing.sh`, `scripts/test-deployment.sh`, and
`.github/workflows/auto_publish_landing.yml`.

**Acceptance:** a clean checkout has one root landing source; every retained HTML
route redirects to `/`; checkout assets return JavaScript with the expected body;
production smoke passes `/`, `/index.html`, robots, sitemap, and all redirect
forms. The Dodo ID remains empty until a controlled payment gate succeeds.

**Failure/retry and visibility:** deployment fails closed on missing files, wrong
content type, stale HTML fallbacks, or redirect drift. Record deployment URL,
commit SHA, route status, asset content type, and provider state. Retry only after
publishing the intended root and rerunning the exact smoke command.

**Verify:**

```bash
./.venv/bin/pytest -q tests/test_landing_surface_contract.py
bash scripts/test-local-landing.sh
bash scripts/test-deployment.sh https://signkit.work
```

Required evidence: Tier 2 local, then Tier 5 network route/content checks. Current
production result is not accepted: `/root` returned 200 and the remote checkout
asset paths returned `text/html`, so this slice is open.

### Slice 2: complete the local vertical execution contract

Finish the local workflow path first: folder ingestion, matching, signature
placement, review, retry/quarantine, and audited export. Add batch progress and
cancel where the current engine supports it. Acceptance is an end-to-end local
operator run with a recoverable failure and a complete event trail.

### Slice 3: converge desktop and browser execution on one aggregate/child contract

**Touch:** `backend/app/schemas/workspace.py`, `services/workspace.py`,
`routers/workspace.py`, `web/cloud_workspace/app.js`, and the desktop workflow
models/store/console. Add membership and explicit role claims before allowing a
participant or reviewer to act directly. Keep `/workspace` as the only workspace
route family.

**Acceptance:** a cloud `WorkspaceExecution` aggregate maps to one or more local
`WorkflowJob` children through an explicit command/event envelope. The mapping
supports create, review, completion, retry, cancel, and replay without inventing
a second state machine. Unauthorized reads are 404, invalid transitions are 409,
terminal replay is rejected, event sequence is monotonic, and the operator can
see who acted, when, why, and what remains. This slice remains metadata-only.

**Failure/retry and visibility:** use idempotency keys for transition retries;
record correlation ID, actor, previous state, next state, attempt, and error class;
never log credentials, PDFs, signature bytes, or raw filesystem paths. A failed
transition leaves the prior state intact and offers a safe retry action.

**Verify:**

```bash
./.venv/bin/pytest -q backend/tests desktop_app/tests/test_workflow_engine.py \
  desktop_app/tests/test_workflow_store.py desktop_app/tests/test_workflow_screen_smoke.py
contract_tmp_dir="$(mktemp -d /tmp/signkit-contract.XXXXXX)"
trap 'rm -rf "$contract_tmp_dir"' EXIT
DATABASE_URL="sqlite:///$contract_tmp_dir/contract.db" \
JWT_SECRET="$(python3 -c 'print("a"*64)')" \
PYTHONPATH="$PWD" ./.venv/bin/python -m alembic -c backend/alembic.ini upgrade head
```

Add a browser/API test that exercises register, login, create, review, confirm,
replay, foreign-owner access, and retry. Target Tier 3 integration plus Tier 4
browser observation before calling the slice ready.

### Slice 4: ship a privacy-safe document asset path, then expose it to web

**Touch:** first the canonical desktop PDF/Vault contracts and a new data map;
then extend `backend/app/routers/extraction.py` and its schemas only after
owner-scoped storage, retention/deletion, malware/content checks, encryption,
and operator recovery are accepted. `web/cloud_workspace` is a consumer, not a
new pipeline.

**Acceptance:** a document set or signature asset has an explicit owner,
content-integrity hash, retention deadline, deletion/export behavior, storage
location abstraction, and audit event. Upload, processing, partial failure, retry,
and cancellation preserve an explainable state. No public static mount exposes
private bytes. This slice cannot start until a separate privacy/storage ADR is
marked **Accepted** by its owner/reviewers and Tier 3 security/integration
evidence is attached. Until then, cloud document bytes are prohibited and the
workspace may carry metadata or opaque references only. The browser can show
source, processing, output, and operator status without claiming legal signing
or identity verification.

**Failure/retry and visibility:** reject malformed or oversized input; use bounded
retries with idempotency; quarantine failed inputs; expose operator repair and
deletion actions; redact sensitive values in logs. Roll back partial output or mark
it explicitly as partial and non-final.

**Verify:**

```bash
./.venv/bin/pytest -q desktop_app/tests/test_extractor.py \
  desktop_app/tests/test_vault_metadata.py desktop_app/tests/test_pdf_features.py \
  tests/test_landing_surface_contract.py backend/tests
```

Add security tests for unauthenticated upload, cross-owner access, stale retention,
garbage bytes, duplicate retry, and log redaction. Tier 3 integration is the
minimum. Do not enable a public Cloud upload based on current Tier 1 extraction
code.

## 4. Build, deployment, and release contracts

- **Web build:** there is no root `package.json`; root `package-lock.json` lists
  Puppeteer, while `web/e2e/package.json` owns Playwright scripts. `npm test` in
  `web/e2e` currently fails because `@playwright/test` is not installed. Run
  `cd web/e2e && npm install --no-audit --no-fund && npx playwright install` in a
  controlled setup before claiming browser E2E.
- **Landing deploy:** `.github/workflows/auto_publish_landing.yml` and
  `manual_publish_landing.yml` publish the repository root to Cloudflare Pages.
  `wrangler.toml` has `pages_build_output_dir = "."`. These workflows do not
  deploy FastAPI, migrations, or `/workspace-app` as a hosted backend.
- **Backend run:** `scripts/run-backend-dev.sh` uses the local `BACKEND_PORT`
  default of 8001 and starts `uvicorn backend.app.main:app` on that port.
  `backend/alembic/` is the migration source. `backend/app/main.py` still calls `Base.metadata.create_all` for local
  compatibility, so production must run migrations explicitly and avoid relying on
  import-time schema creation.
- **Desktop build:** `build-tools/build.py --show-targets` reports standard
  Darwin/Linux/Windows specs and the `mac-premium` Darwin spec. CI workflows
  `.github/workflows/build-all-platforms.yml` and `build-macos.yml` produce DMG,
  ZIP, and tar artifacts. A build directory or signed release artifact is not
  present in this checkout, so release readiness remains unproven.
- **Web E2E:** `web/e2e/playwright.config.js` targets `http://localhost:8080`;
  current specs mostly exercise legacy `/purchase.html` and remote
  `https://signkit.work`, not `/workspace-app`. Add canonical root and workspace
  specs after dependency installation, with fresh-tab console and responsive
  checks.

## 5. Non-goals, review prompts, and update log

### Non-goals for these slices

- Do not replace `web/live` or publish a concept tree as the canonical landing.
- Do not add duplicate workspace or extraction routes.
- Do not claim cloud document storage, legal signatures, identity verification,
  certificates, sync, payment activation, or production deployment without Tier 3+
  evidence.
- Do not publish Team/Business/Automated Packet Ops prices before fulfilment,
  retention, support, and payment contracts exist.
- Do not treat a passing unit/static test as browser, device, provider, or release
  proof.

### Anything else?

Yes. The super-app direction is viable only if Local, Cloud, and Hybrid are
topologies over one execution and asset contract. The current repository already
has strong local workflow primitives and a metadata-only Cloud control plane, but
the boundary between them is not yet a deployed product. The highest-risk gap is
not visual polish. It is private document handling, role authorization,
idempotent retries, and observable deployment. Close those contracts before
adding more surface area.

### Update log

- 2026-08-03: Added the vertical/horizontal matrix, mapped current desktop,
  backend, browser, landing, and build surfaces, and defined the dependency-
  ordered implementation slices. Focused verification command:
  `./.venv/bin/pytest -q tests/test_landing_surface_contract.py backend/tests/test_workspace_service.py`
  -> `8 passed in 1.31s`.
- 2026-08-03: Recorded that hosted route and checkout evidence remains open and
  that Playwright dependencies are not installed in `web/e2e`.
- 2026-08-12: Extraction API ownership contract advanced from Tier 1 to Tier 3
  application evidence. The canonical route now requires JWT authentication,
  enforces asset/workspace ownership, records export/delete/audit receipts, and
  converges duplicate and concurrent retries. Isolated SQLite migration through
  `e42b7f8c91aa` passed. Production migration, live hosted smoke, and operator
  recovery remain open; the earlier matrix row is historical and must not be
  read as current hosted behavior.
