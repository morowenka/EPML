#!/usr/bin/env python3
"""Script to help setup ClearML authentication configuration."""

import os
from pathlib import Path


def create_clearml_config(
    access_key: str, secret_key: str, api_server: str = "http://localhost:8080"
):
    """Create ~/clearml.conf configuration file and export environment variables.

    Note: ClearML looks for config in ~/clearml.conf (without dot) by default,
    but we also create ~/.clearml.conf for compatibility.
    """
    # ClearML default location (without dot)
    config_path = Path.home() / "clearml.conf"
    # Also create .clearml.conf for compatibility
    config_path_dot = Path.home() / ".clearml.conf"

    # Determine URLs based on API server
    if "api.clear.ml" in api_server or "app.clear.ml" in api_server:
        # ClearML Cloud
        api_url = "https://api.clear.ml"
        web_url = "https://app.clear.ml"
        files_url = "https://files.clear.ml"
    else:
        # Local server
        api_url = api_server
        web_url = api_server
        files_url = (
            api_server.replace(":8080", ":8081") if ":8080" in api_server else f"{api_server}:8081"
        )

    # Create config file (format from ClearML UI)
    config_content = f"""api {{
    web_server: {web_url}/
    api_server: {api_url}
    files_server: {files_url}
    credentials {{
        "access_key" = "{access_key}"
        "secret_key" = "{secret_key}"
    }}
}}
"""

    # Check if config already exists
    if config_path.exists() or config_path_dot.exists():
        response = input("Config file already exists. Overwrite? (y/N): ")
        if response.lower() != "y":
            print("Aborted.")
            return False

    # Write config to both locations for compatibility
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w") as f:
        f.write(config_content)
    os.chmod(config_path, 0o600)

    # Also create .clearml.conf for compatibility
    with config_path_dot.open("w") as f:
        f.write(config_content)
    os.chmod(config_path_dot, 0o600)

    # Also create shell script for environment variables (more reliable)
    shell_script = Path.home() / ".clearml_env.sh"
    with shell_script.open("w") as f:
        f.write(f"""# ClearML Environment Variables
export CLEARML_API_HOST="{api_url}"
export CLEARML_WEB_HOST="{web_url}"
export CLEARML_FILES_HOST="{files_url}"
export CLEARML_API_ACCESS_KEY="{access_key}"
export CLEARML_API_SECRET_KEY="{secret_key}"
""")
    os.chmod(shell_script, 0o600)

    print(f"✓ Created ClearML configuration at {config_path} (primary)")
    print(f"✓ Created ClearML configuration at {config_path_dot} (compatibility)")
    print(f"✓ Created environment variables script at {shell_script}")
    print("\nTo use environment variables, run:")
    print(f"  source {shell_script}")
    print("Or add to your ~/.zshrc or ~/.bashrc:")
    print(f"  source {shell_script}")
    return True


def main():
    """Interactive setup of ClearML authentication."""
    print("ClearML Authentication Setup")
    print("=" * 40)
    print()
    print("To get your API credentials:")
    print("For ClearML Cloud: https://app.clear.ml → Profile → Create new credentials")
    print("For local server: http://localhost:8080 → Profile → Create new credentials")
    print()

    use_cloud = input("Use ClearML Cloud? (Y/n): ").strip().lower()
    if use_cloud in ("", "y", "yes"):
        api_server = "https://api.clear.ml"
        print("Using ClearML Cloud")
    else:
        api_server = (
            input("Enter API Server URL [http://localhost:8080]: ").strip()
            or "http://localhost:8080"
        )

    print()
    access_key = input("Enter Access Key: ").strip()
    secret_key = input("Enter Secret Key: ").strip()

    if not access_key or not secret_key:
        print("Error: Access Key and Secret Key are required")
        return 1

    if create_clearml_config(access_key, secret_key, api_server):
        print()
        print("✓ Configuration created successfully!")
        print("You can now use ClearML in your Python scripts.")
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
