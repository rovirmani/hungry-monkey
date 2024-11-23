from typing import List, Optional, Dict, Any
from app.clients.supabase import SupabaseClient
from app.models import Restaurant, SearchParams

class RestaurantDB:
    def __init__(self):
        self.supabase = SupabaseClient()

    async def create_restaurant(self, restaurant: Restaurant) -> Dict[str, Any]:
        """Create a new restaurant record."""
        try:
            data = restaurant.model_dump()
            response = await self.supabase.client.table('restaurants').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Failed to create restaurant: {str(e)}")

    async def get_restaurant(self, business_id: str) -> Optional[Restaurant]:
        """Get a restaurant by its business ID."""
        try:
            response = await self.supabase.client.table('restaurants').select("*").eq('business_id', business_id).execute()
            if response.data:
                return Restaurant(**response.data[0])
            return None
        except Exception as e:
            raise Exception(f"Failed to get restaurant: {str(e)}")

    async def search_restaurants(self, params: SearchParams) -> List[Restaurant]:
        """Search restaurants with filters."""
        try:
            query = self.supabase.client.table('restaurants').select("*")

            # Apply filters based on search parameters
            if params.term:
                query = query.ilike('name', f'%{params.term}%')
            if params.location:
                query = query.ilike('location', f'%{params.location}%')
            if params.price:
                query = query.eq('price', params.price)
            if params.open_now:
                query = query.eq('is_open', True)
            if params.sort_by:
                query = query.order(params.sort_by, desc=True)

            response = await query.execute()
            return [Restaurant(**item) for item in response.data]
        except Exception as e:
            raise Exception(f"Failed to search restaurants: {str(e)}")

    async def update_restaurant(self, business_id: str, data: Dict[str, Any]) -> Optional[Restaurant]:
        """Update a restaurant's information."""
        try:
            response = await self.supabase.client.table('restaurants').update(data).eq('business_id', business_id).execute()
            if response.data:
                return Restaurant(**response.data[0])
            return None
        except Exception as e:
            raise Exception(f"Failed to update restaurant: {str(e)}")

    async def delete_restaurant(self, business_id: str) -> bool:
        """Delete a restaurant."""
        try:
            response = await self.supabase.client.table('restaurants').delete().eq('business_id', business_id).execute()
            return bool(response.data)
        except Exception as e:
            raise Exception(f"Failed to delete restaurant: {str(e)}")

    async def bulk_upsert_restaurants(self, restaurants: List[Restaurant]) -> List[Dict[str, Any]]:
        """Bulk upsert restaurants (insert or update based on business_id)."""
        try:
            data = [rest.model_dump() for rest in restaurants]
            response = await self.supabase.client.table('restaurants').upsert(data).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to bulk upsert restaurants: {str(e)}")
