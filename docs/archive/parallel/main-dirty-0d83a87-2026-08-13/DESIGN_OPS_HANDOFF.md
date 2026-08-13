# Design-operations handoff for landing experiments

Date: 2026-08-12
Owner: CDO / Product Ops

## Principle

An experiment is a learning instrument, not a second product surface. Every
variant must have an owner, a hypothesis, a measurement plan, a claim boundary,
and a retirement path before it is exposed to customers.

## Lifecycle

1. **Frame**: record the customer problem, target segment, hypothesis, and
   system stage affected.
2. **Bound**: identify claims, legal language, checkout path, data collected,
   and operational support implications.
3. **Instrument**: define one event schema, source attribution, success metric,
   guardrail metrics, and failure visibility.
4. **Review**: obtain product, design, legal, analytics, and platform review
   according to the QA matrix.
5. **Run**: keep the variant behind an explicit route or controlled mechanism;
   never let route-level drift become an undocumented public default.
6. **Decide**: promote, iterate, archive, or stop using recorded evidence.
7. **Handoff**: if promoted, migrate into the canonical root and registry; if
   retired, redirect or archive it and mark all old docs as historical.

## Required experiment record

- Experiment ID and owner:
- Customer problem:
- Hypothesis:
- Affected promise/capability/proof/transaction/follow-through stage:
- Canonical route and temporary exposure mechanism:
- Claim IDs used:
- Checkout and event schema:
- Primary metric and guardrails:
- Legal/product risks:
- Start and decision dates:
- Decision and evidence:
- Migration or retirement commit:
- Documentation addendum:

## Non-negotiable handoff rules

- No experiment may create a second editable checkout configuration.
- No variant may publish an unregistered customer-facing claim.
- No retired variant may remain linked from an acquisition surface.
- Historical docs remain valuable, but must be clearly marked as superseded.
- A promotion is incomplete until the canonical route, registry, tests, and
  release record are updated together.
