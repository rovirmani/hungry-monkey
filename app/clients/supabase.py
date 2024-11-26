import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from supabase import create_client, Client

class SupabaseClient:
    RESTAURANTS_TABLE_NAME = 'restaurants'
    OPERATING_HOURS_TABLE_NAME = 'operating_hours' 

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
            self.client.table(self.RESTAURANTS_TABLE_NAME).upsert(restaurant_data).execute()
            print("✅ Restaurant stored successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to store restaurant: {str(e)}")
            return False
            
    def get_restaurant(self, business_id: str) -> Optional[Dict]:
        """Get a restaurant by business ID."""
        try:
            print(f"🔍 Getting restaurant with ID: {business_id}")
            response = self.client.table(self.RESTAURANTS_TABLE_NAME).select("*").eq('business_id', business_id).execute()
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
            query = self.client.table(self.RESTAURANTS_TABLE_NAME).select("*")
            if limit:
                query = query.limit(limit)
            response = query.execute()  
            print(f"✅ Found {len(response.data)} restaurants")
            return response.data
        except Exception as e:
            print(f"❌ Failed to get restaurants: {str(e)}")
            return []
            
    def get_all_restaurants(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all restaurants from the database."""
        try:
            print("🔍 Fetching restaurants from Supabase...")
            query = self.client.table('restaurants').select('*')
            if limit:
                print(f"📊 Limiting to {limit} results")
                query = query.limit(limit)
            print("🚀 Executing query...")
            response = query.execute()
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
            self.client.table(self.RESTAURANTS_TABLE_NAME).update(data).eq('business_id', business_id).execute()
            print("✅ Restaurant updated successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to update restaurant: {str(e)}")
            return False
            
    def delete_restaurant(self, business_id: str) -> bool:
        """Delete a restaurant."""
        try:
            print(f"🚮 Deleting restaurant with ID: {business_id}")
            self.client.table(self.RESTAURANTS_TABLE_NAME).delete().eq('business_id', business_id).execute()
            print("✅ Restaurant deleted successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to delete restaurant: {str(e)}")
            return False
            
    def bulk_upsert_restaurants(self, restaurants: List[Dict]) -> bool:
        """Bulk upsert restaurants."""
        try:
            print(f"💾 Bulk upserting {len(restaurants)} restaurants")
            self.client.table(self.RESTAURANTS_TABLE_NAME).upsert(restaurants).execute()
            print("✅ Restaurants bulk upserted successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to bulk upsert restaurants: {str(e)}")
            return False

    def get_restaurants_without_hours(self) -> List[Dict[str, Any]]:
        try:

            # if restuaraut's business_id doesnt exist in operating_hours table as restaurant_id 
            # then add to queue in order of oldest creation time first
            print("🔍 Fetching restaurants without hours from Supabase...")

            query = self.client.table(self.RESTAURANTS_TABLE_NAME).select("*").eq('is_hours_verified', False).order('created_at')
            response = query.execute()
            print("🚀 Executing query...")
            print(f"✅ Found {len(response.data)} restaurants without hours")
            return response.data
        except Exception as e:
            print(f"❌ Error fetching restaurants without hours: {str(e)}")

    def search_restaurants(self, term: Optional[str] = None, location: Optional[str] = None, 
                         price: Optional[str] = None, categories: Optional[List[str]] = None) -> List[Dict]:
        """Search restaurants in Supabase."""
        try:
            print(f"\n🔍 Searching restaurants with term: {term}, location: {location}")
            query = self.client.table(self.RESTAURANTS_TABLE_NAME).select("*")
            
            # Build filters
            if term:
                query = query.ilike("name", f"%{term}%")
            
            if location:
                # Search in city field
                query = query.filter("location->>city", "ilike", f"%{location}%")
                
            if price:
                query = query.eq("price", price)
                
            if categories and len(categories) > 0:
                query = query.contains("categories", categories)
            
            print("🚀 Executing query...")
            response = query.execute()
            print(f"✅ Found {len(response.data)} restaurants")
            return response.data
            
        except Exception as e:
            print(f"❌ Failed to search restaurants: {str(e)}")
            return []
            
    async def search_restaurants_async(
        self,
        term: Optional[str] = None,
        location: Optional[str] = None,
        price: Optional[str] = None,
        categories: Optional[str] = None
    ) -> List[Dict]:
        """Search for restaurants in Supabase."""
        try:
            print(f"\n🔍 Searching restaurants with term='{term}' location='{location}'")
            
            # Build query conditions
            conditions = []
            if location:
                conditions.append(f"location.ilike.%{location}%")
            if term:
                conditions.append(f"name.ilike.%{term}%")
                conditions.append(f"categories.ilike.%{term}%")
            if price:
                conditions.append(f"price.eq.{price}")
            if categories:
                conditions.append(f"categories.ilike.%{categories}%")
                
            # Execute query with OR conditions for term
            query_str = ",".join(conditions)
            response = await self.client.table(self.RESTAURANTS_TABLE_NAME).select("*").or_(query_str).execute()
            
            print(f"✅ Found {len(response.data)} restaurants")
            return response.data
            
        except Exception as e:
            print(f"❌ Failed to search restaurants: {str(e)}")
            return []
