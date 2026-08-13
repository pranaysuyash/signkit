# Local packaged desktop runtime proof

Run date: 2026-08-13
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Target: macOS ARM64 standard PyInstaller bundle
Evidence boundary: local artifact only. This is not notarization, hosted
deployment, cross-platform installation, provider activation, or rollback proof.
Decision record: `docs/decisions/ADR-0148-local-packaged-runtime-boundary.md`

## Scope

This proof closes the local packaged-runtime contract needed for the current
first-principles product direction:

- the artifact must not bundle developer `.env` files or their credentials;
- the frozen desktop process must generate or reuse a user-writable JWT secret
  and SQLite database location before importing the in-process backend;
- the backend health route must become available from the packaged process;
- the canonical browser workspace served by the local companion must be present;
- the artifact must pass local ad hoc code-sign verification;
- the process must stop within the bounded smoke window without leaving the
  local companion listening on port 8001.

## Implementation

- `desktop_app/backend_manager.py` now applies the same explicit
  `DATABASE_URL`, `JWT_SECRET`, runtime profile, and health-token contract to
  the in-process server that the subprocess path already received.
- All desktop PyInstaller specs no longer include `backend/.env`.
- All desktop PyInstaller specs include the canonical
  `web/cloud_workspace/` assets so the packaged local companion can serve
  `/workspace-app/`.
- `desktop_app/tests/test_backend_manager.py` guards the frozen environment
  contract.
- `tests/test_build_profile.py` guards both no-secret-bundling and required
  workspace-asset inclusion across the release specs.

## Verification

Focused contract tests:

```text
QT_QPA_PLATFORM=offscreen ./.venv/bin/pytest -q \
  desktop_app/tests/test_backend_manager.py tests/test_build_profile.py
10 passed in 0.09s
```

Sensitivity gate:

```text
TMPDIR=/var/tmp SIGNKIT_DATA_DIR="$PWD/.codex-test-tmp/mutation-packaged-runtime" \
  ./.venv/bin/python tools/mutation_check.py
13/13 mutants killed.
```

The added `local-inprocess-backend-environment` mutant removes the environment
assignment guarded by `desktop_app/tests/test_backend_manager.py`; the test
fails against that mutation and therefore provides S3 evidence for the new
contract.

Build command:

```text
venv/bin/python build-tools/build.py \
  --build-platform darwin \
  --profile standard \
  --spec build-tools/SignatureExtractor_macOS.spec
```

The build completed with PyInstaller 6.16.0 on macOS arm64. The generated
bundle is `dist/SignKit.app`; generated `build/` and `dist/` directories remain
local ignored artifacts for review and are reproducible from the command above.

Bounded frozen smoke:

```text
QT_QPA_PLATFORM=offscreen \
SIGNKIT_DATA_DIR="$PWD/.codex-test-tmp/frozen-launch-data-3" \
SIGNKIT_PROFILE=standard \
/opt/homebrew/bin/timeout 15 \
  dist/SignKit.app/Contents/MacOS/SignKit
```

Observed local evidence:

| Check | Result | Tier |
| --- | --- | --- |
| Bundle executable is Mach-O arm64 | pass | Tier 1 |
| `codesign --verify --deep --strict dist/SignKit.app` | exit 0 | Tier 2, ad hoc verification only |
| Bundle contains `.env` or `.env.*` | absent | Tier 1 |
| Bundle contains `web/cloud_workspace/index.html` | present | Tier 1 |
| Frozen backend settings validation | no error | Tier 4 |
| Frozen `/health` request | HTTP 200 | Tier 4 |
| Frozen backend startup | `In-process backend started successfully` | Tier 4 |
| Frozen browser workspace | HTTP 200 and workspace marker | Tier 4 |
| Packaged workspace real-browser flow | `run_local_product_browser_proof.mjs` passed at 1440x900, 390x844, and 320x844 against the source canonical landing plus the packaged workspace; `run_local_workspace_bridge_browser_proof.mjs` passed against the packaged backend | Tier 4 |
| Local data root | SQLite database, secret file, and app log created under isolated root | Tier 4 |
| Bounded shutdown | timeout exit 124, no listener remained on port 8001 | Tier 4 |

The earlier frozen smoke is retained as a negative result: before this change,
the app UI started but the in-process backend failed with missing `JWT_SECRET`.
The focused environment test and the current artifact smoke provide S2-style
regression evidence for that defect: the failure was observed before the fix,
then the corrected artifact reached health-ready state.

## Cross-surface browser evidence

While the frozen ARM64 app was running on port 8001 and the canonical local
landing server was running on port 8080, these reusable browser proofs passed:

```text
SIGNKIT_LANDING_BASE_URL=http://127.0.0.1:8080 \
SIGNKIT_WORKSPACE_BASE_URL=http://127.0.0.1:8001 \
node tools/run_local_product_browser_proof.mjs

SIGNKIT_DATA_DIR="$PWD/.codex-test-tmp/frozen-browser-data-2" \
SIGNKIT_WORKSPACE_BASE_URL=http://127.0.0.1:8001 \
SIGNKIT_PYTHON=./.venv/bin/python \
node tools/run_local_workspace_bridge_browser_proof.mjs
```

The product proof passed all three viewport contracts, keyboard and pointer
state transitions, skip-link focus, reduced motion, workspace handoff, and
zero browser errors. The bridge proof passed unauthenticated `401`, missing
job `404`, owner-bound authenticated projection, retry-to-recovery behavior,
opaque receipt visibility, private-path exclusion, and no document bytes in
the browser workspace.

## Remaining release boundary

`RECON-20` is closed for this local ARM64 artifact contract. The broader
`RECON-09` and `L0-05` release gates remain open for:

- Intel macOS, Windows, and Linux build and launch evidence;
- distribution signing identity, notarization, installer integrity, and
  clean-machine installation;
- a recoverable prior release and rollback receipt;
- a source-controlled machine-readable ledger for a real release artifact;
- hosted deployment and provider-backed activation evidence.

The build warnings in `build/SignatureExtractor_macOS/warn-SignatureExtractor_macOS.txt`
are retained for release review. The current smoke proves the exercised local
path, not that every optional import or platform artifact is production-ready.
