from __future__ import annotations

import random
from typing import Any, Dict, List


# Fixed vocabularies keep every group working from the same relatable story.
DAYS_OF_WEEK = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
WEATHER_TYPES = ["sunny", "cloudy", "rainy"]
CROP_TYPES = ["maize", "beans", "tomato"]


def _decide_water_need(
    weather: str, temperature_c: int, soil_moisture: int, rainfall_mm: int
) -> str:
    """
    Turn the weather-and-soil observation into a water need label.

    This is a simple, human-readable rule so the dataset feels realistic:
    - very dry soil (or a hot, dry day) needs more water
    - wet soil or recent rain needs less water
    - everything in between lands on "medium"
    """
    dryness = 0

    if soil_moisture < 30:
        dryness += 2
    elif soil_moisture < 55:
        dryness += 1

    if temperature_c >= 30:
        dryness += 1

    if weather == "sunny" and rainfall_mm == 0:
        dryness += 1
    elif weather == "rainy" or rainfall_mm >= 10:
        dryness -= 1

    if dryness >= 3:
        return "high"
    if dryness <= 0:
        return "low"
    return "medium"


def _generate_records(count: int) -> List[Dict[str, Any]]:
    """Build a list of synthetic garden observations."""
    rng = random.Random(42)

    records: List[Dict[str, Any]] = []
    for _ in range(count):
        weather = rng.choice(WEATHER_TYPES)

        if weather == "rainy":
            rainfall_mm = rng.randint(8, 30)
        elif weather == "cloudy":
            rainfall_mm = rng.randint(0, 8)
        else:
            rainfall_mm = 0

        temperature_c = rng.randint(18, 38)
        soil_moisture = rng.randint(10, 80)
        day_of_week = rng.choice(DAYS_OF_WEEK)
        crop_type = rng.choice(CROP_TYPES)

        water_need = _decide_water_need(
            weather, temperature_c, soil_moisture, rainfall_mm
        )

        records.append(
            {
                "day_of_week": day_of_week,
                "weather": weather,
                "temperature_c": temperature_c,
                "rainfall_mm": rainfall_mm,
                "soil_moisture": soil_moisture,
                "crop_type": crop_type,
                "water_need": water_need,
            }
        )

    return records


def fetch_event_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create or load the controlled synthetic dataset for the workshop pipeline.

    Input contract:
    - config["dataset_name"]: human-friendly name for the dataset.
    - config["source"]: should be the string "synthetic" for this starter repo.
    - config["limit"]: optional maximum number of rows to keep.

    Output contract:
    - dataset_name: str
    - source: str
    - records: list[dict]
    - notes: list[str]

    Suggested beginner story:
    - use a fictional school garden / community farm story
    - keep one row per weather-and-soil observation
    - do not change the output keys
    """
    config = config or {}
    dataset_name = config.get("dataset_name", "school_garden_water_need")
    source = config.get("source", "synthetic")

    default_size = 200
    limit = config.get("limit")

    if isinstance(limit, int) and limit > 0:
        row_count = limit
    else:
        row_count = default_size

    records = _generate_records(row_count)

    notes = [
        "Fully synthetic school garden / community farm dataset.",
        "Each row is one weather-and-soil observation for a garden plot.",
        "The target 'water_need' is one of: low, medium, high.",
        f"Generated {len(records)} rows with a fixed random seed for reproducibility.",
    ]

    return {
        "dataset_name": dataset_name,
        "source": source,
        "records": records,
        "notes": notes,
    }
