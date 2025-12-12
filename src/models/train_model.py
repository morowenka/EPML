import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import click
import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from omegaconf import OmegaConf
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from src.utils.monitoring import log_pipeline_end, log_pipeline_start, setup_monitoring

# ClearML integration (optional, fails gracefully if not configured)
try:
    from clearml import OutputModel, Task

    CLEARML_AVAILABLE = True
except ImportError:
    CLEARML_AVAILABLE = False
    Task = None
    OutputModel = None

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


def _load_params(params_path: Path) -> dict[str, Any]:
    if not params_path.exists():
        logger.warning("Params file %s not found. Using defaults.", params_path)
        return {}

    # Try OmegaConf first (YAML), fallback to JSON
    if params_path.suffix in (".yaml", ".yml"):
        cfg = OmegaConf.load(params_path)
        return OmegaConf.to_container(cfg, resolve=True)

    with params_path.open("r", encoding="utf-8") as fp:
        return cast(dict[str, Any], json.load(fp))


def _build_model(model_params: dict[str, Any]):
    model_type = model_params.get("type", "logistic_regression")

    if model_type == "logistic_regression":
        default_config: dict[str, Any] = {"max_iter": 500}
        user_config = model_params.get("logistic_regression", {})
        config = {**default_config, **user_config}
        return LogisticRegression(**config)
    elif model_type == "random_forest":
        default_config: dict[str, Any] = {"n_estimators": 100, "random_state": 13}
        user_config = model_params.get("random_forest", {})
        config = {**default_config, **user_config}
        return RandomForestClassifier(**config)
    elif model_type == "svm":
        default_config: dict[str, Any] = {"C": 1.0, "kernel": "rbf", "random_state": 13}
        user_config = model_params.get("svm", {})
        config = {**default_config, **user_config}
        return SVC(**config)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def _prepare_mlflow(train_params: dict[str, Any]) -> tuple[str, str]:
    mlflow_params: dict[str, Any] = train_params.get("mlflow", {})
    tracking_uri = mlflow_params.get("tracking_uri")
    tracking_dir = Path(mlflow_params.get("tracking_dir", "mlruns"))
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    else:
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(tracking_dir.resolve().as_uri())

    experiment_name = mlflow_params.get("experiment_name", "wine-quality")
    mlflow.set_experiment(experiment_name)

    timestamp = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
    run_name_prefix = mlflow_params.get("run_name_prefix")
    run_name = mlflow_params.get("run_name")
    if not run_name:
        run_name = f"{run_name_prefix}-{timestamp}" if run_name_prefix else f"run-{timestamp}"

    return experiment_name, run_name


def _log_model_params(model) -> dict[str, Any]:
    prepared: dict[str, Any] = {}
    for key, value in model.get_params().items():
        param_key = f"model__{key}"
        if isinstance(value, str | int | float | bool):
            prepared[param_key] = value
        elif value is None:
            prepared[param_key] = "None"
        else:
            prepared[param_key] = str(value)
    return prepared


def _init_clearml_task(
    train_params: dict[str, Any],
    model_type: str,
    config_path: Path | None,
) -> Task | None:
    """Initialize ClearML Task for experiment tracking."""
    if not CLEARML_AVAILABLE:
        logger.debug("ClearML not available, skipping ClearML integration")
        return None

    try:
        clearml_params = train_params.get("clearml", {})
        project_name = clearml_params.get("project_name", "wine-quality-mlops")
        task_name = clearml_params.get("task_name")

        if not task_name:
            timestamp = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
            task_name = f"{model_type}-{timestamp}"

        # Initialize ClearML Task
        task = Task.init(
            project_name=project_name,
            task_name=task_name,
            auto_connect_frameworks={
                "matplotlib": False,  # We'll log manually
                "tensorboard": False,
                "pytorch": False,
                "xgboost": False,
                "scikit": True,  # Auto-connect scikit-learn
            },
            auto_connect_streams=True,
        )

        # Add tags
        task.add_tags(["train_model", model_type, "mlops"])

        # Connect configuration
        if config_path and config_path.exists():
            task.connect_configuration(config_path, name="config")
        else:
            # Connect parameters from dict
            task.connect(train_params)

        logger.info("ClearML Task initialized: %s/%s", project_name, task_name)
        return task

    except Exception as e:
        logger.warning("Failed to initialize ClearML Task: %s", e)
        return None


@click.command()
@click.argument("processed_dataset_path", type=click.Path(exists=True, path_type=Path))
@click.argument("model_output_path", type=click.Path(path_type=Path))
@click.argument("metrics_output_path", type=click.Path(path_type=Path))
@click.option(
    "--params-path",
    default="params.json",
    show_default=True,
    type=click.Path(exists=False, path_type=Path),
    help="Path to the parameters file (JSON or YAML) that controls the training procedure.",
)
@click.option(
    "--config-path",
    default=None,
    show_default=True,
    type=click.Path(exists=False, path_type=Path),
    help="Path to OmegaConf configuration file (YAML). Overrides --params-path if provided.",
)
def main(
    processed_dataset_path: Path,
    model_output_path: Path,
    metrics_output_path: Path,
    params_path: Path,
    config_path: Path | None,
) -> None:
    """Train a simple classification model and persist it."""
    # Use OmegaConf config if provided, otherwise fallback to params_path
    if config_path and config_path.exists():
        cfg = OmegaConf.load(config_path)
        params = OmegaConf.to_container(cfg, resolve=True)
        logger.info("Loaded configuration from %s", config_path)
    else:
        params = _load_params(params_path)

    # Setup monitoring
    monitor = setup_monitoring(config_path)
    log_pipeline_start(
        monitor,
        "train_model",
        {"model_type": params.get("train", {}).get("model", {}).get("type", "unknown")},
    )

    train_params = params.get("train", {})

    random_state = train_params.get("random_state", 13)
    test_size = train_params.get("test_size", 0.2)
    model_params = train_params.get("model", {})

    logger.info("Loading processed dataset from %s", processed_dataset_path)
    df = pd.read_csv(processed_dataset_path)

    if "target" not in df.columns:
        msg = "Processed dataset must contain a 'target' column."
        raise ValueError(msg)

    X = df.drop(columns=["target"])
    y = df["target"]

    logger.info("Splitting dataset: test_size=%s, random_state=%s", test_size, random_state)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    model = _build_model(model_params)
    experiment_name, run_name = _prepare_mlflow(train_params)

    # Initialize ClearML Task
    clearml_task = _init_clearml_task(
        train_params,
        model_params.get("type", "unknown"),
        config_path,
    )

    logger.info("Training %s", model.__class__.__name__)
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.set_tag("stage", "train_model")
        mlflow.log_params({
            "random_state": random_state,
            "test_size": test_size,
            "n_features": X.shape[1],
            "n_samples": len(df),
            "experiment_name": experiment_name,
        })
        mlflow.log_params(_log_model_params(model))

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1_macro = f1_score(y_test, y_pred, average="macro")

        mlflow.log_metrics({"accuracy": accuracy, "f1_macro": f1_macro})

        # Log metrics to ClearML
        if clearml_task:
            try:
                clearml_task.logger.report_scalar(
                    title="Metrics",
                    series="accuracy",
                    value=accuracy,
                    iteration=0,
                )
                clearml_task.logger.report_scalar(
                    title="Metrics",
                    series="f1_macro",
                    value=f1_macro,
                    iteration=0,
                )
                # Log hyperparameters
                clearml_task.logger.report_scalar(
                    title="Data",
                    series="n_samples",
                    value=len(df),
                    iteration=0,
                )
                clearml_task.logger.report_scalar(
                    title="Data",
                    series="n_features",
                    value=X.shape[1],
                    iteration=0,
                )
            except Exception as e:
                logger.warning("Failed to log metrics to ClearML: %s", e)

        model_output_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Persisting trained model to %s", model_output_path)
        joblib.dump(model, model_output_path)

        mlflow.log_artifact(str(model_output_path))
        model_info = mlflow.sklearn.log_model(model, artifact_path="model")

        # Register model in Model Registry
        mlflow_params = train_params.get("mlflow", {})
        model_name = mlflow_params.get("model_name", "wine-quality-model")
        logger.info("Registering model '%s' in Model Registry", model_name)
        mlflow.register_model(model_info.model_uri, model_name)

        # Register model in ClearML
        if clearml_task:
            try:
                clearml_model = OutputModel(task=clearml_task, name=model_name)
                clearml_model.update_weights(weights_filename=str(model_output_path))
                clearml_model.update_metadata(
                    metadata={
                        "model_type": model.__class__.__name__,
                        "accuracy": accuracy,
                        "f1_macro": f1_macro,
                        "n_samples": len(df),
                        "n_features": X.shape[1],
                        "timestamp": datetime.now(tz=UTC).isoformat(),
                    }
                )
                clearml_model.set_tags(["production", model_params.get("type", "unknown")])
                logger.info("Model registered in ClearML Model Registry")
            except Exception as e:
                logger.warning("Failed to register model in ClearML: %s", e)

        metadata = {
            "timestamp_utc": datetime.now(tz=UTC).isoformat(),
            "mlflow": {
                "tracking_uri": mlflow.get_tracking_uri(),
                "experiment_id": run.info.experiment_id,
                "run_id": run.info.run_id,
                "run_name": run.info.run_name,
            },
            "model": {
                "type": model.__class__.__name__,
                "params": model.get_params(),
            },
            "data": {
                "n_samples": len(df),
                "n_features": X.shape[1],
                "test_size": test_size,
            },
            "metrics": {
                "accuracy": accuracy,
                "f1_macro": f1_macro,
            },
        }

        logger.info("Writing metrics and metadata to %s", metrics_output_path)
        with metrics_output_path.open("w", encoding="utf-8") as fp:
            json.dump(metadata, fp, indent=2)

        mlflow.log_artifact(str(metrics_output_path))

        # Log artifacts to ClearML
        if clearml_task:
            try:
                clearml_task.upload_artifact(
                    name="metrics", artifact_object=str(metrics_output_path)
                )
                clearml_task.upload_artifact(name="model", artifact_object=str(model_output_path))
            except Exception as e:
                logger.warning("Failed to upload artifacts to ClearML: %s", e)

        # Log pipeline completion
        log_pipeline_end(monitor, "train_model", {"accuracy": accuracy, "f1_macro": f1_macro})

        # Close ClearML Task
        if clearml_task:
            try:
                clearml_task.close()
            except Exception as e:
                logger.warning("Failed to close ClearML Task: %s", e)


if __name__ == "__main__":
    main()
