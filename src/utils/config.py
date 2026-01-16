"""Configuration management using Hydra compose API."""

import json
import logging
from pathlib import Path
from typing import Any, cast

from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra
from omegaconf import DictConfig, OmegaConf

logger = logging.getLogger(__name__)


def load_config(
    config_path: Path | None = None,
    config_name: str = "config",
    overrides: list[str] | None = None,
) -> dict[str, Any]:
    """
    Load configuration using Hydra compose API with proper composition.

    This function properly handles Hydra's defaults composition, merging
    base configs with overrides as specified in the config files.

    Args:
        config_path: Path to the config directory (default: conf/)
        config_name: Name of the config file without extension (default: config)
        overrides: List of Hydra-style overrides (e.g., ["train.model.type=svm"])

    Returns:
        Dictionary with resolved configuration
    """
    if config_path is None:
        config_path = Path("conf")

    # Ensure config_path is absolute
    config_dir = config_path.resolve() if config_path.is_dir() else config_path.parent.resolve()

    # Extract config name from path if it's a file
    if config_path.is_file():
        config_name = config_path.stem

    # Clear any existing Hydra instance
    GlobalHydra.instance().clear()

    try:
        # Initialize Hydra with the config directory
        with initialize_config_dir(config_dir=str(config_dir), version_base=None):
            cfg: DictConfig = compose(config_name=config_name, overrides=overrides or [])

            # Convert to plain dict with resolved interpolations
            config_dict = OmegaConf.to_container(cfg, resolve=True)

            logger.info("Loaded configuration from %s/%s.yaml", config_dir, config_name)
            logger.debug("Configuration: %s", config_dict)

            return cast(dict[str, Any], config_dict)

    except Exception as e:
        logger.warning("Failed to load config with Hydra: %s. Falling back to direct load.", e)
        return _load_config_fallback(config_path)


def _load_config_fallback(config_path: Path) -> dict[str, Any]:
    """Fallback config loading without Hydra composition."""
    if not config_path.exists():
        logger.warning("Config file %s not found. Using empty config.", config_path)
        return {}

    if config_path.suffix in (".yaml", ".yml"):
        cfg = OmegaConf.load(config_path)
        return cast(dict[str, Any], OmegaConf.to_container(cfg, resolve=True))

    if config_path.suffix == ".json":
        with config_path.open("r", encoding="utf-8") as fp:
            return cast(dict[str, Any], json.load(fp))

    logger.warning("Unknown config format: %s", config_path.suffix)
    return {}


def load_config_with_params(
    config_path: Path | None = None,
    params_path: Path | None = None,
    config_name: str = "config",
) -> dict[str, Any]:
    """
    Load configuration with fallback to params.json for backward compatibility.

    Args:
        config_path: Path to Hydra config (takes precedence)
        params_path: Path to params.json (fallback)
        config_name: Name of the config file without extension

    Returns:
        Dictionary with resolved configuration
    """
    # Try Hydra config first
    if config_path and (config_path.exists() or config_path.is_dir()):
        return load_config(config_path, config_name)

    # Fallback to params.json
    if params_path and params_path.exists():
        logger.info("Using fallback params from %s", params_path)
        return _load_config_fallback(params_path)

    # Check default config directory
    default_config = Path("conf")
    if default_config.exists():
        return load_config(default_config, config_name)

    logger.warning("No configuration found. Using defaults.")
    return {}
