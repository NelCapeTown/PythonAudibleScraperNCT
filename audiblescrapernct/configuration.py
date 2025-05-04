from dataclasses import dataclass
from typing import Optional
import os

@dataclass(slots=True)
class Configuration:
    """
    Strongly-typed configuration loaded from config.json.
    """
    data_folder: str
    logging_folder: str
    log_file: str
    log_level: str
    auth_file: str
    output_json_file: str
    output_excel_file: str
    output_markdown_file: str
    images_folder: str
    audible_library_url: str
    max_image_download_retries: int = 5
    delay_between_retries_seconds: int = 10
    page_timeout_milliseconds: int = 60000
    user_agent: Optional[str] = None

    @staticmethod
    def from_dict(config_dict: dict) -> "Configuration":
        """
        Create a Configuration instance from a dictionary,
        handling relative paths smartly.
        """
        data_folder = config_dict.get("data_folder", "")
        if not os.path.isabs(data_folder):
            data_folder = os.path.abspath(data_folder)
        config_dict["data_folder"] = data_folder

        images_folder = config_dict.get("images_folder", "images")
        if not os.path.isabs(images_folder):
            images_folder = os.path.join(data_folder, images_folder)
        config_dict["images_folder"] = images_folder

        return Configuration(**config_dict)
