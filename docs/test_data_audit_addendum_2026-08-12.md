# Test Data and Runtime Audit Addendum: 2026-08-12

This addendum records the continuation pass for the local SignKit desktop app and web workspace. It is append-only evidence for the test-data engineering ledger and does not replace earlier audit findings.

## Work ledger

| ID | Work item | State | Evidence or closure condition |
|---|---|---|---|
| TD-021 | Restore the canonical project runtime | Closed for this pass | Recreated `.venv` with Python 3.13 and installed the pinned requirements, including Pillow, OpenCV, PySide6, NumPy, requests, and bcrypt. |
| TD-022 | Repair the web workspace projection import boundary | Closed for this pass | `backend/app/routers/workspace.py` now imports `project_workspace_execution` from the canonical passport service. Full test collection is restored. |
| TD-023 | Re-run data and cross-surface validation | Closed at S1 | Environment, manifest, and corpus validators passed; focused regression passed 38 tests; full suite passed 130 tests. Passing tests are S1 evidence, not proof of defect sensitivity. |
| TD-024 | Preserve runtime and test-data privacy boundaries | Closed for this pass | Storage audit made no changes. `.venv` and the private external corpus are protected; legacy `venv` and caches remain review-only. |
| TD-025 | Establish independent multi-signature evaluation corpus | Open | Acquire or create a consented, licensed, privacy-reviewed corpus with multiple signatures, negative pages, subject-disjoint splits, and frozen annotations. Closure requires held-out precision, recall, AP, localization, and count metrics. |
| TD-026 | Obtain legal/privacy approval for external corpus use | Open | The private AGPL corpus remains internal research-only. Closure requires documented approval before production deployment, external sharing, publication, or network-accessible use. |
| TD-027 | Raise test sensitivity beyond S1 | Open | Add deliberate mutation or fault-injection checks for extraction, workspace projection, idempotency, and fallback behavior. Closure requires S2 or S3 evidence for each high-risk defect contract. |

## Commands and outcomes

- `./.venv/bin/python tools/validate_test_data_environment.py --repo-root .`: passed.
- `./.venv/bin/python tools/validate_test_data_manifest.py --repo-root .`: 16 entries validated.
- `./.venv/bin/python tools/validate_signature_corpus.py --repo-root .`: passed.
- Focused data, passport, topology, launch, and claim tests: `38 passed in 0.37s`.
- Full project suite: `130 passed in 5.65s`.
- `./.venv/bin/python tools/audit_test_data_storage.py --repo-root .`: passed; no files deleted or modified; latest observed free space was `45.3 GiB`.

## Environment recovery decision

The canonical `.venv` was absent during this continuation pass. The alternate `venv` was not adopted because its `pyvenv.cfg` described Python 3.11 while its executable resolved to Python 3.13, making it an unsafe source of reproducible evidence. The canonical `.venv` was rebuilt from `desktop_app/requirements.txt` using the installed Python 3.13 interpreter. Future agents must use `.venv` and must not silently substitute `venv` or system Python.

## Remaining confidence boundary

The passing suite demonstrates that the current deterministic contracts execute under the canonical runtime. It does not establish production population performance, subject-level generalization, legal approval, or S2/S3 defect sensitivity. Those claims remain intentionally open under TD-025 through TD-027.
