import os
from typing import Dict, List, Optional, Any
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root directory
root_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(root_dir / '.env')

from app.models import (
    Restaurant, SearchParams, Review, 
    AutocompleteParams
)

class YelpClient:
    def __init__(self):
        self.api_key = os.getenv("YELP_API_KEY")
        if not self.api_key:
            raise ValueError("YELP_API_KEY not found in .env file")
            
        self.base_url = "https://api.yelp.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "accept": "application/json"
        }
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the Yelp API"""
        url = f"{self.base_url}{endpoint}"
        print(f"Making request to: {url}")  # Debug logging
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()

    async def search_restaurants(self, params: SearchParams) -> List[Restaurant]:
        """Search for restaurants using the Yelp Fusion API"""
        # Convert params to dictionary and remove None values
        query_params = params.model_dump(exclude_none=True)
        
        data = await self._make_request("/businesses/search", query_params)
        return [Restaurant.model_validate(business) for business in data["businesses"]]

    async def get_restaurant_by_id(self, business_id: str) -> Restaurant:
        """Get detailed information about a specific restaurant"""
        data = await self._make_request(f"/businesses/{business_id}")
        return Restaurant.model_validate(data)

    async def get_restaurant_reviews(
        self, 
        business_id: str, 
        locale: str = "en_US",
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: str = "yelp_sort"
    ) -> List[Review]:
        """
        Get review excerpts for a restaurant (REQUIRES PAID API PLAN)
        
        Note: This functionality requires Yelp Fusion Plus or Enterprise Plan.
        Visit https://fusion.yelp.com to upgrade your plan.
        
        Args:
            business_id: Business ID or alias from Yelp
            locale: Locale code (e.g., 'en_US')
            offset: Offset for pagination (0 to 1000)
            limit: Number of reviews to return (0 to 50, default 20)
            sort_by: Sort order for reviews (default: yelp_sort)
        """
        raise NotImplementedError(
            "Reviews endpoint requires Yelp Fusion Plus or Enterprise Plan. "
            "Visit https://fusion.yelp.com to upgrade your plan."
        )

    async def search_by_phone(self, phone: str) -> List[Restaurant]:
        """Search for restaurants by phone number"""
        data = await self._make_request("/businesses/search/phone", {"phone": phone})
        return [Restaurant.model_validate(business) for business in data["businesses"]]

    async def get_autocomplete(self, params: AutocompleteParams) -> Dict[str, Any]:
        """Get autocomplete suggestions for search text"""
        query_params = params.model_dump(exclude_none=True)
        return await self._make_request("/autocomplete", query_params)

    async def search_transaction(self, transaction_type: str, latitude: float, longitude: float) -> List[Restaurant]:
        """Search for restaurants that support a specific transaction type (e.g., 'delivery')"""
        params = {
            "latitude": latitude,
            "longitude": longitude
        }
        data = await self._make_request(f"/transactions/{transaction_type}/search", params)
        return [Restaurant.model_validate(business) for business in data["businesses"]]
