# Playwright E2E tests

Run tests:

```bash
cd web/e2e
npm install --no-audit --no-fund
npx playwright install --with-deps
npm test
```

Visual snapshot tests
---------------------

To generate/update visual baseline snapshots for Playwright tests:

```bash
cd web/e2e
npm install --no-audit --no-fund
npx playwright install --with-deps
npx playwright test --update-snapshots
```

Commit generated snapshots to the repo so CI comparisons use the baseline snapshots.

ContractDesk workspace proof
----------------------------

The ContractDesk workspace browser proof uses the canonical backend proof
surface and does not use a second static server. Start the backend proof server
with its keep-running option, then run the focused spec with the installed
Playwright CLI:

```bash
TMPDIR=/var/tmp .venv/bin/python tools/run_contractdesk_web_proof.py --host 127.0.0.1 --port 8872 --keep-running
# In a second terminal:
/opt/homebrew/bin/playwright test web/e2e/specs/contractdesk_workspace.spec.js --config=web/e2e/playwright.config.js --reporter=line
```

This proves the browser can load the live workspace mount and observe the
local-companion, cloud metadata-only, and source-deletion boundaries. It does
not prove hosted document processing, signing, or legal certificate behavior.
