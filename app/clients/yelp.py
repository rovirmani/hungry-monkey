import os
from typing import List, Optional, Dict, Any
import httpx
from dotenv import load_dotenv
from app.models import Restaurant, SearchParams

class YelpClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("YELP_API_KEY")
        if not self.api_key:
            raise ValueError("YELP_API_KEY not found in .env file")
            
        self.base_url = "https://api.yelp.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "accept": "application/json"
        }

    async def search_restaurants(self, params: SearchParams) -> List[Restaurant]:
        """Search for restaurants using Yelp API."""
        try:
            print(f"Making request to: {self.base_url}/businesses/search")
            
            # Convert parameters to Yelp API format
            search_params = {
                "term": params.term,
                "location": params.location,
                "radius": int(params.radius) if params.radius else None,
                "limit": params.limit,
                "sort_by": params.sort_by,
                "open_now": params.open_now,
                "price": params.price,
            }
            
            # Remove None values
            search_params = {k: v for k, v in search_params.items() if v is not None}
            
            print(f"Search params: {search_params}")  # Debug log
            print(f"Headers: {self.headers}")  # Debug log
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/businesses/search",
                    headers=self.headers,
                    params=search_params,
                )
                
                if response.status_code != 200:
                    print(f"Response status: {response.status_code}")
                    print(f"Response text: {response.text}")
                    response.raise_for_status()
                    
                data = response.json()
                
                # Convert response to Restaurant objects
                restaurants = []
                for business in data.get("businesses", []):
                    restaurant = Restaurant(
                        business_id=business["id"],
                        name=business["name"],
                        rating=business["rating"],
                        price=business.get("price"),
                        phone=business.get("phone"),
                        location=business["location"],
                        coordinates=business["coordinates"],
                        photos=business.get("photos", []),
                        categories=business.get("categories", []),
                        is_open=not business.get("is_closed", True)
                    )
                    restaurants.append(restaurant)
                
                return restaurants
                
        except httpx.HTTPError as e:
            print(f" Error: {str(e)}")
            print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
            raise
        except Exception as e:
            print(f" Unexpected error: {str(e)}")
            raise

    async def get_business_details(self, business_id: str) -> Optional[Restaurant]:
        """Get detailed information about a specific business."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/businesses/{business_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                business = response.json()
                
                return Restaurant(
                    business_id=business["id"],
                    name=business["name"],
                    rating=business["rating"],
                    price=business.get("price"),
                    phone=business.get("phone"),
                    location=business["location"],
                    coordinates=business["coordinates"],
                    photos=business.get("photos", []),
                    categories=business.get("categories", []),
                    is_open=not business.get("is_closed", True)
                )
                
        except httpx.HTTPError:
            return None
