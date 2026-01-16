"""Compute dataset statistics - runs in parallel with train_model."""

import json
import logging
from pathlib import Path

import click
import pandas as pd

from src.utils.config import load_config_with_params
from src.utils.monitoring import log_pipeline_end, log_pipeline_start, setup_monitoring

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


@click.command()
@click.argument("processed_dataset_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_path", type=click.Path(path_type=Path))
@click.option(
    "--config-path",
    default=None,
    type=click.Path(exists=False, path_type=Path),
    help="Path to Hydra/OmegaConf configuration file.",
)
def main(
    processed_dataset_path: Path,
    output_path: Path,
    config_path: Path | None,
) -> None:
    """Compute and save dataset statistics."""
    # Load configuration using Hydra compose API
    if config_path:
        config_name = config_path.stem if config_path.is_file() else "config"
        config_dir = config_path if config_path.is_dir() else config_path.parent
        params = load_config_with_params(config_dir, None, config_name)
    else:
        params = load_config_with_params(None, None)

    # Setup monitoring
    monitor = setup_monitoring(config_path)
    log_pipeline_start(monitor, "compute_statistics", params.get("data", {}))

    logger.info("Loading processed dataset from %s", processed_dataset_path)
    df = pd.read_csv(processed_dataset_path)

    # Compute statistics
    feature_columns = [col for col in df.columns if col != "target"]

    statistics = {
        "dataset": {
            "n_samples": len(df),
            "n_features": len(feature_columns),
            "feature_names": feature_columns,
        },
        "target": {
            "unique_values": df["target"].nunique(),
            "value_counts": df["target"].value_counts().to_dict(),
        },
        "features": {},
    }

    # Per-feature statistics
    for col in feature_columns:
        statistics["features"][col] = {
            "mean": float(df[col].mean()),
            "std": float(df[col].std()),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "median": float(df[col].median()),
        }

    # Correlation with target (if numeric)
    if df["target"].dtype in ["int64", "float64"]:
        correlations = {}
        for col in feature_columns:
            correlations[col] = float(df[col].corr(df["target"]))
        statistics["correlations_with_target"] = correlations

    # Save statistics
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fp:
        json.dump(statistics, fp, indent=2)

    logger.info("Saved dataset statistics to %s", output_path)

    log_pipeline_end(
        monitor,
        "compute_statistics",
        {
            "n_samples": statistics["dataset"]["n_samples"],
            "n_features": statistics["dataset"]["n_features"],
        },
    )


if __name__ == "__main__":
    main()
