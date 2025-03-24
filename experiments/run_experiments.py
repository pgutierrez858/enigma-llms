import json
from pathlib import Path

from loguru import logger

from experiments.config import ConfigModel
from experiments.experiment_runner import run_experiment
from experiments.times import save_to_csv

# Define paths
CONFIGS_DIR = Path("configs")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


def load_config(file_path: Path) -> ConfigModel:
    """Loads and validates a JSON config file using Pydantic."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)  # Load JSON data from file

    return ConfigModel(**data)  # Validate and return a Pydantic model


def save_results(config_name, game_model):
    """Save results to JSON and CSV."""
    # Save as JSON
    json_path = RESULTS_DIR / f"{config_name}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(game_model.model_dump(), f, indent=4)

    # Save as CSV
    save_to_csv(f"{config_name}.csv", RESULTS_DIR)


def run_all_experiments():
    """Run experiments for each config file."""
    config_files = list(CONFIGS_DIR.glob("*.json"))
    for config_file in config_files:
        logger.info(f"Found config file: {config_file}")

    if not config_files:
        logger.debug("No config files found in the 'configs' folder.")
        return

    for config_file in config_files:
        for preprocess in [True, False]:
            logger.debug(f"Running experiment for {config_file.name}...")
            logger.debug(f"Preprocessing set to {preprocess}")
            config = load_config(config_file)
            results = run_experiment(config, preprocess)  # Runs the experiment based on config
            exp_type = "_pre" if preprocess else "_raw"
            save_results(config_file.stem + exp_type, results)
            logger.debug(f"Results saved for {config_file.stem + exp_type}\n")


if __name__ == "__main__":
    run_all_experiments()
