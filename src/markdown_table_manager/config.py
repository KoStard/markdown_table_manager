import json
import os
from pathlib import Path
from typing import Dict

def _get_config_dir() -> Path:
    """
    Determine the configuration directory.
    This reads the environment variable each time it is called,
    ensuring that tests which monkeypatch the environment see the
    correct (temporary) location.
    """
    return Path(
        os.getenv(
            "MARKDOWN_TABLE_MANAGER_CONFIG_DIR",
            os.path.expanduser("~/.config/markdown_table_manager")
        )
    )

def _ensure_config_dir():
    """
    Ensure that the configuration directory exists.
    """
    config_dir = _get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

def _config_file() -> Path:
    """
    Return the full path to the config file.
    """
    return _get_config_dir() / "config.json"

def load_config() -> Dict:
    """
    Load the configuration from the JSON file.
    If the file does not exist, return an empty configuration.
    """
    _ensure_config_dir()
    config_path = _config_file()
    if not config_path.exists():
        return {"tables": {}}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config: Dict):
    """
    Save the given configuration dictionary to the JSON file.
    """
    _ensure_config_dir()
    config_path = _config_file()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def register_table(name: str, path: Path):
    """
    Register a markdown table under the given name.
    """
    cfg = load_config()
    cfg["tables"][name] = str(path)
    save_config(cfg)

def unregister_table(name: str):
    """
    Unregister the table with the given name.
    """
    cfg = load_config()
    cfg["tables"].pop(name, None)
    save_config(cfg)

def list_tables() -> Dict[str, str]:
    """
    Return a dictionary of registered tables.
    """
    return load_config().get("tables", {})
