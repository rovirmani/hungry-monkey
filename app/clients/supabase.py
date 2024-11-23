import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from supabase import create_client, Client

class SupabaseClient:
    TABLE_NAME = 'restaurants'  # Define table name as a class constant
    
    def __init__(self):
        load_dotenv()
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
            
        self.client = create_client(self.supabase_url, self.supabase_key)
        print(f"🔌 Connected to Supabase at {self.supabase_url}")
        
    def store_restaurant(self, restaurant_data: Dict) -> bool:
        """Store a restaurant in Supabase."""
        try:
            print(f"💾 Storing restaurant: {restaurant_data.get('name', 'Unknown')}")
            self.client.table(self.TABLE_NAME).upsert(restaurant_data).execute()
            print("✅ Restaurant stored successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to store restaurant: {str(e)}")
            return False
            
    def get_restaurant(self, business_id: str) -> Optional[Dict]:
        """Get a restaurant by business ID."""
        try:
            print(f"🔍 Getting restaurant with ID: {business_id}")
            response = self.client.table(self.TABLE_NAME).select("*").eq('business_id', business_id).execute()
            if response.data:
                print("✅ Found restaurant")
            else:
                print("⚠️ Restaurant not found")
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Failed to get restaurant: {str(e)}")
            return None
            
    def get_restaurants(self, limit: Optional[int] = None) -> List[Dict]:
        """Get restaurants from Supabase."""
        try:
            print("\n🔍 Fetching restaurants from Supabase...")
            query = self.client.table(self.TABLE_NAME).select("*")
            if limit:
                print(f"📊 Limiting to {limit} results")
                query = query.limit(limit)
            print("🚀 Executing query...")    
            response = query.execute()
            
            if not response.data:
                print("⚠️ No restaurants found in Supabase")
                return []
                
            print(f"✅ Found {len(response.data)} restaurants")
            # Print first restaurant as example
            if response.data:
                print(f"📝 Example restaurant: {response.data[0]}")
            return response.data
        except Exception as e:
            print(f"❌ Error getting restaurants: {str(e)}")
            print(f"❌ Error type: {type(e)}")
            return []
            
    def get_all_restaurants(self) -> List[Dict[str, Any]]:
        """Get all restaurants from the database."""
        try:
            print("🔍 Fetching restaurants from Supabase...")
            print("🚀 Executing query...")
            response = self.client.table('restaurants').select('*').execute()
            restaurants = response.data
            print(f"✅ Found {len(restaurants)} restaurants")
            if restaurants:
                print("📝 Example restaurant:", restaurants[0])
            return restaurants
        except Exception as e:
            print(f"❌ Error fetching restaurants: {str(e)}")
            return []
            
    def update_restaurant(self, business_id: str, data: Dict) -> bool:
        """Update a restaurant's information."""
        try:
            print(f"🔄 Updating restaurant with ID: {business_id}")
            self.client.table(self.TABLE_NAME).update(data).eq('business_id', business_id).execute()
            print("✅ Restaurant updated successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to update restaurant: {str(e)}")
            return False
            
    def delete_restaurant(self, business_id: str) -> bool:
        """Delete a restaurant."""
        try:
            print(f"🚮 Deleting restaurant with ID: {business_id}")
            self.client.table(self.TABLE_NAME).delete().eq('business_id', business_id).execute()
            print("✅ Restaurant deleted successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to delete restaurant: {str(e)}")
            return False
            
    def bulk_upsert_restaurants(self, restaurants: List[Dict]) -> bool:
        """Bulk upsert restaurants."""
        try:
            print(f"💾 Bulk upserting {len(restaurants)} restaurants")
            self.client.table(self.TABLE_NAME).upsert(restaurants).execute()
            print("✅ Restaurants bulk upserted successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to bulk upsert restaurants: {str(e)}")
            return False
