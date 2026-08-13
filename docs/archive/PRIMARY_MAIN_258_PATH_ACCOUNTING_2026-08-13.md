# Original primary-main path accounting

Date: 2026-08-13
Canonical checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Purpose: account for every path changed in the original dirty primary `main`
before reconciliation, independently from the later 92-path implementation
promotion count.

## Authoritative refs

```text
common baseline:       0d83a87
primary dirty snapshot: ee12dba, parent 0d83a87
primary archive ref:    archive/main-dirty-0d83a87-2026-08-13 -> 874a6b7
incoming baseline:      17f644b
current local main:     51a3769
```

The original primary snapshot was captured before reconciliation with:

```bash
git diff 0d83a87..ee12dba
```

Its authoritative result was:

```text
258 files changed, 21541 insertions(+), 759 deletions(-)
```

The complete dirty snapshot remains recoverable from the immutable archive
ref. The archive commit also preserves the original deleted asset as a
recorded deletion, while its bytes remain available from the `0d83a87` parent.

## Path disposition

| Disposition | Count | Meaning |
| --- | ---: | --- |
| Original changed paths | 258 | The complete primary dirty diff from `0d83a87` to `ee12dba` |
| Non-deleted primary paths | 257 | All original paths except the explicitly deleted signature image |
| Same path exists in current `main` | 256 | The path is still present in the current tree, whether exact or reconciled |
| Exact primary content still current | 218 | Current blob equals the primary snapshot blob |
| Present with reconciled content | 38 | Current path exists but a later incoming, nitpicked, or superseding version won |
| Original deleted asset | 1 | `512px-Mohammad_Rafiquzzaman_signature.jpg`, recoverable from `0d83a87` |
| Historical ADR absent at original path | 1 | `docs/decisions/ADR-0145-signkit-replacement-visual-direction.md`, preserved at the archive snapshot path and superseded by the canonical current ADR-0145 |

The two paths not present at their original path are therefore intentional
dispositions, not unaccounted loss:

```text
512px-Mohammad_Rafiquzzaman_signature.jpg
docs/decisions/ADR-0145-signkit-replacement-visual-direction.md
```

The historical ADR is preserved at:

```text
docs/archive/parallel/main-dirty-0d83a87-2026-08-13/decisions/ADR-0145-signkit-replacement-visual-direction.md
```

## Why only 92 paths were in the implementation promotion commits

The later implementation commits are a focused promotion series, not a count
of the entire original dirty primary diff:

```text
17f644b -> b631e35 -> 6d0e54e -> 5798235
```

Of the 257 non-deleted primary paths:

| Content comparison | Count | Disposition |
| --- | ---: | --- |
| Primary content already identical in incoming `17f644b` | 198 | Already present before the focused promotion series |
| Current content exactly equals primary snapshot | 218 | Preserved without content change, including overlap with incoming |
| Current content equals incoming but not primary | 16 | Incoming version superseded the primary variant |
| Current content equals common baseline but not primary | 1 | `DESIGN.md`, whose dirty primary edit was not retained as canonical |
| Current content differs from primary, incoming, and common baseline | 21 | Reconciled or superseding current implementation or documentation |

The 92 unique paths in `b631e35`, `6d0e54e`, and `5798235` are the focused
implementation and evidence promotion series. They intentionally overlap some
of the original primary paths and are not a replacement count for the full
primary diff. Their per-commit counts sum to 94 because
`desktop_app/app_bootstrap.py` and
`tools/mutation_check.py` are each touched twice.

The complete implementation comparison is reproducible with:

```bash
git diff --stat 17f644b..5798235
git diff --name-status 17f644b..5798235
```

The complete original-primary comparison is reproducible with:

```bash
git diff --stat 0d83a87..ee12dba
git diff --name-status 0d83a87..ee12dba
```

## Current conclusion

The original 250-plus primary work was not reduced to the 92-path series.
Most of it was already present in the incoming `17f644b` baseline, 218 paths
remain byte-identical to the primary snapshot, 38 paths have explicit
reconciled content, and the two paths absent from their original location have
documented deletion or supersession dispositions. The full historical primary
stream remains recoverable through
`archive/main-dirty-0d83a87-2026-08-13`.

This artifact is an accounting record. It does not claim hosted deployment,
provider activation, signed packaging, or production readiness.
