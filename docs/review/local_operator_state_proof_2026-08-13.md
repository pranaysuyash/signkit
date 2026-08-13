# Local operator state and recovery proof

Date: 2026-08-13
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Evidence tier: Tier 4 local disposable workflow observation

## Command

```text
TMPDIR="$PWD/.codex-test-tmp" ./.venv/bin/python tools/run_local_source_to_ready_proof.py
```

## Observed result

The reusable proof returned `status: pass` and exercised the complete local
source-to-ready path using disposable generated input:

- Signature extraction created a session and produced an RGBA result of
  `394 x 83` pixels.
- The encrypted local Vault round trip returned the exact extracted bytes.
- A deliberately forced signing failure produced `ERR_SIGNING_FAILED` and
  moved the job to `retry` after attempt `1`.
- The canonical retry path ran once more and reached `completed`.
- The final artifact receipt was verified with artifact SHA-256
  `05e27f5b3e8d2d0fe8b978bb89e2c696a895af1fe90de39629bbea4b5edb21b5`.
- The final passport reported `source_of_truth: local_workflow_store`,
  `topology: local`, `recovery_action: none`, and
  `data_boundary: metadata_only_no_document_bytes`.
- The proof reported `hosted_service_contacted: false` and
  `document_bytes_in_browser_workspace: false`.

## Scope boundary

This is Tier 4 local disposable evidence for extraction, Vault, controlled PDF
placement, forced failure, retry, passport projection, and verified visual
placement output. The receipt explicitly says
`visual_signature_placement_not_cryptographic_signature`.

It does not close malformed-input, timeout, partial-export, deletion-cleanup,
local-companion-outage, assistive-technology, cross-platform, provider,
hosted-migration, or legal-signature gates. `L1-08` remains in progress until
those state mappings have their own scoped controls and evidence.
