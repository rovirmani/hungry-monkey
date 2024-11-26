import logging
from typing import List, Optional, Dict, Any
from app.clients.supabase import SupabaseClient
from app.clients.yelp import YelpClient
from app.models import Restaurant, SearchParams

logger = logging.getLogger(__name__)

class RestaurantDB:
    def __init__(self):
        self.supabase = SupabaseClient()
        self.yelp = YelpClient()
        logger.info("✅ RestaurantDB initialized")

    async def create_restaurant(self, restaurant: Restaurant) -> Dict[str, Any]:
        """Create a new restaurant record."""
        try:
            data = restaurant.model_dump()
            self.supabase.store_restaurant(data)
            logger.info(f"✅ Created restaurant {restaurant.name}")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to create restaurant: {str(e)}", exc_info=True)
            raise Exception(f"Failed to create restaurant: {str(e)}")

    async def get_restaurant(self, business_id: str) -> Optional[Restaurant]:
        """Get a restaurant from storage, if not found fetch from Yelp."""
        try:
            # Try database first
            stored = self.supabase.get_restaurant(business_id)
            if stored:
                logger.info(f"✅ Found restaurant {business_id} in database")
                return Restaurant(**stored)

            # If not in database, get from Yelp
            restaurant = await self.yelp.get_business_details(business_id)
            if restaurant:
                # Store it
                await self.create_restaurant(restaurant)
                logger.info(f"✅ Fetched and stored restaurant {business_id} from Yelp")
                return restaurant

            logger.info(f"ℹ️ Restaurant {business_id} not found")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get restaurant: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get restaurant: {str(e)}")

    async def search_restaurants(self, params: SearchParams) -> List[Restaurant]:
        """
        Search for restaurants using the Yelp API
        """
        try:
            logger.info(f"🔍 Searching Yelp with params: {params}")
            restaurants = await self.yelp.search_businesses(
                term=params.term,
                location=params.location,
                price=params.price,
                categories=params.categories,
                limit=params.limit,
                sort_by=params.sort_by
            )
            
            logger.info(f"✅ Found {len(restaurants)} restaurants from Yelp")
            
            # Store all restaurants in cache
            for restaurant in restaurants:
                try:
                    await self.create_restaurant(restaurant)
                except Exception as store_error:
                    logger.error(f"❌ Failed to cache restaurant {restaurant.name}: {str(store_error)}")
                    # Continue with next restaurant even if one fails to cache
                    continue
                
            return restaurants
            
        except Exception as e:
            logger.error(f"❌ Failed to search Yelp: {str(e)}", exc_info=True)
            raise Exception(f"Yelp API search failed: {str(e)}")

    async def search_cached_restaurants(self, params: SearchParams) -> List[Restaurant]:
        """
        Search for restaurants in our database cache
        """
        try:
            logger.info(f"🔍 Searching cache with params: {params}")
            # Use Supabase's built-in filtering
            restaurants = self.supabase.search_restaurants(
                term=params.term,
                location=params.location,
                price=params.price,
                categories=params.categories
            )
            
            if not restaurants:
                logger.info("ℹ️ No results found in cache")
                return []
                
            logger.info(f"✅ Found {len(restaurants)} restaurants in cache")
            return [Restaurant(**r) for r in restaurants]
            
        except Exception as e:
            logger.error(f"❌ Failed to search cache: {str(e)}", exc_info=True)
            raise Exception(f"Database search failed: {str(e)}")

    async def update_restaurant(self, business_id: str, data: Dict[str, Any]) -> None:
        """Update a restaurant's information."""
        try:
            logger.info(f"🔄 Updating restaurant {business_id} with new data")
            self.supabase.update_restaurant(business_id, data)
            logger.info(f"✅ Successfully updated restaurant {business_id}")
        except Exception as e:
            logger.error(f"❌ Error updating restaurant {business_id}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to update restaurant: {str(e)}")

    def delete_restaurant(self, business_id: str) -> bool:
        """Delete a restaurant."""
        try:
            self.supabase.delete_restaurant(business_id)
            logger.info(f"✅ Deleted restaurant {business_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete restaurant: {str(e)}", exc_info=True)
            raise Exception(f"Failed to delete restaurant: {str(e)}")

    def bulk_upsert_restaurants(self, restaurants: List[Restaurant]) -> List[Dict[str, Any]]:
        """Bulk upsert restaurants (insert or update based on business_id)."""
        try:
            data = [rest.model_dump() for rest in restaurants]
            self.supabase.bulk_upsert_restaurants(data)
            logger.info(f"✅ Bulk upserted {len(restaurants)} restaurants")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to bulk upsert restaurants: {str(e)}", exc_info=True)
            raise Exception(f"Failed to bulk upsert restaurants: {str(e)}")

    async def search_by_phone(self, phone: str) -> List[Restaurant]:
        """Search restaurants by phone number."""
        try:
            # First check database
            stored = self.supabase.search_by_phone(phone)
            if stored:
                logger.info(f"✅ Found {len(stored)} restaurants in database with phone {phone}")
                return [Restaurant(**r) for r in stored]

            # If not in database, search Yelp
            restaurants = await self.yelp.search_by_phone(phone)
            
            # Store results
            for restaurant in restaurants:
                try:
                    await self.create_restaurant(restaurant)
                except Exception as store_error:
                    logger.error(f"❌ Failed to cache restaurant {restaurant.name}: {str(store_error)}")
                    # Continue with next restaurant even if one fails to cache
                    continue
                
            logger.info(f"✅ Found {len(restaurants)} restaurants with phone {phone}")
            return restaurants
        except Exception as e:
            logger.error(f"❌ Failed to search by phone: {str(e)}", exc_info=True)
            raise Exception(f"Failed to search by phone: {str(e)}")

    def get_cached_restaurants(self, limit: Optional[int] = None) -> List[Restaurant]:
        """Get restaurants from the database cache."""
        try:
            logger.info("🔍 Getting cached restaurants...")
            stored = self.supabase.get_restaurants(limit)
            logger.info(f"✅ Found {len(stored)} cached restaurants")
            return [Restaurant(**r) for r in stored]
        except Exception as e:
            logger.error(f"❌ Failed to get cached restaurants: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get cached restaurants: {str(e)}")

    def get_stored_restaurants(self, limit: Optional[int] = None) -> List[Restaurant]:
        """Get all restaurants from storage."""
        try:
            logger.info("🔍 Getting stored restaurants from Supabase...")
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
                    logger.error(f"⚠️ Error formatting restaurant {data.get('business_id')}: {str(e)}")
                    continue
            
            if limit:
                restaurants = restaurants[:limit]
                
            logger.info(f"✅ Found {len(restaurants)} stored restaurants")
            return restaurants
        except Exception as e:
            logger.error(f"❌ Failed to get stored restaurants: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get stored restaurants: {str(e)}")
            
    def get_restaurants_without_hours(self) -> List[Dict[str, Any]]:
        try:
            logger.info("🔍 Getting restaurants without hours...")
            restaurants = self.supabase.get_restaurants_without_hours()
            logger.info(f"✅ Found {len(restaurants)} restaurants without hours")
            return restaurants
        except Exception as e:
            logger.error(f"❌ Failed to get restaurants without hours: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get restaurants without hours: {str(e)}")