import asyncio
from app.db.restaurants import RestaurantDB
from app.models import SearchParams

async def find_restaurants_near_yc():
    print("🔍 Searching for restaurants near Y Combinator (SF)...")
    db = RestaurantDB()
    
    # 2.5 miles = 4023 meters (Yelp API uses meters)
    search_params = SearchParams(
        location="320 Pioneer Way, Mountain View, CA",
        radius=4023,  # 2.5 miles in meters
        limit=50,     # Get more results
        sort_by="rating"  # Sort by rating
    )
    
    try:
        restaurants = await db.search_restaurants(search_params)
        
        print(f"\nFound {len(restaurants)} restaurants within 2.5 miles:")
        print("\nTop Rated Restaurants:")
        print("-" * 50)
        
        # Sort by rating and display details
        for restaurant in sorted(restaurants, key=lambda x: x.rating or 0, reverse=True):
            price = restaurant.price if restaurant.price else "N/A"
            rating = restaurant.rating if restaurant.rating else "N/A"
            
            print(f"\n🍽️  {restaurant.name}")
            print(f"⭐ Rating: {rating}")
            print(f"💰 Price: {price}")
            print(f"📞 Phone: {restaurant.phone if restaurant.phone else 'N/A'}")
            print(f"🏠 Address: {restaurant.location.address1}, {restaurant.location.city}")
            if restaurant.categories:
                categories = ", ".join([cat.title for cat in restaurant.categories])
                print(f"🏷️  Categories: {categories}")
            
            if restaurant.is_closed is False:  # Specifically check for False as it might be None
                print("✅ Currently Open")
            elif restaurant.is_closed is True:
                print("❌ Currently Closed")
            print("-" * 50)
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(find_restaurants_near_yc())
