# SignKit documentation truth map

Date: 2026-08-13
Scope: canonical local `main`, preserved historical material, and reachable
public-surface source files

## Why this exists

The repository contains launch-era status reports, landing variants, strategy
explorations, and preserved parallel-work snapshots. They are valuable
evidence, but they do not all describe the same product state. This map
establishes which sources control current decisions and how older material must
be interpreted.

A dated historical document can explain what was believed at that time, but it
cannot override the current Product Owner backlog, current QA evidence, current
claim registry, or the current source implementation.

## Precedence for current work

Use these sources in order when two documents disagree:

| Order | Source | Authority |
| ---: | --- | --- |
| 1 | `docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md` | Canonical explicit and implicit task state, priority, owner, evidence, and closure criteria |
| 2 | `docs/QA_RESULTS.md` | Dated local test results, evidence tiers, known skips, and non-claims |
| 3 | `docs/RECONCILIATION_STATUS_2026-08-13.md` | Parallel-work preservation, local promotion, release boundaries, and current handoff state |
| 4 | `docs/launch_claims/registry.md` | Allowed customer-facing wording and required claim gates |
| 5 | Current implementation and runtime evidence | `index.html`, `web/canonical_landing/`, desktop/backend code, reusable proof tools, and their scoped tests |

The Product Owner backlog is the task authority even when a condensed TODO or
an older status report uses a different checkbox or completion word.

## Current product and operator sources

| Surface | Classification | Current source or evidence |
| --- | --- | --- |
| Canonical public root | Current local source | `index.html` and `web/canonical_landing/`; hosted publication remains a separate `L0-04`, `L0-13`, and `RECON-08` gate |
| Local workspace | Current local source | `web/cloud_workspace/`, local companion routes, and local browser/runtime proof records |
| Desktop extraction and PDF workflow | Current implementation | `desktop_app/`, `desktop_app/workflows/`, `docs/PRODUCT_GLOSSARY.md`, and `docs/STATE_CONTENT_MATRIX.md` |
| Local entitlement boundary | Current implementation | `desktop_app/license/`, ADR-0151, and `QA-23`; provider activation remains open |
| Local release QA | Current evidence | `docs/QA_RESULTS.md` and linked dated review/research reports |
| Current task state | Current authority | `docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md` |
| Customer-facing claim rules | Current authority | `docs/launch_claims/registry.md`; static claim tests do not replace deployment or legal review |
| Current legal boundary | Current review set | `legal/PRIVACY_POLICY.md`, `legal/TERMS_OF_SERVICE.md`, and `legal/EULA.md`, with conflicts tracked as backlog tasks |

## Historical or non-authoritative material

The following files are retained for audit context and must not be cited as
current release proof without a newer evidence record:

| Material | Classification | Handling |
| --- | --- | --- |
| `docs/CURRENT_LAUNCH_STATUS.md` | Historical November 2025 launch snapshot | Preserve; do not use its complete/launch claims as current state |
| `docs/FINAL_LAUNCH_STATUS.md` | Historical November 2025 launch snapshot | Preserve; artifact, provider, and launch statements require current ledger evidence |
| `docs/FINAL_STATUS_AND_TODO.md` and other `FINAL_*` or dated `*_STATUS*` reports | Historical status or decision snapshot | Preserve; follow the current backlog and truth map for active work |
| `docs/ARCHITECTURE_FINAL_DECISION.md`, `docs/VERTICAL_INTEGRATION_PRODUCT_VISION.md`, and broad strategy studies | Historical or exploratory strategy | Use as context only; current local-first topology is governed by current ADRs and backlog evidence |
| `web/live/`, `root.html`, `buy.html`, `purchase.html`, and `gum.html` | Retained legacy public-source variants | Not current claim sources. Redirect, scrub, archive, or exclude them from a release artifact under `L0-13` and `L1-07` |
| `web/backups/` and `deploy_dist/` | Historical/generated delivery material | Preserve for provenance; do not treat as the current root or release artifact without a dated build ledger |
| `docs/archive/parallel/` | Immutable parallel-work preservation | Never silently edit or use as current product truth; promote selected work through the canonical backlog and a new commit |

## How to update truth safely

When implementation moves ahead of a historical document:

1. Add or update the task in the Product Owner backlog, including evidence and
   the remaining boundary.
2. Update the relevant current QA, claim, glossary, or state contract.
3. Add a dated addendum to the reconciliation record when the change affects
   parallel-work accounting or release claims.
4. Mark the older document historical or superseded without deleting its
   evidence unless removal is explicitly authorized.
5. Run the focused documentation/claim checks and the canonical local suite.

This map does not close hosted deployment, provider fulfilment, legal review,
cross-platform packaging, external research, or real-user evidence gates. It
makes the current-versus-historical boundary executable and discoverable.
