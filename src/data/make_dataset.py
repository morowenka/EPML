import logging
from pathlib import Path

import click
import pandas as pd
from dotenv import find_dotenv, load_dotenv
from sklearn.preprocessing import StandardScaler

from src.utils.config import load_config_with_params
from src.utils.monitoring import log_pipeline_end, log_pipeline_start, setup_monitoring

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


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
    # Load configuration using Hydra compose API for proper config composition
    # This handles 'defaults:' directives and merges configs correctly
    if config_path:
        config_name = config_path.stem if config_path.is_file() else "config"
        config_dir = config_path if config_path.is_dir() else config_path.parent
        params = load_config_with_params(config_dir, params_path, config_name)
    else:
        params = load_config_with_params(None, params_path)

    # Setup monitoring
    monitor = setup_monitoring(config_path)
    log_pipeline_start(monitor, "prepare_data", params.get("data", {}))

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
    load_dotenv(find_dotenv())
    main()
