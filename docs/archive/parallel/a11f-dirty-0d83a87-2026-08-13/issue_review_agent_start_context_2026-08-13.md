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
