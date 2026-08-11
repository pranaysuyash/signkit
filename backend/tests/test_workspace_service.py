import pytest

from backend.app.schemas.workspace import WorkspaceExecutionStatus, WorkspaceTransitionAction
from backend.app.services.workspace import (
    WorkspaceCatalogError,
    WorkspaceTransitionError,
    get_template,
    list_templates,
    resolve_transition,
)


def test_catalog_exposes_versioned_hr_template_without_document_payloads():
    templates = list_templates()

    assert len(templates) == 1
    template = templates[0]
    assert template.code == "hr-onboarding-core"
    assert template.version == 1
    assert len(template.steps) == 3
    assert "does not upload" in template.privacy_note


def test_transition_path_is_explicit_and_terminal_states_fail_closed():
    awaiting_participant = resolve_transition(
        WorkspaceExecutionStatus.PENDING_REVIEW,
        WorkspaceTransitionAction.RECORD_REVIEW,
    )
    assert awaiting_participant is WorkspaceExecutionStatus.AWAITING_PARTICIPANT
    assert resolve_transition(
        awaiting_participant,
        WorkspaceTransitionAction.RECORD_PARTICIPANT_CONFIRMATION,
    ) is WorkspaceExecutionStatus.COMPLETED

    with pytest.raises(WorkspaceTransitionError):
        resolve_transition(
            WorkspaceExecutionStatus.COMPLETED,
            WorkspaceTransitionAction.RECORD_PARTICIPANT_CONFIRMATION,
        )


def test_unknown_catalog_entry_is_rejected():
    with pytest.raises(WorkspaceCatalogError):
        get_template("not-a-template")
