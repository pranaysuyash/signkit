# Tools

Reusable helpers for local exploration and validation.

## ContractDesk web proof

- `run_contractdesk_web_proof.py`: starts the canonical backend on deterministic
  port `8871` by default, checks `/health`, `/workspace-app/`, its assets, and
  the synthetic fixture, then shuts the backend down. Use `--keep-running` to
  leave it available for a fresh browser context. Use `--check-existing` when
  probing an already-running backend on the same explicit port.
- `package_contractdesk_proof.py`: atomically packages the deterministic web
  fixture into a content-addressed synthetic manifest and `receipt.ndjson`.
  The package explicitly reports `synthetic: true` and
  `signature_status: not_signed`; it is not a signed document export.
- `run_contractdesk_browser_proof.py`: uses the installed Python Playwright
  browser API against a keep-running canonical backend to verify the live
  workspace control-plane markers and local/cloud boundary copy. It does not
  prove hosted document processing or signing behavior.

Usage:

```bash
./.venv/bin/python tools/run_contractdesk_web_proof.py
./.venv/bin/python tools/run_contractdesk_web_proof.py --port 8871 --keep-running
/opt/homebrew/opt/python@3.11/bin/python3.11 tools/run_contractdesk_browser_proof.py --base-url http://127.0.0.1:8872
./.venv/bin/python tools/package_contractdesk_proof.py
./.venv/bin/pytest tests/test_contractdesk_proof_tools.py -q
```

## Public-surface audit

- `audit_public_surface.py`: checks parity between `_redirects` and `serve.py`,
  verifies root claim markers against the launch registry, confirms canonical
  checkout assets, and reports retained historical route references.
- `test_deployed_surface.py`: probes the live root, redirects, and canonical
  checkout asset without following redirects.

Usage:

```bash
python3 tools/audit_public_surface.py --strict
python3 tools/audit_public_surface.py --json
python3 tools/test_deployed_surface.py --base-url https://signkit.work
```

## Local product browser proof

- `run_local_product_browser_proof.mjs`: runs a real Playwright browser
  context against the local canonical root and existing workspace. It checks
  1440x900, 390x844, and 320x844; the semantic main landmark; focused skip-link
  target and visibility; labeled five-state rail; canonical primary workspace
  CTA; reduced-motion media behavior; keyboard and pointer state progression;
  checkout fallback; responsive overflow; browser errors; and the
  root-to-`/workspace-app/` handoff. It does not start servers or contact a
  hosted service. This is a bounded browser accessibility contract, not a
  screen-reader or assistive-technology certification. The default Playwright
  module path points to the shared
  Browser Daemon skill; override it with `SIGNKIT_PLAYWRIGHT_MODULE` when a
  different installed runtime is authoritative.

Usage:

```bash
node tools/run_local_product_browser_proof.mjs
SIGNKIT_LANDING_BASE_URL=http://127.0.0.1:8080 \
SIGNKIT_WORKSPACE_BASE_URL=http://127.0.0.1:8001 \
node tools/run_local_product_browser_proof.mjs
```

## Local product stack

- `run_local_product_stack.py`: starts the existing FastAPI local companion and
  canonical `serve.py` landing together, waits for `/health` and `/`, prints
  both URLs, and terminates both children together. It defaults to an isolated
  rebuildable SQLite database and data root under `.codex-test-tmp/`; pass
  `--database-url` or `--data-dir` only when intentionally using another local
  resource. Ambient `DATABASE_URL` and `SIGNKIT_DATA_DIR` values are ignored
  unless explicitly passed through those options. This keeps preview uploads
  and logs out of the normal SignKit application-support directory. It does
  not proxy or duplicate the workspace route.

Usage:

```bash
./.venv/bin/python tools/run_local_product_stack.py
./.venv/bin/python tools/run_local_product_stack.py --once
```

## Local source-to-ready proof

- `run_local_source_to_ready_proof.py`: composes the existing desktop
  `SignatureExtractor`, encrypted `NotaryVault`, persisted `WorkflowEngine`,
  metadata-only `ExecutionPassport`, PDF signer, and `ArtifactReceipt` into a
  disposable local proof. It forces one transient signing failure after real
  extraction and vault resolution, then retries through the canonical engine
  path. It writes a JSON manifest and receipt under the requested output
  directory. It does not contact a hosted service or use the browser workspace
  to retain document bytes.

The browser workspace can now project an authorized local desktop passport
through `/workspace/local-jobs`. The projection is metadata-only and retry
delegates to the existing `WorkflowEngine`; it does not create a second local
store or signing pipeline.

`run_local_workspace_bridge_browser_proof.mjs` extends the local proof with a
disposable authenticated account and a seeded, grant-bound desktop job. It
checks unauthenticated and missing-job direct URLs, exact owner binding,
private-path exclusion, browser passport visibility, and real retry recovery.
The retry route accepts an optional bounded `Idempotency-Key`, derives a
deterministic default when absent, persists an internal replay receipt, and
serializes the canonical local store so repeated or concurrent keyed requests
converge on one engine execution. The browser receives only the opaque key and
passport projection.
Run it with the local stack using the same isolated `SIGNKIT_DATA_DIR`:

```bash
SIGNKIT_DATA_DIR="$PWD/.codex-test-tmp/bridge-browser-data" \
node tools/run_local_workspace_bridge_browser_proof.mjs
```

To link the bridge proof to an actual source-to-ready artifact receipt, pass
the `artifact_id` from that proof's `manifest.json`:

```bash
SIGNKIT_DATA_DIR="$PWD/.codex-test-tmp/bridge-browser-data" \
SIGNKIT_LOCAL_RECEIPT_REFERENCE="sha256:..." \
node tools/run_local_workspace_bridge_browser_proof.mjs
```

Usage:

```bash
./.venv/bin/python tools/run_local_source_to_ready_proof.py
./.venv/bin/python tools/run_local_source_to_ready_proof.py \
  --output-dir .codex-test-tmp/source-to-ready-proof-review
```

## Release artifact evidence

- `release_artifact_ledger.py`: the canonical producer and validator for the
  machine-readable release artifact ledger. It records digests, signing and
  smoke status, evidence references, and a recoverable prior release. File
  existence or a successful build does not satisfy the strict ready gate.

Usage:

```bash
python3 tools/release_artifact_ledger.py --help
python3 tools/release_artifact_ledger.py --ledger ./artifacts/release_artifact_ledger.json --require-ready
```

## PDF fixtures

- `generate_native_form_fixture.py`: generates a reusable AcroForm benchmark PDF with text, checkbox, dropdown, and radio widgets.
- `generate_parser_benchmark_corpus.py`: generates the broader parser benchmark corpus.
- `compare_parser_baselines.py`: prints the current parser comparison matrix.

## Signature test-data fixtures

- `generate_signature_edge_case_fixtures.py`: regenerates the deterministic,
  synthetic signature corpus used for blank, low-contrast, tilted, noisy, and
  partially occluded inputs.
- `generate_signature_benchmark.py`: generates a deterministic, synthetic,
  subject-disjoint train/validation/test benchmark with single, multiple, and
  negative pages. It is a test-data benchmark, not human or production data.
- `validate_test_data_environment.py`: rejects system Python and reports missing
  extractor modules before tests or builds mutate an environment. Use
  `--backend` to additionally require Alembic, FastAPI, SQLAlchemy, multipart
  parsing, JWT, and a pytest launcher that targets the selected interpreter.
- `run_extraction_hosted_smoke.py`: applies the Alembic head to a temporary
  SQLite database and exercises the real authenticated extraction flow through
  upload, replay, ownership denial, processing, export, delete, and audit.
- `run_local_migration_recovery_proof.py`: applies the current Alembic head to
  temporary SQLite state, downgrades the latest receipt-field migration to its
  preceding revision, and re-upgrades it. This is local migration recovery
  evidence, not target-database rollback proof.
- `run_local_packaged_runtime_proof.py`: verifies the current macOS package,
  ad hoc signature, credential exclusion, bundled workspace asset, frozen
  health readiness, isolated data root, and clean port-8001 shutdown. Browser
  interaction remains a separate Playwright proof.
- `evaluate_signature_corpus.py`: evaluates labeled signature boxes with
  presence, instance, localization, and count metrics.
- `validate_signature_corpus.py`: checks annotation geometry, image dimensions,
  hashes, required coverage tags, and optional subject split leakage before
  scoring.
- `import_ultralytics_signature_corpus.py`: converts an externally stored
  Ultralytics YOLO corpus into SignKit metadata without copying raw images into
  the repository.
- `audit_test_data_storage.py`: reports disk pressure and explicitly classified
  cleanup candidates without deleting environments, caches, or raw corpora.
- `mutation_check.py`: runs the hand-curated S3 test-sensitivity manifest. Each
  type-valid source mutation must be killed by its declared tests; parse or
  collection failures are reported as broken mutants, not false kills.
- `validate_dataset_registry.py`: validates the machine-readable external
  dataset candidate registry and blocks contradictory download/decision states.
- `inspect_signverod_corpus.py`: reads SignverOD Parquet schema, row, category,
  and multi-box counts without copying raw document images into the repository.
- `evaluate_signverod_corpus.py`: evaluates only signature-class boxes directly
  from protected Parquet bytes and writes metrics without materializing images
  into the repository.

Usage:

```bash
./.venv/bin/python tools/generate_signature_edge_case_fixtures.py
./.venv/bin/python tools/validate_test_data_environment.py --repo-root .
./.venv/bin/python tools/validate_test_data_environment.py --repo-root . --backend
./.venv/bin/python tools/run_extraction_hosted_smoke.py
./.venv/bin/python tools/evaluate_signature_corpus.py --repo-root .
./.venv/bin/python tools/validate_signature_corpus.py --repo-root .
```

Usage:

```bash
./.venv/bin/python tools/generate_native_form_fixture.py
./.venv/bin/python tools/generate_parser_benchmark_corpus.py
./.venv/bin/python tools/compare_parser_baselines.py
```
