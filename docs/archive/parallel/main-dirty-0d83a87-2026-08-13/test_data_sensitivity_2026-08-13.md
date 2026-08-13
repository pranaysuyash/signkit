# Test Data Sensitivity Evidence: 2026-08-13

## Decision

The repository now has a small, hand-curated S3 gate rather than a mutation
score. The gate mutates real source expressions, runs only the tests named by
each invariant, rejects parse or collection failures as `BROKEN`, and restores
the original source byte-for-byte after each mutant.

## Manifest

| Mutant | Invariant | Declared tests |
|---|---|---|
| `extractor-bounded-candidates` | `auto_detect_signatures()` must honor `max_candidates` and retain two independently ranked candidates in the deterministic two-signature fixture. | `tests/test_color_signature_candidate.py` |
| `workspace-replay-key-matching` | Repeating a workspace transition with the same idempotency key must not append a second event. | `backend/tests/test_workspace_service.py` |
| `extractor-grayscale-fallback` | Color detection failure must expose the explicit grayscale fallback candidate. | `tests/test_color_signature_candidate.py` |
| `workspace-owner-filter` | A user must not read or transition another owner’s workspace execution. | `backend/tests/test_workspace_router.py` |
| `passport-metadata-boundary-validation` | Passport validation must reject a document-byte boundary. | `tests/test_execution_passport_contract.py` |
| `runtime-hosted-route-exclusion` | Hosted runtime profile must not register the local document-inspection route. | `backend/tests/test_runtime_profile.py` |
| `inspection-candidate-confidence-bound` | Worker confidence outside `0..1` must be rejected at the API boundary. | `backend/tests/test_workspace_router.py` |

## Reproduction

```bash
./.venv/bin/python tools/mutation_check.py --list
./.venv/bin/python tools/mutation_check.py
```

Observed result before the latest runtime/candidate extension: `5/5 mutants
killed`. The extractor bounding and fallback-threshold mutants, workspace
replay and ownership mutants, and passport privacy-boundary mutant all caused
their declared tests to fail. The runner restored every source file after the
run.

The extended seven-mutant run below is the current dated S3 result; it covers
hosted route exclusion and the bounded worker result contract.

## Addendum: latest gate attempt (2026-08-13)

The extended seven-mutant run was first attempted with `.venv` but could not create
the first `.mutation-backup` because the root filesystem had only 221 MB free
and returned `OSError: [Errno 28] No space left on device`. No mutation sidecar
was left behind. The prior `5/5` result remains historical evidence for the
original manifest; the extended run below is the current S3 result.

After the authorized Playwright-cache-only recovery, the closure command passed
with `7/7 mutants killed`, including `runtime-hosted-route-exclusion` and
`inspection-candidate-confidence-bound`:

```bash
TMPDIR=/var/tmp .venv/bin/python tools/mutation_check.py
```

The mutation runner restored every source file after the successful run.

## Evidence boundary

This gate is S3 evidence for the two named invariants when it reports every
mutant as `killed`. It does not establish production population performance,
multi-signature recall on independent data, legal/privacy approval, or full
coverage of every extraction fallback and workspace route. Those remain open
follow-up items in the test-data ledger.

## Safety

The runner uses `.mutation-backup` sidecars and restores source in a `finally`
block. An interrupted run is recovered before the next run. It must only be
run from the canonical checkout with `.venv`; it must not be pointed at a copy
or alternate `venv` without a deliberate reproducibility decision.
