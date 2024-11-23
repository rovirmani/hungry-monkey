import asyncio
from app.clients.yelp import YelpClient
from app.clients.supabase import SupabaseClient
from app.models import SearchParams

async def fetch_and_store_restaurants():
    try:
        # Initialize clients
        print("Initializing clients...")
        yelp_client = YelpClient()
        supabase = SupabaseClient()
        
        # Set up search parameters
        search_params = SearchParams(
            term="sushi",
            location="San Francisco, CA",  # Added state for more precise location
            radius=8000,  # Rounded to nearest thousand
            limit=20,  # Default limit
            sort_by="rating",
            price="1,2"  # Just moderate price ranges
        )
        
        # Fetch restaurants from Yelp
        print("\nFetching sushi restaurants from Yelp API...")
        restaurants = await yelp_client.search_restaurants(search_params)
        print(f"Found {len(restaurants)} restaurants")
        
        # Store in Supabase
        print("\nStoring restaurants in Supabase...")
        stored_count = 0
        for restaurant in restaurants:
            # Convert Pydantic model to dict
            restaurant_data = restaurant.model_dump()
            success = supabase.store_restaurant(restaurant_data)
            if success:
                stored_count += 1
                print(f"✅ Stored {restaurant.name}")
            else:
                print(f"❌ Failed to store {restaurant.name}")
        
        # Verify stored data
        print("\nVerifying stored data...")
        stored_restaurants = supabase.get_restaurants()
        print(f"Successfully stored {stored_count} out of {len(restaurants)} restaurants")
        print(f"Total restaurants in database: {len(stored_restaurants)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(fetch_and_store_restaurants())
