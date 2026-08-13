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
