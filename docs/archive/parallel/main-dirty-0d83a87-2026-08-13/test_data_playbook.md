# Test Data Engineering Playbook

Use this playbook when creating, changing, or reviewing SignKit fixtures. The
canonical inventory is [test_data_manifest.md](test_data_manifest.md). The
runtime authority is [test_data_environment.md](test_data_environment.md).

## Required workflow

1. Identify the canonical consumer and failure mode before creating data.
2. Prefer synthetic data. Do not add production-like or identity-indicative
   signatures without an explicit privacy decision and owner.
3. Make generated data deterministic. Record the seed, generator, schema or
   algorithm version, and output checksum.
4. Add the fixture and its manifest row together. Include `origin`, `pii`,
   `contains_pii`, `redacted`, `reviewed_on`, and `sha256`.
5. Add a behavioral test that would fail if the fixture were missing or the
   expected contract were broken.
6. Run the project environment gate before diagnosing imports:

   ```bash
   ./.venv/bin/python tools/validate_test_data_environment.py --repo-root .
   ```

7. Run the manifest and focused checks:

   ```bash
   ./.venv/bin/python tools/validate_test_data_manifest.py --manifest docs/test_data_manifest.md --repo-root .
   ./.venv/bin/python tools/validate_signature_corpus.py --repo-root .
   ./.venv/bin/pytest -q desktop_app/tests/test_extractor.py desktop_app/tests/test_signature_edge_cases.py
   ```

8. If the change affects shared behavior, run the complete project suite:

   ```bash
   QT_QPA_PLATFORM=offscreen ./.venv/bin/pytest -q
   ```

## Fixture classes

- Stable golden: checked-in output or labels whose intentional change requires review and a checksum update.
- Synthetic edge case: generated from a versioned deterministic script and labeled by the failure mode it exercises.
- Integration fixture: drives a real cross-module flow, not only a helper.
- Negative control: proves that invalid or empty input is rejected or produces the documented no-result behavior.
- Historical artifact: retained only as evidence in dated documentation; it is not an active test-data source.

## Corpus evaluation contract

Use `tools/evaluate_signature_corpus.py` when a fixture family has labeled
ground-truth boxes. It reports image-level presence precision/recall/F1,
one-to-one instance precision/recall/F1 at the configured IoU threshold,
matched-box mean/median IoU, exact signature-count accuracy, and count MAE.

The current extractor returns one unscored heuristic box, so average precision
is intentionally reported as unsupported. Do not invent AP or population
quality claims until the extractor emits ranked candidates/confidence and a
representative labeled corpus is available.

## Evidence discipline

- S0: test exists.
- S1: test passes.
- S2: test failed for the intended reason before the fix and passed after it.
- S3: deliberate mutation of the behavior makes the test fail.

Record evidence tiers with task outcomes. A local focused pass is not a hosted CI result, a multi-image benchmark, or production-like quality evidence.

## Privacy rules

- Treat signatures as potentially identifying biometric-style artifacts until provenance is known.
- Prefer neutral filenames and synthetic strokes.
- Do not restore `512px-Mohammad_Rafiquzzaman_signature.jpg` to active code, fixtures, scripts, or packaging specs.
- Keep historical references intact when they document past behavior, but label them as historical and never use them as current provenance.
