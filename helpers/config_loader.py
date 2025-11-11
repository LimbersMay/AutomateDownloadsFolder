from pathlib import Path

from models.app_config import AppConfig


def load_config(json_path: str) -> AppConfig:
    """ Load the application configuration from a JSON file. """
    config_path = Path(json_path)

    try:
        json_data_string = config_path.read_text(encoding='utf-8')

        return AppConfig.model_validate_json(json_data_string)

    except Exception as e:
        raise RuntimeError(f"Failed to load configuration from {json_path}: {e}")