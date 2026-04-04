"""Integration tests: scripted booking scenarios.

These simulate the full booking flow that the agent would execute
by calling the tools in sequence, verifying that the business rules
hold across multi-step interactions.

Per the langchain-expert skill checklist:
- Happy-path booking (cat)
- Happy-path booking (dog)
- Day rejected due to quota
- Day rejected due to dog limit but still available for cats
"""
import json
from datetime import date, timedelta

import pytest

from clinic_bot.availability import (
    check_availability,
    create_booking,
    suggest_alternative_dates,
    _reset_bookings,
)


def _next_weekday(weekday: int) -> str:
    today = date.today()
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return (today + timedelta(days=days_ahead)).isoformat()


@pytest.fixture(autouse=True)
def clean_bookings():
    _reset_bookings()
    yield
    _reset_bookings()


class TestHappyPathCatBooking:
    """Full booking flow for a female cat sterilisation."""

    def test_end_to_end(self):
        monday = _next_weekday(0)

        avail = json.loads(check_availability(monday, "cat", "female"))
        assert avail["status"] == "AVAILABLE"
        assert avail["duration_minutes"] == 15
        assert avail["drop_off_window"] == "08:00–09:00"

        booking = json.loads(create_booking(
            owner_name="Maria Garcia",
            phone="+34 612 345 678",
            animal_name="Luna",
            species="cat",
            sex="female",
            date=monday,
            age=2,
            health_notes="Healthy, vaccinated",
        ))
        assert booking["status"] == "CONFIRMED"
        assert booking["booking"]["animal_name"] == "Luna"
        assert booking["booking"]["duration_minutes"] == 15
        assert booking["booking"]["drop_off_window"] == "08:00–09:00"
        assert booking["booking"]["blood_test_required"] is False

        avail_after = json.loads(check_availability(monday, "cat", "female"))
        assert avail_after["status"] == "AVAILABLE"
        assert avail_after["remaining_minutes"] == 240 - 15 - 15


class TestHappyPathDogBooking:
    """Full booking flow for a female dog sterilisation (25 kg)."""

    def test_end_to_end(self):
        tuesday = _next_weekday(1)

        avail = json.loads(check_availability(tuesday, "dog", "female", weight_kg=25.0))
        assert avail["status"] == "AVAILABLE"
        assert avail["duration_minutes"] == 60
        assert avail["drop_off_window"] == "09:00–10:30"

        booking = json.loads(create_booking(
            owner_name="Carlos Lopez",
            phone="+34 698 765 432",
            animal_name="Rocky",
            species="dog",
            sex="female",
            weight_kg=25.0,
            date=tuesday,
            age=3,
            health_notes="",
        ))
        assert booking["status"] == "CONFIRMED"
        assert booking["booking"]["animal_name"] == "Rocky"
        assert booking["booking"]["duration_minutes"] == 60
        assert booking["booking"]["drop_off_window"] == "09:00–10:30"
        assert booking["booking"]["blood_test_required"] is False

        avail_after = json.loads(check_availability(tuesday, "dog", "male"))
        assert avail_after["status"] == "AVAILABLE"
        assert avail_after["dog_count"] == 2


class TestOldAnimalBloodTestRequired:
    """Booking a 9-year-old cat triggers the blood test flag."""

    def test_blood_test_flag(self):
        wednesday = _next_weekday(2)

        booking = json.loads(create_booking(
            owner_name="Ana Ruiz",
            phone="+34 600 111 222",
            animal_name="Viejo",
            species="cat",
            sex="male",
            date=wednesday,
            age=9,
        ))
        assert booking["status"] == "CONFIRMED"
        assert booking["booking"]["blood_test_required"] is True


class TestDayRejectedDueToQuota:
    """Fill a day to 240 minutes, then verify the next booking is rejected."""

    def test_quota_full_rejects_then_suggests_alternatives(self):
        thursday = _next_weekday(3)

        for i in range(16):
            result = json.loads(create_booking(
                "Owner", "555", f"Cat{i}", "cat", "female", date=thursday, age=1
            ))
            assert result["status"] == "CONFIRMED", f"Booking {i} should succeed"

        rejected = json.loads(check_availability(thursday, "cat", "female"))
        assert rejected["status"] == "NOT_AVAILABLE"
        assert "quota" in rejected["reason"].lower() or "remaining" in rejected["reason"].lower()

        alternatives = json.loads(suggest_alternative_dates("cat", "female"))
        assert len(alternatives["available_dates"]) > 0
        assert thursday not in alternatives["available_dates"]


class TestDogLimitButCatsStillAllowed:
    """2 dogs fill the dog limit; a 3rd dog is rejected; cats still accepted."""

    def test_dog_limit_then_cat_allowed(self):
        monday = _next_weekday(0)

        dog1 = json.loads(create_booking(
            "Owner A", "111", "Fido", "dog", "male", date=monday, age=2
        ))
        assert dog1["status"] == "CONFIRMED"

        dog2 = json.loads(create_booking(
            "Owner B", "222", "Buddy", "dog", "male", date=monday, age=4
        ))
        assert dog2["status"] == "CONFIRMED"

        dog3_avail = json.loads(check_availability(monday, "dog", "male"))
        assert dog3_avail["status"] == "NOT_AVAILABLE"
        assert "dog" in dog3_avail["reason"].lower()

        dog3_booking = json.loads(create_booking(
            "Owner C", "333", "Rex", "dog", "male", date=monday, age=3
        ))
        assert dog3_booking["status"] == "NOT_AVAILABLE"

        cat_avail = json.loads(check_availability(monday, "cat", "male"))
        assert cat_avail["status"] == "AVAILABLE"

        cat_booking = json.loads(create_booking(
            "Owner D", "444", "Whiskers", "cat", "male", date=monday, age=1
        ))
        assert cat_booking["status"] == "CONFIRMED"
        assert cat_booking["booking"]["drop_off_window"] == "08:00–09:00"


class TestWeekendAndFridayBlocking:
    """Surgery is Mon-Thu only. Friday/weekends blocked by default."""

    def test_friday_dog_blocked(self):
        friday = _next_weekday(4)
        result = json.loads(check_availability(friday, "dog", "male"))
        assert result["status"] == "NOT_AVAILABLE"

    def test_friday_cat_blocked(self):
        """Friday is not an operating day by default (surgery Mon-Thu only)."""
        friday = _next_weekday(4)
        result = json.loads(check_availability(friday, "cat", "male"))
        assert result["status"] == "NOT_AVAILABLE"

    def test_saturday_blocked(self):
        saturday = _next_weekday(5)
        result = json.loads(check_availability(saturday, "cat", "male"))
        assert result["status"] == "NOT_AVAILABLE"

    def test_sunday_blocked(self):
        sunday = _next_weekday(6)
        result = json.loads(check_availability(sunday, "dog", "male"))
        assert result["status"] == "NOT_AVAILABLE"


class TestSuggestAlternativeDatesMultiStep:
    """When preferred date is full, alternatives must all be valid."""

    def test_alternatives_respect_all_rules(self):
        monday = _next_weekday(0)
        for i in range(16):
            create_booking("O", "1", f"C{i}", "cat", "female", date=monday, age=1)

        alternatives = json.loads(suggest_alternative_dates("cat", "female"))
        for iso_date in alternatives["available_dates"]:
            avail = json.loads(check_availability(iso_date, "cat", "female"))
            assert avail["status"] == "AVAILABLE", f"{iso_date} should be available"
