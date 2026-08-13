# Test Data Environment Contract

Status: active
Owner: Test Data Engineering
Last updated: 2026-08-12

This document records the runtime authority for test-data and extractor checks. Read it before diagnosing missing Python modules or installing dependencies.

## Verified environment finding

The initial import failure occurred under the system `python3`, which did not provide `PIL`. The project environments were then checked directly:

- `./.venv/bin/python` provides `PIL` (Pillow), `cv2` (OpenCV), and `PySide6`.
- `./venv/bin/python` also provides `PIL`, `cv2`, and `PySide6`.
- Focused extractor validation with `./.venv/bin/pytest -q desktop_app/tests/test_extractor.py` passed: `8 passed in 0.45s`.
- Test-data manifest validation with `python3 tools/validate_test_data_manifest.py --manifest docs/test_data_manifest.md --repo-root .` passed: `Manifest OK: 9 entries validated.`

The focused extractor result is evidence tier 2 and test sensitivity S1: the targeted tests passed, but they have not been deliberately broken to demonstrate S3 enforcement. This is not full application, packaging, or production-like corpus evidence.

## Agent execution protocol

1. Prefer `./.venv/bin/python` and `./.venv/bin/pytest` for this checkout.
2. If `.venv` is unavailable or incomplete, inspect `./venv/bin/python` before changing dependencies.
3. Do not install packages into system Python because a project test was launched with the wrong interpreter.
4. Do not edit dependency manifests or install packages until both project environments have been checked and the missing module is confirmed in the selected project runtime.
5. For build tooling that invokes bare `python`, put the preferred environment first: `PATH="$PWD/.venv/bin:$PATH"`.
6. Record the interpreter path, import check, and exact test command in the task ledger whenever an environment issue affects validation.

Useful import check:

```bash
./.venv/bin/python -c "import PIL, cv2, PySide6; print('project test-data modules available')"
```

## Privacy and reproducibility guardrails

- The extractor fixture uses the synthetic neutral signature asset documented in `docs/test_data_manifest.md`.
- The removed identity-indicative signature asset must not be restored as a test fixture or copied into new scripts.
- Existing project dependencies are reused; unnecessary installation is avoided to reduce uncontrolled environment drift.
- Test runs must identify the interpreter so a passing or failing result can be reproduced by another agent.

## Tracked task state

- `F-004`: synthetic replacement and legacy fixture removal, complete; see `docs/test_data_audit.md`.
- `F-005`: project-venv authority and dependency diagnosis, complete; this document is the durable handoff.
- `F-006`: project-venv gate and CI workflow, complete in `tools/validate_test_data_environment.py`, `build-tools/build_macos.sh`, and `.github/workflows/test-data.yml`.
- `F-014`: backend test-runtime preflight, implementation complete in `tools/validate_test_data_environment.py --backend`; it validates Alembic/FastAPI/httpx/SQLAlchemy/multipart/JWT dependencies and detects a stale pytest shebang in the selected environment before backend evidence is collected. A repaired canonical environment is still required for a green preflight; the alternate `venv` remains review-only.
- `F-007`: deterministic edge-case corpus, integration checks, and dynamic mutation probe, complete in `tools/generate_signature_edge_case_fixtures.py` and `desktop_app/tests/test_signature_edge_cases.py`.
- `F-008`: contributor playbook and agent-start handoff, complete in `docs/test_data_playbook.md` and `docs/context/agent-start/`.
- `F-009`: labeled corpus evaluator and synthetic multi-signature baseline, complete in `tools/evaluate_signature_corpus.py`, `tests/test_signature_corpus_evaluation.py`, and `docs/test_data_evaluation.md`.
- `F-010`: annotation readiness gate and split-leakage checks, complete in `tools/validate_signature_corpus.py` and `tests/test_signature_corpus_validation.py`.
- `F-011`: external corpus/privacy research, complete in `docs/test_data_corpus_research.md`; user-approved internal-only download and evaluation are now in progress, with raw images outside Git.
- Open `F-012`: multi-box extractor evolution, implemented but open for independent multi-signature evidence and score calibration, owned by Extractor Engineering.
- Open `F-013`: controlled external corpus intake and independent evaluation, implemented for local validation but open for legal/privacy approval and an independent held-out corpus, owned by Test Data Engineering with product/legal/privacy review.
- Storage incident: read-only audit in `tools/audit_test_data_storage.py`; duplicate `venv`, `.mypy_cache`, and `.pytest_cache` are classified candidates, but no cleanup is authorized by this audit.
- Remaining external evidence: hosted CI execution, an approved independently annotated corpus, and calibrated candidate scores. The local API contract now emits multiple scored candidates, and the full local suite passes `126 passed`.

## Addendum (2026-08-13): backend runtime and hosted smoke

- The backend preflight now passes in the repaired Python 3.13 project environment.
- `tools/run_extraction_hosted_smoke.py` passed after applying the full Alembic migration chain through `e42b7f8c91aa` against a temporary SQLite database.
- The environment repair restored pip with `ensurepip`, installed `alembic==1.16.4`, and regenerated the pytest launcher with the selected interpreter.
