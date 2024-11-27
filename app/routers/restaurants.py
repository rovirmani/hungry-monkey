<<<<<<< HEAD
from fastapi import APIRouter, HTTPException, Query, Response
from typing import List, Optional
from ..db.restaurants import RestaurantDB
from ..db.operating_hours import OperatingHoursDB
from ..models import Restaurant, SearchParams, RestaurantWithHours, OperatingHours
from ..clients.google_custom_search import image_search
import httpx
import asyncio
from urllib.parse import quote
=======
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query, Response, Depends
from typing import List, Optional
from ..db.restaurants import RestaurantDB
from ..db.operating_hours import OperatingHoursDB
from ..clients.google_custom_search import image_search
from ..auth.clerk import require_auth, optional_auth, get_optional_user
import httpx
import asyncio
import logging
from urllib.parse import quote
from ..models import Restaurant, SearchParams, RestaurantWithHours, OperatingHours

logger = logging.getLogger(__name__)
>>>>>>> origin

router = APIRouter()
db = RestaurantDB()
oh_db = OperatingHoursDB()
<<<<<<< HEAD


@router.get("/cached", response_model=List[RestaurantWithHours])
async def get_cached_restaurants(
    limit: Optional[int] = Query(None, description="Maximum number of restaurants to return"),
    fetch_images: Optional[bool] = Query(False, description="Whether to fetch missing images")
) -> List[RestaurantWithHours]:
    """
    Get restaurants from cache only, without hitting the Yelp API.
    """
    try:
        print("🔍 Getting cached restaurants...")
        base_restaurants = db.get_cached_restaurants(limit)
    
        # Get hours for all restaurants in a single query
        restaurant_ids = [r.business_id for r in base_restaurants]
        hours_map = oh_db.get_hours_bulk(restaurant_ids)
        
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
=======
>>>>>>> origin


@router.get("/", response_model=List[RestaurantWithHours])
async def get_cached_restaurants(
    limit: Optional[int] = Query(None, description="Maximum number of restaurants to return"),
    fetch_images: Optional[bool] = Query(False, description="Whether to fetch missing images"),
    user: Optional[dict] = optional_auth
) -> List[RestaurantWithHours]:
    """
    Get cached restaurants. Authentication is optional - authenticated users get access to image fetching.
    """
    try:
        logger.info("🔄 Fetching cached restaurants")
        
        # Get restaurants from cache using asyncio.to_thread for CPU-bound operations
        restaurants = await asyncio.to_thread(db.get_cached_restaurants, limit)
        logger.info(f"📦 Found {len(restaurants)} restaurants in cache")
        
        if not restaurants:
            # Return empty list instead of 404
            logger.info("ℹ️ No restaurants found in cache")
            return []
        
        # Get operating hours for each restaurant
        restaurant_ids = [r.business_id for r in restaurants]
        logger.info(f"⏰ Fetching hours for {len(restaurant_ids)} restaurants")
        hours_map = await asyncio.to_thread(oh_db.get_hours_bulk, restaurant_ids)
        
        # Combine restaurants with their hours
        results = []
        for restaurant in restaurants:
            hours = hours_map.get(restaurant.business_id)
            results.append(RestaurantWithHours(
                **restaurant.model_dump(),
                operating_hours=hours
            ))
            
        # Optionally fetch missing images
        if fetch_images:
            for restaurant in results:
                if not restaurant.image_url:
                    try:
                        image_url = await image_search(f"{restaurant.name} {restaurant.location.address1}")
                        if image_url:
                            restaurant.image_url = image_url
                            # Update in database
                            await db.update_restaurant(restaurant.business_id, {"image_url": image_url})
                    except Exception as e:
                        logger.error(f"❌ Failed to fetch image for {restaurant.name}: {str(e)}", exc_info=True)
                        continue
        
        logger.info(f"✅ Successfully processed {len(results)} restaurants")
        return results
            
    except Exception as e:
        logger.error(f"❌ Error in get_cached_restaurants: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch restaurants: {str(e)}"
        )


@router.get("/search")
async def search_restaurants(
<<<<<<< HEAD
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
        # params = SearchParams(
        #     term=term,
        #     location=location,
        #     price=price,
        #     open_now=open_now,
        #     categories=categories
        # )

        params = SearchParams(
            term="Restaurants",
            location=location)
        
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
=======
    term: Optional[str] = None,
    location: Optional[str] = None,
    radius: Optional[int] = None,
    limit: Optional[int] = 20,
    sort_by: Optional[str] = "best_match",
    price: Optional[str] = None,
    categories: Optional[str] = None,
    offset: Optional[int] = None,
    open_now: Optional[bool] = None,
    user: Optional[dict] = optional_auth
) -> List[Restaurant]:
    """
    Search for restaurants. Always search local database first.
    If user is authenticated and no results found, then search Yelp API.
    """
    try:
        db = RestaurantDB()
        params = SearchParams(
            term=term,
            location=location,
            radius=radius,
            limit=limit,
            sort_by=sort_by,
            price=price,
            categories=categories.split(",") if categories else None,
            offset=offset,
            open_now=open_now
        )
        
        logger.info(f"🔍 Searching with params: {params}")
        logger.info(f"👤 User authenticated: {bool(user)}")
        
        # Always search local cache first
        logger.info("🔄 Searching local cache...")
        restaurants = await db.search_cached_restaurants(params)
        if restaurants:
            logger.info(f"✅ Found {len(restaurants)} restaurants in cache")
            return restaurants
            
        # If no results in cache and user is authenticated, try Yelp API
        if not restaurants and user:
            try:
                logger.info("🔄 No cache results, attempting Yelp API search...")
                restaurants = await db.search_restaurants(params)
                if restaurants:
                    logger.info(f"✅ Found {len(restaurants)} restaurants from Yelp")
                    return restaurants
                logger.info("⚠️ No results from Yelp API")
            except Exception as e:
                logger.error(f"❌ Yelp search failed: {str(e)}")
        
        logger.info("ℹ️ No restaurants found")
        return []
            
    except Exception as e:
        logger.error(f"❌ Search operation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search operation failed: {str(e)}"
        )


@router.get("/{business_id}", response_model=Restaurant)
async def get_restaurant_details(business_id: str, auth: dict = require_auth) -> Restaurant:
    """Get detailed information about a specific restaurant."""
    try:
        logger.info(f"🔍 Fetching restaurant details for {business_id}")
>>>>>>> origin
        restaurant = await db.get_restaurant(business_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
            
        # Fetch images if none exist
        if not restaurant.photos or len(restaurant.photos) == 0:
            search_query = f"{restaurant.name} {restaurant.location.city} restaurant"
            images = await image_search.search_images(search_query, num=5)  # Get more images for detail view
            if images:
                restaurant.photos = images
<<<<<<< HEAD
                print(f"✅ Found {len(images)} images for {restaurant.name}")
            else:
                print(f"⚠️ No images found for {restaurant.name}")
=======
                logger.info(f"✅ Found {len(images)} images for {restaurant.name}")
            else:
                logger.warning(f"⚠️ No images found for {restaurant.name}")
>>>>>>> origin
                
        return restaurant
    except HTTPException:
        raise
    except Exception as e:
<<<<<<< HEAD
        print(f"❌ Error in get_restaurant_details: {str(e)}")
=======
        logger.error(f"❌ Error in get_restaurant_details: {str(e)}", exc_info=True)
>>>>>>> origin
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/phone", response_model=List[Restaurant])
async def search_by_phone(
<<<<<<< HEAD
    phone: str = Query(..., description="Phone number to search for")
=======
    phone: str = Query(..., description="Phone number to search for"),
    auth: dict = require_auth
>>>>>>> origin
) -> List[Restaurant]:
    """
    Search for restaurants by phone number.
    Phone number should be in E.164 format (+14157492060).
    """
    try:
<<<<<<< HEAD
=======
        logger.info(f"📞 Searching for restaurants by phone number: {phone}")
>>>>>>> origin
        return await db.search_by_phone(phone)
    except Exception as e:
        logger.error(f"❌ Error in search_by_phone: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
