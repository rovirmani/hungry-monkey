from __future__ import annotations

import asyncio
import logging
from typing import List, Optional
from urllib.parse import quote

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from ..auth.clerk import UserData, get_optional_user, optional_auth, require_auth
from ..clients.google_custom_search import image_search
from ..db.operating_hours import OperatingHoursDB
from ..db.restaurants import restaurant_db
from ..db.users import UserDB
from ..models import OperatingHours, Restaurant, RestaurantWithHours, SearchParams

logger = logging.getLogger(__name__)

router = APIRouter()
oh_db = OperatingHoursDB()
user_db = UserDB()


@router.get("/", response_model=List[RestaurantWithHours])
async def get_stored_restaurants(
    limit: Optional[int] = Query(None, description="Maximum number of restaurants to return"),
    fetch_images: Optional[bool] = Query(False, description="Whether to fetch missing images"),
    user: Optional[dict] = optional_auth
) -> List[RestaurantWithHours]:
    """
    Get cached restaurants. Authentication is optional - authenticated users get access to image fetching.
    Uses restaurantDB to fetch stored restaurants with their operating hours.
    """
    try:
        fused_restaurants = await asyncio.to_thread(restaurant_db.get_restaurants_with_hours())
        if not fused_restaurants:
            return []
        
        # Optionally fetch missing images
        if fetch_images:
            for restaurant in fused_restaurants:
                if not restaurant.image_url:
                    try:
                        image_url = await image_search(f"{restaurant.name} {restaurant.location.address1}")
                        if image_url:
                            restaurant.image_url = image_url
                            await restaurant_db.update_restaurant(restaurant.business_id, {"image_url": image_url})
                    except Exception as e:
                        logger.error(f"Failed to fetch image for {restaurant.name}: {str(e)}")
                        continue
        
        return fused_restaurants

    except Exception as e:
        logger.error(f"Failed to fetch restaurants: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch restaurants: {str(e)}"
        )


@router.get("/search")
async def search_restaurants(
    request: Request,
    term: Optional[str] = None,
    location: Optional[str] = None,
    radius: Optional[int] = None,
    limit: Optional[int] = 20,
    sort_by: Optional[str] = "best_match",
    price: Optional[str] = None,
    categories: Optional[str] = None,
    offset: Optional[int] = None,
    open_now: Optional[bool] = None,
    user: Optional[UserData] = optional_auth
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
        logger.info(f"👤 User authenticated: {user.first_name} {user.last_name}")

        is_search_permitted = await user_db.is_search_permitted(user.user_id)
        logger.info(f"✅ User search permitted: {is_search_permitted}") 
        # Always search local cache first
        logger.info("🔄 Searching local cache...")
        restaurants = await db.search_cached_restaurants(params)
        if restaurants:
            logger.info(f"✅ Found {len(restaurants)} restaurants in cache")
            print("The limit is ", limit)
            return restaurants[:limit]
            
        # If no results in cache and user is authenticated, try Yelp API
        if (not restaurants or len(restaurants) < 10) and is_search_permitted:
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
