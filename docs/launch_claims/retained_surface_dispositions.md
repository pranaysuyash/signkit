# Retained public-surface dispositions

Date: 2026-08-14
Owner: Product, Web Platform, Legal, and release engineering
Scope: local source-tree warning disposition

This file is the local disposition register for warnings emitted by
`tools/audit_public_surface.py --strict --json`. The canonical root is the only
current acquisition surface. The retained pages below are archive or redirect
inputs and are not current product evidence. Their text is preserved for
reconciliation and recovery, but a release artifact and deployed probe must
still prevent them from becoming public routes.

## Retained HTML pages with claim warnings

| Surface | Disposition | Closure gate |
| --- | --- | --- |
| `/buy.html` | Historical, redirect-only, archive review | Deployed 301 redirect and release artifact exclusion |
| `/gum.html` | Historical, redirect-only, archive review | Deployed 301 redirect and release artifact exclusion |
| `/purchase.html` | Historical, redirect-only, archive review | Deployed 301 redirect and release artifact exclusion |
| `/root.html` | Historical, redirect-only, archive review | Deployed 301 redirect and release artifact exclusion |
| `/web/live/index.html` | Historical, redirect-only, archive review | Deployed 301 redirect and release artifact exclusion |
| `/web/new_landing_page/index.html` | Historical, redirect-only, archive review | Deployed 301 redirect and release artifact exclusion |

These pages may contain legacy checkout references, placeholders, or stronger
privacy and social-proof language. That content is not approved for the
canonical root and is not evidence of current product behavior.

## Historical documents with retired-route references

All files in this table are preserved documentation history. They are not
current claim authorities and must not be copied into public or legal copy.

| Document | Disposition | Closure gate |
| --- | --- | --- |
| `docs/landing/LANDING_PAGE_SETUP_NOTES.md` | Historical archive | Documentation truth-map classification |
| `docs/landing/AB_TEST_STRUCTURE.md` | Historical archive | Documentation truth-map classification |
| `docs/landing/CLOUDFLARE_DEPLOYMENT.md` | Historical archive | Documentation truth-map classification |
| `docs/landing/AB_TEST_VARIANTS.md` | Historical archive | Documentation truth-map classification |
| `docs/landing/LANDING_PAGE_BRANCH.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/DOCS_UPDATED.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/NEXT_STEPS.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/TODO_NOV_19_2025.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/README_LANDING_PAGE.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/LANDING_PAGE_SETUP_NOTES.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/TODAY_NOV_19_PRIORITIES.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/AB_TEST_STRUCTURE.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/SOFT_LAUNCH_TEMPLATES_NOV_19.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/CLOUDFLARE_REDIRECTS_ISSUE.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/DEPLOYMENT_STATUS.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/CLOUDFLARE_DEPLOYMENT.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/DAY_1_METRICS_NOV_19.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/AB_TEST_VARIANTS.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/LANDING_PAGE_README.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/DOMAIN_SETUP_GUIDE.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/ANALYTICS_FIX_SUMMARY.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/REDIRECT_FIX_NOV_19.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/DEPLOYMENT_SUMMARY.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/IMMEDIATE_ACTION_PLAN_NOV_19.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/POST_LAUNCH_ACTION_PLAN_NOV_19.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/ANALYTICS_IMPROVEMENTS.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/LANDING_PAGE_BRANCH.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/QUICK_START.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/DEPLOYMENT_CHECKLIST.md` | Historical archive | Documentation truth-map classification |
| `docs/moved_root_docs/DOCS_UPDATE_NOV_19.md` | Historical archive | Documentation truth-map classification |

## Evidence boundary

The executable contract in `tests/test_claim_surface_dispositions.py` checks
that every current strict-audit warning path appears in this register. This is
local source-tree evidence. It does not establish deployed redirect behavior,
release artifact exclusion, legal approval, provider activation, or hosted
claim parity. Those remain open under `L0-13`, `L1-07`, `RECON-08`, and
`RECON-09`.
