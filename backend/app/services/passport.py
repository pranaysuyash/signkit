"""Read-only projection from the workspace control plane to Execution Passport."""

from __future__ import annotations

from typing import Any, Sequence

from contracts.execution_passport import (
    DATA_BOUNDARY_METADATA_ONLY,
    ExecutionPassport,
    PassportEvidence,
)


def _timestamp(value: Any) -> str:
    if value is None:
        return ""
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def _recovery_action(status: str) -> str:
    return {
        "ready_for_review": "await_review",
        "needs_correction": "request_correction",
        "exception": "retry_workspace_execution",
        "pending_review": "prepare_review",
        "received": "request_review",
    }.get(status, "none")


def project_workspace_execution(
    execution: Any,
    events: Sequence[Any],
) -> ExecutionPassport:
    """Project workspace metadata without claiming local document execution."""
    ordered_events = sorted(events, key=lambda event: int(event.sequence))
    evidence = tuple(
        PassportEvidence(
            sequence=int(event.sequence),
            code=str(event.event_type),
            state_from=event.status_from,
            state_to=str(event.status_to),
            actor="workspace_owner",
            occurred_at=_timestamp(getattr(event, "created_at", None)),
            message=str(event.summary),
        )
        for event in ordered_events
    )
    last_idempotency_key = next(
        (event.idem_key for event in reversed(ordered_events) if event.idem_key),
        None,
    )
    topology = str(execution.topology)
    passport = ExecutionPassport(
        execution_id=str(execution.id),
        topology=topology,
        source_of_truth="workspace_control_plane",
        owner_role="workspace_owner",
        template_code=str(execution.template_code),
        template_version=int(execution.template_version),
        aggregate_status=str(execution.status),
        correlation_id=f"{topology}:{execution.id}",
        idempotency_key=last_idempotency_key,
        evidence=evidence,
        recovery_action=_recovery_action(str(execution.status)),
        data_boundary=DATA_BOUNDARY_METADATA_ONLY,
        created_at=_timestamp(getattr(execution, "created_at", None)),
        updated_at=_timestamp(getattr(execution, "updated_at", None)),
    )
    return passport.validate()
