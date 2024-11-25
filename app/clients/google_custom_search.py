import os
from typing import List
import httpx
from dotenv import load_dotenv

load_dotenv()

class GoogleCustomImageSearch:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        if not self.api_key or not self.search_engine_id:
            raise ValueError(
                "GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID must be set in .env file"
            )
        
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def search_images(self, query: str, num: int = 1) -> List[str]:
        """
        Search for images using Google Custom Search API.
        
        Args:
            query: Search query string
            num: Number of images to return (max 10)
        
        Returns:
            List of image URLs
        """
        print(f"🔍 Searching for images for query: {query}")
        
        # Ensure num is within API limits (1-10)
        num = max(1, min(num, 10))
        
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "searchType": "image",
            "num": num,
            # Request full size images
            "imgSize": "large",
            # Filter for high quality images
            "safe": "active",
            "imgType": "photo"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    print(f"❌ API request failed: {response.status_code}")
                    print(f"Error: {response.text}")
                    return []

                data = response.json()
                
                if "items" not in data:
                    print("❌ No images found")
                    return []

                # Extract image URLs from the response
                image_urls = [item["link"] for item in data["items"][:num]]
                
                print(f"✅ Found {len(image_urls)} images for query: {query}")
                return image_urls

        except Exception as e:
            print(f"❌ Error searching for images: {str(e)}")
            return []

# Create singleton instance
image_search = GoogleCustomImageSearch()
