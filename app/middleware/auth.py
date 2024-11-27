from typing import Optional
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import httpx
from jwt import PyJWT
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
        self.jwt = PyJWT()

    async def verify_jwt(self, token: str) -> dict:
        try:
            # Get JWKS
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.clerk_jwt_issuer}/.well-known/jwks.json")
                response.raise_for_status()
                jwks = response.json()

            # Get unverified header
            header = self.jwt.get_unverified_header(token)
            if not header or "kid" not in header:
                raise HTTPException(status_code=401, detail="Invalid token header")

            # Find signing key
            key = next((k for k in jwks["keys"] if k["kid"] == header["kid"]), None)
            if not key:
                raise HTTPException(status_code=401, detail="No matching key found")

            # Verify token
            try:
                decoded = self.jwt.decode(
                    token,
                    self.jwt.algorithms.RSAAlgorithm.from_jwk(key),
                    algorithms=["RS256"],
                    audience=os.getenv("CLERK_JWT_AUDIENCE"),
                    issuer=self.clerk_jwt_issuer
                )
                return decoded
            except Exception as e:
                raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

        except httpx.HTTPError as e:
            raise HTTPException(status_code=401, detail=f"Failed to verify token: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

    async def __call__(self, request: Request) -> Optional[str]:
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
            
            if credentials:
                if not credentials.scheme == "Bearer":
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid authentication scheme. Use Bearer token."
                    )
                
                await self.verify_jwt(credentials.credentials)
                return credentials.credentials
                
            return None
        except Exception:
            return None
