#!/usr/bin/env python3
"""ClearML Pipeline definition for ML workflow."""

import logging
from pathlib import Path

from clearml import PipelineController, Task

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


def create_pipeline(
    project_name: str = "wine-quality-mlops",
    pipeline_name: str = "wine-quality-pipeline",
    config_path: str | Path = "conf/config.yaml",
    use_dvc: bool = True,
) -> PipelineController:
    """Create and configure ClearML pipeline."""
    # Initialize pipeline
    pipe = PipelineController(
        name=pipeline_name,
        project=project_name,
        version="1.0.0",
        add_pipeline_tags=["mlops", "wine-quality"],
    )

    if use_dvc:
        # Use DVC integration: each step runs DVC repro for that stage
        # Step 1: Prepare data (DVC stage)
        pipe.add_step(
            name="prepare_data",
            base_task_project=project_name,
            base_task_name="dvc_prepare_data_template",
            parameter_override={
                "General/dvc_stage": "prepare_data",
                "General/config_path": str(config_path),
            },
            cache_executed_step=True,
            execution_queue=None,  # Run locally
        )

        # Step 2: Train model (DVC stage)
        pipe.add_step(
            name="train_model",
            base_task_project=project_name,
            base_task_name="dvc_train_model_template",
            parents=["prepare_data"],
            parameter_override={
                "General/dvc_stage": "train_model",
                "General/config_path": str(config_path),
            },
            cache_executed_step=True,
            execution_queue=None,  # Run locally
        )

        # Step 3: Visualize (DVC stage)
        pipe.add_step(
            name="visualize",
            base_task_project=project_name,
            base_task_name="dvc_visualize_template",
            parents=["train_model"],
            parameter_override={
                "General/dvc_stage": "visualize",
                "General/config_path": str(config_path),
            },
            cache_executed_step=True,
            execution_queue=None,  # Run locally
        )
    else:
        # Direct Python script execution
        # Step 1: Prepare data
        pipe.add_step(
            name="prepare_data",
            base_task_project=project_name,
            base_task_name="prepare_data_template",
            parameter_override={
                "General/dataset_path": "data/raw/WineQT.csv",
                "General/output_path": "data/processed/wine_processed.csv",
                "General/config_path": str(config_path),
            },
            cache_executed_step=True,
        )

        # Step 2: Train model
        pipe.add_step(
            name="train_model",
            base_task_project=project_name,
            base_task_name="train_model_template",
            parents=["prepare_data"],
            parameter_override={
                "General/processed_dataset_path": "${prepare_data.artifacts.dataset}",
                "General/model_output_path": "models/model.pkl",
                "General/metrics_output_path": "reports/metrics.json",
                "General/config_path": str(config_path),
            },
            cache_executed_step=True,
        )

        # Step 3: Visualize
        pipe.add_step(
            name="visualize",
            base_task_project=project_name,
            base_task_name="visualize_template",
            parents=["train_model"],
            parameter_override={
                "General/metrics_path": "${train_model.artifacts.metrics}",
                "General/output_dir": "reports/figures",
                "General/config_path": str(config_path),
            },
            cache_executed_step=True,
        )

    return pipe


def create_template_tasks(project_name: str = "wine-quality-mlops", use_dvc: bool = True):
    """Create template tasks for pipeline steps."""
    project_root = Path(__file__).parent.parent.parent

    if use_dvc:
        # DVC-based templates
        # Template for DVC prepare_data
        script_path = project_root / "scripts" / "run_dvc_stage.py"
        dvc_prepare_task = Task.create(
            project_name=project_name,
            task_name="dvc_prepare_data_template",
            task_type=Task.TaskTypes.data_processing,
            script=str(script_path),
            repo=".",
        )
        dvc_prepare_task.set_parameter("General/dvc_stage", "prepare_data")
        dvc_prepare_task.set_parameter("General/config_path", "conf/config.yaml")
        dvc_prepare_task.add_tags(["template", "dvc", "prepare_data"])
        dvc_prepare_task.close()
        logger.info("Created template task: dvc_prepare_data_template")

        # Template for DVC train_model
        dvc_train_task = Task.create(
            project_name=project_name,
            task_name="dvc_train_model_template",
            task_type=Task.TaskTypes.training,
            script=str(script_path),
            repo=".",
        )
        dvc_train_task.set_parameter("General/dvc_stage", "train_model")
        dvc_train_task.set_parameter("General/config_path", "conf/config.yaml")
        dvc_train_task.add_tags(["template", "dvc", "train_model"])
        dvc_train_task.close()
        logger.info("Created template task: dvc_train_model_template")

        # Template for DVC visualize
        dvc_visualize_task = Task.create(
            project_name=project_name,
            task_name="dvc_visualize_template",
            task_type=Task.TaskTypes.monitor,
            script=str(script_path),
            repo=".",
        )
        dvc_visualize_task.set_parameter("General/dvc_stage", "visualize")
        dvc_visualize_task.set_parameter("General/config_path", "conf/config.yaml")
        dvc_visualize_task.add_tags(["template", "dvc", "visualize"])
        dvc_visualize_task.close()
        logger.info("Created template task: dvc_visualize_template")
    else:
        # Direct Python script templates
        # Template for prepare_data
        prepare_script_path = project_root / "src" / "data" / "make_dataset.py"
        prepare_task = Task.create(
            project_name=project_name,
            task_name="prepare_data_template",
            task_type=Task.TaskTypes.data_processing,
            script=str(prepare_script_path),
            repo=".",
        )
        prepare_task.set_parameter("General/dataset_path", "data/raw/WineQT.csv")
        prepare_task.set_parameter("General/output_path", "data/processed/wine_processed.csv")
        prepare_task.set_parameter("General/config_path", "conf/config.yaml")
        prepare_task.add_tags(["template", "prepare_data"])
        prepare_task.close()
        logger.info("Created template task: prepare_data_template")

        # Template for train_model
        train_script_path = project_root / "src" / "models" / "train_model.py"
        train_task = Task.create(
            project_name=project_name,
            task_name="train_model_template",
            task_type=Task.TaskTypes.training,
            script=str(train_script_path),
            repo=".",
        )
        train_task.set_parameter(
            "General/processed_dataset_path", "data/processed/wine_processed.csv"
        )
        train_task.set_parameter("General/model_output_path", "models/model.pkl")
        train_task.set_parameter("General/metrics_output_path", "reports/metrics.json")
        train_task.set_parameter("General/config_path", "conf/config.yaml")
        train_task.add_tags(["template", "train_model"])
        train_task.close()
        logger.info("Created template task: train_model_template")

        # Template for visualize
        visualize_script_path = project_root / "src" / "visualization" / "visualize.py"
        visualize_task = Task.create(
            project_name=project_name,
            task_name="visualize_template",
            task_type=Task.TaskTypes.monitor,
            script=str(visualize_script_path),
            repo=".",
        )
        visualize_task.set_parameter("General/metrics_path", "reports/metrics.json")
        visualize_task.set_parameter("General/output_dir", "reports/figures")
        visualize_task.set_parameter("General/config_path", "conf/config.yaml")
        visualize_task.add_tags(["template", "visualize"])
        visualize_task.close()
        logger.info("Created template task: visualize_template")

    logger.info("All template tasks created successfully")


def main():
    """Main function to create and run pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Create and run ClearML pipeline")
    parser.add_argument(
        "--project-name",
        default="wine-quality-mlops",
        help="ClearML project name",
    )
    parser.add_argument(
        "--pipeline-name",
        default="wine-quality-pipeline",
        help="Pipeline name",
    )
    parser.add_argument(
        "--config-path",
        default="conf/config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--create-templates",
        action="store_true",
        help="Create template tasks before running pipeline",
    )
    parser.add_argument(
        "--queue",
        default=None,
        help="Queue name to run pipeline on (default: local)",
    )
    parser.add_argument(
        "--use-dvc",
        action="store_true",
        default=True,
        help="Use DVC integration (default: True)",
    )
    parser.add_argument(
        "--no-dvc",
        dest="use_dvc",
        action="store_false",
        help="Disable DVC integration",
    )

    args = parser.parse_args()

    # Create template tasks if requested
    if args.create_templates:
        create_template_tasks(args.project_name, use_dvc=args.use_dvc)

    # Create pipeline
    pipe = create_pipeline(
        project_name=args.project_name,
        pipeline_name=args.pipeline_name,
        config_path=args.config_path,
        use_dvc=args.use_dvc,
    )

    # Configure notifications
    # Notifications are configured in ClearML UI: Settings -> Notifications
    # Or via environment variables:
    # CLEARML_NOTIFICATION_EMAIL, CLEARML_NOTIFICATION_WEBHOOK, etc.
    logger.info("Pipeline notifications can be configured in ClearML UI")

    # Start pipeline
    logger.info("Starting pipeline: %s", args.pipeline_name)
    if args.queue:
        pipe.set_default_execution_queue(args.queue)
        pipe.start(queue=args.queue)
        logger.info("Pipeline queued on: %s", args.queue)
    else:
        # For local execution, ClearML pipelines require an execution queue
        # The recommended approach is to use DVC for local runs (dvc repro)
        # which is already integrated with ClearML for experiment tracking
        logger.warning("ClearML pipelines require an execution queue for remote execution.")
        logger.info("For local execution, use DVC (already integrated with ClearML):")
        logger.info("  dvc repro")
        logger.info("")
        logger.info("To run via ClearML pipeline with queue:")
        logger.info("  1. Create a queue in ClearML UI: Settings -> Queues")
        logger.info("  2. Run: python scripts/run_pipeline.py --queue <queue_name>")
        logger.info("")
        logger.info("Pipeline definition is available in ClearML UI for manual execution.")
        logger.info("All experiments are automatically tracked in ClearML when using DVC.")

    logger.info("Pipeline execution started. Monitor in ClearML UI.")
    logger.info("To configure notifications:")
    logger.info("  1. Go to ClearML UI -> Settings -> Notifications")
    logger.info("  2. Configure email/webhook notifications")
    logger.info("  3. Set up alerts for pipeline completion/failure")


if __name__ == "__main__":
    main()
