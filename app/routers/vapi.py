from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..clients.vapi import VAPIClient

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

@router.get("/check-hours/{phone_number}")
async def check_hours(phone_number: str):
    """Call a restaurant to check their hours. Get that calls id. Use the id to get structured data."""
    try:
        # Make the call and get call ID
        call_id = await vapi_client.make_call(phone_number)
        
        # Wait for call to complete (default 2 minute timeout)
        await vapi_client.wait_for_call_completion(call_id)
        
        # Get the analysis once call is completed
        analysis = await vapi_client.get_call_analysis(call_id)
        structured_data = analysis.get("structuredData", {})

        # populate the operatingHours table in supabase

        return {"success": analysis.get("successEvaluation", False), "data": structured_data}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))