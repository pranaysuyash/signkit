# ContractDesk Idempotency Proof Manifest (Synthetic)

**Date:** 2026-08-12  
**Run ID:** `contractdesk-api-idempotency-2026-08-12`  
**Scope:** Workspace transition idempotency regressions for route/service boundaries and actor-scope behavior  
**Decision Gate:** Stage 1 API runtime hardening lane  

## Inputs

| Path | SHA-256 |
| --- | --- |
| `backend/tests/test_workspace_router.py` | `43fee7959ec2cd4e8a88689cbca05046a63006a06bb07bbfcd8f62d66a8082ee` |
| `backend/tests/test_workspace_service.py` | `664c0bc77ac768e66680f29ee25affd4d1d9ad918acf84a417b2321c54380edb` |
| `backend/app/services/workspace.py` | `9a05be41eca8da79cc93ecc2c86ef022152c8ba000492883fbda5436479a7df7` |
| `backend/app/routers/workspace.py` | `508799cad8359b36616609646244ba10f9a4756b93fc62c4724728c758d1da1b` |
| `backend/app/models/workspace.py` | `6ee0b028d278b8f245ba458d8b77c53d808869c9922ca725bd553b7e756a2b0a` |
| `backend/app/schemas/workspace.py` | `4d11f3acc53677621479130b406bbfe78b20e1f71916ab997924fce03680ba1c` |

## Command

```bash
. .venv/bin/activate && pytest backend/tests/test_workspace_router.py backend/tests/test_workspace_service.py -q --junitxml=docs/expansion/artifacts/contractdesk_api_idempotency_2026-08-12.xml | tee docs/expansion/artifacts/contractdesk_api_idempotency_2026-08-12.log
```

## Output paths

- `docs/expansion/artifacts/contractdesk_api_idempotency_2026-08-12.xml`
- `docs/expansion/artifacts/contractdesk_api_idempotency_2026-08-12.log`

## Result

- `2026-08-12T12:30:44Z`
- **Status:** PASS
- Tests executed: 13 passed
- Command runtime: `2.29s`
- Scope verified:
  - route-level duplicate-replay idempotency
  - route-level cross-state keyed transition replay regressions
  - service-level actor-scope idempotency behavior
  - route conflict behavior without `idem_key`

## Reproducibility checklist

- Re-run command in same repo root with the same input SHA-256 values to re-generate artifacts.
- Evidence is valid until tracked input files change; rerun if any file listed in **Inputs** mutates.
