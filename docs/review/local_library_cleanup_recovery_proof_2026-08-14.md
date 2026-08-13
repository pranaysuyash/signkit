# Local library cleanup recovery proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Scope: local desktop library deletion and explicit cleanup recovery only

## Question

Can an operator recover a deletion whose image was removed but whose JSON
sidecar cleanup did not complete, without a silent retry, path escape, or
false completion claim?

## Implementation contract

`desktop_app/library/storage.py` records a metadata-only deletion receipt for
each library deletion. An incomplete receipt retains the image basename,
derived sidecar basename, cleanup status, and timestamps, but no document
bytes. `incomplete_deletion_count()` exposes whether an explicit repair action
is needed.

`desktop_app/views/main_window_parts/extraction.py` exposes `Repair Cleanup`
only when incomplete receipts exist. The control invokes
`recover_incomplete_deletions()` only after an operator action, refreshes the
library, reports remaining unresolved items, and keeps the repair action
available when recovery is incomplete. There is no background or deletion-time
retry of a failed cleanup.

The recovery path accepts only basename fields from a receipt and resolves the
candidate through the local library boundary. It removes regular sidecar
files inside that boundary, marks the receipt complete atomically, and records
`recovered_at`. Missing sidecars are already clean. Directories, malformed or
ambiguous receipts, symlink escapes, permission failures, and receipt-write
failures remain incomplete.

## Evidence

Command:

```text
./.venv/bin/python -m pytest tests/test_library_deletion_contract.py tests/test_operator_content.py desktop_app/tests/test_main_window_logic.py -q
```

Result: `37 passed, 3 skipped`.

The tests prove:

1. A normal image plus JSON sidecar deletion records a complete metadata-only
   receipt.
2. A simulated sidecar deletion failure removes the primary image, returns
   `cleanup_incomplete`, retains the sidecar, and creates an incomplete
   receipt.
3. The explicit recovery call removes the retained sidecar, atomically marks
   the receipt complete, records `recovered_at`, and reports zero remaining
   items.
4. A sidecar directory is not removed or falsely marked complete.
5. A library item outside the library boundary is not deleted.
6. The extraction surface keeps `Repair Cleanup` disabled when no incomplete
   receipt is present, while the deletion action remains governed by explicit
   selection.
7. Operator copy distinguishes complete deletion, incomplete cleanup,
   repaired cleanup, and failed deletion without exposing raw paths or
   exception text.

## Evidence boundary and remaining gates

This is Tier 2 local contract evidence with an offscreen Qt component. It does
not prove permission-denied behavior on a real filesystem, cross-device or
provider-backed storage, recovery after application restart, packaged runtime
behavior, screen-reader behavior, or hosted deletion. Those remain separate
gates and must not be inferred from this proof.
