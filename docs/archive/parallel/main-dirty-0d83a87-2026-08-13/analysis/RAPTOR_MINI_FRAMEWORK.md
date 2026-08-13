# Raptor mini — Moved

This file was moved to the repo root at `docs/RAPTOR_MINI_FRAMEWORK.md`.
Please see that file for the verification & analysis framework used for auditing docs and code.

This duplicate exists here for historical purposes and will be removed in a later housekeeping pass. For now, reference the root-level file.

Core steps

1. Read the doc: fully read the targeted doc and extract the feature list and intentions. Note proposed owner/priority if present.
2. Search the repo: grep for key symbols (class names, functions, keywords) that map to doc claims. Check common patterns:
   - UI: QIcon, setWindowIcon, setStyleSheet, style.py, icons.py
   - Processing: OpenCV usage (cv2), PIL Image operations
   - Backend: FastAPI endpoint names, OpenAPI docs, routers
   - Tests: pytest, tests/, integration test patterns
3. Validate each claim: for every doc bullet, look for evidence in the codebase. If a feature is fully implemented, mark it ✅. If partial (e.g., QIcon exists but not all icons), mark ⚠️. If missing or outdated, mark ❌.
4. Add references and diffs: for each item change the doc to include a `ref:` link to the file. Prefer examples, file paths and line snippets if helpful.
5. Suggest next steps: provide concrete, small, actionable tasks (test, UI, unit test, API docs) and owners.
6. Marketability check: for features that are product or premium (e.g., style transfer), add a short marketability paragraph: market fit, monetization options, MVP scope, and risks.
7. Clean up: fix simple lint issues (MD) and run static checks to ensure the doc is clean.

Template for each audit

- File: (doc filename)
- Date: YYYY-MM-DD
- Summary: One-liner
- Findings: bullet list of ✅/⚠️/❌ with `ref:` path
- Market fit: short paragraph if applicable
- Next steps: 1-3 actionable tickets with owners

Reusing the framework

- When you ask me to audit a doc, I will create or update a child file under `docs/analysis/` with the same name using this template and sign it with my name and date.

Notes

- This framework assumes a Python/Qt/FastAPI stack. Tailor the grep tokens for other stacks.
- The template focuses on small, verifiable incremental work and supports launching quick POCs.

Addendum: I committed this under the model name to ensure you can ask "use the RAPTOR_MINI_FRAMEWORK" and I'll follow the exact steps above.
