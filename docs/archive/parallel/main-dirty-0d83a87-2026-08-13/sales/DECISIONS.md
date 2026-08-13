# SignKit Sales Decisions

## 2026-07-22 — Establish a repo-local sales workspace

**Decision:** Keep sales strategy, prospect research, outreach templates, and the
lightweight pipeline under `docs/sales/` in the SignKit repository.

**Why:** Commercial claims must stay aligned with the shipped product, checkout,
privacy/legal language, and current implementation. A repo-local workspace preserves
that relationship and makes evidence review possible.

**Tradeoff:** CSV is intentionally simple and not a multi-user CRM. Migrate only when
the current workflow demonstrates the need; preserve the same schema during migration.

**Revisit when:** multiple collaborators need concurrent updates, automated activity
sync is required, or pipeline volume makes CSV error-prone.

## 2026-07-22 — Start with a legal-operations wedge

**Decision:** The first measured prospect campaign should test small legal teams before
expanding to accounting, real estate, HR, or document-service teams.

**Why:** The product's privacy/local-first value is clearest where confidential PDFs,
repeated document preparation, and signature reuse coexist. This is a testable thesis,
not a claim of proven product-market fit.

**Revisit when:** 20–30 qualified conversations produce weaker pain, access, or purchase
signals than another segment.
