# Signature Test-Data Legal and Privacy Research

Date: 2026-08-12
Owner: Test Data Engineering
Status: research complete; legal/privacy approval remains open

This is engineering research, not legal advice or an approval to deploy. The
purpose is to define review questions and prevent an internal-use decision from
being mistaken for a provenance, consent, or license determination.

## Findings

- The GNU FAQ says that making multiple copies within one organization is not
  distribution, while transfers to other organizations or individuals are
  distribution. It also describes AGPL obligations for modified versions
  offered over a computer network: [GNU license FAQ](https://www.gnu.org/licenses/gpl-faq.en.html).
- The AGPL text distinguishes network interaction from conveying a copy, but
  customer-facing production packaging and modified network services still need
  product/legal review: [GNU AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html.en).
- Official privacy guidance defines biometric data around specific technical
  processing that can uniquely identify a person. The ICO specifically lists
  handwritten signature analysis among behavioural biometric examples and says
  that even transient processing can still be processing: [ICO special category
  data guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/special-category-data/what-is-special-category-data/?q=transparency), [ICO biometric concepts](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/biometric-data-guidance-biometric-recognition/key-data-protection-concepts/).
- The NIST Privacy Framework is a voluntary risk-management tool using
  Identify-P, Govern-P, Control-P, Communicate-P, and Protect-P. It is a
  governance aid, not dataset approval: [NIST Privacy Framework](https://www.nist.gov/privacy-framework).

## Decision applied to this repository

The Ultralytics archive remains permitted only for controlled internal
evaluation, with raw data outside Git and no redistribution. The repository
must not claim that the source documentation establishes subject consent,
commercial provenance, or lawful production use. The public validation split
is validation evidence only, not an independent held-out test set.

## Required review before production use

- Identify the legal entity and jurisdiction responsible for processing.
- Establish the source corpus provider, acquisition terms, and commercial-use
  rights for every image and annotation.
- Determine whether the intended product performs extraction only or any
  identity/authentication, matching, ranking, or decision about a person.
- Record the lawful basis, special-category condition where applicable, notice,
  retention, deletion, access, incident response, and data-subject rights path.
- Confirm whether AGPL-licensed data, annotations, or trained/derived artifacts
  enter a distributed product or network-accessible service.
- Obtain written product/legal/privacy sign-off before using this corpus to
  justify a production release threshold.

Until those items are closed, the benchmark is engineering evidence for local
development only.
