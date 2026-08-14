# Local migration recovery proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Evidence scope: disposable local Alembic recovery only

## Result

The reusable migration proof passed:

```text
./.venv/bin/python tools/run_local_migration_recovery_proof.py
status: passed
initial_head: 9c4b7e2d1a6f
rollback_target: e42b7f8c91aa
final_head: 9c4b7e2d1a6f
```

The proof uses a temporary SQLite database and never touches a project or
hosted database. It verifies that the current head creates the
`request_hash` and `result_json` fields and their index on
`workspace_execution_events`, that the latest migration can be downgraded to
the preceding ownership-receipt revision, and that re-upgrading restores the
fields.

## Sensitivity evidence

`tests/test_local_migration_recovery_proof_tool.py` runs the proof as a
subprocess and asserts the rollback target and both removal/restoration checks.
The dedicated `migration-recovery-rollback-target` mutation was killed. The
complete repository mutation manifest passed `18/18` after the extraction
smoke and migration sensitivity gates were included.

## Boundary and closure

This closes the local forward, rollback, and re-upgrade contract for the
current SQLite migration chain. It does not prove data-preserving rollback on
the production database, backup restoration, migration locking under multiple
workers, target schema permissions, hosted rollout, or operator recovery after
a live deployment failure. Those remain open under `L0-09`, `L0-03`, and
`RECON-07`.

## Source paths

- `tools/run_local_migration_recovery_proof.py`
- `tests/test_local_migration_recovery_proof_tool.py`
- `backend/alembic/versions/9c4b7e2d1a6f_add_document_inspection_receipt_fields.py`
- `backend/alembic/versions/e42b7f8c91aa_add_extraction_asset_ownership_receipts.py`
- `tools/mutation_check.py`
- `tools/README.md`
- `docs/QA_RESULTS.md`
