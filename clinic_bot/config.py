"""Centralized configuration for the veterinary clinic business rules.

All booking logic, tool implementations, and prompts should read from
these constants so that a single change here propagates everywhere.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Operating schedule
# ---------------------------------------------------------------------------

OPERATING_DAYS: list[int] = [0, 1, 2, 3]  # Monday=0 … Thursday=3

MAX_DAILY_MINUTES: int = 240

MAX_DOGS_PER_DAY: int = 2

# ---------------------------------------------------------------------------
# Service time costs (minutes)
# ---------------------------------------------------------------------------

CAT_TIME_COSTS: dict[str, int] = {
    "male": 12,
    "female": 15,
}

DOG_TIME_COSTS_MALE: int = 30

DOG_TIME_COSTS_FEMALE: list[tuple[float, float, int]] = [
    (0, 10, 45),
    (10, 20, 50),
    (20, 30, 60),
    (30, 40, 60),
    (40, float("inf"), 70),
]

# ---------------------------------------------------------------------------
# Drop-off windows
# ---------------------------------------------------------------------------

DROP_OFF_WINDOWS: dict[str, dict] = {
    "cat": {
        "start": "08:00",
        "end": "09:00",
        "days": [0, 1, 2, 3, 4],  # Mon-Fri
    },
    "dog": {
        "start": "09:00",
        "end": "10:30",
        "days": [0, 1, 2, 3],  # Mon-Thu
    },
}


# ---------------------------------------------------------------------------
# Duration calculator
# ---------------------------------------------------------------------------


def compute_duration(species: str, sex: str, weight_kg: float | None = None) -> int:
    """Return the time cost in minutes for a surgery.

    Raises ValueError if inputs are invalid or weight is missing for female dogs.
    """
    species = species.strip().lower()
    sex = sex.strip().lower()

    if species == "cat":
        if sex not in CAT_TIME_COSTS:
            raise ValueError(f"Invalid sex for cat: {sex}")
        return CAT_TIME_COSTS[sex]

    if species == "dog":
        if sex == "male":
            return DOG_TIME_COSTS_MALE
        if sex == "female":
            if weight_kg is None:
                raise ValueError("Weight is required for female dogs")
            for low, high, minutes in DOG_TIME_COSTS_FEMALE:
                if low <= weight_kg < high:
                    return minutes
            # Fallback for exactly 40 kg boundary — covered by (30, 40, 60) range
            raise ValueError(f"Could not determine duration for female dog at {weight_kg} kg")
        raise ValueError(f"Invalid sex for dog: {sex}")

    raise ValueError(f"Unsupported species: {species}")
