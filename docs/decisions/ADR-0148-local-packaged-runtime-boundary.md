# ADR-0148: Local packaged runtime boundary

- Status: accepted for local product execution
- Date: 2026-08-13
- Scope: desktop PyInstaller artifacts and their in-process local companion
- Related: ADR-0146, ADR-0147, `docs/review/local_packaging_runtime_proof_2026-08-13.md`

## Decision

The packaged desktop app owns a local companion runtime with an explicit,
user-writable configuration contract. Before importing the in-process FastAPI
backend, the desktop launcher applies the generated or explicitly supplied
`DATABASE_URL`, `JWT_SECRET`, `SIGNKIT_RUNTIME_PROFILE`, and
`SIGNKIT_HEALTH_TOKEN` values to the current process.

Release specs must never bundle a developer `.env` file. The canonical
`web/cloud_workspace/` directory is bundled as data because the local
companion is the serving boundary for `/workspace-app/` in the promoted local
product flow.

## Context

The first frozen ARM64 smoke reached the desktop UI but the in-process backend
failed settings validation because the subprocess-style prepared environment
was not applied to the current process. The same packaging specs also
conditionally copied the untracked `backend/.env`, which contained
credential-shaped configuration and was not an acceptable release input.

The backend already mounts `/workspace-app/` from `web/cloud_workspace/`, so a
desktop artifact that starts the backend without those assets silently loses a
canonical operator surface.

## Options considered

1. Bundle `backend/.env` and rely on the backend settings file lookup.
   Rejected because it copies developer configuration and makes secret
   provenance ambiguous.
2. Keep the backend subprocess-only in frozen builds.
   Rejected because the packaged artifact does not have a stable external
   interpreter or backend executable boundary.
3. Apply the prepared local contract in-process and bundle only non-secret
   application assets. Chosen because it preserves one runtime contract,
   keeps state user-writable, and makes the browser workspace available from
   the same local companion.

## Consequences and safeguards

- Local state is generated under `SIGNKIT_DATA_DIR` when supplied, otherwise
  the platform user application-data directory. It is not stored in the
  artifact.
- Explicit environment configuration remains honored, including a deliberate
  database URL, while absent local values receive SQLite and a persisted JWT
  secret.
- `.env` files remain development inputs only and are not release data.
- `web/cloud_workspace/` is an owned canonical asset path, not a second browser
  implementation or API route family.
- Ad hoc code-sign verification is useful local evidence but is not Apple
  distribution signing or notarization.
- The decision does not close Intel, Windows, Linux, clean-install, rollback,
  hosted, provider, or remote-release gates.

## Validation and rollback

- `desktop_app/tests/test_backend_manager.py` verifies the in-process
  environment contract.
- `tests/test_build_profile.py` verifies all desktop specs exclude `.env` and
  include the browser workspace assets.
- The mutation manifest kills the dedicated environment-removal mutant,
  contributing to `13/13` S3 sensitivity evidence.
- A rebuilt macOS ARM64 artifact reached `/health` with HTTP 200, served
  `/workspace-app/` with HTTP 200, passed ad hoc `codesign --verify`, created
  isolated local state, and left no listener after bounded shutdown.

Rollback is artifact-level: retain the prior release bundle and its ledger,
then distribute that prior bundle if the new artifact fails clean-machine or
operator verification. The current local proof does not claim that a
recoverable prior release or ready ledger exists yet.

## Revisit triggers

Revisit this ADR if the packaged app changes from in-process backend startup,
the local database/secret contract changes, `/workspace-app/` moves, a real
distribution-signing pipeline is introduced, or the product intentionally
separates the browser workspace from the desktop companion.
