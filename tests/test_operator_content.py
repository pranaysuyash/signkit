"""Tests for safe, stable operator-facing workflow copy."""

from desktop_app.workflows.models import WorkflowState
from desktop_app.workflows.operator_content import outcome_message, state_label


def test_state_labels_are_human_facing_and_stable() -> None:
    assert state_label(WorkflowState.NEEDS_REVIEW) == "Needs review"
    assert state_label(WorkflowState.RETRY) == "Retry available"
    assert state_label("completed") == "Completed"
    assert state_label("future_state") == "Future State"


def test_failure_copy_does_not_leak_raw_paths_or_exception_text() -> None:
    raw = "ERR_OUTPUT_IO: /Users/pranay/private/document.pdf: disk full"
    message = outcome_message("ERR_OUTPUT_IO", WorkflowState.FAILED)

    assert message == "The output could not be written. Check the local destination and retry if safe."
    assert "/Users/pranay" not in message
    assert "disk full" not in message
    assert raw not in message


def test_terminal_and_recovery_copy_follows_state_contract() -> None:
    assert outcome_message(None, WorkflowState.COMPLETED) == "Completed successfully."
    assert outcome_message("ERR_SIGNING_FAILED", WorkflowState.RETRY) == (
        "The visual output could not be created. Retry is available when safe."
    )
    assert outcome_message(None, WorkflowState.NEEDS_REVIEW) == "Needs review before the workflow can continue."
