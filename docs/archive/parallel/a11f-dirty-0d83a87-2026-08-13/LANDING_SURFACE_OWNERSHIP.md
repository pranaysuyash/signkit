# Landing-surface ownership matrix

Date: 2026-08-12
Owner: CDO / Product Ops

## Ownership rule

There is one public acquisition owner: the canonical root page. Other landing
HTML is retained for historical review or asset recovery and is not an editable
production surface unless it is first reintroduced through the release gate.

| Surface | Current role | Edit authority | Required reviewers | Evidence required |
| --- | --- | --- | --- | --- |
| `/` and `index.html` | Canonical acquisition and checkout entry | Web Platform with Product approval | CDO, Legal for claims, Analytics for events | QA matrix, claim registry, focused tests, route smoke |
| Legacy HTML variants | Historical review only | No direct production edits | CDO + Web Platform before reactivation | Migration decision and full QA gate |
| `web/live/js/checkout-config.js` | Public provider configuration | Platform owner | Product Ops, Analytics, Legal where copy changes | Provider-state review and checkout smoke |
| `web/live/js/checkout.js` | Canonical checkout behavior and telemetry | Platform owner | Analytics, QA | Syntax/test plus browser event inspection |
| `_redirects` | Deployed route authority | Web Platform | Product Ops | Route parity audit and deployment smoke |
| `serve.py` | Local route authority | Web Platform | QA | Local HTTP smoke and parity audit |
| `docs/launch_claims/registry.md` | Customer-claim authority | CDO + Product | Legal for regulated or financial language | Evidence tier and enforcing test |
| `legal/*` | Contract and policy authority | Product + Legal | Legal owner | Dated review and public-copy parity |
| Historical landing docs | Context and decision history | Documentation owner | CDO when superseded | Dated addendum, never silent rewrite |

## Change workflow

1. Propose the customer or business outcome, not a screen-level change.
2. Identify the affected promise, capability, proof, transaction, and
   follow-through stages.
3. Update the canonical source and claim registry together.
4. Run the QA matrix and parity auditor.
5. Obtain the required review based on claim risk.
6. Publish or redirect; record the evidence and rollback path.

No owner may ship a route-specific checkout, claim, or analytics implementation
outside this workflow.
