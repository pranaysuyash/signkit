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
