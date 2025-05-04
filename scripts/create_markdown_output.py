# scripts/scrape_audible.py
import logging
import os
from audiblescrapernct.load_config import load_config
from audiblescrapernct.create_markdown import export_markdown
from audiblescrapernct.configuration import Configuration

# Map string levels to logging constants
LOG_LEVEL_MAP = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

def setup_logging(log_folder: str, log_file: str = "audiblescraper.log", log_level: str = "INFO") -> None:
    """
    Sets up logging for the package.
    Creates a log folder if it doesn't exist and configures logging to both a file and the console.

    Args:
        log_folder (str): The folder where the log files will be stored.
        log_file (str, optional): The name of the log file. Defaults to "audiblescraper.log".
    """
    os.makedirs(log_folder, exist_ok=True)
    filename=os.path.join(log_folder, log_file)
    num_log_level = LOG_LEVEL_MAP.get(log_level.lower(), logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(num_log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(formatter)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)  
    logger.info(f"Logging setup complete. Logs will be saved to {filename}")
    
def main() -> None:
    """
    Entry point for creating Markdown output file from previously scraped Audible Library JSON file.
    """
    config = None
    try:
        config = load_config()
        setup_logging(config.logging_folder)
    except Exception as e:
        print(f"Could not load configuration or set up logging.\nDetails: {repr(e)}")   
        return
    
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting Markdown export process...")
        export_markdown(config)
        logger.info("Markdown export process completed.")
    except KeyboardInterrupt:
        logger.warning("Markdown export process interrupted by user.")
    except Exception as e:
        print(f"❌ Markdown export failed due to unexpected error.\nDetails: {repr(e)}")
    else:
        print("✅ Markdown export completed successfully!")

if __name__ == "__main__":    main()
