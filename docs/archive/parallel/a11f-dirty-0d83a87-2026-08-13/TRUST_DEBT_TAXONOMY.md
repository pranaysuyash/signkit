# Trust-debt severity taxonomy

Date: 2026-08-12
Owner: CDO + Product Ops

Trust debt is any gap between what the customer is led to believe and what the
product, evidence, transaction, or support operation can sustain.

| Level | Definition | Examples | Default priority | Closure evidence |
| --- | --- | --- | --- | --- |
| T0 | Cosmetic coherence issue with no promise or workflow impact | Spacing, icon, or motion mismatch | Batch | Visual review |
| T1 | Comprehension friction that can create hesitation | Vague CTA, unexplained terminology, inconsistent voice | High | Copy review and usability smoke |
| T2 | Evidence or capability mismatch | Screenshot implies a feature not in the bundle; stale price | Critical before release | Registry row, product evidence, updated test |
| T3 | Legal, financial, privacy, or eligibility overstatement | Absolute offline promise, unsupported refund or update guarantee | Release blocker | Legal/product approval and operational proof |
| T4 | Systemic route or transaction fragmentation | Variant pages bypass claims, checkout, or telemetry | Immediate systemic work | Route parity, checkout smoke, funnel evidence |

## Triage questions

1. Can a customer make a materially wrong decision because of the gap?
2. Does the gap affect money, privacy, legal rights, or support expectations?
3. Does it appear in more than one route, document, or owner boundary?
4. Can an operator explain and recover from the resulting failure?
5. Is the evidence current, reproducible, and tied to a source of truth?

## Required issue record

- Trust level:
- Customer belief:
- Actual capability or boundary:
- Affected surfaces:
- Evidence currently available:
- Owner:
- Reviewer:
- Closure criteria:
- Rollback or containment:
- Revisit trigger:
