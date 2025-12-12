#!/usr/bin/env python3
"""Script to create a ClearML project and verify connection."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from clearml import Task
except ImportError:
    print("Error: clearml is not installed. Run: uv sync")
    sys.exit(1)


def create_project():
    """Create a ClearML project and verify connection."""
    project_name = "wine-quality-mlops"

    print(f"Creating ClearML project: {project_name}")

    try:
        # Initialize a task to create/verify project
        task = Task.init(
            project_name=project_name,
            task_name="setup-verification",
            auto_connect_frameworks=False,
        )

        print("✓ Successfully connected to ClearML Server")
        print(f"✓ Project '{project_name}' is ready")
        print(f"  Task ID: {task.id}")
        print(f"  Project ID: {task.project}")

        # Close the task (we don't need to keep it)
        task.close()

        print("\n✓ ClearML setup verification completed successfully!")
        return True

    except Exception as e:
        print("Error: Failed to connect to ClearML Server")
        print(f"Details: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure ClearML Server is running: docker-compose ps")
        print("2. Check your ~/.clearml.conf configuration")
        print("3. Verify server is accessible at http://localhost:8080")
        return False


if __name__ == "__main__":
    success = create_project()
    sys.exit(0 if success else 1)
