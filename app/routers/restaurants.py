from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..clients.yelp import YelpClient
from ..models import Restaurant, SearchParams

router = APIRouter()
client = YelpClient()

@router.get("/search", response_model=List[Restaurant])
async def search_restaurants(
    term: str = Query(None, description="Search term (e.g., 'coffee', 'restaurants')"),
    location: str = Query(..., description="Location (e.g., 'San Francisco, CA')"),
    price: Optional[str] = Query(None, description="Price level (1, 2, 3, 4)"),
    open_now: Optional[bool] = Query(None, description="Filter for open restaurants"),
    categories: Optional[str] = Query(None, description="Category filter (e.g., 'italian')")
) -> List[Restaurant]:
    """
    Search for restaurants using the Yelp API.
    Returns a list of restaurants matching the search criteria.
    """
    try:
        params = SearchParams(
            term=term or "restaurants",
            location=location,
            price=price,
            open_now=open_now,
            categories=categories
        )
        return await client.search_restaurants(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{business_id}", response_model=Restaurant)
async def get_restaurant_details(business_id: str) -> Restaurant:
    """
    Get detailed information about a specific restaurant.
    """
    try:
        return await client.get_restaurant_by_id(business_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Restaurant not found: {str(e)}")

@router.get("/search/phone")
async def search_by_phone(phone: str = Query(..., description="Phone number to search for")) -> List[Restaurant]:
    """
    Search for restaurants by phone number.
    Phone number should be in E.164 format (+14157492060).
    """
    try:
        return await client.search_by_phone(phone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
