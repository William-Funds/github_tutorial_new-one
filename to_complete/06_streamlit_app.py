from __future__ import annotations

from typing import Any, Dict


def build_streamlit_dashboard(visual_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare the data that a Streamlit app will render.

    Input contract:
    - visual_bundle["dataset_name"]: str
    - visual_bundle["metrics"]: dict
    - visual_bundle["figure_paths"]: list[str]
    - visual_bundle["chart_notes"]: list[str]
    - visual_bundle["sample_predictions"]: list[dict]

    Expected work:
    - build the layout for a Streamlit page
    - show the metrics
    - show the saved plots
    - show a small table of predictions

    Tip:
    - keep the page simple and visual first

    Output contract:
    - dataset_name: str
    - title: str
    - metrics: dict
    - figure_paths: list[str]
    - widgets: list[str]
    - sample_predictions: list[dict]
    """
    dataset_name = visual_bundle.get("dataset_name", "unknown_dataset")
    metrics = visual_bundle.get("metrics", {})
    figure_paths = visual_bundle.get("figure_paths", [])
    chart_notes = visual_bundle.get("chart_notes", [])
    sample_predictions = visual_bundle.get("sample_predictions", [])

    # Build a friendly page title. Use the one passed in if present,
    # otherwise turn "school_garden_water_need" into "School Garden Water Need".
    title = visual_bundle.get("title")
    if not title:
        pretty_name = dataset_name.replace("_", " ").title()
        title = f"{pretty_name} Dashboard"

    # Describe, in order, the pieces the Streamlit page will render.
    # These are simple labels the app can loop over to lay out the page.
    widgets = ["header", "metrics_summary"]
    widgets += [f"figure:{path}" for path in figure_paths]
    widgets += [f"note:{note}" for note in chart_notes]
    if sample_predictions:
        widgets.append("predictions_table")

    return {
        "dataset_name": dataset_name,
        "title": title,
        "metrics": metrics,
        "figure_paths": figure_paths,
        "widgets": widgets,
        "sample_predictions": sample_predictions,
    }


def render_dashboard(dashboard: Dict[str, Any]) -> None:
    """
    Draw the dashboard payload on a Streamlit page.

    This reads the dict returned by build_streamlit_dashboard and turns
    each part into a Streamlit widget. It is kept separate so the payload
    logic above can be tested without a running Streamlit server.
    """
    import os

    import streamlit as st

    st.title(dashboard["title"])
    st.caption(f"Dataset: {dashboard['dataset_name']}")

    # Metrics summary, one metric box per entry.
    metrics = dashboard.get("metrics", {})
    if metrics:
        st.subheader("Metrics")
        columns = st.columns(len(metrics))
        for column, (name, value) in zip(columns, metrics.items()):
            column.metric(name, value)

    # Saved plots from the visualization step.
    figure_paths = dashboard.get("figure_paths", [])
    if figure_paths:
        st.subheader("Charts")
        for path in figure_paths:
            if os.path.exists(path):
                st.image(path, caption=path)
            else:
                st.warning(f"Figure not found on disk yet: {path}")

    # Small table of sample predictions.
    sample_predictions = dashboard.get("sample_predictions", [])
    if sample_predictions:
        st.subheader("Sample predictions")
        st.table(sample_predictions)


def _demo_bundle() -> Dict[str, Any]:
    """A tiny stand-in bundle so the app can run before the other steps exist."""
    return {
        "dataset_name": "school_garden_water_need",
        "metrics": {"accuracy": 0.75, "precision": 0.70, "recall": 0.80},
        "figure_paths": ["artifacts/plots/confusion_matrix.png"],
        "chart_notes": ["Show the confusion matrix", "Show a metric summary"],
        "sample_predictions": [
            {"actual": "high", "predicted": "high"},
            {"actual": "low", "predicted": "low"},
        ],
    }


if __name__ == "__main__":
    # Run with: streamlit run to_complete/06_streamlit_app.py
    dashboard = build_streamlit_dashboard(_demo_bundle())
    render_dashboard(dashboard)
