"""Booking availability tools that enforce clinic business rules in code.

These are pure-function tools: the LLM can call them, but cannot override
their results. All quota, dog-limit, and drop-off validation happens here.
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from .config import (
    OPERATING_DAYS,
    MAX_DAILY_MINUTES,
    MAX_DOGS_PER_DAY,
    DROP_OFF_WINDOWS,
    compute_duration,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory booking store (MVP — replace with DB later)
# ---------------------------------------------------------------------------

_bookings: dict[str, list[dict[str, Any]]] = defaultdict(list)


def _reset_bookings() -> None:
    """Clear all bookings (used in tests)."""
    _bookings.clear()


def _day_stats(iso_date: str) -> tuple[int, int]:
    """Return (minutes_occupied, dog_count) for a given date."""
    entries = _bookings.get(iso_date, [])
    minutes = sum(e["duration"] for e in entries)
    dogs = sum(1 for e in entries if e["species"] == "dog")
    return minutes, dogs


# ---------------------------------------------------------------------------
# Tool input schemas
# ---------------------------------------------------------------------------


class CheckAvailabilityInput(BaseModel):
    date: str = Field(description="Desired surgery date in YYYY-MM-DD format")
    species: str = Field(description="Animal species: 'cat' or 'dog'")
    sex: str = Field(description="Animal sex: 'male' or 'female'")
    weight_kg: float | None = Field(default=None, description="Weight in kg (required for female dogs)")


class CreateBookingInput(BaseModel):
    owner_name: str = Field(description="Pet owner's full name")
    phone: str = Field(description="Contact phone number")
    animal_name: str = Field(description="Name of the animal")
    species: str = Field(description="'cat' or 'dog'")
    sex: str = Field(description="'male' or 'female'")
    weight_kg: float | None = Field(default=None, description="Weight in kg (required for dogs)")
    age: float = Field(description="Animal's age in years")
    health_notes: str = Field(default="", description="Any known health conditions")
    date: str = Field(description="Surgery date in YYYY-MM-DD format")


class SuggestAlternativeDatesInput(BaseModel):
    species: str = Field(description="'cat' or 'dog'")
    sex: str = Field(description="'male' or 'female'")
    weight_kg: float | None = Field(default=None, description="Weight in kg (required for female dogs)")


# ---------------------------------------------------------------------------
# Core logic (deterministic, testable)
# ---------------------------------------------------------------------------


def _is_operating_day(d: date) -> bool:
    return d.weekday() in OPERATING_DAYS


def _validate_date(iso_date: str, species: str, duration: int) -> dict[str, Any]:
    """Validate a date against all business rules. Returns a result dict."""
    try:
        d = date.fromisoformat(iso_date)
    except ValueError:
        return {"status": "NOT_AVAILABLE", "reason": f"Invalid date format: {iso_date}"}

    if d < date.today():
        return {"status": "NOT_AVAILABLE", "reason": "Date is in the past"}

    if not _is_operating_day(d):
        return {"status": "NOT_AVAILABLE", "reason": f"{d.strftime('%A')} is not an operating day (Mon-Thu only)"}

    window = DROP_OFF_WINDOWS.get(species)
    if window and d.weekday() not in window["days"]:
        return {
            "status": "NOT_AVAILABLE",
            "reason": f"No drop-off window for {species} on {d.strftime('%A')}",
        }

    minutes_occupied, dog_count = _day_stats(iso_date)
    remaining = MAX_DAILY_MINUTES - minutes_occupied

    if minutes_occupied + duration > MAX_DAILY_MINUTES:
        return {
            "status": "NOT_AVAILABLE",
            "reason": f"Exceeds daily 240-minute quota (remaining: {remaining} min, needed: {duration} min)",
            "remaining_minutes": remaining,
            "dog_count": dog_count,
        }

    if species == "dog" and dog_count >= MAX_DOGS_PER_DAY:
        return {
            "status": "NOT_AVAILABLE",
            "reason": f"Maximum {MAX_DOGS_PER_DAY} dogs already scheduled for this day",
            "remaining_minutes": remaining,
            "dog_count": dog_count,
        }

    drop_off = DROP_OFF_WINDOWS.get(species, {})
    return {
        "status": "AVAILABLE",
        "remaining_minutes": remaining - duration,
        "dog_count": dog_count + (1 if species == "dog" else 0),
        "drop_off_window": f"{drop_off.get('start', '?')}–{drop_off.get('end', '?')}",
        "duration_minutes": duration,
    }


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


def check_availability(
    date: str,
    species: str,
    sex: str,
    weight_kg: float | None = None,
) -> str:
    """Check whether a surgery date is available for the given animal."""
    species = species.strip().lower()
    sex = sex.strip().lower()
    try:
        duration = compute_duration(species, sex, weight_kg)
    except ValueError as exc:
        return json.dumps({"status": "ERROR", "reason": str(exc)})

    result = _validate_date(date, species, duration)
    logger.info("check_availability date=%s species=%s → %s", date, species, result["status"])
    return json.dumps(result)


def create_booking(
    owner_name: str,
    phone: str,
    animal_name: str,
    species: str,
    sex: str,
    weight_kg: float | None = None,
    age: float = 0,
    health_notes: str = "",
    date: str = "",
) -> str:
    """Create a surgery booking after validating all business rules."""
    species = species.strip().lower()
    sex = sex.strip().lower()

    try:
        duration = compute_duration(species, sex, weight_kg)
    except ValueError as exc:
        return json.dumps({"status": "ERROR", "reason": str(exc)})

    validation = _validate_date(date, species, duration)
    if validation["status"] != "AVAILABLE":
        return json.dumps(validation)

    blood_test_required = age > 6

    booking = {
        "owner_name": owner_name,
        "phone": phone,
        "animal_name": animal_name,
        "species": species,
        "sex": sex,
        "weight_kg": weight_kg,
        "age": age,
        "health_notes": health_notes,
        "date": date,
        "duration": duration,
    }
    _bookings[date].append(booking)

    drop_off = DROP_OFF_WINDOWS.get(species, {})
    logger.info("create_booking date=%s animal=%s owner=%s", date, animal_name, owner_name)

    return json.dumps({
        "status": "CONFIRMED",
        "booking": {
            "date": date,
            "animal_name": animal_name,
            "species": species,
            "duration_minutes": duration,
            "drop_off_window": f"{drop_off.get('start', '?')}–{drop_off.get('end', '?')}",
            "blood_test_required": blood_test_required,
        },
    })


def suggest_alternative_dates(
    species: str,
    sex: str,
    weight_kg: float | None = None,
) -> str:
    """Find the next available operating days for the requested surgery."""
    species = species.strip().lower()
    sex = sex.strip().lower()

    try:
        duration = compute_duration(species, sex, weight_kg)
    except ValueError as exc:
        return json.dumps({"status": "ERROR", "reason": str(exc)})

    available: list[str] = []
    d = date.today()
    for _ in range(60):
        d += timedelta(days=1)
        result = _validate_date(d.isoformat(), species, duration)
        if result["status"] == "AVAILABLE":
            available.append(d.isoformat())
            if len(available) >= 5:
                break

    return json.dumps({"available_dates": available, "duration_minutes": duration})


# ---------------------------------------------------------------------------
# LangChain StructuredTool wrappers
# ---------------------------------------------------------------------------

check_availability_tool = StructuredTool.from_function(
    func=check_availability,
    name="check_availability",
    description=(
        "Check whether a specific date is available for a sterilisation surgery. "
        "MUST be called before creating any booking. Returns AVAILABLE or NOT_AVAILABLE "
        "with remaining capacity details."
    ),
    args_schema=CheckAvailabilityInput,
)

create_booking_tool = StructuredTool.from_function(
    func=create_booking,
    name="create_booking",
    description=(
        "Create a confirmed surgery booking. Only call this AFTER check_availability "
        "returns AVAILABLE and the client has confirmed they want to proceed. "
        "All client and animal fields are required."
    ),
    args_schema=CreateBookingInput,
)

suggest_alternative_dates_tool = StructuredTool.from_function(
    func=suggest_alternative_dates,
    name="suggest_alternative_dates",
    description=(
        "Find up to 5 next available dates for a sterilisation surgery. "
        "Call this when the client's preferred date is not available, "
        "or when the client asks what dates are open."
    ),
    args_schema=SuggestAlternativeDatesInput,
)
