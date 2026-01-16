import logging
from pathlib import Path

import hydra
import pandas as pd
from omegaconf import DictConfig
from sklearn.preprocessing import StandardScaler

from src.utils.monitoring import log_pipeline_end, log_pipeline_start, setup_monitoring

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


@hydra.main(config_path="../../conf", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    """Generate the project dataset and prepare processed features."""
    # Setup monitoring
    monitor = setup_monitoring()
    log_pipeline_start(monitor, "prepare_data", dict(cfg.data))

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
