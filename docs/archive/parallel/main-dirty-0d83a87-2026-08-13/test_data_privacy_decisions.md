# Test Data Privacy Decisions

## Decision Log

### TD-PII-001 (2026-08-12)
- **Decision**: Treat signature source assets and derived fixtures as privacy-sensitive until provenance is confirmed.
- **Context**: The repository contained `512px-Mohammad_Rafiquzzaman_signature.jpg` and generated `test_signature.png` that could be interpreted as personal-style signature data.
- **Decision driver**: Avoid shipping any fixture with implicit personal identity interpretation.
- **Chosen action**:
  - Replace the legacy signature source file with a synthetic, anonymized template.
  - Rename the canonical source asset to a neutral identifier.
  - Update manifest/pipeline references so future test fixtures can be audited as synthetic.
  - Remove the legacy identity-indicative file from the active test-data surface.
- **Owner**: Test Data Engineering
- **Status**: Completed by creating `desktop_app/resources/signature_template_synthetic_512.jpg`, moving callers to the neutral path, and re-running manifest refresh.
- **Validation**: `python3 tools/validate_test_data_manifest.py --manifest docs/test_data_manifest.md --repo-root .`

## Current open follow-up
- `T-006` closed after synthetic replacement and manifest refresh.

## Historical-reference boundary (2026-08-12)

The legacy identity-indicative filename may remain in dated review or cleanup
documents because those records describe prior repository state. It must not
appear in active code, fixtures, generators, packaging specs, or current test
data provenance. Agents should treat `docs/test_data_manifest.md` and
`docs/test_data_environment.md` as the current source of truth.

### TD-PII-002 (2026-08-12)

- **Decision**: Permit controlled local evaluation of the researched public
  signature corpus for production improvement, with no redistribution and no
  raw corpus committed to the repository.
- **Candidate**: Ultralytics Signature Detection Dataset, documented in
  `docs/test_data_corpus_research.md`.
- **Reason**: Public availability and an AGPL-3.0 archive do not, by
  themselves, establish subject-level consent or product-use compatibility.
  The user explicitly authorized internal, non-redistributive use, which changes
  the intake boundary but does not close privacy/legal review.
- **Owner**: Test Data Engineering with product/legal/privacy review before
  intake.
- **Controls**: Keep the archive and extracted images outside Git; record the
  source URL, archive checksum, date, license, and access boundary; retain only
  sanitized metadata and aggregate metrics in the repository; do not embed raw
  images in production artifacts; do not call the publisher's validation split
  an independent test set.
- **Status**: Internal evaluation approved by the user. Privacy/legal review
  remains open before production deployment, external sharing, publication, or
  network-accessible use influenced by this corpus.
