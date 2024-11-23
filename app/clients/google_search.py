import os
from typing import List
import httpx
from bs4 import BeautifulSoup
from pathlib import Path

class GoogleImageSearch:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }

    async def search_images(self, query: str, num: int = 1) -> List[str]:
        """
        Search for images using Google Images and return the first result.
        """
        try:
            # Construct the Google Images search URL
            search_url = f"https://www.google.com/search?q={query}&tbm=isch"
            
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
                response = await client.get(search_url)
                if response.status_code != 200:
                    print(f"❌ Failed to fetch images: {response.status_code}")
                    return []

                # Parse the HTML and find image URLs
                soup = BeautifulSoup(response.text, 'html.parser')
                img_tags = soup.find_all('img')
                
                # Skip the first image as it's usually a Google Images logo
                image_urls = []
                for img in img_tags[1:]:  # Skip first image
                    src = img.get('src')
                    if src and src.startswith('http'):
                        image_urls.append(src)
                        if len(image_urls) >= num:
                            break

                if image_urls:
                    print(f"✅ Found image for query: {query}")
                    return image_urls
                return []

        except Exception as e:
            print(f"❌ Error searching for images: {str(e)}")
            return []

# Create singleton instance
image_search = GoogleImageSearch()
