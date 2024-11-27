import os
from typing import Dict, List, Optional, Any
<<<<<<< HEAD
from dotenv import load_dotenv
from supabase import create_client, Client
=======
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)
>>>>>>> origin

class SupabaseClient:
    RESTAURANTS_TABLE_NAME = 'restaurants'
    OPERATING_HOURS_TABLE_NAME = 'operating_hours' 

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
<<<<<<< HEAD
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
=======
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
>>>>>>> origin
            
    def get_restaurants(self, limit: Optional[int] = None) -> List[Dict]:
        """Get restaurants from Supabase."""
        try:
<<<<<<< HEAD
            print("\n🔍 Fetching restaurants from Supabase...")
            query = self.client.table(self.RESTAURANTS_TABLE_NAME).select("*")
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
=======
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
>>>>>>> origin
            
    def get_all_restaurants(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all restaurants from the database."""
        try:
<<<<<<< HEAD
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
=======
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
>>>>>>> origin
            
    def update_restaurant(self, business_id: str, data: Dict) -> bool:
        """Update a restaurant's information."""
        try:
<<<<<<< HEAD
            print(f"🔄 Updating restaurant with ID: {business_id}")
            self.client.table(self.RESTAURANTS_TABLE_NAME).update(data).eq('business_id', business_id).execute()
            print("✅ Restaurant updated successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to update restaurant: {str(e)}")
            return False
=======
            logger.info(f"🔄 Updating restaurant with ID: {business_id}")
            self.client.table(self.RESTAURANTS_TABLE_NAME).update(data).eq('business_id', business_id).execute()
            logger.info("✅ Restaurant updated successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update restaurant: {str(e)}", exc_info=True)
            raise
>>>>>>> origin
            
    def delete_restaurant(self, business_id: str) -> bool:
        """Delete a restaurant."""
        try:
<<<<<<< HEAD
            print(f"🚮 Deleting restaurant with ID: {business_id}")
            self.client.table(self.RESTAURANTS_TABLE_NAME).delete().eq('business_id', business_id).execute()
            print("✅ Restaurant deleted successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to delete restaurant: {str(e)}")
            return False
=======
            logger.info(f"🚮 Deleting restaurant with ID: {business_id}")
            self.client.table(self.RESTAURANTS_TABLE_NAME).delete().eq('business_id', business_id).execute()
            logger.info("✅ Restaurant deleted successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete restaurant: {str(e)}", exc_info=True)
            raise
>>>>>>> origin
            
    def bulk_upsert_restaurants(self, restaurants: List[Dict]) -> bool:
        """Bulk upsert restaurants."""
        try:
<<<<<<< HEAD
            print(f"💾 Bulk upserting {len(restaurants)} restaurants")
            self.client.table(self.RESTAURANTS_TABLE_NAME).upsert(restaurants).execute()
            print("✅ Restaurants bulk upserted successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to bulk upsert restaurants: {str(e)}")
            return False

    def get_restaurants_without_hours(self) -> List[Dict[str, Any]]:
=======
            logger.info(f"💾 Bulk upserting {len(restaurants)} restaurants")
            self.client.table(self.RESTAURANTS_TABLE_NAME).upsert(restaurants).execute()
            logger.info("✅ Restaurants bulk upserted successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to bulk upsert restaurants: {str(e)}", exc_info=True)
            raise

    def get_restaurants_without_hours(self) -> List[Dict]:
>>>>>>> origin
        try:

            # if restuaraut's business_id doesnt exist in operating_hours table as restaurant_id 
            # then add to queue in order of oldest creation time first
<<<<<<< HEAD
            print("🔍 Fetching restaurants without hours from Supabase...")

            query = self.client.table(self.RESTAURANTS_TABLE_NAME).select("*").eq('is_hours_verified', False).order('created_at')
            response = query.execute()
            print("🚀 Executing query...")
            print(f"✅ Found {len(response.data)} restaurants without hours")
            return response.data
        except Exception as e:
            print(f"❌ Error fetching restaurants without hours: {str(e)}")
=======
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
            logger.info(f"🔍 Searching restaurants with term='{term}' location='{location}'")
            
            # Start with a base query
            query = self.client.table(self.RESTAURANTS_TABLE_NAME)
            
            # Build the select query with filters
            select_query = "*"
            
            # Add filters
            filters = []
            if term:
                filters.append(f"name.ilike.%{term}%")
            if location:
                filters.append(f"location->>'city'.ilike.%{location}%")
            if price:
                filters.append(f"price.eq.{price}")
            
            # Execute query with filters
            if filters:
                query = query.select(select_query).or_(",".join(filters))
            else:
                query = query.select(select_query)
            
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
        categories: Optional[str] = None
    ) -> List[Dict]:
        """Search for restaurants in Supabase."""
        try:
            logger.info(f"\n🔍 Searching restaurants with term='{term}' location='{location}'")
            
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
            
            logger.info(f"✅ Found {len(response.data)} restaurants")
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Failed to search restaurants: {str(e)}", exc_info=True)
            raise
>>>>>>> origin
