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
