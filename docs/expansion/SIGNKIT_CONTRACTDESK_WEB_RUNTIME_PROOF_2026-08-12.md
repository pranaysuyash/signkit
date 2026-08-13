# SignKit ContractDesk Web Runtime Proof

Date: 2026-08-12
Scope: Stage 1 local-companion control-plane proof slice
Owner: QA/Runtime with Frontend and Backend implementation lanes

## Decision and boundary

The canonical browser surface is the backend-mounted `web/cloud_workspace` app at `/workspace-app/`. It uses the existing `/auth` and `/workspace` routes. This proof does not introduce a second API route, signing engine, hosted API, document store, identity verification flow, or legal signing certificate.

The proof fixture is synthetic and metadata-only. `EXPORTED` means a deterministic control-plane audit manifest was produced in the browser state model; it does not mean a signed document or production artifact was created.

## Runtime evidence

Browser: fresh Playwright context against the existing SignKit backend on `http://127.0.0.1:8001`.

Observed request and workflow evidence:

- `POST /auth/register` returned `201 Created` for a syntactically valid non-reserved fixture address.
- `POST /auth/login` returned `200 OK`.
- `GET /workspace/templates` and `GET /workspace/executions` returned `200 OK`.
- `GET /workspace-app/proof-fixtures.json` returned `200 OK`.
- The deterministic packet replay displayed `RECEIVED`, `READY FOR REVIEW`, `APPROVED`, `SIGNED`, and `EXPORTED` in order.
- The receipt trail displayed six chronological events, including review, approval, signing-stage marker, and deterministic manifest export.
- The synthetic manifest displayed `workflow`, `input_hash`, `decision_rules`, `stages`, `last_action`, `last_status`, and synthetic output metadata.
- A negative registration using a reserved `.test` domain returned backend `422` and the browser rendered the actionable validation message instead of `[object Object]`.

Evidence tier: Tier 4 runtime/manual observation. The browser path was exercised through the real mounted backend and real local database/API boundary, with synthetic fixture data only.

## Code changes required by runtime proof

- `web/cloud_workspace/index.html` now uses same-directory asset URLs for `styles.css` and `app.js`, so the surface works under the canonical `/workspace-app/` mount and a direct static preview.
- `web/cloud_workspace/app.js` now loads `proof-fixtures.json` from its same directory.
- `web/cloud_workspace/app.js` now formats string, object, and validation-array API errors into operator-readable messages.

## Reproducible runner and synthetic package

- Runner: `./.venv/bin/python tools/run_contractdesk_web_proof.py`
- Runner result: `PASS` on deterministic `http://127.0.0.1:8871`, with health, mounted page, `app.js`, `styles.css`, and fixture checks all returning `200`.
- Browser handoff: `./.venv/bin/python tools/run_contractdesk_web_proof.py --keep-running`, followed by a fresh browser context against `/workspace-app/index.html`.
- Synthetic package: `docs/expansion/artifacts/contractdesk_stage1_synthetic_receipt`
- Package ID: `contractdesk-stage1-proof-20260812-0a788804d744`
- Package contents: `manifest.json`, `receipt.ndjson`, and `package_index.json`.
- Package hashes: manifest `8a9b8de5b8775e54a7db3c5bcf4505cf2e9f674a42571ff733e6e7de519d1dae`; receipt `16ff3c2eb446ed5858385577a604bc5cffd6a1edbadeddcce07e7459cd0dfef3`; index `311a5a6db0e1e017a3c7b3e79831c6e4fa561f4ff121628bae308d1ff3db43af`.
- Package semantics: `synthetic=true`, `signature_status=not_signed`, `document_artifact=null`, and `signature_artifact=null`.

## Static and targeted checks

- `node -c web/cloud_workspace/app.js`: passed, S1 static syntax evidence.
- `python -m json.tool web/cloud_workspace/proof-fixtures.json`: passed, S1 fixture syntax evidence.
- `.venv/bin/pytest backend/tests/test_workspace_router.py -k contractdesk_proof_slice_smoke_path -q`: passed, 1 passed and 5 deselected, S1 targeted test evidence. This test proves the route slice executes; it has not been mutation-tested in this continuation.

## Environment findings

- Port `4173` was already serving an unrelated local app and was not used as SignKit evidence.
- Port `8000` was already serving an unrelated local service. The existing SignKit backend on port `8001` was used without changing or stopping the unrelated process.
- The documented Browser Daemon executable under `/Users/pranay/.claude/skills/playwright-skill/browser-client.js` was unavailable. Installed Playwright MCP browser controls supplied the runtime evidence instead. A reusable local proof runner remains an operational follow-up.

## Open tasks and closure criteria

- Hosted API product remains deferred until identity, tenancy, idempotency, versioning, observability, recovery, legal, and commercial gates are approved and implemented.
- Production-like signed output packaging remains deferred. Closure requires a real artifact contract, cryptographic/signing boundary, storage policy, and Tier 3+ integration evidence.
- Real signed output packaging remains open. Closure requires a cryptographic/signing boundary, signer identity, storage and retention policy, recovery behavior, legal wording, and Tier 3 integration evidence. The synthetic package is not a substitute for that contract.
