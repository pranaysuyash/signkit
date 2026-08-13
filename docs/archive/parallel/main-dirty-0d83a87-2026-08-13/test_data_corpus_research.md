# Signature Corpus Research and Intake Decision

Status: research complete; controlled internal evaluation intake in progress
Owner: Test Data Engineering
Last updated: 2026-08-12

## Candidate reviewed

Ultralytics documents a Signature Detection Dataset with 178 document images,
one `signature` class, and bounding-box annotations. Its published split is 143
training images and 35 validation images, with no separate test split. The
documentation also states that the archive is 11.3 MB and is released under
AGPL-3.0: [Ultralytics Signature Detection Dataset](https://docs.ultralytics.com/datasets/detect/signature).

## Intake decision

Decision: permit controlled local evaluation for production improvement, with
no redistribution and no raw corpus committed to the repository.

Reasons for the original hold:

- The published train/validation arrangement is insufficient by itself for a
  held-out product evaluation; a separate evaluation split would need careful
  provenance and leakage review.
- The page describes the dataset license, but does not establish subject-level
  consent, biometric-risk assessment, or whether every underlying document has
  a commercial-use basis. That uncertainty is material for signature imagery.
- AGPL-3.0 obligations need product/legal review before using the corpus in a
  production or network-accessible workflow or distributing derived artifacts.
- The current extractor has a single-box API, while the product requirement
  includes multi-signature behavior; a single-class corpus does not close that
  contract by itself.

The user has now explicitly approved internal, non-redistributive use to improve
production. That changes the operational intake decision, not the need for
privacy/legal review, access controls, or independent validation. Raw archive
and extracted images must remain outside the tracked repository. Only sanitized
metadata, aggregate metrics, and reproducible intake instructions may enter the
repository.

## Preferred intake order

1. Synthetic, deterministic corpus for regression and algorithm development.
2. This approved public corpus for controlled internal validation, held outside
   the repository and never redistributed or embedded in shipped artifacts.
3. Explicitly consented or contractually governed document corpus held outside
   the repository, with independent annotations and a privacy review.

The NIST Privacy Framework is used as a governance reference for identifying
and managing privacy risk, not as evidence that any candidate dataset is safe:
[NIST Privacy Framework](https://www.nist.gov/privacy-framework/privacy-framework).

## Required intake record

Before an external corpus can be scored as held-out evidence, record:

- source URL, version/date, license, and redistribution restrictions;
- dataset owner and contact for provenance questions;
- subject-level consent or documented lawful basis where applicable;
- retention, access, deletion, and incident-response controls;
- annotation protocol, annotator count, disagreement policy, and schema;
- split assignment with no document/template/person leakage;
- image dimensions, file checksums, coverage strata, and a held-out test split;
- whether raw images may enter the repository or must remain in a protected store.

For this intake, raw images must remain in a private project-adjacent store,
the source validation split must remain `validation` rather than `held_out`,
and the train split may only support development diagnostics. The corpus cannot
by itself support a production accuracy claim because it has no independent
test split and its subject provenance is not established by the source page.

Run the local structural gate before evaluation:

```bash
./.venv/bin/python tools/validate_signature_corpus.py \
  --repo-root /absolute/path/to/private/ultralytics_signature \
  --corpus /absolute/path/to/private/ultralytics_signature/signkit_corpus.json
```

The `--require-held-out` gate remains intentionally unavailable for this source
corpus because the publisher provides train and validation splits but no
independent test split.
