# Local packaged artifact proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Evidence scope: current macOS arm64 local artifact only

## Build

The declared build requirements were installed into the project `.venv`:

```text
pyinstaller 6.22.0
pyinstaller-hooks-contrib 2026.6
```

The current standard bundle was built with:

```bash
./.venv/bin/python build-tools/build.py \
  --build-platform darwin \
  --profile standard \
  --spec build-tools/SignatureExtractor_macOS.spec \
  --no-clean
```

PyInstaller completed successfully on macOS arm64. The generated app and DMG
remain ignored local build outputs:

| Artifact | Observation |
| --- | --- |
| `dist/SignKit.app/Contents/MacOS/SignKit` | Mach-O arm64 |
| App executable SHA-256 | `53574f260addaf3e8d55630090fc637ac00bf00b5454c88e914f8acc903cbc63` |
| `dist/SignKit_macOS_ARM64.dmg` | 133,828,894 bytes, approximately 128M |
| DMG SHA-256 | `00d21e954ffcf61eb77cae905389cb4123944b1a4212ccc39c899b451a649818` |
| Source SHA | `df76b3d1d27c5a066485ddf33b9af7c0dd897edd` |

## Frozen runtime proof

The reusable command passed:

```bash
./.venv/bin/python tools/run_local_packaged_runtime_proof.py \
  --app dist/SignKit.app \
  --data-dir .codex-test-tmp/fresh-packaged-proof \
  --timeout 15
```

Observed checks:

- `codesign --verify --deep --strict` passed with ad hoc verification.
- No `.env` or `.env.*` file was present inside the app bundle.
- `Contents/Resources/web/cloud_workspace/index.html` was present.
- Frozen `/health` returned HTTP `200`.
- Isolated data produced `logs/app.log`, `secrets/jwt_secret`, and
  `signature_extractor.db` under the requested data root.
- Port `8001` was closed after bounded process shutdown.

The packaged browser proof also passed against this running artifact and the
canonical local landing server at 1440x900, 390x844, and 320x844. It observed
the document-registration-studio title, five-state rail, keyboard and pointer
state transitions, reduced motion, no overflow, workspace HTTP 200, and zero
browser errors. The authenticated bridge proof passed `401` unauthenticated,
`404` missing-job, owner-bound recovery, opaque receipt visibility, no document
bytes in the browser workspace, and zero browser errors.

## Ledger boundary

A local machine-readable ledger was generated at
`.codex-test-tmp/fresh-arm64-release-ledger.json` for source
`df76b3d1d27c5a066485ddf33b9af7c0dd897edd`. It records the DMG checksum and
size, but intentionally remains non-ready:

```text
signing_status: not_verified
smoke_status: not_run
rollback_artifact: not-recorded
```

The local runtime and browser observations are retained as evidence, but they
are not substituted for a signed release attestation or a release-owner smoke
receipt. No Intel macOS, Windows, Linux, notarization, clean-machine install,
recoverable prior release, hosted deployment, provider activation, or remote
CI release evidence is claimed.

## Source paths

- `build-tools/build.py`
- `build-tools/SignatureExtractor_macOS.spec`
- `tools/run_local_packaged_runtime_proof.py`
- `tools/release_artifact_ledger.py`
- `docs/release/RELEASE_ARTIFACT_LEDGER_SPEC.md`
- `docs/QA_RESULTS.md`

## Addendum: current `main` artifact reproof, 2026-08-14

The historical checkpoint above was built from source
`df76b3d1d27c5a066485ddf33b9af7c0dd897edd`. It remains preserved as historical
evidence. The current `main` checkout was rebuilt and re-proven after the
entitlement lifecycle and claim-provenance changes at source
`b2dde9e4919df1679809b6554a5bba0fa8df3ef4`.

The PyInstaller app build was run with the repository `.venv`:

```bash
./.venv/bin/python build-tools/build.py \\
  --build-platform darwin \\
  --profile standard \\
  --spec build-tools/SignatureExtractor_macOS.spec \\
  --no-clean
hdiutil create -volname 'SignKit' -srcfolder dist/SignKit.app \\
  -ov -format UDZO dist/SignKit_macOS_ARM64.dmg
```

Current artifact identity:

| Artifact | Observation |
| --- | --- |
| Source SHA | `b2dde9e4919df1679809b6554a5bba0fa8df3ef4` |
| `dist/SignKit.app/Contents/MacOS/SignKit` | Mach-O 64-bit arm64, 18,857,824 bytes |
| App executable SHA-256 | `9efb3711d1af10a47dae2013f9199f8d6a394b9b4c5190fd95d5f9ada8b7d379` |
| `dist/SignKit_macOS_ARM64.dmg` | 133,831,747 bytes |
| DMG SHA-256 | `50ddf14e9b6f82a18f3f9a7ad7979d6f793b55d1a55d2f284aaab7788fddb40b` |

The current frozen runtime proof passed:

```bash
./.venv/bin/python tools/run_local_packaged_runtime_proof.py \\
  --app dist/SignKit.app \\
  --data-dir .codex-test-tmp/current-packaged-proof \\
  --timeout 15
```

It observed frozen health `200`, ad hoc `codesign --verify --deep --strict`
verification, no bundled `.env`, the bundled workspace asset, isolated
SQLite/JWT/log state, and a closed port `8001` after bounded shutdown.

With the canonical local landing and companion running on ports `8080` and
`8001`, the current real-browser proofs also passed:

```bash
SIGNKIT_LANDING_BASE_URL=http://127.0.0.1:8080 \\
SIGNKIT_WORKSPACE_BASE_URL=http://127.0.0.1:8001 \\
node tools/run_local_product_browser_proof.mjs
SIGNKIT_DATA_DIR="$PWD/.codex-test-tmp/current-browser-stack-data" \\
node tools/run_local_workspace_bridge_browser_proof.mjs
```

The landing proof passed at `1440x900`, `390x844`, and `320x844`, including
the five-state rail, keyboard and pointer transitions, reduced motion,
canonical workspace handoff, no overflow, checkout fallback, and zero browser
errors. The bridge proof passed `401` unauthenticated rejection, `404`
missing-job rejection, owner-bound metadata visibility, bounded retry
recovery, no document bytes in the browser workspace, and zero browser errors.

The current machine-readable ledger is generated locally at
`.codex-test-tmp/current-arm64-release-ledger.json`, with the review rendering
at `.codex-test-tmp/current-arm64-release-ledger.md`. It records source SHA
`b2dde9e4919df1679809b6554a5bba0fa8df3ef4`, the current DMG checksum, smoke
status `passed`, signing status `not_verified`, and rollback
`not-recorded`. Normal schema validation passed. The strict `--require-ready`
gate failed as intended for missing verified signing and missing rollback
evidence. This is a current local artifact identity and runtime proof, not a
ready release claim.

QA-65 records this current reproof. The complete canonical suite also passed
`541 passed, 4 skipped` at the same source revision after the proof-record
updates. Signing or notarization, recoverable rollback,
Intel/Windows/Linux artifacts, clean-machine installation, hosted deployment,
provider activation, and remote CI remain open under `L0-02`, `L0-05`,
`L0-14`, `L2-03`, `RECON-09`, and `RECON-10`.
