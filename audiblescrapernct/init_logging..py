import logging
import os
import json
from typing import Optional, Tuple

# Map string levels to logging constants
LOG_LEVEL_MAP = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

# --- Define the Custom JSON Formatter ---
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "pathname": record.pathname,
            "lineno": record.lineno,
            "message": record.getMessage(), # Use getMessage() to format the message string
        }
        # Include exception info if available
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        if record.stack_info:
            log_entry['stack_info'] = self.formatStack(record.stack_info)

        return json.dumps(log_entry, indent=4, default=str)

# Initialize logging for the package
def setup_logging(log_folder: str, log_file: str, log_level: str) -> None:
    """
    Sets up logging for the package.
    Creates a log folder if it doesn't exist and configures logging to
        - write to a file as specified in the configuration in json format
        - print to the console in a human-readable format.

    Args:
        log_folder (str): The folder where the log files will be stored.
        log_file (str): The name of the log file.
        log_level (str): The logging level. Can be 'debug', 'info', 'warning', 'error', or 'critical'.
    """
    os.makedirs(log_folder, exist_ok=True)
    filename = os.path.join(log_folder, log_file)
    num_log_level = LOG_LEVEL_MAP.get(log_level.lower(), logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(num_log_level)
    formatter = logging.Formatter('%(asctime)s - %(pathname)s - %(name)s - %(levelname)s - %(message)s')
    json_formatter = JsonFormatter()
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(json_formatter)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)  
    logger.info(f"Logging setup complete. Logs will be saved to {filename}")
    
