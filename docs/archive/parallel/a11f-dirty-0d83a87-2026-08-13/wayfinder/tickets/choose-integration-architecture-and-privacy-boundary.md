---
parent: ../SIGNKIT_SCALING_EXPANSION_WAYFINDER_MAP.md
labels:
  - wayfinder:research
status: open
mode: AFK
assignee: unassigned
blocked_by:
  - define-local-cloud-hybrid-capability-contract.md
---

# Choose the integration architecture and privacy boundary

## Question

What canonical integration contract lets external systems trigger or receive local SignKit workflow outcomes while preserving local document execution, idempotency, auditability, recovery, and customer control?

## Scope additions

Evaluate the integration ladder: explicit local import/export, governed folder adapters, template-level lifecycle webhooks, one selected vertical-system adapter, a Cloud/Hybrid MCP adapter for metadata and approved extraction jobs, and only then a local-agent bridge or broader enterprise ecosystem. Each candidate must state the trigger, permitted data, authoritative state, retry/idempotency key, receipt, failure recovery, and operator owner.

## Discussion addendum (2026-08-04)

The proposed MCP surface is documented in
`docs/analysis/2026-08-04_cloud_mcp_signature_extraction_discussion.md`.
The scope is future Cloud and Hybrid expansion only. The current local desktop
product is not being exposed through MCPMeter, and the existing extraction
router is not accepted as a hosted document boundary.
