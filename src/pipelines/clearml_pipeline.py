#!/usr/bin/env python3
"""ClearML Pipeline definition for ML workflow using PipelineDecorator.

This pipeline uses the function-based approach which is simpler and works
locally without needing pre-created template tasks or execution queues.
"""

import json
import logging
from pathlib import Path
from typing import Any

from clearml import PipelineDecorator, Task

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


@PipelineDecorator.component(
    return_values=["processed_data_path"],
    cache=True,
    task_type=Task.TaskTypes.data_processing,
)
def prepare_data(raw_data_path: str, processed_data_path: str, feature_scaling: bool = True) -> str:
    """Prepare data for training.

    Args:
        raw_data_path: Path to raw CSV data
        processed_data_path: Path to save processed data
        feature_scaling: Whether to apply feature scaling

    Returns:
        Path to processed data file
    """
    import pandas as pd
    from sklearn.preprocessing import StandardScaler

    logger = logging.getLogger(__name__)
    logger.info("Loading raw data from %s", raw_data_path)

    df = pd.read_csv(raw_data_path)
    logger.info("Loaded dataset with shape: %s", df.shape)

    # Rename quality column to target
    if "quality" in df.columns:
        df = df.rename(columns={"quality": "target"})

    # Drop Id column if present
    if "Id" in df.columns:
        df = df.drop(columns=["Id"])

    # Apply feature scaling if enabled
    if feature_scaling and "target" in df.columns:
        feature_cols = [c for c in df.columns if c != "target"]
        scaler = StandardScaler()
        df[feature_cols] = scaler.fit_transform(df[feature_cols])
        logger.info("Applied StandardScaler to %d features", len(feature_cols))

    # Save processed data
    output_path = Path(processed_data_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Saved processed data to %s", output_path)

    # Log to ClearML
    task = Task.current_task()
    if task:
        task.upload_artifact("processed_dataset", artifact_object=str(output_path))
        task.get_logger().report_scalar("data", "n_samples", value=len(df), iteration=0)
        task.get_logger().report_scalar("data", "n_features", value=df.shape[1] - 1, iteration=0)

    return str(output_path)


@PipelineDecorator.component(
    return_values=["model_path", "metrics"],
    cache=True,
    task_type=Task.TaskTypes.training,
)
def train_model(
    processed_data_path: str,
    model_output_path: str,
    metrics_output_path: str,
    model_type: str = "logistic_regression",
    random_state: int = 13,
    test_size: float = 0.2,
    model_params: dict[str, Any] | None = None,
) -> tuple[str, dict[str, float]]:
    """Train a classification model.

    Args:
        processed_data_path: Path to processed data
        model_output_path: Path to save trained model
        metrics_output_path: Path to save metrics
        model_type: Type of model (logistic_regression, random_forest, svm)
        random_state: Random seed for reproducibility
        test_size: Fraction of data for testing
        model_params: Additional model parameters

    Returns:
        Tuple of (model_path, metrics_dict)
    """
    from datetime import UTC, datetime

    import joblib
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, f1_score
    from sklearn.model_selection import train_test_split
    from sklearn.svm import SVC

    logger = logging.getLogger(__name__)
    model_params = model_params or {}

    logger.info("Loading processed data from %s", processed_data_path)
    df = pd.read_csv(processed_data_path)

    X = df.drop(columns=["target"])
    y = df["target"]

    logger.info("Splitting data: test_size=%s, random_state=%s", test_size, random_state)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Build model based on type
    if model_type == "logistic_regression":
        default_params = {"max_iter": 500, "random_state": random_state}
        model = LogisticRegression(**{**default_params, **model_params})
    elif model_type == "random_forest":
        default_params = {"n_estimators": 100, "random_state": random_state}
        model = RandomForestClassifier(**{**default_params, **model_params})
    elif model_type == "svm":
        default_params = {"C": 1.0, "kernel": "rbf", "random_state": random_state}
        model = SVC(**{**default_params, **model_params})
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    logger.info("Training %s model", model.__class__.__name__)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average="macro")

    metrics = {"accuracy": accuracy, "f1_macro": f1_macro}
    logger.info("Metrics: accuracy=%.4f, f1_macro=%.4f", accuracy, f1_macro)

    # Save model
    model_path = Path(model_output_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    logger.info("Saved model to %s", model_path)

    # Save metrics
    metrics_path = Path(metrics_output_path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    full_metrics = {
        "timestamp_utc": datetime.now(tz=UTC).isoformat(),
        "model": {"type": model.__class__.__name__, "params": model.get_params()},
        "data": {"n_samples": len(df), "n_features": X.shape[1], "test_size": test_size},
        "metrics": metrics,
    }
    with open(metrics_path, "w") as f:
        json.dump(full_metrics, f, indent=2)
    logger.info("Saved metrics to %s", metrics_path)

    # Log to ClearML
    task = Task.current_task()
    if task:
        task.get_logger().report_scalar("metrics", "accuracy", value=accuracy, iteration=0)
        task.get_logger().report_scalar("metrics", "f1_macro", value=f1_macro, iteration=0)
        task.upload_artifact("model", artifact_object=str(model_path))
        task.upload_artifact("metrics", artifact_object=str(metrics_path))

        # Register model
        from clearml import OutputModel

        output_model = OutputModel(task=task, name=f"wine-quality-{model_type}")
        output_model.update_weights(weights_filename=str(model_path))
        # Note: update_labels expects integer values for label enumeration
        # Use task metadata for string values instead
        task.set_parameter("model/type", model_type)
        task.set_parameter("model/accuracy", accuracy)

    return str(model_path), metrics


@PipelineDecorator.component(
    return_values=["figure_path"],
    cache=True,
    task_type=Task.TaskTypes.monitor,
)
def visualize_results(metrics_path: str, figures_dir: str) -> str:
    """Create visualizations from metrics.

    Args:
        metrics_path: Path to metrics JSON file
        figures_dir: Directory to save figures

    Returns:
        Path to generated figure
    """
    from pathlib import Path

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    logger = logging.getLogger(__name__)
    logger.info("Loading metrics from %s", metrics_path)

    with open(metrics_path) as f:
        data = json.load(f)

    metrics = data.get("metrics", {})
    accuracy = metrics.get("accuracy", 0)
    f1_macro = metrics.get("f1_macro", 0)

    # Create bar chart
    fig, ax = plt.subplots(figsize=(8, 6))
    metric_names = ["Accuracy", "F1 Macro"]
    metric_values = [accuracy, f1_macro]
    colors = ["#2ecc71", "#3498db"]

    bars = ax.bar(metric_names, metric_values, color=colors, edgecolor="black")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Model Performance Metrics")

    # Add value labels on bars
    for bar, val in zip(bars, metric_values, strict=False):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, f"{val:.4f}", ha="center"
        )

    # Save figure
    output_dir = Path(figures_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_path = output_dir / "metrics_summary.png"
    plt.tight_layout()
    plt.savefig(figure_path, dpi=150)
    plt.close()
    logger.info("Saved figure to %s", figure_path)

    # Log to ClearML
    task = Task.current_task()
    if task:
        task.get_logger().report_image(
            "Metrics Summary", "Performance", local_path=str(figure_path)
        )
        task.upload_artifact("metrics_figure", artifact_object=str(figure_path))

    return str(figure_path)


@PipelineDecorator.pipeline(
    name="wine-quality-pipeline",
    project="wine-quality-mlops",
    version="1.0.0",
)
def run_pipeline(
    raw_data_path: str = "data/raw/WineQT.csv",
    processed_data_path: str = "data/processed/wine_processed.csv",
    model_output_path: str = "models/model.pkl",
    metrics_output_path: str = "reports/metrics.json",
    figures_dir: str = "reports/figures",
    feature_scaling: bool = True,
    model_type: str = "logistic_regression",
    random_state: int = 13,
    test_size: float = 0.2,
) -> dict[str, Any]:
    """Run the full ML pipeline.

    Args:
        raw_data_path: Path to raw data
        processed_data_path: Path for processed data
        model_output_path: Path for trained model
        metrics_output_path: Path for metrics JSON
        figures_dir: Directory for figures
        feature_scaling: Whether to scale features
        model_type: Type of model to train
        random_state: Random seed
        test_size: Test set fraction

    Returns:
        Dictionary with pipeline outputs
    """
    # Step 1: Prepare data
    processed_path = prepare_data(
        raw_data_path=raw_data_path,
        processed_data_path=processed_data_path,
        feature_scaling=feature_scaling,
    )

    # Step 2: Train model
    model_path, metrics = train_model(
        processed_data_path=processed_path,
        model_output_path=model_output_path,
        metrics_output_path=metrics_output_path,
        model_type=model_type,
        random_state=random_state,
        test_size=test_size,
    )

    # Step 3: Visualize
    figure_path = visualize_results(
        metrics_path=metrics_output_path,
        figures_dir=figures_dir,
    )

    return {
        "processed_data_path": processed_path,
        "model_path": model_path,
        "metrics": metrics,
        "figure_path": figure_path,
    }


def main():
    """Main entry point for running the pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Run ClearML ML pipeline")
    parser.add_argument("--raw-data", default="data/raw/WineQT.csv", help="Path to raw data")
    parser.add_argument(
        "--processed-data",
        default="data/processed/wine_processed.csv",
        help="Path for processed data",
    )
    parser.add_argument("--model-output", default="models/model.pkl", help="Path for model")
    parser.add_argument("--metrics-output", default="reports/metrics.json", help="Path for metrics")
    parser.add_argument("--figures-dir", default="reports/figures", help="Directory for figures")
    parser.add_argument("--no-scaling", action="store_true", help="Disable feature scaling")
    parser.add_argument(
        "--model-type",
        default="logistic_regression",
        choices=["logistic_regression", "random_forest", "svm"],
        help="Model type",
    )
    parser.add_argument("--random-state", type=int, default=13, help="Random seed")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set fraction")
    parser.add_argument(
        "--local",
        action="store_true",
        default=True,
        help="Run pipeline locally (default: True)",
    )

    args = parser.parse_args()

    # Set local execution mode
    if args.local:
        PipelineDecorator.run_locally()
        logger.info("Running pipeline locally")

    # Run pipeline
    logger.info("Starting wine-quality-pipeline")
    result = run_pipeline(
        raw_data_path=args.raw_data,
        processed_data_path=args.processed_data,
        model_output_path=args.model_output,
        metrics_output_path=args.metrics_output,
        figures_dir=args.figures_dir,
        feature_scaling=not args.no_scaling,
        model_type=args.model_type,
        random_state=args.random_state,
        test_size=args.test_size,
    )

    logger.info("Pipeline completed!")
    logger.info("Results: %s", result)
    return result


if __name__ == "__main__":
    main()
