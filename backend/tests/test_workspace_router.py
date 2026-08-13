from __future__ import annotations

from io import BytesIO
from pathlib import Path
from uuid import uuid4

from contextlib import contextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest

from backend.app.database import Base, get_db
from backend.app.models.user import User
from backend.app.routers.workspace import router as workspace_router
from backend.app.utils.dependencies import get_current_user


@contextmanager
def _build_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def _seed_owner(session, email="owner@example.com"):
    owner = User(
        id=uuid4(),
        email=email,
        hashed_password="x" * 80,
    )
    session.add(owner)
    session.commit()
    session.refresh(owner)
    return owner


def _build_client(session, owner):
    app = FastAPI()
    app.include_router(workspace_router, prefix="/workspace")

    def _override_db():
        yield session

    def _override_current_user():
        return owner

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_current_user
    return TestClient(app)


def _create_execution(client, topology="cloud"):
    response = client.post(
        "/workspace/executions",
        json={
            "template_code": "hr-onboarding-core",
            "participant_name": "Alex Example",
            "participant_email": "alex@example.com",
            "reviewer_name": "Priya Review",
            "reviewer_email": "priya@example.com",
            "notes": "synthetic contract packet",
            "topology": topology,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.fixture()
def workspace_client():
    with _build_session() as session:
        owner = _seed_owner(session)
        client = _build_client(session, owner)
        try:
            yield client
        finally:
            client.close()


def test_transition_route_replay_is_idempotent_for_same_idem_key(workspace_client):
    execution_id = _create_execution(workspace_client)
    transition_payload = {
        "action": "request_review",
        "idem_key": "idem-key-route-001",
    }

    first = workspace_client.post(
        f"/workspace/executions/{execution_id}/transitions",
        json=transition_payload,
    )
    assert first.status_code == 200
    assert first.json()["status"] == "ready_for_review"

    replay = workspace_client.post(
        f"/workspace/executions/{execution_id}/transitions",
        json=transition_payload,
    )
    assert replay.status_code == 200
    assert replay.json()["status"] == "ready_for_review"
    assert len(replay.json()["events"]) == 2


def test_workspace_route_hides_foreign_execution_from_non_owner():
    with _build_session() as session:
        owner = _seed_owner(session)
        foreign_owner = _seed_owner(session, "foreign@example.com")
        owner_client = _build_client(session, owner)
        foreign_client = _build_client(session, foreign_owner)
        try:
            execution_id = _create_execution(owner_client)

            get_response = foreign_client.get(f"/workspace/executions/{execution_id}")
            transition_response = foreign_client.post(
                f"/workspace/executions/{execution_id}/transitions",
                json={"action": "request_review", "idem_key": "foreign-owner-001"},
            )

            assert get_response.status_code == 404
            assert transition_response.status_code == 404
        finally:
            owner_client.close()
            foreign_client.close()


def test_transition_route_returns_conflict_after_state_advances_without_idem_key(workspace_client):
    execution_id = _create_execution(workspace_client)

    first = workspace_client.post(
        f"/workspace/executions/{execution_id}/transitions",
        json={"action": "request_review"},
    )
    assert first.status_code == 200

    conflict = workspace_client.post(
        f"/workspace/executions/{execution_id}/transitions",
        json={"action": "request_review"},
    )
    assert conflict.status_code == 409
    assert "Cannot apply 'request_review'" in conflict.json()["detail"]


def _post_transition(
    client,
    execution_id,
    action,
    idem_key=None,
):
    payload = {"action": action}
    if idem_key is not None:
        payload["idem_key"] = idem_key
    return client.post(f"/workspace/executions/{execution_id}/transitions", json=payload)


@pytest.mark.parametrize(
    ("setup_actions", "target_action", "target_idem_key", "expected_status", "expected_event_count"),
    [
        (
            ["mark_received"],
            "request_review",
            "idem-key-route-received",
            "ready_for_review",
            3,
        ),
        (
            ["request_review", "approve"],
            "sign",
            "idem-key-route-signed",
            "signed",
            4,
        ),
        (
            ["request_review", "approve", "sign"],
            "export",
            "idem-key-route-exported",
            "exported",
            5,
        ),
    ],
)
def test_transition_route_replay_is_idempotent_for_keyed_state_edges(
    workspace_client,
    setup_actions,
    target_action,
    target_idem_key,
    expected_status,
    expected_event_count,
):
    execution_id = _create_execution(workspace_client)

    for action in setup_actions:
        setup_response = _post_transition(workspace_client, execution_id, action)
        assert setup_response.status_code == 200

    first = _post_transition(
        workspace_client,
        execution_id,
        target_action,
        idem_key=target_idem_key,
    )
    assert first.status_code == 200
    assert first.json()["status"] == expected_status

    replay = _post_transition(
        workspace_client,
        execution_id,
        target_action,
        idem_key=target_idem_key,
    )
    assert replay.status_code == 200
    assert replay.json()["status"] == expected_status
    assert len(replay.json()["events"]) == expected_event_count


def test_contractdesk_proof_slice_smoke_path(workspace_client):
    execution_id = _create_execution(workspace_client)

    transition_sequence = [
        ("mark_received", "idem-proof-001", "received"),
        ("request_review", "idem-proof-002", "ready_for_review"),
        ("request_correction", "idem-proof-003", "needs_correction"),
        ("request_review", "idem-proof-004", "ready_for_review"),
        ("approve", "idem-proof-005", "approved"),
        ("sign", "idem-proof-006", "signed"),
        ("export", "idem-proof-007", "exported"),
    ]

    for action, idem_key, expected_status in transition_sequence:
        response = _post_transition(workspace_client, execution_id, action, idem_key=idem_key)
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == expected_status
        assert payload["events"][-1]["status_to"] == expected_status
        assert payload["events"][-1]["summary"]

    final = _post_transition(workspace_client, execution_id, "export", idem_key="idem-proof-007")
    assert final.status_code == 200
    assert final.json()["status"] == "exported"
    assert final.json()["events"][-1]["status_to"] == "exported"
    assert len(final.json()["events"]) >= 8


def _pdf_payload(label="Signature"):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(72, 720, label)
    pdf.line(72, 680, 260, 680)
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def test_local_document_inspection_is_isolated_replay_safe_and_cloud_rejected(workspace_client):
    local_execution_id = _create_execution(workspace_client, topology="local")
    headers = {"Idempotency-Key": "document-inspection-local-001"}
    payload = _pdf_payload()

    first = workspace_client.post(
        f"/workspace/executions/{local_execution_id}/document-inspections",
        files={"file": ("contract.pdf", payload, "application/pdf")},
        data={"page_index": "0"},
        headers=headers,
    )
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["runtime_mode"] == "isolated"
    assert first_payload["retained"] is False
    assert first_payload["input_sha256"]
    assert first_payload["receipt_id"]
    assert isinstance(first_payload["receipt_id"], str)
    assert first_payload["pages_processed"] == 1
    assert first_payload["candidates"]

    replay = workspace_client.post(
        f"/workspace/executions/{local_execution_id}/document-inspections",
        files={"file": ("contract.pdf", payload, "application/pdf")},
        data={"page_index": "0"},
        headers=headers,
    )
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    assert replay.json()["receipt_id"] == first_payload["receipt_id"]
    assert replay.json()["input_sha256"] == first_payload["input_sha256"]

    conflict = workspace_client.post(
        f"/workspace/executions/{local_execution_id}/document-inspections",
        files={"file": ("contract.pdf", _pdf_payload("Different"), "application/pdf")},
        data={"page_index": "0"},
        headers=headers,
    )
    assert conflict.status_code == 409

    cloud_execution_id = _create_execution(workspace_client, topology="cloud")
    cloud = workspace_client.post(
        f"/workspace/executions/{cloud_execution_id}/document-inspections",
        files={"file": ("contract.pdf", payload, "application/pdf")},
        data={"page_index": "0"},
        headers={"Idempotency-Key": "document-inspection-cloud-001"},
    )
    assert cloud.status_code == 409
    assert "local topology" in cloud.json()["detail"]


def test_local_document_inspection_rejects_malformed_or_unkeyed_input(workspace_client):
    execution_id = _create_execution(workspace_client, topology="local")

    malformed = workspace_client.post(
        f"/workspace/executions/{execution_id}/document-inspections",
        files={"file": ("contract.pdf", b"not-a-pdf", "application/pdf")},
        data={"page_index": "0"},
        headers={"Idempotency-Key": "document-invalid-001"},
    )
    assert malformed.status_code == 422
    assert "Invalid PDF" in malformed.json()["detail"]

    unkeyed = workspace_client.post(
        f"/workspace/executions/{execution_id}/document-inspections",
        files={"file": ("contract.pdf", _pdf_payload(), "application/pdf")},
        data={"page_index": "0"},
    )
    assert unkeyed.status_code == 422
    assert "Idempotency-Key" in unkeyed.json()["detail"]


def test_local_document_inspection_removes_temporary_source_after_worker(monkeypatch, workspace_client):
    execution_id = _create_execution(workspace_client, topology="local")
    worker_paths = []

    def fake_detect_page(self, pdf_path, page_index):
        worker_paths.append(Path(pdf_path))
        return [{"page_index": page_index, "confidence": 0.9}]

    monkeypatch.setattr(
        "backend.app.services.document_inspection.IsolatedDocumentRuntime.detect_page",
        fake_detect_page,
    )
    response = workspace_client.post(
        f"/workspace/executions/{execution_id}/document-inspections",
        files={"file": ("contract.pdf", _pdf_payload(), "application/pdf")},
        data={"page_index": "0"},
        headers={"Idempotency-Key": "document-cleanup-001"},
    )

    assert response.status_code == 200
    assert worker_paths
    assert not worker_paths[0].exists()
