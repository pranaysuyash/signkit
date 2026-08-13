# Solo operator and agent operating model

Date: 2026-08-12
Owner: Pranay
Status: Active project operating context

## Operating reality

Pranay is the sole human operator for this project. Agents are the research,
implementation, testing, documentation, and maintenance team. Work should be
organized so one person can review decisions, run the product, and ship without
creating unnecessary organizational ceremony.

## Default rules for agents

- Do the repo-local research, implementation, testing, documentation, and task
  tracking directly.
- Prefer self-service release gates, qualified copy, reversible changes, and
  durable evidence over meetings or approval queues.
- Do not create a formal legal, certification, compliance, or organizational
  workstream unless Pranay explicitly requests it or a specific customer,
  payment, platform, or regulatory requirement makes it unavoidable.
- Do not treat external legal review or certification as a default blocker.
- When wording has risk, make it accurate and conditional, record the exact
  uncertainty, and continue all repo-local work that can proceed safely.
- If outside authority is genuinely required, identify the smallest exact
  decision needed, why it is required, and the concrete closure test. Do not
  expand that into a broad certification program.
- Keep ownership, open tasks, evidence tiers, and next actions in repo-local
  documents so future agents do not rediscover this context.

## Customer-facing trust boundary

Solo execution does not mean inventing guarantees. Agents must still avoid
unsupported privacy, payment, refund, update, performance, or certification
claims. The default response is to narrow the wording to what the product and
available evidence support, not to start a large legal process.

## Decision rule

For every proposed external approval, ask:

1. Is this explicitly required by the user, customer contract, payment
   provider, platform, or applicable regulation?
2. Can truthful qualified wording and a repo-held evidence record address the
   risk for the current stage?
3. What is the minimum decision or proof needed to proceed?

Only the first question creates a default external approval task. Otherwise,
agents should document the risk and keep building.
