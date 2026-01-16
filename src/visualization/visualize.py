import json
import logging
from pathlib import Path

import hydra
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from omegaconf import DictConfig

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

sns.set_style("whitegrid")


@hydra.main(config_path="../../conf", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    """Generate visualization plots from metrics."""
    # Setup monitoring
    monitor = setup_monitoring()
    log_pipeline_start(monitor, "visualize")

    # Initialize ClearML task (optional)
    clearml_task = None
    if CLEARML_AVAILABLE:
        try:
            clearml_cfg = cfg.train.get("clearml", {}) if "train" in cfg else {}
            project_name = clearml_cfg.get("project_name", "wine-quality-mlops")
            clearml_task = Task.init(
                project_name=project_name,
                task_name="visualize",
                task_type=Task.TaskTypes.monitor,
            )
            clearml_task.add_tags(["visualization", "metrics"])
            logger.info("ClearML task initialized: %s/visualize", project_name)
        except Exception as e:
            logger.warning("ClearML initialization failed (continuing without): %s", e)
            clearml_task = None
    else:
        logger.info("ClearML not available, running without experiment tracking")

    # Get paths from config
    metrics_path = Path(cfg.paths.metrics)
    output_dir = Path(cfg.paths.figures)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if visualization enabled
    enabled = cfg.visualization.enabled

    if not enabled:
        logger.info("Visualization disabled in configuration")
        log_pipeline_end(monitor, "visualize", {"status": "disabled"})
        return

    logger.info("Loading metrics from %s", metrics_path)
    with metrics_path.open("r", encoding="utf-8") as fp:
        metrics = json.load(fp)

    # Create metrics summary plot
    fig, ax = plt.subplots(figsize=(8, 6))
    metric_values = {
        "Accuracy": metrics["metrics"]["accuracy"],
        "F1 Macro": metrics["metrics"]["f1_macro"],
    }
    ax.bar(metric_values.keys(), metric_values.values(), color=["#2ecc71", "#3498db"])
    ax.set_ylabel("Score")
    ax.set_title("Model Performance Metrics")
    ax.set_ylim(0, 1)
    for i, (_k, v) in enumerate(metric_values.items()):
        ax.text(i, v + 0.02, f"{v:.3f}", ha="center", va="bottom")

    output_file = output_dir / "metrics_summary.png"
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("Saved visualization to %s", output_file)

    # Log to ClearML if available
    if clearml_task:
        try:
            clearml_task.get_logger().report_image(
                "Metrics Summary", "Performance", local_path=str(output_file)
            )
            clearml_task.get_logger().report_scalar(
                "metrics", "accuracy", value=metric_values["Accuracy"], iteration=0
            )
            clearml_task.get_logger().report_scalar(
                "metrics", "f1_macro", value=metric_values["F1 Macro"], iteration=0
            )
            clearml_task.upload_artifact("metrics_figure", artifact_object=str(output_file))
            logger.info("Visualization logged to ClearML")
        except Exception as e:
            logger.warning("ClearML logging failed (continuing): %s", e)

    log_pipeline_end(monitor, "visualize", {"output_file": str(output_file)})


if __name__ == "__main__":
    main()
