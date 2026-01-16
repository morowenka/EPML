"""Compute dataset statistics - runs in parallel with train_model."""

import json
import logging
from pathlib import Path

import hydra
import pandas as pd
from omegaconf import DictConfig

from src.utils.monitoring import log_pipeline_end, log_pipeline_start, setup_monitoring

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


@hydra.main(config_path="../../conf", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    """Compute and save dataset statistics."""
    # Setup monitoring
    monitor = setup_monitoring()
    log_pipeline_start(monitor, "compute_statistics", dict(cfg.data))

    # Get paths from config
    processed_dataset_path = Path(cfg.paths.processed_data)
    output_path = Path(cfg.paths.statistics)

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
