from typing import List, Optional
from app.clients.yelp import YelpClient
from app.db.restaurants import RestaurantDB
from app.models import Restaurant, SearchParams

class RestaurantService:
    def __init__(self):
        self.yelp_client = YelpClient()
        self.db = RestaurantDB()

    async def search_restaurants(self, params: SearchParams) -> List[Restaurant]:
        """
        Search restaurants using Yelp API and cache results in Supabase.
        """
        # First, search Yelp
        yelp_results = await self.yelp_client.search_restaurants(params)
        
        # Cache results in database
        await self.db.bulk_upsert_restaurants(yelp_results)
        
        return yelp_results

    async def get_restaurant_details(self, business_id: str) -> Optional[Restaurant]:
        """
        Get restaurant details, first checking cache then Yelp API.
        """
        # Try to get from cache first
        cached_restaurant = await self.db.get_restaurant(business_id)
        if cached_restaurant:
            return cached_restaurant

        # If not in cache, get from Yelp and cache it
        yelp_restaurant = await self.yelp_client.get_business_details(business_id)
        if yelp_restaurant:
            await self.db.create_restaurant(yelp_restaurant)
            return yelp_restaurant

        return None

    async def update_restaurant_cache(self, business_id: str) -> Optional[Restaurant]:
        """
        Force update restaurant details from Yelp API to cache.
        """
        yelp_restaurant = await self.yelp_client.get_business_details(business_id)
        if yelp_restaurant:
            await self.db.update_restaurant(business_id, yelp_restaurant.model_dump())
            return yelp_restaurant
        return None
