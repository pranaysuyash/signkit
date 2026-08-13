# Issue review: agent-start full retrieval context refresh

Date: 2026-08-13
Status: Open infrastructure dependency
Owner: Workspace tooling

## Symptom

The canonical refresh command returns success from the shell wrapper but emits
the following diagnostic during a full refresh:

```text
zsh:16: no such file or directory: /Users/pranay/Projects/workspace_memory/.venv/bin/python
```

The generated context then contains `_Search failed for this collection/query._`
for project and shared retrieval sections. A bounded `--skip-index --quiet`
refresh completes and produces `_Fast mode (--skip-index): retrieval skipped ..._`,
which is expected fast-mode behavior and not retrieval health.

## Reproduction evidence

```bash
timeout 120 /Users/pranay/Projects/agent-start \
  --project Data_Science/computer_vision/proj6/signature-extractor-app \
  --quiet
```

Observed exit code: `0`, with the missing interpreter diagnostic above.

Static inspection shows:

- `/Users/pranay/Projects/agent-start` selects
  `/Users/pranay/Projects/workspace_memory/.venv/bin/python`.
- That interpreter does not exist.
- The only current `memsearch` file is a shell stub that exits `0`.
- The workspace runbook says `projects-memory setup` recreates the environment
  with `uv` and Python `>=3.13`.
- The setup script removes and recreates the exact `.venv` directory, so that
  action requires an explicit workspace-tooling repair decision rather than a
  silent change from a project agent.

## Impact

Project motto propagation and generated context formatting can succeed, but
agents receive no searchable project or shared retrieval context. The wrapper's
success status is therefore misleading for full refreshes and can cause the
`L0-08` propagation task to be mistaken for `L0-11` retrieval health.

## Closure criteria

Workspace tooling owner must:

1. Preserve or rebuild the workspace memory environment using the documented
   setup path, without deleting source Markdown or derived indexes.
2. Verify the real `memsearch` executable and Python interpreter exist and are
   runnable.
3. Run a full project sync/index or an equivalent verified retrieval refresh.
4. Confirm context sections contain retrieval results or an explicit, truthful
   unavailable status, and make the wrapper return non-zero when its required
   interpreter is missing.
5. Re-run `agent-start` within the bounded timeout and attach command output and
   generated context hashes to the Product Owner backlog.

## Current evidence boundary

This review is Tier 1 static plus command-execution evidence. It does not claim
that workspace memory indexing is repaired, and it does not authorize deleting
or recreating the shared `.venv`.

## Addendum (2026-08-13): bounded full-refresh result

The bounded command was rerun from the canonical checkout:

```bash
/opt/homebrew/bin/timeout 90 /Users/pranay/Projects/agent-start \
  --project Data_Science/computer_vision/proj6/signature-extractor-app \
  --quiet
```

The shell reported exit code `0`, but emitted:

```text
zsh:16: no such file or directory: /Users/pranay/Projects/workspace_memory/.venv/bin/python
```

The generated context timestamp advanced to `2026-08-13T10:21:51Z`, while all
retrieval sections contained `_Search failed for this collection/query._`.
This is therefore a repeatable false-success and retrieval-health failure, not
closure of RECON-05. The closure criteria above remain unchanged. The generated
context files were restored after capture because they contain only the failed
refresh output and are derived artifacts.

## Addendum (2026-08-13): full-refresh false-success guard

The shared `/Users/pranay/Projects/agent-start` wrapper now fails closed before
source sync or retrieval when a non-fast refresh cannot find its configured
workspace Python interpreter or when the `memsearch` entry point does not
advertise the required CLI commands. This preserves the intentional
non-blocking `--skip-index` path while preventing a full refresh from claiming
success on missing or placeholder retrieval tooling.

Current verification:

- Before the guard, the full refresh returned shell exit code `0` while
  reporting `zsh:16: no such file or directory:
  /Users/pranay/Projects/workspace_memory/.venv/bin/python` and generating
  failed retrieval sections.
- After the guard, the same full refresh returns exit code `1` with the
  actionable `workspace memory Python interpreter not found` diagnostic, S2.
- `agent-start --skip-index --quiet` still returns exit code `0` and generates
  explicit `_Fast mode (--skip-index): retrieval skipped ..._` sections.
- `AGENT_START_SKIP_INDEX_RETRIEVE=1 agent-start --skip-index --quiet` now also
  returns exit code `1`; the quiet flag no longer masks an explicitly requested
  retrieval attempt, S2.
- The configured `memsearch` file is still a 17-byte shell `exit 0` stub, and
  the workspace Python interpreter is still absent. Rebuilding the shared
  environment and proving real indexing/retrieval remain open and require the
  documented workspace-tooling setup path.

The current truthful fast-mode context hashes are:

```text
SESSION_CONTEXT.md       0a96aa5f48567df0fd0fd1bd7cec61de1661445a52857397876210b4bb77ebe6
AGENT_KICKOFF_PROMPT.txt b9c0119cd9d26d8383a3e7b21db652573cf3c779b0958136e90e0ecda27b76e7
STEP1_ENV.sh             5a8a24dfe122d7d38f282b4c55898eb5b04d382cd2fded5e055b98e98f0f84a8
```

## Addendum (2026-08-13): project-local doctrine override

A later context refresh exposed a second source-of-truth conflict. The shared
generator synchronized workspace Doctrine 6.0 into this project and removed
the tracked `motto_v5.md`, even though the project instruction stack and the
operator's release brief designate `motto_v5.md` as the more-specific project
doctrine. The deleted file was restored byte-for-byte from `HEAD` with SHA-256
`f1ade186d46bf2e20e9eebd56ceca3a733711671471198284828482659524840`.

The generator now detects an existing project-local `motto_v5.md`, retains it
as the selected doctrine, and leaves the workspace-wide Doctrine 6.0 symlink
separate. A fresh `agent-start --project ... --skip-index --quiet` run exits
`0`, retains the project file, and regenerates `docs/context/agent-start/*`
with the local path, version `5`, matching SHA-256, and explicit provenance.
The workspace symlink was restored after verifying that the generated regular
copy matched `/Users/pranay/Downloads/OPERATING_DOCTRINE.md`; that copy remains
preserved at `/Users/pranay/Projects/OPERATING_DOCTRINE.md.generated-copy-20260813`.

This closes the project-local determinism portion of L0-11. Shared retrieval
rebuild, real indexing/search, and provider/runtime availability remain open
under RECON-06.

## Addendum (2026-08-13): repeated-refresh verification and installer hardening

The first follow-up commit exposed that the shared generator and its hook
installer had been overwritten back to the workspace Doctrine 6.0 defaults by
another concurrent refresh. The live tools were rechecked and corrected again:
`/Users/pranay/Projects/agent-start` now selects a project-local
`motto_v5.md` before workspace Doctrine 6.0, skips synchronization of that
more-specific file, and retains the workspace Doctrine symlink separately.
`/Users/pranay/Projects/workspace_memory/scripts/install_git_precommit_agent_hook.py`
now emits hooks that choose `motto_v5.md` when present and otherwise fall back
to `OPERATING_DOCTRINE.md`.

Two consecutive `agent-start --project ... --skip-index --quiet` runs exited
`0`, left the project motto byte-identical to `HEAD` with SHA-256
`f1ade186d46bf2e20e9eebd56ceca3a733711671471198284828482659524840`, and
regenerated context that names the project motto, version `5`, and explicit
workspace Doctrine 6.0 separation. The generated root Doctrine duplicate was
classified as ignored runtime output and removed after hash preservation.

## Addendum (2026-08-13): live fast-refresh source-selection regression

The bounded fast refresh was rerun from the canonical clean checkout after the
earlier guard correction:

```bash
/opt/homebrew/bin/timeout 45 /Users/pranay/Projects/agent-start \
  --project Data_Science/computer_vision/proj6/signature-extractor-app \
  --skip-index --quiet
```

It returned exit code `0`, but the result was unsafe and not deterministic:

- `docs/context/agent-start/STEP1_ENV.sh` selected
  `/Users/pranay/Downloads/OPERATING_DOCTRINE.md` instead of the project-local
  `motto_v5.md`.
- The generated session context described workspace Doctrine 6.0 as the
  project doctrine.
- The tracked project-local `motto_v5.md` was deleted.
- The six generated context files were modified.
- The live `/Users/pranay/Projects/motto_v5.md` alias was already absent.

The generated files and `motto_v5.md` were restored byte-for-byte from `HEAD`
after capture; the checkout is clean and the project-local file still hashes
to `f1ade186d46bf2e20e9eebd56ceca3a733711671471198284828482659524840`.
This is command-execution evidence of a shared-tool regression, not a product
closure. It supersedes the earlier addendum's claim that two consecutive fast
refreshes retained the project doctrine. `RECON-26` tracks the required
source-selection and retention fix; `RECON-06` remains open for the shared
runtime rebuild and real retrieval proof.
