from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.models import Event
from app.schemas import EventCreate


def test_create_valid_event(sample_event_dict):
    event = EventCreate(**sample_event_dict)

    assert event.title == sample_event_dict["title"]
    assert event.capacity == sample_event_dict["capacity"]


def test_reject_event_with_short_title(sample_event_dict):
    sample_event_dict["title"] = "AB"

    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)


def test_reject_event_with_invalid_capacity(sample_event_dict):
    sample_event_dict["capacity"] = 0

    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)


def test_create_event_in_database(mock_event_store, sample_event_dict):
    event = Event(**sample_event_dict)

    mock_event_store.add(event)
    mock_event_store.commit()
    mock_event_store.refresh(event)

    saved_event = (
        mock_event_store.query(Event)
        .filter_by(title=sample_event_dict["title"])
        .first()
    )

    assert saved_event is not None
    assert saved_event.id is not None
    assert saved_event.title == sample_event_dict["title"]
    assert saved_event.capacity == sample_event_dict["capacity"]

def test_reject_event_with_short_location(sample_event_dict):
    sample_event_dict["location"] = "A"

    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)
def test_reject_event_with_title_too_long(sample_event_dict):
    sample_event_dict["title"] = "A" * 101

    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)