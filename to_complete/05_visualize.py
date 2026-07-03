from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import matplotlib

# Use a non-interactive backend so the figures render on any machine, even
# without a display attached (headless servers, CI, the workshop laptops).
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Where the plots get written. Later steps (the Streamlit dashboard) expect to
# find the confusion matrix under this folder.
PLOTS_DIR = Path("artifacts") / "plots"


def create_visual_report(evaluation_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Turn model results into plots and visual summaries.

    Input contract:
    - evaluation_bundle["dataset_name"]: str
    - evaluation_bundle["metrics"]: dict
    - evaluation_bundle["sample_predictions"]: list[dict]
    - evaluation_bundle["confusion_matrix"]: list[list[int]]

    Expected work:
    - create at least one plot with matplotlib or seaborn
    - save the figure to disk
    - prepare chart notes for the dashboard step

    Tip:
    - confusion matrix plots work well for beginners

    Output contract:
    - dataset_name: str
    - metrics: dict
    - figure_paths: list[str]
    - chart_notes: list[str]
    - sample_predictions: list[dict]
    """
    evaluation_bundle = evaluation_bundle or {}
    dataset_name = evaluation_bundle.get("dataset_name", "school_garden_water_need")
    metrics = evaluation_bundle.get("metrics", {})
    confusion_matrix = evaluation_bundle.get("confusion_matrix", [])
    sample_predictions = evaluation_bundle.get("sample_predictions", [])

    # Make sure the output folder exists before we try to save into it.
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    figure_paths: List[str] = []
    chart_notes: List[str] = []

    # --- Plot 1: confusion matrix -----------------------------------------
    if confusion_matrix:
        cm_path = _plot_confusion_matrix(confusion_matrix, dataset_name)
        figure_paths.append(cm_path)
        chart_notes.append(
            "Confusion matrix: rows are the true water needs, columns are the "
            "predictions. A strong model has big numbers on the diagonal."
        )

    # --- Plot 2: metric summary bar chart ---------------------------------
    if metrics:
        metrics_path = _plot_metric_summary(metrics, dataset_name)
        figure_paths.append(metrics_path)
        chart_notes.append(
            "Metric summary: taller bars are better. Accuracy, precision, and "
            "recall are all reported on a 0 to 1 scale."
        )

    if not chart_notes:
        chart_notes.append("No metrics or confusion matrix were provided to plot.")

    return {
        "dataset_name": dataset_name,
        "metrics": metrics,
        "figure_paths": figure_paths,
        "chart_notes": chart_notes,
        "sample_predictions": sample_predictions,
    }


def _plot_confusion_matrix(
    confusion_matrix: List[List[int]], dataset_name: str
) -> str:
    """Draw the confusion matrix as a labelled heatmap and save it to disk."""
    fig, ax = plt.subplots(figsize=(5, 4))
    image = ax.imshow(confusion_matrix, cmap="Blues")

    # Write the count inside each cell so the plot is readable without a legend.
    for row_index, row in enumerate(confusion_matrix):
        for col_index, value in enumerate(row):
            ax.text(
                col_index,
                row_index,
                str(value),
                ha="center",
                va="center",
                color="black",
            )

    ax.set_title(f"Confusion Matrix\n{dataset_name}")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    fig.colorbar(image, ax=ax)
    fig.tight_layout()

    out_path = PLOTS_DIR / "confusion_matrix.png"
    fig.savefig(out_path)
    plt.close(fig)
    return out_path.as_posix()


def _plot_metric_summary(metrics: Dict[str, Any], dataset_name: str) -> str:
    """Draw a simple bar chart of the numeric metrics and save it to disk."""
    # Keep only the metrics that are actual numbers we can plot.
    numeric_metrics = {
        name: float(value)
        for name, value in metrics.items()
        if isinstance(value, (int, float))
    }

    fig, ax = plt.subplots(figsize=(5, 4))
    names = list(numeric_metrics.keys())
    values = [numeric_metrics[name] for name in names]
    ax.bar(names, values, color="#2a9d8f")

    ax.set_ylim(0, 1)
    ax.set_title(f"Metric Summary\n{dataset_name}")
    ax.set_ylabel("Score")
    fig.tight_layout()

    out_path = PLOTS_DIR / "metric_summary.png"
    fig.savefig(out_path)
    plt.close(fig)
    return out_path.as_posix()
