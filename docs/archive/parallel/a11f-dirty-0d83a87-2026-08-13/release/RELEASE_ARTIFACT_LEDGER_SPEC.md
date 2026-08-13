# Release artifact ledger specification

Status: accepted implementation contract, 2026-08-13

The release workflow must produce one machine-readable ledger for every tagged
release. The ledger is the release evidence boundary for packaged artifacts. A
file existing in the build workspace proves only that a file exists. It does
not prove that the artifact was signed, launched successfully, or can be
rolled back.

Before ledger generation, the tagged release job runs the dependency-free
`tools/audit_public_surface.py --strict` claim gate. This verifies source route
parity, canonical claim markers, and checkout asset ownership before artifact
evidence is published. It does not replace the deployed probe or legal review.

## Canonical producer

`tools/release_artifact_ledger.py` is the only producer and validator. The
GitHub Actions release job in `.github/workflows/build-all-platforms.yml` must
invoke it after all platform artifacts have been downloaded and before the
release is published.

The JSON document uses schema version `signkit.release-ledger.v1` and contains:

- release tag, source SHA, release URL, and generation timestamp;
- an explicit rollback artifact identifier;
- one record per artifact with name, platform, architecture, path, byte count,
  SHA-256 digest, signing status, smoke status, and references to the signing
  and smoke evidence.

## Status contract

Signing status is one of `signed`, `not_applicable`, `not_verified`,
`not_recorded`, or `failed`. Smoke status is one of `passed`,
`not_applicable`, `not_run`, or `failed`.

The strict release gate accepts an artifact only when signing is `signed` or
`not_applicable`, smoke is `passed` or `not_applicable`, and
`rollback_artifact` identifies a recoverable prior release. Both evidence
reference fields must be non-empty. The gate must fail for `not_verified`,
`not_recorded`, `not_run`, or `failed`; the workflow must not infer a positive
status from a filename, checksum, or build success.

## Evidence boundary

The ledger provides Tier 1 static release metadata and Tier 2 targeted
validation of its schema and readiness rules. It becomes Tier 3 only when the
workflow runs successfully with real platform artifacts and the platform smoke
checks are recorded. It is Tier 4 or Tier 5 evidence only after a human or
production-like launch and rollback observation is linked to the release.

The current repository does not yet provide signing/notarization secrets,
cross-platform launch smoke, or a recoverable prior-release identifier to the
workflow. Until those inputs are supplied, a tagged release is intentionally
blocked by the strict gate. This is a release control, not evidence that the
artifacts are signed or deployable.

## CLI example

```bash
python3 tools/release_artifact_ledger.py \
  --output ./artifacts/release_artifact_ledger.json \
  --markdown-output ./artifacts/release_artifact_ledger.md \
  --release-tag v1.2.3 \
  --source-sha "$GITHUB_SHA" \
  --release-url "https://github.com/example/signkit/releases/tag/v1.2.3" \
  --rollback-artifact v1.2.2-artifacts \
  --artifact "SignKit macOS|macOS|arm64|./artifacts/SignKit.dmg|signed|passed|attestation://signkit-v1.2.3|smoke://signkit-v1.2.3" \
  --require-ready
```

The markdown output is for operator review. The JSON output is the canonical
machine-readable record and should be retained with the release artifacts.

The deployment wrapper also requires the repository `.venv` interpreter for
its Python audit and deployed-probe gates. This prevents system-Python drift
from producing a false preflight result; deployment still requires the explicit
`DEPLOY_CONFIRM=signkit-landing` confirmation and a passing target probe.
