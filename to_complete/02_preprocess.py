from __future__ import annotations

import random
from typing import Any, Dict, List


# The six inputs from the story, plus the label we want to predict.
FEATURE_NAMES = [
    "day_of_week",
    "weather",
    "temperature_c",
    "rainfall_mm",
    "soil_moisture",
    "crop_type",
]
TARGET_NAME = "water_need"

# Which features are text categories and which are plain numbers.
TEXT_FEATURES = {"day_of_week", "weather", "crop_type"}
NUMERIC_FEATURES = {"temperature_c", "rainfall_mm", "soil_moisture"}

# Fraction of rows used for training; the rest become the test set.
TRAIN_FRACTION = 0.8


def preprocess_event_data(raw_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Turn raw records into trainable data.

    Input contract:
    - raw_bundle["dataset_name"]: str
    - raw_bundle["source"]: str
    - raw_bundle["records"]: list[dict]

    Expected work:
    - clean missing values
    - normalize text fields
    - convert categories into model-friendly features
    - split the data into train and test rows

    Output contract:
    - dataset_name: str
    - feature_names: list[str]
    - target_name: str  # likely "water_need"
    - train_rows: list[dict]
    - test_rows: list[dict]
    - summary: dict
    """
    raw_bundle = raw_bundle or {}
    dataset_name = raw_bundle.get("dataset_name", "school_garden_water_need")
    records = raw_bundle.get("records", [])

    cleaned = [row for row in (_clean_row(rec) for rec in records) if row is not None]

    # Fill any missing numbers with that column's average, so no row is dropped
    # just because one measurement was blank.
    _fill_missing_numbers(cleaned)

    train_rows, test_rows = _split_rows(cleaned)

    summary = {
        "n_raw_records": len(records),
        "n_clean_rows": len(cleaned),
        "n_train_rows": len(train_rows),
        "n_test_rows": len(test_rows),
        "label_counts": _label_counts(cleaned),
    }

    return {
        "dataset_name": dataset_name,
        "feature_names": FEATURE_NAMES,
        "target_name": TARGET_NAME,
        "train_rows": train_rows,
        "test_rows": test_rows,
        "summary": summary,
    }


def _clean_row(record: Dict[str, Any]) -> Dict[str, Any] | None:
    """Normalize one raw record. Returns None if it has no usable label."""
    if not isinstance(record, dict):
        return None

    label = record.get(TARGET_NAME)
    if label is None or str(label).strip() == "":
        # Without a label we cannot train or score on this row.
        return None

    row: Dict[str, Any] = {}
    for feature in FEATURE_NAMES:
        value = record.get(feature)
        if feature in TEXT_FEATURES:
            row[feature] = _clean_text(value)
        else:
            row[feature] = _clean_number(value)

    row[TARGET_NAME] = str(label).strip().lower()
    return row


def _clean_text(value: Any) -> str:
    """Trim and lowercase text; use 'unknown' when the value is missing."""
    if value is None or str(value).strip() == "":
        return "unknown"
    return str(value).strip().lower()


def _clean_number(value: Any) -> float | None:
    """Convert to float; return None (a gap to fill later) if it is not a number."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fill_missing_numbers(rows: List[Dict[str, Any]]) -> None:
    """Replace any None numeric values with the column mean, in place."""
    for feature in NUMERIC_FEATURES:
        present = [row[feature] for row in rows if row.get(feature) is not None]
        mean_value = sum(present) / len(present) if present else 0.0
        for row in rows:
            if row.get(feature) is None:
                row[feature] = mean_value


def _split_rows(rows: List[Dict[str, Any]]):
    """Shuffle with a fixed seed, then split into train and test sets."""
    shuffled = list(rows)
    random.Random(7).shuffle(shuffled)

    split_index = int(len(shuffled) * TRAIN_FRACTION)
    # Guarantee at least one test row whenever we have more than one row.
    if len(shuffled) > 1:
        split_index = min(split_index, len(shuffled) - 1)

    return shuffled[:split_index], shuffled[split_index:]


def _label_counts(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in rows:
        label = row[TARGET_NAME]
        counts[label] = counts.get(label, 0) + 1
    return counts
