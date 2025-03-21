from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def extract_chapter_content(url):
    try:
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        #chrome_options.add_argument('--headless')  # Run without opening browser window
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        
        # Initialize the WebDriver (assuming Chrome)
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the content to load
        # Wait up to 10 seconds for the chapter content to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'chapter_content'))
        )
        
        # Give extra time for all content to render
        time.sleep(2)
        
        # Find the chapter content
        content_div = driver.find_element(By.ID, 'chapter_content')
        
        if not content_div:
            return "Could not find chapter content on the page"
        
        # Get all paragraph elements
        paragraphs = content_div.find_elements(By.TAG_NAME, 'p')
        
        # Combine paragraph texts
        chapter_text = ''
        for p in paragraphs:
            chapter_text += p.text.strip() + '\n\n'
        
        return chapter_text.strip()
    
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
    finally:
        # Clean up: close the browser
        try:
            driver.quit()
        except:
            pass

# URL to scrape
url = "https://tomatomtl.com/book/7420021196307057689/7420410130262409753"

# Get and print the content
content = extract_chapter_content(url)
print(content)

# Optionally save to file
with open('chapter_content.txt', 'w', encoding='utf-8') as f:
    f.write(content)