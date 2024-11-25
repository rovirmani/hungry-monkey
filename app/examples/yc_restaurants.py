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
from app.clients.google_search import image_search

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
        
        print("\n Fetching and storing images for each restaurant...")
        for restaurant in restaurants:
            print(f"\n Processing: {restaurant.name}")
            
            # Search for images
            search_query = f"{restaurant.name} {restaurant.location.address1} {restaurant.location.city}"
            image_urls = await image_search.search_images(search_query, num=3)
            
            if image_urls:
                print(f"✅ Found {len(image_urls)} images for {restaurant.name}")
                # Update restaurant with image URLs in photos field
                restaurant.photos = image_urls
                
                # Store updated restaurant in database
                await db.upsert_restaurant(restaurant)
                print(f"💾 Stored {restaurant.name} with images in database")
            else:
                print(f"❌ No images found for {restaurant.name}")
        
        # Verify storage in Supabase
        print("\n🔍 Verifying Supabase storage...")
        for restaurant in restaurants:
            cached = await db.get_restaurant(restaurant.business_id)
            if cached and cached.photos:
                print(f"✅ Restaurant '{restaurant.name}' stored with {len(cached.photos)} images")
            else:
                print(f"❌ Failed to store images for '{restaurant.name}'")
        
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
            
            # Print image URLs if available
            if restaurant.photos:
                print(f"🖼️  Images: {len(restaurant.photos)} found")
                for i, url in enumerate(restaurant.photos, 1):
                    print(f"   {i}. {url}")
            
            if restaurant.is_open:
                print(" Currently Open")
            else:
                print(" Currently Closed")
            print("-" * 50)
    except Exception as e:
        print(f" Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(find_restaurants_near_yc())
