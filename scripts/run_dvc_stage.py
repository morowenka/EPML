#!/usr/bin/env python3
"""Script to run a DVC stage from ClearML pipeline."""

import subprocess
import sys
from pathlib import Path

from clearml import Task

# Get DVC stage from task parameters
task = Task.current_task()
if task:
    dvc_stage = task.get_parameter("General/dvc_stage")
    config_path = task.get_parameter("General/config_path", "conf/config.yaml")
else:
    # Fallback for direct execution
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dvc-stage", required=True)
    parser.add_argument("--config-path", default="conf/config.yaml")
    args = parser.parse_args()
    dvc_stage = args.dvc_stage
    config_path = args.config_path

if not dvc_stage:
    print("Error: DVC stage not specified")
    sys.exit(1)

# Run DVC repro for the specific stage
project_root = Path(__file__).parent.parent
cmd = ["dvc", "repro", dvc_stage]

print(f"Running DVC stage: {dvc_stage}")
print(f"Command: {' '.join(cmd)}")

result = subprocess.run(
    cmd,
    cwd=project_root,
    check=False,
)

if result.returncode != 0:
    print(f"Error: DVC repro failed with exit code {result.returncode}")
    sys.exit(result.returncode)

print(f"✓ DVC stage {dvc_stage} completed successfully")
