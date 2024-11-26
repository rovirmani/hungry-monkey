from fastapi import APIRouter, HTTPException, Query, Response, Depends
from typing import List, Optional
from ..db.restaurants import RestaurantDB
from ..db.operating_hours import OperatingHoursDB
from ..models import Restaurant, SearchParams, RestaurantWithHours, OperatingHours
from ..clients.google_custom_search import image_search
from ..auth.clerk import verify_auth_token, verify_auth_token_optional
import httpx
import asyncio
from urllib.parse import quote

router = APIRouter()
db = RestaurantDB()
oh_db = OperatingHoursDB()


@router.get("/cached", response_model=List[RestaurantWithHours])
async def get_cached_restaurants(
    limit: Optional[int] = Query(None, description="Maximum number of restaurants to return"),
    fetch_images: Optional[bool] = Query(False, description="Whether to fetch missing images"),
) -> List[RestaurantWithHours]:
    """
    Get restaurants from cache only, without hitting the Yelp API.
    This endpoint is public and does not require authentication.
    """
    try:
        print("🔍 Getting cached restaurants...")
        base_restaurants = db.get_cached_restaurants(limit)
    
        # Get hours for all restaurants in a single query
        restaurant_ids = [r.business_id for r in base_restaurants]
        hours_map = await oh_db.get_hours_bulk(restaurant_ids)
        
        # Convert to RestaurantWithHours and add operating hours
        restaurants_with_hours: List[RestaurantWithHours] = []
        for restaurant in base_restaurants:
            # Convert base restaurant to RestaurantWithHours
            restaurant_dict = restaurant.model_dump()
            hours = hours_map.get(restaurant.business_id)
            if hours:
                restaurant_dict['operating_hours'] = OperatingHours(
                    time_open=hours.get('time_open'),
                    time_closed=hours.get('time_closed'),
                    is_hours_verified=hours.get('is_hours_verified', False),
                    is_consenting=hours.get('is_consenting', False),
                    is_open=hours.get('is_open')
                )
            restaurants_with_hours.append(RestaurantWithHours(**restaurant_dict))

        if fetch_images:
            # Fetch images asynchronously for restaurants without photos
            async def fetch_image_for_restaurant(restaurant: RestaurantWithHours):
                if not restaurant.photos or len(restaurant.photos) == 0:
                    try:
                        # Simple search query with restaurant name
                        search_query = quote(f"{restaurant.name} restaurant")
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
                for restaurant in restaurants_with_hours[:10] 
                if not restaurant.photos or len(restaurant.photos) == 0
            ]
            
            if tasks:
                # Run image fetching concurrently
                await asyncio.gather(*tasks)
        
        print(f"✅ Found {len(restaurants_with_hours)} restaurants in cache")
        return restaurants_with_hours
    except Exception as e:
        print(f"❌ Error getting cached restaurants: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[RestaurantWithHours])
async def search_restaurants(
    term: str = Query(None, description="Search term (e.g., 'coffee', 'restaurants')"),
    location: str = Query(..., description="Location (e.g., 'San Francisco, CA')"),
    price: Optional[str] = Query(None, description="Price level (1, 2, 3, 4)"),
    categories: Optional[str] = Query(None, description="Category filter"),
    auth: Optional[dict] = Depends(verify_auth_token_optional)
) -> List[RestaurantWithHours]:
    """
    Search for restaurants. If user is authenticated, also searches Yelp API.
    """
    try:
        # Create search params with all provided filters
        params = SearchParams(
            term=term or "Restaurants",
            location=location,
            price=price,
            categories=categories
        )
        
        print(f"🔍 Searching with params: {params}")
        
        # First search in our database
        stored_restaurants = await db.search_cached_restaurants(params)
        print(f"✅ Found {len(stored_restaurants)} restaurants in cache")
        
        # If user is authenticated, also search Yelp
        if auth:
            print("🔑 User is authenticated, searching Yelp API...")
            yelp_restaurants = await db.search_restaurants(params)
            print(f"✅ Found {len(yelp_restaurants)} additional restaurants from Yelp")
            
            # Combine results, avoiding duplicates
            seen_ids = {r.business_id for r in stored_restaurants}
            for restaurant in yelp_restaurants:
                if restaurant.business_id not in seen_ids:
                    stored_restaurants.append(restaurant)
                    seen_ids.add(restaurant.business_id)
        
        # Get hours for all restaurants in a single query
        restaurant_ids = [r.business_id for r in stored_restaurants]
        hours_map = await oh_db.get_hours_bulk(restaurant_ids)
        
        # Convert to RestaurantWithHours and add operating hours
        restaurants_with_hours: List[RestaurantWithHours] = []
        for restaurant in stored_restaurants:
            # Convert base restaurant to RestaurantWithHours
            restaurant_dict = restaurant.model_dump()
            hours = hours_map.get(restaurant.business_id)
            if hours:
                restaurant_dict['operating_hours'] = OperatingHours(
                    time_open=hours.get('time_open'),
                    time_closed=hours.get('time_closed'),
                    is_hours_verified=hours.get('is_hours_verified', False),
                    is_consenting=hours.get('is_consenting', False),
                    is_open=hours.get('is_open')
                )
            restaurants_with_hours.append(RestaurantWithHours(**restaurant_dict))
        
        return restaurants_with_hours
        
    except Exception as e:
        print(f"❌ Error in search_restaurants: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{business_id}", response_model=Restaurant)
async def get_restaurant_details(business_id: str, auth: dict = Depends(verify_auth_token)) -> Restaurant:
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
    phone: str = Query(..., description="Phone number to search for"),
    auth: dict = Depends(verify_auth_token)
) -> List[Restaurant]:
    """
    Search for restaurants by phone number.
    Phone number should be in E.164 format (+14157492060).
    """
    try:
        return await db.search_by_phone(phone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
