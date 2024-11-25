import os
from typing import List
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote, urlencode
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class GoogleImageSearch:
    def __init__(self):
        # Set up Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # Run in headless mode
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        # Add realistic user agent
        self.chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')

    async def search_images(self, query: str, num: int = 3) -> List[str]:
        """Search for images using Google Images with Selenium."""
        print(f"\n🔍 Searching for images for query: {query}")
        
        try:
            # Create a new Chrome driver instance
            driver = webdriver.Chrome(options=self.chrome_options)
            
            try:
                # Construct search URL
                search_query = f"{query} restaurant exterior"
                search_url = f"https://www.google.com/search?q={quote(search_query)}&tbm=isch"
                print(f"📡 Using search URL: {search_url}")

                # Load the page
                driver.get(search_url)
                time.sleep(2)  # Wait for dynamic content to load

                # Wait for image results to appear
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "img"))
                )

                # Find all image elements
                image_elements = driver.find_elements(By.CSS_SELECTOR, "img")
                
                # Extract image URLs
                image_urls = []
                for img in image_elements:
                    try:
                        # Try different attributes where the actual image URL might be stored
                        url = img.get_attribute('src') or img.get_attribute('data-src')
                        
                        if url and url.startswith('http') and not url.startswith('https://www.google.com'):
                            if '.jpg' in url.lower() or '.jpeg' in url.lower() or '.png' in url.lower():
                                if url not in image_urls:
                                    print(f"✅ Found valid image URL: {url}")
                                    image_urls.append(url)
                                    if len(image_urls) >= num:
                                        break
                    except Exception as e:
                        print(f"⚠️ Error extracting URL from image: {str(e)}")
                        continue

                print(f"\n✨ Found {len(image_urls)} valid image URLs:")
                for i, url in enumerate(image_urls, 1):
                    print(f"🖼️  {i}. {url}")

                return image_urls[:num]

            finally:
                # Always close the browser
                driver.quit()

        except Exception as e:
            print(f"❌ Error during image search: {str(e)}")
            return []

# Create singleton instance
image_search = GoogleImageSearch()
