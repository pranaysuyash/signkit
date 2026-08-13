import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.models.user import User
from backend.app.models.workspace import WorkspaceExecutionEvent
from backend.app.schemas.workspace import (
    WorkspaceExecutionCreate,
    WorkspaceExecutionStatus,
    WorkspaceTransitionAction,
)
from backend.app.services.workspace import (
    WorkspaceCatalogError,
    WorkspaceTransitionError,
    create_execution,
    get_template,
    list_templates,
    resolve_transition,
    transition_execution,
)


def _session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)
    return TestSession()


def _seed_owner(db, email: str = "owner@example.com"):
    owner = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password="x" * 80,
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return owner


def _seed_execution(db, owner: User | None = None):
    owner = owner or _seed_owner(db)
    return create_execution(
        db,
        owner,
        WorkspaceExecutionCreate(
            template_code="hr-onboarding-core",
            participant_name="Alex Example",
            participant_email="alex@example.com",
            reviewer_name="Priya Review",
            reviewer_email="priya@example.com",
            notes="sample metadata packet",
        ),
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
    assert (
        resolve_transition(
            awaiting_participant,
            WorkspaceTransitionAction.RECORD_PARTICIPANT_CONFIRMATION,
        )
        is WorkspaceExecutionStatus.COMPLETED
    )

    with pytest.raises(WorkspaceTransitionError):
        resolve_transition(
            WorkspaceExecutionStatus.COMPLETED,
            WorkspaceTransitionAction.RECORD_PARTICIPANT_CONFIRMATION,
        )


def test_contractdesk_states_and_exceptions_are_modeled_explicitly():
    ready_for_review = resolve_transition(
        WorkspaceExecutionStatus.PENDING_REVIEW,
        WorkspaceTransitionAction.REQUEST_REVIEW,
    )
    assert ready_for_review is WorkspaceExecutionStatus.READY_FOR_REVIEW

    needs_correction = resolve_transition(
        WorkspaceExecutionStatus.READY_FOR_REVIEW,
        WorkspaceTransitionAction.REQUEST_CORRECTION,
    )
    assert needs_correction is WorkspaceExecutionStatus.NEEDS_CORRECTION

    ready_again = resolve_transition(
        WorkspaceExecutionStatus.NEEDS_CORRECTION,
        WorkspaceTransitionAction.REQUEST_REVIEW,
    )
    assert ready_again is WorkspaceExecutionStatus.READY_FOR_REVIEW

    approved = resolve_transition(
        WorkspaceExecutionStatus.READY_FOR_REVIEW,
        WorkspaceTransitionAction.APPROVE,
    )
    assert approved is WorkspaceExecutionStatus.APPROVED

    signed = resolve_transition(
        WorkspaceExecutionStatus.APPROVED,
        WorkspaceTransitionAction.SIGN,
    )
    assert signed is WorkspaceExecutionStatus.SIGNED

    exported = resolve_transition(
        WorkspaceExecutionStatus.SIGNED,
        WorkspaceTransitionAction.EXPORT,
    )
    assert exported is WorkspaceExecutionStatus.EXPORTED

    exception = resolve_transition(
        WorkspaceExecutionStatus.READY_FOR_REVIEW,
        WorkspaceTransitionAction.RECORD_EXCEPTION,
    )
    assert exception is WorkspaceExecutionStatus.EXCEPTION

    recovered = resolve_transition(
        WorkspaceExecutionStatus.EXCEPTION,
        WorkspaceTransitionAction.RETRY_REVIEW,
    )
    assert recovered is WorkspaceExecutionStatus.READY_FOR_REVIEW


def test_contractdesk_received_entry_point_is_available_from_new_packets():
    received = resolve_transition(
        WorkspaceExecutionStatus.PENDING_REVIEW,
        WorkspaceTransitionAction.MARK_RECEIVED,
    )
    assert received is WorkspaceExecutionStatus.RECEIVED


def test_unknown_catalog_entry_is_rejected():
    with pytest.raises(WorkspaceCatalogError):
        get_template("not-a-template")


def test_transition_with_idem_key_is_replay_safe_when_repeated():
    db = _session()
    execution = _seed_execution(db)
    owner = db.query(User).filter_by(email="owner@example.com").first()

    first = transition_execution(
        db,
        execution,
        owner,
        WorkspaceTransitionAction.REQUEST_REVIEW,
        idem_key="idem-review-replay-001",
    )
    assert first.status == WorkspaceExecutionStatus.READY_FOR_REVIEW

    replay = transition_execution(
        db,
        execution,
        owner,
        WorkspaceTransitionAction.REQUEST_REVIEW,
        idem_key="idem-review-replay-001",
    )
    assert replay.status == WorkspaceExecutionStatus.READY_FOR_REVIEW
    assert db.query(WorkspaceExecutionEvent).count() == 2


def test_transition_idem_key_lookup_is_scoped_to_actor_not_global():
    db = _session()
    owner = _seed_owner(db)
    other_owner = _seed_owner(db, "other-owner@example.com")
    owner_execution = _seed_execution(db, owner)
    other_execution = _seed_execution(db, other_owner)
    shared_key = "idem-key-cross-actor-001"

    transition_execution(
        db,
        owner_execution,
        owner,
        WorkspaceTransitionAction.REQUEST_REVIEW,
        idem_key=shared_key,
    )
    transition_execution(
        db,
        owner_execution,
        owner,
        WorkspaceTransitionAction.REQUEST_REVIEW,
        idem_key=shared_key,
    )

    other_transition = transition_execution(
        db,
        other_execution,
        other_owner,
        WorkspaceTransitionAction.REQUEST_REVIEW,
        idem_key=shared_key,
    )

    assert other_transition.status == WorkspaceExecutionStatus.READY_FOR_REVIEW
    assert db.query(WorkspaceExecutionEvent).filter(
        WorkspaceExecutionEvent.execution_id == owner_execution.id
    ).count() == 2
    assert db.query(WorkspaceExecutionEvent).filter(
        WorkspaceExecutionEvent.execution_id == other_execution.id
    ).count() == 2
    assert db.query(WorkspaceExecutionEvent).filter(
        WorkspaceExecutionEvent.idem_key == shared_key,
        WorkspaceExecutionEvent.actor_user_id == owner.id,
    ).count() == 1
    assert db.query(WorkspaceExecutionEvent).filter(
        WorkspaceExecutionEvent.idem_key == shared_key,
        WorkspaceExecutionEvent.actor_user_id == other_owner.id,
    ).count() == 1


def test_transition_without_idem_key_still_advances_and_expects_state_change():
    db = _session()
    execution = _seed_execution(db)
    owner = db.query(User).filter_by(email="owner@example.com").first()

    first = transition_execution(
        db,
        execution,
        owner,
        WorkspaceTransitionAction.REQUEST_REVIEW,
        idem_key=None,
    )
    assert first.status == WorkspaceExecutionStatus.READY_FOR_REVIEW

    with pytest.raises(WorkspaceTransitionError):
        transition_execution(
            db,
            execution,
            owner,
            WorkspaceTransitionAction.REQUEST_REVIEW,
            idem_key=None,
        )
