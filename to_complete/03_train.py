from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier


# These features are text categories; the rest are treated as numbers.
CATEGORICAL_FEATURES = ["day_of_week", "weather", "crop_type"]


class WaterNeedModel:
    """
    A tiny wrapper around a scikit-learn pipeline.

    It keeps the workshop contract simple: the model can be trained on a list
    of feature dicts and can predict directly from the same kind of list. That
    way the evaluation step can just call ``model.predict(rows)`` without
    knowing anything about scikit-learn internals.
    """

    def __init__(self, feature_names: List[str], target_name: str) -> None:
        self.feature_names = feature_names
        self.target_name = target_name

        categorical = [f for f in feature_names if f in CATEGORICAL_FEATURES]
        numeric = [f for f in feature_names if f not in CATEGORICAL_FEATURES]

        preprocess = ColumnTransformer(
            transformers=[
                ("categories", OneHotEncoder(handle_unknown="ignore"), categorical),
                ("numbers", "passthrough", numeric),
            ]
        )

        # A small decision tree is easy to understand and enough for the workshop.
        self.pipeline: Pipeline = Pipeline(
            steps=[
                ("preprocess", preprocess),
                ("tree", DecisionTreeClassifier(max_depth=4, random_state=42)),
            ]
        )

    def _rows_to_frame(self, rows: List[Dict[str, Any]]) -> pd.DataFrame:
        frame = pd.DataFrame(rows)
        # Guarantee every expected feature column exists and is in a stable order.
        for feature in self.feature_names:
            if feature not in frame.columns:
                frame[feature] = None
        return frame[self.feature_names]

    def fit(self, train_rows: List[Dict[str, Any]]) -> "WaterNeedModel":
        features = self._rows_to_frame(train_rows)
        labels = [row[self.target_name] for row in train_rows]
        self.pipeline.fit(features, labels)
        return self

    def predict(self, rows: List[Dict[str, Any]]) -> List[str]:
        if not rows:
            return []
        features = self._rows_to_frame(rows)
        return list(self.pipeline.predict(features))


def train_model(processed_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fit a model on the training rows.

    Input contract:
    - processed_bundle["dataset_name"]: str
    - processed_bundle["feature_names"]: list[str]
    - processed_bundle["target_name"]: str
    - processed_bundle["train_rows"]: list[dict]
    - processed_bundle["test_rows"]: list[dict]

    Expected work:
    - pick a simple model first
    - train it on the training rows
    - store anything needed for evaluation later

    Tip:
    - a small decision tree or logistic regression is enough for this workshop

    Output contract:
    - dataset_name: str
    - feature_names: list[str]
    - target_name: str
    - train_rows: list[dict]
    - test_rows: list[dict]
    - model: object
    - training_summary: dict
    """
    dataset_name = processed_bundle["dataset_name"]
    feature_names = processed_bundle["feature_names"]
    target_name = processed_bundle["target_name"]
    train_rows = processed_bundle["train_rows"]
    test_rows = processed_bundle["test_rows"]

    # Build and train the small decision-tree model.
    model = WaterNeedModel(feature_names, target_name).fit(train_rows)

    # How well did the model learn the training data? (A sanity check, not a grade.)
    train_labels = [row[target_name] for row in train_rows]
    train_predictions = model.predict(train_rows)
    correct = sum(
        1 for actual, predicted in zip(train_labels, train_predictions)
        if actual == predicted
    )
    train_accuracy = correct / len(train_labels) if train_labels else 0.0

    label_counts: Dict[str, int] = {}
    for label in train_labels:
        label_counts[label] = label_counts.get(label, 0) + 1

    training_summary = {
        "model_type": "DecisionTreeClassifier",
        "n_train_rows": len(train_rows),
        "n_test_rows": len(test_rows),
        "n_features": len(feature_names),
        "classes": sorted(label_counts),
        "label_counts": label_counts,
        "train_accuracy": round(train_accuracy, 4),
    }

    return {
        "dataset_name": dataset_name,
        "feature_names": feature_names,
        "target_name": target_name,
        "train_rows": train_rows,
        "test_rows": test_rows,
        "model": model,
        "training_summary": training_summary,
    }
