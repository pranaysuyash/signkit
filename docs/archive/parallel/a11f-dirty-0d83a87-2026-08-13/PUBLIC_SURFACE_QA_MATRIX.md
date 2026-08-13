# Public-surface QA matrix and release gate

Date: 2026-08-12
Owner: Solo operator with agent support
Applies to: `index.html`, `_redirects`, `serve.py`, checkout assets, legal
documents, and any proposed public landing surface

## Release gate

All blocking checks must pass before a public route or customer-facing claim
is published. Warnings require an owner and closure date in the release note.

| Area | Check | Required evidence | Owner | Failure action |
| --- | --- | --- | --- | --- |
| Route | `/` is the only acquisition surface | Route audit plus deployed redirect smoke | Web Platform | Block release; update both route authorities |
| Route | Legacy and direct HTML paths redirect to `/` | 301 responses with query preservation from the deployed probe | Web Platform | Block release |
| Claims | Every root claim marker has a registry row and test | Registry test, S1 minimum | CDO + Legal | Block release |
| Claims | No social proof, benchmark, or absolute privacy claims | Static claim scan and manual copy review | CDO | Block release |
| Narrative | Promise, capability, proof, transaction, and follow-through align | Brand narrative contract review | Product + Design | Block release |
| Checkout | Provider state is configuration-driven | Config inspection, JavaScript content-type probe, and browser smoke | Platform | Block release |
| Checkout | Checkout intent includes placement and bounded entry attribution | Event inspection without personal data | Analytics | Block release |
| Policy truth | Pricing, refund, licence, privacy, and update language match the current policy docs | Solo-operator policy review record | Solo operator + agents | Qualify or defer the claim; external review only when specifically required |
| Product | Named workflow exists in the release bundle | Release-manifest or runtime evidence | Product | Block release or qualify copy |
| Accessibility | Keyboard path, focus state, labels, contrast, and reduced motion reviewed | Manual accessibility pass and Lighthouse audit | Solo operator + agents | Fix critical failures; record non-blocking follow-up |
| Mobile | Root page loads and primary CTA remains usable on narrow viewport | Browser/device smoke | QA | Block release for broken conversion |
| Operations | Support and refund path are visible and actionable | Support simulation | Product Ops | Block release |
| Observability | Operator can identify provider, placement, source, and failure state | Event/log review | Platform + Analytics | Block release |

## Minimum command gate

```bash
python3 tools/audit_public_surface.py --strict
python3 -m pytest -p no:cacheprovider tests/test_launch_claim_registry.py tests/test_public_surface_audit.py tests/test_deployed_surface_probe.py -q
python3 -m py_compile serve.py tools/audit_public_surface.py tools/test_deployed_surface.py
node --check web/live/js/checkout.js
```

The release owner must also run both deployed checks after publishing:

```bash
bash scripts/test-deployment.sh https://signkit.work
python3 tools/test_deployed_surface.py --base-url https://signkit.work --json
```

These commands provide static and local evidence. They do not prove deployed
redirect behavior, provider activation, real purchase completion, or legal
approval. Those checks require the release owner to attach their own evidence.

## Release record template

- Release/date:
- Canonical commit or artifact:
- Route smoke evidence:
- Claim registry revision:
- Checkout provider and configuration state:
- Policy reviewer and date; external reviewer only if specifically required:
- Product bundle evidence:
- Accessibility/device evidence:
- Known warnings and owners:
- Rollback path:
