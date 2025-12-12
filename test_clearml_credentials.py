#!/usr/bin/env python3
"""Test script to verify ClearML credentials loading."""

import os
import sys
from pathlib import Path

print("=" * 60)
print("ClearML Credentials Test")
print("=" * 60)
print()

# Check config file
config_path = Path.home() / ".clearml.conf"
print(f"1. Checking config file: {config_path}")
if config_path.exists():
    print("   ✓ Config file exists")
    with config_path.open() as f:
        content = f.read()
        print("   Content preview (first 200 chars):")
        print(f"   {content[:200]}...")
        if "access_key" in content and "secret_key" in content:
            print("   ✓ Credentials found in config file")
        else:
            print("   ✗ Credentials NOT found in config file")
else:
    print("   ✗ Config file does NOT exist")

print()

# Check environment variables
print("2. Checking environment variables:")
env_vars = {
    "CLEARML_API_HOST": os.getenv("CLEARML_API_HOST"),
    "CLEARML_WEB_HOST": os.getenv("CLEARML_WEB_HOST"),
    "CLEARML_FILES_HOST": os.getenv("CLEARML_FILES_HOST"),
    "CLEARML_API_ACCESS_KEY": os.getenv("CLEARML_API_ACCESS_KEY"),
    "CLEARML_API_SECRET_KEY": os.getenv("CLEARML_API_SECRET_KEY"),
}

for var, value in env_vars.items():
    if value:
        masked = value[:10] + "..." if len(value) > 10 else value
        print(f"   ✓ {var} = {masked}")
    else:
        print(f"   ✗ {var} is NOT set")

print()

# Try to import and initialize ClearML
print("3. Testing ClearML import and initialization:")
try:
    from clearml import Task

    print("   ✓ ClearML imported successfully")

    # Try to initialize a test task
    print("   Attempting to initialize ClearML Task...")
    task = Task.init(
        project_name="test-credentials",
        task_name="credentials-test",
        auto_connect_frameworks=False,
    )

    print("   ✓ Task initialized successfully!")
    print(f"   Task ID: {task.id}")
    print(f"   Project: {task.project}")
    print(f"   Server: {task.get_output_log_web_page()}")

    # Close the task
    task.close()
    print("   ✓ Task closed successfully")
    print()
    print("=" * 60)
    print("SUCCESS: ClearML credentials are working correctly!")
    print("=" * 60)
    sys.exit(0)

except ImportError as e:
    print(f"   ✗ Failed to import ClearML: {e}")
    print("   Install with: uv sync")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Failed to initialize ClearML Task: {e}")
    print()
    print("   Troubleshooting:")
    print("   1. Check ~/.clearml.conf exists and has correct format")
    print("   2. Check environment variables are set")
    print("   3. Verify credentials are correct in ClearML UI")
    print("   4. Try: source ~/.clearml_env.sh")
    print()
    print("=" * 60)
    print("FAILED: ClearML credentials are NOT working")
    print("=" * 60)
    sys.exit(1)
