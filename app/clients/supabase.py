from typing import Optional, Dict, Any
from supabase import create_client, Client
import os
from dotenv import load_dotenv

class SupabaseClient:
    def __init__(self):
        load_dotenv()
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    async def store_restaurant_data(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store restaurant data in Supabase."""
        try:
            response = await self.client.table('restaurants').insert(restaurant_data).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to store restaurant data: {str(e)}")

    async def get_restaurant_by_id(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve restaurant data by ID."""
        try:
            response = await self.client.table('restaurants').select("*").eq('id', restaurant_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Failed to retrieve restaurant: {str(e)}")

    async def update_restaurant_stats(self, restaurant_id: str, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Update restaurant statistics."""
        try:
            response = await self.client.table('restaurants').update(stats).eq('id', restaurant_id).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to update restaurant stats: {str(e)}")
