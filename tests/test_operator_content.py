"""Tests for safe, stable operator-facing workflow copy."""

from desktop_app.workflows.models import WorkflowState
from desktop_app.workflows.operator_content import (
    companion_status_label,
    companion_status_message,
    companion_tooltip,
    deletion_outcome_message,
    export_outcome_message,
    timeout_outcome_message,
    outcome_message,
    state_label,
)


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


def test_malformed_input_copy_requires_review_without_retry_claim() -> None:
    message = outcome_message("ERR_INPUT_INVALID", WorkflowState.NEEDS_REVIEW)

    assert message == "The input is not a readable PDF. Choose a valid PDF or review the source."
    assert "retry" not in message.lower()


def test_terminal_and_recovery_copy_follows_state_contract() -> None:
    assert outcome_message(None, WorkflowState.COMPLETED) == "Completed successfully."
    assert outcome_message("ERR_SIGNING_FAILED", WorkflowState.RETRY) == (
        "The visual output could not be created. Retry is available when safe."
    )
    assert outcome_message(None, WorkflowState.NEEDS_REVIEW) == "Needs review before the workflow can continue."


def test_interrupted_workflow_copy_requires_output_review_before_retry() -> None:
    message = outcome_message("ERR_WORKFLOW_INTERRUPTED", WorkflowState.NEEDS_REVIEW)

    assert "stopped before completion" in message
    assert "planned output" in message
    assert "retrying" in message
    assert "/Users/pranay" not in message


def test_local_companion_copy_is_bounded_and_recoverable() -> None:
    assert companion_status_label("offline") == "Local service: Offline"
    message = companion_status_message("offline")
    tooltip = companion_tooltip("offline")

    assert "local companion" in message.lower()
    assert "core signature extraction" in message.lower()
    assert "retry" in message.lower()
    assert "127.0.0.1" not in tooltip
    assert "Backend unavailable" not in tooltip
    assert "raw exception" not in tooltip.lower()


def test_unknown_companion_state_fails_to_checking_copy() -> None:
    assert companion_status_label("future_state") == "Local service: Checking..."
    assert "status is checked" in companion_status_message("future_state")


def test_partial_export_copy_protects_against_incomplete_output_claim() -> None:
    message = export_outcome_message("ERR_EXPORT_VERIFY")

    assert "did not pass local output verification" in message
    assert "No incomplete output was kept" in message
    assert "/Users/pranay" not in message


def test_deletion_copy_distinguishes_complete_and_incomplete_cleanup() -> None:
    assert deletion_outcome_message("deleted") == "Signature removed and cleanup completed."
    assert "cleanup is incomplete" in deletion_outcome_message("cleanup_incomplete")
    assert "No deletion was recorded" in deletion_outcome_message("not_deleted")


def test_timeout_copy_preserves_local_recovery_boundary() -> None:
    message = timeout_outcome_message()

    assert "did not respond in time" in message
    assert "continue local work" in message
    assert "127.0.0.1" not in message
