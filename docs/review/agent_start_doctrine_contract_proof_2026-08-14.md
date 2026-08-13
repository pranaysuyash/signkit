# Agent-start doctrine contract proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Scope: shared `/Users/pranay/Projects/agent-start` wrapper and this project's generated context
Evidence tier: Tier 4 local command execution, S2 for the prior defect and S1 for the repaired behavior

## Prior defect

Before this repair, the live wrapper treated the repository's tracked
`motto_v5.md` as a legacy filename. A bounded
`agent-start --skip-index --quiet` run returned exit code `0`, selected
workspace Doctrine 6.0, rewrote six generated context files, and deleted the
tracked project-local doctrine. The Projects-root `motto_v5.md` alias was also
absent. The captured failure is recorded as `QA-39` and `RECON-26` in the
Product Owner and reconciliation records.

## Repaired contract

The wrapper now:

- selects an existing project-local `motto_v5.md` as the project doctrine;
- reports version `5`, the selected source, SHA-256, generator, and provenance;
- leaves workspace Doctrine 6.0 separate at `/Users/pranay/Projects/OPERATING_DOCTRINE.md`;
- safely creates `/Users/pranay/Projects/motto_v5.md` only when absent;
- refuses to overwrite a conflicting non-symlink or unexpected symlink;
- excludes `motto_v5.md` from destructive legacy-file cleanup;
- avoids copying a doctrine file onto itself;
- keeps full retrieval fail-closed when the shared workspace runtime is unavailable.

## Live verification

The bounded command was run twice consecutively with shared hook installation
disabled so this proof exercised only context generation:

```bash
/opt/homebrew/bin/timeout 45 env AGENT_START_INSTALL_PRECOMMIT_HOOKS=0 \
  /Users/pranay/Projects/agent-start \
  --project Data_Science/computer_vision/proj6/signature-extractor-app \
  --skip-index --quiet
```

Both runs returned `0`. On the second run:

- project motto SHA before and after: `f1ade186d46bf2e20e9eebd56ceca3a733711671471198284828482659524840`;
- `/Users/pranay/Projects/motto_v5.md` resolved to `/Users/pranay/Downloads/motto_v5.md`;
- generated context selected the repository-local `motto_v5.md`;
- generated context reported internal version `5`;
- generated context reported `project-local canonical motto_v5.md; workspace Doctrine 6.0 remains separate`;
- no project motto deletion occurred.

The generated session timestamp changed as expected. The project-local
generated context was retained because it now contains truthful source
selection and provenance. The shared workspace-memory Python interpreter and
usable `memsearch` CLI remain unavailable, so real retrieval/index health is
not claimed.

## Regression guard

`tests/test_agent_start_doctrine_contract.py` statically checks the live
wrapper's project-local selection, alias safety, and non-destructive legacy
list. This local guard is intentionally skipped when the shared wrapper is
not present in another environment. The wrapper itself remains an
unversioned shared filesystem tool, so the durable issue record and this test
are required to detect future drift.

## Preserved parallel calibration work

During the live regeneration, an untracked `calibration/` implementation was
present in the checkout. It includes detector adapters, dataset validation,
metrics, isotonic/Platt calibrators, a harness, CLI, and a deterministic
synthetic self-test. It was preserved and is now integrated with one-to-one
candidate/ground-truth matching, PDF page-index validation, and an explicit
non-held-out warning for manifests without a test split. Its self-test and
focused contracts execute successfully, but it is not accepted as a product
calibration claim. The slice remains separately tracked as `RECON-28` pending
held-out evaluation, privacy/consent governance, and threshold promotion.
