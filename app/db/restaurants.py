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

    def get_restaurants(self, limit: Optional[int] = None) -> List[Dict]:
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

    async def get_restaurant(self, business_id: str) -> Optional[Restaurant]:
        """Get a restaurant from the restaurant table."""
        try:
            response = self.supabase.table(RESTAURANTS_TABLE_NAME).select("*").eq('business_id', business_id).execute()
            if response.data:
                return Restaurant(**response.data[0])
            raise Exception(f"Restaurant {business_id} not found")
        except Exception as e:
            logger.error(f"Failed to get restaurant {business_id}: {str(e)}", exc_info=True)
            raise

    async def search_restaurants(self, params: SearchParams) -> List[Restaurant]:
        """Search for restaurants using the Yelp API"""
        try:
            self.yelp = YelpClient()
            restaurants = await self.yelp.search_businesses(
                term=params.term,
                location=params.location,
                price=params.price,
                categories=params.categories,
                limit=params.limit,
                sort_by=params.sort_by
            )
            
            # Store all restaurants in cache
            for restaurant in restaurants:
                try:
                    await self.upsert_restaurant(restaurant)
                except Exception as store_error:
                    logger.error(f"Failed to cache restaurant {restaurant.name}: {str(store_error)}")
                    continue
                
            return restaurants
        except Exception as e:
            logger.error(f"Failed to search restaurants: {str(e)}", exc_info=True)
            raise

    async def search_stored_restaurants(self, params: SearchParams) -> List[Restaurant]:
        """Search for restaurants in our database cache"""
        try:
            restaurants = self.supabase.search_restaurants(
                term=params.term,
                location=params.location,
                price=params.price,
                categories=params.categories
            )
            
            if not restaurants:
                return []
                
            return [Restaurant(**r) for r in restaurants]
        except Exception as e:
            logger.error(f"Failed to search stored restaurants: {str(e)}", exc_info=True)
            raise

    async def update_restaurant(self, business_id: str, data: Dict[str, Any]) -> None:
        """Update a restaurant's information."""
        try:
            self.supabase.update_restaurant(business_id, data)
        except Exception as e:
            logger.error(f"Failed to update restaurant {business_id}: {str(e)}", exc_info=True)
            raise

    def get_cached_restaurants(self, limit: Optional[int] = None) -> List[Restaurant]:
        """Get restaurants from the database cache."""
        try:
            stored = self.supabase.get_restaurants(limit)
            return [Restaurant(**r) for r in stored]
        except Exception as e:
            logger.error(f"Failed to get cached restaurants: {str(e)}", exc_info=True)
            raise

    def get_stored_restaurants(self, limit: Optional[int] = None) -> List[Restaurant]:
        """Get all restaurants from storage."""
        try:
            stored = self.supabase.get_restaurants(limit)
            restaurants = []
            
            for data in stored:
                try:
                    # Format location data to match Restaurant model
                    if 'location' in data:
                        data['location'] = {
                            'address1': data['location'].get('address1'),
                            'address2': None,
                            'address3': None,
                            'city': data['location'].get('city'),
                            'state': data['location'].get('state'),
                            'zip_code': data['location'].get('zip_code'),
                            'country': 'US',
                            'display_address': None
                        }
                    restaurant = Restaurant(**data)
                    restaurants.append(restaurant)
                except Exception as e:
                    logger.error(f"Error formatting restaurant {data.get('business_id')}: {str(e)}")
                    continue
            
            if limit:
                restaurants = restaurants[:limit]
                
            return restaurants
        except Exception as e:
            logger.error(f"Failed to get stored restaurants: {str(e)}", exc_info=True)
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

restaurant_db = RestaurantDB()
