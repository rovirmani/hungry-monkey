from fastapi import APIRouter, HTTPException, Query, Response, Depends
from typing import List, Optional
from ..db.restaurants import RestaurantDB
from ..db.operating_hours import OperatingHoursDB
from ..models import Restaurant, SearchParams, RestaurantWithHours, OperatingHours
from ..clients.google_custom_search import image_search
from ..auth.clerk import require_auth, optional_auth, get_optional_user
import httpx
import asyncio
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)

router = APIRouter()
db = RestaurantDB()
oh_db = OperatingHoursDB()


@router.get("/", response_model=List[RestaurantWithHours])
async def get_cached_restaurants(
    limit: Optional[int] = Query(None, description="Maximum number of restaurants to return"),
    fetch_images: Optional[bool] = Query(False, description="Whether to fetch missing images"),
) -> List[RestaurantWithHours]:
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
    Search for restaurants. If user is authenticated, search Yelp API.
    Otherwise, search local database.
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
        
        # If user is authenticated, search Yelp
        if user:
            try:
                logger.info("🔄 Attempting Yelp API search...")
                restaurants = await db.search_restaurants(params)
                if restaurants:
                    logger.info(f"✅ Found {len(restaurants)} restaurants from Yelp")
                    return restaurants
                logger.info("⚠️ No results from Yelp API")
            except Exception as e:
                logger.error(f"❌ Yelp search failed: {str(e)}")
                # Fall through to cache search
                
        # Search local cache
        logger.info("🔄 Searching local cache...")
        restaurants = await db.search_cached_restaurants(params)
        if restaurants:
            logger.info(f"✅ Found {len(restaurants)} restaurants in cache")
            return restaurants
            
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
        restaurant = await db.get_restaurant(business_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
            
        # Fetch images if none exist
        if not restaurant.photos or len(restaurant.photos) == 0:
            search_query = f"{restaurant.name} {restaurant.location.city} restaurant"
            images = await image_search.search_images(search_query, num=5)  # Get more images for detail view
            if images:
                restaurant.photos = images
                logger.info(f"✅ Found {len(images)} images for {restaurant.name}")
            else:
                logger.warning(f"⚠️ No images found for {restaurant.name}")
                
        return restaurant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in get_restaurant_details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/phone", response_model=List[Restaurant])
async def search_by_phone(
    phone: str = Query(..., description="Phone number to search for"),
    auth: dict = require_auth
) -> List[Restaurant]:
    """
    Search for restaurants by phone number.
    Phone number should be in E.164 format (+14157492060).
    """
    try:
        logger.info(f"📞 Searching for restaurants by phone number: {phone}")
        return await db.search_by_phone(phone)
    except Exception as e:
        logger.error(f"❌ Error in search_by_phone: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
