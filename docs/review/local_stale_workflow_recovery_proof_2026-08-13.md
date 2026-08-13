# Local stale workflow recovery proof

Date: 2026-08-13
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Scope: local desktop workflow store and operator recovery surface
Evidence tier: Tier 2 local command execution, S1

## Contract

A process interruption can leave a durable workflow job in `VALIDATING`,
`MATCHING`, `PROCESSING`, or `VERIFYING`. Those states are not safe to resume
blindly because a planned output may exist, a source may have changed, or a
signing operation may have stopped between side effects. The local operator
surface now exposes `Recover stale` as an explicit action.

Recovery uses a caller-supplied age threshold, examines only transient states,
and moves an old job to `NEEDS_REVIEW` with `ERR_WORKFLOW_INTERRUPTED`. It
records the state event and preserves the attempt count. It does not retry,
delete, or overwrite a planned output. A fresh transient job remains in its
current state, and an invalid timestamp is left untouched because the system
cannot safely infer its age.

The primary copy is bounded:

> The local workflow stopped before completion. Review the input and any planned output before retrying.

Technical details remain in the metadata-only workflow receipt and event store.

## Verification

Command:

```bash
./.venv/bin/python -m pytest \
  desktop_app/tests/test_workflow_engine.py \
  tests/test_operator_content.py \
  desktop_app/tests/test_workflow_screen_smoke.py -q
```

Result: `36 passed`.

The focused tests prove:

- an old transient job is moved to `NEEDS_REVIEW` with zero additional retry attempts;
- the interruption code and durable event are recorded;
- a fresh transient job remains unchanged;
- an invalid timestamp is not guessed as stale;
- operator copy asks for planned-output review and does not expose local paths;
- the workflow console initializes with the recovery control present in the local Qt smoke surface.

## Boundary

This closes the local source/state recovery contract only. It does not prove
packaged cross-platform process interruption, filesystem permission recovery,
assistive-technology behavior, hosted workflow recovery, provider behavior,
or legal-signature validity. Those remain separate gates under `L1-08`,
`RECON-10`, and the hosted/provider backlog.
