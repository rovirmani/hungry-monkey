from fastapi import APIRouter, HTTPException, Query, Response
from typing import List, Optional
from ..db.restaurants import RestaurantDB
from ..models import Restaurant, SearchParams
from ..clients.google_search import image_search
import httpx
import asyncio

router = APIRouter()
db = RestaurantDB()

@router.get("/cached", response_model=List[Restaurant])
async def get_cached_restaurants(
    limit: Optional[int] = Query(None, description="Maximum number of restaurants to return"),
    fetch_images: Optional[bool] = Query(False, description="Whether to fetch missing images")
) -> List[Restaurant]:
    """
    Get restaurants from cache only, without hitting the Yelp API.
    """
    try:
        print("🔍 Getting cached restaurants...")
        restaurants = db.get_cached_restaurants(limit)
        
        if fetch_images:
            # Fetch images asynchronously for restaurants without photos
            async def fetch_image_for_restaurant(restaurant: Restaurant):
                if not restaurant.photos or len(restaurant.photos) == 0:
                    try:
                        # Simple search query with restaurant name
                        search_query = f"{restaurant.name} restaurant"
                        images = await image_search.search_images(search_query, num=1)
                        
                        if images:
                            restaurant.photos = images
                            await db.update_restaurant(restaurant.business_id, {"photos": images})
                            print(f"✅ Found image for {restaurant.name}")
                    except Exception as e:
                        print(f"⚠️ Error fetching image for {restaurant.name}: {str(e)}")

            # Create tasks for restaurants without photos (limit to first 10)
            tasks = [
                fetch_image_for_restaurant(restaurant) 
                for restaurant in restaurants[:10] 
                if not restaurant.photos or len(restaurant.photos) == 0
            ]
            
            if tasks:
                # Run image fetching concurrently
                await asyncio.gather(*tasks)
        
        print(f"✅ Found {len(restaurants)} restaurants in cache")
        return restaurants
    except Exception as e:
        print(f"❌ Error getting cached restaurants: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[Restaurant])
async def search_restaurants(
    term: str = Query(None, description="Search term (e.g., 'coffee', 'restaurants')"),
    location: str = Query(..., description="Location (e.g., 'San Francisco, CA')"),
    price: Optional[str] = Query(None, description="Price level (1, 2, 3, 4)"),
    open_now: Optional[bool] = Query(None, description="Filter for open restaurants"),
    categories: Optional[str] = Query(None, description="Category filter")
) -> List[Restaurant]:
    """
    Search for restaurants using database and fetch images if needed.
    """
    try:
        params = SearchParams(
            term=term,
            location=location,
            price=price,
            open_now=open_now,
            categories=categories
        )
        restaurants = await db.search_restaurants(params)
        
        # Fetch images asynchronously for restaurants without photos
        async def fetch_image_for_restaurant(restaurant: Restaurant):
            if not restaurant.photos or len(restaurant.photos) == 0:
                try:
                    # Simple search query with restaurant name
                    search_query = f"{restaurant.name} restaurant"
                    images = await image_search.search_images(search_query, num=1)
                    
                    if images:
                        restaurant.photos = images
                        await db.update_restaurant(restaurant.business_id, {"photos": images})
                        print(f"✅ Found image for {restaurant.name}")
                except Exception as e:
                    print(f"⚠️ Error fetching image for {restaurant.name}: {str(e)}")

        # Create tasks for restaurants without photos
        tasks = [
            fetch_image_for_restaurant(restaurant) 
            for restaurant in restaurants 
            if not restaurant.photos or len(restaurant.photos) == 0
        ]
        
        if tasks:
            # Run image fetching concurrently
            await asyncio.gather(*tasks)
        
        return restaurants
    except Exception as e:
        print(f"❌ Error in search_restaurants: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{business_id}", response_model=Restaurant)
async def get_restaurant_details(business_id: str) -> Restaurant:
    """Get detailed information about a specific restaurant."""
    try:
        restaurant = await db.get_restaurant(business_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
            
        # Fetch images if none exist
        if not restaurant.photos or len(restaurant.photos) == 0:
            search_query = f"{restaurant.name} {restaurant.location.city} restaurant"
            images = await image_search.search_images(search_query, num=5)  # Get more images for detail view
            if images:
                restaurant.photos = images
                print(f"✅ Found {len(images)} images for {restaurant.name}")
            else:
                print(f"⚠️ No images found for {restaurant.name}")
                
        return restaurant
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_restaurant_details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/phone", response_model=List[Restaurant])
async def search_by_phone(
    phone: str = Query(..., description="Phone number to search for")
) -> List[Restaurant]:
    """
    Search for restaurants by phone number.
    Phone number should be in E.164 format (+14157492060).
    """
    try:
        return await db.search_by_phone(phone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))