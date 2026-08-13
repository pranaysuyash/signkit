# Discussion Map: What We Can Discuss

Date: 2026-06-21

This map aligns brainstorm outcomes with `motto_v3` long-term principles for this project.

## Scope Rule

1. We discuss and build signature-engine mechanics in PDF workflows first.
2. We avoid compliance/legal positioning language in product direction and implementation claims.
3. Every discussion must either improve reliability, repeatability, or recoverability in local document completion.

## Discussion Topics (Priority Order)

1. Core signature engine
2. Placement confidence and field detection
3. Memory, templates, and reuse
4. Preflight and export-receipt reliability
5. Session durability and recovery design
6. Auditability without compliance claims
7. Offline/local-first data flow
8. Performance and ergonomics for repetitive work
9. Product wording and claim boundaries
10. Long-term roadmap pruning and dependency control
11. Failure handling and operator observability
12. Tradeoffs and kill/reframe checkpoints

## First-Principles Lens (motto_v3-aligned)

1. Build for long-term reliability, not short-term feature volume.
2. Make every core action visible and reversible.
3. Prefer deterministic local workflow state over opaque automation.
4. Store only what enables faster safe next action.
5. Track decisions for operator recovery.
6. Treat legal/compliance claims as out-of-scope unless product evidence and wording support it.

## What we can discuss by default

1. Engine design and implementation detail
2. Workflow and UX for high-volume use
3. Local persistence design and file-level traceability
4. Field detection and fallback behavior
5. Recovery-first exception handling
6. Export confidence controls
7. Roadmap sequencing for native PDF and document completion
8. Product claims and guardrails for marketing and docs
9. Measurement of user trust and rework reduction
10. Cost and complexity control for each decision
11. Parser strategy: local stack vs optional API parsers, including signatures/fields and licensing.
12. LLM-assisted document extraction boundaries (kept optional and behind consent).

## What is blocked from discussion (unless explicitly redefined)

1. Public claims of legal enforceability.
2. ISO/SOC/certification positioning.
3. PKI or legal-validity framing as a product promise.
4. KYC-like identity assurance scope as a default feature.
5. Unbounded external API parser defaults (egress, pricing, data residency) without explicit user consent and audit logging.

## Parser Research Add-on (2026-06-21)

Current decision branch in this brainstorm:

- default parser behavior remains local-first and conservative;
- non-signature field detection is part of core detector expansion;
- `LiteParse` is the preferred first optional enhancement;
- broader API parsers (for example `LlamaParse`) are optional, gated by user opt-in and explicit data-path controls.

- [Online parser research packet](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-06-19_wide_open_brainstorm/online_parser_research_2026-06-21.md)
- [Exploration map branch](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-06-19_wide_open_brainstorm/exploration_map_2026-06-21_parser_branch.md)

## Handoff Rule

Every topic should end with one of these outcomes:
1. proceed
2. prototype
3. pause
4. kill
5. reframe
