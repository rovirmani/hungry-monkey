import os
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import logging
from constants import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)
client = None
class SupabaseClient:
    RESTAURANTS_TABLE_NAME = 'restaurants'
    OPERATING_HOURS_TABLE_NAME = 'operating_hours' 

    def __init__(self):
        
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
