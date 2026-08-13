from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from threading import Event, Lock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.models.user import User
from backend.app.routers import workspace as workspace_module
from backend.app.routers.workspace import router as workspace_router
from backend.app.utils.dependencies import get_current_user
from desktop_app.workflows import authorization, models, store
from desktop_app.workflows import engine as workflow_engine_module


@contextmanager
def _session():
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
        engine.dispose()


def _owner(session, email: str) -> User:
    user = User(id=uuid4(), email=email, hashed_password="x" * 80)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _client(session, user: User) -> TestClient:
    app = FastAPI()
    app.include_router(workspace_router, prefix="/workspace")

    def override_db():
        yield session

    def override_user():
        return user

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user
    return TestClient(app)


def _seed_job(tmp_path: Path, subject: str, *, state: models.WorkflowState = models.WorkflowState.RETRY):
    recipe = models.ControlledSigningRecipe.new(
        recipe_id=f"bridge-recipe-{uuid4().hex}",
        name="Bridge proof recipe",
        status=models.RecipeStatus.ACTIVE.value,
        input_folder=models.FolderConfig(
            folder_id=f"input-{uuid4().hex}",
            path=str(tmp_path),
        ),
        output_folder=models.FolderConfig(
            folder_id=f"output-{uuid4().hex}",
            path=str(tmp_path),
        ),
    )
    store.save_recipe(recipe)
    grant = authorization.create_grant(recipe.recipe_id, {}, subject)
    private_path = tmp_path / "private-source-document.pdf"
    job = models.WorkflowJob.new(
        job_id=f"bridge-job-{uuid4().hex}",
        input_path_ref=str(private_path),
        input_fingerprint="sha256:bridge-input",
        recipe_id=recipe.recipe_id,
        recipe_version=recipe.version,
        state=state,
        grant_id=grant.grant_id,
    )
    job = replace(job, attempts=1)
    store.save_job(job)
    store.append_job_event(
        event_id=None,
        job_id=job.job_id,
        state_from=models.WorkflowState.VERIFYING,
        state_to=state,
        actor="desktop-engine",
        code="ERR_SIGNING_FAILED",
        message=f"private-path:{private_path}",
    )
    return job, private_path


def test_local_bridge_lists_exact_id_or_email_bound_metadata_and_hides_document_path(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "APP_DIR", tmp_path / "workflow")
    monkeypatch.setattr(store, "WORKFLOW_STORE_FILE", tmp_path / "workflow" / "workflow_store.json")
    store.clear_store()

    with _session() as session:
        user = _owner(session, "bridge-owner@example.com")
        foreign = _owner(session, "bridge-foreign@example.com")
        owned_job, private_path = _seed_job(tmp_path, str(user.id))
        email_job, email_private_path = _seed_job(tmp_path, user.email)
        _seed_job(tmp_path, str(foreign.id))
        client = _client(session, user)
        try:
            response = client.get("/workspace/local-jobs")
            assert response.status_code == 200
            payload = response.json()
            assert {item["job_id"] for item in payload} == {owned_job.job_id, email_job.job_id}
            serialized = response.text
            assert str(private_path) not in serialized
            assert str(email_private_path) not in serialized
            assert "private-path:" not in serialized
            assert "input_path_ref" not in serialized
            assert all(item["passport"]["data_boundary"] == "metadata_only_no_document_bytes" for item in payload)
            assert all(item["passport"]["source_of_truth"] == "local_workflow_store" for item in payload)
        finally:
            client.close()


def test_local_bridge_hides_foreign_job_and_hosted_profile(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "APP_DIR", tmp_path / "workflow")
    monkeypatch.setattr(store, "WORKFLOW_STORE_FILE", tmp_path / "workflow" / "workflow_store.json")
    store.clear_store()

    with _session() as session:
        owner = _owner(session, "bridge-owner@example.com")
        foreign = _owner(session, "bridge-foreign@example.com")
        foreign_job, _ = _seed_job(tmp_path, str(foreign.id))
        client = _client(session, owner)
        try:
            hidden = client.get(f"/workspace/local-jobs/{foreign_job.job_id}")
            assert hidden.status_code == 404

            monkeypatch.setattr(workspace_module, "is_local_companion", lambda: False)
            hosted = client.get("/workspace/local-jobs")
            assert hosted.status_code == 404
        finally:
            client.close()


def test_local_bridge_retry_delegates_to_canonical_engine_and_rejects_completed_job(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "APP_DIR", tmp_path / "workflow")
    monkeypatch.setattr(store, "WORKFLOW_STORE_FILE", tmp_path / "workflow" / "workflow_store.json")
    store.clear_store()

    with _session() as session:
        user = _owner(session, "bridge-owner@example.com")
        job, _ = _seed_job(tmp_path, str(user.id))
        client = _client(session, user)
        calls: list[tuple[str, str]] = []

        class FakeEngine:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def start(self):
                return None

            def stop(self):
                return None

            def retry_job(
                self,
                job_id: str,
                *,
                actor: str,
                action_subject: str,
                idempotency_key: str | None = None,
            ):
                calls.append((actor, action_subject))
                current = store.get_job(job_id)
                assert current is not None
                updated = replace(current, state=models.WorkflowState.COMPLETED)
                store.save_job(updated)
                return updated

        monkeypatch.setattr(workflow_engine_module, "WorkflowEngine", FakeEngine)
        try:
            response = client.post(f"/workspace/local-jobs/{job.job_id}/retry")
            assert response.status_code == 200
            assert response.json()["status"] == "completed"
            assert calls == [(f"workspace-local:{user.id}", str(user.id))]

            replayed = client.post(f"/workspace/local-jobs/{job.job_id}/retry")
            assert replayed.status_code == 200
            assert replayed.json()["status"] == "completed"
            assert calls == [(f"workspace-local:{user.id}", str(user.id))]
        finally:
            client.close()


def test_local_bridge_retry_replays_same_key_without_second_engine_call(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "APP_DIR", tmp_path / "workflow")
    monkeypatch.setattr(store, "WORKFLOW_STORE_FILE", tmp_path / "workflow" / "workflow_store.json")
    store.clear_store()

    with _session() as session:
        user = _owner(session, "bridge-idempotency@example.com")
        job, _ = _seed_job(tmp_path, str(user.id))
        client = _client(session, user)
        calls: list[tuple[str, str, str | None]] = []

        class FakeEngine:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def start(self):
                return None

            def stop(self):
                return None

            def retry_job(
                self,
                job_id: str,
                *,
                actor: str,
                action_subject: str,
                idempotency_key: str | None = None,
            ):
                calls.append((actor, action_subject, idempotency_key))
                current = store.get_job(job_id)
                assert current is not None
                updated = replace(
                    current,
                    state=models.WorkflowState.COMPLETED,
                    attempts=current.attempts + 1,
                    last_idempotency_key=idempotency_key,
                )
                return store.save_job(updated)

        monkeypatch.setattr(workflow_engine_module, "WorkflowEngine", FakeEngine)
        try:
            invalid = client.post(
                f"/workspace/local-jobs/{job.job_id}/retry",
                headers={"Idempotency-Key": "x"},
            )
            assert invalid.status_code == 400

            headers = {"Idempotency-Key": "bridge-retry-key-001"}
            first = client.post(f"/workspace/local-jobs/{job.job_id}/retry", headers=headers)
            assert first.status_code == 200
            assert first.json()["status"] == "completed"
            assert first.json()["passport"]["idempotency_key"] == "bridge-retry-key-001"

            replay = client.post(f"/workspace/local-jobs/{job.job_id}/retry", headers=headers)
            assert replay.status_code == 200
            assert replay.json() == first.json()
            assert calls == [
                (f"workspace-local:{user.id}", str(user.id), "bridge-retry-key-001")
            ]

            stored = store.get_retry_receipt(job.job_id, "bridge-retry-key-001")
            assert stored is not None
            assert stored["job"]["state"] == models.WorkflowState.COMPLETED.value
            assert stored["job"]["last_idempotency_key"] == "bridge-retry-key-001"
        finally:
            client.close()


def test_local_bridge_concurrent_keyed_retry_converges_on_one_execution(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "APP_DIR", tmp_path / "workflow")
    monkeypatch.setattr(store, "WORKFLOW_STORE_FILE", tmp_path / "workflow" / "workflow_store.json")
    store.clear_store()

    with _session() as session:
        user = _owner(session, "bridge-concurrent@example.com")
        job, _ = _seed_job(tmp_path, str(user.id))
        client = _client(session, user)
        calls: list[str] = []
        calls_lock = Lock()
        first_call_started = Event()
        release_first_call = Event()

        class FakeEngine:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def start(self):
                return None

            def stop(self):
                return None

            def retry_job(
                self,
                job_id: str,
                *,
                actor: str,
                action_subject: str,
                idempotency_key: str | None = None,
            ):
                with calls_lock:
                    calls.append(idempotency_key or "")
                    first = len(calls) == 1
                if first:
                    first_call_started.set()
                    assert release_first_call.wait(5)
                current = store.get_job(job_id)
                assert current is not None
                updated = replace(
                    current,
                    state=models.WorkflowState.COMPLETED,
                    attempts=current.attempts + 1,
                    last_idempotency_key=idempotency_key,
                )
                return store.save_job(updated)

        monkeypatch.setattr(workflow_engine_module, "WorkflowEngine", FakeEngine)
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                headers = {"Idempotency-Key": "concurrent-retry-key-001"}
                first_future = executor.submit(
                    client.post,
                    f"/workspace/local-jobs/{job.job_id}/retry",
                    headers=headers,
                )
                assert first_call_started.wait(5)
                second_future = executor.submit(
                    client.post,
                    f"/workspace/local-jobs/{job.job_id}/retry",
                    headers=headers,
                )
                release_first_call.set()
                first = first_future.result(timeout=5)
                second = second_future.result(timeout=5)

            assert first.status_code == 200
            assert second.status_code == 200
            assert second.json() == first.json()
            assert calls == ["concurrent-retry-key-001"]
        finally:
            client.close()
