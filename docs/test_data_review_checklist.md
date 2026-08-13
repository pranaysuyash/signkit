# Test Data Review Checklist

Use this checklist before creating or changing test data fixtures.

## 1) Source and reproducibility
- [ ] Is the fixture source/authoring path documented in `docs/test_data_manifest.md`?
- [ ] For generated fixtures, is `reproducible_seed` and generator script/version recorded?
- [ ] Is the fixture output file listed in `desktop_app/tests/fixtures` or documented as intentionally ephemeral?

## 2) Privacy and redaction
- [ ] Does the fixture contain any real person names, addresses, or signatures from users?
- [ ] Is `contains_pii` set to `yes`/`no`/`unknown`?
- [ ] If PII is present, is `redacted` marked `yes` or `partial` with notes?
- [ ] If `redacted` is `partial`, is there a migration ticket or remediation plan?

## 3) Coverage and realism
- [ ] Does this fixture target at least one explicit test pathway in `desktop_app/tests` or `tests`?
- [ ] Are edge conditions represented (noise, layout density, occlusion, rotation) where applicable?

## 4) Governance
- [ ] Is `reviewed_on` updated in the manifest?
- [ ] Are there acceptance criteria for the fixture in tests and docs?
- [ ] Is the manifest validation status clean: `python3 tools/validate_test_data_manifest.py --manifest docs/test_data_manifest.md --repo-root .`?

## 5) Artifact hygiene
- [ ] Are related diffs limited to fixture content and the manifest (and any expected test updates)?
- [ ] If large fixture churn occurs, is the reason documented and intentional?
