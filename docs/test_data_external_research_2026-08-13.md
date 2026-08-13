# External Test-Data Research and Acquisition Policy: 2026-08-13

## Research conclusion

We can explore and, where rights and privacy permit, use publicly obtainable
datasets for internal ML development. “Publicly obtainable,” “licensed,”
“privacy-safe,” and “approved for this product use” are different facts. The
registry at `docs/test_data_dataset_registry_2026-08-13.json` records them
separately and defaults candidates to not downloaded or research-only.

## Candidate triage

| Candidate | Technical value | Current decision |
|---|---|---|
| Ultralytics Signature | Document signature localization; 143 train and 35 validation images reported by the card | Keep the already downloaded raw corpus outside Git as private research-only; AGPL and consent remain open. |
| SignverOD | Scanned-document object detection including signatures, initials, dates, and redaction | Review original source chain and consent before download. |
| SigDetectVerifyFlow | Document images with one or more signature boxes plus verification fields | Review underlying datasets, identity linkage, and whether verification data is necessary. |
| OHSDA | 6,010 isolated signatures from 601 volunteers; owner description reports written consent and ethics approval | Potential conditional candidate for crop-level robustness, not multi-signature document localization. Verify Mendeley terms and minimize age/sex metadata. |
| Tapendra Handwritten | Large handwritten/AI-generated classification corpus with MIT card claim | Block until the card’s commercial-use wording and source rights are reconciled. |
| tech4humans signature-detection | Object detection splits and Apache-2.0 card claim | Do not request gated access until privacy and access terms are reviewed. |
| ifkash signatures | Large image set with names attached | Do not download: license and identity provenance are unresolved. |
| SignEEG | Sensitive multimodal biometric research data | Do not download: irrelevant to extraction and unnecessarily high privacy risk. |

## Approval gates before any new acquisition

1. Capture the owner/source URL, exact revision, license text, access conditions, and checksum.
2. Confirm whether the license covers internal commercial ML use, redistribution, model/output use, and network-accessible processing.
3. Confirm provenance, subject consent or another documented permission basis, and whether names, age, sex, EEG, or other metadata can be excluded.
4. Confirm the task is localization/extraction rather than identity verification or signer matching.
5. Store raw data outside the repository, encrypted or access-controlled as appropriate; commit only the registry, derived metadata, and non-sensitive reports.
6. Record a named reviewer and decision before moving a candidate from `research_only` or `blocked` to `approved_internal`.
7. Run split leakage, hash, annotation, retention, and deletion checks before evaluation.

## Primary-source research notes

- The Ultralytics dataset card reports 143 training and 35 validation images and identifies the dataset as AGPL-3.0: <https://huggingface.co/datasets/Ultralytics/Signature>.
- The SignverOD card describes signature object detection in scanned documents and credits an original Kaggle source: <https://huggingface.co/datasets/ondrs/signverod>.
- The SigDetectVerifyFlow card describes document images with one or more signature boxes and reports Apache-2.0: <https://huggingface.co/datasets/Mels22/SigDetectVerifyFlow>.
- The OHSDA record reports 6,010 samples from 601 volunteers, written consent, and institutional ethics approval; license and downstream use still require verification: <https://data.mendeley.com/datasets/c5mfhr2xcz/1>.
- The ICO identifies handwritten signature analysis as an example of behavioural biometric analysis and says organisations should document the rationale and risk analysis when unique identification is not the purpose: <https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/special-category-data/what-is-special-category-data/>.
- The official Digital Personal Data Protection Act, 2023 is a jurisdiction-specific source requiring separate legal review for applicable processing: <https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf>.

This is engineering governance documentation, not legal advice or approval.
