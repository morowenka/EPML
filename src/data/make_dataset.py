import logging
from pathlib import Path

import hydra
import pandas as pd
from omegaconf import DictConfig
from sklearn.preprocessing import StandardScaler

from src.utils.monitoring import log_pipeline_end, log_pipeline_start, setup_monitoring

# Optional ClearML integration
try:
    from clearml import Task

    CLEARML_AVAILABLE = True
except ImportError:
    CLEARML_AVAILABLE = False
    Task = None  # type: ignore[assignment, misc]

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


@hydra.main(config_path="../../conf", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    """Generate the project dataset and prepare processed features."""
    # Setup monitoring
    monitor = setup_monitoring()
    log_pipeline_start(monitor, "prepare_data", dict(cfg.data))

    # Initialize ClearML task (optional)
    clearml_task = None
    if CLEARML_AVAILABLE:
        try:
            clearml_cfg = cfg.train.get("clearml", {}) if "train" in cfg else {}
            project_name = clearml_cfg.get("project_name", "wine-quality-mlops")
            clearml_task = Task.init(
                project_name=project_name,
                task_name="prepare_data",
                task_type=Task.TaskTypes.data_processing,
            )
            clearml_task.add_tags(["data_processing", "prepare_data"])
            logger.info("ClearML task initialized: %s/prepare_data", project_name)
        except Exception as e:
            logger.warning("ClearML initialization failed (continuing without): %s", e)
            clearml_task = None
    else:
        logger.info("ClearML not available, running without experiment tracking")

    # Get paths from config
    raw_input_filepath = Path(cfg.paths.raw_data)
    processed_output_filepath = Path(cfg.paths.processed_data)

    # Get data params
    feature_scaling = cfg.data.feature_scaling

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

    # Log to ClearML if available
    if clearml_task:
        try:
            clearml_task.get_logger().report_scalar(
                "data", "n_samples", value=len(processed_df), iteration=0
            )
            clearml_task.get_logger().report_scalar(
                "data", "n_features", value=len(feature_columns), iteration=0
            )
            clearml_task.upload_artifact(
                "processed_dataset", artifact_object=str(processed_output_filepath)
            )
            logger.info("Data logged to ClearML")
        except Exception as e:
            logger.warning("ClearML logging failed (continuing): %s", e)

    log_pipeline_end(
        monitor,
        "prepare_data",
        {
            "n_samples": len(processed_df),
            "n_features": len(feature_columns),
            "feature_scaling": feature_scaling,
        },
    )


if __name__ == "__main__":
    main()
