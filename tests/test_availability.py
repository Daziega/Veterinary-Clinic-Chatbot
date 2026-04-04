"""Unit tests for the booking availability business rules.

These tests verify that the clinic's scheduling constraints are enforced
in code -- independent of the LLM or prompts.
"""
import json
from datetime import date, timedelta

import pytest

from clinic_bot.config import compute_duration
from clinic_bot.availability import (
    check_availability,
    create_booking,
    suggest_alternative_dates,
    _bookings,
    _reset_bookings,
)


def _next_weekday(weekday: int) -> str:
    """Return the next date (ISO format) that falls on the given weekday (0=Mon)."""
    today = date.today()
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return (today + timedelta(days=days_ahead)).isoformat()


@pytest.fixture(autouse=True)
def clean_bookings():
    """Reset the in-memory booking store before each test."""
    _reset_bookings()
    yield
    _reset_bookings()


# ------------------------------------------------------------------ config
class TestComputeDuration:
    def test_male_cat(self):
        assert compute_duration("cat", "male") == 12

    def test_female_cat(self):
        assert compute_duration("cat", "female") == 15

    def test_male_dog(self):
        assert compute_duration("dog", "male") == 30

    def test_female_dog_light(self):
        assert compute_duration("dog", "female", 8.0) == 45

    def test_female_dog_medium(self):
        assert compute_duration("dog", "female", 15.0) == 50

    def test_female_dog_heavy(self):
        assert compute_duration("dog", "female", 25.0) == 60

    def test_female_dog_very_heavy(self):
        assert compute_duration("dog", "female", 45.0) == 70

    def test_female_dog_requires_weight(self):
        with pytest.raises(ValueError, match="Weight is required"):
            compute_duration("dog", "female")

    def test_invalid_species(self):
        with pytest.raises(ValueError, match="Unsupported species"):
            compute_duration("rabbit", "male")


# -------------------------------------------------------- check_availability
class TestCheckAvailability:
    def test_available_monday(self):
        monday = _next_weekday(0)
        result = json.loads(check_availability(monday, "cat", "male"))
        assert result["status"] == "AVAILABLE"
        assert result["duration_minutes"] == 12

    def test_blocked_on_weekend(self):
        saturday = _next_weekday(5)
        result = json.loads(check_availability(saturday, "cat", "male"))
        assert result["status"] == "NOT_AVAILABLE"
        assert "operating day" in result["reason"].lower() or "not" in result["reason"].lower()

    def test_blocked_on_friday_for_dogs(self):
        friday = _next_weekday(4)
        result = json.loads(check_availability(friday, "dog", "male"))
        assert result["status"] == "NOT_AVAILABLE"

    def test_quota_exceeded(self):
        monday = _next_weekday(0)
        for _ in range(20):
            create_booking("O", "1", "C", "cat", "female", date=monday, age=2)
        result = json.loads(check_availability(monday, "cat", "female"))
        assert result["status"] == "NOT_AVAILABLE"
        assert "quota" in result["reason"].lower() or "remaining" in result["reason"].lower()

    def test_dog_limit_blocks_third_dog(self):
        monday = _next_weekday(0)
        create_booking("A", "1", "D1", "dog", "male", date=monday, age=3)
        create_booking("B", "2", "D2", "dog", "male", date=monday, age=4)
        result = json.loads(check_availability(monday, "dog", "male"))
        assert result["status"] == "NOT_AVAILABLE"
        assert "2 dogs" in result["reason"] or "dog" in result["reason"].lower()

    def test_cat_allowed_when_dog_limit_hit(self):
        monday = _next_weekday(0)
        create_booking("A", "1", "D1", "dog", "male", date=monday, age=3)
        create_booking("B", "2", "D2", "dog", "male", date=monday, age=4)
        result = json.loads(check_availability(monday, "cat", "male"))
        assert result["status"] == "AVAILABLE"


# ------------------------------------------------------------ create_booking
class TestCreateBooking:
    def test_successful_booking(self):
        monday = _next_weekday(0)
        result = json.loads(
            create_booking("John", "555", "Whiskers", "cat", "male", date=monday, age=2)
        )
        assert result["status"] == "CONFIRMED"
        assert result["booking"]["animal_name"] == "Whiskers"
        assert result["booking"]["drop_off_window"] == "08:00–09:00"

    def test_booking_dog(self):
        monday = _next_weekday(0)
        result = json.loads(
            create_booking("Jane", "555", "Rex", "dog", "male", date=monday, age=3)
        )
        assert result["status"] == "CONFIRMED"
        assert result["booking"]["drop_off_window"] == "09:00–10:30"

    def test_booking_rejected_when_full(self):
        monday = _next_weekday(0)
        for i in range(16):
            create_booking("O", "1", f"C{i}", "cat", "female", date=monday, age=2)
        result = json.loads(
            create_booking("X", "1", "Extra", "cat", "female", date=monday, age=2)
        )
        assert result["status"] == "NOT_AVAILABLE"

    def test_blood_test_flag_over_6(self):
        monday = _next_weekday(0)
        result = json.loads(
            create_booking("John", "555", "Old Cat", "cat", "male", date=monday, age=8)
        )
        assert result["status"] == "CONFIRMED"
        assert result["booking"]["blood_test_required"] is True

    def test_no_blood_test_under_6(self):
        monday = _next_weekday(0)
        result = json.loads(
            create_booking("John", "555", "Young Cat", "cat", "male", date=monday, age=3)
        )
        assert result["status"] == "CONFIRMED"
        assert result["booking"]["blood_test_required"] is False


# ------------------------------------------------ suggest_alternative_dates
class TestSuggestAlternativeDates:
    def test_returns_available_dates(self):
        result = json.loads(suggest_alternative_dates("cat", "male"))
        assert len(result["available_dates"]) > 0
        assert result["duration_minutes"] == 12

    def test_skips_weekends(self):
        result = json.loads(suggest_alternative_dates("dog", "male"))
        for iso_date in result["available_dates"]:
            d = date.fromisoformat(iso_date)
            assert d.weekday() in [0, 1, 2, 3], f"{iso_date} is not Mon-Thu"
