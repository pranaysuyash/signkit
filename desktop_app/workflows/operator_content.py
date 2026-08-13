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
    "ERR_INPUT_INVALID": "The input is not a readable PDF. Choose a valid PDF or review the source.",
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

_COMPANION_LABELS = {
    "checking": "Local service: Checking...",
    "starting": "Local service: Starting...",
    "online": "Local service: Online",
    "offline": "Local service: Offline",
}

_COMPANION_MESSAGES = {
    "checking": "Checking the local companion. Core document work remains available while status is checked.",
    "starting": "The local companion is starting. Core document work remains available while it starts.",
    "online": "The local companion is running. Document processing remains local by default.",
    "offline": (
        "The local companion is unavailable. Core signature extraction and PDF work remain available locally. "
        "Retry the local service or continue local work."
    ),
}

_EXPORT_COPY = {
    "ERR_EXPORT_FAILED": (
        "The PDF could not be exported. No incomplete output was kept. "
        "Check the source and destination, then try again if safe."
    ),
    "ERR_EXPORT_VERIFY": (
        "The exported PDF did not pass local output verification. No incomplete output was kept. "
        "Review the source and destination before trying again."
    ),
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


def companion_status_label(state: str) -> str:
    """Return stable operator copy for the local companion lifecycle."""

    normalized = str(state).strip().lower()
    return _COMPANION_LABELS.get(normalized, _COMPANION_LABELS["checking"])


def companion_status_message(state: str) -> str:
    """Return bounded recovery copy without raw endpoint or exception details."""

    normalized = str(state).strip().lower()
    return _COMPANION_MESSAGES.get(normalized, _COMPANION_MESSAGES["checking"])


def companion_tooltip(state: str, *, version: str | None = None) -> str:
    """Return secondary companion detail that keeps the primary boundary clear."""

    message = companion_status_message(state)
    if str(state).strip().lower() == "online" and version:
        return f"{message}\nVersion: {version}\nOpen local health details for diagnostics."
    return f"{message}\nOpen Help for local companion recovery."


def export_outcome_message(code: str | None) -> str:
    """Return bounded recovery copy for a local PDF export result."""

    return _EXPORT_COPY.get(code or "", _EXPORT_COPY["ERR_EXPORT_FAILED"])


__all__ = [
    "companion_status_label",
    "companion_status_message",
    "companion_tooltip",
    "export_outcome_message",
    "outcome_message",
    "state_label",
]
