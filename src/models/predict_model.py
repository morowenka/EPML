"""Model prediction module with ClearML integration."""

import logging
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

# ClearML integration (optional)
try:
    from clearml import InputModel

    CLEARML_AVAILABLE = True
except ImportError:
    CLEARML_AVAILABLE = False
    InputModel = None

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


def load_model_from_clearml(model_name: str, version: str | None = None) -> Any:
    """Load a model from ClearML Model Registry."""
    if not CLEARML_AVAILABLE:
        raise ImportError("ClearML is not available. Install with: uv sync")

    try:
        if version:
            model = InputModel(model_id=version)
        else:
            # Get latest version
            model = InputModel(name=model_name)

        model_path = model.get_local_copy()
        logger.info(f"Loaded model from ClearML: {model_name}, version: {model.id}")

        # Load the model file
        model_file = Path(model_path) / "model.pkl"
        if not model_file.exists():
            # Try to find any .pkl file
            pkl_files = list(Path(model_path).glob("*.pkl"))
            if pkl_files:
                model_file = pkl_files[0]
            else:
                raise FileNotFoundError(f"No model file found in {model_path}")

        return joblib.load(model_file)

    except Exception as e:
        logger.error(f"Failed to load model from ClearML: {e}")
        raise


def load_model_from_file(model_path: str | Path) -> Any:
    """Load a model from a local file."""
    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    logger.info(f"Loading model from file: {model_path}")
    return joblib.load(model_path)


def predict(model: Any, X: pd.DataFrame) -> pd.Series:
    """Make predictions using the model."""
    logger.info(f"Making predictions for {len(X)} samples")
    predictions = model.predict(X)
    return pd.Series(predictions, name="prediction")


def predict_from_file(
    model_path: str | Path,
    data_path: str | Path,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """Load model and data, make predictions, and save results."""
    model = load_model_from_file(model_path)
    data = pd.read_csv(data_path)

    # Assume target column should be dropped if present
    if "target" in data.columns:
        X = data.drop(columns=["target"])
    else:
        X = data

    predictions = predict(model, X)

    # Combine with original data
    results = data.copy()
    results["prediction"] = predictions

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        results.to_csv(output_path, index=False)
        logger.info(f"Predictions saved to {output_path}")

    return results


def predict_from_clearml(
    model_name: str,
    data_path: str | Path,
    output_path: str | Path | None = None,
    version: str | None = None,
) -> pd.DataFrame:
    """Load model from ClearML, make predictions, and save results."""
    model = load_model_from_clearml(model_name, version=version)
    data = pd.read_csv(data_path)

    # Assume target column should be dropped if present
    if "target" in data.columns:
        X = data.drop(columns=["target"])
    else:
        X = data

    predictions = predict(model, X)

    # Combine with original data
    results = data.copy()
    results["prediction"] = predictions

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        results.to_csv(output_path, index=False)
        logger.info(f"Predictions saved to {output_path}")

    return results
