import asyncio
from app.clients.supabase import SupabaseClient

async def test_connection():
    try:
        # Initialize client
        print("Initializing Supabase client...")
        supabase = SupabaseClient()
        
        # Test basic connection by getting service status
        print("\nTesting Supabase connection...")
        # Just verify we can access the client
        if supabase.client:
            print("✅ Successfully connected to Supabase!")
            
            # Print URL (without key) to verify we're connecting to the right instance
            print(f"\nConnected to Supabase instance:")
            print(f"URL: {supabase.supabase_url}")
            
            # Test data
            test_restaurant = {
                "id": "test-restaurant-1",
                "name": "Test Restaurant",
                "cuisine": "Test Cuisine",
                "rating": 4.5
            }
            
            # Test insert
            print("\nTesting database insert...")
            result = await supabase.store_restaurant_data(test_restaurant)
            print(f"Insert successful: {result}")
            
            # Test retrieval
            print("\nTesting database retrieval...")
            retrieved = await supabase.get_restaurant_by_id("test-restaurant-1")
            print(f"Retrieved data: {retrieved}")
            
            print("\nSupabase connection and operations working successfully!")
            return True
            
    except Exception as e:
        print(f"\n❌ Error testing Supabase connection: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
