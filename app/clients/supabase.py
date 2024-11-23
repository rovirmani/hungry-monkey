import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

class SupabaseClient:
    def __init__(self):
        load_dotenv()
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
            
        self.client = create_client(self.supabase_url, self.supabase_key)
        
    def store_restaurant(self, restaurant_data: Dict) -> bool:
        """Store a restaurant in Supabase."""
        try:
            self.client.table('restaurants').upsert(restaurant_data).execute()
            return True
        except Exception as e:
            print(f"Failed to store restaurant: {str(e)}")
            return False
            
    def get_restaurant(self, business_id: str) -> Optional[Dict]:
        """Get a restaurant by business ID."""
        try:
            response = self.client.table('restaurants').select("*").eq('business_id', business_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Failed to get restaurant: {str(e)}")
            return None
            
    def get_restaurants(self, limit: Optional[int] = None) -> List[Dict]:
        """Get restaurants from Supabase."""
        try:
            query = self.client.table('restaurants').select("*")
            if limit:
                query = query.limit(limit)
            data = query.execute()
            return data.data
        except Exception as e:
            print(f"Failed to get restaurants: {str(e)}")
            return []
            
    def update_restaurant(self, business_id: str, data: Dict) -> bool:
        """Update a restaurant's information."""
        try:
            self.client.table('restaurants').update(data).eq('business_id', business_id).execute()
            return True
        except Exception as e:
            print(f"Failed to update restaurant: {str(e)}")
            return False
            
    def delete_restaurant(self, business_id: str) -> bool:
        """Delete a restaurant."""
        try:
            self.client.table('restaurants').delete().eq('business_id', business_id).execute()
            return True
        except Exception as e:
            print(f"Failed to delete restaurant: {str(e)}")
            return False
            
    def bulk_upsert_restaurants(self, restaurants: List[Dict]) -> bool:
        """Bulk upsert restaurants."""
        try:
            self.client.table('restaurants').upsert(restaurants).execute()
            return True
        except Exception as e:
            print(f"Failed to bulk upsert restaurants: {str(e)}")
            return False
