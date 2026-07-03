from __future__ import annotations

import random
from typing import Any, Dict, List


# The controlled story: predict how much water a garden plot needs.
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEATHERS = ["sunny", "cloudy", "rainy"]
CROPS = ["maize", "beans", "tomato", "cassava"]

# How many rows to generate when we build the synthetic dataset.
DEFAULT_ROW_COUNT = 240


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
    limit = config.get("limit")

    # A fixed seed keeps the dataset the same every run, so every group member
    # sees identical numbers. That makes the workshop easier to debug together.
    rng = random.Random(42)

    records: List[Dict[str, Any]] = []
    for _ in range(DEFAULT_ROW_COUNT):
        weather = rng.choice(WEATHERS)
        records.append(_make_record(rng, weather))

    # Respect an optional row cap from the caller (used by the smoke test).
    if isinstance(limit, int) and limit > 0:
        records = records[:limit]

    notes = [
        "Synthetic school-garden dataset generated for the AI 4 Africa workshop.",
        "Each row is one daily observation of a garden plot.",
        "The label 'water_need' is one of: low, medium, high.",
        f"Generated {len(records)} rows with a fixed random seed for reproducibility.",
    ]

    return {
        "dataset_name": dataset_name,
        "source": source,
        "records": records,
        "notes": notes,
    }


def _make_record(rng: random.Random, weather: str) -> Dict[str, Any]:
    """Build a single believable observation with a learnable water-need label."""
    # Rainfall depends on the weather, which keeps the story realistic.
    if weather == "rainy":
        rainfall_mm = rng.randint(8, 25)
    elif weather == "cloudy":
        rainfall_mm = rng.randint(0, 8)
    else:  # sunny
        rainfall_mm = rng.randint(0, 2)

    temperature_c = rng.randint(18, 38)
    soil_moisture = rng.randint(5, 90)

    record = {
        "day_of_week": rng.choice(DAYS),
        "weather": weather,
        "temperature_c": temperature_c,
        "rainfall_mm": rainfall_mm,
        "soil_moisture": soil_moisture,
        "crop_type": rng.choice(CROPS),
    }
    record["water_need"] = _water_need_label(temperature_c, rainfall_mm, soil_moisture)
    return record


def _water_need_label(temperature_c: int, rainfall_mm: int, soil_moisture: int) -> str:
    """
    Turn the numbers into a low/medium/high label.

    The idea is simple and physical: dry soil, little rain, and high heat mean
    the plot needs more water. Wet soil or lots of rain means it needs less.
    """
    # A higher "dryness" score means the plot needs more water.
    dryness = (100 - soil_moisture) * 0.5 + temperature_c - rainfall_mm * 1.5

    if soil_moisture > 60 or rainfall_mm > 15:
        return "low"
    if dryness > 45 or soil_moisture < 25:
        return "high"
    return "medium"
