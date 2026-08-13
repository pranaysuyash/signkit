# Test Data Audit & Task Ledger

**Owner:** Test Data Engineering Track
**Scope:** signature-extractor-app
**Date:** 2026-08-12
**Status:** Active

## 1) Audit Method
- Evidence-first: each task below links to concrete files and commands we should add to future runs.
- Test-data quality criteria: **privacy, realism, reproducibility, coverage**.
- Risk-first priorities:
  - **P0**: Data governance or security/privacy risk
  - **P1**: Missing reliability signal for reproducibility/coverage
  - **P2**: Gaps in observability or maintainability
  - **P3**: Nice-to-have enhancements

## 2) Current Test-Data Surface (Observed)
- Fixtures and synthetic artifacts are concentrated in `desktop_app/tests/fixtures` and `tools/` scripts.
- Core sources referenced today:
  - `desktop_app/tests/fixtures/sample.pdf`
  - `desktop_app/tests/fixtures/signed_output.pdf`
  - `desktop_app/tests/fixtures/auto_detect_golden.json`
  - `desktop_app/tests/fixtures/native_form_benchmark.pdf`
  - `desktop_app/tests/fixtures/checkbox_heavy_benchmark.pdf`
  - `desktop_app/tests/fixtures/mixed_layout_benchmark.pdf`
  - `desktop_app/tests/fixtures/scan_like_benchmark.pdf`
  - `desktop_app/tests/fixtures/test_signature.png`
  - synthetic/fallback source in `desktop_app/resources/sample_signature.py`
  - benchmark tooling in `tools/generate_parser_benchmark_corpus.py`, `tools/generate_native_form_fixture.py`, `tools/compare_parser_baselines.py`

## 3) Task Ledger

### Execution Sessions

Each session updates the board directly with status and evidence.

- Session `2026-08-12T01` (this turn): initialize manifest, governance metadata, and validation scaffolding.
- Last update: 2026-08-12

### Active Tasks

- [x] **T-001 (P1)** Create a canonical test-data manifest for fixture inventory and metadata.
  - Deliverable: `docs/test_data_manifest.md` with file-level purpose/source/privacy/reproducibility metadata.
  - Status: **Done**
  - Acceptance: manifest exists and is kept alongside fixture changes.
  - Last updated: 2026-08-12

- [x] **T-002 (P1)** Define and enforce a reproducibility contract for generated datasets.
  - Deliverable: seed/version fields in dataset generation workflows (`tools/generate_parser_benchmark_corpus.py`, `tools/generate_native_form_fixture.py`) and recorded run notes.
  - Acceptance: deterministic reruns produce matching outputs when inputs/seeds are fixed.
  - Status: **Done**
  - Note: Runtime execution for these scripts is dependency-gated (`PIL`, `reportlab`) in this environment.
  - Owner: Test Data Engineering
  - Last updated: 2026-08-12

- [x] **T-002A (P1)** Add lightweight manifest validation script to catch broken fixture entries.
  - Deliverable: `tools/validate_test_data_manifest.py`
  - Status: **Done**
  - Acceptance: script checks fixture existence, required columns, and markdown row integrity.
  - Last updated: 2026-08-12

- [ ] **T-003 (P1)** Add explicit privacy and source annotations for non-anonymous fixtures.
  - Deliverable: manifest columns indicating origin + redaction status and a rule on adding future fixtures.
  - Acceptance: every fixture entry declares `origin`, `contains_pii`, `redacted`.
  - Status: **Done**
  - Last updated: 2026-08-12

- [x] **T-004 (P2)** Expand dataset coverage by edge-case tags.
  - Deliverable: `edge_case_tags` for each fixture family (low contrast, clipped fields, multiple signature positions, partial occlusion, rotation skew, noisy scans).
  - Acceptance: every test flow can map fixture tags to scenario coverage.
  - Status: **Done**
  - Last updated: 2026-08-12
  - Artifact: [docs/test_data_edge_case_matrix.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/test_data_edge_case_matrix.md)

- [ ] **T-005 (P2)** Add a lightweight seed dataset review checklist for pre-commit PR hygiene.
  - Deliverable: short checklist in docs for adding/updating fixtures.
  - Acceptance: reviewers can quickly verify privacy/reproducibility before merge.
  - Status: **Done**
  - Last updated: 2026-08-12
  - Artifact: [docs/test_data_review_checklist.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/test_data_review_checklist.md)

- [x] **T-006 (P0)** Confirm and document PII handling for legacy signature-like imagery names/metadata (example filename patterns indicate personal-like naming).
  - Deliverable: decision entry in manifest and migration strategy if sensitive source is confirmed.
  - Acceptance: explicit owner + remediation path (replace or redact).
  - Status: **Done**
  - Owner: Test Data Engineering
  - Last updated: 2026-08-12
  - Decision log: [docs/test_data_privacy_decisions.md](docs/test_data_privacy_decisions.md)

### Deferred or Follow-up Tasks

- [x] **F-001 (P2)** Add a dataset coverage matrix linking fixture tags to test modules (`desktop_app/tests/test_pdf_field_detection.py`, `desktop_app/tests/test_pdf_bulk_field_detection.py`, `tests/test_integration_workflows.py`).
  - Last updated: 2026-08-12
- [x] **F-002 (P2)** Add checksum/lock records for large fixture family outputs for drift detection.
  - Last updated: 2026-08-12
- [x] **F-003 (P3)** Add a `docs/test_data_playbook.md` with contributor templates.
  - Status: **Done**
  - Last updated: 2026-08-12
- [x] **F-004 (P0)** Replace legacy signature source asset with synthetic/anonymized equivalent and rename to neutral identifier.
  - Acceptance: no filename indicates real identity, no unresolved PII assumptions.
  - Owner: Test Data Engineering
  - Last updated: 2026-08-12
  - Status: **Done**
  - Artifact updates:
    - `desktop_app/resources/sample_signature.py`
    - `desktop_app/resources/signature_template_synthetic_512.jpg`
    - `docs/test_data_manifest.md`
    - `desktop_app/tests/fixtures/auto_detect_golden.json`
    - `desktop_app/tests/test_extractor.py`
    - `desktop_app/tests/test_workflow_engine.py`
    - `scripts/*.py` calling signature fixtures
    - `build-tools/*.spec`

- [x] **F-005 (P1)** Establish project-venv authority and prevent system-Python dependency drift.
  - Deliverable: `docs/test_data_environment.md`, `tools/validate_test_data_environment.py`, and CI/build integration.
  - Acceptance: valid `.venv` passes; system Python fails with an actionable message.
  - Status: **Done**
  - Evidence: `.venv` gate passes; system-Python negative control exits 2.

- [x] **F-006 (P1)** Add deterministic extractor edge-case corpus and integration coverage.
  - Deliverable: `desktop_app/tests/fixtures/signature_edge_cases`, generator, metadata, and tests.
  - Acceptance: blank, low-contrast, tilted, noisy, and partially occluded cases are versioned and exercised.
  - Status: **Done**
  - Evidence: focused extractor/corpus tests `19 passed`; mutation probe included.

- [x] **F-007 (P2)** Restore explicit-entrypoint testability exposed by the full-suite gate.
  - Deliverable: lazy module-level `_run_profile` hooks in both explicit entrypoints.
  - Acceptance: full `.venv` suite is green without eager dependency imports.
  - Status: **Done**
  - Evidence: full suite `98 passed`.

- [x] **F-008 (P2)** Publish the contributor playbook and agent-start handoff.
  - Deliverable: `docs/test_data_playbook.md` plus links in current agent context.
  - Acceptance: another agent can reproduce environment, manifest, focused, and full-suite checks from repo docs.
  - Status: **Done**

- [x] **F-009 (P1)** Define and implement labeled-corpus evaluation for detection, localization, and multi-signature count behavior.
  - Deliverable: `tools/evaluate_signature_corpus.py`, `tests/test_signature_corpus_evaluation.py`, synthetic labels, and `docs/test_data_evaluation.md`.
  - Acceptance: metrics are explicit, reproducible, one-to-one at a documented IoU threshold, and do not claim AP without confidence-ranked candidates.
  - Status: **Done**
  - Evidence: evaluator ran against six synthetic cases; multi-signature limitation surfaced as instance recall `0.8333` and exact count accuracy `0.8333`.

- [x] **F-010 (P1)** Add annotation readiness, geometry, hash, coverage, and split-leakage validation.
  - Deliverable: `tools/validate_signature_corpus.py` and `tests/test_signature_corpus_validation.py`.
  - Acceptance: synthetic regression corpus passes; held-out mode fails without a test/held-out split.
  - Status: **Done**

- [x] **F-011 (P1)** Research external signature corpus candidates and record intake decisions.
  - Deliverable: `docs/test_data_corpus_research.md` and privacy decision `TD-PII-002`.
  - Acceptance: candidate license, split design, provenance uncertainty, and owner/approval path are documented.
  - Status: **Done**
  - Decision: no external corpus downloaded or added.

- [ ] **F-012 (P1)** Harden auto-detection's multi-box scored API against independently annotated multi-signature data.
  - Owner: Extractor Engineering
  - Why: current multi-signature instance recall and count accuracy are structurally capped; AP is unsupported without ranked confidence.
  - Acceptance: API contract returns zero or more boxes with confidence, deterministic ordering, duplicate suppression, and tests for no-signature, one-signature, and multi-signature inputs.
  - Progress: `auto_detect_signatures()` and all-points AP are implemented; the current external corpus is single-box and cannot validate multi-instance behavior.
  - Closure trigger: an independently annotated multi-signature evaluation reports multi-instance recall and calibrated precision-recall behavior without unacceptable false positives.

- [ ] **F-013 (P1)** Intake the user-approved external corpus for controlled internal evaluation, while retaining a separate independent held-out corpus as the production-evidence requirement.
  - Owner: Test Data Engineering with product/legal/privacy review
  - Why: synthetic labels establish regression behavior but not population quality.
  - Acceptance: source/license/provenance/retention record, raw images outside Git, no redistribution, no leakage across source splits, aggregate validation metrics, and an explicit privacy/legal gate before production deployment. Closure as production evidence still requires an independently annotated held-out corpus and `validate_signature_corpus.py --require-held-out`.
  - Closure trigger: held-out report includes per-stratum presence, instance, IoU, and count metrics without tuning on the held-out split.

## 4) Evidence and Signals (to capture next)
- Commands to run per task update:
  - `rg -n "fixtures/" desktop_app/tests tools docs`
  - `python`/`ruff` or targeted script that reads manifest and validates required columns.
- Manual checks:
  - Review fixture naming and visual content for embedded identities.
  - Validate that each fixture maps to at least one integration or acceptance test.

### Implicit Tasks Discovered

- [x] **IT-001 (P1)** Standardize generator seeds with a documented `--seed` argument and versioned source metadata in both generator scripts.
- [x] **IT-002 (P2)** Add `fixtures/` diff check in PR/review scripts so fixture churn is intentional.
  - Status: **Done**
  - Artifact: [tools/validate_fixture_changes.py](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/tools/validate_fixture_changes.py)
- [x] **IT-003 (P2)** Add hash fingerprints to manifest for selected large PDFs to detect accidental drift.
  - Last updated: 2026-08-12
- [x] **IT-004 (P1)** Add a reviewer-facing one-page checklist for privacy decisions (no PII, known redaction, migration plan).
  - Last updated: 2026-08-12
- [x] **IT-005 (P1)** Make generated signature fixture assets reproducible and visible to version control.
  - Deliverable: deterministic generators, manifest hashes, canonical image assets, and `.gitignore` allowlists for edge-case and benchmark PNGs.
  - Acceptance: `validate_test_data_manifest.py` validates every listed file, direct SHA-256 comparison reports no mismatches, and `validate_signature_corpus.py` passes in the canonical Python 3.13 environment.
  - Evidence: 2026-08-13, manifest `29 entries validated`, corpus `OK`, zero hash mismatches.

## 5) Next Decision Points
- Whether test artifacts should be split into:
  - **Stable golden fixtures** vs **ephemeral generated artifacts**
  - **Privacy-grade production-like fixtures** vs **stress-only synthetic fixtures**
- Whether `desktop_app/tests/fixtures` should be considered canonical dataset root for all parser/form tests.

## 6) Progress Log (append-only)

- 2026-08-12T00:00Z - T-001 started and completed by creating `docs/test_data_manifest.md`.
- 2026-08-12T00:20Z - T-002 marked In Progress; a concrete deliverable (validation automation) added as T-002A.
- 2026-08-12T00:35Z - T-002A completed with `tools/validate_test_data_manifest.py`.
- 2026-08-12T00:45Z - T-002 completed with reproducibility metadata hooks added to generator scripts.
- 2026-08-12T00:48Z - T-002 execution validation blocked in this environment due missing runtime deps (`PIL`, `reportlab`).
- 2026-08-12T00:55Z - manifest validator passes after updating reproducibility metadata and fixing table parsing-safe fields.
- 2026-08-12T01:10Z - T-003 completed; manifest now captures origin/contains_pii/redacted and validator enforces schema.
- 2026-08-12T01:22Z - T-005 completed with `docs/test_data_review_checklist.md`; validator remains clean.
- 2026-08-12T01:35Z - T-006 decision drafted in `docs/test_data_privacy_decisions.md`; hash tracking added via `sha256` columns.
- 2026-08-12T01:42Z - T-006 decision completed; F-004 added for mandatory signature source replacement.
- 2026-08-12T01:50Z - IT-002 completed with `tools/validate_fixture_changes.py`.
- 2026-08-12T01:58Z - T-004/F-001 completed with `docs/test_data_edge_case_matrix.md`.
- 2026-08-12T02:12Z - F-004 completed by replacing legacy `512px-Mohammad_Rafiquzzaman_signature.jpg` with neutral synthetic `desktop_app/resources/signature_template_synthetic_512.jpg` and updating references.
- 2026-08-12T02:20Z - Legacy `512px-Mohammad_Rafiquzzaman_signature.jpg` file removed from active test-data surface; updated `docs/test_data_audit.md` to mark `F-004` complete.
- 2026-08-12T12:45Z - F-005 completed: confirmed `.venv` contains Pillow/OpenCV/PySide6, added the environment gate, and recorded the system-Python negative control.
- 2026-08-12T12:50Z - F-006 completed: generated five deterministic synthetic signature edge cases with seed `20260812`, added manifest hashes, and exercised detection plus RGBA processing.
- 2026-08-12T12:55Z - Full `.venv` suite first exposed two explicit-entrypoint patchability failures; F-007 repaired the canonical lazy hook and the suite passed `98` tests.
- 2026-08-12T13:00Z - F-008 completed with the contributor playbook and agent-start handoff. Historical documents retaining the legacy filename are intentionally preserved as historical evidence, not active test data.
- 2026-08-12T13:20Z - F-009 completed: added explicit presence, instance, IoU, and count metrics; ran the six-case synthetic baseline and documented why AP remains unsupported.
- 2026-08-12T13:35Z - F-010 completed: added annotation geometry, image/hash, coverage-tag, and held-out split readiness validation.
- 2026-08-12T13:40Z - F-011 completed: researched the Ultralytics candidate and recorded the privacy, provenance, license, and split limitations.
- 2026-08-12T14:00Z - User approved internal, non-redistributive evaluation; F-013 moved to controlled intake with raw data outside Git and production/legal review still open.
- 2026-08-12T14:20Z - Downloaded and checksum-verified the Ultralytics archive outside Git, converted 178 YOLO cases, and recorded the baseline/improved benchmark in `docs/test_data_external_evaluation_2026-08-12.md`. The color-aware production path improved localization from 0/178 to 126/178 at IoU 0.5; independent held-out evidence and legal/privacy review remain open.
- 2026-08-12T15:00Z - F-012 progressed: added ranked `SignatureCandidate` output, bounded multi-candidate defaults, all-points AP, and focused multi-box tests. Independent multi-signature evidence and score calibration remain open.
- 2026-08-12T15:20Z - Added legal/privacy research and a read-only storage audit. Internal use is still not legal/privacy approval; duplicate `venv` and cache cleanup candidates are classified but untouched pending explicit preservation-safe approval.
- 2026-08-12T16:00Z - Repaired the concurrent desktop extraction indentation defect, corrected checkout empty-href behavior, made the browser workspace use one main landmark, and verified the full repository suite at `126 passed`.
- 2026-08-12T13:45Z - Added F-012 and F-013 as explicit open tasks; the current blocker is API/corpus evidence, not missing regression tests.
- 2026-08-13T13:50Z - IT-005 completed: restored the deterministic synthetic signature template, edge-case PNGs, and benchmark PNGs; added image ignore allowlists; validated 29 manifest entries, zero hash mismatches, and the synthetic corpus in the Python 3.13 project environment.
