#!/usr/bin/env python3
import os
import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from app.db.restaurants import RestaurantDB
from app.models import SearchParams

async def find_restaurants_near_yc():
    print(" Initializing restaurant search...")
    db = RestaurantDB()
    params = SearchParams(
        term="food",  # Add search term
        location="1478 Thunderbird Ave, Sunnyvale, CA",
        radius=4023,  # 2.5 miles in meters
        limit=20,     # Get more results
        sort_by="rating",  # Sort by rating
        categories="restaurants,food"  # Explicitly request only restaurants and food places
    )
    
    try:
        print("\n Fetching restaurants from Yelp...")
        restaurants = await db.search_restaurants(params)
        
        # Verify storage in Supabase
        print("\n Verifying Supabase storage...")
        for restaurant in restaurants:
            cached = await db.get_restaurant(restaurant.business_id)
            if cached:
                print(f" Restaurant '{restaurant.name}' stored in Supabase")
            else:
                print(f" Failed to store '{restaurant.name}' in Supabase")
        
        print(f"\n Found {len(restaurants)} restaurants within 2.5 miles:")
        print("\n Top Rated Restaurants:")
        print("-" * 50)
        
        # Sort by rating and display details
        for restaurant in sorted(restaurants, key=lambda x: x.rating or 0, reverse=True):
            price = restaurant.price if restaurant.price else "N/A"
            rating = restaurant.rating if restaurant.rating else "N/A"
            
            print(f"\n  {restaurant.name}")
            print(f" Rating: {rating}")
            print(f" Price: {price}")
            print(f" Phone: {restaurant.phone if restaurant.phone else 'N/A'}")
            print(f" Address: {restaurant.location.address1}, {restaurant.location.city}")
            if restaurant.categories:
                categories = ", ".join([cat.title for cat in restaurant.categories])
                print(f"  Categories: {categories}")
            
            if restaurant.is_open:
                print(" Currently Open")
            else:
                print(" Currently Closed")
            print("-" * 50)
    except Exception as e:
        print(f" Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(find_restaurants_near_yc())
