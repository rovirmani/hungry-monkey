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
        """Get a restaurant from storage, if not found fetch from Yelp."""
        try:
            # Try database first
            stored = self.supabase.get_restaurant(business_id)
            if stored:
                return Restaurant(**stored)

            # If not in database, get from Yelp
            restaurant = await self.yelp.get_business_details(business_id)
            if restaurant:
                # Store it
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
            # First check database
            stored = self.supabase.search_by_phone(phone)
            if stored:
                return [Restaurant(**r) for r in stored]

            # If not in database, search Yelp
            restaurants = await self.yelp.search_by_phone(phone)
            
            # Store results
            for restaurant in restaurants:
                self.supabase.store_restaurant(restaurant.model_dump())
                
            return restaurants
        except Exception as e:
            raise Exception(f"Failed to search by phone: {str(e)}")

    def get_cached_restaurants(self, limit: Optional[int] = None) -> List[Restaurant]:
        """Get restaurants from the database cache."""
        try:
            stored = self.supabase.get_restaurants(limit)
            return [Restaurant(**r) for r in stored]
        except Exception as e:
            raise Exception(f"Failed to get cached restaurants: {str(e)}")

    def get_stored_restaurants(self, limit: Optional[int] = None) -> List[Restaurant]:
        """Get all restaurants from storage."""
        try:
            print("🔍 Getting stored restaurants from Supabase...")
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
                    print(f"⚠️ Error formatting restaurant {data.get('business_id')}: {str(e)}")
                    continue
            
            if limit:
                restaurants = restaurants[:limit]
                
            return restaurants
        except Exception as e:
            raise Exception(f"Failed to get stored restaurants: {str(e)}")
            
    def get_restaurants_without_hours(self) -> List[Dict[str, Any]]:
        return self.supabase.get_restaurants_without_hours()