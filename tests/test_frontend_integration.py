from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def api_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_events_endpoint_returns_a_list_and_allows_frontend_origin(api_client):
    response = api_client.get("/events/", headers={"Origin": "http://localhost"})

    assert response.status_code == 200
    assert response.json() == []
    assert response.headers["access-control-allow-origin"] == "http://localhost"


def test_created_event_is_available_to_frontend(api_client):
    event = {
        "title": "DevOps Workshop",
        "description": "Container integration test",
        "date": (date.today() + timedelta(days=1)).isoformat(),
        "location": "Constantine",
        "capacity": 30,
    }

    create_response = api_client.post("/events/", json=event)
    list_response = api_client.get("/events/")

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert list_response.json()[0]["title"] == event["title"]
    assert list_response.json()[0]["location"] == event["location"]
