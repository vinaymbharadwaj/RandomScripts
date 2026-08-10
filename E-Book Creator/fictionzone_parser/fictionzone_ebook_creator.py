import random
import re
import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ebooklib import epub

# --- CONFIGURATION ---
NOVEL_TITLE = "Detective Science: The Grim Reaper Elementary School Student"
NOVEL_SLUG = "detective-science-the-grim-reaper-elementary-school-student-helps-me-become-a-tycoon"
BASE_URL = f"https://fictionzone.net/novel/{NOVEL_SLUG}/"
INPUT_FILE = "input.txt"  # This file should contain the HTML snippet with chapter links

# Path to your EXISTING Firefox profile (already logged in)
# Using 'r' before the string handles the Windows backslashes
FIREFOX_PROFILE_PATH = r"C:\Users\vinay\AppData\Roaming\Mozilla\Firefox\Profiles\spdu5de0.default-release"

# --- CSS SELECTORS ---
TITLE_SELECTOR = "#__nuxt > div.chapter-page.is-mounted > main > div.content-container > article > header"
CONTENT_SELECTOR = "#__nuxt > div.chapter-page.is-mounted > main > div.content-container > article > div.chapter-text"

def create_epub():
    # 1. Read input from input.txt
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            INPUT_HTML = f.read()
    except FileNotFoundError:
        print(f"Error: '{INPUT_FILE}' not found. Please ensure it exists in the same folder as this script.")
        return

    # 2. Parse the input to get IDs
    soup = BeautifulSoup(INPUT_HTML, 'html.parser')
    chapters_to_fetch = []
    
    for a in soup.find_all('a'):
        href = a.get('href')
        match = re.search(r'chapter_id=(\d+)', href)
        if match:
            c_id = match.group(1)
            full_url = f"{BASE_URL}{c_id}"
            chapters_to_fetch.append({
                'url': full_url,
                'id': c_id
            })

    if not chapters_to_fetch:
        print("No valid chapter links were found in input.txt.")
        return

    # 3. Setup Selenium with Firefox Profile
    options = FirefoxOptions()
    options.add_argument("-profile")
    options.add_argument(FIREFOX_PROFILE_PATH)
    
    print("Launching Firefox with your profile...")
    # Make sure Firefox is closed before this line executes!
    driver = webdriver.Firefox(options=options)
    
    # Set up the explicit wait (up to 15 seconds)
    wait = WebDriverWait(driver, 15)
    
    # 4. Initialize EPUB
    book = epub.EpubBook()
    book.set_title(NOVEL_TITLE)
    book.set_language('en')
    book.add_author('FictionZone Author')

    epub_chapters = []

    try:
        for idx, item in enumerate(chapters_to_fetch):
            #--- THE NEW RANDOM DELAY ---
            # We skip the delay on the very first chapter so it starts immediately
            if idx > 0:
                # Pick a random wait time between 7.0 and 15.0 seconds
                sleep_time = random.uniform(20.0, 30.0)
                print(f"Waiting for {sleep_time:.2f} seconds to mimic human behavior...")
                time.sleep(sleep_time)

            print(f"Loading URL: {item['url']}...")
            driver.get(item['url'])
            
            try:
                # Wait for BOTH elements to be present and visible on the page
                content_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, CONTENT_SELECTOR)))
                title_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, TITLE_SELECTOR)))
                
                # Extract text and HTML directly from Selenium elements
                chapter_title = title_element.text.strip()
                chapter_html = content_element.get_attribute('innerHTML')
                
                print(f"Successfully scraped: {chapter_title}")

                # Create EPUB chapter object
                c = epub.EpubHtml(title=chapter_title, file_name=f"chap_{idx+1}.xhtml", lang='en')
                c.content = f"<h1>{chapter_title}</h1>\n{chapter_html}"
                
                book.add_item(c)
                epub_chapters.append(c)

            except Exception as e:
                print(f"Error scraping chapter {item['url']}: {e}")
                # Skips to the next chapter if one fails, rather than crashing the whole script

    finally:
        driver.quit()

    # 5. Finalize EPUB structure
    if not epub_chapters:
        print("No chapters were successfully scraped. Aborting EPUB creation.")
        return

    book.toc = tuple(epub_chapters)
    book.add_item(epub.NavPoint())
    book.add_item(epub.EpubNcx())
    book.spine = ['nav'] + epub_chapters

    # 6. Save file
    output_file = f"{NOVEL_TITLE}.epub"
    epub.write_epub(output_file, book, {})
    print(f"Success! Created '{output_file}'")

if __name__ == "__main__":
    create_epub()