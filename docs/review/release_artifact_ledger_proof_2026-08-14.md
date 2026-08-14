# Release artifact ledger identity proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Evidence scope: local release-gate contract only

## Decision

The release artifact ledger now fails closed when its source identity is not a
40- or 64-character lowercase hexadecimal commit identifier. It also rejects
duplicate artifact names and duplicate artifact paths within one ledger. These
are identity invariants, not cosmetic validation: a release record must not be
able to point at an ambiguous source or silently represent two platform
records as one artifact.

The schema and release workflow remain local contract surfaces. No real
platform artifact, signing or notarization attestation, launch smoke output,
rollback artifact, hosted deployment, provider activation, or remote CI run was
created by this proof.

## Red-first and sensitivity evidence

The first red-first run added source-identity and duplicate-name cases to the
existing ledger suite. Before implementation, the suite reported `3 passed,
2 failed`; the failures were the intended missing invariants. A path-identity
case was then added, and the corrected implementation passed `6 passed`.

The three new mutation probes all killed the intended defect:

```text
release-ledger-source-identity          1/1 killed
release-ledger-duplicate-name-identity 1/1 killed
release-ledger-duplicate-path-identity 1/1 killed
```

This is S3 mutation evidence for the three new ledger invariants. The complete
repository mutation manifest then passed `16/16`, including these three new
probes. It must be rerun when the shared mutation harness or any covered source
changes.

## Commands and outcomes

| Check | Outcome | Tier | Boundary |
| --- | --- | --- | --- |
| `./.venv/bin/python -m pytest tests/test_release_artifact_ledger.py -q` | `6 passed` | S2 contract | Local parser and validator behavior only |
| `TMPDIR=/var/tmp ./.venv/bin/python tools/mutation_check.py --only release-ledger-source-identity` | `1/1 killed` | S3 mutation | One source-identity mutation |
| `TMPDIR=/var/tmp ./.venv/bin/python tools/mutation_check.py --only release-ledger-duplicate-name-identity` | `1/1 killed` | S3 mutation | One duplicate-name mutation |
| `TMPDIR=/var/tmp ./.venv/bin/python tools/mutation_check.py --only release-ledger-duplicate-path-identity` | `1/1 killed` | S3 mutation | One duplicate-path mutation |
| `TMPDIR=/var/tmp ./.venv/bin/python tools/mutation_check.py` | `16/16 killed` | S3 mutation | Complete repository sensitivity manifest |
| `git diff --check` | pass | S1 hygiene | Whitespace only |

## Closure status

This closes the local identity-hardening subtask under `L0-05` and `L0-14`,
but those P0 backlog items remain in progress. Full closure still requires a
real per-platform release artifact set, source tag and release URL, checksum
records, distribution signing or notarization evidence, launch smoke output,
an independently recoverable rollback artifact, a strict workflow run on the
remote runner, and review of the final public claim surface. Hosted and
provider evidence are not inferred from this local proof.

## Source paths

- `tools/release_artifact_ledger.py`
- `tests/test_release_artifact_ledger.py`
- `tools/mutation_check.py`
- `docs/release/RELEASE_ARTIFACT_LEDGER_SPEC.md`
- `docs/QA_RESULTS.md`
- `docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`
