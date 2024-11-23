import asyncio
from app.db.restaurants import RestaurantDB
from app.models import SearchParams

async def test_restaurant_api():
    try:
        # Initialize DB layer
        print("Initializing DB layer...")
        db = RestaurantDB()
        
        # Test 1: Search Restaurants
        print("\n🔍 Test 1: Searching for sushi restaurants...")
        search_params = SearchParams(
            term="sushi",
            location="San Francisco, CA",
            radius=8000,
            limit=5,
            sort_by="rating",
            price="1,2"
        )
        restaurants = await db.search_restaurants(search_params)
        print(f"Found {len(restaurants)} restaurants")
        for restaurant in restaurants:
            print(f"- {restaurant.name} (Rating: {restaurant.rating})")
        
        if restaurants:
            # Test 2: Get Restaurant Details
            print(f"\n🔍 Test 2: Getting details for {restaurants[0].name}...")
            restaurant_details = await db.get_restaurant(restaurants[0].business_id)
            if restaurant_details:
                print(f"Details retrieved successfully:")
                print(f"Name: {restaurant_details.name}")
                print(f"Rating: {restaurant_details.rating}")
                print(f"Price: {restaurant_details.price}")
                print(f"Phone: {restaurant_details.phone}")
                print(f"Address: {restaurant_details.location.address1}, {restaurant_details.location.city}")
            
            # Test 3: Check Cache
            print("\n🔍 Test 3: Getting restaurants from cache...")
            cached = db.get_cached_restaurants(limit=5)
            print(f"Found {len(cached)} restaurants in cache")
            for restaurant in cached:
                print(f"- {restaurant.name}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_restaurant_api())
