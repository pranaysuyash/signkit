"""Canonical human-facing labels for local workflow states and outcomes."""

from __future__ import annotations

from typing import Optional

from desktop_app.workflows.models import WorkflowState


_STATE_LABELS = {
    WorkflowState.QUEUED: "Queued",
    WorkflowState.VALIDATING: "Validating",
    WorkflowState.MATCHING: "Matching document",
    WorkflowState.PROCESSING: "Processing",
    WorkflowState.VERIFYING: "Verifying output",
    WorkflowState.COMPLETED: "Completed",
    WorkflowState.NEEDS_REVIEW: "Needs review",
    WorkflowState.RETRY: "Retry available",
    WorkflowState.FAILED: "Failed",
    WorkflowState.CANCELLED: "Cancelled",
}

_OUTCOME_COPY = {
    "ERR_AUTH_MISSING": "This action needs an active execution grant.",
    "ERR_AUTH_EXPIRED": "The execution grant has expired. Request a new grant before retrying.",
    "ERR_AUTH_REVOKED": "The execution grant was revoked. Request a new grant before retrying.",
    "ERR_WORKFLOW_INVALID": "The workflow configuration or input is not valid.",
    "ERR_WORKFLOW_STATE": "This action is not valid for the current workflow state.",
    "ERR_WORKFLOW_PAUSED": "The local workflow engine is paused. Resume it before continuing.",
    "ERR_MATCH_NONE": "The document did not match an approved recipe and needs review.",
    "ERR_MATCH_AMBIGUOUS": "The document match is ambiguous and needs review.",
    "ERR_JOB_QUARANTINED": "The job was moved to review and will not progress automatically.",
    "ERR_JOB_CANCELLED": "The job was cancelled by the operator.",
    "ERR_RETRY_FORBIDDEN": "This job cannot be retried in its current state.",
    "ERR_SIGNING_FAILED": "The visual output could not be created. Retry is available when safe.",
    "ERR_VERIFY_MISMATCH": "The output did not pass verification and needs review.",
    "ERR_OUTPUT_EXISTS": "The planned output already exists. Review the destination before retrying.",
    "ERR_IO_UNSTABLE": "The input or destination changed during processing. Stabilize it before retrying.",
    "ERR_OUTPUT_IO": "The output could not be written. Check the local destination and retry if safe.",
}


def _coerce_state(state: WorkflowState | str) -> Optional[WorkflowState]:
    if isinstance(state, WorkflowState):
        return state
    try:
        return WorkflowState(str(state))
    except ValueError:
        return None


def state_label(state: WorkflowState | str) -> str:
    """Return stable operator copy for a persisted workflow state."""

    normalized = _coerce_state(state)
    if normalized is not None:
        return _STATE_LABELS[normalized]
    raw = str(state).strip().replace("_", " ")
    return raw.title() if raw else "Unknown state"


def outcome_message(code: str | None, state: WorkflowState | str) -> str:
    """Return safe primary copy without exposing paths or raw exception text."""

    normalized = _coerce_state(state)
    if normalized is WorkflowState.COMPLETED:
        return "Completed successfully."
    if normalized is WorkflowState.CANCELLED:
        return "Cancelled. No further automatic processing will occur."
    if code and code in _OUTCOME_COPY:
        return _OUTCOME_COPY[code]
    if normalized is WorkflowState.NEEDS_REVIEW:
        return "Needs review before the workflow can continue."
    if normalized is WorkflowState.RETRY:
        return "Retry is available under the workflow contract."
    if normalized is WorkflowState.FAILED:
        return "The workflow failed safely. Inspect the receipt before retrying."
    return "No failure recorded."


__all__ = ["outcome_message", "state_label"]
