import json
from audiblescrapernct.configuration import Configuration

def load_config(config_path: str = "config.json") -> Configuration:
    """
    Loads configuration from a JSON file and returns a Configuration object.
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
        return Configuration.from_dict(config_dict)
    except Exception as e:
        print(f"❌ Failed to load config file: {repr(e)}")
        raise
