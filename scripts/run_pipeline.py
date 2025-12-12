#!/usr/bin/env python3
"""Script to run ClearML pipeline."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipelines.clearml_pipeline import main  # noqa: E402

if __name__ == "__main__":
    # Run the main function from the pipeline module
    main()
