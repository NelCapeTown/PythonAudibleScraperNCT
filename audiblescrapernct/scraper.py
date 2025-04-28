# Required Libraries:
import json
import os
import requests
from playwright.sync_api import sync_playwright, Page
from time import sleep
from urllib.parse import urlparse, parse_qs
from book import Book

# Constants
AUDIBLE_DOMAIN = "https://www.audible.com"
AUTH_FILE = "auth.json"
DESTINATION_JSON_FILE = "audible_books.json"
IMAGES_FOLDER = "images"

# Downloads one page of audiobooks from the user's Audible library
# def load_books(page):
def load_books(page: Page) -> list[Book]:    
    """Downloads one page of audiobooks from the user's Audible library.

    Args:
        page (type): The Playwright page object that will be downloaded.

    Returns:
        books (list): A list of dictionaries containing book details (or None if nothing).

    Raises:
        General Exception: If any specific line on the page fails to parse, it will be caught and printed.
    
    Side Effects:
        The calling function should maintain the state of the books list.

    Example:
        master_list = []
        master_list += load_books(page)
    """
    books: list[Book] = []
    items = page.query_selector_all(".adbl-library-content-row")
    for item in items:
        try:
            title_el = item.query_selector("span.bc-size-headline3")
            title = title_el.inner_text().strip() if title_el else ""
            
            author_el = item.query_selector("span.authorLabel a")
            author = author_el.inner_text().strip() if author_el else ""
            
            series_el = item.query_selector("li.seriesLabel span a")
            series = series_el.inner_text().strip() if series_el else ""
            
            narrator_el = item.query_selector("span.narratorLabel a")
            narrator = narrator_el.inner_text().strip() if narrator_el else ""
            description_span = item.query_selector("span.merchandisingSummary")
            
            description = ""
            
            if description_span:
                for p in description_span.query_selector_all("p"):
                    text = p.inner_text().strip()
                    if text:
                        description = text
                        break
                if not description:
                    description = description_span.inner_text().strip()
            
            if not description:
                description = "No description found"
            
            cover_el = item.query_selector("img.bc-image-inset-border")
            cover = cover_el.get_attribute("src") if cover_el else ""

            books.append({
                "Title": title,
                "Author": author,
                "Narrator": narrator,
                "Series": series,
                "Description": description,
                "CoverImageURL": cover
            })
        except Exception as e:
            print(f"Error parsing item: {repr(e)}")
    return books

# Parses the URL to extract the page number
def get_page_number(url: str) -> int:    
    """Parses a URL to extract the page number from its query parameters.

    Args:
        url (str): The URL string containing potential query parameters.

    Returns:
        int: The extracted page number, or 1 if the 'page' parameter is not found.

    Example:
        page_num = get_page_number("https://www.audible.com/library/titles?page=3")
        # page_num will be 3

        page_num = get_page_number("https://www.audible.com/library/titles")
        # page_num will be 1
    """
    query = urlparse(url).query
    params = parse_qs(query)
    page_values = params.get("page")
    return int(page_values[0]) if page_values else 1

# Interates through all pages of the Audible library
def scrape_all_pages(page: Page) -> list[Book]:
    """Iterates through all pages of the Audible library, scraping book data.

    Starts scraping from the current page provided and continues by clicking
    the 'Next' button until there are no more pages or an error occurs.

    Args:
        page: The Playwright Page object, assumed to be the first page the user's library.

    Returns:
        books (list): A list of dictionaries, where each dictionary contains the
            details of a scraped book. Returns an empty list if no books
            are found or if pagination fails early.

    Side Effects:
        - Navigates the provided 'page' object to subsequent library pages.
        - Prints status messages about scraping progress and potential errors
            to standard output.
    """
    books: list[Book] = []
    while True:
        print(f"📘 Scraping: {page.url}")
        books += load_books(page)
        try:
            next_button = page.query_selector("span.nextButton a")
            if next_button:
                href = next_button.get_attribute("href")
                if href:
                    next_url = AUDIBLE_DOMAIN + href
                    current_page_number = get_page_number(page.url)
                    next_page_number = get_page_number(next_url)

                    if next_page_number <= current_page_number:
                        print("✅ No more new pages to scrape.")
                        break
                    page.goto(next_url, timeout=60000)
                    # Wait for content to ensure page transition is complete
                    page.wait_for_selector(".adbl-library-content-row", timeout=60000)
                else:
                    # No href found on the next button
                    print("✅ Reached the end of pagination (no href on next button).")
                    break
            else:
                # No next button found
                print("✅ Reached the end of pagination (no next button found).")
                break
        except Exception as e:
            print(f"⚠️ Pagination error while trying to navigate: {repr(e)}")
            print(f"Current URL during error: {page.url}")
            break # Stop pagination on error
    return books

# Downloads all the images for books in the user's library
def download_images(books: list[Book]) -> None:
    """Downloads cover images for the provided list of books.

    Iterates through the list of book dictionaries, extracts the cover image URL,
    and attempts to download the image into the specified IMAGES_FOLDER.
    Skips download if the file already exists. Includes a retry mechanism
    for download failures.

    Args:
        books (list): A list of dictionaries, where each dictionary represents
            a book and must contain a 'CoverImageURL' key.

    Side Effects:
        - Creates the IMAGES_FOLDER directory if it doesn't exist.
        - Downloads image files into the IMAGES_FOLDER.
        - Prints status messages for each download attempt (success, failure, already exists).
        - Prints a summary message indicating the number of failures or success.
    """
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    failures = 0
    for book in books:
        url = book.get("CoverImageURL", "")
        if not url:
            continue

        filename = os.path.basename(urlparse(url).path)
        filepath = os.path.join(IMAGES_FOLDER, filename)

        if os.path.exists(filepath):
            print(f"🟡 Already exists: {filename}")
            continue

        tries = 0
        success = False
        while tries < 5 and not success:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"✅ Downloaded: {filename}")
                success = True
            except Exception as e:
                tries += 1
                print(f"❌ Error downloading {filename} (Attempt {tries}): {repr(e)}")
                sleep(10)  # small delay before retry
        if not success:
            print(f"❌ Failed to download {filename} after 5 attempts.")
            failures += 1
    if failures > 0:
        print(f"❌ {failures} images failed to download.")
    else:
        print("✅ All images downloaded.")

# Gets the first page of the Audible library and then calls scrape_all_pages(page) with the first page as the argument
def launch_scraper():
    """Initializes the scraping process.

    Launches a Playwright browser instance, attempts to load the Audible library
    page, handling potential login/CAPTCHA issues with a user prompt and retry
    mechanism. If the library page loads successfully, it proceeds to scrape
    all pages, save the collected book data to a JSON file, and download
    the associated cover images.

    Side Effects:
        - Launches a browser window.
        - May prompt the user for input if the initial library page load fails.
        - Creates or overwrites the JSON output file (`DESTINATION_JSON_FILE`).
        - Creates the image output directory (`IMAGES_FOLDER`) if it doesn't exist.
        - Downloads image files into the image output directory.
        - Prints status messages to standard output.
        - Closes the browser and context upon completion or user interruption.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=AUTH_FILE) if os.path.exists(AUTH_FILE) else browser.new_context()
        page = context.new_page()
        page.goto(AUDIBLE_DOMAIN + "/library/titles", timeout=60000)

        library_loaded = False
        while not library_loaded:
            try:
                print("⏳ Waiting for library page content...")
                # Wait for the first book row element to appear
                page.wait_for_selector(".adbl-library-content-row", timeout=60000)
                print("✅ First library page loaded successfully.")
                library_loaded = True # Set flag to exit loop
            except Exception as e:
                print(f"❌ Failed to load the library page: {repr(e)}")  # Corrected to use repr(e)
                print(f"Current URL: {page.url}")
                # Ask user if they want to retry or stop
                action = input("Please log in manually or solve CAPTCHA if needed. Type 'S' to stop or press ENTER to retry: ").strip().upper()
                if action == 'S':
                    print("🛑 User chose to stop.")
                    books = [] # Ensure books list is empty
                    context.close()
                    browser.close()
                    return # Exit the function early

                # If not stopping, the loop will continue and retry page.wait_for_selector

        # Only proceed if the library loaded successfully
        if library_loaded:
            books = scrape_all_pages(page)
            if books:
                # Save books to JSON
                with open(DESTINATION_JSON_FILE, "w", encoding="utf-8") as f:
                    json.dump(books, f, ensure_ascii=False, indent=2)
                print(f"✅ {len(books)} books written to '{DESTINATION_JSON_FILE}' as JSON")

                # Download images
                download_images(books)
                print(f"✅ Saved {len(books)} books and downloaded images.")
            else:
                print("✅ No books found in the library.")

        context.close()
        browser.close()

# Entry point for the script
if __name__ == "__main__":
    launch_scraper()
