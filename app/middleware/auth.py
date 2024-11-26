from typing import Optional
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class ClerkAuthMiddleware(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(ClerkAuthMiddleware, self).__init__(auto_error=auto_error)
        self.clerk_api_key = os.getenv("CLERK_SECRET_KEY")
        if not self.clerk_api_key:
            raise ValueError("CLERK_SECRET_KEY not found in environment variables")
        self.clerk_jwt_issuer = os.getenv("CLERK_JWT_ISSUER")
        if not self.clerk_jwt_issuer:
            raise ValueError("CLERK_JWT_ISSUER not found in environment variables")

    async def verify_jwt(self, token: str) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.clerk_jwt_issuer}/session",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    }
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=401,
                    detail=f"Invalid authentication credentials: {str(e)}"
                )

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication scheme. Use Bearer token."
                )
            
            await self.verify_jwt(credentials.credentials)
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization code."
            )
