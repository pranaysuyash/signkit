---
parent: ../SIGNKIT_SCALING_EXPANSION_WAYFINDER_MAP.md
labels:
  - wayfinder:grilling
status: closed
mode: HITL
assignee: pranay
blocked_by: []
---

# Establish the enduring product boundary: local execution and web control plane

## Question

Which customer outcomes must remain local by default, which outcomes may be offered through an opt-in web control plane, and what authority/data boundaries prevent SignKit from becoming a duplicate cloud document product?

## Resolution

**Decision date:** 2026-07-31

SignKit will support three first-class delivery topologies:

- **Local:** the desktop app operates without sync. Documents, signature assets, workflow state, and audit records remain on the customer's device.
- **Cloud:** a complete web-native SignKit product operates without requiring the desktop app. It owns its cloud execution, storage, recovery, audit, and support obligations.
- **Hybrid:** local and cloud components synchronize only the capabilities and data the customer explicitly enables. Local execution remains viable while connected coordination and sync add value.

This is not a decision to create three independent products. The shared product model, capability taxonomy, workflow lifecycle, entitlement model, audit semantics, and customer-facing claims must remain canonical. Each topology is a deployment and data-authority choice with an explicit capability matrix.

The prior framing of web as only a control plane is too narrow. The web product may become a complete cloud-native option, but it must be designed to the same operational standard as the desktop product rather than acting as a thin remote wrapper.

**User source:** Founder direction in this Wayfinder session.

**Consequences:** The map now needs a topology capability/data contract before integration architecture, commercial packaging, or first-web-surface sequencing can be decided.
