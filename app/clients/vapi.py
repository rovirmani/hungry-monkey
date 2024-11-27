from typing import AsyncGenerator, Dict, Any
import httpx
import os
import re
from dotenv import load_dotenv
from ..models.vapi import VAPICallRequest, VAPICallResponse, Customer, BusinessHoursResponse, CallAnalysisResponse

class VAPIClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("VAPI_API_KEY")
        self.base_url = "https://api.vapi.ai"  # Replace with actual VAPI base URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

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
