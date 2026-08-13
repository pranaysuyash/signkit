from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models.user import User
from backend.app.utils.dependencies import get_current_user


@pytest.fixture()
def extraction_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    db = session_factory()
    owner = User(
        id=uuid.uuid4(),
        email=f"owner-{uuid.uuid4()}@example.com",
        hashed_password="x" * 80,
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)

    def override_db():
        yield db

    def override_current_user():
        return owner

    previous_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_current_user
    try:
        with TestClient(app) as client:
            yield client, owner, db
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
