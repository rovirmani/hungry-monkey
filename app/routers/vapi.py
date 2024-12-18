from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ..clients.vapi import VAPIClient
from ..db.operating_hours import OperatingHoursDB
from ..db.restaurants import RestaurantDB
from ..middleware.auth import ClerkAuthMiddleware
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
vapi_client = VAPIClient()
auth = ClerkAuthMiddleware()

@router.post("/call/{phone_number}")
async def make_call(
    phone_number: str, 
    message: Optional[str] = "This is a call from Hungry Monkey",
    token: str = Depends(auth)
):
    """Make a call using VAPI."""
    try:
        result = await vapi_client.make_call(phone_number, message)
        return {"status": "success", "call_id": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/call-analysis/{call_id}")
async def get_call_analysis(
    call_id: str,
    token: str = Depends(auth)
):
    """Get the analysis and structured output from a completed call."""
    try:
        analysis = await vapi_client.get_call_analysis(call_id)
        return {"success": True, "data": analysis}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/test/test_check_hours")
async def check_hours():
    try:
        hours_db = OperatingHoursDB()
        restaurant_db = RestaurantDB()
        structured_data = {
            "time_open": "10:00 AM",
            "time_closed": "2:00 PM",
            "is_open": True,
        }
        print(f"✅ Got hours from VAPI: {structured_data}")
        if structured_data and "time_open" in structured_data and "time_closed" in structured_data:
            hours_db.update_hours("jJigeJake", structured_data.get("time_open"), structured_data.get("time_closed"), structured_data.get("is_open"))

        return {"status": "success", "message": f"Got hours from VAPI. {structured_data}"}
    except Exception as e:
        logger.error(f"Error checking hours for restaurant : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Import models at the bottom
from ..models import VAPICallRequest, BusinessHoursResponse, CallAnalysisResponse