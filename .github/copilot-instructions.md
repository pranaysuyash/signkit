## Quick repository snapshot (big picture)

<!-- PROJECTS_MEMORY_AGENT_ALIGNMENT_BEGIN -->

## Projects-Level Agent Alignment (Workspace Memory)

**Purpose:** ensure any agent/LLM (Codex, Copilot, Claude Code, Qwen, GLM, etc.) starts aligned with the same workspace memory + project context.

### Step 0 (first time in this folder)
Generate the per-project context pack:
```bash
/Users/pranay/Projects/agent-start
```

### Step 1 (per shell)
Load the shared defaults for this project session:
```bash
source Docs/context/agent-start/STEP1_ENV.sh
# Or (no file read) print exports and eval:
/Users/pranay/Projects/agent-start --print-step1 --skip-index
```

### Step 2 (generate aligned context pack)
```bash
/Users/pranay/Projects/agent-start
```

Outputs:
- Canonical project-local pack:
  - `Docs/context/agent-start/SESSION_CONTEXT.md`
  - `Docs/context/agent-start/AGENT_KICKOFF_PROMPT.txt`
  - `Docs/context/agent-start/STEP1_ENV.sh`
- Compatibility mirrors when present:
  - `.agent/SESSION_CONTEXT.md`
  - `.agent/AGENT_KICKOFF_PROMPT.txt`
  - `.agent/STEP1_ENV.sh`
  - `frontend/docs/context/agent-start/*`

### Automation (already configured)
- Terminal auto-loads `Docs/context/agent-start/STEP1_ENV.sh` when you `cd` into a project under `/Users/pranay/Projects` (zsh hook).
- VS Code/Antigravity can run `agent-start --skip-index` on folder open via `.vscode/tasks.json`.

### How agents should use this
- Provide the canonical `Docs/context/agent-start/AGENT_KICKOFF_PROMPT.txt` and `Docs/context/agent-start/SESSION_CONTEXT.md` as the first context for the agent.
- If sources conflict, the agent must cite concrete file paths and ask before proceeding.
- If the canonical context pack is missing or stale, run `/Users/pranay/Projects/agent-start --skip-index` before planning changes.
- Treat `.agent/` files as compatibility mirrors only.
- Do not start implementation until `Docs/context/agent-start/AGENT_KICKOFF_PROMPT.txt` and `Docs/context/agent-start/SESSION_CONTEXT.md` are loaded.

### Mandatory agent operating mandate
- Begin every substantial task by refreshing ground truth: read the applicable instruction stack, repo-local `AGENTS.md`/`CLAUDE.md`, and any Qwen, Codex, Copilot, or other agent-specific instruction files relevant to the repo.
- Check the current codebase, docs, worklogs, and project status before planning or coding. Parallel agents may have changed files, decisions, or docs since the last session.
- Treat drift as normal: before editing and again before finalizing, re-check the files and docs you rely on, then adapt rather than assuming older context still holds.
- Use relevant skills and workflow guidance after checking the configured skill locations. Do not default to one toolset when a better domain skill exists.
- Think from first principles and optimize for long-term, scalable, architecturally sound solutions. Existing code is evidence, not a boundary; if current implementation no longer fits the product reality or architecture, propose or implement the proper path.
- Avoid building duplicate or parallel systems. Extend canonical routes, pipelines, validation, docs, and tools unless the project explicitly calls for a new replacement path.
- Git safety: read-only git inspection is allowed; no destructive commands, staging, commits, pushes, resets, or checkouts without explicit permission in the current conversation.
- Research online when facts may be current, external, or uncertain; cite sources when research affects decisions.
- Test changes, verify for regressions, and document findings, decisions, open questions, and follow-up work in durable project artifacts.

### Mandatory commit gate
Install or refresh the managed repo-local git hooks. They resolve the repo's effective hook path, block commit creation in `prepare-commit-msg` until the current full `motto_v3.md` has a fresh attestation, then enforce objective diff checks plus commit trailers in `pre-commit` and `commit-msg`:
```bash
python3 /Users/pranay/Projects/workspace_memory/scripts/install_git_precommit_agent_hook.py
```

Refresh the current repo's motto attestation before committing:
```bash
python3 /Users/pranay/Projects/workspace_memory/scripts/attest_motto.py --repo "$PWD"
```

### Shared Idea Pad Protocol (Required)
- Canonical file: `/Users/pranay/Projects/idea_pad/IDEA_PAD.md`
- Raw capture file: `/Users/pranay/Projects/idea_pad/IDEA_DUMP.md`
- Do not create per-model primary copies of the idea pad.
- Do not overwrite the whole file; use append/update workflow with validation.
- Capture rough ideas in `IDEA_DUMP.md`, then promote high-signal items into `IDEA_PAD.md`.
- Before edits:
```bash
python3 /Users/pranay/Projects/idea_pad/scripts/idea_pad_tool.py validate
```
- Add new ideas safely:
```bash
python3 /Users/pranay/Projects/idea_pad/scripts/idea_pad_tool.py add --title "<title>" --owner "<agent>" --type build
```
- After updates, refresh shared memory index:
```bash
cd /Users/pranay/Projects
./projects-memory index
```

<!-- PROJECTS_MEMORY_AGENT_ALIGNMENT_END -->

- Desktop-first application with a PySide6 (Qt) GUI and a FastAPI backend used for optional cloud features.
- Desktop frontend: `desktop_app/` (entry: `desktop_app/main.py`). Backend: `backend/app/` (entry: `backend/app/main.py`).
- Backend provides authentication and image extraction APIs under `/auth` and `/extraction`; uploaded images are stored under `uploads/images` for internal backend processing and are not publicly mounted.

## High-level architecture & why it matters

- Hybrid offline-first design: the desktop app starts an embedded or subprocess backend (see `desktop_app/backend_manager.py`) to enable cloud features while remaining functional offline using local extraction logic (`desktop_app/processing/extractor.py`).
- Local processing is the preferred fast path — `SignatureExtractor` has robust input validation and resource limits to prevent malicious files and DoS (magic numbers, size limits, PIL verify, path sanitization).
- Backend uses SQLAlchemy with optional Postgres; SQLite is used as a default fallback when `DATABASE_URL` is not set.

## Practical developer tasks and commands

- Run desktop app (dev):
  - `python -m desktop_app.main` (the app will auto-start the backend on an available port)
- Run backend (dev):
  - `uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001`
- Initialize or reset the DB (dev):
  - `python backend/setup_db.py` (creates/drops tables using SQLAlchemy models)
- Generate secure JWT_SECRET (if needed):
  - `python backend/generate_secret.py` (prints a 32-byte hex key — add to your `.env`)
- Small integration tests (scripts in `backend/`):
  - `python backend/test_auth.py` — generates `test_token.txt` for further tests (requires DB and backend running)
  - `python backend/test_upload.py` — exercises `/extraction/upload` using the test token

## Configuration & environment notes

- Key settings and `.env`: `backend/app/config.py` expects `JWT_SECRET` (required). Use `.env` at repo root or export env vars. Example: `DATABASE_URL=sqlite:///backend/data/app.db` and `JWT_SECRET=<secure value>`.
- Desktop config loader: `desktop_app/config.py` reads `.env` and validates `API_BASE_URL` and `UPDATES_URL`. Default API base URL: `http://127.0.0.1:8001`.

## Project-specific code patterns and conventions

- API endpoints in `backend/app/routers/` use FastAPI routers included in `backend/app/main.py`.
- Uploads mount and path: backend creates a user-writable `uploads/images` directory for internal use; no public `StaticFiles` mount for image serving is configured. See `UPLOADS_DIR` usage in `backend/app/routers/extraction.py`.
- Desktop backend management: `desktop_app/backend_manager.py` dynamically finds uvicorn or the backend script and starts it, falling back to an in-process server when packaged.
- Client & session lifecycle: `desktop_app/api/client.py` stores `session_id` and `last_request` in `desktop_app/state/session.py` which is the single-session state object shared across the app.
- Local processing implementation: `desktop_app/processing/extractor.py` is the offline extraction engine. Prefer it for offline-first behavior. It implements strong security checks (magic numbers, size/dimension limits, PIL validation) and robust session handling.

## Integration & security notes

- Local vs backend processing: Desktop `MainWindow` prefers `SignatureExtractor` for immediate, offline processing. The backend `process_image` mirrors its behavior — keep both implementations in sync for feature parity.
- Security: Validate `JWT_SECRET` and DB credentials; if using packaged app, `BackendManager` will persist a JWT secret in user data dir and default to SQLite to keep things robust.
- File uploads: Backend `/extraction/upload` expects `multipart/form-data` with a `file` field — desktop `ApiClient.upload_image()` does this correctly.

## Build, packaging, and tests

- Packaging: Use `build-tools/build.py` (PyInstaller wrapper) or native spec files under `build-tools/` to create platform-specific builds. The script includes helper options (`--one-file`, `--debug`, `--console`, `--create-scripts`).
- PDF features: The desktop app optionally uses `pypdfium2` and `pikepdf`. If you need PDF features, ensure these dependencies are installed; otherwise the `PdfTab` features will be disabled with a helpful message.
- Tests: Backend has runnable scripts under `backend/` (not pytest suites). Use these scripts for quick integration checks when backend and DB are running.

## Where to start for common changes

- Fix backend APIs: check `backend/app/routers/__init__.py`, `backend/app/routers/extraction.py`, `backend/app/routers/auth.py`, and `backend/app/main.py`.
- Fix client or UI behavior: `desktop_app/api/client.py`, `desktop_app/views/*`, and `desktop_app/main.py`.
- Update security or processing: `desktop_app/processing/extractor.py` and `backend/app/routers/extraction.py` (mirror logic).
- Packaging & build tweaks: `build-tools/build.py` and spec files in `build-tools/`.

If you'd like, I can add CI steps, Docker dev containers, or a Makefile to codify common runs (backend start, setup DB, run desktop app) — tell me which you prefer.
