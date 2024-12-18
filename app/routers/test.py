from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..clients.yelp import YelpClient
from ..models import Restaurant, SearchParams

logger = logging.getLogger(__name__)
router = APIRouter()
yelp_client = YelpClient()

@router.get("/yelp-images")
async def search_restaurant_images(
    term: Optional[str] = Query(None, description="Search term (e.g., restaurant name)"),
    location: str = Query(..., description="Location (e.g., 'San Francisco, CA')"),
    limit: Optional[int] = Query(5, description="Number of results to return")
) -> List[dict]:
    """
    Test endpoint that searches for restaurants using Yelp API and returns their image URLs.
    Returns a list of dicts containing restaurant name, id, and image URL.
    """
    try:
        # Create search params
        params = SearchParams(
            term=term,
            location=location,
            limit=limit
        )
        
        # Search using Yelp API
        restaurants = await yelp_client.search_businesses(
            term=params.term,
            location=params.location,
            limit=params.limit
        )
        
        # Extract relevant information
        results = []
        for restaurant in restaurants:
            result = {
                "id": restaurant.business_id,
                "name": restaurant.name,
                "image_url": restaurant.photos[0] if restaurant.photos else None
            }
            results.append(result)
            
        return results
        
    except Exception as e:
        logger.error(f"Failed to search restaurant images: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search restaurant images: {str(e)}"
        )