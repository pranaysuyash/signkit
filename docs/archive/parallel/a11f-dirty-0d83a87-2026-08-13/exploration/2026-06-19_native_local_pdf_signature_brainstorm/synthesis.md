# Native Local PDF + Signature App Brainstorm Synthesis

Date: 2026-06-19

This is a synthesis of the role docs in this folder:

- [Product strategist](./product.md)
- [Engineering / architecture](./engineering.md)
- [Privacy / security / compliance](./privacy_security.md)
- [Power user / operator](./workflow_power_user.md)
- [Skill path audit + rerun](./skill_path_audit_and_rebrainstorm.md)

This note is a `wide open brainstorm` artifact, not a roadmap or implementation spec.

## The Shared Answer

Across all roles, the app does not want to be a generic PDF editor or a cloud e-sign clone. The best version of SignKit is a **local-first document completion workspace** that helps users:

`extract -> recognize -> place -> review -> export -> reuse`

That sequence is the real product. Signature extraction is the asset source. PDF editing is the transport layer. The user-visible value comes from making the whole loop fast, private, repeatable, and trustworthy on a local machine.

## What Each Role Contributed

### Product view

- The best wedge is recurring signature placement with field detection, reusable templates, and durable export state.
- The product should widen only in adjacent trust-building directions.
- Breadth is useful only if it increases confidence and repeatability.

### Engineering view

- The app needs explicit seams for rendering, detection, coordinate normalization, editing, audit, and recovery.
- Reopenability, deterministic behavior, and a canonical export path are core requirements.
- Optional engines should stay optional; the default path should stay simple and local.

### Privacy and security view

- Local-first must be real, visible, and enforceable.
- The app should distinguish visible signing from cryptographic signing and redaction from visual masking.
- Trust features like lineage, retention controls, and tamper-evident logs should be product features, not footnotes.

### Power-user view

- Operators need speed, shortcuts, previews, batch runs, templates, and recovery.
- Confidence should be visible before export, not inferred afterward.
- The app should behave like a local production instrument, not a disposable form.

## Strongest Feature Cluster

The highest-leverage cluster is:

1. Signature field detection with confidence overlays
2. Provenance-rich signature vault
3. Template replay for repeat documents
4. Durable document session state
5. Preview-first export verification
6. Audit trail and export receipts
7. Batch signing and watch-folder automation
8. OCR/scan cleanup as an enhancer

These features reinforce one another. Detection improves placement. Templates improve repeatability. Session state and audit logs improve trust. Batch and watch-folder flows convert the app from a one-off utility into a repeatable workflow engine.

## Best Narrow Wedge

The clearest wedge is:

**Local-first signature placement for recurring PDFs, with field detection, reusable templates, and durable export/audit state.**

Why this wedge wins:

- It matches the repo’s current direction.
- It solves a real repeated pain.
- It is differentiated by trust and repeatability, not feature count.
- It naturally expands into annotations, form filling, scan cleanup, batch operations, and eventually digital signing.

## Tensions That Matter Most

### Breadth vs trust

The app can expand, but only in directions that make the signing loop more believable. A broader product is not automatically a better product.

### Automation vs review

The system should suggest aggressively, but never silently mutate documents when confidence is low. Power users want speed, but not at the cost of surprise.

### Visible signing vs digital signing

These are different trust classes. The product should not blur them.

### Local privacy vs optional expansion

The core path must stay local. Optional OCR, advanced engines, or future cloud features should not destabilize the default experience.

## What Not To Build

- A generic Acrobat replacement.
- Cloud-first collaboration as the default.
- Parallel PDF write paths.
- Model-first document intelligence before the core loop is trustworthy.
- Fake redaction that only paints over content.
- Marketing claims that exceed the product’s trust class.

## Open Questions

- Which first beachhead matters most: contracts, HR forms, tax docs, real estate, or internal approvals?
- Should the product lean more toward document completion or toward PDF workspace?
- What should be the first post-signing adjacency: annotations, form filling, batch automation, or scan cleanup?
- How much automation should happen before user confirmation?
- Should the local vault optimize for personal convenience, team reuse, or portability first?

## Practical Direction

If this exploration turns into product work, the safest long-term path is:

1. Harden the local signing loop.
2. Add trust-building document state and auditability.
3. Add reusable templates and batch workflows.
4. Expand into annotations, form filling, and cleanup.
5. Keep digital signing and broader intelligence as explicit later layers.

That path keeps the product coherent and avoids the most common trap in this category: trying to become everything before it becomes indispensable.
