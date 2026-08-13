# a11f worktree path accounting

Date: 2026-08-13
Canonical checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Purpose: account for the separate a11f worktree and its preserved tracked and
untracked files.

## Authoritative refs and worktrees

```text
common baseline:       0d83a87
a11f snapshot:         b8d024c, parent 0d83a87
a11f archive ref:      archive/a11f-dirty-0d83a87-2026-08-13
incoming clean ref:    17f644b
current local main:    3b85b12
a11f worktree:         /Users/pranay/.codex/worktrees/a11f/signature-extractor-app
eb41 worktree:         /Users/pranay/.codex/worktrees/eb41/signature-extractor-app
```

The a11f tracked snapshot was captured with:

```bash
git diff 0d83a87..b8d024c
```

Its authoritative result was:

```text
281 files changed, 20221 insertions(+), 758 deletions(-)
```

## Tracked-path disposition

| Disposition | Count | Meaning |
| --- | ---: | --- |
| a11f changed paths | 281 | Complete tracked diff from `0d83a87` to `b8d024c` |
| Non-deleted a11f snapshot paths | 280 | All paths except the explicit signature-image deletion |
| Same path exists in current `main` | 280 | No non-deleted a11f tracked path is absent from current `main` |
| Current content byte-identical to a11f snapshot | 234 | Preserved without content change |
| Current content differs from a11f snapshot | 46 | Incoming, reconciled, or superseding content is canonical in current `main` |
| a11f explicit deletion | 1 | `512px-Mohammad_Rafiquzzaman_signature.jpg`, recoverable from `0d83a87` |

The 46 differing paths are classified as 16 incoming-compatible versions, 4
common-baseline versions, and 26 current reconciled or superseding versions.
The exact path list is reproducible from the refs with:

```bash
git diff --name-status 0d83a87..b8d024c
```

## Untracked worktree artifacts

The a11f worktree has no uncommitted tracked changes. Its only untracked
directories are:

```text
.codex-test-tmp/
.wrangler/
```

These are test and deployment runtime outputs, not source files. They remain
on disk and were intentionally excluded from the immutable source archive.
They must not be deleted or added to the product tree without a separate
artifact-classification decision. The current inventory does not treat them as
lost work.

## eb41 incoming worktree

The eb41 worktree is detached at `17f644b`, has no tracked diff, and has no
untracked source files. It is identical to `origin/main` and is retained as a
clean incoming reference.

## Reproducible checks

```bash
git -C /Users/pranay/.codex/worktrees/a11f/signature-extractor-app status --short
git -C /Users/pranay/.codex/worktrees/a11f/signature-extractor-app diff --shortstat
git -C /Users/pranay/.codex/worktrees/eb41/signature-extractor-app status --short
```

## Current conclusion

The a11f worktree files were preserved in the immutable archive ref and are
represented in current `main` by exact content or documented reconciled
content. No non-deleted tracked a11f path is missing from current `main`. The
only untracked a11f items are runtime directories intentionally excluded from
source history and still present on disk.
