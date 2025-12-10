import json
import logging
from pathlib import Path
from typing import Any, cast

import click
from dotenv import find_dotenv, load_dotenv
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


def _load_params(params_path: Path) -> dict[str, Any]:
    if not params_path.exists():
        logger.warning("Params file %s not found. Using defaults.", params_path)
        return cast(dict[str, Any], {})

    with params_path.open("r", encoding="utf-8") as fp:
        return cast(dict[str, Any], json.load(fp))


@click.command()
@click.argument("raw_output_filepath", type=click.Path(path_type=Path))
@click.argument("processed_output_filepath", type=click.Path(path_type=Path))
@click.option(
    "--params-path",
    default="params.json",
    show_default=True,
    type=click.Path(exists=False, path_type=Path),
    help="Path to the parameters file that controls dataset generation.",
)
def main(
    raw_output_filepath: Path,
    processed_output_filepath: Path,
    params_path: Path,
) -> None:
    """Generate the project dataset and prepare processed features."""
    params = _load_params(params_path)
    data_params = params.get("data", {})
    feature_scaling = data_params.get("feature_scaling", True)

    dataset = load_wine(as_frame=True)
    df = dataset.frame

    logger.info("Writing raw dataset to %s", raw_output_filepath)
    raw_output_filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(raw_output_filepath, index=False)

    processed_df = df.copy()
    feature_columns = [col for col in processed_df.columns if col != "target"]

    if feature_scaling:
        logger.info("Applying standard scaling to numerical features.")
        scaler = StandardScaler()
        processed_df[feature_columns] = scaler.fit_transform(processed_df[feature_columns])
    else:
        logger.info("Skipping feature scaling as per configuration.")

    logger.info("Writing processed dataset to %s", processed_output_filepath)
    processed_output_filepath.parent.mkdir(parents=True, exist_ok=True)
    processed_df.to_csv(processed_output_filepath, index=False)


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    main()
