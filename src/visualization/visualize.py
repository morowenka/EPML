import json
import logging
from datetime import UTC, datetime
from pathlib import Path

import click
import matplotlib.pyplot as plt
import seaborn as sns
from omegaconf import OmegaConf

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

sns.set_style("whitegrid")


def _init_clearml_task(config_path: Path | None) -> Task | None:
    """Initialize ClearML Task for visualization tracking."""
    if not CLEARML_AVAILABLE:
        logger.debug("ClearML not available, skipping ClearML integration")
        return None

    try:
        project_name = "wine-quality-mlops"
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
        task_name = f"visualize-{timestamp}"

        task = Task.init(
            project_name=project_name,
            task_name=task_name,
            task_type=Task.TaskTypes.monitor,
            auto_connect_frameworks={
                "matplotlib": True,  # Auto-connect matplotlib
            },
        )

        task.add_tags(["visualize", "monitoring", "mlops"])

        if config_path and config_path.exists():
            task.connect_configuration(config_path, name="config")

        logger.info("ClearML Task initialized for visualization: %s/%s", project_name, task_name)
        return task

    except Exception as e:
        logger.warning("Failed to initialize ClearML Task: %s", e)
        return None


@click.command()
@click.argument("metrics_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option(
    "--config-path",
    default=None,
    type=click.Path(exists=False, path_type=Path),
    help="Path to OmegaConf configuration file.",
)
def main(metrics_path: Path, output_dir: Path, config_path: Path | None) -> None:
    """Generate visualization plots from metrics."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup monitoring
    monitor = setup_monitoring(config_path)
    log_pipeline_start(monitor, "visualize")

    # Initialize ClearML Task
    clearml_task = _init_clearml_task(config_path)

    enabled = True
    if config_path and config_path.exists():
        cfg = OmegaConf.load(config_path)
        enabled = cfg.get("visualization", {}).get("enabled", True)

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

    # Log to ClearML
    if clearml_task:
        try:
            clearml_task.logger.report_image(
                title="Metrics Summary",
                series="metrics_plot",
                iteration=0,
                local_path=str(output_file),
            )
            clearml_task.logger.report_scalar(
                title="Metrics",
                series="accuracy",
                value=metrics["metrics"]["accuracy"],
                iteration=0,
            )
            clearml_task.logger.report_scalar(
                title="Metrics",
                series="f1_macro",
                value=metrics["metrics"]["f1_macro"],
                iteration=0,
            )
            clearml_task.upload_artifact(
                name="visualization",
                artifact_object=str(output_file),
            )
        except Exception as e:
            logger.warning("Failed to log to ClearML: %s", e)

    plt.close()
    logger.info("Saved visualization to %s", output_file)

    log_pipeline_end(monitor, "visualize", {"output_file": str(output_file)})

    # Close ClearML Task
    if clearml_task:
        try:
            clearml_task.close()
        except Exception as e:
            logger.warning("Failed to close ClearML Task: %s", e)


if __name__ == "__main__":
    main()
