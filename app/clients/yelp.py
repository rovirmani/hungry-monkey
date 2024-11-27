from __future__ import annotations
import os
<<<<<<< HEAD
from typing import List, Optional, Dict, Any
import httpx
from dotenv import load_dotenv
from app.models import Restaurant, SearchParams
=======
import json
from typing import List, Optional, Dict, Any
import httpx
import logging

logger = logging.getLogger(__name__)
>>>>>>> origin

class YelpClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("YELP_API_KEY")
        if not self.api_key:
            logger.error("❌ YELP_API_KEY not found in environment variables")
            raise ValueError("YELP_API_KEY not found in environment variables")
            
        self.base_url = "https://api.yelp.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "accept": "application/json"
        }
<<<<<<< HEAD
=======
        logger.info("✅ YelpClient initialized with API key")

    async def search_businesses(
        self,
        term: Optional[str] = None,
        location: str = None,
        price: Optional[str] = None,
        categories: Optional[str] = None,
        limit: Optional[int] = 20,
        sort_by: Optional[str] = "best_match"
    ) -> List[Restaurant]:
        """
        Search for businesses using the Yelp Fusion API
        """
        try:
            # Build query parameters
            params = {
                "term": term or "restaurants",
                "location": location,
                "limit": limit,
                "sort_by": sort_by
            }
            if price:
                params["price"] = price
            if categories:
                params["categories"] = categories
                
            logger.info(f"🔍 Searching Yelp API with params: {params}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/businesses/search",
                    params=params,
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                
                # Convert Yelp response to Restaurant models
                restaurants = []
                for business in data.get("businesses", []):
                    try:
                        restaurant = Restaurant(
                            id=business["id"],
                            name=business["name"],
                            rating=business["rating"],
                            price=business.get("price"),
                            phone=business.get("phone"),
                            location=Location(
                                address1=business["location"].get("address1"),
                                address2=business["location"].get("address2"),
                                address3=business["location"].get("address3"),
                                city=business["location"]["city"],
                                state=business["location"]["state"],
                                zip_code=business["location"]["zip_code"],
                                country=business["location"].get("country", "US"),
                                display_address=business["location"].get("display_address", [])
                            ),
                            coordinates=Coordinates(
                                latitude=business["coordinates"]["latitude"],
                                longitude=business["coordinates"]["longitude"]
                            ),
                            photos=[business.get("image_url")] if business.get("image_url") else [],
                            categories=[
                                Category(alias=cat["alias"], title=cat["title"])
                                for cat in business.get("categories", [])
                            ],
                            is_closed=business.get("is_closed", False)
                        )
                        restaurants.append(restaurant)
                    except Exception as e:
                        logger.error(f"❌ Failed to parse restaurant {business.get('name')}: {str(e)}")
                        continue
                
                logger.info(f"✅ Found {len(restaurants)} restaurants from Yelp")
                return restaurants
                
        except Exception as e:
            logger.error(f"❌ Failed to search Yelp API: {str(e)}")
            return []
>>>>>>> origin

    async def search_restaurants(self, params: SearchParams) -> List[Restaurant]:
        """Search for restaurants using Yelp API."""
        try:
<<<<<<< HEAD
            print(f"Making request to: {self.base_url}/businesses/search")
=======
            logger.info(f"Making request to: {self.base_url}/businesses/search")
>>>>>>> origin
            
            # Convert parameters to Yelp API format
            search_params = {
                "term": params.term,
                "location": params.location,
                "radius": int(params.radius) if params.radius else None,
                "limit": params.limit,
                "sort_by": params.sort_by,
<<<<<<< HEAD
                "open_now": params.open_now,
                "price": params.price,
=======
                "price": params.price,
                "categories": params.categories
>>>>>>> origin
            }
            
            # Remove None values
            search_params = {k: v for k, v in search_params.items() if v is not None}
            
<<<<<<< HEAD
            print(f"Search params: {search_params}")  # Debug log
            print(f"Headers: {self.headers}")  # Debug log
=======
            logger.info(f"Search params: {search_params}")  # Debug log
            logger.info(f"Headers: {self.headers}")  # Debug log
>>>>>>> origin
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/businesses/search",
                    headers=self.headers,
                    params=search_params,
                )
                
                if response.status_code != 200:
<<<<<<< HEAD
                    print(f"Response status: {response.status_code}")
                    print(f"Response text: {response.text}")
=======
                    logger.error(f"Response status: {response.status_code}")
                    logger.error(f"Response text: {response.text}")
>>>>>>> origin
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
<<<<<<< HEAD
            print(f" Error: {str(e)}")
            print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
            raise
        except Exception as e:
            print(f" Unexpected error: {str(e)}")
=======
            logger.error(f" Error: {str(e)}")
            logger.error(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
            raise
        except Exception as e:
            logger.error(f" Unexpected error: {str(e)}")
>>>>>>> origin
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
<<<<<<< HEAD
=======

# Import models at the bottom
from ..models.base import Restaurant, SearchParams, Location, Coordinates, Category
>>>>>>> origin
