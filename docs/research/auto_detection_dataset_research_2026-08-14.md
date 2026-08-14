# Auto-detection dataset research refresh: 2026-08-14

Scope: current public source records for the RECON-24 auto-detection and
confidence-evaluation decision. No dataset files were downloaded or added to
the repository during this refresh.

## Decision

No candidate moves from `research_only` or `review_before_download` to an
approved external evaluation corpus based only on a repository license label,
a hosted dataset card, or public availability. The project still needs either
a permissioned internal corpus with documented provenance and consent, or an
explicit product decision to remain synthetic-only.

This preserves the existing boundary in
`docs/test_data_dataset_registry_2026-08-13.json`: availability is not
permission, and a detection benchmark does not become signer-authentication or
legal-validity evidence.

## Source observations

| Candidate | Current primary-source observation | Product fit | Decision |
| --- | --- | --- | --- |
| SignverOD | The Hugging Face card labels the dataset Apache-2.0 and describes 2,576 scanned document images with 7,103 boxes across signature, initials, redaction, and date. Its metadata shows a 2,299-row train split. The card names Tobacco800, NIST Special Database 2, bank-cheque images, and GSA lease documents as upstream sources. | Strongest document-localization fit, including multiple artifact categories and realistic document context. | Keep private research-only. Do not treat the redistributed Apache label as proof that every upstream source permits SignKit use. Re-check upstream terms, consent, provenance, and intended use before any new evaluation or redistribution. |
| tech4humans signature-detection | The hosted record labels the dataset Apache-2.0, object detection, and parquet format, but it is gated. The record says access requires agreement to share contact information and that files cannot be accessed before the conditions are accepted. | Potentially useful localization corpus, but access and data-handling terms are part of the gate. | Do not request access until product, privacy, and provenance review is complete. |
| SigDetectVerifyFlow | The hosted record labels it Apache-2.0, image classification plus object detection, document modality, and approximately 3.55 GB. The dataset combines detection and verification concerns. | Potentially broad, but it exceeds the current narrow extraction-localization need and may carry identity or source-chain risk. | Review before download. Do not use verification fields or identity-linked data for extraction evaluation without a separate privacy decision. |
| OHSDA | The primary Mendeley record reports 6,010 isolated signatures from 601 volunteers, age and sex metadata, written informed consent, institutional ethics approval, and CC BY 4.0. | Useful for handwriting or writer-analysis research, not for locating signatures in documents. Its biometric-like metadata creates unnecessary sensitivity for the current detector gate. | Do not use for RECON-24 localization. Keep as research-only and require a separate privacy and data-minimization decision for any future use. |
| NIST Special Database 2 | NIST describes 5,590 binary images of computer-synthesized tax-form documents, 900 simulated submissions, and field-isolation/document-processing uses. | Useful as synthetic document context, but it does not supply permissioned handwritten signature ground truth for this product decision. | Treat as synthetic or document-background research only. It does not close the real-signature or human-accuracy gate. |

## What is verified versus unresolved

Verified from the current source records:

- The SignverOD card exposes a source chain rather than a single-origin corpus.
- The tech4humans record is gated and requires contact-information sharing.
- SigDetectVerifyFlow is materially larger and includes both detection and
  verification tasks.
- OHSDA's primary record states written consent, ethics approval, and CC BY 4.0.
- NIST Special Database 2 is computer-synthesized document imagery, not a
  collection of user-submitted handwritten signatures.

Still unresolved for any real-data promotion:

- rights and terms for every upstream source and redistribution layer;
- whether the data subjects consented to this internal evaluation purpose;
- whether names, signatures, or other fields create identity or biometric risk;
- whether the split is subject-disjoint and representative of SignKit's users;
- retention, deletion, access control, and incident-response rules;
- the product accuracy bar for suggestion, confirmation, and any unattended
  placement behavior.

## Recommended next action

Do not download another public candidate as a substitute for a permissioned
corpus. The next RECON-24 decision is one of:

1. approve a documented internal corpus acquisition protocol with consent,
   minimization, split, retention, deletion, and review owners; or
2. explicitly keep auto-detection synthetic-only and retain human confirmation
   as the product contract.

Until that decision and its evidence exist, calibration reports and detector
metrics remain regression evidence only. They must not promote a threshold,
change the default, or support production, legal, privacy, or signer-
authentication claims.

## Source records

- SignverOD dataset card: <https://huggingface.co/datasets/ondrs/signverod/blob/main/README.md>
- tech4humans gated dataset record: <https://huggingface.co/datasets/tech4humans/signature-detection/tree/main>
- SigDetectVerifyFlow dataset record: <https://huggingface.co/datasets/Mels22/SigDetectVerifyFlow/tree/main>
- OHSDA primary Mendeley record: <https://data.mendeley.com/datasets/c5mfhr2xcz/1>
- NIST Special Database 2: <https://www.nist.gov/srd/nist-special-database-2>
- Apache License 2.0 text: <https://www.apache.org/licenses/LICENSE-2.0>

The source pages were inspected on 2026-08-14. Hosted cards and labels may
change; re-check them before access, ingestion, or release use.
