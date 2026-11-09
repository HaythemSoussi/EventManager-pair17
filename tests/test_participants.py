
import pytest
from datetime import date, timedelta

from pydantic import ValidationError

from app.schemas import ParticipantCreate

from app.models import Participant

from sqlalchemy.exc import IntegrityError

from app.models import Event, Registration



def test_create_valid_participant():
    participant = ParticipantCreate(
        name="Ahmed Benali",
        email="ahmed.benali@example.com",
    )

    assert participant.name == "Ahmed Benali"
    assert participant.email == "ahmed.benali@example.com"


def test_reject_participant_with_short_name():
    with pytest.raises(ValidationError):
        ParticipantCreate(
            name="A",
            email="ahmed.benali@example.com",
        )


def test_reject_participant_with_invalid_email():
    with pytest.raises(ValidationError):
        ParticipantCreate(
            name="Ahmed Benali",
            email="not-an-email",
        )


def test_create_participant_in_database(mock_event_store):
    participant = Participant(
        name="Ahmed Benali",
        email="ahmed.benali@example.com",
    )

    mock_event_store.add(participant)
    mock_event_store.commit()
    mock_event_store.refresh(participant)

    saved_participant = (
        mock_event_store.query(Participant)
        .filter_by(email="ahmed.benali@example.com")
        .first()
    )

    assert saved_participant is not None
    assert saved_participant.id is not None
    assert saved_participant.name == "Ahmed Benali"
    assert saved_participant.email == "ahmed.benali@example.com"


def test_prevent_duplicate_registration(mock_event_store):
    event = Event(
        title="Python Workshop",
        description="Python programming workshop",
        date=date.today() + timedelta(days=10),
        location="Constantine",
        capacity=30,
    )

    participant = Participant(
        name="Ahmed Benali",
        email="ahmed.benali@example.com",
    )

    mock_event_store.add_all([event, participant])
    mock_event_store.commit()

    registration = Registration(
        event_id=event.id,
        participant_id=participant.id,
    )
    mock_event_store.add(registration)
    mock_event_store.commit()

    duplicate_registration = Registration(
        event_id=event.id,
        participant_id=participant.id,
    )
    mock_event_store.add(duplicate_registration)

    with pytest.raises(IntegrityError):
        mock_event_store.commit()

    mock_event_store.rollback()

    registrations = (
        mock_event_store.query(Registration)
        .filter_by(
            event_id=event.id,
            participant_id=participant.id,
        )
        .count()
    )

    assert registrations == 1




def test_reject_participant_work_does_not_apply_to_event_capacity():
    from pydantic import ValidationError
    from app.schemas import EventCreate
    from datetime import date, timedelta

    with pytest.raises(ValidationError):
        EventCreate(
            title="Python Workshop",
            description="A workshop about Python",
            date=date.today() + timedelta(days=10),
            location="Constantine",
            capacity=10001,
        )
