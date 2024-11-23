from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..db.restaurants import RestaurantDB
from ..models import Restaurant, SearchParams

router = APIRouter()
db = RestaurantDB()

@router.get("/search", response_model=List[Restaurant])
async def search_restaurants(
    term: str = Query(None, description="Search term (e.g., 'coffee', 'restaurants')"),
    location: str = Query(..., description="Location (e.g., 'San Francisco, CA')"),
    price: Optional[str] = Query(None, description="Price level (1, 2, 3, 4)"),
    open_now: Optional[bool] = Query(None, description="Filter for open restaurants"),
    categories: Optional[str] = Query(None, description="Category filter")
) -> List[Restaurant]:
    """
    Search for restaurants using Yelp API and cache results.
    Returns a list of restaurants matching the search criteria.
    """
    try:
        params = SearchParams(
            term=term,
            location=location,
            price=price,
            open_now=open_now,
            categories=categories
        )
        return await db.search_restaurants(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{business_id}", response_model=Restaurant)
async def get_restaurant_details(business_id: str) -> Restaurant:
    """
    Get detailed information about a specific restaurant.
    Checks cache first, then Yelp API if not found.
    """
    restaurant = await db.get_restaurant(business_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

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

@router.get("/cached", response_model=List[Restaurant])
async def get_cached_restaurants(
    limit: Optional[int] = Query(None, description="Maximum number of restaurants to return")
) -> List[Restaurant]:
    """
    Get restaurants from cache only, without hitting the Yelp API.
    """
    return await db.get_cached_restaurants(limit)
