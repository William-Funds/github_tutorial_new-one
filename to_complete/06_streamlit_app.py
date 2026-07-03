from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable, Dict


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
<<<<<<< HEAD
    visual_bundle = visual_bundle or {}
    dataset_name = visual_bundle.get("dataset_name", "school_garden_water_need")
=======
    dataset_name = visual_bundle.get("dataset_name", "unknown_dataset")
>>>>>>> b083eca4ef8e9a95f278691d39a7a2172ae824d5
    metrics = visual_bundle.get("metrics", {})
    figure_paths = visual_bundle.get("figure_paths", [])
    chart_notes = visual_bundle.get("chart_notes", [])
    sample_predictions = visual_bundle.get("sample_predictions", [])

<<<<<<< HEAD
    title = visual_bundle.get("title") or f"{_prettify(dataset_name)} Dashboard"

    # "widgets" is a simple, ordered plan of what the page will render. Keeping
    # it as plain strings means the dashboard is easy to inspect and test.
    widgets = [f"header: {title}"]
    for name, value in metrics.items():
        widgets.append(f"metric: {name} = {value}")
    for path in figure_paths:
        widgets.append(f"image: {path}")
    for note in chart_notes:
        widgets.append(f"caption: {note}")
    if sample_predictions:
        widgets.append("table: sample predictions (actual vs predicted)")
=======
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
>>>>>>> b083eca4ef8e9a95f278691d39a7a2172ae824d5

    return {
        "dataset_name": dataset_name,
        "title": title,
        "metrics": metrics,
        "figure_paths": figure_paths,
        "widgets": widgets,
        "sample_predictions": sample_predictions,
    }


<<<<<<< HEAD
def _prettify(name: str) -> str:
    """Turn 'school_garden_water_need' into 'School Garden Water Need'."""
    return name.replace("_", " ").title()


# ---------------------------------------------------------------------------
# Live Streamlit page
#
# The code below only runs when the file is launched with:
#     streamlit run to_complete/06_streamlit_app.py
# It runs the whole pipeline (steps 01 -> 05), builds the dashboard payload,
# and renders it. When main.py imports this file for its contract check, the
# module name is not "__main__", so none of this executes.
# ---------------------------------------------------------------------------


def _load_step(file_name: str, function_name: str) -> Callable[[Dict[str, Any]], Any]:
    """Load one numbered pipeline file from this folder by path."""
    path = Path(__file__).resolve().parent / file_name
    module_name = f"step_{path.stem.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ModuleNotFoundError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def _run_pipeline() -> Dict[str, Any]:
    """Chain steps 01 -> 05 and return the visual bundle for the dashboard."""
    fetch = _load_step("01_data_fetch.py", "fetch_event_data")
    preprocess = _load_step("02_preprocess.py", "preprocess_event_data")
    train = _load_step("03_train.py", "train_model")
    evaluate = _load_step("04_evaluate.py", "evaluate_model")
    visualize = _load_step("05_visualize.py", "create_visual_report")

    raw = fetch({"dataset_name": "school_garden_water_need", "source": "synthetic"})
    processed = preprocess(raw)
    trained = train(processed)
    evaluated = evaluate(trained)
    return visualize(evaluated)


def _render() -> None:
    import streamlit as st

    st.set_page_config(page_title="School Garden Water Need", layout="centered")

    visual_bundle = _run_pipeline()
    dashboard = build_streamlit_dashboard(visual_bundle)

    st.title(dashboard["title"])
    st.caption(f"Dataset: {dashboard['dataset_name']}")

    # Metrics row.
    metrics = dashboard["metrics"]
    if metrics:
        st.subheader("Model metrics")
        columns = st.columns(len(metrics))
        for column, (name, value) in zip(columns, metrics.items()):
            display = f"{value:.2f}" if isinstance(value, float) else str(value)
            column.metric(name.replace("_", " ").title(), display)

    # Saved plots.
    figure_paths = dashboard["figure_paths"]
    notes = visual_bundle.get("chart_notes", [])
    if figure_paths:
        st.subheader("Charts")
        for index, path in enumerate(figure_paths):
            if Path(path).exists():
                caption = notes[index] if index < len(notes) else ""
                st.image(path, caption=caption, use_container_width=True)
            else:
                st.warning(f"Missing figure: {path}")

    # Sample predictions table.
    predictions = dashboard["sample_predictions"]
    if predictions:
        st.subheader("Sample predictions")
        st.table(predictions)


if __name__ == "__main__":
    _render()
=======
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
>>>>>>> b083eca4ef8e9a95f278691d39a7a2172ae824d5
