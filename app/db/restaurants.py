<<<<<<< HEAD
from typing import List, Optional, Dict, Any
from app.clients.supabase import SupabaseClient
from app.clients.yelp import YelpClient
from app.models import Restaurant, SearchParams
=======
from __future__ import annotations
import logging
from typing import List, Optional, Dict, Any
from app.clients.supabase import SupabaseClient
from app.clients.yelp import YelpClient

logger = logging.getLogger(__name__)
>>>>>>> origin

class RestaurantDB:
    def __init__(self):
        self.supabase = SupabaseClient()
        self.yelp = YelpClient()
<<<<<<< HEAD
=======
        logger.info("✅ RestaurantDB initialized")
>>>>>>> origin

    async def create_restaurant(self, restaurant: Restaurant) -> Dict[str, Any]:
        """Create a new restaurant record."""
        try:
            data = restaurant.model_dump()
            self.supabase.store_restaurant(data)
<<<<<<< HEAD
            return data
        except Exception as e:
=======
            logger.info(f"✅ Created restaurant {restaurant.name}")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to create restaurant: {str(e)}", exc_info=True)
>>>>>>> origin
            raise Exception(f"Failed to create restaurant: {str(e)}")

    async def get_restaurant(self, business_id: str) -> Optional[Restaurant]:
        """Get a restaurant from storage, if not found fetch from Yelp."""
        try:
            # Try database first
            stored = self.supabase.get_restaurant(business_id)
            if stored:
<<<<<<< HEAD
=======
                logger.info(f"✅ Found restaurant {business_id} in database")
>>>>>>> origin
                return Restaurant(**stored)

            # If not in database, get from Yelp
            restaurant = await self.yelp.get_business_details(business_id)
            if restaurant:
                # Store it
<<<<<<< HEAD
                self.supabase.store_restaurant(restaurant.model_dump())
                return restaurant

            return None
        except Exception as e:
            raise Exception(f"Failed to get restaurant: {str(e)}")

    async def search_restaurants(self, params: SearchParams) -> List[Restaurant]:
        """Search restaurants from Yelp and store them."""
        try:
            # Get fresh results from Yelp
            restaurants = await self.yelp.search_restaurants(params)
            
            # Store them in Supabase
            for restaurant in restaurants:
                print(f"📝 Storing {restaurant.name} in Supabase...")
                data = restaurant.model_dump()
                print(f"📝 Stored data: {data}")
                self.supabase.store_restaurant(data)
                print(f"✅ {restaurant.name} stored successfully")
                
            return restaurants
        except Exception as e:
            raise Exception(f"Failed to search restaurants: {str(e)}")
=======
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
>>>>>>> origin

    async def update_restaurant(self, business_id: str, data: Dict[str, Any]) -> None:
        """Update a restaurant's information."""
        try:
<<<<<<< HEAD
            print(f"🔄 Updating restaurant {business_id} with new data")
            self.supabase.update_restaurant(business_id, data)
            print(f"✅ Successfully updated restaurant {business_id}")
        except Exception as e:
            print(f"❌ Error updating restaurant {business_id}: {str(e)}")
=======
            logger.info(f"🔄 Updating restaurant {business_id} with new data")
            self.supabase.update_restaurant(business_id, data)
            logger.info(f"✅ Successfully updated restaurant {business_id}")
        except Exception as e:
            logger.error(f"❌ Error updating restaurant {business_id}: {str(e)}", exc_info=True)
>>>>>>> origin
            raise Exception(f"Failed to update restaurant: {str(e)}")

    def delete_restaurant(self, business_id: str) -> bool:
        """Delete a restaurant."""
        try:
            self.supabase.delete_restaurant(business_id)
<<<<<<< HEAD
            return True
        except Exception as e:
=======
            logger.info(f"✅ Deleted restaurant {business_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete restaurant: {str(e)}", exc_info=True)
>>>>>>> origin
            raise Exception(f"Failed to delete restaurant: {str(e)}")

    def bulk_upsert_restaurants(self, restaurants: List[Restaurant]) -> List[Dict[str, Any]]:
        """Bulk upsert restaurants (insert or update based on business_id)."""
        try:
            data = [rest.model_dump() for rest in restaurants]
            self.supabase.bulk_upsert_restaurants(data)
<<<<<<< HEAD
            return data
        except Exception as e:
=======
            logger.info(f"✅ Bulk upserted {len(restaurants)} restaurants")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to bulk upsert restaurants: {str(e)}", exc_info=True)
>>>>>>> origin
            raise Exception(f"Failed to bulk upsert restaurants: {str(e)}")

    async def search_by_phone(self, phone: str) -> List[Restaurant]:
        """Search restaurants by phone number."""
        try:
            # First check database
            stored = self.supabase.search_by_phone(phone)
            if stored:
<<<<<<< HEAD
=======
                logger.info(f"✅ Found {len(stored)} restaurants in database with phone {phone}")
>>>>>>> origin
                return [Restaurant(**r) for r in stored]

            # If not in database, search Yelp
            restaurants = await self.yelp.search_by_phone(phone)
            
            # Store results
            for restaurant in restaurants:
<<<<<<< HEAD
                self.supabase.store_restaurant(restaurant.model_dump())
                
            return restaurants
        except Exception as e:
=======
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
>>>>>>> origin
            raise Exception(f"Failed to search by phone: {str(e)}")

    def get_cached_restaurants(self, limit: Optional[int] = None) -> List[Restaurant]:
        """Get restaurants from the database cache."""
        try:
<<<<<<< HEAD
            stored = self.supabase.get_restaurants(limit)
            return [Restaurant(**r) for r in stored]
        except Exception as e:
=======
            logger.info("🔍 Getting cached restaurants...")
            stored = self.supabase.get_restaurants(limit)
            logger.info(f"✅ Found {len(stored)} cached restaurants")
            return [Restaurant(**r) for r in stored]
        except Exception as e:
            logger.error(f"❌ Failed to get cached restaurants: {str(e)}", exc_info=True)
>>>>>>> origin
            raise Exception(f"Failed to get cached restaurants: {str(e)}")

    def get_stored_restaurants(self, limit: Optional[int] = None) -> List[Restaurant]:
        """Get all restaurants from storage."""
        try:
<<<<<<< HEAD
            print("🔍 Getting stored restaurants from Supabase...")
=======
            logger.info("🔍 Getting stored restaurants from Supabase...")
>>>>>>> origin
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
<<<<<<< HEAD
                    print(f"⚠️ Error formatting restaurant {data.get('business_id')}: {str(e)}")
=======
                    logger.error(f"⚠️ Error formatting restaurant {data.get('business_id')}: {str(e)}")
>>>>>>> origin
                    continue
            
            if limit:
                restaurants = restaurants[:limit]
                
<<<<<<< HEAD
            return restaurants
        except Exception as e:
            raise Exception(f"Failed to get stored restaurants: {str(e)}")
            
    def get_restaurants_without_hours(self) -> List[Dict[str, Any]]:
        return self.supabase.get_restaurants_without_hours()
=======
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

# Import models at the bottom
from app.models import Restaurant, SearchParams

# No need for update_forward_refs() since we're not defining any Pydantic models in this file
>>>>>>> origin
