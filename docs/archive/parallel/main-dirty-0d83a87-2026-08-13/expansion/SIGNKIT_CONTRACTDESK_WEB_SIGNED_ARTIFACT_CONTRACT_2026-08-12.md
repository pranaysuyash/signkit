# SignKit ContractDesk Signed-Artifact Boundary

Date: 2026-08-12
Status: Local artifact contract and certificate-backed PAdES baseline implemented; production trust and hosted integration remain gated
Owner: Desktop/PDF, API Product, Security, Legal, Operations

## Decision

The canonical local output path now has a typed artifact receipt contract in `desktop_app/workflows/verifier.py`. The receipt verifies that an output exists, is non-empty, is not written in place, and differs from the source by SHA-256 digest. It also records whether the artifact was produced by the explicit certificate-backed PAdES path.

For the visual placement path, the receipt is an integrity and provenance record and is not a cryptographic signature, signer authentication, certificate, non-repudiation assertion, or hosted export. For the certificate-backed path, the receipt records the embedded PDF signature verification result, certificate fingerprint, trust scope, and cryptographic-signature semantics without asserting legal qualification by itself.

## Receipt contract

`ArtifactReceipt` uses schema `signkit.artifact_receipt.v1` and contains:

- `artifact_id`: `sha256:<output digest>` only when verification succeeds.
- `input_sha256` and `output_sha256` for immutable content comparison.
- `verification_status`: `verified` or `rejected`.
- `verification_reason`: explicit failure such as `input_missing`, `output_missing`, `output_empty`, `in_place_not_allowed`, or `unchanged_digest`.
- `signature_semantics`: explicit `visual_signature_placement_not_cryptographic_signature`.
- `operator_subject` and `execution_id` when the caller has those values.
- `generated_at`, output name, and output size for operator reconstruction.

Receipts are written atomically by `write_artifact_receipt`; partial JSON must never become the visible receipt.

## Current local integration boundary

- Existing `PDFSigner` and desktop PDF workflows remain the canonical visual artifact producers. `desktop_app/pdf/digital_signer.py` is now the canonical certificate-backed PAdES producer, exposed deliberately through `desktop_app/pdf/signer.py` and `desktop_app/workflows/engine.py` without creating a parallel signing engine. `desktop_app.workflows.engine.export_pdf_artifact` is the explicit dispatch seam: visual mode accepts only visual signature data, certificate mode accepts only the PKCS#12 path and certificate options.
- Existing `verify_output` remains the fail-closed primitive and now shares the same rejection rules as receipt creation.
- The web control plane may reference a receipt or manifest in a future integration, but it must not claim that a visual placement receipt is a cryptographic signature.
- No new API route was added. The existing `/workspace` transition remains metadata-only.

The next integration task is B-12: unify the UI/export seam around the explicit signing choice, add production key custody and trust policy, and close storage, recovery, legal, and hosted evidence gates. The cryptographic/PAdES stage itself is no longer deferred: it is implemented locally and must not be conflated with the remaining production-readiness work.

The desktop UI now routes its Save Signed PDF action through `desktop_app.workflows.engine.export_pdf_artifact`. Visual placement remains the default explicit choice and is labeled non-cryptographic. Certificate-backed PAdES mode requires a PKCS#12 path and passphrase, and reports the generated receipt path after local verification. The signer also accepts a `Pkcs12CredentialProvider`; `MacOSKeychainPkcs12CredentialProvider` resolves a passphrase without putting it in logs or object representations, and an optional authorized-subject allowlist rejects unauthorized operators before output promotion. These controls do not by themselves provide hardware-backed or remote key custody.

## Verification evidence

- `.venv/bin/pytest tests/test_artifact_receipt.py -q`: `3 passed` (S1 targeted test evidence).
- `.venv/bin/pytest desktop_app/tests/test_pdf_features.py -k 'test_add_signature or test_sign_pdf_convenience_function' -q`: `3 passed, 21 deselected` (S1 existing producer regression evidence).
- `TMPDIR=/var/tmp .venv/bin/pytest desktop_app/tests/test_digital_signer.py -q`: `3 passed` (S1 targeted evidence for certificate-backed signing, signed-revision tampering, and wrong-passphrase failure).
- `TMPDIR=/var/tmp .venv/bin/pytest desktop_app/tests/test_digital_signer_trust.py -q`: `1 passed` (S1 configured trust-root rejection and no-promotion evidence).
- `TMPDIR=/var/tmp .venv/bin/pytest desktop_app/tests/test_digital_signer.py desktop_app/tests/test_digital_signer_trust.py -q`: `4 passed` (S1 combined signing and trust evidence).
- `TMPDIR=/var/tmp .venv/bin/pytest desktop_app/tests/test_export_mode_dispatch.py -q`: `3 passed` (S1 explicit export-mode contract and ambiguous-configuration rejection).
- `QT_QPA_PLATFORM=offscreen TMPDIR=/var/tmp .venv/bin/pytest desktop_app/tests/test_workflow_screen_smoke.py -q`: `11 passed` (S1 desktop workflow smoke evidence).
- `QT_QPA_PLATFORM=offscreen TMPDIR=/var/tmp .venv/bin/pytest desktop_app/tests/test_pdf_bulk_field_detection.py -q`: `6 passed` (S1 PDF UI regression evidence).
- `TMPDIR=/var/tmp .venv/bin/pytest desktop_app/tests/test_certificate_credentials.py -q`: `4 passed` (S1 provider contract, secret redaction, fixed invocation, and exactly-one-source evidence).
- `TMPDIR=/var/tmp .venv/bin/pytest desktop_app/tests/test_certificate_credentials.py desktop_app/tests/test_digital_signer.py desktop_app/tests/test_digital_signer_trust.py -q`: `9 passed` (S1 credential, signing, trust, and unauthorized-operator evidence).
- `TMPDIR=/var/tmp .venv/bin/pytest tests/test_integration_workflows.py -k 'pdf' -q`: `1 passed, 10 deselected` (S1 focused workflow compatibility evidence).
- `.venv/bin/python -m py_compile desktop_app/workflows/verifier.py`: passed.
- `.venv/bin/python -m pip check`: no broken requirements found.

Timestamp-source validation is included in the digital/trust suite; external TSA, revocation, DSS/VRI, and LTV behavior remain unverified.

These checks establish local integrity, producer compatibility, certificate-backed PDF signing, and signed-revision verification. They do not establish public-CA trust, revocation/timestamp/LTV status, legal effect in a jurisdiction, or hosted execution readiness.

## Cryptographic signing gate

A production-grade cryptographic/PAdES deployment remains an approved stage behind this boundary, not a reinterpretation of the visual receipt. The local baseline now exists; production deployment requires:

1. Signer identity and authorization model.
2. Key custody and cryptographic provider decision.
3. PDF signature profile and certificate validation policy.
4. Timestamping, revocation, and long-term validation policy where applicable.
5. Artifact storage, retention, deletion, and recovery behavior.
6. Security, legal, and customer-claim review.
7. Tier 3 or higher integration evidence against real PDF artifacts.

The local implementation uses `pyHanko` with a PKCS#12 signer and a PAdES baseline detached signature. Verification requires cryptographic validity, intact signed revision, and a configured trust scope. With no external trust roots configured, the local default is explicit trust in the embedded signer certificate for deterministic development and test use; that is not public-CA qualification or a legal-signing claim. A byte changed inside the signed revision is rejected, while arbitrary post-signature incremental updates are a separate PDF revision-control concern and require policy before production use.

The trust boundary is fail-closed when external roots are supplied: a certificate that does not chain to the configured root is rejected before the output is promoted or its receipt is written. Current pyHanko validation covers cryptographic integrity, certificate-chain trust, and PDF incremental-update analysis, but its documentation states that structural compliance with every PAdES profile provision is not established automatically. PAdES-T/LT/LTA therefore remain explicit production profile work, including an RFC 3161 timestamp authority and revocation/long-term validation policy where required.

The signer now accepts either `timestamp_url` or an injected `timestamper`, never both. A timestamp URL constructs pyHanko's HTTP timestamp provider only when explicitly configured; baseline signing performs no timestamp-network call. Timestamp configuration validation is covered, but no external TSA has been exercised in this local pass.

Research references for this hardening step:

- [pyHanko validation factors and trust settings](https://docs.pyhanko.eu/en/latest/cli-guide/validation.html)
- [RFC 3161 Time-Stamp Protocol](https://datatracker.ietf.org/doc/rfc3161/)

PAdES is the relevant PDF digital-signature standards family, while FIPS 186-5 describes digital-signature algorithms and identity/authentication properties. JSON receipts should use a canonicalization policy before any future signing operation. These standards are inputs to the gate, not evidence that SignKit currently implements them.

Research references:

- [ETSI EN 319 142-1 PAdES](https://www.etsi.org/deliver/etsi_EN/319100_319199/31914201/01.02.01_60/en_31914201v010201p.pdf)
- [NIST FIPS 186-5 Digital Signature Standard](https://csrc.nist.gov/pubs/fips/186-5/final)
- [RFC 8785 JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785.html)
