from time import sleep
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs
import os
import json
import requests


AUTH_FILE = "auth.json"
OUTPUT_FILE = "audible_books.json"
IMAGES_FOLDER = "images"

def load_books(page):
    books = []
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

            books.append({
                "Title": title,
                "Author": author,
                "Narrator": narrator,
                "Series": series,
                "Description": description,
                "CoverImageURL": cover_el.get_attribute("src") if cover_el else ""
            })
        except Exception as e:
            print("Error parsing item:", e)
    return books

def get_page_number(url):
    query = urlparse(url).query
    params = parse_qs(query)
    page_values = params.get("page")
    return int(page_values[0]) if page_values else 1

def scrape_all_pages(page):
    books = []
    while True:
        print(f"📘 Scraping: {page.url}")
        books += load_books(page)
        try:
            next_button = page.query_selector("span.nextButton a")
            if next_button:
                href = next_button.get_attribute("href")
                if href:
                    next_url = "https://www.audible.com" + href
                    current_page_number = get_page_number(page.url)
                    next_page_number = get_page_number(next_url)

                    if next_page_number <= current_page_number:
                        print("✅ No more new pages to scrape.")
                        break
                    page.goto(next_url, timeout=60000)
                    page.wait_for_selector(".adbl-library-content-row")
                else:
                    break
            else:
                break
        except Exception as e:
            print(f"⚠️ Pagination error: {e}")
            break
    return books

def download_images(books):
    os.makedirs("images", exist_ok=True)
    for book in books:
        url = book.get("CoverImageURL", "")
        if not url:
            continue

        filename = os.path.basename(urlparse(url).path)
        filepath = os.path.join("images", filename)

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
                print(f"❌ Error downloading {filename} (Attempt {tries}): {e}")
                sleep(10)  # small delay before retry
        if not success:
            print(f"❌ Failed to download {filename} after 5 attempts.")
    print("✅ All images downloaded.")

def launch_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=AUTH_FILE) if os.path.exists(AUTH_FILE) else browser.new_context()
        page = context.new_page()
        page.goto("https://www.audible.com/library/titles", timeout=60000)
        try:
            page.wait_for_selector(".adbl-library-content-row", timeout=60000)
        except Exception:
            print("Please log in manually or solve CAPTCHA. Press ENTER after done...")
            input()
            page.wait_for_selector(".adbl-library-content-row", timeout=60000)
        books = scrape_all_pages(page)
        if books:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(books, f, ensure_ascii=False, indent=2)
            download_images(books)
            print(f"✅ Saved {len(books)} books and covers.")
        context.close()
        browser.close()

if __name__ == "__main__":
    launch_scraper()
