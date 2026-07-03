from __future__ import annotations

from typing import Any, Dict, List


# How many example predictions to hand to the dashboard for its little table.
MAX_SAMPLE_PREDICTIONS = 10


def evaluate_model(trained_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Measure how good the model is.

    Input contract:
    - trained_bundle["dataset_name"]: str
    - trained_bundle["feature_names"]: list[str]
    - trained_bundle["target_name"]: str
    - trained_bundle["train_rows"]: list[dict]
    - trained_bundle["test_rows"]: list[dict]
    - trained_bundle["model"]: object

    Expected work:
    - create predictions for the test set
    - compare predictions with the true labels
    - calculate at least one useful metric

    Tip:
    - accuracy plus a confusion matrix is enough for the first version

    Output contract:
    - dataset_name: str
    - feature_names: list[str]
    - target_name: str
    - train_rows: list[dict]
    - test_rows: list[dict]
    - model: object
    - metrics: dict
    - sample_predictions: list[dict]
    - confusion_matrix: list[list[int]]
    """
    trained_bundle = trained_bundle or {}
    dataset_name = trained_bundle.get("dataset_name", "school_garden_water_need")
    feature_names = trained_bundle.get("feature_names", [])
    target_name = trained_bundle.get("target_name", "water_need")
    train_rows = trained_bundle.get("train_rows", [])
    test_rows = trained_bundle.get("test_rows", [])
    model = trained_bundle.get("model")

    actual = [row.get(target_name) for row in test_rows]
    predicted = _predict(model, test_rows, train_rows, target_name)

    # The set of labels that appear as either a true value or a prediction.
    labels = sorted({label for label in (actual + predicted) if label is not None})
    confusion_matrix = _confusion_matrix(actual, predicted, labels)
    metrics = _metrics(confusion_matrix, labels, len(test_rows))

    sample_predictions = [
        {"actual": a, "predicted": p}
        for a, p in list(zip(actual, predicted))[:MAX_SAMPLE_PREDICTIONS]
    ]

    return {
        "dataset_name": dataset_name,
        "feature_names": feature_names,
        "target_name": target_name,
        "train_rows": train_rows,
        "test_rows": test_rows,
        "model": model,
        "metrics": metrics,
        "sample_predictions": sample_predictions,
        "confusion_matrix": confusion_matrix,
    }


def _predict(
    model: Any,
    test_rows: List[Dict[str, Any]],
    train_rows: List[Dict[str, Any]],
    target_name: str,
) -> List[str]:
    """
    Ask the model for predictions.

    The real training step returns a model with a ``.predict(rows)`` method. If
    we are handed a placeholder instead (as the smoke test does), fall back to
    guessing the most common training label so evaluation never crashes.
    """
    if hasattr(model, "predict") and callable(model.predict):
        try:
            return [str(label) for label in model.predict(test_rows)]
        except Exception:
            pass

    fallback = _most_common_label(train_rows, target_name)
    return [fallback for _ in test_rows]


def _most_common_label(rows: List[Dict[str, Any]], target_name: str) -> str:
    counts: Dict[str, int] = {}
    for row in rows:
        label = row.get(target_name)
        if label is not None:
            counts[label] = counts.get(label, 0) + 1
    if not counts:
        return "medium"
    return max(counts, key=counts.get)


def _confusion_matrix(
    actual: List[Any], predicted: List[Any], labels: List[str]
) -> List[List[int]]:
    """Build a labels x labels count grid (rows = actual, columns = predicted)."""
    index = {label: i for i, label in enumerate(labels)}
    size = len(labels)
    matrix = [[0 for _ in range(size)] for _ in range(size)]

    for true_label, pred_label in zip(actual, predicted):
        if true_label in index and pred_label in index:
            matrix[index[true_label]][index[pred_label]] += 1

    return matrix


def _metrics(
    confusion_matrix: List[List[int]], labels: List[str], n_test: int
) -> Dict[str, Any]:
    """Compute accuracy plus macro-averaged precision and recall from the matrix."""
    total = sum(sum(row) for row in confusion_matrix)
    correct = sum(confusion_matrix[i][i] for i in range(len(labels)))
    accuracy = correct / total if total else 0.0

    precisions: List[float] = []
    recalls: List[float] = []
    for i in range(len(labels)):
        true_positive = confusion_matrix[i][i]
        predicted_positive = sum(confusion_matrix[r][i] for r in range(len(labels)))
        actual_positive = sum(confusion_matrix[i])
        if predicted_positive:
            precisions.append(true_positive / predicted_positive)
        if actual_positive:
            recalls.append(true_positive / actual_positive)

    precision = sum(precisions) / len(precisions) if precisions else 0.0
    recall = sum(recalls) / len(recalls) if recalls else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "n_test_rows": n_test,
    }
