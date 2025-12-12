import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from omegaconf import OmegaConf


def setup_monitoring(config_path: Path | None = None) -> logging.Logger:
    """Setup monitoring logger based on configuration."""
    logger = logging.getLogger("pipeline_monitor")

    if config_path and config_path.exists():
        cfg = OmegaConf.load(config_path)
        monitoring_cfg = cfg.get("monitoring", {})
        enabled = monitoring_cfg.get("enabled", True)
        log_file = monitoring_cfg.get("log_file", "experiments.log")
    else:
        enabled = True
        log_file = "experiments.log"

    if not enabled:
        logger.setLevel(logging.WARNING)
        return logger

    logger.setLevel(logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # File handler
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def log_pipeline_start(
    logger: logging.Logger, stage: str, config: dict[str, Any] | None = None
) -> None:
    """Log pipeline stage start."""
    logger.info("=" * 80)
    logger.info("Pipeline stage started: %s", stage)
    logger.info("Timestamp: %s", datetime.now(tz=UTC).isoformat())
    if config:
        logger.info("Configuration: %s", config)
    logger.info("=" * 80)


def log_pipeline_end(
    logger: logging.Logger, stage: str, metrics: dict[str, Any] | None = None
) -> None:
    """Log pipeline stage completion."""
    logger.info("=" * 80)
    logger.info("Pipeline stage completed: %s", stage)
    logger.info("Timestamp: %s", datetime.now(tz=UTC).isoformat())
    if metrics:
        logger.info("Metrics: %s", metrics)
    logger.info("=" * 80)
