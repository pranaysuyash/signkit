"""Read-only projection from the local workflow store to Execution Passport."""

from __future__ import annotations

from typing import Sequence

from contracts.execution_passport import (
    DATA_BOUNDARY_METADATA_ONLY,
    ExecutionPassport,
    PassportEvidence,
)
from desktop_app.workflows.models import WorkflowJob, WorkflowJobEvent, WorkflowState


def _recovery_action(state: WorkflowState) -> str:
    return {
        WorkflowState.RETRY: "retry_local_job",
        WorkflowState.FAILED: "inspect_local_job",
        WorkflowState.CANCELLED: "recreate_local_job",
        WorkflowState.NEEDS_REVIEW: "review_local_job",
    }.get(state, "none")


def project_local_job(
    job: WorkflowJob,
    events: Sequence[WorkflowJobEvent],
    *,
    topology: str = "local",
) -> ExecutionPassport:
    """Project one local job without exposing paths, files, or error text."""
    if topology != "local":
        raise ValueError("Local workflow jobs can only project to the local topology")

    evidence = tuple(
        PassportEvidence(
            sequence=index,
            code=event.code,
            state_from=event.state_from,
            state_to=event.state_to,
            actor=event.actor,
            occurred_at=event.occurred_at,
            message=None,
        )
        for index, event in enumerate(events, start=1)
    )
    output_reference = f"local-output:{job.job_id}" if job.output_path_ref else None
    passport = ExecutionPassport(
        execution_id=job.job_id,
        topology="local",
        source_of_truth="local_workflow_store",
        owner_role="local_operator",
        template_code=job.recipe_id,
        template_version=job.recipe_version,
        aggregate_status=job.state.value,
        child_job_id=job.job_id,
        child_job_status=job.state.value,
        correlation_id=f"local:{job.job_id}",
        input_fingerprint=job.input_fingerprint or None,
        output_reference=output_reference,
        attempt=job.attempts,
        max_attempts=job.max_attempts,
        evidence=evidence,
        recovery_action=_recovery_action(job.state),
        data_boundary=DATA_BOUNDARY_METADATA_ONLY,
        created_at=job.created_at or None,
        updated_at=job.updated_at or None,
    )
    return passport.validate()
