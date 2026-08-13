# Template -> Recipe Migration Checklist

## Migration objectives

- Keep existing templates editable where possible for user continuity.
- Introduce versioned multi-field recipe behavior without losing legacy data.
- Ensure no silent data loss during one-step and rollback paths.

## Migration phases

### Phase 1: Pre-flight validation

1. Capture count of legacy templates and fields from `template_store`.
2. Record validation failures for:
   - missing required fields,
   - malformed JSON,
   - unresolved signature file paths.
3. Snapshot template store file before write migration.

### Phase 2: Read conversion

4. Parse one legacy template at a time.
5. Map legacy `signature_path` to `signature_asset_ref` only if asset exists.
6. Expand scalar placement into first-class `FieldBinding` array with one slot.
7. Default `field_kind` to `signature` when unknown.
8. Populate `recipe.version = 1`, `status='draft'`.

### Phase 3: Versioning and lock-in

9. Persist new `recipe_version` entity.
10. Keep immutable old recipe pointer for audit-only access.
11. Mark migration status on recipe (`migrated=true`, `migration_source_legacy=true`).

### Phase 4: Invariant checks

12. Verify every migrated recipe:
   - has at least one binding,
   - does not reference raw file paths,
   - has deterministic hash computed.
13. Reject migration for recipes with unresolved assets and route to manual remediation list.

### Phase 5: Rollback and rollback verification

14. Provide `--rollback` path to restore legacy file snapshot.
15. Verify rollback leaves no partially written dual-truth rows.
16. Confirm legacy app mode can still read pre-migration snapshots.

## Human-in-the-loop controls

- Migration dry-run mode must be available before write.
- Any unresolved assets appear in `migration_issues.json`.
- Product operator receives migration report before activation.

## Delivery artifacts

- `migration_report.json`
- `migration_issues.json`
- `migration_audit_log` with before/after ids and actor.

## Rollback criteria

- Any missing legacy template cannot be mapped and recovered.
- Any migration step throws an unrecoverable parse error.
- Signature asset mapping confidence below 95% in test set.
