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
            # Supabase-py doesn't support async operations yet, so we use sync methods
            data = self.client.table('restaurants').upsert(restaurant_data).execute()
            return True
        except Exception as e:
            print(f"Failed to store restaurant: {str(e)}")
            return False
            
    def get_restaurants(self, limit: Optional[int] = None) -> List[Dict]:
        """Get restaurants from Supabase."""
        try:
            # Supabase-py doesn't support async operations yet, so we use sync methods
            query = self.client.table('restaurants').select("*")
            if limit:
                query = query.limit(limit)
            data = query.execute()
            return data.data
        except Exception as e:
            print(f"Failed to get restaurants: {str(e)}")
            return []
