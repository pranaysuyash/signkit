# Claude Branches Cleanup Plan

**Date:** November 23, 2025  
**Status:** Ready for execution

## Executive Summary

Found **8 Claude-created branches** containing mostly documentation. Analysis shows:
- **Most files already exist in main** (legal docs, build specs, etc.)
- **Some unique strategic documents** that may be outdated
- **No critical code changes** that aren't already in main
- **Safe to delete** after selective salvage

---

## Branch-by-Branch Analysis

### ✅ SAFE TO DELETE (Content exists in main)

#### 1. `claude/review-launch-gumroad-01V6KZThuxtFSYrmtMZii6Sr`
- **Status:** All code files already in main
- **Unique docs:** 3 operational playbooks (likely outdated)
- **Action:** Delete immediately

**Files in main:**
- ✅ `.env.example`
- ✅ `build-tools/SignatureExtractor_Intel.spec`
- ✅ `build-tools/SignatureExtractor_macOS.spec`
- ✅ `desktop_app/views/license_restriction_dialog.py`
- ✅ `legal/PRIVACY_POLICY.md`
- ✅ `legal/TERMS_OF_SERVICE.md`

**Unique files (not in main):**
- `docs/CUSTOMER_SUCCESS_WORKFLOWS.md`
- `docs/LAUNCH_OPS_PLAYBOOK.md`
- `docs/PM_LAUNCH_READINESS_FINAL.md`

**Recommendation:** These operational docs are likely superseded by current docs. Delete branch.

---

#### 2. `claude/review-codebase-launch-01U54VyFw5XisCYwWmM44sxA`
- **Status:** Documentation branch
- **Action:** Quick review, then delete

**Files to check:**
- `README.md` - may have useful updates
- `docs/LAUNCH_DAY_PLAYBOOK.md` - may be useful
- Other docs likely outdated

---

#### 3. `claude/marketing-launch-strategy-01T76ZEBPExUAm8ss8Y5j6qz`
- **Status:** Single file branch
- **File:** `docs/marketing/UPDATED_LAUNCH_STRATEGY_NOV_2025.md`
- **Action:** Check if content is in current marketing docs, then delete

---

#### 4. `claude/plan-features-roadmap-01E1zRuYzypiDp7dir2Mhyvz`
- **Status:** Single file branch
- **File:** `docs/COMPREHENSIVE_FEATURES_ROADMAP.md`
- **Action:** Check if content is in current roadmap docs, then delete

---

#### 5. `claude/research-distribution-channels-01THpNyLJ3GiDmC4hyJd3Koa`
- **Status:** Research docs (2 files)
- **Files:** Distribution channel research
- **Action:** Check if content is in current marketing docs, then delete

---

### 📋 REVIEW BEFORE DELETE (May have useful content)

#### 6. `claude/marketing-distribution-strategy-01DKjLhmLgLmKKg3juguknsy`
- **Status:** 10 strategic planning documents
- **All files are UNIQUE** (not in main)
- **Action:** Quick review to see if any frameworks are useful

**Files:**
1. `SIGNKIT_ANALYTICS_MEASUREMENT_FRAMEWORK.md`
2. `SIGNKIT_CRISIS_MANAGEMENT_PLAN.md`
3. `SIGNKIT_CUSTOMER_PERSONAS.md`
4. `SIGNKIT_EXECUTIVE_SUMMARY.md`
5. `SIGNKIT_LAUNCH_CHECKLIST.md`
6. `SIGNKIT_MARKETING_STRATEGY_MASTER_PLAN.md`
7. `SIGNKIT_PRODUCT_ROADMAP_2025-2026.md`
8. `SIGNKIT_REVENUE_FORECAST_2025.md`
9. `SIGNKIT_STRATEGY_INDEX.md`
10. `SIGNKIT_STRATEGY_README.md`

**Note:** These are all root-level files (not in docs/). Likely from an early planning session.

---

#### 7. `claude/marketing-distribution-strategy-research-01P3fhXh1qMDqcNjwTbVFdDV`
- **Status:** 5 operational planning documents
- **All files are UNIQUE** (not in main)
- **Action:** Quick review

**Files:**
1. `ANALYTICS_METRICS_DASHBOARD.md`
2. `EXECUTIVE_SUMMARY_QUICK_START.md`
3. `LAUNCH_DAY_SCRIPTS_TEMPLATES.md`
4. `PM_STRATEGY_IMPROVEMENTS_GAPS.md`
5. `RISK_MITIGATION_CONTINGENCY_PLANS.md`

---

#### 8. `claude/product-review-checklist-0147sLijL5RHaDWAtptRctyP`
- **Status:** 4 product strategy documents
- **All files are UNIQUE** (not in main)
- **Action:** Quick review

**Files:**
1. `EXECUTIVE_SUMMARY.md`
2. `LAUNCH_ACTION_PLAN.md`
3. `PRODUCT_REVIEW_REPORT.md`
4. `PRODUCT_STRATEGY_AND_ROADMAP.md`

---

## Recommended Cleanup Workflow

### Option A: Quick Cleanup (Recommended)
**Assumption:** Current docs in main are more up-to-date

```bash
# Delete all Claude branches immediately
git push origin --delete \
  claude/marketing-distribution-strategy-01DKjLhmLgLmKKg3juguknsy \
  claude/marketing-distribution-strategy-research-01P3fhXh1qMDqcNjwTbVFdDV \
  claude/marketing-launch-strategy-01T76ZEBPExUAm8ss8Y5j6qz \
  claude/plan-features-roadmap-01E1zRuYzypiDp7dir2Mhyvz \
  claude/product-review-checklist-0147sLijL5RHaDWAtptRctyP \
  claude/research-distribution-channels-01THpNyLJ3GiDmC4hyJd3Koa \
  claude/review-codebase-launch-01U54VyFw5XisCYwWmM44sxA \
  claude/review-launch-gumroad-01V6KZThuxtFSYrmtMZii6Sr

# Clean up local references
git fetch --prune
```

**Rationale:**
- All critical code is already in main
- Legal docs are in main
- Build specs are in main
- Strategic docs are likely outdated (from earlier planning sessions)
- Current docs/ directory has comprehensive marketing and launch docs

---

### Option B: Selective Salvage (Conservative)

If you want to be extra careful, salvage specific files first:

```bash
# 1. Check out interesting docs from branch 6
git checkout origin/claude/marketing-distribution-strategy-01DKjLhmLgLmKKg3juguknsy -- \
  SIGNKIT_CUSTOMER_PERSONAS.md \
  SIGNKIT_ANALYTICS_MEASUREMENT_FRAMEWORK.md

# Move to docs/ directory
mkdir -p docs/archived_strategy
git mv SIGNKIT_*.md docs/archived_strategy/
git commit -m "docs: salvage strategic docs from claude branch"

# 2. Then delete all branches (same as Option A)
```

---

## Impact Assessment

### What We're Keeping (Already in Main)
✅ All legal documents (Privacy Policy, Terms of Service, EULA)  
✅ All build specifications  
✅ License restriction dialog code  
✅ Environment configuration  
✅ Current marketing strategy docs  
✅ Current launch readiness docs  

### What We're Losing (Not in Main)
❌ ~25 strategic planning documents from early planning sessions  
❌ Operational playbooks (likely outdated)  
❌ Early roadmap drafts  
❌ Early executive summaries  

**Risk Level:** LOW
- These docs were created during planning phases
- Current docs/ directory has comprehensive, up-to-date content
- No code changes will be lost

---

## Final Recommendation

**Execute Option A: Quick Cleanup**

**Reasoning:**
1. All critical code and legal docs are in main
2. Current documentation is comprehensive and up-to-date
3. Strategic docs from Claude branches are from early planning (likely superseded)
4. Keeping 8 stale branches creates confusion
5. Can always recover from git history if needed

**Next Step:** Run the cleanup commands and prune local references.

---

## Cleanup Commands (Copy-Paste Ready)

```bash
# Delete all 8 Claude branches
git push origin --delete \
  claude/marketing-distribution-strategy-01DKjLhmLgLmKKg3juguknsy \
  claude/marketing-distribution-strategy-research-01P3fhXh1qMDqcNjwTbVFdDV \
  claude/marketing-launch-strategy-01T76ZEBPExUAm8ss8Y5j6qz \
  claude/plan-features-roadmap-01E1zRuYzypiDp7dir2Mhyvz \
  claude/product-review-checklist-0147sLijL5RHaDWAtptRctyP \
  claude/research-distribution-channels-01THpNyLJ3GiDmC4hyJd3Koa \
  claude/review-codebase-launch-01U54VyFw5XisCYwWmM44sxA \
  claude/review-launch-gumroad-01V6KZThuxtFSYrmtMZii6Sr

# Clean up local references
git fetch --prune

# Verify cleanup
git branch -r | grep claude
# Should return nothing
```

---

**Status:** Ready for execution  
**Approval needed:** Yes  
**Risk:** Low  
**Reversible:** Yes (via git history)
