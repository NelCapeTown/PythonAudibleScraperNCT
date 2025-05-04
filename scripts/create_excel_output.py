# scripts/create_excel_output.py
import logging
import os
from audiblescrapernct.load_config import load_config
from audiblescrapernct.create_excel import create_audible_library_excel
from audiblescrapernct.configuration import Configuration
from audiblescrapernct.init_logging import setup_logging

logger = logging.getLogger(__name__)

def main() -> None:
    """
    Entry point for creating Markdown output file from previously scraped Audible Library JSON file.
    """
    config = None
    try:
        config = load_config()
        setup_logging(config.logging_folder, config.log_file, config.log_level)
    except Exception as e:
        print(f"Could not load configuration or set up logging.\nDetails: {repr(e)}")   
        return

    try:
        logger.info("Starting Excel export process...")
        create_audible_library_excel(config)
        logger.info("Excel export process completed.")
    except KeyboardInterrupt:
        logger.warning("Markdown export process interrupted by user.")
    except Exception as e:
        logger.exception(f"❌ Markdown export failed due to unexpected error.\nDetails: {repr(e)}")
    else:
        logger.info("✅ Markdown export completed successfully!")

if __name__ == "__main__":    
    main()
