from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from contracts.execution_passport import ExecutionPassport
from backend.app.services.passport import project_workspace_execution
from desktop_app.workflows.models import WorkflowJob, WorkflowJobEvent, WorkflowState
from desktop_app.workflows.passport import project_local_job


def _local_job(state: WorkflowState = WorkflowState.COMPLETED) -> WorkflowJob:
    return WorkflowJob(
        job_id="local-job-001",
        input_path_ref="/private/documents/onboarding.pdf",
        input_fingerprint="sha256:input-001",
        recipe_id="recipe-001",
        recipe_version=3,
        output_path_ref="/private/output/onboarding-signed.pdf" if state is WorkflowState.COMPLETED else "",
        state=state,
        grant_id="grant-001",
        attempts=1,
        max_attempts=3,
        created_at="2026-08-12T10:00:00+00:00",
        updated_at="2026-08-12T10:01:00+00:00",
    )


def test_local_projection_is_metadata_only_and_uses_local_source_of_truth():
    passport = project_local_job(
        _local_job(),
        [
            WorkflowJobEvent(
                event_id="event-001",
                job_id="local-job-001",
                state_from="verifying",
                state_to="completed",
                actor="local-operator",
                code="EVT_SIGNING_DONE",
                message="output=/private/output/onboarding-signed.pdf",
                occurred_at="2026-08-12T10:01:00+00:00",
            )
        ],
    )

    payload = passport.to_payload()

    assert payload["passport_version"] == "1.0"
    assert payload["execution_id"] == "local-job-001"
    assert payload["topology"] == "local"
    assert payload["source_of_truth"] == "local_workflow_store"
    assert payload["child_job_id"] == "local-job-001"
    assert payload["child_job_status"] == "completed"
    assert payload["input_fingerprint"] == "sha256:input-001"
    assert payload["output_reference"] == "local-output:local-job-001"
    assert payload["evidence"][0]["message"] is None
    assert "/private/" not in str(payload)
    assert "input_path_ref" not in payload
    assert "document_bytes" not in payload


def test_local_projection_exposes_recovery_without_exposing_error_text():
    passport = project_local_job(
        _local_job(WorkflowState.RETRY),
        [
            WorkflowJobEvent(
                event_id="event-002",
                job_id="local-job-001",
                state_from="processing",
                state_to="retry",
                actor="system",
                code="ERR_OUTPUT_IO",
                message="output_path=/private/output/onboarding-signed.pdf",
                occurred_at="2026-08-12T10:01:00+00:00",
            )
        ],
    )

    assert passport.aggregate_status == "retry"
    assert passport.recovery_action == "retry_local_job"
    assert passport.evidence[0].code == "ERR_OUTPUT_IO"
    assert passport.evidence[0].message is None


def test_workspace_projection_keeps_control_plane_authority_and_idempotency_receipt():
    execution_id = uuid4()
    execution = SimpleNamespace(
        id=execution_id,
        owner_user_id=uuid4(),
        template_code="hr-onboarding-core",
        template_version=1,
        topology="cloud",
        status="ready_for_review",
        title="HR Onboarding Core: Alex Example",
        participant_name="Alex Example",
        participant_email="alex@example.com",
        reviewer_name="Priya Review",
        reviewer_email="priya@example.com",
    )
    events = [
        SimpleNamespace(
            id=uuid4(),
            execution_id=execution_id,
            sequence=1,
            actor_user_id=execution.owner_user_id,
            event_type="execution_created",
            status_from=None,
            status_to="pending_review",
            idem_key=None,
            summary="Workflow metadata created.",
        ),
        SimpleNamespace(
            id=uuid4(),
            execution_id=execution_id,
            sequence=2,
            actor_user_id=execution.owner_user_id,
            event_type="request_review",
            status_from="pending_review",
            status_to="ready_for_review",
            idem_key="idem-review-001",
            summary="Review requested.",
        ),
    ]

    passport = project_workspace_execution(execution, events)

    assert passport.execution_id == str(execution_id)
    assert passport.topology == "cloud"
    assert passport.source_of_truth == "workspace_control_plane"
    assert passport.idempotency_key == "idem-review-001"
    assert passport.aggregate_status == "ready_for_review"
    assert passport.recovery_action == "await_review"
    assert passport.data_boundary == "metadata_only_no_document_bytes"
    assert passport.evidence[-1].code == "request_review"
    assert "document" not in str(passport.to_payload()["evidence"][-1]).lower()


def test_passport_rejects_unknown_topology_and_document_payload_fields():
    with pytest.raises(ValueError, match="topology"):
        project_local_job(_local_job(), [], topology="cloud")


def test_passport_rejects_document_byte_boundary():
    passport = ExecutionPassport(
        execution_id="execution-001",
        topology="cloud",
        source_of_truth="workspace_control_plane",
        owner_role="workspace_owner",
        template_code="hr-onboarding-core",
        template_version=1,
        aggregate_status="pending_review",
        data_boundary="document_bytes_included",
    )

    with pytest.raises(ValueError, match="cannot carry document bytes"):
        passport.validate()
