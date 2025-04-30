# audiblescrapernct/scraper.py

import json
import os
import requests
import time
import logging
from dataclasses import asdict
from urllib.parse import urlparse, parse_qs, urljoin
from typing import Optional, List, Dict, Any, Set, Tuple # Corrected Tuple import
from playwright.sync_api import (
    sync_playwright,
    Page,
    Browser,
    BrowserContext,
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
)

# Import classes/functions from your provided modules
from audiblescrapernct.book import Book #
from audiblescrapernct.configuration import Configuration #
from audiblescrapernct.load_config import load_config #
from audiblescrapernct.element_selectors import ELEMENT_SELECTORS, Selectors # Import the instance and class

logger = logging.getLogger(__name__)


# --- Helper Functions ---
# def ensure_directory_exists(path: str) -> None:
def setup_environment(config: Configuration) -> Tuple[str, str, str]:
    """Creates necessary directories (if needed) and returns key file paths."""
    # Configuration.from_dict already makes paths absolute
    logger.info("Setting up environment...")
    auth_file_path = os.path.normpath(os.path.join(config.data_folder, config.auth_file))
    logger.info(f"Auth file path: {auth_file_path}")
    json_output_path = os.path.normpath(os.path.join(config.data_folder, config.output_json_file))
    logger.info(f"JSON output path: {json_output_path}")
    images_save_path = os.path.normpath(config.images_folder)
    logger.info(f"Images save path: {images_save_path}")

    try:
        # data_folder is already created by Configuration logic if relative
        os.makedirs(images_save_path, exist_ok=True)
        logger.info(f"✅ Data directory: '{config.data_folder}'") #
        logger.info(f"✅ Images directory: '{images_save_path}'") #
    except OSError as e:
        logger.error(f"❌ Error ensuring directories exist: {repr(e)}. Check permissions.")
        raise # Re-raise the error to stop execution
    return auth_file_path, json_output_path, images_save_path

def download_image(
    url: str,
    save_folder: str,
    max_retries: int = 3,
    delay_seconds: int = 5
) -> bool:
    """Downloads a cover image with retry mechanism, returning success status.

    Args:
        url (str): The URL of the image to download.
        save_folder (str): Path to the directory where the image should be saved.
        max_retries (int): Maximum number of download attempts.
        delay_seconds (int): Seconds to wait between retries.

    Returns:
        bool: True if download was successful or skipped, False otherwise.

    Side Effects:
        - Downloads an image file into `save_folder`.
        - Prints status messages.
    """
    if not url:
        logger.warning("⚠️ Inside download_image: Skipping download: No URL provided.")
        return True # Treat as skipped, not failed

    try:
        parsed_url = urlparse(url)
        logger.info(f"In download_image: Parsed URL: {parsed_url}")
        base_name = os.path.basename(parsed_url.path)
        if not base_name:
            fallback_name = f"image_{abs(hash(url))}.jpg"
            logger.warning(f"⚠️ Could not determine filename from URL path '{parsed_url.path}', using fallback: {fallback_name}")
            filename = fallback_name
        else:
            filename = base_name

        filepath = os.path.join(save_folder, filename)

        if os.path.exists(filepath):
            logger.info(f"⏩ Skipping existing image: {filename}")
            return True

        logger.info(f"⬇️ Attempting to download: {filename} from {url}")
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=delay_seconds)
                response.raise_for_status()

                with open(filepath, "wb") as f:
                    f.write(response.content)

                logger.info(f"✅ Downloaded image: {filename}")
                return True

            except requests.exceptions.Timeout:
                logger.error(f"⏱️ Timeout on attempt {attempt+1}/{max_retries} for {filename}")
            except requests.exceptions.RequestException as e:
                logger.error(f"⚠️ Request failed on attempt {attempt+1}/{max_retries} for {filename}: {repr(e)}")
            except IOError as e:
                logger.error(f"❌ IO Error writing file on attempt {attempt+1}/{max_retries} for {filename}: {repr(e)}")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error on attempt {attempt+1}/{max_retries} for {filename}: {repr(e)}")

            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay_seconds}s...")
                time.sleep(delay_seconds)

        logger.error(f"❌ Failed to download image after {max_retries} attempts: {filename}")
        return False

    except OSError as e:
        logger.error(f"❌ OS Error preparing to download image {url}: {repr(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error initiating download for {url}: {repr(e)}")
        return False

def get_page_number(url: str) -> int:
    """Parses a URL to extract the page number from its query parameters.

    Args:
        url (str): The URL string.

    Returns:
        int: The extracted page number, or 1 if not found or invalid.
    """
    try:
        logger.info(f"Parsing page number from URL: {url}")
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        page_values = params.get("page", ["1"])
        return int(page_values[0])
    except (ValueError, IndexError, TypeError):
        logger.error(f"⚠️ Could not parse page number from URL '{url}', assuming page 1.")
        return 1


def load_books(page: Page, selectors: Selectors) -> List[Book]: # Updated type hint
    """Loads book entries from the current library page using provided selectors.

    Args:
        page (Page): The Playwright page object for the current library page.
        selectors (Selectors): An object containing CSS selectors for book details. # Updated docstring

    Returns:
        List[Book]: A list of Book objects scraped from the page. Empty if none found.
    """
    items = page.query_selector_all(selectors.library_row) # Use attribute access
    books: List[Book] = []
    logger.info(f"Found {len(items)} potential book rows on the page.")

    for item in items:
        try:

            title_el = item.query_selector(selectors.title)
            title = title_el.inner_text().strip() if title_el else "Unknown Title"
            logger.info(f"Parsing book item: {title}")
            
            author = item.query_selector(selectors.author)
            author = author.inner_text().strip() if author else "Unknown Author"
            logger.info(f"Author: {author}")
            narrator_el = item.query_selector(selectors.narrator)
            narrator = narrator_el.inner_text().strip() if narrator_el else "Unknown Narrator"
            logger.info(f"Narrator: {narrator}")
            # Use the correct field name from book.py
            series_el = item.query_selector(selectors.series)
            series = series_el.inner_text().strip() if series_el else ""
            logger.info(f"Series: {series}")
            description = ""
            description_span = item.query_selector(selectors.description)
            if description_span:
                for p in description_span.query_selector_all(selectors.description_paragraph):
                    text = p.inner_text().strip()
                    if text:
                        description = text
                        break
                if not description:
                    description = description_span.inner_text().strip()
            if not description:
                description = "No description available"
            logger.info(f"Description: {description}")
            
            cover_el = item.query_selector(selectors.image)
            cover = cover_el.get_attribute("src") if cover_el else ""
            logger.info(f"Cover image URL: {cover}")
            
            books.append(Book(
                title=title,
                author=author,
                narrator=narrator,
                description=description,
                cover_image_url=cover, # Assign to cover_image_url
                series=series
            ))
            logger.info(f"✅ Added to books list: {title}")
        except PlaywrightTimeoutError:
            logger.error(f"⏱️ Timeout parsing book item {title}. Skipping item.")
        except PlaywrightError as e:
            logger.error(f"❌ Playwright error parsing book item {title}: {repr(e)}. Skipping item.")
        except Exception as e:
            logger.error(f"❌ Unexpected error parsing book item {title}: {repr(e)}. Skipping item.")

    return books


def save_authentication(context: BrowserContext, auth_file_path: str) -> None:
    """Saves the browser context's authentication state to a file.

    Args:
        context (BrowserContext): The Playwright browser context to save.
        auth_file_path (str): The file path for saving the state.
    """
    try:
        context.storage_state(path=auth_file_path)
        logger.info(f"✅ Authentication state saved to {auth_file_path}")
    except PlaywrightError as e:
        logger.error(f"❌ Failed to save authentication state via Playwright: {repr(e)}")
    except IOError as e:
        logger.error(f"❌ IO Error saving authentication state to {auth_file_path}: {repr(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error saving authentication state: {repr(e)}")

# --- Main Scraper Logic ---

def launch_scraper(config: Optional[Configuration] = None) -> None:
    """Launches the Audible library scraper using configuration from config_path.

    Initializes Playwright, navigates to Audible library, handles login,
    scrapes all pages, saves book data to JSON, and downloads cover images.

    Args:
        config (Optional[Configuration]): Configuration object. If None, defaults to loading from config: Optional[Configuration] = Noneconfig: Optional[Configuration] = Noneconfig: Optional[Configuration] = None"config.json".
    """
    try:
        # Load configuration using the provided function
        config_path = "config.json" # Default path
        effective_config = config or load_config(config_path)
        logger.info("✅ Configuration loaded successfully.")
    except Exception as e:
        # load_config already prints an error message
        logger.error(f"❌ Aborting due to configuration load failure: {repr(e)}")
        return # Cannot proceed without config

    try:
        auth_file_path, json_output_path, images_save_path = setup_environment(effective_config)
    except Exception:
        logger.error("❌ Aborting due to setup environment failure.")
        return

    browser: Optional[Browser] = None
    context: Optional[BrowserContext] = None
    page: Optional[Page] = None
    start_time = time.time()
    logger.info("Setup and Config completed. Starting Audible Library Scraper...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False) # Consider making headless configurable
            logger.info("Browser launched.")

            context_options: Dict[str, Any] = {}
            # Add user agent from config if needed (assuming it might be added to Configuration later)
            if hasattr(effective_config, 'user_agent') and effective_config.user_agent:
                context_options["user_agent"] = effective_config.user_agent

            if os.path.exists(auth_file_path):
                try:
                    context = browser.new_context(storage_state=auth_file_path, **context_options)
                    logger.info(f"Loaded existing authentication state from: {auth_file_path}")
                except Exception as e:
                    logger.error(f"⚠️ Failed to load authentication state: {repr(e)}. Creating new context.")
                    context = browser.new_context(**context_options)
                    logger.error(f"⚠️ New context created.")
            else:
                context = browser.new_context(**context_options)
                logger.info("No existing authentication state found. Created new context.")

            page = context.new_page()
            # Use timeout from loaded configuration
            page.set_default_timeout(effective_config.page_timeout_milliseconds)
            logger.info("Browser page created.")

            # --- Initial Navigation and Login Handling ---
            # Use library URL from loaded configuration
            logger.info(f"Navigating to Audible library: {effective_config.audible_library_url}")
            logged_in = False
            try:
                page.goto(effective_config.audible_library_url, wait_until="domcontentloaded")
                page.wait_for_selector(ELEMENT_SELECTORS.library_row, state="attached", timeout=effective_config.page_timeout_milliseconds) # Use attribute access
                logger.info("✅ Initial library page loaded successfully.")
                logged_in = True
                save_authentication(context, auth_file_path)
            except PlaywrightTimeoutError:
                logger.error("⏳ Timed out waiting for library page elements. Manual login might be required.")
            except PlaywrightError as e:
                logger.error(f"⚠️ Playwright error during initial load: {repr(e)}")

            if not logged_in:
                print("\n" + "="*30)
                print("ACTION REQUIRED: Please log in to Audible manually in the browser window.")
                print("Look for CAPTCHAs or 2FA prompts.")
                print("Ensure you land on the main Library page (showing your books).")
                logger.info("Waiting for manual login...")

                input("🔵 Press Enter here AFTER you have successfully logged in and see your library...")
                print("="*30 + "\n")
                try:
                    logger.info("Verifying library page access after manual login...")
                    # Use longer timeout after manual step
                    page.wait_for_selector(ELEMENT_SELECTORS.library_row, state="attached", timeout=90000) # Use attribute access
                    logger.info("✅ Library page access confirmed.")
                    logged_in = True
                    save_authentication(context, auth_file_path)
                except (PlaywrightError, PlaywrightTimeoutError) as e_retry:
                    logger.error(f"❌ Failed to confirm library access after manual login: {repr(e_retry)}")
                    return

            # --- Scraping Loop ---
            all_books: List[Book] = []
            previous_page_books_repr: Optional[str] = None

            logger.info("--- Starting Library Scraping ---")
            while True:
                current_url = page.url

                current_page_num = get_page_number(current_url)
                logger.info(f"📚 Scraping Page {current_page_num}: {current_url}")

                try:
                    page.wait_for_selector(ELEMENT_SELECTORS.library_row, state="visible", timeout=30000) # Use attribute access
                    page_books = load_books(page, ELEMENT_SELECTORS) # Pass the instance
                    if page_books:
                        # Create a stable representation (JSON string) for comparison
                        current_page_books_repr = json.dumps([asdict(b) for b in page_books], sort_keys=True)
                        if current_page_books_repr == previous_page_books_repr:
                            logger.info(f"⚠️ Content on page {current_page_num} is identical to the previous page. Assuming end of unique content.")
                            break # Stop pagination, do not add these books again
                        previous_page_books_repr = current_page_books_repr # Update for the next iteration's check
                    elif previous_page_books_repr is not None:
                        # If the current page is empty but the previous one wasn't, we've likely gone past the end.
                        logger.info(f"⚠️ Page {current_page_num} is empty after a non-empty page. Assuming end.")
                        break # Stop pagination

                    # Add the unique books found on this page
                    logger.info(f"Found {len(page_books)} books on page {current_page_num}.")
                    all_books.extend(page_books)
                except PlaywrightTimeoutError:
                    logger.error(f"⏱️ Timed out waiting for book content on page {current_page_num}. Skipping page.")
                except PlaywrightError as e:
                    logger.error(f"❌ Playwright error loading books on page {current_page_num}: {repr(e)}. Skipping page.")
                except Exception as e:
                    logger.error(f"❌ Unexpected error loading books on page {current_page_num}: {repr(e)}. Skipping page.")

                # --- Pagination Logic ---
                try:
                    next_button = page.query_selector(ELEMENT_SELECTORS.next_button) # Use attribute access
                    if not next_button:
                        logger.info("✅ No 'next' button found. Reached the end of library pages.")
                        break

                    next_href = next_button.get_attribute("href")
                    if not next_href:
                        logger.info("⚠️ Next button found, but has no href attribute. Assuming end.")
                        break

                    # Use base URL from config if available, otherwise default
                    audible_base = effective_config.audible_library_url
                    next_page_url = urljoin(audible_base, next_href)
                    next_page_num = get_page_number(next_page_url)

                    if next_page_num <= current_page_num:
                        logger.info(f"Pagination logic indicates no new forward page (Next URL: {next_page_url}, Num: {next_page_num}). Assuming end.")
                        break

                    logger.info(f"Navigating to next page ({next_page_num}): {next_page_url}")
                    page.goto(next_page_url, wait_until="domcontentloaded")

                except PlaywrightTimeoutError:
                    logger.error(f"⏱️ Timed out during navigation to next page. Stopping pagination.")
                    break
                except PlaywrightError as e:
                    logger.error(f"❌ Playwright error during pagination: {repr(e)}. Stopping pagination.")
                    break
                except Exception as e:
                    logger.error(f"❌ Unexpected error during pagination: {repr(e)}. Stopping pagination.")
                    break

            logger.info(f"\n--- Scraping Finished. Total books collected: {len(all_books)} ---")

            # --- Save Books Data ---
            if all_books:
                logger.info(f"\n💾 Saving book data to: {json_output_path}")
                try:
                    books_data = [asdict(book) for book in all_books] # Use asdict to convert dataclass to dict
                    with open(json_output_path, "w", encoding="utf-8") as f:
                        json.dump(books_data, f, indent=4, ensure_ascii=False)
                    logger.info(f"✅ Successfully saved {len(all_books)} books.")
                except TypeError as e:
                    logger.error(f"❌ JSON Serialization Error: {repr(e)}. Check Book class and data types.")
                except IOError as e:
                    logger.error(f"❌ IO Error saving JSON file: {repr(e)}")
                except Exception as e:
                    logger.error(f"❌ Unexpected error saving JSON: {repr(e)}")
            else:
                logger.warning("⚠️ No books were collected. Nothing to save.")

            # --- Download Images ---
            if all_books:
                logger.info(f"--- Starting Image Downloads to: {images_save_path} ---")
                success_count = 0
                fail_count = 0
                skip_count = 0
                # Use correct attribute name
                total_images = len([book for book in all_books if book.cover_image_url])
                logger.info(f"Attempting to download images for {total_images} books (if URL available).")

                for i, book in enumerate(all_books):
                    # Use correct attribute name
                    if book.cover_image_url:
                        if download_image(
                            book.cover_image_url, #
                            images_save_path,
                            # Use retry settings from config
                            max_retries=effective_config.max_image_download_retries,
                            delay_seconds=effective_config.delay_between_retries_seconds
                        ):
                            success_count += 1
                        else:
                            fail_count += 1
                    else:
                        skip_count +=1

                    processed_count = i + 1
                    if processed_count % 25 == 0 or processed_count == len(all_books):
                        logger.info(f"Image download progress: {processed_count}/{len(all_books)} books processed...")

                logger.info("\n--- Image Download Summary ---")
                logger.info(f"✅ Successful/Skipped: {success_count}")
                logger.info(f"❌ Failed: {fail_count}")
                logger.info(f"🚫 No URL/Not Attempted: {skip_count}")

            # --- Final Auth Save ---
            logger.info("\nAttempting final authentication state save...")
            save_authentication(context, auth_file_path)

    except PlaywrightError as e:
        logger.error(f"❌ A critical Playwright error occurred: {repr(e)}")
    except KeyboardInterrupt:
        logger.error("\n🛑 User interrupted the process (Ctrl+C).")
    except Exception as e:
        logger.error(f"❌ An unexpected critical error occurred: {repr(e)}")

    # --- Cleanup ---
    finally:
        input("🔵 Press Enter here to close browser and release system resources...")
        print("="*30 + "\n")
        logger.info("\n--- Cleaning up resources ---")
        if page:
            try: page.close()
            except Exception as e: logger.error(f"⚠️ Error closing page: {repr(e)}")
        if context:
            try: context.close()
            except Exception as e: logger.error(f"⚠️ Error closing context: {repr(e)}")
        if browser:
            try: browser.close()
            except Exception as e: logger.error(f"⚠️ Error closing browser: {repr(e)}")

        end_time = time.time()
        minutes, seconds = divmod(end_time - start_time, 60)
        logger.info(f"\n🏁 Scraper finished in {minutes:.0f} minutes and {seconds:.2f} seconds.")


# --- Script Entry Point ---
if __name__ == "__main__":
    print("Starting Audible Library Scraper...")
    # You might want to use argparse here to allow specifying config path via CLI
    # import argparse
    # parser = argparse.ArgumentParser(description="Scrape Audible Library")
    # parser.add_argument("-c", "--config", default="config.json", help="Path to configuration file")
    # args = parser.parse_args()
    # launch_scraper(config_path=args.config)
    launch_scraper() # Uses default "config.json"
    print("Script execution complete.")