from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Event, Participant, Registration


@pytest.fixture
def sample_event_dict():
    return {
        "title": "Python Workshop",
        "description": "A workshop about Python programming",
        "date": date.today() + timedelta(days=10),
        "location": "Constantine",
        "capacity": 30,
    }


@pytest.fixture
def sample_participant_dict():
    return {
        "name": "Ahmed Benali",
        "email": "ahmed.benali@example.com",
    }


@pytest.fixture
def mock_event_store():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def prepopulated_event_store(mock_event_store):
    event = Event(
        title="Python Workshop",
        description="A workshop about Python programming",
        date=date.today() + timedelta(days=10),
        location="Constantine",
        capacity=30,
    )

    another_event = Event(
        title="Cybersecurity Conference",
        description="An introduction to cybersecurity",
        date=date.today() + timedelta(days=20),
        location="Algiers",
        capacity=50,
    )

    mock_event_store.add_all([event, another_event])
    mock_event_store.commit()

    return mock_event_store


@pytest.fixture
def global_environment_logger():
    return {
        "events_created": 0,
        "participants_created": 0,
        "registrations_created": 0,
    }