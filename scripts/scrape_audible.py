# scripts/scrape_audible.py
import logging
import os
from audiblescrapernct.load_config import load_config
from audiblescrapernct.scraper import launch_scraper
from audiblescrapernct.configuration import Configuration
from audiblescrapernct.init_logging import setup_logging

logger = logging.getLogger(__name__)
    
def main() -> None:
    """
    Entry point for scraping Audible library.
    """
    config = None
    try:
        config = load_config()
        setup_logging(config.logging_folder, config.log_file, config.log_level)
    except Exception as e:
        print(f"Could not load configuration or set up logging.\nDetails: {repr(e)}")   
        return

    try:
        logger.info("Starting Audible scraping process...")
        launch_scraper(config)
        logger.info("Audible scraping process completed.")
    except KeyboardInterrupt:
        logger.warning("Scraping process interrupted by user.")
    except Exception as e:
        logger.exception(f"❌ Scraping failed due to unexpected error.\nDetails: {repr(e)}")
    else:
        logger.info("✅ Scraping completed successfully!")

if __name__ == "__main__":
    main()
