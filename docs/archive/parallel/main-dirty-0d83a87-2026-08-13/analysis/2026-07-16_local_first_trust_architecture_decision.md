# Decision: local-first trust architecture and vertical product model

**Date:** 2026-07-16
**Status:** Accepted product direction; implementation is not complete
**Reviewers:** Product owner, security reviewer, and jurisdiction-specific counsel

## Context

SignKit currently excels at local extraction, signature reuse, PDF preparation, and
local export. It needs legally defensible signing and deeper industry workflows without
abandoning privacy-first operation or becoming a generic cloud agreement platform.

## Decision

Build one local-first signed-document core with four explicit trust modes:

1. private local completion;
2. evidence-backed local or in-person electronic signing;
3. certificate-backed local digital signing with a user-controlled key;
4. optional connected or regulated signing through narrow external services.

Legal, CA/accounting, real-estate, and HR experiences are configurations over the same
workspace, roles, document sets, fields, policy, ceremony, evidence, and export models.
They are not parallel applications or APIs.

## Why

- preserves the product's strongest capability and differentiation;
- matches evidence strength and cost to each document;
- keeps files local where remote participation is unnecessary;
- makes identity, timestamp, and regulated-service costs transparent;
- avoids becoming a CA/QTSP while supporting trusted providers;
- supports jurisdictions without forking the core;
- separates owned software from recurring trust-service costs.

## Options rejected

- **Cloud-first envelope platform:** erases differentiation and competes directly on
  infrastructure, integrations, and compliance breadth. A narrow encrypted remote
  ceremony remains optional.
- **Market image placement as legal e-signature:** a visual mark alone lacks designed
  evidence of intent, consent, attribution, integrity, and retention.
- **Become a certifying authority:** unnecessary early regulatory/operational burden.
  SignKit can use user-held certificates and licensed CA/ESP/TSP/QTSP partners.
- **Separate products per profession:** would duplicate trust logic. Verticals differ
  through roles, rules, checklists, terminology, templates, and integrations.

## Derived implementation scope

- versioned evidence-event schema and append-only hash chain;
- final-document integrity service;
- consent/intent ceremony state machine;
- completion certificate and portable verifier;
- certificate/PKCS#11 abstraction and PAdES path;
- assurance policy engine and trust-provider adapter;
- canonical workspace/document-set/role model;
- vertical configuration schema;
- backup, recovery, observability, and dispute tooling.

Do not add a signing route until the existing route map and shared validation pipeline
are reviewed. All providers must use one adapter contract and ceremony state machine.

## Risks

- jurisdiction rules and excluded documents are easy to overgeneralise;
- local clocks, mutable logs, and self-asserted identity have limited independence;
- remote ceremonies add delivery, abuse, privacy, availability, and dispute risks;
- certificate signing adds token-driver, revocation, timestamp, algorithm, PDF
  interoperability, and long-term-validation risks;
- vertical scope can drift into full practice management.

## Validation

- threat model and counsel review before claims;
- golden evidence fixtures plus tampering/negative tests;
- validate signed PDFs in independent validators and operating systems;
- provider sandbox tests for success, decline, timeout, duplicate callback, retry,
  revocation, and partial completion;
- workflow interviews and paid pilots in Legal, CA/accounting, and Real Estate;
- measure local value independently from remote-signing demand.

## Rollback and migration

The current local placement flow remains available and honestly labelled. Evidence
schemas are versioned. Providers can be disabled without blocking private operation.
Vertical configurations migrate without changing document/evidence identifiers.

## Revisit triggers

- buyers primarily need cloud collaboration;
- a target jurisdiction needs a different provider/licensing model;
- DSC/certificate interoperability cannot meet support targets;
- paid pilots prove a vertical needs a distinct core contract;
- trust-service cost or liability makes packaging unsustainable.

## Related material

- `docs/research/2026-07-16_signkit_market_legal_vertical_research.md`
- `docs/VERTICAL_INTEGRATION_PRODUCT_VISION.md` (historical broad vision)
- `docs/analysis/2026-06-28_signkit_sensitive_document_positioning.md`
- `docs/analysis/2026-07-16_dodo_primary_checkout_decision.md`
