# ADR-0149: Make First-Party Test Discovery Canonical

Date: 2026-08-13
Status: accepted for local CI and developer verification
Owner: Product and engineering

## Context

The root `pytest.ini` selected only `tests/`. A root run collected 181 tests,
while the checkout also contained 291 backend and desktop tests. The CI
workflow invoked a small hand-picked subset of those suites. This created a
silent regression boundary: a test could exist, pass when called explicitly,
and still be absent from the normal release command.

The first explicit run of the omitted suites collected 291 tests and found
three failures in `desktop_app/tests/test_pdf_form_fields.py`. Those tests use
PyMuPDF, which is intentionally declared in
`desktop_app/requirements-pymupdf-optional.txt` and is not part of the base
runtime. The tests were missing an explicit optional-dependency skip.

The same expanded run exposed repeated logging errors from
`SignatureExtractor.__del__` after interpreter logging shutdown. Finalization
must clear sensitive state without writing to a closed logging handler.

## Decision

1. Configure `pytest.ini` to discover `tests`, `backend/tests`, and
   `desktop_app/tests` by default.
2. Make the native-form test module skip with an explicit `fitz` import guard
   when the optional PyMuPDF capability is not installed. The optional
   capability remains documented and is not silently treated as available.
3. Change the CI release matrix to run the canonical default collection rather
   than a hand-maintained list of selected paths.
4. Make destructor cleanup silent while preserving normal explicit cleanup
   logging. Add a regression test for the interpreter-shutdown boundary.

## Alternatives considered

### Keep the hand-picked CI list

Rejected. It preserves the exact coverage gap that this audit found and makes
future test additions invisible unless a maintainer remembers to edit CI.

### Add a second test runner or parallel pytest configuration

Rejected. It creates another source of truth for collection and increases the
risk that local and CI evidence diverge.

### Install PyMuPDF into every base environment

Rejected for this change. Native PDF form editing is an optional capability,
already separated into its own requirements file. Making it mandatory would
increase the base install and packaging surface without a product decision.

## Evidence and acceptance

- Before the change, root collection was `181 tests collected`.
- Before the optional skip, the omitted suites were `285 passed, 3 skipped,
  3 failed`; every failure was `ModuleNotFoundError: No module named 'fitz'`.
- After the change, root collection is `478 tests collected` with one
  explicit PyMuPDF skip.
- Full local execution passes `475 passed, 4 skipped`.
- The destructor regression test failed under a deliberate reversion and
  passed after the fix, providing S2-style sensitivity evidence.

The remaining skips are visible and bounded: native form tests require the
optional PyMuPDF capability, and three Qt tests require an event loop for
`QTimer.singleShot` callbacks. Neither is converted into a false pass.

## Operational and rollback path

The canonical command is:

```bash
QT_QPA_PLATFORM=offscreen \
SIGNKIT_DATA_DIR="$PWD/.codex-test-tmp/full-first-party-suite" \
DATABASE_URL="sqlite:///$PWD/.codex-test-tmp/full-first-party-suite.db" \
JWT_SECRET='test-only-secret-that-is-at-least-32-bytes' \
./.venv/bin/pytest -q
```

If collection fails, first inspect the explicit skip and dependency report.
Do not remove a suite from `testpaths` to make the command green. A future
install profile that includes `desktop_app/requirements-pymupdf-optional.txt`
should turn the PyMuPDF skip into three exercised tests.

## Anything else?

Yes. The expanded collection is local evidence only. It does not close the
hosted migration, remote CI runner, provider, signed-artifact, device, or
assistive-technology gates. Those remain separate PO backlog items.
