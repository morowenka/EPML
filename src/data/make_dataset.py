import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import click
import pandas as pd
from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf
from sklearn.preprocessing import StandardScaler

from src.utils.monitoring import log_pipeline_end, log_pipeline_start, setup_monitoring

# ClearML integration (optional, fails gracefully if not configured)
try:
    from clearml import Task

    CLEARML_AVAILABLE = True
except ImportError:
    CLEARML_AVAILABLE = False
    Task = None

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


def _init_clearml_task(params: dict[str, Any], config_path: Path | None) -> Task | None:
    """Initialize ClearML Task for data preparation tracking."""
    if not CLEARML_AVAILABLE:
        logger.debug("ClearML not available, skipping ClearML integration")
        return None

    try:
        clearml_params = params.get("clearml", {})
        project_name = clearml_params.get("project_name", "wine-quality-mlops")
        task_name = clearml_params.get("data_task_name")

        if not task_name:
            timestamp = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
            task_name = f"prepare-data-{timestamp}"

        task = Task.init(
            project_name=project_name,
            task_name=task_name,
            task_type=Task.TaskTypes.data_processing,
            auto_connect_frameworks=False,
        )

        task.add_tags(["prepare_data", "data_processing", "mlops"])

        if config_path and config_path.exists():
            task.connect_configuration(config_path, name="config")
        else:
            task.connect(params.get("data", {}))

        logger.info("ClearML Task initialized for data preparation: %s/%s", project_name, task_name)
        return task

    except Exception as e:
        logger.warning("Failed to initialize ClearML Task: %s", e)
        return None


@click.command()
@click.argument("raw_input_filepath", type=click.Path(exists=True, path_type=Path))
@click.argument("processed_output_filepath", type=click.Path(path_type=Path))
@click.option(
    "--params-path",
    default="params.json",
    show_default=True,
    type=click.Path(exists=False, path_type=Path),
    help="Path to the parameters file (JSON or YAML) that controls dataset generation.",
)
@click.option(
    "--config-path",
    default=None,
    show_default=True,
    type=click.Path(exists=False, path_type=Path),
    help="Path to OmegaConf configuration file (YAML). Overrides --params-path if provided.",
)
def main(
    raw_input_filepath: Path,
    processed_output_filepath: Path,
    params_path: Path,
    config_path: Path | None,
) -> None:
    """Generate the project dataset and prepare processed features."""
    # Use OmegaConf config if provided, otherwise fallback to params_path
    if config_path and config_path.exists():
        cfg = OmegaConf.load(config_path)
        params = OmegaConf.to_container(cfg, resolve=True)
        logger.info("Loaded configuration from %s", config_path)
    else:
        params = _load_params(params_path)

    # Setup monitoring
    monitor = setup_monitoring(config_path)
    log_pipeline_start(monitor, "prepare_data", params.get("data", {}))

    # Initialize ClearML Task
    clearml_task = _init_clearml_task(params, config_path)

    data_params = params.get("data", {})
    feature_scaling = data_params.get("feature_scaling", True)

    logger.info("Loading raw dataset from %s", raw_input_filepath)
    df = pd.read_csv(raw_input_filepath)

    # Rename 'quality' to 'target' if exists, and drop 'Id' column if exists
    if "quality" in df.columns:
        df = df.rename(columns={"quality": "target"})
    if "Id" in df.columns:
        df = df.drop(columns=["Id"])

    processed_df = df.copy()
    feature_columns = [col for col in processed_df.columns if col != "target"]

    if feature_scaling:
        logger.info("Applying standard scaling to numerical features.")
        scaler = StandardScaler()
        processed_df[feature_columns] = scaler.fit_transform(processed_df[feature_columns])
    else:
        logger.info("Skipping feature scaling as per configuration.")

    logger.info("Writing processed dataset to %s", processed_output_filepath)
    processed_output_filepath.parent.mkdir(parents=True, exist_ok=True)
    processed_df.to_csv(processed_output_filepath, index=False)

    # Log to ClearML
    if clearml_task:
        try:
            clearml_task.logger.report_scalar(
                title="Data Statistics",
                series="n_samples",
                value=len(processed_df),
                iteration=0,
            )
            clearml_task.logger.report_scalar(
                title="Data Statistics",
                series="n_features",
                value=len(feature_columns),
                iteration=0,
            )
            clearml_task.upload_artifact(
                name="processed_dataset",
                artifact_object=str(processed_output_filepath),
            )
        except Exception as e:
            logger.warning("Failed to log to ClearML: %s", e)

    log_pipeline_end(
        monitor,
        "prepare_data",
        {
            "n_samples": len(processed_df),
            "n_features": len(feature_columns),
            "feature_scaling": feature_scaling,
        },
    )

    # Close ClearML Task
    if clearml_task:
        try:
            clearml_task.close()
        except Exception as e:
            logger.warning("Failed to close ClearML Task: %s", e)


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    main()
