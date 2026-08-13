# Controlled Signing Workflow Launch Pack (v1)

## What is included in v1

- Authorized multi-field recipe authoring
- Exact-template unmatched queue and review lane
- Folder-based intake from designated unsigned folder
- Signed output folder publication with atomic write semantics
- Grant-based execution with expiry/usage caps
- Receipt export and recovery controls

## Pre-launch checklist

1. Approvals and boundaries
   - Confirm decision-gate decisions are approved.
   - Verify legal wording in UI and help docs uses “authorized visual signature application”.
2. Technical readiness
   - Migration from existing template format validated.
   - Secure store adapter tested in fail-closed mode.
   - Folder monitor recovery test completed.
3. Operational readiness
   - Runbook published to operators.
   - Emergency stop and grant revoke process tested.
   - Incident response contact path confirmed.

## Operator runbook

### Start-up

1. Launch SignKit and open Workflow Dashboard.
2. Validate workflow is unlocked with the right grant active.
3. Confirm watched folders and output folder are distinct.
4. Run one dry-run on sample docs.

### Runtime

- If jobs fail:
  - Check failure reason.
  - Retry when transient (IO/stability issues).
  - Move to quarantine for review-required failures.
- If signs are not expected:
  - Pause workflow.
  - Inspect matcher class and job detail state.
  - Validate recipe drift warnings.

### Shut-down

- Revoke temporary grants if batch process is complete.
- Export receipts for the period.
- Archive/keep execution logs per retention policy.

## Incident playbook

- **Unauthorized run blocked**
  - Verify grant validity and principal role.
  - Review denial reasons.
- **Excessive false matches**
  - Pause workflow.
  - Move to manual mode and re-calibrate matcher.
- **Signing service fails repeatedly**
  - Confirm key store availability.
  - Check disk/permission constraints.
  - Restart workflow after issue is fixed.

## Go-live acceptance

- 0 unauthorized runs on invalid grants
- Deterministic exact-match success for approved corpus
- Review queue contains all non-exact/ambiguous inputs
- Receipt export includes complete lineage
- Emergency lock tested and effective within one action
- Signed decision on native split for mac based on W16 evidence and the split decision record:
  - [gtm_mac_runtime_split_record.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/gtm_mac_runtime_split_record.md)
  - [w16_go_no_go_matrix.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/w16_go_no_go_matrix.md)

## Marketing and pricing collateral references

- [gtm_persona_flows_pricing_screens_pack.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/gtm_persona_flows_pricing_screens_pack.md)
  - use for launch messaging, pricing copy, and screen-level rollout targets.
- [launch_deck_v1.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/launch_deck_v1.md)
  - use as a shareable internal launch brief (v1).
- [workflows_screen_and_task_execution_plan.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/workflows_screen_and_task_execution_plan.md)
  - use for implementation sequence and developer handoff.
