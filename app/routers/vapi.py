from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..clients.vapi import VAPIClient
from ..db.operating_hours import OperatingHoursDB
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
vapi_client = VAPIClient()

class VAPICallRequest(BaseModel):
    phone_number: str
    message: Optional[str] = "This is a call from Hungry Monkey"

@router.post("/call")
async def make_call(request: VAPICallRequest):
    """Make a call using VAPI."""
    try:
        result = await vapi_client.make_call(request.phone_number, request.message)
        return {"status": "success", "call_id": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/call-analysis/{call_id}")
async def get_call_analysis(call_id: str):
    """Get the analysis and structured output from a completed call."""
    try:
        analysis = await vapi_client.get_call_analysis(call_id)
        return {"success": True, "data": analysis}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/check-hours/{restaurant_id}")
async def check_hours(restaurant_id: str):
    try:
        hours_db = OperatingHoursDB()
        # For now just mark as unverified since we haven't implemented actual hours checking yet
        hours_db.mark_hours_unverified(restaurant_id)
        return {"status": "success", "message": "Hours check initiated"}
    except Exception as e:
        logger.error(f"Error checking hours for restaurant {restaurant_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))