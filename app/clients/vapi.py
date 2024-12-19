from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from typing import Any, AsyncGenerator, Dict

import httpx
from fastapi import HTTPException

from ..db.operating_hours import OperatingHoursDB
from ..db.restaurants import RestaurantDB
from ..models import (
    BusinessHoursResponse,
    CallAnalysisResponse,
    Customer,
    VAPICallRequest,
    VAPICallResponse,
)
from ..utils.constants import (
    ENABLE_CALLS,
    RESTAURANT_CALL_DELAY,
    SUPABASE_KEY,
    SUPABASE_URL,
)

logger = logging.getLogger(__name__)

class VAPIClient:
    def __init__(self):
        self.api_key = os.getenv("VAPI_API_KEY")
        if not self.api_key:
            logger.error("❌ VAPI_API_KEY not found in environment variables")
            raise ValueError("VAPI_API_KEY not found in environment variables")
            
        self.base_url = "https://api.vapi.ai"  # Replace with actual VAPI base URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info("✅ VAPIClient initialized with API key")

    def _format_phone_number(self, phone_number: str) -> str:
        """Format phone number to E.164 format (+1XXXXXXXXXX)."""
        # Remove any non-digit characters
        digits = re.sub(r'\D', '', phone_number)
        
        # Handle 10-digit numbers
        if len(digits) == 10:
            digits = f"1{digits}"
            
        # Ensure it's 11 digits
        if len(digits) != 11:
            raise ValueError("Phone number must be 10 or 11 digits")
            
        # Add + if not present
        if not phone_number.startswith('+'):
            return f"+{digits}"
        
        return phone_number

    async def make_call(self, phone_number: str, message: str = "This is a test call from Hungry Monkey") -> str:
        """Make a call using VAPI."""
        # Format the phone number
        formatted_number = self._format_phone_number(phone_number)
        print(f"Formatted phone number: {formatted_number}") 
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/call",
                    headers=self.headers,
                    json={
                        "name": "Test Call",
                        "phoneNumberId": os.getenv("VAPI_PHONE_NUMBER_ID"),
                        "customer": {"number": formatted_number},
                        "assistantId": os.getenv("VAPI_ASSISTANT_ID")  # Make sure to add this to your .env file
                    }
                )
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 201:
                    data = response.json()
                    print(f"Call successfully created: {data}")
                    return data.get("id")  # VAPI typically returns 'id' rather than 'call_id'
                elif response.status_code == 200:
                    data = response.json()
                    print(f"Call successful: {data}")
                    return data.get("id")
                else:
                    raise Exception(f"VAPI call failed with status {response.status_code}: {response.text}")
            except Exception as e:
                raise Exception(f"Failed to make call: {str(e)}")

    async def stream_conversation(self, conversation_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream conversation data from VAPI."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/stream/{conversation_id}",
                    headers=self.headers
                )
                if response.status_code != 200:
                    raise Exception(f"Failed to stream conversation: {response.text}")
                
                async for line in response.aiter_lines():
                    if line:
                        yield self._parse_stream_data(line)
            except Exception as e:
                raise Exception(f"Failed to stream conversation: {str(e)}")

    def _parse_stream_data(self, data: str) -> Dict[str, Any]:
        """Parse streaming data from VAPI."""
        return data

    async def send_message(self, conversation_id: str, message: str) -> Dict[str, Any]:
        """Send a message to VAPI."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/conversations/{conversation_id}/messages",
                    headers=self.headers,
                    json={"content": message}
                )
                return response.json()
            except Exception as e:
                raise Exception(f"Failed to send message: {str(e)}")

    async def get_call_status(self, call_id: str) -> str:
        """Get the status of a call."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/call/{call_id}",
                    headers=self.headers
                )
                print(f"Response status: {response.status_code}")
                # print(f"Response content: {response.text}") 
                if response.status_code != 200:
                    raise Exception(f"Failed to get call status: {response.text}")
                data = response.json()
                return data.get("status", "unknown")
            except Exception as e:
                raise Exception(f"Failed to get call status: {str(e)}")

    async def get_call_analysis(self, call_id: str) -> Dict[str, Any]:
        """Get the analysis of a completed call."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/call/{call_id}",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    raise Exception(f"Failed to get call analysis: {response.text}")
                analysis = response.json().get("analysis", {})
                return analysis
            except Exception as e:
                raise Exception(f"Failed to get call analysis: {str(e)}")

    async def wait_for_call_completion(self, call_id: str, max_attempts: int = 60, delay: int = 5, 
                                     initial_delay: int = 15, max_retries: int = 3) -> None:
        """Wait for a call to complete, checking status periodically."""
        import asyncio
        
        print(f"Waiting {initial_delay} seconds before checking call status...")
        await asyncio.sleep(initial_delay)
        
        retries = 0
        for _ in range(max_attempts):
            try:
                status = await self.get_call_status(call_id)
                print(f"Call status: {status}")
                
                if status in ["ended", "completed"]:  
                    print("Call completed successfully")
                    return
                elif status in ["failed", "error"]:
                    retries += 1
                    if retries >= max_retries:
                        raise Exception(f"Call failed with status: {status} after {max_retries} retries")
                    print(f"Call failed (attempt {retries}/{max_retries}), retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    continue
                elif status in ["queued", "in-progress", "ringing"]:
                    print(f"Call in progress (status: {status}), checking again in {delay} seconds...")
                
                await asyncio.sleep(delay)
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    raise Exception(f"Failed to check call status after {max_retries} retries: {str(e)}")
                print(f"Error checking status (attempt {retries}/{max_retries}), retrying in {delay} seconds...")
                await asyncio.sleep(delay)
        
        raise Exception("Call timed out waiting for completion")

    async def check_hours(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        try:
            hours_db = OperatingHoursDB()
            restaurant_db = RestaurantDB()
            logger.info(f"🔍 Calling to check hours for restaurant: {restaurant_id}")
            # get phone number from restaurant id
            restaurant = await restaurant_db.find_restaurant(restaurant_id)
            phone_number = restaurant.phone

            if ENABLE_CALLS:
                call_id = await self.make_call(phone_number, "This is a call to check hours")
                await self.wait_for_call_completion(call_id)
                analysis = await self.get_call_analysis(call_id)
                structured_data = analysis.get("structuredData", {})
                successEvaluation = analysis.get("successEvaluation", False)
            else:
                logger.info(f"👨‍🍳 Skipping call to restaurant ${restaurant_id} because ENABLE_CALLS is False")
                structured_data = {
                    "time_open": "N/A",
                    "time_closed": "N/A",
                    "is_open": False,
                }
                successEvaluation = False


            if successEvaluation and structured_data and "time_open" in structured_data and "time_closed" in structured_data:
                logger.info(f"✅ Updating hours for restaurant: {restaurant_id}")
                hours_db.update_hours(restaurant_id, structured_data.get("time_open"), structured_data.get("time_closed"), structured_data.get("is_open"))
                restaurant.is_open = structured_data.get("is_open")
                restaurant.is_hours_verified = True
                restaurant_db.update_restaurant(restaurant_id, {
                    "is_open": structured_data.get("is_open"),
                    "is_hours_verified": True,
                    "operating_hours": {
                        "time_open": structured_data.get("time_open"),
                        "time_closed": structured_data.get("time_closed"),
                        "is_open": structured_data.get("is_open")
                    }
                })
            else:
                print(f"❌ Failed to determine hours for restaurant: {restaurant_id}")
                restaurant.is_closed = True
                restaurant_db.update_restaurant(restaurant_id, {"is_hours_verified": False, "is_closed": True})
            return {"successEvaluation": successEvaluation, "message": f"Got hours from VAPI. {structured_data}"}
        except Exception as e:
            logger.error(f"Error checking hours for restaurant {restaurant_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def call_dispatch_loop(self):
        while True:
            try:
                logger.info("Starting dispatch loop...")
                await self.dispatch_calls()
            except Exception as e:
                logger.error(f"Error in dispatch loop: {str(e)}")
            await asyncio.sleep(RESTAURANT_CALL_DELAY) 

    async def dispatch_calls(self):
        logger.info("Dispatching calls...") 
        try:
            db = RestaurantDB()
            restaurants = db.get_restaurants_without_hours()
            
            if not restaurants:
                return
                
            vapi_client = VAPIClient()
            for restaurant in restaurants[:5]:
                try:
                    logger.info(f"Getting hours for {restaurant['business_id']}")
                    current_time = time.localtime()
                    if current_time.tm_hour < 8:
                        logger.info("It's before 8 AM. Skipping dispatch.")
                        return
                    await vapi_client.check_hours(restaurant["business_id"])
                    logger.info(f"Got hours for {restaurant['business_id']}")
                except Exception as e:
                    logger.error(f"Failed to get hours for {restaurant['business_id']}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to dispatch calls: {str(e)}")

