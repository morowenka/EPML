"""
Модуль обучения моделей (Model Training).

Этот модуль реализует обучение моделей машинного обучения
на датасете Wine Quality с интеграцией MLflow и ClearML.

Поддерживаемые модели
---------------------

- **LogisticRegression** - Логистическая регрессия
- **RandomForestClassifier** - Случайный лес
- **SVC** - Метод опорных векторов

Использование
-------------

Запуск через Hydra::

    uv run python src/models/train_model.py

Запуск через DVC pipeline::

    dvc repro train_model

Параметры конфигурации (conf/config.yaml)::

    train:
      random_state: 42
      test_size: 0.2
      model:
        type: random_forest  # или logistic_regression, svm
        random_forest:
          n_estimators: 100
          max_depth: 10

Результаты
----------

После обучения создаются следующие артефакты:

- ``models/model.pkl`` - Обученная модель (joblib)
- ``reports/metrics.json`` - Метрики и метаданные

Метрики логируются в MLflow и опционально в ClearML.
"""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import hydra
import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from omegaconf import DictConfig
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from src.utils.monitoring import log_pipeline_end, log_pipeline_start, setup_monitoring

# Optional ClearML integration
try:
    from clearml import OutputModel, Task

    CLEARML_AVAILABLE = True
except ImportError:
    CLEARML_AVAILABLE = False
    Task = None  # type: ignore[assignment, misc]
    OutputModel = None  # type: ignore[assignment, misc]

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


def _build_model(model_params: dict[str, Any]):
    model_type = model_params.get("type", "logistic_regression")

    if model_type == "logistic_regression":
        default_config: dict[str, Any] = {"max_iter": 500}
        user_config = model_params.get("logistic_regression", {})
        config = {**default_config, **user_config}
        return LogisticRegression(**config)
    elif model_type == "random_forest":
        default_config = {"n_estimators": 100, "random_state": 13}
        user_config = model_params.get("random_forest", {})
        config = {**default_config, **user_config}
        return RandomForestClassifier(**config)
    elif model_type == "svm":
        default_config = {"C": 1.0, "kernel": "rbf", "random_state": 13}
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


@hydra.main(config_path="../../conf", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    """Train a simple classification model and persist it."""
    # Setup monitoring
    monitor = setup_monitoring()
    log_pipeline_start(
        monitor,
        "train_model",
        {"model_type": cfg.train.model.type},
    )

    # Initialize ClearML task (optional)
    clearml_task = None
    if CLEARML_AVAILABLE:
        try:
            clearml_cfg = cfg.train.get("clearml", {})
            project_name = clearml_cfg.get("project_name", "wine-quality-mlops")
            task_name = clearml_cfg.get("task_name") or f"train_{cfg.train.model.type}"
            clearml_task = Task.init(
                project_name=project_name,
                task_name=task_name,
                task_type=Task.TaskTypes.training,
                auto_connect_frameworks={"scikit-learn": True},
            )
            clearml_task.add_tags([cfg.train.model.type, "train_model"])
            logger.info("ClearML task initialized: %s/%s", project_name, task_name)
        except Exception as e:
            logger.warning("ClearML initialization failed (continuing without): %s", e)
            clearml_task = None
    else:
        logger.info("ClearML not available, using MLflow only")

    # Get paths from config
    processed_dataset_path = Path(cfg.paths.processed_data)
    model_output_path = Path(cfg.paths.model)
    metrics_output_path = Path(cfg.paths.metrics)

    # Get train params
    train_params = dict(cfg.train)
    random_state = cfg.train.random_state
    test_size = cfg.train.test_size
    model_params = dict(cfg.train.model)

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

        # Log to ClearML if available
        if clearml_task:
            try:
                clearml_task.get_logger().report_scalar(
                    "metrics", "accuracy", value=accuracy, iteration=0
                )
                clearml_task.get_logger().report_scalar(
                    "metrics", "f1_macro", value=f1_macro, iteration=0
                )
                clearml_task.upload_artifact("model", artifact_object=str(model_output_path))
                clearml_task.upload_artifact("metrics", artifact_object=str(metrics_output_path))

                # Register model in ClearML
                clearml_model = OutputModel(task=clearml_task, name=model_name)
                clearml_model.update_weights(weights_filename=str(model_output_path))
                # Note: update_labels expects integer values for label enumeration
                # Use task metadata for string values instead
                clearml_task.set_parameter("model/type", model.__class__.__name__)
                clearml_task.set_parameter("model/accuracy", accuracy)
                clearml_task.set_parameter("model/f1_macro", f1_macro)
                logger.info("Model registered in ClearML: %s", model_name)
            except Exception as e:
                logger.warning("ClearML logging failed (continuing): %s", e)

        # Log pipeline completion
        log_pipeline_end(monitor, "train_model", {"accuracy": accuracy, "f1_macro": f1_macro})


if __name__ == "__main__":
    main()
