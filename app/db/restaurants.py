from typing import List, Optional, Dict, Any
from app.clients.supabase import SupabaseClient
from app.clients.yelp import YelpClient
from app.models import Restaurant, SearchParams

class RestaurantDB:
    def __init__(self):
        self.supabase = SupabaseClient()
        self.yelp = YelpClient()

    async def create_restaurant(self, restaurant: Restaurant) -> Dict[str, Any]:
        """Create a new restaurant record."""
        try:
            data = restaurant.model_dump()
            self.supabase.store_restaurant(data)
            return data
        except Exception as e:
            raise Exception(f"Failed to create restaurant: {str(e)}")

    async def get_restaurant(self, business_id: str) -> Optional[Restaurant]:
        """Get a restaurant, first from cache then Yelp."""
        try:
            # Try cache first
            cached = self.supabase.get_restaurant(business_id)
            if cached:
                return Restaurant(**cached)

            # If not in cache, get from Yelp
            restaurant = await self.yelp.get_business_details(business_id)
            if restaurant:
                # Cache it
                self.supabase.store_restaurant(restaurant.model_dump())
                return restaurant

            return None
        except Exception as e:
            raise Exception(f"Failed to get restaurant: {str(e)}")

    async def search_restaurants(self, params: SearchParams) -> List[Restaurant]:
        """Search restaurants from Yelp and cache them."""
        try:
            # Get fresh results from Yelp
            restaurants = await self.yelp.search_restaurants(params)
            
            # Cache them in Supabase
            for restaurant in restaurants:
                data = restaurant.model_dump()
                self.supabase.store_restaurant(data)
                
            return restaurants
        except Exception as e:
            raise Exception(f"Failed to search restaurants: {str(e)}")

    async def update_restaurant(self, business_id: str, data: Dict[str, Any]) -> None:
        """Update a restaurant's information."""
        try:
            print(f"🔄 Updating restaurant {business_id} with new data")
            self.supabase.update_restaurant(business_id, data)
            print(f"✅ Successfully updated restaurant {business_id}")
        except Exception as e:
            print(f"❌ Error updating restaurant {business_id}: {str(e)}")
            raise Exception(f"Failed to update restaurant: {str(e)}")

    def delete_restaurant(self, business_id: str) -> bool:
        """Delete a restaurant."""
        try:
            self.supabase.delete_restaurant(business_id)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete restaurant: {str(e)}")

    def bulk_upsert_restaurants(self, restaurants: List[Restaurant]) -> List[Dict[str, Any]]:
        """Bulk upsert restaurants (insert or update based on business_id)."""
        try:
            data = [rest.model_dump() for rest in restaurants]
            self.supabase.bulk_upsert_restaurants(data)
            return data
        except Exception as e:
            raise Exception(f"Failed to bulk upsert restaurants: {str(e)}")

    async def search_by_phone(self, phone: str) -> List[Restaurant]:
        """Search restaurants by phone number."""
        try:
            # First check cache
            cached = self.supabase.search_by_phone(phone)
            if cached:
                return [Restaurant(**r) for r in cached]

            # If not in cache, search Yelp
            restaurants = await self.yelp.search_by_phone(phone)
            
            # Cache results
            for restaurant in restaurants:
                self.supabase.store_restaurant(restaurant.model_dump())
                
            return restaurants
        except Exception as e:
            raise Exception(f"Failed to search by phone: {str(e)}")

    def get_cached_restaurants(self, limit: Optional[int] = None) -> List[Restaurant]:
        """Get all restaurants from cache."""
        try:
            print("🔍 Getting cached restaurants from Supabase...")
            cached = self.supabase.get_all_restaurants()
            restaurants = []
            
            for data in cached:
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
                    print(f"📝 Example formatted: {data}")
                    restaurant = Restaurant(**data)
                    restaurants.append(restaurant)
                except Exception as e:
                    print(f"⚠️ Error formatting restaurant {data.get('business_id')}: {str(e)}")
                    continue
            
            if limit:
                restaurants = restaurants[:limit]
                
            return restaurants
        except Exception as e:
            raise Exception(f"Failed to get cached restaurants: {str(e)}")
