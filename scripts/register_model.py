#!/usr/bin/env python3
"""Script to manually register a model in ClearML Model Registry."""

import argparse
import sys
from pathlib import Path

try:
    from clearml import OutputModel, Task
except ImportError:
    print("Error: clearml is not installed. Run: uv sync")
    sys.exit(1)


def register_model(
    model_path: str | Path,
    model_name: str,
    project_name: str = "wine-quality-mlops",
    task_id: str | None = None,
    metadata: dict | None = None,
):
    """Register a model in ClearML Model Registry."""
    model_path = Path(model_path)

    if not model_path.exists():
        print(f"Error: Model file not found: {model_path}")
        return False

    try:
        # If task_id is provided, use it to create OutputModel
        if task_id:
            task = Task.get_task(task_id=task_id)
            model = OutputModel(task=task, name=model_name)
        else:
            # Create a new task for model registration
            task = Task.init(
                project_name=project_name,
                task_name=f"register-{model_name}",
                task_type=Task.TaskTypes.inference,
            )
            model = OutputModel(task=task, name=model_name)

        # Update model weights
        model.update_weights(weights_filename=str(model_path))

        # Add metadata if provided
        if metadata:
            model.update_metadata(metadata=metadata)

        # Set tags
        model.set_tags(["manual_registration", "production"])

        print(f"✓ Model '{model_name}' registered successfully")
        print(f"  Model ID: {model.id}")
        print(f"  Project: {project_name}")

        if not task_id:
            task.close()

        return True

    except Exception as e:
        print(f"Error: Failed to register model: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Register a model in ClearML Model Registry")
    parser.add_argument("model_path", type=Path, help="Path to model file (.pkl)")
    parser.add_argument("--model-name", required=True, help="Model name in registry")
    parser.add_argument("--project-name", default="wine-quality-mlops", help="ClearML project name")
    parser.add_argument("--task-id", help="Task ID to associate model with")
    parser.add_argument("--metadata", help="JSON string with metadata")

    args = parser.parse_args()

    metadata = None
    if args.metadata:
        import json

        metadata = json.loads(args.metadata)

    success = register_model(
        model_path=args.model_path,
        model_name=args.model_name,
        project_name=args.project_name,
        task_id=args.task_id,
        metadata=metadata,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
