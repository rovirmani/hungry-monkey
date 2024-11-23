from typing import List, Optional, Dict, Any
from app.clients.supabase import SupabaseClient
from app.clients.yelp import YelpClient
from app.models import Restaurant, SearchParams

class RestaurantDB:
    def __init__(self):
        self.supabase = SupabaseClient()
        self.yelp = YelpClient()

    async def create_restaurant(self, restaurant: Restaurant) -> Dict[str, Any]:
        """Create a new restaurant record."""
        try:
            data = restaurant.model_dump()
            self.supabase.store_restaurant(data)
            return data
        except Exception as e:
            raise Exception(f"Failed to create restaurant: {str(e)}")

    async def get_restaurant(self, business_id: str) -> Optional[Restaurant]:
        """Get a restaurant, first from cache then Yelp."""
        try:
            # Try cache first
            cached = self.supabase.get_restaurant(business_id)
            if cached:
                return Restaurant(**cached)

            # If not in cache, get from Yelp
            restaurant = await self.yelp.get_business_details(business_id)
            if restaurant:
                # Cache it
                self.supabase.store_restaurant(restaurant.model_dump())
                return restaurant

            return None
        except Exception as e:
            raise Exception(f"Failed to get restaurant: {str(e)}")

    async def search_restaurants(self, params: SearchParams) -> List[Restaurant]:
        """Search restaurants from Yelp and cache them."""
        try:
            # Get fresh results from Yelp
            restaurants = await self.yelp.search_restaurants(params)
            
            # Cache them in Supabase
            for restaurant in restaurants:
                data = restaurant.model_dump()
                self.supabase.store_restaurant(data)
                
            return restaurants
        except Exception as e:
            raise Exception(f"Failed to search restaurants: {str(e)}")

    async def update_restaurant(self, business_id: str, data: Dict[str, Any]) -> Optional[Restaurant]:
        """Update a restaurant's information."""
        try:
            self.supabase.update_restaurant(business_id, data)
            return Restaurant(**data)
        except Exception as e:
            raise Exception(f"Failed to update restaurant: {str(e)}")

    def delete_restaurant(self, business_id: str) -> bool:
        """Delete a restaurant."""
        try:
            self.supabase.delete_restaurant(business_id)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete restaurant: {str(e)}")

    def bulk_upsert_restaurants(self, restaurants: List[Restaurant]) -> List[Dict[str, Any]]:
        """Bulk upsert restaurants (insert or update based on business_id)."""
        try:
            data = [rest.model_dump() for rest in restaurants]
            self.supabase.bulk_upsert_restaurants(data)
            return data
        except Exception as e:
            raise Exception(f"Failed to bulk upsert restaurants: {str(e)}")

    async def search_by_phone(self, phone: str) -> List[Restaurant]:
        """Search restaurants by phone number."""
        return await self.yelp.search_by_phone(phone)

    def get_cached_restaurants(self, limit: Optional[int] = None) -> List[Restaurant]:
        """Get restaurants from cache only."""
        try:
            results = self.supabase.get_restaurants(limit)
            return [Restaurant(**r) for r in results]
        except Exception as e:
            raise Exception(f"Failed to get cached restaurants: {str(e)}")
