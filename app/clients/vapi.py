from typing import AsyncGenerator, Dict, Any
import httpx
import os
from dotenv import load_dotenv

class VAPIClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("VAPI_API_KEY")
        self.base_url = "https://api.vapi.ai"  # Replace with actual VAPI base URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def stream_conversation(self, conversation_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream conversation data from VAPI."""
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    'GET',
                    f"{self.base_url}/conversations/{conversation_id}/stream",
                    headers=self.headers
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            yield self._parse_stream_data(line)
            except Exception as e:
                raise Exception(f"Failed to stream conversation: {str(e)}")

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

    def _parse_stream_data(self, data: str) -> Dict[str, Any]:
        """Parse streaming data from VAPI."""
        # Implement parsing logic based on VAPI's streaming format
        # This is a placeholder - adjust based on actual VAPI response format
        return {"data": data}
