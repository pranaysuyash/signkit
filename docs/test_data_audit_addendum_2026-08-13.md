# Test Data Audit Addendum: 2026-08-13

## Work ledger update

| ID | Work item | State | Evidence or closure condition |
|---|---|---|---|
| TD-027 | Raise test sensitivity beyond S1 | Closed for this stage | Expanded `tools/mutation_check.py` passes `5/5 mutants killed` for bounded extraction, grayscale fallback, workspace replay, ownership, and passport privacy-boundary invariants. Further mutants can be added as new high-risk contracts land. |
| TD-028 | Preserve a reusable S3 gate | Closed for this stage | Manifest, restoration safety, broken-mutant classification, usage, and evidence limits are documented in `docs/test_data_sensitivity_2026-08-13.md`. |
| TD-029 | Make backend mutation evidence reproducible | Closed for this stage | `httpx==0.28.1` and the concurrent `alembic==1.16.4` pin are installed in `.venv`; `tools/validate_test_data_environment.py --backend` passes and checks only the selected environment. |
| TD-030 | Build a subject-disjoint synthetic held-out benchmark | Closed for this stage | Generated and validated 12 synthetic subject-disjoint pages. The three-page/four-instance held-out test slice scored presence and instance precision/recall `1.0/1.0`, count accuracy `1.0`, AP `1.0`, and mean IoU `0.7843`; limitations are documented separately. |
| TD-031 | Research and govern real/public dataset candidates | In progress | Added the 9-entry machine-readable registry, validator, primary-source research brief, and conservative decisions. Next closure requires legal/privacy review and a named approval for any candidate acquisition beyond the existing private Ultralytics artifact. |

## Implementation scope

- Added one reusable tool: `tools/mutation_check.py`.
- Added one sensitivity evidence record: `docs/test_data_sensitivity_2026-08-13.md`.
- Pinned backend test dependencies in `desktop_app/requirements.txt` and made
  backend preflight selection-aware.
- No production data, private corpus files, route definitions, or runtime
  dependencies were changed.

## Verification

- `./.venv/bin/python tools/validate_test_data_environment.py --repo-root . --backend`: passed.
- `./.venv/bin/python tools/mutation_check.py`: `5/5 mutants killed`.
- Focused local/web/backend suite: `56 passed in 0.77s`.
- Full suite: `136 passed in 5.17s`.
- Synthetic benchmark generator and subject-disjoint validator: passed.
- Synthetic held-out test evaluation: 3 pages, 4 instances, mean IoU `0.7843`, AP `1.0`.
- Storage audit: `27.9 GiB` free observed; no files deleted or modified.
- Dataset registry validator: passed; no candidate is marked `approved_internal`.
- Research-focused registry/corpus tests: `11 passed in 0.39s`.
- Full suite after registry work: `145 passed in 10.64s`.

## Next closure criteria

TD-027 closes only after the gate passes and additional mutants cover the
grayscale fallback contract, the authenticated workspace route binding, and a
privacy/data-boundary invariant. The gate remains complementary to the
independent held-out corpus and legal/privacy approval tasks.
