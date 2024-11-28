import os
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    RESTAURANTS_TABLE_NAME = 'restaurants'
    OPERATING_HOURS_TABLE_NAME = 'operating_hours' 

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Log environment state (without exposing sensitive values)
        logger.info("🔧 Supabase Configuration:", extra={
            "has_url": bool(self.supabase_url),
            "has_key": bool(self.supabase_key),
            "url_prefix": self.supabase_url[:20] + "..." if self.supabase_url else None
        })
        
        if not self.supabase_url or not self.supabase_key:
            error_msg = "Missing Supabase configuration. Ensure SUPABASE_URL and SUPABASE_KEY are set in environment variables."
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
            
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info(f"✅ Connected to Supabase")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {str(e)}", exc_info=True)
            raise
        
    def store_restaurant(self, restaurant_data: Dict) -> bool:
        """Store a restaurant in Supabase."""
        try:
            logger.info(f"💾 Storing restaurant: {restaurant_data.get('name', 'Unknown')}")
            self.client.table(self.RESTAURANTS_TABLE_NAME).upsert(restaurant_data).execute()
            logger.info("✅ Restaurant stored successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store restaurant: {str(e)}", exc_info=True)
            raise
            
    def get_restaurant(self, business_id: str) -> Optional[Dict]:
        """Get a restaurant by business ID."""
        try:
            logger.info(f"🔍 Getting restaurant with ID: {business_id}")
            response = self.client.table(self.RESTAURANTS_TABLE_NAME).select("*").eq('business_id', business_id).execute()
            if response.data:
                logger.info("✅ Found restaurant")
            else:
                logger.warning("⚠️ Restaurant not found")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"❌ Failed to get restaurant: {str(e)}", exc_info=True)
            raise
            
    def get_restaurants(self, limit: Optional[int] = None) -> List[Dict]:
        """Get restaurants from Supabase."""
        try:
            logger.info(f"🔍 Fetching restaurants from Supabase (limit={limit})")
            query = self.client.table(self.RESTAURANTS_TABLE_NAME).select("*")
            if limit:
                query = query.limit(limit)
            response = query.execute()
            logger.info(f"✅ Found {len(response.data)} restaurants")
            return response.data
        except Exception as e:
            logger.error(f"❌ Failed to get restaurants: {str(e)}", exc_info=True)
            raise
            
    def get_all_restaurants(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all restaurants from the database."""
        try:
            logger.info("🔍 Fetching restaurants from Supabase...")
            query = self.client.table('restaurants').select('*')
            if limit:
                logger.info(f"📊 Limiting to {limit} results")
                query = query.limit(limit)
            logger.info("🚀 Executing query...")
            response = query.execute()
            restaurants = response.data
            logger.info(f"✅ Found {len(restaurants)} restaurants")
            if restaurants:
                logger.info("📝 Example restaurant:", restaurants[0])
            return restaurants
        except Exception as e:
            logger.error(f"❌ Error fetching restaurants: {str(e)}", exc_info=True)
            raise
            
    def update_restaurant(self, business_id: str, data: Dict) -> bool:
        """Update a restaurant's information."""
        try:
            logger.info(f"🔄 Updating restaurant with ID: {business_id}")
            self.client.table(self.RESTAURANTS_TABLE_NAME).update(data).eq('business_id', business_id).execute()
            logger.info("✅ Restaurant updated successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update restaurant: {str(e)}", exc_info=True)
            raise
            
    def delete_restaurant(self, business_id: str) -> bool:
        """Delete a restaurant."""
        try:
            logger.info(f"🚮 Deleting restaurant with ID: {business_id}")
            self.client.table(self.RESTAURANTS_TABLE_NAME).delete().eq('business_id', business_id).execute()
            logger.info("✅ Restaurant deleted successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete restaurant: {str(e)}", exc_info=True)
            raise
            
    def bulk_upsert_restaurants(self, restaurants: List[Dict]) -> bool:
        """Bulk upsert restaurants."""
        try:
            logger.info(f"💾 Bulk upserting {len(restaurants)} restaurants")
            self.client.table(self.RESTAURANTS_TABLE_NAME).upsert(restaurants).execute()
            logger.info("✅ Restaurants bulk upserted successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to bulk upsert restaurants: {str(e)}", exc_info=True)
            raise

    def get_restaurants_without_hours(self) -> List[Dict]:
        try:

            # if restuaraut's business_id doesnt exist in operating_hours table as restaurant_id 
            # then add to queue in order of oldest creation time first
            logger.info("🔍 Fetching restaurants without hours from Supabase...")

            query = self.client.table(self.RESTAURANTS_TABLE_NAME).select("*").eq('is_hours_verified', False).order('created_at')
            response = query.execute()
            logger.info("🚀 Executing query...")
            logger.info(f"✅ Found {len(response.data)} restaurants without hours")
            return response.data
        except Exception as e:
            logger.error(f"❌ Error fetching restaurants without hours: {str(e)}", exc_info=True)
            raise

    def search_restaurants(
        self,
        term: Optional[str] = None,
        location: Optional[str] = None,
        price: Optional[str] = None,
        categories: Optional[List[str]] = None
    ) -> List[Dict]:
        """Search restaurants in Supabase."""
        try:
            logger.info(f"🔍 Searching restaurants with term='{term}' location='{location}' categories={categories}")
            
            # Start with a base query
            query = self.client.table(self.RESTAURANTS_TABLE_NAME).select("*")
            
            # Add filters one by one
            if term:
                # Search in both name and categories using OR
                query = query.ilike("name", f"%{term}%")
            if location:
                query = query.ilike("location->>city", f"%{location}%")
            if price:
                query = query.eq("price", price)
            if categories and len(categories) > 0:
                query = query.eq("business_type", categories[0])
            
            logger.info("🚀 Executing query...")
            response = query.execute()
            logger.info(f"✅ Found {len(response.data)} restaurants")
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Failed to search restaurants: {str(e)}", exc_info=True)
            raise Exception(f"Failed to search restaurants: {str(e)}")
            
    async def search_restaurants_async(
        self,
        term: Optional[str] = None,
        location: Optional[str] = None,
        price: Optional[str] = None,
        categories: Optional[List[str]] = None
    ) -> List[Dict]:
        """Search for restaurants in Supabase."""
        try:
            logger.info(f"\n🔍 Searching restaurants with term='{term}' location='{location}' categories={categories}")
            
            # Start with base query
            query = self.client.table(self.RESTAURANTS_TABLE_NAME).select("*")
            
            # Add filters one by one
            if term:
                # Search in both name and categories using OR
                query = query.ilike("name", f"%{term}%").or_("categories.ilike.%{term}%")
            if location:
                query = query.ilike("location->>city", f"%{location}%")
            if price:
                query = query.eq("price", price)
            if categories and len(categories) > 0:
                query = query.eq("business_type", categories[0])
            
            logger.info("🚀 Executing query...")
            response = await query.execute()
            logger.info(f"✅ Found {len(response.data)} restaurants")
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Failed to search restaurants: {str(e)}", exc_info=True)
            raise
