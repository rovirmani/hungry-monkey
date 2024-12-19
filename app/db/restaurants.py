from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.clients.yelp import YelpClient
from app.models import Restaurant, SearchParams
from supabase import create_client

from ..utils.constants import (
    OPERATING_HOURS_TABLE_NAME,
    RESTAURANTS_TABLE_NAME,
    SUPABASE_KEY,
    SUPABASE_URL,
)
from ..utils.decorators import handle_exceptions

logger = logging.getLogger(__name__)

class RestaurantDB:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ RestaurantDB initialized")

    def get_all_restaurants(self, limit: Optional[int] = None) -> List[Dict]:
        """get stored restaurants from Supabase"""
        try:
            query = self.supabase.table(RESTAURANTS_TABLE_NAME).select("*")
            if limit:
                query = query.limit(limit)
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"❌ Failed to get restaurants: {str(e)}", exc_info=True)
            raise

    async def create_restaurant(self, restaurant: Restaurant) -> Dict[str, Any]:
        """Create a new restaurant record."""
        try:
            data = restaurant.model_dump()
            response = self.supabase.table(RESTAURANTS_TABLE_NAME).select("*").eq('business_id', restaurant.business_id).execute()
            if response.data:
                return response.data[0]
            else:
                return None
        except Exception as e:
            logger.error(f"❌ Failed to create restaurant: {str(e)}", exc_info=True)
            raise

    async def find_restaurant(self, business_id: str) -> Optional[Restaurant]:
        """Get a restaurant from the restaurant table."""
        try:
            response = self.supabase.table(RESTAURANTS_TABLE_NAME).select("*").eq('business_id', business_id).execute()
            if response.data:
                return Restaurant(**response.data[0])
            raise Exception(f"Restaurant {business_id} not found")
        except Exception as e:
            logger.error(f"Failed to get restaurant {business_id}: {str(e)}", exc_info=True)
            raise

    async def search_restaurants(self, params: SearchParams, hours_filter: Optional[str] = None) -> List[Restaurant]:
        """
        Search the restaurant table with the given query filters.
        Args:
            params: Search parameters for filtering restaurants
            hours_filter: Optional filter for hours verification status
                        'verified' - only restaurants with verified hours
                        'unverified' - only restaurants with unverified hours
                        None - all restaurants
        """
        logger.info(f"🔍 Searching restaurants with term='{params.term}' location='{params.location}' categories={params.categories} hours_filter={hours_filter}")
        try:
            query = self._generate_search_query(params)
            if hours_filter == 'verified':
                query = query.eq('is_hours_verified', True)
            elif hours_filter == 'unverified':
                query = query.eq('is_hours_verified', False)
            
            response = query.execute()
            return [Restaurant(**r) for r in response.data]
        except Exception as e:
            logger.error(f"Failed to search restaurants: {str(e)}", exc_info=True)
            raise

    async def update_restaurant(self, business_id: str, data: Dict[str, Any]) -> None:
        """Update a restaurant's information."""
        try:
            self.supabase.update_restaurant(business_id, data)
        except Exception as e:
            logger.error(f"Failed to update restaurant {business_id}: {str(e)}", exc_info=True)
            raise
    

    def get_restaurants_without_hours(self) -> List[Dict[str, Any]]:
        """Returns: List of restaurant dicts for restaurants whose hours have not been verified."""
        try:
            query = self.supabase.table(RESTAURANTS_TABLE_NAME).select("*").eq('is_hours_verified', False).eq("is_closed", False).order('created_at')
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get restaurants without hours: {str(e)}", exc_info=True)
            raise

    def get_restaurants_with_hours(self) -> List[Dict[str, Any]]:
        """Returns: List of restaurant dicts for restaurants whose hours have been verified."""
        try:
            query = self.supabase.table(RESTAURANTS_TABLE_NAME).select("*").eq('is_hours_verified', True).eq("is_closed", False).order('created_at')
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get restaurants with hours: {str(e)}", exc_info=True)
            raise

    def _generate_search_query(self, params: SearchParams) -> str:
        """Generate a search query based on the given parameters. Match by location and category."""
        query = self.supabase.table(RESTAURANTS_TABLE_NAME).select("*")
        logger.info(f"🔍  Search query: term='{params.term}', categories={params.categories}")
        if params.location:
            query = query.ilike("location->>city", f"%{params.location}%")
        if params.categories and len(params.categories) > 0:
            query = query.eq("business_type", params.categories[0])
        return query

restaurant_db = RestaurantDB()
